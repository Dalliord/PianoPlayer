"""Encode the user's Wild Side piano tutorial transcription for the player.

The checked-in note table records the tutorial's pressed keys at 30 fps.
This is an adaptation of ALI / Sheet Music Boss, not an original composition.
Absolute onsets are rounded independently to 20 ms, avoiding cumulative drift.
"""
from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.render_song import KEY_TO_MIDI, physical_key

SONG_ID = "wild-side-piano"
NOTE_DELAY_MS = 20
KEY_HOLD_MS = 100
DURATION_MS = 90_000
SOURCE_START_FRAME = 103
KEYS = {midi: key for key, midi in KEY_TO_MIDI.items()}
REFERENCE = ROOT / "assets/arrangements/wild-side-reference.json"


def load_reference() -> dict:
    return json.loads(REFERENCE.read_text(encoding="utf-8"))


def adapted_notes(reference: dict | None = None) -> list[dict]:
    reference = load_reference() if reference is None else reference
    groups = defaultdict(list)
    for midi, start, end, hand in reference["notes"]:
        if not 21 <= midi <= 108 or not SOURCE_START_FRAME <= start < end or hand not in ("L", "R"):
            raise ValueError("Invalid reference note")
        groups[start].append((midi, end, hand))
    result = []
    for start, group in sorted(groups.items()):
        lift_bass = any(midi < 36 for midi, _, _ in group)
        onset = round((start - SOURCE_START_FRAME) * 1000 / 30 / NOTE_DELAY_MS) * NOTE_DELAY_MS
        physical = set()
        for midi, end, hand in sorted(group):
            # Keep a written C1/C2 octave as C2/C3 instead of collapsing it
            # onto one key. Melody and all in-range bass figures stay intact.
            pitch = midi + 12 if lift_bass and hand == "L" and midi < 48 else midi
            if pitch not in KEYS:
                raise ValueError(f"Pitch outside player range: {pitch}")
            key = KEYS[pitch]
            if physical_key(key) in physical:
                raise ValueError(f"Conflicting simultaneous physical keys at frame {start}")
            physical.add(physical_key(key))
            release = round((end - SOURCE_START_FRAME) * 1000 / 30)
            hold = max(5, release - onset)
            result.append({"pitch": pitch, "source_pitch": midi, "source_frame": start,
                           "offset_ms": onset, "hold_ms": hold, "key": key, "hand": hand})
    return result


def make_sheet(reference: dict | None = None) -> str:
    groups = defaultdict(list)
    for note in adapted_notes(reference):
        groups[note["offset_ms"] // NOTE_DELAY_MS].append(note)
    cells = ["-"] * (DURATION_MS // NOTE_DELAY_MS)
    for slot, notes in groups.items():
        if not 0 <= slot < len(cells):
            raise ValueError("Note outside the arrangement")
        holds = {note["hold_ms"] for note in notes}
        if len(notes) == 1:
            cells[slot] = f'{notes[0]["key"]}<{notes[0]["hold_ms"]}>'
        elif len(holds) == 1:
            cells[slot] = "[" + "".join(note["key"] for note in notes) + f"]<{holds.pop()}>"
        else:
            cells[slot] = "[" + "".join(f'{note["key"]}<{note["hold_ms"]}>' for note in notes) + "]"
    # Lines are one second long; whitespace has no musical duration.
    return "\n".join(" ".join(cells[i:i+50]) for i in range(0, len(cells), 50)) + "\n"


def main() -> None:
    sheet = make_sheet()
    target = ROOT / "assets/songs/wild-side-piano.txt"
    target.write_text(sheet, encoding="utf-8")
    notes = adapted_notes()
    lifted = sum(n["pitch"] != n["source_pitch"] for n in notes)
    print(f"{target}: {len(notes)} attacks, {lifted} octave-adapted bass notes, {DURATION_MS / 1000:.0f} s")


if __name__ == "__main__":
    main()
