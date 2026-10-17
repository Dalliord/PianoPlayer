"""Velvet Teeth: compact original piano shuffle, 48 bars at 125 BPM.

The reference is the short, rhythm-led character of the Wild Side opening,
not a transcription of its copyrighted melody. The six-part quarter grid
writes swing into the sheet; explicit holds connect the lead over the bass.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.compose_moonlit_platform import PITCH_TO_KEY, make_sheet as encode_plain_sheet, pitch_number

SONG_ID = "velvet-teeth"
TITLE = "Velvet Teeth"
BPM = 125
NOTE_DELAY_MS = 80
KEY_HOLD_MS = 140
SLOTS_PER_BAR = 24
DURATION_MS = 92_160
PITCH_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")

# Root, four bass notes, a small middle-register voicing. The top voice is
# composed separately; accompaniment does not replace it with chord arpeggios.
HARMONIES = {
    "Em9": ("E2", "E3 G3 B3 D4", "G3 D4 F#4"),
    "Em6": ("E2", "E3 G3 B3 C#4", "G3 C#4 F#4"),
    "Am9": ("A2", "A2 C3 E3 G3", "C4 G4 B4"),
    "D13": ("D2", "D3 F#3 A3 C4", "F#3 C4 B4"),
    "Gmaj9": ("G2", "G2 B2 D3 F#3", "B3 F#4 A4"),
    "Cmaj9": ("C3", "C3 E3 G3 B3", "E4 B4 D5"),
    "F#half": ("F#2", "F#2 A2 C3 E3", "A3 C4 E4"),
    "B7": ("B2", "B2 D#3 F#3 A3", "D#4 F#4 A4"),
    "B7b9": ("B2", "B2 D#3 F#3 A3", "D#4 A4 C5"),
    "Am6": ("A2", "A2 C3 E3 F#3", "C4 F#4 B4"),
    "A13": ("A2", "A2 C#3 E3 G3", "C#4 F#4 G4"),
    "Em": ("E2", "E3 G3 B3 E4", "G3 B3 E4"),
}

SWING = (0, 4, 6, 10, 12, 16, 18, 22)
HOOK = (0, 4, 6, 10, 16, 22)
ANSWER = (0, 6, 10, 12, 18, 22)
PUSH = (0, 3, 6, 10, 12, 15, 18, 22)
SEVEN = (0, 4, 6, 10, 12, 18, 22)
SPACE = (0, 6, 12, 18)


def bar(section, harmony, melody, rhythm=SWING, texture="riff", change_at=12):
    notes = melody.split()
    if len(notes) != len(rhythm) or len(set(rhythm)) != len(rhythm):
        raise ValueError(f"Phrase mismatch: {section} {melody}")
    return {"section": section, "harmony": harmony.split(" | "),
            "melody": dict(zip(rhythm, notes)), "texture": texture, "change_at": change_at}


INTRO = [
    bar("Count-in riff", "Em6", "E5 G5 E5 B4", SPACE, "hits"),
    bar("Count-in riff", "F#half | B7", "A4 C5 B4 D#5 F#5 A5", ANSWER, "pickup"),
]

# A four-bar, mostly pentatonic hook. Its repetition is deliberate: a listener
# gets a tune to recognise, instead of a new unrelated run in every measure.
THEME = [
    bar("Night walk", "Em6", "E5 G5 A5 G5 E5 G5", HOOK),
    bar("Night walk", "Am9", "B5 A5 G5 E5 D5 B4", ANSWER),
    bar("Night walk", "Em9", "E5 E5 G5 A5 B5 A5 G5 E5", PUSH),
    bar("Night walk", "B7", "D#5 F#5 A5 B5 A5 F#5 D#5", SEVEN, "answer"),
    bar("Night walk", "Em6", "E5 G5 A5 B5 D6 B5", HOOK),
    bar("Night walk", "Cmaj9", "C6 B5 G5 E5 D5 E5", ANSWER, "answer"),
    bar("Night walk", "Am9 | B7b9", "A5 G5 E5 D5 C5 B4 D#5 F#5", SWING),
    bar("Night walk", "B7", "A5 F#5 D#5 B4 D5 D#5 F#5 B5", SWING, "turn"),
]

VERSE = [
    bar("Quickstep", "Em9", "E5 E5 G5 A5 G5 E5 D5 B4", PUSH, "dry"),
    bar("Quickstep", "Am9", "C5 E5 G5 A5 G5 E5 D5 C5", SWING, "dry"),
    bar("Quickstep", "D13", "F#5 A5 G5 E5 D5 F#5 A5 C6", PUSH, "dry"),
    bar("Quickstep", "Gmaj9", "B5 A5 G5 F#5 D5 E5 G5 B5", SWING, "answer"),
    bar("Quickstep", "Cmaj9", "G5 G5 E5 D5 C5 E5 G5 B5", PUSH, "dry"),
    bar("Quickstep", "F#half", "A5 G5 E5 C5 E5 G5 A5 C6", SWING, "dry"),
    bar("Quickstep", "B7b9", "B5 A5 F#5 D#5 C5 B4 D#5 F#5", SWING, "turn"),
    bar("Quickstep", "Em6 | B7", "G5 E5 D5 B4 D#5 F#5 A5 B5", (0, 4, 6, 10, 12, 16, 20, 22), "break"),
]

LIFT = [
    bar("Open the door", "Cmaj9", "G5 B5 A5 G5", SPACE, "open"),
    bar("Open the door", "Gmaj9", "F#5 G5 B5 D6", SPACE, "open"),
    bar("Open the door", "Am9", "C6 B5 A5 E5 G5 A5", HOOK, "open"),
    bar("Open the door", "D13", "F#5 A5 C6 B5 A5 F#5", ANSWER, "open"),
    bar("Open the door", "Cmaj9", "E5 G5 B5 D6 C6 B5", HOOK, "lift"),
    bar("Open the door", "Am9", "C6 B5 A5 G5 E5 G5 A5 C6", PUSH, "lift"),
    bar("Open the door", "F#half | B7b9", "A5 C6 E6 D6 C6 A5 F#5 D#5", SWING, "lift"),
    bar("Open the door", "B7", "F#5 A5 B5 D#6 B5 A5 F#5 D#5", SWING, "pickup"),
]

CHORUS = [
    bar("Dancing on the edge", "Gmaj9", "B5 A5 G5 D5 E5 G5", HOOK, "chorus"),
    bar("Dancing on the edge", "D13", "A5 G5 F#5 E5 D5 F#5", ANSWER, "chorus"),
    bar("Dancing on the edge", "Em9", "G5 B5 D6 B5 A5 G5 E5 D5", SWING, "chorus"),
    bar("Dancing on the edge", "B7", "D#5 F#5 A5 B5 A5 F#5 D#5", SEVEN, "answer"),
    bar("Dancing on the edge", "Cmaj9", "G5 B5 C6 B5 G5 E5", HOOK, "chorus"),
    bar("Dancing on the edge", "Gmaj9", "D6 B5 A5 G5 F#5 G5", ANSWER, "chorus"),
    bar("Dancing on the edge", "Am9 | D13", "C6 B5 A5 G5 F#5 A5 C6 D6", SWING, "chorus"),
    bar("Dancing on the edge", "Gmaj9 | B7", "B5 A5 G5 D5 D#5 F#5 A5 B5", PUSH, "turn"),
    bar("Dancing on the edge", "Em6", "E5 G5 A5 G5 E5 G5", HOOK, "chorus"),
    bar("Dancing on the edge", "Am9", "B5 A5 G5 E5 D5 B4", ANSWER, "answer"),
    bar("Dancing on the edge", "Em9", "E5 E5 G5 A5 B5 A5 G5 E5", PUSH, "chorus"),
    bar("Dancing on the edge", "B7", "D#5 F#5 A5 B5 A5 F#5 D#5", SEVEN, "chorus"),
    bar("Dancing on the edge", "Cmaj9", "E6 D6 B5 G5 A5 B5", HOOK, "chorus"),
    bar("Dancing on the edge", "A13 | Am6", "C#6 B5 A5 G5 F#5 E5", ANSWER, "answer"),
    bar("Dancing on the edge", "F#half | B7b9", "A5 G5 E5 C5 B4 D#5 F#5 A5", SWING, "chorus"),
    bar("Dancing on the edge", "Em6", "G5 E5 D5 B4 E5 G5 A5 B5", PUSH, "break"),
]

TAG = [
    bar("Last turn", "Cmaj9 | Am9", "G5 E5 D5 C5 E5 G5", HOOK, "open"),
    bar("Last turn", "F#half | B7", "A5 F#5 E5 C5 B4 D#5", ANSWER, "answer"),
    bar("Last turn", "Em6", "E5 G5 A5 G5 E5 G5", HOOK, "riff"),
    bar("Last turn", "A13 | Am6", "C#6 B5 A5 G5 F#5 E5", ANSWER, "open"),
    bar("Last turn", "F#half | B7", "A5 F#5 E5 D#5 B4 D#5", (0, 4, 6, 12, 16, 20), "cadence"),
    bar("Last turn", "B7 | Em", "F#5 D#5 E5", (0, 2, 4), "seal", change_at=4),
]

BARS = INTRO + THEME + VERSE + LIFT + CHORUS + TAG


def pitch_name(number):
    return f"{PITCH_NAMES[number % 12]}{number // 12 - 1}"


def physical(pitch):
    key = PITCH_TO_KEY[pitch]
    return key.upper() if key.isalpha() else key.translate(str.maketrans("!@$%^*(", "1245689"))


def place(pitches, reserved, low=48, high=77):
    chosen = set()
    for pitch in pitches:
        if pitch in reserved or pitch in chosen:
            continue
        number = pitch_number(pitch)
        used = {physical(p) for p in reserved | chosen}
        candidates = [pitch_name(number + shift) for shift in (0, -12, 12, -24, 24)
                      if low <= number + shift <= high]
        candidate = next((p for p in candidates if physical(p) not in used), None)
        if candidate is None:
            raise ValueError(f"Cannot place {pitch} against {reserved | chosen}")
        chosen.add(candidate)
    return chosen


def make_score():
    if len(BARS) != 48:
        raise ValueError("The compact form needs 48 bars")
    score = []
    for number, measure in enumerate(BARS, 1):
        texture = measure["texture"]
        voices = {name: [set() for _ in range(24)] for name in ("lead", "bass", "comp")}
        lead = measure["melody"]
        for slot, pitch in lead.items():
            voices["lead"][slot].add(pitch)

        def reserved(slot):
            return set().union(*(voice[slot] for voice in voices.values()))

        def harmony_at(slot):
            name = measure["harmony"][min(slot // measure["change_at"], len(measure["harmony"]) - 1)]
            root, walk, chord = HARMONIES[name]
            return root, walk.split(), chord.split()

        bass_slots = (0, 6, 12, 18)
        if texture in ("open", "hits", "break"):
            bass_slots = (0, 12)
        elif texture == "seal":
            bass_slots = (0, 4)
        for slot in bass_slots:
            root, walk, _ = harmony_at(slot)
            note = root if texture in ("open", "hits", "seal") else walk[(slot // 6) % 4]
            voices["bass"][slot].update(place([note], reserved(slot), 36, 59))

        comp_slots = {
            "riff": (4, 16), "dry": (4, 10, 22), "answer": (4, 16),
            "open": (0, 12), "lift": (4, 10, 16, 22),
            "chorus": (4, 10, 16, 22), "turn": (4, 10, 16),
            "hits": (0, 6, 12, 18), "pickup": (4, 12, 18),
            "break": (0, 12), "cadence": (0, 6, 12, 20), "seal": (0, 4),
        }[texture]
        for slot in comp_slots:
            _, _, chord = harmony_at(slot)
            if texture in ("riff", "dry", "answer"):
                chord = chord[:2]
            if texture == "seal":
                chord = ["D#4", "A4"] if slot == 0 else ["B2", "G3", "B3", "E4", "G4"]
            voices["comp"][slot].update(place(chord, reserved(slot), 47 if texture == "seal" else 48, 79))

        grid = [sorted(reserved(slot), key=pitch_number) for slot in range(24)]
        holds = [None] * 24
        lead_slots = list(lead)
        for slot, pitches in enumerate(grid):
            if not pitches:
                continue
            if slot in lead:
                index = lead_slots.index(slot)
                if index + 1 < len(lead_slots):
                    next_slot = lead_slots[index + 1]
                elif number < len(BARS):
                    next_slot = 24 + min(BARS[number]["melody"])
                else:
                    next_slot = 24
                # Sung phrases use a small breath before their next note.
                hold = max(70, min(620, round((next_slot - slot) * NOTE_DELAY_MS * .88)))
            elif voices["comp"][slot]:
                hold = 520 if texture == "open" else 220 if texture in ("dry", "hits") else 300
            else:
                hold = 350
            if texture == "seal":
                hold = 800 if slot == 4 else 120
            holds[slot] = hold
        if any(len(pitches) > 7 for pitches in grid):
            raise ValueError(f"Chord too large in bar {number}")
        score.append({"bar": number, "section": measure["section"], "harmony": measure["harmony"],
                      "change_at": measure["change_at"], "texture": texture,
                      "voices": {name: [{"slot": slot, "pitches": sorted(pitches, key=pitch_number),
                                         "hold_ms": holds[slot]}
                                        for slot, pitches in enumerate(voice) if pitches]
                                 for name, voice in voices.items()}, "grid": grid, "holds_ms": holds})
    encode_plain_sheet(score)  # Independently validates the physical keyboard layout.
    return score


def make_sheet(score):
    plain = encode_plain_sheet(score)
    measures = iter(score)
    lines = []
    for line in plain.splitlines():
        if not line:
            lines.append("")
            continue
        measure = next(measures)
        tokens = line.split()
        for slot, hold in enumerate(measure["holds_ms"]):
            if hold is not None and hold != KEY_HOLD_MS:
                tokens[slot] += f"<{hold}>"
        lines.append(" ".join(tokens))
    return "\n".join(lines) + "\n"


def main():
    score = make_score()
    directory = ROOT / "assets/originals"
    directory.mkdir(parents=True, exist_ok=True)
    sheet_path = ROOT / "assets/songs" / f"{SONG_ID}.txt"
    sheet_path.write_text(make_sheet(score), encoding="utf-8")
    document = {"title": TITLE, "original": True, "revision": "short-opening-form",
                "inspiration": "Beastars / Wild Side: compact shuffle feel; original melody",
                "bpm": BPM, "meter": "4/4", "grid": "sextuplet", "swing_ratio": "2:1",
                "slots_per_bar": SLOTS_PER_BAR, "duration_ms": DURATION_MS,
                "note_delay_ms": NOTE_DELAY_MS, "key_hold_ms": KEY_HOLD_MS, "bars": score}
    (directory / f"{SONG_ID}-score.json").write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(score)} bars, {DURATION_MS / 1000:.2f} s: {sheet_path}")


if __name__ == "__main__":
    main()
