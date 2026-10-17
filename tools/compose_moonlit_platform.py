"""Original piano miniature: Moonlit Platform.

The written pitches and rhythm below are the composition, not imported sheets.
One grid slot is a sixteenth at 100 BPM (150 ms); each line is one 4/4 bar.
Run from any directory to regenerate the bundled sheet and readable score.
"""
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SONG_ID = "moonlit-platform"
TITLE = "Moonlit Platform"
BPM = 100
NOTE_DELAY_MS = 150
KEY_HOLD_MS = 200
SLOTS_PER_BAR = 16

# PlayPianoSheets' untransposed keyboard. Standard MIDI uses C4 = 60.
WHITE_KEYS = "1234567890qwertyuiopasdfghjklzxcvbnm"
WHITE_PITCHES = (
    "C2 D2 E2 F2 G2 A2 B2 C3 D3 E3 F3 G3 A3 B3 C4 D4 E4 "
    "F4 G4 A4 B4 C5 D5 E5 F5 G5 A5 B5 C6 D6 E6 F6 G6 A6 B6 C7"
).split()
BLACK_KEYS = "!@$%^*(QWETYIOPSDGHJLZCVB"
BLACK_PITCHES = (
    "C#2 D#2 F#2 G#2 A#2 C#3 D#3 F#3 G#3 A#3 C#4 D#4 F#4 G#4 A#4 "
    "C#5 D#5 F#5 G#5 A#5 C#6 D#6 F#6 G#6 A#6"
).split()
PITCH_TO_KEY = dict(zip(WHITE_PITCHES + BLACK_PITCHES, WHITE_KEYS + BLACK_KEYS, strict=True))

# name: quarter-note bass root, fifth, and a four-note middle-register voicing.
HARMONIES = {
    "Am9": ("A2", "E3", "G3 B3 C4 E4"),
    "Dm9": ("D2", "A2", "F3 A3 C4 E4"),
    "G13": ("G2", "D3", "F3 B3 E4 A4"),
    "Cmaj9": ("C2", "G2", "E3 G3 B3 D4"),
    "Fmaj9": ("F2", "C3", "E3 A3 C4 G4"),
    "Bm7b5": ("B2", "F3", "A3 B3 D4 F4"),
    "E7b9": ("E2", "B2", "G#3 B3 D4 F4"),
    "E7": ("E2", "B2", "G#3 B3 D4 E4"),
    "Am6": ("A2", "E3", "F#3 A3 C4 E4"),
    "Fm6": ("F2", "C3", "G#3 C4 D4 F4"),
    "Cmaj9/E": ("E2", "G2", "G3 B3 D4 E4"),
    "A7b9": ("A2", "E3", "G3 A#3 C#4 E4"),
    "G7b9": ("G2", "D3", "F3 G#3 B3 D4"),
}

MOTIF = (0, 3, 4, 6, 8, 11, 12, 14)
FLOW = (0, 2, 4, 6, 8, 10, 12, 14)
LIFT = (0, 2, 3, 6, 8, 10, 12, 15)
INTRO = (0, 4, 8, 10, 12, 14)
ENDING = (0, 4, 8, 12)


def bar(section, harmony, melody, rhythm=MOTIF, texture="full"):
    pitches = melody.split()
    if len(pitches) != len(rhythm):
        raise ValueError("Every melody pitch needs an explicit grid position")
    return {"section": section, "harmony": harmony.split(" | "),
            "melody": dict(zip(rhythm, pitches)), "texture": texture}


