"""Local SMF 0/1 import with a global tempo map and independent key releases.

No MIDI ports, synthesizers, network access or physical input are used here.
Times are written as absolute millisecond waits, not quantized to Note Delay.
"""
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
import io
from pathlib import Path

from player.piano_keys import MIDI_TO_KEY, physical_key


class MidiImportError(ValueError):
    pass


@dataclass(frozen=True)
class MidiTrackInfo:
    index: int
    name: str
    notes: int
    drums: int


@dataclass(frozen=True)
class MidiDocument:
    name: str
    tracks: tuple[MidiTrackInfo, ...]
    events: tuple  # (absolute milliseconds, track index, mido Message)
    duration_ms: float
    tempo_changes: int


@dataclass(frozen=True)
class ImportedScore:
    sheet: str
    duration_ms: float
    source_notes: int
    played_notes: int
    changes: dict[str, int]
    summary: str
    repairs: int = 0


def read_midi(path: Path) -> MidiDocument:
    try:
        import mido
    except ImportError:
        raise MidiImportError("Для импорта MIDI установите зависимости: pip install -r requirements.txt") from None
    try:
        if path.stat().st_size > 16 * 1024 * 1024:
            raise MidiImportError("MIDI-файл должен быть не больше 16 MB.")
        midi = mido.MidiFile(file=io.BytesIO(path.read_bytes()))
        if midi.type not in (0, 1) or midi.ticks_per_beat <= 0:
            raise MidiImportError("Поддерживаются MIDI 0/1 с музыкальной сеткой PPQN. Формат 2 и SMPTE пока не поддерживаются.")
        events, tracks = [], []
        for index, track in enumerate(midi.tracks):
            tick, notes, drums = 0, 0, 0
            for order, message in enumerate(track):
                tick += message.time
                events.append((tick, index, order, message))
                if message.type == "note_on" and message.velocity:
                    if message.channel == 9:
                        drums += 1
                    else:
                        notes += 1
            tracks.append(MidiTrackInfo(index, track.name, notes, drums))
        if len(events) > 500_000 or sum(t.notes for t in tracks) > 200_000:
            raise MidiImportError("Слишком большой MIDI: предел — 200 000 нот и 500 000 событий.")
        tempo, previous, elapsed, changes = 500_000, 0, 0.0, 0
        timed = []
        for tick, index, order, message in sorted(events, key=lambda e: e[:3]):
            elapsed += (tick - previous) * tempo / midi.ticks_per_beat / 1000
            previous = tick
            if elapsed > 3_599_000:
                raise MidiImportError("Максимальная длительность MIDI — чуть меньше одного часа.")
            if message.type == "set_tempo":
                if message.tempo <= 0:
                    raise MidiImportError("В MIDI указан нулевой темп.")
                changes += tick > 0 and message.tempo != tempo
                tempo = message.tempo
            timed.append((elapsed, index, message))
        if not any(track.notes for track in tracks):
            raise MidiImportError("В файле нет мелодических нот. Ударные канала 10 не импортируются.")
        return MidiDocument(path.stem, tuple(tracks), tuple(timed), elapsed, changes)
    except MidiImportError:
        raise
    except (OSError, ValueError, EOFError, KeyError, IndexError, TypeError) as error:
        raise MidiImportError(f"Не удалось прочитать MIDI: {error}") from error


def _extract_notes(document: MidiDocument, selected: set[int], sustain: bool):
    held = defaultdict(deque)
    sustained = defaultdict(list)
    pedal = defaultdict(bool)
    notes = []
    repairs = 0

    def finish(item, end):
        track, channel, pitch, start = item
        notes.append((pitch, start, max(start, end)))

    def release_channel(channel, now, immediate=False):
        for key in list(held):
            if key[1] != channel:
                continue
            while held[key]:
                item = held[key].popleft()
                if pedal[channel] and not immediate:
                    sustained[channel].append(item)
                else:
                    finish(item, now)
        if immediate:
            for item in sustained.pop(channel, []):
                finish(item, now)

    for now, track, msg in document.events:
        channel = getattr(msg, "channel", -1)
        if msg.type == "control_change" and channel != 9:
            if msg.control == 64 and sustain:
                down = msg.value >= 64
                if pedal[channel] and not down:
                    for item in sustained.pop(channel, []):
                        finish(item, now)
                pedal[channel] = down
            elif msg.control in (120, 123):
                release_channel(channel, now, immediate=msg.control == 120)
            elif msg.control == 121:
                pedal[channel] = False
                for item in sustained.pop(channel, []):
                    finish(item, now)
            continue
        if track not in selected or channel == 9 or msg.type not in ("note_on", "note_off"):
            continue
        key = (track, channel, msg.note)
        if msg.type == "note_on" and msg.velocity:
            held[key].append((track, channel, msg.note, now))
        elif held[key]:
            item = held[key].popleft()
            if pedal[channel]:
                sustained[channel].append(item)
            else:
                finish(item, now)
    for queue in held.values():
        for item in queue:
            repairs += 1
            finish(item, document.duration_ms)
    for queue in sustained.values():
        for item in queue:
            finish(item, document.duration_ms)
    return sorted(notes, key=lambda n: (n[1], n[0])), repairs


