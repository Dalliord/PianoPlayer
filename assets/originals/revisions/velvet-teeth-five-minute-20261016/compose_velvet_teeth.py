"""Velvet Teeth: an original five-minute jazz story inspired by Beastars.

No opening melody or sheet is imported. Every lead/counter phrase is written
below. A six-part quarter-note grid makes the 2:1 swing part of the score,
independent of playback humanization: 24 slots * 100 ms = one 4/4 bar.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.compose_moonlit_platform import PITCH_TO_KEY, make_sheet, pitch_number

SONG_ID = "velvet-teeth"
TITLE = "Velvet Teeth"
BPM = 100
NOTE_DELAY_MS = 100
KEY_HOLD_MS = 160
SLOTS_PER_BAR = 24
PITCH_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")

# Root, walking-bass outline, rootless piano voicing, solo accompaniment path.
# Flat chord names use enharmonic sharp pitch spellings for the keyboard map.
HARMONIES = {
    "Dm9": ("D2", "D3 F3 A3 C4", "F4 C5 E5", "D4 F4 A4 C5 E5"),
    "Dm6": ("D2", "D3 F3 A3 B3", "F4 B4 E5", "D4 F4 A4 B4 E5"),
    "Gm9": ("G2", "G2 A#2 D3 F3", "A#3 F4 A4", "G3 A#3 D4 F4 A4"),
    "C13": ("C2", "C3 E3 G3 A3", "E4 A4 A#4", "C4 E4 G4 A4 A#4"),
    "Fmaj9": ("F2", "F2 A2 C3 E3", "A3 E4 G4", "F3 A3 C4 E4 G4"),
    "Bbmaj9": ("A#2", "A#2 D3 F3 A3", "D4 A4 C5", "A#3 D4 F4 A4 C5"),
    "Em7b5": ("E2", "E3 G3 A#3 D4", "G4 A#4 D5", "E4 G4 A#4 D5 E5"),
    "A7b9": ("A2", "A2 C#3 E3 G3", "C#4 G4 A#4", "A3 C#4 E4 G4 A#4"),
    "A7alt": ("A2", "A2 C#3 G3 A#3", "C#4 G4 C5", "A3 C#4 G4 A#4 C5"),
    "D7b9": ("D2", "D3 F#3 A3 C4", "F#4 C5 D#5", "D4 F#4 A4 C5 D#5"),
    "Eb9": ("D#2", "D#3 G3 A#3 C#4", "G4 C#5 F5", "D#4 G4 A#4 C#5 F5"),
    "Ab7": ("G#2", "G#2 C3 D#3 F#3", "C4 F#4 A#4", "G#3 C4 D#4 F#4 A#4"),
    "Fm6": ("F2", "F2 G#2 C3 D3", "G#3 D4 G4", "F3 G#3 C4 D4 G4"),
    "Bdim7": ("B2", "B2 D3 F3 G#3", "D4 F4 G#4", "B3 D4 F4 G#4 B4"),
    "E7alt": ("E2", "E3 G#3 B3 D4", "G#4 D5 F5", "E4 G#4 B4 D5 F5"),
    "Am9": ("A2", "A2 C3 E3 G3", "C4 G4 B4", "A3 C4 E4 G4 B4"),
    "Dmaj9": ("D2", "D3 F#3 A3 C#4", "F#4 C#5 E5", "D4 F#4 A4 C#5 E5"),
    "D6": ("D2", "D3 F#3 A3 B3", "F#4 B4 E5", "D4 F#4 A4 B4 E5"),
    "Gmaj9": ("G2", "G2 B2 D3 F#3", "B3 F#4 A4", "G3 B3 D4 F#4 A4"),
    "E9": ("E2", "E3 G#3 B3 D4", "G#4 D5 F#5", "E4 G#4 B4 D5 F#5"),
    "A13": ("A2", "A2 C#3 E3 F#3", "C#4 F#4 G4", "A3 C#4 E4 F#4 G4"),
    "D": ("D2", "D3 F#3 A3 D4", "D4 F#4 A4", "D4 F#4 A4 D5 F#5"),
}

SWING = (0, 4, 6, 10, 12, 16, 18, 22)
PICKUP = (2, 4, 6, 10, 12, 16, 18, 22)
ANSWER = (0, 4, 6, 9, 10, 16, 18, 22)
SUSPEND = (0, 4, 6, 10, 15, 16, 18, 22)
SPACE = (0, 4, 9, 12, 18, 22)
LONG = (0, 6, 12, 16, 18, 22)
RUN = (0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22)
BURST = (0, 1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 22)


def bar(section, harmony, melody, rhythm=SWING, texture="walk", *, counter="", counter_rhythm=()):
    notes = melody.split()
    if (len(notes) != len(rhythm) or len(counter.split()) != len(counter_rhythm)
            or len(set(rhythm)) != len(rhythm) or any(not 0 <= slot < 24 for slot in rhythm)
            or len(set(counter_rhythm)) != len(counter_rhythm)):
        raise ValueError(f"Unmatched phrase in {section}: {melody}")
    return {"section": section, "harmony": harmony.split(" | "),
            "melody": dict(zip(rhythm, notes)), "texture": texture,
            "counter": dict(zip(counter_rhythm, counter.split()))}


# The repeated short A, falling F-E-C#, and resolving D are the original hook.
# It is answered, fragmented, inverted and finally changed to its major form.
INTRO = [
    bar("After-hours", "Dm6", "A4 A4 F5 E5 C#5 D5", SPACE, "noir"),
    bar("After-hours", "Gm9", "D5 C5 A#4 A4 G4 D4", SPACE, "noir"),
    bar("After-hours", "Em7b5 | A7b9", "G4 A#4 D5 C#5 E5 G5", SPACE, "shell"),
    bar("After-hours", "Dm6", "F5 E5 D5 A4 F4 D4", SPACE, "noir"),
    bar("After-hours", "Bbmaj9", "F4 A4 C5 D5 C5 A4", LONG, "stride"),
    bar("After-hours", "Em7b5 | A7alt", "G4 A#4 D5 C5 A#4 G4", LONG, "shell"),
    bar("After-hours", "Dm9 | Eb9", "A4 F5 E5 D5 C#5 F5 G5 A#5", SUSPEND, "rising"),
    bar("After-hours", "A7b9", "A5 G5 E5 C#5 A4 G4 A4 A4", PICKUP, "break"),
]

THEME = [
    bar("Velvet footsteps", "Dm6", "A4 A4 F5 E5 C#5 D5 F5 A5", PICKUP),
    bar("Velvet footsteps", "Gm9", "G5 F5 D5 C5 A#4 A4 G4 D4", ANSWER, "shell"),
    bar("Velvet footsteps", "C13", "E5 G5 A5 G5 E5 D5 C5 A4", SUSPEND),
    bar("Velvet footsteps", "Fmaj9", "C5 E5 G5 A5 G5 E5 F5 C5", SWING, "stride"),
    bar("Velvet footsteps", "Bbmaj9", "F5 F5 D6 C6 A5 F5 E5 D5", PICKUP),
    bar("Velvet footsteps", "Em7b5 | A7b9", "G5 A#5 A5 G5 E5 C#5 A4 C#5", ANSWER, "shell"),
    bar("Velvet footsteps", "Dm9", "D5 A4 F5 E5 D5 C5 A4 F4", SUSPEND),
    bar("Velvet footsteps", "A7alt", "E5 G5 A#5 C6 C#6 A#5 G5 E5", SWING, "break"),
    bar("Velvet footsteps", "Dm9", "A5 A5 F6 E6 C#6 D6 A5 F5", PICKUP, "walk"),
    bar("Velvet footsteps", "D7b9", "F#5 A5 C6 D#6 D6 C6 A5 F#5", ANSWER, "cross"),
    bar("Velvet footsteps", "Gm9", "G5 D6 C6 A#5 A5 G5 F5 D5", SWING, "shell"),
    bar("Velvet footsteps", "C13", "E5 G5 A#5 A5 G5 E5 D5 C5", SUSPEND, "stride"),
    bar("Velvet footsteps", "Fmaj9 | Bbmaj9", "A5 G5 F5 E5 D5 F5 A5 C6", ANSWER),
    bar("Velvet footsteps", "Em7b5 | A7b9", "A#5 G5 F5 D5 C#5 E5 G5 A#5", SWING, "cross"),
    bar("Velvet footsteps", "Dm6 | A7alt", "A5 F5 E5 D5 C#5 E5 A#5 G5", SUSPEND, "shell"),
    bar("Velvet footsteps", "Dm6", "F5 E5 D5 A4 D5 F5 A5 C6", ANSWER, "break"),
]

DANCE = [
    bar("Two shadows dance", "Fmaj9", "C6 A5 G5 E5 F5 A5 G5 F5", SWING, "light"),
    bar("Two shadows dance", "Bbmaj9", "A5 C6 D6 C6 A5 F5 D5 F5", ANSWER, "stride"),
    bar("Two shadows dance", "Gm9", "A#5 A5 G5 D5 F5 G5 A5 A#5", SWING, "light"),
    bar("Two shadows dance", "C13", "G5 A5 A#5 D6 C6 A5 G5 E5", SUSPEND, "cross"),
    bar("Two shadows dance", "Fmaj9", "A5 G5 E5 F5 C6 A5 G5 F5", PICKUP, "light"),
    bar("Two shadows dance", "Fm6", "G#5 G5 F5 D5 C5 D5 G#5 C6", ANSWER, "shell"),
    bar("Two shadows dance", "Am9 | D7b9", "B5 A5 G5 E5 F#5 A5 C6 D#6", SWING, "cross"),
    bar("Two shadows dance", "Gm9 | C13", "D6 A#5 A5 G5 E5 G5 A5 C6", SUSPEND, "break"),
    bar("Two shadows dance", "Fmaj9", "C6 A5 G5 E5 F5 A5 C6 E6", SWING, "light", counter="C4 E4 F4 G4", counter_rhythm=(2, 8, 14, 20)),
    bar("Two shadows dance", "Bbmaj9", "D6 C6 A5 F5 A5 C6 D6 F6", ANSWER, "light", counter="D4 F4 A4 F4", counter_rhythm=(2, 8, 14, 20)),
    bar("Two shadows dance", "Bdim7", "D6 F6 G#6 F6 D6 B5 G#5 F5", SWING, "shell"),
    bar("Two shadows dance", "E7alt", "F5 G#5 B5 D6 F6 E6 D6 B5", SUSPEND, "cross"),
    bar("Two shadows dance", "Am9", "C6 B5 A5 G5 E5 G5 B5 A5", ANSWER, "walk"),
    bar("Two shadows dance", "Ab7", "A#5 G#5 F#5 D#5 C5 D#5 F#5 G#5", SWING, "shell"),
    bar("Two shadows dance", "Gm9 | A7alt", "A#5 A5 G5 D5 C#5 E5 G5 C6", SUSPEND, "rising"),
    bar("Two shadows dance", "Dm9", "A5 F5 E5 D5 F5 A5 D6 C6", ANSWER, "break"),
]

HUNGER = [
    bar("Hunger in the brass", "Dm9", "D5 F5 A5 C6 D6 C6 A5 F5", SWING, "stabs"),
    bar("Hunger in the brass", "Eb9", "D#5 G5 A#5 C#6 F6 D#6 C#6 A#5", ANSWER, "cross"),
    bar("Hunger in the brass", "Dm9", "A5 F5 E5 D5 C5 A4 C5 D5", SUSPEND, "stabs"),
    bar("Hunger in the brass", "A7alt", "C#5 E5 G5 A#5 C6 A#5 G5 E5", SWING, "break"),
    bar("Hunger in the brass", "Gm9", "G5 A5 A#5 D6 F6 E6 D6 A#5", SWING, "walk"),
    bar("Hunger in the brass", "Ab7", "C6 A#5 G#5 F#5 D#5 F#5 G#5 A#5", ANSWER, "stabs"),
    bar("Hunger in the brass", "Dm9 | Bdim7", "A5 F5 E5 D5 F5 G#5 B5 D6", SUSPEND, "cross"),
    bar("Hunger in the brass", "Em7b5 | A7b9", "D6 A#5 G5 E5 C#5 E5 G5 A#5", SWING, "break"),
    bar("Hunger in the brass", "Dm9", "D6 C6 A5 F5 E5 D5 C5 A4 F4 E4 D4 F4", RUN, "run"),
    bar("Hunger in the brass", "Gm9", "G4 A4 A#4 D5 F5 G5 A5 A#5 D6 C6 A#5 A5", RUN, "run"),
    bar("Hunger in the brass", "C13", "G5 E5 D5 C5 E5 G5 A5 A#5 C6 D6 E6 G6", RUN, "run"),
    bar("Hunger in the brass", "Fmaj9 | A7alt", "A6 G6 E6 C6 A5 G5 E5 C#5 A4 A#4 C5 C#5", BURST, "run"),
    bar("Hunger in the brass", "Bbmaj9", "D6 C6 A5 F5 D5 C5 A4 F4", SWING, "stabs"),
    bar("Hunger in the brass", "Em7b5 | A7alt", "G5 A#5 D6 F6 E6 C#6 A#5 G5", ANSWER, "cross"),
    bar("Hunger in the brass", "Dm9 | Eb9", "F5 E5 D5 A4 G5 F5 D#5 C#5", SUSPEND, "stabs"),
    bar("Hunger in the brass", "A7b9", "C#5 E5 G5 A#5 A5 G5 E5 C#5", (0, 6, 10, 12, 16, 18, 20, 22), "break"),
]

GARDEN = [
    bar("Garden without words", "Bbmaj9", "D5 F5 A5 G5 F5 D5", SPACE, "duet", counter="F4 A4 C5", counter_rhythm=(6, 15, 21)),
    bar("Garden without words", "Fm6", "C5 D5 F5 G#5 G5 F5", SPACE, "duet", counter="G#4 F4 D4", counter_rhythm=(6, 15, 21)),
    bar("Garden without words", "Dm9", "E5 F5 A5 C6 A5 F5", SPACE, "duet", counter="D4 F4 E4", counter_rhythm=(6, 15, 21)),
    bar("Garden without words", "D7b9", "F#5 A5 C6 A5 F#5 D#5", SPACE, "noir"),
    bar("Garden without words", "Gm9", "D5 F5 G5 A#5 A5 G5", SPACE, "duet", counter="A#4 A4 G4", counter_rhythm=(6, 15, 21)),
    bar("Garden without words", "C13", "E5 G5 A5 C6 A5 G5", SPACE, "duet", counter="A#4 G4 E4", counter_rhythm=(6, 15, 21)),
    bar("Garden without words", "Fmaj9 | Em7b5", "A5 G5 E5 F5 D5 A#4", SPACE, "noir"),
    bar("Garden without words", "A7b9", "E5 C#5 A4 G4 A4 A4", SPACE, "break"),
]

SOLO = [
    bar("Running the rooftops", "Dm6", "A4 C5 D5 E5 F5 A5 G5 F5 E5 D5 C5 B4", RUN, "run"),
    bar("Running the rooftops", "Gm9", "A#4 D5 F5 G5 A5 A#5 A5 G5 F5 D5 C5 A#4", RUN, "solo"),
    bar("Running the rooftops", "C13", "G4 A4 A#4 B4 C5 E5 G5 A5 A#5 D6 E6 G6", BURST, "run"),
    bar("Running the rooftops", "Fmaj9", "A6 G6 F6 E6 C6 A5 G5 E5 F5 A5 C6 E6", RUN, "solo"),
    bar("Running the rooftops", "Bbmaj9", "F6 D6 C6 A5 F5 D5 C5 D5 F5 A5 C6 D6", RUN, "run"),
    bar("Running the rooftops", "Bdim7", "F6 D6 B5 G#5 F5 D5 B4 D5 F5 G#5 B5 D6", RUN, "solo"),
    bar("Running the rooftops", "E7alt", "E6 F6 D6 B5 G#5 G5 F5 E5 G#5 B5 D6 F6", RUN, "run"),
    bar("Running the rooftops", "Am9 | A7alt", "E6 C6 B5 A5 G5 E5 C#5 E5 G5 A#5 C6 C#6", RUN, "solo"),
    bar("Running the rooftops", "Dm9", "D6 A5 F5 E5 D5 C5 A4 F4", ANSWER, "hocket", counter="F4 A4 C5 E5 F5 E5 D5 C5", counter_rhythm=SWING),
    bar("Running the rooftops", "D7b9", "F#5 A5 C6 D#6 D6 C6 A5 F#5", SUSPEND, "hocket", counter="C4 D4 F#4 A4 C5 A4 F#4 D4", counter_rhythm=SWING),
    bar("Running the rooftops", "Gm9", "D6 C6 A#5 A5 G5 F5 D5 G5", PICKUP, "solo"),
    bar("Running the rooftops", "Ab7", "C6 A#5 G#5 F#5 D#5 C5 A#4 G#4", SWING, "cross"),
    bar("Running the rooftops", "Dm9 | Bdim7", "A4 D5 F5 A5 C6 A5 F5 D5 F5 G#5 B5 D6", RUN, "run"),
    bar("Running the rooftops", "Em7b5 | A7b9", "F6 D6 A#5 G5 E5 G5 A#5 C#6 E6 D6 C#6 A#5", RUN, "solo"),
    bar("Running the rooftops", "Dm6 | Eb9", "A5 F5 E5 D5 B4 A4 G4 F4 G4 A#4 C#5 F5", RUN, "run"),
    bar("Running the rooftops", "A7alt", "G5 A#5 C6 C#6 E6 G6 E6 C#6", SUSPEND, "break"),
]

COLLISION = [
    bar("Claws against the cage", "Dm9", "D6 A5 F5 E5 D5 F5 A5 C6", ANSWER, "stabs"),
    bar("Claws against the cage", "Eb9", "D#6 C#6 A#5 G5 F5 G5 A#5 C#6", SWING, "cross"),
    bar("Claws against the cage", "Dm9", "A5 A5 F6 E6 C#6 D6 A5 F5", PICKUP, "hocket", counter="D4 F4 E4 D4 C4 A3 C4 D4", counter_rhythm=SWING),
    bar("Claws against the cage", "A7alt", "E5 G5 A#5 C6 C#6 A#5 G5 E5", SUSPEND, "break"),
    bar("Claws against the cage", "Gm9", "A#5 A5 G5 D5 F5 G5 A#5 D6", ANSWER, "stabs"),
    bar("Claws against the cage", "C13 | Ab7", "E6 D6 C6 A#5 G#5 F#5 D#5 C5", SWING, "cross"),
    bar("Claws against the cage", "Fmaj9 | Bdim7", "C6 A5 G5 E5 F5 G#5 B5 D6", SUSPEND, "stabs"),
    bar("Claws against the cage", "Em7b5 | A7b9", "G5 A#5 D6 F6 E6 C#6 A#5 G5", ANSWER, "break"),
    bar("Claws against the cage", "Dm9", "D6 C6 A5 F5 E5 D5 C5 A4 F4 E4 D4 C4", RUN, "run"),
    bar("Claws against the cage", "Eb9", "D#4 F4 G4 A#4 C#5 D#5 F5 G5 A#5 C#6 D#6 F6", RUN, "run"),
    bar("Claws against the cage", "Dm6", "E6 D6 B5 A5 F5 E5 D5 A4", SWING, "hocket", counter="D4 E4 F4 A4 B4 A4 F4 E4", counter_rhythm=(2, 5, 8, 11, 14, 17, 20, 23)),
    bar("Claws against the cage", "D7b9", "F#5 A5 C6 D#6 F#6 D#6 C6 A5", SUSPEND, "stabs"),
    bar("Claws against the cage", "Gm9 | Ab7", "D6 A#5 A5 G5 G#5 A#5 C6 D#6", ANSWER, "cross"),
    bar("Claws against the cage", "Dm9 | Bdim7", "D6 C6 A5 F5 G#5 B5 D6 F6", SWING, "stabs"),
    bar("Claws against the cage", "Em7b5 | A7alt", "G6 F6 D6 A#5 G5 E5 C#5 A4", SUSPEND, "break"),
    bar("Claws against the cage", "A7b9", "A4 C#5 E5 G5 A#5 A5 G5 E5", ANSWER, "rising"),
]

SHOUT = [
    bar("Dance beyond the fear", "D6", "A5 A5 F#6 E6 C#6 D6 A5 F#5", PICKUP, "shout"),
    bar("Dance beyond the fear", "Gmaj9", "B5 A5 F#5 E5 D5 E5 F#5 A5", ANSWER, "walk"),
    bar("Dance beyond the fear", "E9", "G#5 B5 D6 F#6 E6 D6 B5 G#5", SWING, "shout"),
    bar("Dance beyond the fear", "A13", "G5 F#5 E5 C#5 A4 C#5 E5 G5", SUSPEND, "break"),
    bar("Dance beyond the fear", "Dmaj9", "F#5 A5 C#6 D6 E6 D6 C#6 A5", SWING, "shout"),
    bar("Dance beyond the fear", "D7b9", "F#6 D#6 C6 A5 F#5 A5 C6 D#6", ANSWER, "cross"),
    bar("Dance beyond the fear", "Gmaj9", "D6 B5 A5 F#5 E5 D5 B4 D5", SUSPEND, "light"),
    bar("Dance beyond the fear", "Gm9 | A13", "A#5 A5 G5 F5 E5 C#5 A4 E5", SWING, "break"),
    bar("Dance beyond the fear", "Dmaj9", "A5 A5 F#6 E6 C#6 D6 F#6 A6", PICKUP, "shout"),
    bar("Dance beyond the fear", "Bdim7 | E7alt", "G#6 F6 D6 B5 G#5 B5 D6 F6", ANSWER, "cross"),
    bar("Dance beyond the fear", "Am9 | D7b9", "E6 C6 B5 A5 F#5 A5 C6 D#6", SWING, "walk"),
    bar("Dance beyond the fear", "Gmaj9", "D6 B5 A5 F#5 E5 D5 B4 A4 G4 A4 B4 D5", RUN, "run"),
    bar("Dance beyond the fear", "Gm9", "D6 C6 A#5 A5 G5 F5 D5 A#4", SUSPEND, "light"),
    bar("Dance beyond the fear", "Dmaj9 | E9", "A5 F#5 E5 D5 G#5 B5 D6 F#6", ANSWER, "shout"),
    bar("Dance beyond the fear", "Em7b5 | A7b9", "G6 F6 D6 A#5 A5 G5 E5 C#5", SWING, "stabs"),
    bar("Dance beyond the fear", "D6", "D6 A5 F#5 E5 D5 A4 F#4 D4", SUSPEND, "break"),
]

CODA = [
    bar("The morning is ours", "Gmaj9", "B5 A5 F#5 E5 D5 B4", SPACE, "duet", counter="G4 A4 B4", counter_rhythm=(6, 15, 21)),
    bar("The morning is ours", "Gm9", "A#5 A5 G5 F5 D5 A#4", SPACE, "duet", counter="G4 F4 D4", counter_rhythm=(6, 15, 21)),
    bar("The morning is ours", "Dmaj9", "A5 F#5 E5 D5 A4 F#4", SPACE, "noir"),
    bar("The morning is ours", "E9 | A13", "G#4 B4 D5 C#5 E5 G5", SPACE, "shell"),
    bar("The morning is ours", "D6", "A4 A4 F#5 E5 C#5 D5 F#5 A5", PICKUP, "light"),
    bar("The morning is ours", "Gmaj9", "B5 A5 F#5 D5 E5 F#5 A5 B5", ANSWER, "light"),
    bar("The morning is ours", "Gm9 | A7b9", "A#5 A5 G5 F5 E5 C#5 A4 G4", SUSPEND, "shell"),
    bar("The morning is ours", "Dmaj9", "F#5 E5 D5 A4 D5 F#5 A5 D6", SWING, "shout"),
    bar("The morning is ours", "Gmaj9 | Gm9", "B5 A5 F#5 D5 A#5 A5 G5 F5", ANSWER, "light"),
    bar("The morning is ours", "Dmaj9 | E9", "F#5 A5 D6 E6 F#6 E6 D6 B5", SUSPEND, "rising"),
    bar("The morning is ours", "A13", "A5 G5 F#5 E5 C#5 E5 G5 A5", SWING, "shell"),
    bar("The morning is ours", "D | A13", "F#6 E6 D6 A5 G5 E5 C#5 A4", ANSWER, "cadence"),
    bar("The morning is ours", "D", "D6 C#6 A5 F#5 E5 D5 D4", (0, 2, 4, 6, 8, 12, 14), "seal"),
]

BARS = INTRO + THEME + DANCE + HUNGER + GARDEN + SOLO + COLLISION + SHOUT + CODA


def pitch_name(number):
    return f"{PITCH_NAMES[number % 12]}{number // 12 - 1}"


def physical(pitch):
    key = PITCH_TO_KEY[pitch]
    return key.upper() if key.isalpha() else key.translate(str.maketrans("!@$%^*(", "1245689"))


def place(desired, occupied, *, low=48, high=83):
    """Revoice accompaniment, preserving its pitch classes and keyboard safety.

    Lead/counter pitches are fixed first. Existing identical pitches are shared;
    an inner note with a sharp/natural key conflict moves to another octave.
    """
    chosen = set()
    for pitch in desired:
        if pitch in occupied or pitch in chosen:
            continue
        number = pitch_number(pitch)
        used = {physical(note) for note in occupied | chosen}
        candidates = [pitch_name(number + shift) for shift in (0, -12, 12, -24, 24)
                      if low <= number + shift <= high]
        safe = next((note for note in candidates if physical(note) not in used), None)
        if safe is None:
            raise ValueError(f"Cannot voice {pitch} against {occupied | chosen}")
        chosen.add(safe)
    return chosen


def make_score():
    result = []
    if len(BARS) != 125:
        raise ValueError("The five-minute form needs 125 bars")
    for number, measure in enumerate(BARS, 1):
        voices = {name: [set() for _ in range(24)] for name in ("lead", "counter", "bass", "comp", "figure")}
        texture = measure["texture"]
        for slot, note in measure["melody"].items():
            if note != "-":
                voices["lead"][slot].add(note)
        for slot, note in measure["counter"].items():
            voices["counter"][slot].update(place([note], voices["lead"][slot], low=48, high=79))

        def occupied(slot):
            return set().union(*(voice[slot] for voice in voices.values()))

        def harmony_at(slot):
            name = measure["harmony"][min(slot // 12, len(measure["harmony"]) - 1)]
            root, walk, chord, path = HARMONIES[name]
            return root, walk.split(), chord.split(), path.split()

        # Walking bass, sparse half-time, stride leaps and stop-time are distinct
        # phrases. Beat four approaches the following harmony chromatically.
        bass_slots = (0, 12) if texture in ("noir", "duet", "light", "run", "hocket") else (0, 6, 12, 18)
        if texture == "break":
            bass_slots = (0,)
        elif texture == "seal":
            bass_slots = (0, 12, 14)
        for slot in bass_slots:
            root, walk, _, _ = harmony_at(slot)
            if texture in ("noir", "duet", "seal", "cadence"):
                note = root if slot != 12 else walk[2]
            else:
                note = walk[(slot // 6) % 4]
            if slot == 18 and texture in ("walk", "cross", "solo", "shout") and number < len(BARS):
                next_root = HARMONIES[BARS[number]["harmony"][0]][0]
                target = pitch_number(next_root) + 12
                note = pitch_name(target - 1 if number % 2 else target + 1)
            voices["bass"][slot].update(place([note], occupied(slot), low=36, high=59))

        schedules = {
            "noir": (9, 21), "shell": (4, 15, 22),
            "walk": ((4, 10, 16, 22), (2, 9, 16), (4, 12, 21), (6, 15, 22))[number % 4],
            "stride": (4, 10, 16, 22), "light": (4, 16), "cross": (3, 10, 15, 21),
            "rising": (4, 10, 14, 16, 20, 22), "break": (0,),
            "stabs": (0, 4, 10, 12, 16, 22), "duet": (0, 12),
            "run": (), "solo": (4, 16), "hocket": (10, 22),
            "shout": (2, 4, 10, 12, 16, 22), "cadence": (0, 6, 12, 18, 22),
            "seal": (0, 12, 14),
        }
        for slot in schedules[texture]:
            _, _, chord, _ = harmony_at(slot)
            if texture in ("duet", "noir", "light", "hocket"):
                chord = chord[:2]
            elif texture == "stabs" and slot in (0, 12):
                chord = [*chord, harmony_at(slot)[3][0]]
            if texture == "seal":
                chord = ["D4", "F#4", "A4"] if slot != 0 else ["F#4", "A4"]
            voices["comp"][slot].update(place(chord, occupied(slot), low=48, high=83))

        if texture in ("run", "rising", "hocket"):
            figure_slots = (4, 10, 16, 22) if texture == "run" else (2, 8, 14, 20)
            for index, slot in enumerate(figure_slots):
                _, _, _, path = harmony_at(slot)
                # A lighter, contrary-motion answer below the solo line.
                note = path[(len(path) - index - 1) % len(path)]
                note = pitch_name(pitch_number(note) - 12)
                voices["figure"][slot].update(place([note], occupied(slot), low=48, high=76))

        grid = [sorted(occupied(slot), key=pitch_number) for slot in range(24)]
        if any(len(notes) > 7 for notes in grid):
            raise ValueError(f"Chord exceeds seven keys in bar {number}")
        result.append({"bar": number, "section": measure["section"], "harmony": measure["harmony"],
                       "texture": texture, "voices": {
                           name: [{"slot": slot, "pitches": sorted(notes, key=pitch_number)}
                                  for slot, notes in enumerate(voice) if notes]
                           for name, voice in voices.items()}, "grid": grid})
    # Also validates printable keys, keyboard range and physical-key uniqueness.
    make_sheet(result)
    return result


def main():
    score = make_score()
    target = ROOT / "assets/songs" / f"{SONG_ID}.txt"
    target.write_text(make_sheet(score), encoding="utf-8")
    directory = ROOT / "assets/originals"
    directory.mkdir(parents=True, exist_ok=True)
    document = {"title": TITLE, "original": True,
                "inspiration": "Beastars; original jazz themes, no opening melody quotation",
                "bpm": BPM, "meter": "4/4", "grid": "sextuplet", "swing_ratio": "2:1",
                "slots_per_bar": SLOTS_PER_BAR, "note_delay_ms": NOTE_DELAY_MS,
                "key_hold_ms": KEY_HOLD_MS, "bars": score}
    (directory / f"{SONG_ID}-score.json").write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(score)} bars, {len(score) * SLOTS_PER_BAR * NOTE_DELAY_MS / 1000:.1f} s: {target}")


if __name__ == "__main__":
    main()
