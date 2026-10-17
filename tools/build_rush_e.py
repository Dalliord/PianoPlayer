"""Adapt PlayPianoSheets' full Hard Rush E for physical keyboard playback.

Preserve the source's attacks, pauses and accelerating opening. One 41-note
cluster requests both versions of nine physical keys; its replacement spans
the keyboard on 32 distinct keys and retains all twelve pitch classes.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from player.parser import SheetParser
from player.plan_writer import build_plan
from tools.render_song import KEY_TO_MIDI, physical_key

SOURCE = ROOT / "assets/arrangements/rush-e-hard-source.txt"
SOURCE_URL = "https://playpianosheets.com/sheets/rush-e-full-version"
TEMPO_URL = "https://virtualpianosheet.com/sheets/rush-e-full-version"
NOTE_DELAY_MS = 117  # 60000 / 128 / 4, rounded to the public integer ms field.
KEY_HOLD_MS = 90
SOURCE_CLUSTER = "!(@*%^$148abcdEfghiIjklmnoOpPqQstTuvWxyYz"
PLAYABLE_CLUSTER = "1@$%^*(qWEtyuiopasdfghjklZxcvbnm"
FINAL_HOLD_MS = 700
TAIL_CELLS = 13


def make_sheet(source: str) -> str:
    parsed = SheetParser().parse(source)
    sounding = [event for event in parsed.events if event.keys]
    if len(sounding) != 895 or source.count("[" + SOURCE_CLUSTER + "]") != 1:
        raise ValueError("Expected the verified full Hard source, not a short preview")
    final = sounding[-1]
    parts = []
    previous = 0
    for event in parsed.events:
        parts.append(source[previous:event.source_start])
        if not event.keys:
            token = source[event.source_start:event.source_end]
        else:
            keys = "".join(chr(key) for key in event.keys)
            cluster = keys == SOURCE_CLUSTER
            if cluster:
                keys = PLAYABLE_CLUSTER
            physical = [physical_key(key) for key in keys]
            if len(set(physical)) != len(physical):
                raise ValueError("Unexpected conflicting physical keys")
            holds = [FINAL_HOLD_MS if event is final else 140 if cluster
                     else 214 if KEY_TO_MIDI[key] < 60 else KEY_HOLD_MS for key in keys]
            if len(set(holds)) == 1:
                token = keys if len(keys) == 1 else "[" + keys + "]"
                if holds[0] != KEY_HOLD_MS:
                    token += f"<{holds[0]}>"
            else:
                token = "[" + "".join(key + (f"<{hold}>" if hold != KEY_HOLD_MS else "")
                                       for key, hold in zip(keys, holds)) + "]"
        parts.append(token)
        previous = event.source_end
    parts.append(source[previous:])
    return "".join(parts).rstrip() + "\n" + "-" * TAIL_CELLS + "\n"


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    sheet = make_sheet(source)
    target = ROOT / "assets/songs/rush-e.txt"
    target.write_text(sheet, encoding="utf-8")
    plan = build_plan(SheetParser().parse(sheet), NOTE_DELAY_MS, KEY_HOLD_MS)
    report = {
        "title": "Rush E (Full Version)", "artist": "Sheet Music Boss", "difficulty": "Hard",
        "retrieved_on": "2026-10-17", "source_url": SOURCE_URL,
        "source_version_file": "rush-e-full-version-hard.rps",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "tempo_basis_url": TEMPO_URL, "published_bpm": 128,
        "tempo_status": "Initial estimate from the published arrangement; not audio-aligned or tested in the browser",
        "grid": "sixteenth", "note_delay_ms": NOTE_DELAY_MS,
        "effective_bpm": 60000 / NOTE_DELAY_MS / 4, "key_hold_ms": KEY_HOLD_MS,
        "bass_hold_ms": 214, "final_hold_ms": FINAL_HOLD_MS,
        "extra_release_tail_cells": TAIL_CELLS, "duration_ms": plan.duration_ms,
        "source_attacks": 895, "source_pitch_attacks": 1760, "adapted_pitch_attacks": 1751,
        "cluster_replacement": {"source": SOURCE_CLUSTER, "adapted": PLAYABLE_CLUSTER,
                                "pitch_classes_preserved": list(range(12)), "physical_keys": 32},
        "limitations": ["One extreme cluster is revoiced for physical keys; it will differ from practice grading",
                        "This is the website's full Hard arrangement, not an exact official impossible MIDI"]
    }
    (SOURCE.parent / "rush-e-adaptation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Rush E: 895 attacks, 1751 pitches, {plan.duration_ms / 1000:.3f} s")
    print(target)


if __name__ == "__main__":
    main()