def _number(value):
    return f"{value:.3f}".rstrip("0").rstrip(".") or "0"


def convert_midi(document: MidiDocument, selected: set[int] | None = None, *,
                 sustain: bool = True, adapt: bool = True) -> ImportedScore:
    selected = {t.index for t in document.tracks if t.notes} if selected is None else selected
    notes, repairs = _extract_notes(document, selected, sustain)
    if not notes:
        raise MidiImportError("Выберите хотя бы одну дорожку с нотами.")
    changes = Counter(unclosed=repairs, range=0, revoiced=0, merged=0, omitted=0, holds=0, retriggered=0)
    grouped = defaultdict(list)
    for pitch, start, end in notes:
        original = pitch
        if not 36 <= pitch <= 96:
            if not adapt:
                raise MidiImportError("Есть ноты вне C2–C7. Включите адаптацию по октавам.")
            while pitch < 36:
                pitch += 12
            while pitch > 96:
                pitch -= 12
            changes["range"] += 1
        grouped[round(start, 3)].append((pitch, round(end, 3), original))
    placed = []
    for start, group in sorted(grouped.items()):
        by_pitch = {}
        for pitch, end, original in group:
            if original in by_pitch:
                changes["merged"] += 1
            by_pitch[original] = (pitch, max(end, by_pitch.get(original, (pitch, end))[1]))
        # Keep the top melody and bottom bass before fitting inner voices.
        pitches = sorted(by_pitch, reverse=True)
        order = [pitches[0]] + ([pitches[-1]] if len(pitches) > 1 else []) + pitches[1:-1]
        used = set()
        for original in order:
            pitch, end = by_pitch[original]
            candidates = [pitch] if not adapt else sorted((p for p in MIDI_TO_KEY if p % 12 == pitch % 12),
                                                         key=lambda p: (abs(p-pitch), p))
            chosen = next((p for p in candidates if physical_key(MIDI_TO_KEY[p]) not in used), None)
            if chosen is None:
                if not adapt:
                    raise MidiImportError("В аккорде конфликтуют обычная и Shift-клавиша. Включите адаптацию по октавам.")
                changes["omitted"] += 1
                continue
            changes["revoiced"] += chosen != pitch
            used.add(physical_key(MIDI_TO_KEY[chosen]))
            hold = round(end - start, 3)
            bounded = max(5, min(60_000, hold))
            changes["holds"] += bounded != hold
            placed.append([start, chosen, bounded])
    placed.sort(key=lambda n: (n[0], n[1]))
    next_onset = {}
    for note in reversed(placed):
        key = physical_key(MIDI_TO_KEY[note[1]])
        following = next_onset.get(key)
        if following is not None and note[0] + note[2] > following + 0.0005:
            changes["retriggered"] += 1
        next_onset[key] = note[0]
    groups = defaultdict(list)
    for start, pitch, hold in placed:
        groups[start].append((pitch, hold))
    lines = ["|delay=0|"]
    previous = 0.0
    for start, group in sorted(groups.items()):
        if start > previous:
            lines.append(f"|wait={_number(start-previous)}|")
        keys = [MIDI_TO_KEY[pitch] for pitch, _ in group]
        holds = [hold for _, hold in group]
        if len(set(holds)) == 1:
            token = keys[0] if len(keys) == 1 else "[" + "".join(keys) + "]"
            token += f"<{_number(holds[0])}>"
        else:
            token = "[" + "".join(f"{key}<{_number(hold)}>" for key, hold in zip(keys, holds)) + "]"
        lines.append(token)
        previous = start
    duration = round(max(document.duration_ms, max(start + hold for start, _, hold in placed)) + 800, 3)
    lines.append(f"|wait={_number(duration-previous)}|")
    summary = (f"{len(placed)} из {len(notes)} нот · {duration/1000:.2f} s · "
               f"смен темпа: {document.tempo_changes}\n"
               f"Переносов по октавам: {changes['range'] + changes['revoiced']} · "
               f"объединено: {changes['merged']} · не поместилось: {changes['omitted']}\n"
               f"Перекрытий одной клавиши: {changes['retriggered']} · "
               f"ограничений удержания: {changes['holds']} · незакрытых нот: {repairs}")
    return ImportedScore("\n".join(lines) + "\n", duration, len(notes), len(placed), dict(changes), summary, repairs)
