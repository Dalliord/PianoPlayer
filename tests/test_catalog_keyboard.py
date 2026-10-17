"""Validate bundled sheets and optionally replay their AHK packets into a recorder.

The recorder never calls SendInput/SendEvent and advances a simulated clock, so
the complete catalog can be checked without keyboard input or musical waits.
"""
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest

from player.parser import SheetParser
from player.plan_writer import build_plan, write_plan
from player.song_library import load_song_library


ROOT = Path(__file__).resolve().parents[1]
AHK = Path(os.environ.get("AHK_EXECUTABLE", "C:/Program Files/AutoHotkey/v2/AutoHotkey64.exe"))

# This US keyboard table is deliberately independent of Windows VkKeyScanExW
# and the production implementation's MapCodePoint.
PHYSICAL_KEYS = {}
for lower, upper in zip("abcdefghijklmnopqrstuvwxyz", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    PHYSICAL_KEYS[lower] = PHYSICAL_KEYS[upper] = ord(upper)
for plain, shifted, vk in zip(
        "`1234567890-=[]\\;',./",
        '~!@#$%^&*()_+{}|:"<>?',
        (0xC0, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38,
         0x39, 0x30, 0xBD, 0xBB, 0xDB, 0xDD, 0xDC, 0xBA, 0xDE,
         0xBC, 0xBE, 0xBF)):
    PHYSICAL_KEYS[plain] = PHYSICAL_KEYS[shifted] = vk


def validate_physical_chords(song_id, sheet, plan):
    """Reject incompatible characters on one physical key; deduplicate repeats."""
    for index, event in enumerate(plan.events, 1):
        seen = {}
        for code in event.keys:
            character = chr(code)
            vk = PHYSICAL_KEYS[character]
            previous = seen.get(vk)
            if previous is not None and previous != character:
                source = sheet[event.source_start:event.source_end]
                raise AssertionError(
                    f"{song_id}: event {index}, source {event.source_start}:{event.source_end} "
                    f"{source!r}: {previous!r} and {character!r} share physical key vk{vk:02X}")
            seen[vk] = character


class CatalogKeyboardValidationTests(unittest.TestCase):
    def test_bundled_chords_have_no_physical_key_collisions(self):
        for song in load_song_library():
            with self.subTest(song=song.id):
                plan = build_plan(SheetParser().parse(song.sheet),
                                  song.note_delay_ms, song.key_hold_ms)
                validate_physical_chords(song.id, song.sheet, plan)

    def test_repeated_character_is_allowed_but_shift_collision_is_rejected(self):
        source = "[aa] [aA]"
        plan = build_plan(SheetParser().parse(source))
        with self.assertRaisesRegex(AssertionError, r"fixture: event 2, source 5:9.*'a'.*'A'.*vk41"):
            validate_physical_chords("fixture", source, plan)


@unittest.skipUnless(os.environ.get("RUN_AHK_TESTS") == "1" and AHK.is_file(),
                     "Set RUN_AHK_TESTS=1 with AHK v2 installed")
class CatalogKeyboardContractTests(unittest.TestCase):
    def test_every_catalog_plan_and_overlapping_holds_emit_the_expected_characters(self):
        from player.humanization import humanize_plan

        cases = []
        parser = SheetParser()
        for song in load_song_library():
            cases.append((song.id, song.sheet, song.note_delay_ms, song.key_hold_ms))
            # Also exercise real song chords with overlapping physical holds,
            # even when that song's preset normally separates every onset.
            cases.append((song.id + "-overlap", song.sheet, 20, 200))
        cases.append(("retrigger-and-mixed-shift", "[aa] {aAAa} [ejTu] [dEuw] S a ! 1 [!!] ---", 20, 200))
        cases.append(("release-at-next-onset", "A a [ejTu] [dEuw] [aa]", 100, 100))
        cases.append(("sustained-chord-with-melody", "[asd]<2000> f g h j k l z x c v b n m ---", 100, 35))
        cases.append(("sustained-partial-retrigger", "[ejTu]<3000> a j<900> t -- T u ---", 100, 35))
        cases.append(("sustained-fast", "{aAAa}<1000> [sd]<60000> f g", 20, 200))
        cases.append(("individual-chord-holds", "[e<1000>j<500>T<200>u]<800> a j<100> t --", 100, 35))
        cases.append(("fractional-midi-timing", "|delay=0| [e<1000.25>j<75.125>T<600.5>u<214.125>] |wait=12.375| a<35.5> |wait=1200|", 100, 35))
        cases.append(("tempo-ramp-and-triplets", "|bpm=120| |step=1/3| [ejTu] a |ramp=180,4| {asd} -- |reset| f", 100, 35))

        with TemporaryDirectory(prefix="catalog-keyboard-") as directory:
            folder = Path(directory)
            manifest = folder / "manifest.tsv"
            rows = []
            for index, (case_id, source, delay, hold) in enumerate(cases):
                plan = build_plan(parser.parse(source), delay, hold)
                validate_physical_chords(case_id, source, plan)
                path = folder / f"{index}.tsv"
                write_plan(plan, path, hold)
                rows.append(f"{case_id}\t{path}\n")
            humanized_cases = [
                ("humanized-mixed-shift", "[ejTu] [dEuw] {aAAa} [!!] S a 1 ! ---", 75, 150),
                ("humanized-overlapping-fast", "[1etuS] {SasSaAS} [dEuw] [ejTu] [aa] ---", 20, 200),
                ("humanized-sustained-chord", "[ejTu]<2000> a s d f g h j ---", 100, 35),
            ]
            humanized_cases.extend((song.id + "-humanized", song.sheet, song.note_delay_ms, song.key_hold_ms)
                                   for song in load_song_library())
            for case_id, source, delay, hold in humanized_cases:
                plan = humanize_plan(build_plan(parser.parse(source), delay, hold),
                                     delay, hold, seed=173)
                validate_physical_chords(case_id, source, plan)
                path = folder / f"{case_id}.tsv"
                write_plan(plan, path, hold)
                rows.append(f"{case_id}\t{path}\n")
            manifest.write_text("".join(rows), encoding="utf-8")
            result = subprocess.run(
                [str(AHK), "/ErrorStdOut=UTF-8", str(ROOT / "tests/catalog_keyboard_contract.ahk"),
                 str(manifest)], capture_output=True, text=True, encoding="utf-8",
                timeout=30, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn(f"OK\tcatalog keyboard contract\t{len(rows)} plans", result.stdout)


if __name__ == "__main__":
    unittest.main()
