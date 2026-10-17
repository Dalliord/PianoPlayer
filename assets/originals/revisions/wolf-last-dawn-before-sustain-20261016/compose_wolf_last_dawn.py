"""Until We Reach the Dawn: an original symphonic fantasy for piano.

125 bars, 4/4, 100 BPM, 32 thirty-second slots per bar: exactly 300 seconds.
Two themes fight, answer and finally join. Beastars inspires the dramatic
premise, not the notes: no soundtrack melody is quoted. This is piano music,
not a claim to have recorded an orchestra or objectively ranked its difficulty.
"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.compose_moonlit_platform import PITCH_TO_KEY, make_sheet, pitch_number

SONG_ID = "wolf-last-dawn"
TITLE = "Until We Reach the Dawn"
BPM = 100
NOTE_DELAY_MS = 75
KEY_HOLD_MS = 150
SLOTS_PER_BAR = 32

# Root, fifth, eight-note broken-harmony path and a wide ceremonial voicing.
HARMONIES = {
    "Cm": ("C2", "G2", "C3 G3 C4 D#4 G3 C4 D4 D#4", "C3 D#4 G4 C5"),
    "Cm/G": ("G2", "C3", "G2 D#3 G3 C4 D3 G3 C4 D#4", "G3 C4 D#4 G4"),
    "Ab": ("G#2", "D#3", "G#2 D#3 G#3 C4 D#3 G#3 A#3 C4", "G#3 C4 D#4 G#4"),
    "Fm": ("F2", "C3", "F3 C4 F4 G#4 C4 G#3 F4 C4", "F3 G#3 C4 F4"),
    "G7": ("G2", "D3", "G3 D4 F4 B4 D4 F3 B3 D4", "G3 B3 D4 F4"),
    "G7b9": ("G2", "D3", "G3 D4 F4 G#4 B3 D4 F4 G#4", "G3 B3 F4 G#4"),
    "Eb": ("D#2", "A#2", "D#3 A#3 D#4 G4 A#3 G3 D#4 F4", "D#3 G3 A#3 D#4"),
    "Bb": ("A#2", "F3", "A#2 F3 A#3 D4 F3 A#3 C4 D4", "A#3 D4 F4 A#4"),
    "Dhalf": ("D2", "G#2", "D3 G#3 C4 F4 G#3 C4 D4 F4", "D3 F3 G#3 C4"),
    "Db": ("C#2", "G#2", "C#3 G#3 C#4 F4 G#3 C#4 D#4 F4", "C#3 F3 G#3 C#4"),
    "F#dim": ("F#2", "C3", "F#3 A3 C4 D#4 A3 C4 D#4 F#4", "F#3 A3 C4 D#4"),
    "C": ("C2", "G2", "C3 G3 C4 E4 G3 C4 D4 E4", "C3 E4 G4 C5"),
    "F": ("F2", "C3", "F3 C4 F4 A4 C4 A3 G4 F4", "F3 A3 C4 F4"),
    "Am": ("A2", "E3", "A2 E3 A3 C4 E4 C4 B3 A3", "A3 C4 E4 A4"),
    "Dm": ("D2", "A2", "D3 A3 D4 F4 A3 D4 E4 F4", "D3 F3 A3 D4"),
}

EIGHTHS = (0, 4, 8, 12, 16, 20, 24, 28)
SIGH = (0, 8, 12, 16, 24, 28)
VOW = (0, 6, 8, 14, 16, 22, 24, 28)
LOVE = (0, 8, 16, 22, 28)
QUARTERS = (0, 8, 16, 24)
SIXTEENTHS = tuple(range(0, 32, 2))
THIRTY_SECONDS = tuple(range(32))
COUNTER = tuple(range(2, 32, 4))


def bar(section, harmony, melody, rhythm=EIGHTHS, texture="woven", counter="", octave=False):
    notes = melody.split()
    if len(notes) != len(rhythm):
        raise ValueError(f"Pitch/rhythm mismatch in {section}: {len(notes)} / {len(rhythm)}")
    reply = counter.split()
    if reply and len(reply) != 8:
        raise ValueError("Countervoice needs eight independent offbeat notes")
    return {"section": section, "harmony": harmony.split(" | "),
            "melody": dict(zip(rhythm, notes)), "counter": reply,
            "texture": texture, "octave": octave}


PROLOGUE = [
    bar("Caged nocturne", "Cm", "G4 C5 D#5 D5 C5 B4", SIGH, "bells"),
    bar("Caged nocturne", "Ab", "C5 G#5 G5 D#5 C5 A#4", SIGH, "bells"),
    bar("Caged nocturne", "Fm | Db", "G#4 C5 F5 G#5 F5 C#5", SIGH, "bells"),
    bar("Caged nocturne", "G7b9", "D5 F5 G#5 G5 F5 B4", SIGH, "tremolo"),
]

# The vow's rising fourth and falling semitone recur through the entire work.
FATE = [
    bar("Vow in the dark", "Cm", "G4 C5 D#5 D5 G5 F5 D#5 D5", VOW),
    bar("Vow in the dark", "Ab", "C5 G#5 G5 D#5 F5 D#5 C5 A#4", EIGHTHS),
    bar("Vow in the dark", "Fm", "G#4 C5 F5 D#5 C5 D#5 F5 G#5", VOW),
    bar("Vow in the dark", "G7", "G5 F5 D5 B4 D5 F5 G5 B5", EIGHTHS),
    bar("Vow in the dark", "Cm", "C6 G5 D#5 D5 C5 D#5 G5 A#5", VOW),
    bar("Vow in the dark", "Eb", "G5 A#5 D#6 D6 A#5 G5 F5 D#5", EIGHTHS),
    bar("Vow in the dark", "Bb | Ab", "D5 F5 A#5 G#5 G5 F5 D#5 C5", VOW),
    bar("Vow in the dark", "G7b9", "B4 D5 F5 G#5 G5 F5 D5 B4", EIGHTHS, "tremolo"),
    bar("Vow in the dark", "Cm", "G4 C5 D#5 D5 G5 A#5 C6 G5", VOW,
        counter="C4 G3 D#4 G3 C4 G3 F4 D4"),
    bar("Vow in the dark", "Ab", "G#5 G5 F5 D#5 C5 D#5 F5 G#5", EIGHTHS,
        counter="G#3 C4 D#4 C4 G#3 A#3 C4 D#4"),
    bar("Vow in the dark", "Fm", "C6 G#5 F5 D#5 C5 G#4 C5 F5", VOW),
    bar("Vow in the dark", "Dhalf | G7", "G#5 F5 D5 C5 B4 D5 F5 G5", EIGHTHS, "tremolo"),
    bar("Vow in the dark", "Cm/G", "G5 C6 D#6 D6 C6 G5 F5 D#5", VOW, "octaves", octave=True),
    bar("Vow in the dark", "Db", "F5 G#5 C#6 C6 G#5 F5 D#5 C#5", EIGHTHS),
    bar("Vow in the dark", "G7b9", "D5 F5 G#5 B5 D6 F6 D6 B5", EIGHTHS, "tremolo"),
    bar("Vow in the dark", "Cm", "C6 G5 D#5 D5 C5 G4 D#4 C4", EIGHTHS, "fall"),
]

HUNT = [
    bar("Trial by fangs", "Cm", "C5 G5 D#5 D5 C6 G5 F5 D#5", EIGHTHS, "storm"),
    bar("Trial by fangs", "Ab", "C6 A#5 G#5 G5 F5 D#5 C5 D#5", VOW, "storm"),
    bar("Trial by fangs", "F#dim", "F#5 A5 C6 D#6 C6 A5 F#5 D#5", EIGHTHS, "tremolo"),
    bar("Trial by fangs", "G7b9", "D5 G5 B5 D6 F6 D6 B5 G#5", VOW, "storm"),
    bar("Trial by fangs", "Cm", "C5 D5 D#5 G5 C6 G5 F5 D#5 D5 C5 A#4 G4 D#4 G4 C5 D#5", SIXTEENTHS, "thin"),
    bar("Trial by fangs", "Fm", "F5 G5 G#5 C6 F6 D#6 C6 G#5 G5 F5 D#5 C5 G#4 C5 F5 G#5", SIXTEENTHS, "thin"),
    bar("Trial by fangs", "Db", "G#5 F5 C#5 G#4 C#6 G#5 F5 D#5", VOW, "octaves", octave=True),
    bar("Trial by fangs", "G7", "B4 D5 G5 F5 D5 B4 G4 D5", EIGHTHS, "tremolo"),
    bar("Trial by fangs", "Cm", "G5 C6 D#6 D6 G6 F6 D#6 D6", VOW, "storm"),
    bar("Trial by fangs", "Ab | Bb", "C6 G#5 G5 D#5 D5 F5 A#5 D6", EIGHTHS, "storm"),
    bar("Trial by fangs", "Eb", "D#6 D6 A#5 G5 F5 G5 A#5 D#6", VOW, "woven",
        counter="D#4 G4 A#4 G4 F4 D#4 D4 A#3"),
    bar("Trial by fangs", "Dhalf | G7b9", "F6 D6 C6 G#5 G5 F5 D5 B4", EIGHTHS, "storm"),
    bar("Trial by fangs", "Cm", "C5 D5 D#5 F5 G5 G#5 A#5 C6 D6 D#6 F6 G6 F6 D#6 D6 C6", SIXTEENTHS, "thin"),
    bar("Trial by fangs", "Db | G7b9", "C#6 C6 A#5 G#5 G5 F5 D5 B4 G4 B4 D5 F5 G#5 B5 D6 F6", SIXTEENTHS, "thin"),
    bar("Trial by fangs", "Cm/G", "D#6 D6 C6 G5 D#5 D5 C5 G4", EIGHTHS, "octaves", octave=True),
    bar("Trial by fangs", "Cm", "D#5 D5 C5 G4", QUARTERS, "silence"),
]

LAMENT = [
    bar("Fragile promise", "Ab", "D#5 C6 A#5 G#5 G5", LOVE, "lyric"),
    bar("Fragile promise", "Eb", "G5 A#5 D#6 D6 A#5", LOVE, "lyric"),
    bar("Fragile promise", "Fm", "G#5 G5 F5 C5 D#5", LOVE, "lyric"),
    bar("Fragile promise", "Bb", "F5 D6 C6 A#5 F5", LOVE, "lyric"),
    bar("Fragile promise", "Eb", "G5 A#5 D#6 F6 G6", LOVE, "lyric"),
    bar("Fragile promise", "Ab", "G#6 G6 D#6 C6 A#5", LOVE, "lyric"),
    bar("Fragile promise", "Fm | Db", "G#5 F5 C6 G#5 F5 C#5", SIGH, "lyric"),
    bar("Fragile promise", "G7b9", "D5 F5 G#5 G5 D5 B4", SIGH, "bells"),
]

FUGATO = [
    bar("Two voices one path", "Cm", "G5 C6 D#6 D6 G5 F5 D#5 D5", EIGHTHS, "duet",
        counter="C4 G4 D#4 D4 C4 D#4 G4 C5"),
    bar("Two voices one path", "G7", "B5 A5 G5 F5 D5 F5 G5 B5", EIGHTHS, "duet",
        counter="G3 D4 F4 B3 D4 G4 F4 D4"),
    bar("Two voices one path", "Cm", "C6 G5 D#5 D5 C5 D#5 G5 A#5", VOW, "duet",
        counter="G3 C4 D#4 D4 G4 F4 D#4 D4"),
    bar("Two voices one path", "Ab", "C6 A#5 G#5 G5 D#5 F5 G#5 C6", EIGHTHS, "duet",
        counter="D#4 C5 A#4 G#4 G4 F4 D#4 C4"),
    bar("Two voices one path", "Fm", "G#5 C6 F6 D#6 C6 G#5 G5 F5", VOW, "duet",
        counter="F3 C4 G#4 G4 F4 D#4 C4 G#3"),
    bar("Two voices one path", "Bb", "D6 C6 A#5 F5 D5 F5 A#5 D6", EIGHTHS, "duet",
        counter="F3 A#3 D4 C4 F4 D4 C4 A#3"),
    bar("Two voices one path", "Eb", "G5 A#5 D#6 D6 A#5 G5 F5 D#5", VOW, "duet",
        counter="D#4 A#4 G4 F4 D#4 G4 A#4 D#5"),
    bar("Two voices one path", "Ab | Db", "C6 G#5 G5 D#5 F5 G#5 C#6 F6", EIGHTHS, "duet",
        counter="G#3 D#4 C5 A#4 G#4 F4 D#4 C#4"),
    bar("Two voices one path", "Dhalf", "F6 D6 C6 G#5 F5 D5 F5 G#5", EIGHTHS, "duet",
        counter="D3 F3 G#3 C4 D4 F4 G#4 C5"),
    bar("Two voices one path", "G7b9", "B5 D6 F6 G#6 F6 D6 B5 G#5", VOW, "duet",
        counter="G3 B3 D4 F4 G#4 F4 D4 B3"),
    bar("Two voices one path", "Cm/G", "C6 D6 D#6 G6 F6 D#6 D6 C6", EIGHTHS, "storm",
        counter="G3 C4 D#4 G4 F4 D#4 D4 C4"),
    bar("Two voices one path", "G7b9", "B5 G#5 F5 D5 B4 D5 F5 G5", VOW, "tremolo"),
]

BREAKTHROUGH = [
    bar("Breaking the cage", "Cm", "G5 C6 D#6 D6 G6 F6 D#6 D6", VOW, "summit", octave=True),
    bar("Breaking the cage", "Ab", "C6 G#6 G6 D#6 F6 D#6 C6 A#5", EIGHTHS, "storm"),
    bar("Breaking the cage", "Fm", "C5 D5 D#5 F5 G5 G#5 A#5 C6 D6 D#6 F6 G6 G#6 G6 F6 D#6", SIXTEENTHS, "thin"),
    bar("Breaking the cage", "Db | G7b9", "C#6 F6 G#6 F6 D6 B5 G#5 F5", VOW, "summit", octave=True),
    bar("Breaking the cage", "Cm/G", "G4 C5 D#5 G5 C6 D6 D#6 F6 G6 F6 D#6 D6 C6 G5 F5 D#5 D5 C5 G4 D#4 C4 D#4 G4 C5 D5 D#5 G5 C6 D6 D#6 G6 C7", THIRTY_SECONDS, "thin"),
    bar("Breaking the cage", "G7b9", "B6 G#6 F6 D6 B5 G#5 F5 D5 B4 G#4 F4 D4 B3 D4 F4 G#4 B4 D5 F5 G#5 B5 D6 F6 G#6 F6 D6 B5 G#5 F5 D5 B4 G4", THIRTY_SECONDS, "thin"),
    bar("Breaking the cage", "Ab | Fm", "D#6 C6 A#5 G#5 G5 G#5 C6 F6", EIGHTHS, "summit", octave=True),
    bar("Breaking the cage", "Db | G7", "F6 D#6 C#6 C6 B5 D6 F6 G6", VOW, "summit", octave=True),
    bar("Breaking the cage", "C", "G5 C6 E6 D6 G6 E6 D6 C6", VOW, "summit", octave=True),
    bar("Breaking the cage", "F | Dm", "A5 C6 F6 E6 D6 F6 A6 G6", EIGHTHS, "storm"),
    bar("Breaking the cage", "Am | F", "E6 C6 A5 G5 F5 A5 C6 F6", VOW, "duet",
        counter="C4 E4 A4 G4 F4 A4 C5 A4"),
    bar("Breaking the cage", "Dm | G7", "F6 E6 D6 A5 B5 D6 F6 D6", EIGHTHS, "summit", octave=True),
]

DAWN = [
    bar("The earned dawn", "C", "G5 C6 E6 D6 G6 E6 D6 C6", VOW, "duet",
        counter="E4 C5 B4 A4 G4 A4 C5 G4"),
    bar("The earned dawn", "Am | F", "E6 C6 A5 G5 A5 C6 F6 E6", EIGHTHS, "woven"),
    bar("The earned dawn", "F | G7", "A5 C6 F6 E6 D6 B5 G5 D6", VOW, "duet",
        counter="F4 A4 C5 A4 G4 B4 D5 B4"),
    bar("The earned dawn", "C", "E6 G6 C7 B6 G6 E6 D6 C6", EIGHTHS, "summit", octave=True),
    bar("The earned dawn", "F | C", "A5 G5 F5 E5 D5 C5", SIGH, "lyric"),
    bar("The earned dawn", "Dm | G7", "F5 E5 D5 B4 D5 G5", SIGH, "lyric"),
    bar("The earned dawn", "C", "G5 C6 E6 C6", (0, 4, 8, 12), "last"),
]

# Compact voicings keep the restored phrases and chord attacks intact.
# Reduce simultaneous keys, never the number of attacks in the musical phrase.
MASSES = {
    "Cm9": "D#3 A#3 D4 G4 C5",
    "Abmaj9#11": "C4 G4 D5 A#4 D#5",
    "Fm11": "G#3 D#4 A#4 G4 C5",
    "G13b9#11": "B3 F4 G#4 C#5 E5",
    "Dbmaj9#11": "F3 C4 G4 D#5 G#4",
    "Dhalf11": "F3 C4 G#4 E5 G4",
    "F#dim": "A3 D#4 C5 F#4",
    "Ebmaj9": "G3 D4 F5 A#4 D#5",
    "Bb13": "D4 G#4 C5 G5 F4",
    "Cmaj13(no11)": "E3 B3 D4 A4 G4",
    "Fmaj9": "A3 E4 G4 C5 F4",
    "Am9": "C4 G4 B4 E5 A3",
    "Dm11": "F3 C4 E4 G4 A4",
    "Abm9": "B3 F#4 A#4 D#5 G#3",
    "E7b9": "G#3 D4 F4 B4 E4",
}

MASS_FOR_HARMONY = {
    "Cm": "Cm9", "Cm/G": "Cm9", "Ab": "Abmaj9#11", "Fm": "Fm11",
    "G7": "G13b9#11", "G7b9": "G13b9#11", "Db": "Dbmaj9#11", "Dhalf": "Dhalf11",
    "F#dim": "F#dim", "Eb": "Ebmaj9", "Bb": "Bb13", "C": "Cmaj13(no11)",
    "F": "Fmaj9", "Am": "Am9", "Dm": "Dm11",
}


def mass_bar(section, harmony, melody, rhythm=VOW, texture="impact", counter="", octave=False):
    return bar(section, harmony, melody, rhythm, texture, counter, octave)


# The original cadence now becomes a believable false ending. A whole empty
# bar follows its existing release; the drop begins at 3:02.4, not after Play.
FALSE_DAWN = [dict(measure, section="False dawn") for measure in DAWN]
FALSE_DAWN[-1] = bar("False dawn", "C", "G5 C6 E6 D6 B5 C6",
                     (0, 4, 8, 12, 14, 16), "false_cadence")
SILENT_BREATH = [bar("Silent breath", "C", "", (), "void")]

DROP = [
    mass_bar("Drop", "Cm", "G5 C6 D#6 D6 G6 F6 D#6 D6", texture="impact", octave=True),
    mass_bar("Drop", "Ab", "C6 G#6 G6 D#6 F6 D#6 C6 A#5", EIGHTHS, "fracture"),
    mass_bar("Drop", "Fm | Db", "C6 F6 G#6 G6 F6 C#6 C6 G#5", texture="impact", octave=True),
    mass_bar("Drop", "G7b9", "B5 D6 F6 G#6 F6 D6 B5 G#5", EIGHTHS, "barrage"),
    mass_bar("Drop", "Cm", "G5 C6 D#6 D6 C6 G5 F5 D#5", texture="barrage"),
    mass_bar("Drop", "Ab | Bb", "C6 A#5 G#5 G5 F5 A#5 D6 F6", EIGHTHS, "barrage"),
    mass_bar("Drop", "F#dim", "F#5 A5 C6 D#6 F#6 D#6 C6 A5", texture="fracture"),
    mass_bar("Drop", "G7b9", "G#6 F6 D6 B5 G#5 F5 D5 B4", EIGHTHS, "impact", octave=True),
    mass_bar("Drop", "Cm/G", "D#6 D6 C6 B5 A#5 A5 G#5 G5 F#5 F5 E5 D#5 D5 C#5 C5 B4", SIXTEENTHS, "crush"),
    mass_bar("Drop", "Db", "F5 G#5 C#6 C6 A#5 G#5 G5 F5", EIGHTHS, "fracture"),
    mass_bar("Drop", "Dhalf | G7b9", "F6 E6 D6 C6 B5 A#5 G#5 G5 F5 E5 D#5 D5 C#5 C5 B4 G4", SIXTEENTHS, "crush"),
    mass_bar("Drop", "Cm", "G5 C6 D#6 D6 G6 F6 D#6 C6", texture="impact", octave=True),
    mass_bar("Drop", "Fm", "C6 G#5 F5 C6 G#6 F6 D#6 C6", EIGHTHS, "antiphon"),
    mass_bar("Drop", "Ab | Eb", "D#6 C6 A#5 G#5 G5 A#5 D#6 G6", texture="antiphon"),
    mass_bar("Drop", "Db | G7b9", "F6 G#6 F6 C#6 D6 B5 G#5 F5", EIGHTHS, "fracture"),
    mass_bar("Drop", "Cm/G", "G5 C6 D#6 G6 F6 D#6 D6 C6", texture="barrage"),
    mass_bar("Drop", "Cm", "G5 C6 D#6 D6 G6 A#6 C7 G6", texture="impact", octave=True),
    mass_bar("Drop", "Ab", "G#6 G6 F6 D#6 C6 D#6 F6 G#6", EIGHTHS, "barrage"),
    mass_bar("Drop", "Fm | F#dim", "F6 G#6 C7 G#6 A6 F#6 D#6 C6", texture="fracture"),
    mass_bar("Drop", "G7b9", "B6 G#6 F6 D6 B5 D6 F6 G#6", EIGHTHS, "crush"),
    mass_bar("Drop", "Cm | Ab", "G6 D#6 C6 G5 G#5 C6 D#6 C6", texture="collapse", octave=True),
    mass_bar("Drop", "Db | G7b9", "F6 D#6 C#6 G#5 G5 F5 D5 B4", EIGHTHS, "fracture"),
    mass_bar("Drop", "Cm/G", "D#6 D6 C6 G5 D#5 D5", SIGH, "collapse"),
    mass_bar("Drop", "Cm", "C6 G5 D#5 C5", QUARTERS, "collapse"),
]

AFTERSHOCK = [
    mass_bar("Aftershock", "Ab", "D#5 C6 A#5 G#5 G5", LOVE, "echo"),
    mass_bar("Aftershock", "Eb", "G5 A#5 D#6 D6 A#5", LOVE, "echo"),
    mass_bar("Aftershock", "Fm", "G#5 G5 F5 C5 D#5", LOVE, "echo"),
    mass_bar("Aftershock", "G7b9", "D5 F5 G#5 G5 D5 B4", SIGH, "echo"),
    mass_bar("Aftershock", "Cm", "G4 C5 D#5 D5 G5 F5 D#5 D5", VOW, "woven",
             counter="C4 G4 D#4 D4 C4 G3 C4 D#4"),
    mass_bar("Aftershock", "Ab | Fm", "C6 A#5 G#5 G5 F5 G#5 C6 F6", EIGHTHS, "echo"),
    mass_bar("Aftershock", "Db", "F6 D#6 C#6 C6 G#5 F5 D#5 C#5", VOW, "echo"),
    mass_bar("Aftershock", "G7b9", "B4 D5 F5 G#5 B5 D6 F6 G5", EIGHTHS, "tremolo"),
]

FINAL_RESISTANCE = [
    mass_bar("Final resistance", "Cm", "G5 C6 D#6 D6 G6 F6 D#6 D6", texture="impact", octave=True),
    mass_bar("Final resistance", "Ab | Fm", "C6 G#6 G6 D#6 F6 C6 G#5 F5", EIGHTHS, "antiphon"),
    mass_bar("Final resistance", "Db | G7b9", "F6 G#6 C#6 C6 B5 D6 F6 G6", texture="fracture"),
    mass_bar("Final resistance", "Cm", "C5 D5 D#5 G5 C6 D6 D#6 F6 G6 F6 D#6 D6 C6 G5 D#5 C5", SIXTEENTHS, "thin"),
    mass_bar("Final resistance", "C", "G5 C6 E6 D6 G6 E6 D6 C6", texture="impact", octave=True),
    mass_bar("Final resistance", "F | Dm", "A5 C6 F6 E6 D6 F6 A6 G6", EIGHTHS, "barrage"),
    mass_bar("Final resistance", "Am | F", "E6 C6 A5 G5 F5 A5 C6 F6", texture="antiphon"),
    mass_bar("Final resistance", "Dm | G7", "F6 E6 D6 A5 B5 D6 F6 D6", EIGHTHS, "impact", octave=True),
]

TRUE_DAWN = [
    mass_bar("True dawn", "C", "G5 C6 E6 D6 G6 E6 D6 C6", texture="sunrise",
             counter="E4 C5 B4 A4 G4 A4 C5 G4"),
    mass_bar("True dawn", "Am | F", "E6 C6 A5 G5 A5 C6 F6 E6", EIGHTHS, "sunrise"),
    mass_bar("True dawn", "F | G7", "A5 C6 F6 E6 D6 B5 G5 D6", texture="sunrise",
             counter="F4 A4 C5 A4 G4 B4 D5 B4"),
    mass_bar("True dawn", "C", "E6 G6 C7 B6 G6 E6 D6 C6", EIGHTHS, "sunrise", octave=True),
    mass_bar("True dawn", "F | C", "A5 G5 F5 E5 D5 C5", SIGH, "lyric"),
    mass_bar("True dawn", "Dm | G7", "F5 E5 D5 B4 D5 G5", SIGH, "echo"),
    mass_bar("True dawn", "C | F", "G5 C6 E6 D6 C6 A5 G5 F5", VOW, "sunrise"),
    mass_bar("True dawn", "Dm | G7", "F5 A5 D6 C6 B5 D6 G6 B5", EIGHTHS, "echo"),
    mass_bar("True dawn", "C", "E6 D6 G5 B5 C6 C5", (0, 4, 8, 12, 14, 16), "final_cadence"),
]

BARS = PROLOGUE + FATE + HUNT + LAMENT + FUGATO + BREAKTHROUGH + FALSE_DAWN + SILENT_BREATH + DROP + AFTERSHOCK + FINAL_RESISTANCE + TRUE_DAWN

# Occasional fuller harmonies also enrich the first three minutes. The quiet
# love theme stays open so the later drop has a real change of weight.
for index in (7, 11, 15, 18, 20, 23, 26, 29, 31, 34, 46, 50, 54, 56, 59, 62, 64, 67):
    BARS[index] = dict(BARS[index], harmonic_accents=True)


def transpose(pitch, semitones):
    wanted = pitch_number(pitch) + semitones
    for candidate in PITCH_TO_KEY:
        if pitch_number(candidate) == wanted:
            return candidate
    raise ValueError(f"Piano range exceeded: {pitch} {semitones:+d}")


def physical_key(pitch):
    key = PITCH_TO_KEY[pitch]
    return key.lower().translate(str.maketrans("!@#$%^&*()", "1234567890"))


def voice_mass(source, reserved, ceiling=96):
    """Voice extensions below the lead; preserve every harmonic pitch class.

    US keyboard sharps share physical keys with naturals. Moving an inner note
    by an octave preserves the harmony without impossible keyboard collisions.
    Exact unisons and redundant octave doublings can merge, like on a piano.
    This deliberately places no human hand-span limit on virtual-piano chords.
    """
    placed = set(reserved)
    used = {physical_key(pitch) for pitch in placed}
    for pitch in source:
        if pitch in placed:
            continue
        number = pitch_number(pitch)
        candidates = [candidate for candidate in PITCH_TO_KEY
                      if (pitch_number(candidate) - number) % 12 == 0
                      and pitch_number(candidate) <= ceiling]
        candidates.sort(key=lambda candidate: (abs(pitch_number(candidate) - number), pitch_number(candidate)))
        for candidate in candidates:
            if physical_key(candidate) not in used:
                placed.add(candidate)
                used.add(physical_key(candidate))
                break
        else:
            if not any((pitch_number(other) - number) % 12 == 0 for other in placed):
                raise ValueError(f"Cannot voice harmonic pitch class {pitch} with {sorted(reserved)}")
    return placed - set(reserved)


MASS_RHYTHMS = {
    "impact": VOW,
    "barrage": (0, 2, 4, 7, 8, 10, 12, 14, 16, 18, 20, 23, 24, 26, 28, 30),
    "fracture": (0, 3, 6, 8, 11, 14, 16, 19, 22, 24, 27, 30),
    "crush": SIXTEENTHS,
    "antiphon": EIGHTHS,
    "collapse": QUARTERS,
    "echo": (0, 16),
    "sunrise": (0, 8, 16, 24),
}


def make_score():
    result = []
    for number, measure in enumerate(BARS, 1):
        voices = {name: [set() for _ in range(32)] for name in ("lead", "bass", "figuration", "counter", "mass")}
        texture = measure["texture"]

        def harmony_at(slot):
            name = measure["harmony"][min(slot // 16, len(measure["harmony"]) - 1)]
            root, fifth, path, chord = HARMONIES[name]
            return root, fifth, path.split(), chord.split()

        for slot in (0, 16):
            root, fifth, path, chord = harmony_at(slot)
            if texture in ("void", "false_cadence", "final_cadence") or (texture == "last" and slot > 0):
                continue
            voices["bass"][slot].add(root if slot == 0 else fifth)
            if texture in ("octaves", "summit", "last"):
                voices["bass"][slot].add(transpose(root if slot == 0 else fifth, 12))

        if texture in ("woven", "lyric"):
            # When three lines meet, interlock the figure and countervoice
            # instead of merging their independent passing notes into chords.
            figure_slots = range(1, 32, 4) if measure["counter"] else COUNTER
            for index, slot in enumerate(figure_slots):
                _, _, path, _ = harmony_at(slot)
                voices["figuration"][slot].add(path[index])
        elif texture == "storm":
            for index, slot in enumerate(range(1, 32, 2)):
                _, _, path, _ = harmony_at(slot)
                # Broad arpeggios rise in the second half; they interlock with
                # the even-slot lead rather than duplicating its rhythm.
                note = path[index % 8]
                voices["figuration"][slot].add(transpose(note, 12 if index >= 8 else 0))
        elif texture == "tremolo":
            for index, slot in enumerate(range(2, 32, 2)):
                _, _, _, chord = harmony_at(slot)
                voices["figuration"][slot].add(chord[(index % 2) * 2])
        elif texture == "octaves":
            for index, slot in enumerate(COUNTER):
                _, _, path, _ = harmony_at(slot)
                voices["figuration"][slot].add(path[index])
                if slot in (6, 22):
                    voices["figuration"][slot].add(transpose(path[index], 12))
        elif texture == "summit":
            for slot in (0, 16):
                _, _, _, chord = harmony_at(slot)
                # A pianist can roll from the bass to the inner harmony while
                # the other hand holds the octave, instead of needing a third hand.
                voices["figuration"][slot + 1].update(chord[:3])
            for index, slot in enumerate(range(2, 32, 4)):
                _, _, path, _ = harmony_at(slot)
                voices["figuration"][slot].add(path[index])
        elif texture == "thin":
            for index, slot in enumerate((7, 15, 23, 31)):
                _, _, path, _ = harmony_at(slot)
                voices["figuration"][slot].add(path[index * 2])
        elif texture == "bells":
            for slot in (4, 20):
                _, _, _, chord = harmony_at(slot)
                voices["figuration"][slot].update((chord[1], chord[3]))
        elif texture == "fall":
            for index, slot in enumerate(COUNTER):
                _, _, path, _ = harmony_at(slot)
                voices["figuration"][slot].add(path[7 - index])
        elif texture == "duet":
            # The countervoice is explicitly composed below, not a chord loop.
            pass
        elif texture == "last":
            _, _, _, chord = harmony_at(0)
            voices["figuration"][0].update(chord[:3])
            voices["figuration"][13].update(("C3", "E4", "G4"))
        elif texture == "false_cadence":
            # Complete the ascending tonic figure with a distinct D-B-C answer.
            # The dominant beneath D/B makes the final C feel like an arrival.
            voices["bass"][0].update(("C2", "C3"))
            voices["figuration"][0].update(("E4", "G4", "C5"))
            voices["bass"][12].add("G2")
            voices["figuration"][12].update(("G3", "B3", "D4", "F4"))
            voices["bass"][16].update(("C2", "C3"))
            voices["figuration"][16].update(("E4", "G4", "C5"))
        elif texture == "final_cadence":
            # A broader V7-I, then a lower tonic seals the real ending. The
            # last sonority contains only C/E/G, with no hanging 7th or 9th.
            voices["bass"][0].update(("C2", "C3"))
            voices["figuration"][0].update(("E4", "G4", "C5"))
            voices["bass"][4].add("G2")
            voices["figuration"][4].update(("G3", "B3", "D4", "F4"))
            voices["figuration"][8].update(("G3", "D4"))
            voices["bass"][12].add("G2")
            voices["figuration"][12].update(("B3", "D4", "F4"))
            voices["figuration"][14].update(("C3", "E4", "G4"))
            voices["bass"][16].update(("C2", "C3"))
            voices["figuration"][16].update(("G3", "C4", "E4", "G4"))
        elif texture in MASS_RHYTHMS:
            pass  # The fully voiced masses are placed after the independent lead.
        elif texture not in ("silence", "void"):
            raise ValueError(f"Unknown texture {texture}")

        for slot, pitch in measure["melody"].items():
            voices["lead"][slot].add(pitch)
            if measure["octave"] and slot in (0, 8, 16, 24):
                voices["lead"][slot].add(transpose(pitch, -12))
        for slot, pitch in zip(COUNTER, measure["counter"]):
            voices["counter"][slot].add(pitch)

        for slot in MASS_RHYTHMS.get(texture, ()):
            harmony = measure["harmony"][min(slot // 16, len(measure["harmony"]) - 1)]
            stack = MASSES[MASS_FOR_HARMONY[harmony]].split()
            if texture == "echo":
                stack = stack[:3]
            elif texture == "antiphon" and slot not in (0, 16):
                stack = stack[:3] if slot in (4, 12, 20, 28) else stack[2:]
            elif texture == "barrage" and slot not in (0, 8, 16, 24):
                stack = stack[:3]
            elif texture == "crush" and slot not in (0, 16):
                stack = stack[:3]
            elif texture == "fracture" and slot not in (0, 16):
                stack = stack[1:4]
            elif texture in ("impact", "sunrise") and slot not in (0, 8, 16, 24):
                stack = stack[:3]
            elif texture == "collapse" and slot != 0:
                stack = stack[:3]
            reserved = set().union(*(voice[slot] for voice in voices.values()))
            # Count the bass and lead in the requested maximum. Strong arrivals
            # may use seven keys, other attacks five or six; no extra octave
            # doubles are added after this choice.
            chord_limit = 7 if slot == 0 and number % 4 == 1 else 6 if slot in (0, 16) else 5
            stack = stack[:max(0, chord_limit - len(reserved))]
            last_lead = [pitch for onset, pitch in measure["melody"].items() if onset <= slot]
            ceiling = pitch_number(last_lead[-1]) if last_lead else 96
            voices["mass"][slot].update(voice_mass(stack, reserved, ceiling))

        if measure.get("harmonic_accents"):
            for slot in (0, 16):
                _, _, _, chord = harmony_at(slot)
                reserved = set().union(*(voice[slot] for voice in voices.values()))
                voices["mass"][slot].update(voice_mass(chord, reserved))

        grid = [sorted(set().union(*(voice[slot] for voice in voices.values())), key=pitch_number)
                for slot in range(32)]
        result.append({"bar": number, "section": measure["section"],
                       "harmony": measure["harmony"], "texture": texture,
                       "harmonic_accents": measure.get("harmonic_accents", False),
                       "voices": {name: [{"slot": slot, "pitches": sorted(notes, key=pitch_number)}
                                          for slot, notes in enumerate(voice) if notes]
                                  for name, voice in voices.items()}, "grid": grid})
    return result


def main():
    score = make_score()
    sheet = make_sheet(score)
    target = ROOT / "assets/songs" / f"{SONG_ID}.txt"
    target.write_text(sheet, encoding="utf-8")
    document = {"title": TITLE, "original": True,
                "bpm": BPM, "meter": "4/4", "grid": "thirty-second",
                "slots_per_bar": SLOTS_PER_BAR, "note_delay_ms": NOTE_DELAY_MS,
                "key_hold_ms": KEY_HOLD_MS, "bars": score}
    directory = ROOT / "assets/originals"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{SONG_ID}-score.json").write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(score)} bars, {len(score) * 32 * NOTE_DELAY_MS / 1000:.1f} s: {target}")


if __name__ == "__main__":
    main()
