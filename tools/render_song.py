"""Export a catalog song as MIDI and a small, offline piano-like WAV preview.

The sheet uses the same parser, onset plan, preset holds, and physical-key
retrigger rules as the app. The WAV is an approximate synthesized piano timbre,
not a recording of the website's instrument. No start countdown is exported.

Example:
    python tools/render_song.py --song moonlit-platform --output-dir assets/originals
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import math
from pathlib import Path
import re
import struct
import sys
import wave

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from player.parser import SheetParser
from player.plan_writer import build_plan
from player.humanization import humanize_plan
from player.song_library import SongPreset, load_song_library
from player.piano_keys import KEY_TO_MIDI, SHARP_KEYS, UNSHIFTED_SYMBOLS, WHITE_KEYS, WHITE_PITCHES, physical_key


MIDI_DIVISION = 9600


@dataclass(slots=True)
class Note:
    pitch: int
    start_ms: float
    end_ms: float


def collect_notes(song: SongPreset, *, humanize: bool = False,
                  seed: int | None = None) -> tuple[list[Note], float]:
    """Apply held-key deadlines, including a release before a same-key retrigger."""
    plan = build_plan(SheetParser().parse(song.sheet), song.note_delay_ms, song.key_hold_ms)
    if humanize:
        plan = humanize_plan(plan, song.note_delay_ms, song.key_hold_ms, seed=seed)
    notes: list[Note] = []
    active: dict[str, Note] = {}
    for event in plan.events:
        mapped: dict[str, str] = {}
        for code in event.keys:
            character = chr(code)
            if character not in KEY_TO_MIDI:
                raise ValueError(f"No piano pitch for sheet character {character!r}")
            physical = physical_key(character)
            if physical in mapped and mapped[physical] != character:
                raise ValueError(f"Incompatible chord characters: {mapped[physical]!r}, {character!r}")
            mapped[physical] = character
        for physical, character in mapped.items():
            previous = active.get(physical)
            if previous is not None and previous.end_ms > event.offset_ms:
                previous.end_ms = event.offset_ms
            note = Note(KEY_TO_MIDI[character], event.offset_ms,
                        event.offset_ms + (event.hold_ms if event.hold_ms is not None else song.key_hold_ms))
            notes.append(note)
            active[physical] = note
    return notes, plan.duration_ms


def variable_length(value: int) -> bytes:
    if value < 0:
        raise ValueError("MIDI delta time cannot be negative")
    data = [value & 0x7f]
    while value >> 7:
        value >>= 7
        data.insert(0, (value & 0x7f) | 0x80)
    return bytes(data)


def midi_meta(kind: int, content: bytes) -> bytes:
    return bytes((0xff, kind)) + variable_length(len(content)) + content


def write_midi(path: Path, song: SongPreset, notes: list[Note],
               duration_ms: float, notes_per_beat: int = 4) -> None:
    """One-track General MIDI piano; default grid is a sixteenth-note slot.

    9,600 PPQN keeps the app's regular and 35% fast onsets exact. Physical holds
    are rounded to the closest MIDI tick (under 0.1 ms at all allowed presets).
    """
    tempo_us = song.note_delay_ms * notes_per_beat * 1000
    ticks_per_ms = MIDI_DIVISION * 1000 / tempo_us
    description = f"Rendered from the bundled sheet; base hold {song.key_hold_ms} ms"
    if song.artist:
        description = song.artist + "; " + description
    events: list[tuple[int, int, bytes]] = [
        (0, 0, midi_meta(0x03, song.title.encode("utf-8"))),
        (0, 1, midi_meta(0x01, description.encode("utf-8"))),
        (0, 2, midi_meta(0x51, tempo_us.to_bytes(3, "big"))),
        (0, 3, midi_meta(0x58, bytes((4, 2, 24, 8)))),
        (0, 4, bytes((0xc0, 0))),  # General MIDI Acoustic Grand Piano.
    ]
    for note in notes:
        events.append((round(note.start_ms * ticks_per_ms), 20, bytes((0x90, note.pitch, 88))))
        events.append((round(note.end_ms * ticks_per_ms), 10, bytes((0x80, note.pitch, 0))))
    events.sort(key=lambda item: (item[0], item[1]))  # Release before retrigger.
    track = bytearray()
    previous_tick = 0
    for tick, _, message in events:
        track.extend(variable_length(tick - previous_tick))
        track.extend(message)
        previous_tick = tick
    end_tick = max(previous_tick, round(duration_ms * ticks_per_ms))
    track.extend(variable_length(end_tick - previous_tick))
    track.extend(midi_meta(0x2f, b""))
    header = b"MThd" + struct.pack(">IHHH", 6, 0, 1, MIDI_DIVISION)
    path.write_bytes(header + b"MTrk" + struct.pack(">I", len(track)) + track)


def write_wav(path: Path, notes: list[Note], duration_ms: float,
              sample_rate: int = 24000) -> tuple[float, float]:
    """Synthesize percussive partials with short, smooth damper release tails."""
    release_seconds = 0.75
    duration_seconds = duration_ms / 1000 + release_seconds
    output = np.zeros(math.ceil(duration_seconds * sample_rate), dtype=np.float32)
    partial_levels = (1.0, 0.43, 0.22, 0.12, 0.075, 0.045, 0.025)
    for note in notes:
        start = round(note.start_ms * sample_rate / 1000)
        hold = (note.end_ms - note.start_ms) / 1000
        count = min(len(output) - start, math.ceil((hold + release_seconds) * sample_rate))
        if count <= 0:
            continue
        time = np.arange(count, dtype=np.float32) / sample_rate
        frequency = 440.0 * 2 ** ((note.pitch - 69) / 12)
        tone = np.zeros(count, dtype=np.float32)
        # A little inharmonicity and faster decay in upper partials suggest a
        # struck string without requiring external samples or instrument banks.
        for partial, level in enumerate(partial_levels, 1):
            partial_frequency = frequency * partial * math.sqrt(1 + 0.00008 * partial * partial)
            if partial_frequency >= sample_rate * 0.46:
                continue
            decay = (1.8 - min(note.pitch, 96) / 100) / math.sqrt(partial)
            phase = (note.pitch * 0.037 * partial) % (2 * math.pi)
            tone += level * np.sin(2 * math.pi * partial_frequency * time + phase) * np.exp(-time / decay)
        attack = np.minimum(time / 0.003, 1.0)
        damper = np.exp(-np.maximum(time - hold, 0) / 0.105)
        # Very low fundamentals can dominate a synthetic mix; soften that bias.
        register_gain = 0.8 + 0.2 * min(max((note.pitch - 36) / 36, 0), 1)
        output[start:start + count] += tone * attack * damper * register_gain
    peak = float(np.max(np.abs(output))) if len(output) else 0.0
    if not math.isfinite(peak) or peak <= 0:
        raise ValueError("The synthesized song is silent or contains invalid samples")
    output *= 0.88 / peak
    pcm = np.rint(output * 32767).astype("<i2")
    with wave.open(str(path), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(sample_rate)
        audio.writeframes(pcm.tobytes())
    return len(output) / sample_rate, float(np.max(np.abs(output)))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--song", default="moonlit-platform", help="Bundled catalog song ID")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "assets/originals")
    parser.add_argument("--sample-rate", type=int, default=24000)
    parser.add_argument("--notes-per-beat", type=int, choices=(1, 2, 4), default=4,
                        help="Grid interpretation for MIDI tempo; WAV onsets are unchanged")
    args = parser.parse_args()
    if not 8000 <= args.sample_rate <= 96000:
        parser.error("Sample rate must be between 8000 and 96000 Hz")
    song = next((song for song in load_song_library(ROOT / "data/library") if song.id == args.song), None)
    if song is None:
        parser.error(f"Unknown song ID: {args.song}")
    if re.fullmatch(r"[a-z0-9][a-z0-9-]*", song.id) is None:
        parser.error("Song ID cannot be used as a filename")
    notes, duration_ms = collect_notes(song)
    if not notes:
        parser.error("The song contains no notes")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    midi_path = args.output_dir / f"{song.id}.mid"
    wav_path = args.output_dir / f"{song.id}.wav"
    write_midi(midi_path, song, notes, duration_ms, args.notes_per_beat)
    seconds, peak = write_wav(wav_path, notes, duration_ms, args.sample_rate)
    print(f"{song.title}: {len(notes)} note attacks, {duration_ms / 1000:.3f} s + release tail")
    print(f"MIDI: {midi_path.resolve()}")
    print(f"WAV: {wav_path.resolve()} ({seconds:.3f} s, {args.sample_rate} Hz, mono 16-bit, peak {peak:.3f})")


if __name__ == "__main__":
    main()
