"""Starlight Chase: original melodic piano piece in D minor, 120 BPM.

80 measures in 4/4 = 160 seconds. The score uses sixteenth-note slots, but
most of the melody moves in eighths; short runs are saved for development.
"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.compose_moonlit_platform import PITCH_TO_KEY, make_sheet, pitch_number

SONG_ID = "starlight-chase"
TITLE = "Starlight Chase"
BPM = 120
NOTE_DELAY_MS = 125
KEY_HOLD_MS = 200
SLOTS_PER_BAR = 16

# Bass root/fifth and middle-register voicing; enharmonics use sharps because
# these are literal keyboard pitches, not conventional engraved spellings.
HARMONIES = {
    "Dm9": ("D2", "A2", "F3 A3 C4 E4"),
    "Dm6/9": ("D2", "A2", "F3 A3 B3 E4"),
    "Bbmaj9": ("A#2", "F3", "A3 C4 D4 F4"),
    "Gm9": ("G2", "D3", "A#3 D4 F4 A4"),
    "A7b9": ("A2", "E3", "G3 A#3 C#4 E4"),
    "A7": ("A2", "E3", "G3 C#4 E4 A4"),
    "A7sus": ("A2", "E3", "G3 D4 E4 A4"),
    "Fmaj9": ("F2", "C3", "A3 C4 E4 G4"),
    "C13": ("C3", "G2", "A#3 D4 E4 A4"),
    "D7b9": ("D2", "A2", "F#3 C4 D#4 A4"),
    "Em7b5": ("E2", "A#2", "G3 A#3 D4 E4"),
    "Dm9/F": ("F2", "A2", "A3 C4 D4 E4"),
    "Cmaj9": ("C3", "G2", "E3 G3 B3 D4"),
    "F6": ("F2", "C3", "A3 C4 D4 F4"),
    "G13": ("G2", "D3", "F3 B3 E4 A4"),
    "Bb6": ("A#2", "F3", "G3 A#3 D4 F4"),
    "Bbm6": ("A#2", "F3", "G3 A#3 C#4 F4"),
    "Eb9": ("D#3", "A#2", "G3 C#4 F4 A#4"),
}

HOOK = (0, 2, 4, 7, 8, 10, 12, 14)
ANSWER = (0, 3, 4, 6, 8, 11, 12, 14)
FLOW = (0, 2, 4, 6, 8, 10, 12, 14)
SPACE = (0, 4, 6, 8, 12, 14)
RUN = (0, 2, 4, 6, 7, 8, 10, 12, 13, 14, 15)
END = (0, 4, 8)


def bar(section, harmony, melody, rhythm=HOOK, texture="pulse"):
    notes = melody.split()
    if len(notes) != len(rhythm):
        raise ValueError(f"Pitch/rhythm mismatch in {section}: {melody}")
    return {"section": section, "harmony": harmony.split(" | "),
            "melody": dict(zip(rhythm, notes)), "texture": texture}


INTRO = [
    bar("Intro", "Dm9", "A4 D5 F5 A5 G5 E5", SPACE, "open"),
    bar("Intro", "Bbmaj9", "F5 A5 D6 C6 A5 F5", SPACE, "open"),
    bar("Intro", "Gm9 | A7sus", "D5 G5 A#5 A5 G5 E5 D5 E5", ANSWER),
    bar("Intro", "A7b9", "C#5 E5 G5 A#5 A5 G5 E5 A5", FLOW),
]

VERSE = [
    bar("Verse", "Dm9", "A5 D6 C6 A5 F5 G5 A5 E5"),
    bar("Verse", "Bbmaj9", "F5 A5 G5 F5 E5 D5 C5 A4", ANSWER),
    bar("Verse", "Gm9", "D5 F5 A#5 A5 G5 A5 D6 C6"),
    bar("Verse", "A7b9", "A#5 A5 G5 E5 C#5 E5 G5 A5", ANSWER),
    bar("Verse", "Dm9", "A5 D6 C6 A5 F5 G5 A5 C6"),
    bar("Verse", "Fmaj9", "E6 C6 A5 G5 F5 A5 C6 D6", FLOW),
    bar("Verse", "Bbmaj9", "F6 E6 D6 C6 A5 G5 F5 D5", ANSWER),
    bar("Verse", "A7", "E5 G5 A5 C#6 E6 D6 C#6 A5"),
    bar("Verse", "Dm9", "F5 A5 D6 E6 F6 E6 D6 A5"),
    bar("Verse", "C13", "G5 E5 D5 C5 D5 E5 G5 A5", ANSWER),
    bar("Verse", "Fmaj9", "C6 A5 G5 E5 F5 G5 A5 C6"),
    bar("Verse", "G13", "B5 A5 G5 E5 D5 E5 F5 A5", FLOW),
    bar("Verse", "Gm9", "A#5 A5 G5 D5 F5 A5 A#5 D6"),
    bar("Verse", "Em7b5", "F6 D6 A#5 G5 F5 G5 A#5 D6", ANSWER),
    bar("Verse", "A7sus | A7", "E6 D6 A5 G5 E5 C#5 E5 G5", FLOW),
    bar("Verse", "Dm9", "F5 A5 D6 C6 A5 F5 E5 D5", ANSWER),
]

CHORUS = [
    bar("Chorus", "Fmaj9", "C6 A5 G5 F5 A5 C6 D6 E6", texture="lift"),
    bar("Chorus", "C13", "D6 C6 A5 G5 E5 G5 A5 C6", ANSWER, "lift"),
    bar("Chorus", "Dm9", "F6 E6 D6 C6 A5 C6 D6 F6", texture="lift"),
    bar("Chorus", "Bbmaj9", "E6 D6 C6 A5 F5 A5 C6 D6", FLOW, "lift"),
    bar("Chorus", "Gm9", "A#5 D6 F6 E6 D6 A#5 A5 G5", texture="lift"),
    bar("Chorus", "D7b9", "F#5 A5 C6 D#6 D6 C6 A5 F#5", ANSWER, "lift"),
    bar("Chorus", "Gm9 | C13", "G5 A5 A#5 D6 C6 A5 G5 E5", texture="lift"),
    bar("Chorus", "Fmaj9 | A7", "F5 A5 C6 E6 C#6 A#5 A5 G5", ANSWER, "lift"),
    bar("Chorus", "Dm9", "A5 D6 C6 A5 F5 G5 A5 C6", texture="lift"),
    bar("Chorus", "Bbmaj9", "D6 F6 E6 D6 C6 A5 F5 E5", FLOW, "lift"),
    bar("Chorus", "Gm9", "G5 A#5 D6 F6 D6 A#5 A5 G5", texture="lift"),
    bar("Chorus", "A7b9", "E5 G5 A#5 C#6 E6 C#6 A#5 G5", ANSWER, "lift"),
    bar("Chorus", "Dm9", "A5 C6 D6 F6 E6 D6 C6 A5", texture="lift"),
    bar("Chorus", "Bbmaj9", "F5 A5 D6 E6 F6 E6 D6 C6", ANSWER, "lift"),
    bar("Chorus", "Em7b5 | A7b9", "A#5 G5 F5 D5 E5 G5 A#5 C#6", FLOW, "lift"),
    bar("Chorus", "Dm9", "D6 A5 F5 E5 D5 F5 A5 D6", ANSWER, "lift"),
]

BRIDGE = [
    bar("Bridge", "Bbmaj9", "D6 - C6 A5 F5 A5", SPACE, "open"),
    bar("Bridge", "Bbm6", "C#6 F6 C#6 A#5 G5 F5", SPACE, "open"),
    bar("Bridge", "Fmaj9", "C6 A5 G5 E5 F5 A5", SPACE, "open"),
    bar("Bridge", "Cmaj9 | A7", "G5 B5 D6 E6 C#6 A5", SPACE, "open"),
    bar("Bridge", "Dm9/F", "F5 A5 C6 D6 E6 D6", SPACE, "open"),
    bar("Bridge", "Gm9 | Eb9", "D6 A#5 A5 G5 F5 C#5", SPACE, "open"),
    bar("Bridge", "Em7b5", "D5 F5 G5 A#5 D6 F6", SPACE),
    bar("Bridge", "A7sus | A7b9", "E6 D6 A#5 A5 G5 E5 C#5 A4", FLOW),
]

DEVELOPMENT = [
    bar("Development", "Dm9", "D5 F5 A5 C6 D6 C6 A5 G5 F5 E5 D5", RUN, "run"),
    bar("Development", "Bbmaj9", "F5 A5 C6 D6 F6 E6 D6 C6 A5 G5 F5", RUN, "run"),
    bar("Development", "Gm9", "D5 G5 A#5 D6 F6 E6 D6 C6 A#5 A5 G5", RUN, "run"),
    bar("Development", "A7b9", "E5 G5 A#5 C#6 E6 D6 C#6 A#5 A5 G5 E5", RUN, "run"),
    bar("Development", "Dm9 | D7b9", "F5 A5 D6 F6 E6 D#6 C6 A5", FLOW, "lift"),
    bar("Development", "Gm9 | C13", "A#5 D6 F6 E6 D6 C6 A5 G5", ANSWER, "lift"),
    bar("Development", "Fmaj9 | Bb6", "A5 C6 E6 G6 F6 D6 C6 A#5", FLOW, "lift"),
    bar("Development", "A7sus | A7b9", "A5 G5 E5 D5 C#5 E5 G5 A#5", ANSWER, "lift"),
]

# Reprise uses a recognisable chorus with newly written answers in its second
# half. Only the first eight bars recur unchanged; contrast comes from phrasing.
FINAL_CHORUS = [dict(measure, section="Final chorus") for measure in CHORUS[:8]] + [
    bar("Final chorus", "Dm9", "A5 D6 F6 E6 D6 C6 A5 F5", texture="lift"),
    bar("Final chorus", "Bbmaj9", "A5 C6 D6 F6 A6 G6 F6 D6", ANSWER, "lift"),
    bar("Final chorus", "Gm9", "F6 D6 A#5 A5 G5 A#5 D6 F6", texture="lift"),
    bar("Final chorus", "A7b9", "E6 C#6 A#5 G5 E5 G5 A#5 C#6", FLOW, "lift"),
    bar("Final chorus", "Dm9", "D6 F6 A6 G6 F6 E6 D6 C6", texture="lift"),
    bar("Final chorus", "Bbmaj9", "A5 D6 F6 E6 D6 C6 A5 F5", ANSWER, "lift"),
    bar("Final chorus", "Em7b5 | A7b9", "G5 A#5 D6 F6 E6 C#6 A#5 G5", FLOW, "lift"),
    bar("Final chorus", "Dm6/9", "A5 D6 C6 A5 F5 E5 D5 A4", ANSWER, "lift"),
]

FINAL_THEME = [
    bar("Final theme", "Dm9", "A5 D6 C6 A5 F5 G5 A5 E5"),
    bar("Final theme", "Bbmaj9", "F5 A5 G5 F5 E5 D5 C5 A4", ANSWER),
    bar("Final theme", "Gm9", "D5 F5 A#5 D6 C6 A#5 A5 G5"),
    bar("Final theme", "A7b9", "E5 G5 A#5 C#6 E6 D6 C#6 A5", ANSWER),
    bar("Final theme", "Dm9/F | Bbmaj9", "F5 A5 D6 F6 E6 D6 C6 A5", FLOW, "lift"),
    bar("Final theme", "Gm9 | C13", "G5 A#5 D6 F6 E6 D6 C6 A5", ANSWER, "lift"),
    bar("Final theme", "Em7b5 | A7b9", "G5 A#5 D6 F6 E6 C#6 A#5 G5", FLOW, "lift"),
    bar("Final theme", "Dm9", "A5 D6 C6 A5 F5 E5 D5 F5", ANSWER),
]

CODA = [
    bar("Coda", "Bbmaj9 | Gm9", "A5 D6 C6 A5 G5 F5", SPACE, "open"),
    bar("Coda", "Em7b5 | A7b9", "G5 A#5 D6 C#6 A#5 G5", SPACE, "open"),
    bar("Coda", "Dm9 | A7", "F5 A5 D6 C6 C#6 E6", SPACE),
    bar("Coda", "Dm6/9", "D6 A5 D5", END, "ending"),
]

BARS = INTRO + VERSE + CHORUS + BRIDGE + DEVELOPMENT + FINAL_CHORUS + FINAL_THEME + CODA


def make_score():
    score = []
    for number, measure in enumerate(BARS, 1):
        grid = [set() for _ in range(SLOTS_PER_BAR)]
        texture = measure["texture"]
        pulses = range(0, 16, 2) if texture in ("pulse", "lift") else (0, 4, 8, 12)
        for slot in pulses:
            harmony = measure["harmony"][min(slot // 8, len(measure["harmony"]) - 1)]
            root, fifth, voice_text = HARMONIES[harmony]
            voice = voice_text.split()
            if texture == "ending":
                notes = [root, fifth, *voice] if slot in (0, 8) else []
            elif texture == "open":
                notes = [root] if slot == 0 else [fifth] if slot == 8 else voice[1:]
            elif texture == "run":
                # A lighter left hand keeps the four short lead runs distinct.
                notes = [root, voice[0]] if slot in (0, 8) else [fifth, voice[2]]
            elif slot % 4 == 2:
                notes = voice if texture == "lift" and slot in (2, 10) else voice[1:]
            elif slot in (0, 8):
                notes = [root, voice[0], voice[2]]
                if texture == "lift":
                    notes.append(voice[-1])
            else:
                notes = [fifth, voice[-1]]
            grid[slot].update(notes)
        for slot, pitch in measure["melody"].items():
            if pitch != "-":
                grid[slot].add(pitch)
        score.append({"bar": number, "section": measure["section"],
                      "harmony": measure["harmony"],
                      "melody": [{"slot": slot, "pitch": pitch}
                                 for slot, pitch in measure["melody"].items() if pitch != "-"],
                      "grid": [sorted(pitches, key=pitch_number) for pitches in grid]})
    return score


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