# Four-bar introduction, A / varied A / contrasting B / returning A, four-bar coda.
# The short-long pickups at slots 3 and 11 are the recurring melodic fingerprint.
BARS = [
    bar("Intro", "Am9", "E5 B4 C5 E5 G5 A5", INTRO, "sparse"),
    bar("Intro", "Dm9", "F5 E5 D5 C5 A4 D5", INTRO, "sparse"),
    bar("Intro", "G13", "B4 D5 E5 G5 A5 B5", INTRO, "sparse"),
    bar("Intro", "Cmaj9 | E7", "G5 E5 D5 B4 G#4 B4", INTRO, "sparse"),

    bar("A", "Am9", "E5 A5 C6 B5 A5 G5 E5 G5"),
    bar("A", "Dm9", "F5 A5 C6 A5 F5 E5 D5 C5"),
    bar("A", "G13", "D5 G5 B5 A5 G5 E5 D5 B4"),
    bar("A", "Cmaj9", "E5 G5 B5 D6 C6 B5 G5 E5"),
    bar("A", "Fmaj9", "A5 C6 E6 D6 C6 A5 G5 E5"),
    bar("A", "Bm7b5 | E7b9", "D5 F5 A5 B5 G#5 F5 E5 D5"),
    bar("A", "Am9", "E5 A5 C6 B5 A5 E5 G5 A5"),
    bar("A", "E7", "G#5 B5 E6 D6 B5 G#5 E5 B4", LIFT),

    bar("A variation", "Am9", "E5 A5 C6 E6 D6 C6 B5 A5"),
    bar("A variation", "Dm9", "F5 A5 D6 C6 A5 G5 F5 E5", LIFT),
    bar("A variation", "G13", "D5 G5 B5 D6 E6 D6 B5 G5"),
    bar("A variation", "Cmaj9", "E5 G5 C6 B5 G5 E5 D5 B4", FLOW),
    bar("A variation", "Fmaj9", "A5 C6 E6 G6 E6 D6 C6 A5"),
    bar("A variation", "Dm9 | E7b9", "F5 E5 D5 A5 G#5 B5 D6 F6", LIFT),
    bar("A variation", "Am9 | E7", "E6 C6 B5 A5 G#5 E5 D5 B4", FLOW),
    bar("A variation", "Am9", "C5 E5 A5 B5 C6 B5 A5 E5"),

    bar("B", "Fmaj9", "C6 - A5 G5 E5 G5 A5 C6", FLOW),
    bar("B", "Fm6", "D6 C6 G#5 G5 F5 G#5 C6 D6", LIFT),
    bar("B", "Cmaj9/E", "E6 D6 B5 G5 E5 G5 B5 D6", FLOW),
    bar("B", "A7b9", "C#6 E6 G6 E6 C#6 A#5 G5 E5"),
    bar("B", "Dm9", "F5 A5 D6 E6 F6 E6 D6 A5", FLOW),
    bar("B", "G7b9", "B5 D6 F6 G#6 F6 D6 B5 G#5", LIFT),
    bar("B", "Cmaj9", "G5 B5 E6 D6 C6 B5 G5 E5", FLOW),
    bar("B", "E7b9", "F5 G#5 B5 D6 F6 E6 D6 B5", LIFT),

    bar("A return", "Am9", "E5 A5 C6 B5 A5 G5 E5 G5"),
    bar("A return", "Dm9", "F5 A5 C6 D6 C6 A5 F5 E5"),
    bar("A return", "G13", "D5 G5 B5 A5 G5 E5 D5 B4"),
    bar("A return", "Cmaj9", "E5 G5 B5 D6 E6 D6 C6 B5", LIFT),
    bar("A return", "Fmaj9", "A5 C6 E6 D6 C6 A5 G5 E5"),
    bar("A return", "Bm7b5 | E7b9", "D5 F5 A5 C6 B5 G#5 F5 D5", FLOW),
    bar("A return", "Am9 | E7", "E5 A5 C6 E6 D6 B5 G#5 E5"),
    bar("A return", "Am6", "C6 B5 A5 E5 F#5 E5 C5 A4", FLOW),

    bar("Coda", "Dm9 | G13", "F5 A5 C6 B5 G5 D5", INTRO, "sparse"),
    bar("Coda", "Cmaj9 | E7b9", "E5 G5 B5 G#5 F5 D5", INTRO, "sparse"),
    bar("Coda", "Am9 | E7", "E5 A5 C6 B5 G#5 E5", INTRO, "sparse"),
    bar("Coda", "Am6", "A5 E5 C5 A4", ENDING, "ending"),
]


def make_score():
    """Combine independent bass, inner voices and the explicitly written lead."""
    result = []
    for number, measure in enumerate(BARS, 1):
        grid = [set() for _ in range(SLOTS_PER_BAR)]
        texture = measure["texture"]
        pulses = range(0, 16, 2) if texture == "full" else (0, 4, 8, 12)
        for slot in pulses:
            harmony = measure["harmony"][min(slot // 8, len(measure["harmony"]) - 1)]
            root, fifth, voicing_text = HARMONIES[harmony]
            voicing = voicing_text.split()
            if texture == "ending":
                # The opening tonic supports the coda's four descending notes.
                accompaniment = [root, *voicing] if slot == 0 else []
            elif texture == "sparse":
                accompaniment = [root] if slot == 0 else [fifth] if slot == 8 else voicing
            elif slot % 4 == 2:
                accompaniment = voicing if slot in (2, 10) else voicing[1:]
            elif slot in (0, 8):
                accompaniment = [root, voicing[slot // 8], voicing[2]]
            else:
                accompaniment = [fifth, voicing[-1]]
            grid[slot].update(accompaniment)
        for slot, pitch in measure["melody"].items():
            if pitch != "-":
                grid[slot].add(pitch)
        result.append({"bar": number, "section": measure["section"],
                       "harmony": measure["harmony"],
                       "melody": [{"slot": slot, "pitch": pitch}
                                  for slot, pitch in measure["melody"].items() if pitch != "-"],
                       "grid": [sorted(pitches, key=pitch_number) for pitches in grid]})
    return result


def pitch_number(pitch):
    semitones = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    return 12 * (int(pitch[-1]) + 1) + semitones[pitch[0]] + ("#" in pitch)


def make_sheet(score):
    lines = []
    previous_section = None
    for measure in score:
        if previous_section is not None and measure["section"] != previous_section:
            lines.append("")
        tokens = []
        for pitches in measure["grid"]:
            keys = "".join(PITCH_TO_KEY[pitch] for pitch in pitches)
            # Different pitches cannot share a physical key inside one chord.
            physical = [key.upper() if key.isalpha() else key.translate(str.maketrans("!@$%^*(", "1245689")) for key in keys]
            if len(set(physical)) != len(physical):
                raise ValueError(f"Physical-key collision in bar {measure['bar']}: {pitches}")
            tokens.append("-" if not keys else keys if len(keys) == 1 else f"[{keys}]")
        lines.append(" ".join(tokens))
        previous_section = measure["section"]
    return "\n".join(lines) + "\n"


def main():
    score = make_score()
    target = ROOT / "assets/songs" / f"{SONG_ID}.txt"
    target.write_text(make_sheet(score), encoding="utf-8")
    document = {"title": TITLE, "original": True,
                "bpm": BPM, "meter": "4/4", "grid": "sixteenth",
                "note_delay_ms": NOTE_DELAY_MS, "key_hold_ms": KEY_HOLD_MS,
                "bars": score}
    directory = ROOT / "assets/originals"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{SONG_ID}-score.json").write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(score)} bars, {len(score) * 16 * NOTE_DELAY_MS / 1000:.1f} s: {target}")


if __name__ == "__main__":
    main()
