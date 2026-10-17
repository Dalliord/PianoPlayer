from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from player.parser import SheetParser
from player.plan_writer import build_plan, write_plan


class PlanTests(unittest.TestCase):
    def plan(self, source, note=100, hold=35):
        return build_plan(SheetParser().parse(source), note, hold)

    def test_note_onsets_do_not_add_hold_time(self):
        plan = self.plan("abc")
        self.assertEqual([event.offset_ms for event in plan.events], [0, 100, 200])
        self.assertEqual(plan.duration_ms, 300)

    def test_fast_sequence_ratio_and_return_to_normal(self):
        plan = self.plan("{asdf}g")
        self.assertEqual([event.offset_ms for event in plan.events], [0, 35, 70, 105, 205])

    def test_fractional_fast_interval(self):
        plan = self.plan("{asd}", note=21)
        self.assertAlmostEqual(plan.events[1].offset_ms, 7.35)
        self.assertAlmostEqual(plan.events[2].offset_ms, 14.7)

    def test_pauses_use_note_delay(self):
        plan = self.plan("a--b", note=120)
        self.assertEqual([event.offset_ms for event in plan.events], [0, 120, 360])
        self.assertEqual(plan.duration_ms, 480)

    def test_chord_stays_one_simultaneous_event(self):
        plan = self.plan("[asd]b")
        self.assertEqual(plan.events[0].keys, tuple(map(ord, "asd")))
        self.assertEqual(plan.events[1].offset_ms, 100)

    def test_long_hold_does_not_slow_fast_sequence(self):
        plan = self.plan("{asd}", note=20, hold=200)
        self.assertEqual([event.offset_ms for event in plan.events], [0, 7, 14])
        self.assertEqual(plan.duration_ms, 214)

    def test_write_numeric_plan(self):
        plan = self.plan("[aS!]--{a-b}")
        with TemporaryDirectory() as folder:
            path = Path(folder) / "plan.tsv"
            write_plan(plan, path, 35)
            lines = path.read_text().splitlines()
        self.assertTrue(lines[0].startswith("ROBLOXSHEETS\t1\t35\t"))
        self.assertEqual(lines[1].split("\t")[2], "97,83,33")
        self.assertTrue(any(line.split("\t")[2] == "45" for line in lines[1:]))

    def test_invalid_timing_rejected(self):
        for note, hold in ((19, 35), (501, 35), (100, 4), (100, 201)):
            with self.subTest(note=note, hold=hold), self.assertRaises(ValueError):
                self.plan("a", note, hold)


if __name__ == "__main__":
    unittest.main()
