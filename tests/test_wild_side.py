"""The imported tune must preserve its reference notes, not become a new riff."""
from collections import Counter
import unittest

from player.humanization import humanize_plan
from player.parser import SheetParser
from player.plan_writer import build_plan
from player.song_library import load_song_library
from tools.build_wild_side import adapted_notes, load_reference, make_sheet
from tools.render_song import KEY_TO_MIDI, collect_notes, physical_key


class WildSideTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.song = next(s for s in load_song_library() if s.id == "wild-side-piano")
        cls.reference = load_reference()
        cls.notes = adapted_notes(cls.reference)
        cls.plan = build_plan(SheetParser().parse(cls.song.sheet), cls.song.note_delay_ms, cls.song.key_hold_ms)

    def test_reference_credit_and_written_preset(self):
        self.assertEqual(self.song.title, "Wild Side — Piano")
        self.assertEqual(self.song.artist, "ALI · Sheet Music Boss arrangement")
        self.assertEqual((self.song.note_delay_ms, self.song.key_hold_ms, self.song.start_delay_s), (20, 100, 3))
        self.assertEqual(self.song.practice_transpose, 0)
        self.assertEqual(len(self.reference["notes"]), 1008)
        self.assertEqual(self.song.sheet, make_sheet(self.reference))
        self.assertEqual(self.plan.duration_ms, 90_000)
        self.assertNotIn("velvet-teeth", {s.id for s in load_song_library()})

    def test_all_reference_attacks_and_individual_releases_survive_encoding(self):
        expected = Counter((n["offset_ms"], n["pitch"], n["hold_ms"]) for n in self.notes)
        actual = Counter((e.offset_ms, KEY_TO_MIDI[chr(key)], e.hold_ms)
                         for e in self.plan.events for key in e.keys)
        self.assertEqual(actual, expected)
        for note in self.notes:
            ideal = (note["source_frame"] - 103) * 1000 / 30
            self.assertLessEqual(abs(note["offset_ms"] - ideal), 10)

    def test_favourite_transition_keeps_the_climbing_run_and_bass(self):
        # Independent pitches and frame positions read at reference 0:50.
        expected = [(1500, 65), (1502, 67), (1504, 69), (1506, 71),
                    (1509, 72), (1511, 74), (1513, 75), (1515, 77),
                    (1517, 79), (1520, 81), (1522, 83), (1524, 84)]
        actual = {(n[1], n[0]) for n in self.reference["notes"] if n[3] == "R"}
        self.assertTrue(set(expected) <= actual)
        self.assertIn((36, 1500, 1502, "L"), [tuple(n) for n in self.reference["notes"]])
        self.assertEqual(next(n["offset_ms"] for n in self.notes
                              if n["source_frame"] == 1500 and n["pitch"] == 65), 46_560)

    def test_only_low_bass_octaves_are_revoiced_and_no_physical_collisions(self):
        self.assertEqual(sum(n["pitch"] != n["source_pitch"] for n in self.notes), 86)
        self.assertTrue(all(n["pitch"] == n["source_pitch"] for n in self.notes if n["hand"] == "R"))
        grouped = {}
        for n in self.notes:
            self.assertTrue(36 <= n["pitch"] <= 96)
            keys = grouped.setdefault(n["offset_ms"], set())
            key = physical_key(n["key"])
            self.assertNotIn(key, keys)
            keys.add(key)

    def test_humanization_keeps_every_note_and_explicit_hold(self):
        for seed in (1, 173, 20261016):
            actual = humanize_plan(self.plan, 20, 100, seed=seed)
            self.assertEqual(Counter((e.source_start, key, e.hold_ms) for e in actual.events for key in e.keys),
                             Counter((e.source_start, key, e.hold_ms) for e in self.plan.events for key in e.keys))
            self.assertEqual(actual.duration_ms, 90_000)
        notes, duration = collect_notes(self.song)
        self.assertEqual(len(notes), 1008)
        self.assertEqual(duration, 90_000)
        self.assertGreaterEqual(duration - max(n.end_ms for n in notes), 750)


if __name__ == "__main__":
    unittest.main()
