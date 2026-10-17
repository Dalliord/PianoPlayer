import math
import unittest

from player.models import EventKind
from player.parser import SheetParser, SheetSyntaxError
from player.plan_writer import build_plan


class TempoCommandTests(unittest.TestCase):
    def plan(self, source):
        return build_plan(SheetParser().parse(source), 100, 35)

    def test_local_tempo_triplets_and_reset_preserve_base_settings(self):
        plan = self.plan("a |bpm=120| b |step=1/3| c d e |reset| f")
        sounding = [e for e in plan.events if e.keys]
        for actual, expected in zip([e.offset_ms for e in sounding], [0, 100, 225, 225+500/3, 225+1000/3, 725]):
            self.assertAlmostEqual(actual, expected)
        self.assertAlmostEqual(plan.duration_ms, 825)
        self.assertTrue(all(e.kind == EventKind.NOTE for e in plan.events))

    def test_exact_ms_waits_zero_clock_and_fractional_independent_holds(self):
        plan = self.plan("|delay=0| [a<1000.25>s<75.125>] |wait=10.125| d<8.5> |wait=1500.375|")
        self.assertEqual([(e.offset_ms, e.hold_ms) for e in plan.events if e.keys],
                         [(0, 1000.25), (0, 75.125), (10.125, 8.5)])
        self.assertEqual(plan.duration_ms, 1510.5)
        self.assertEqual(self.plan("|delay=75.5| a-b").duration_ms, 226.5)

    def test_ramp_integrates_linear_bpm_across_notes_and_long_rests(self):
        # 120 -> 240 BPM over four quarter notes: integral = 2 ln(2) seconds.
        plan = self.plan("|bpm=120| |step=1| |ramp=240,4| a b c d e")
        notes = [e for e in plan.events if e.keys]
        for i, note in enumerate(notes):
            self.assertAlmostEqual(note.offset_ms, 2000 * math.log1p(i / 4))
        self.assertAlmostEqual(plan.duration_ms, 2000*math.log(2)+250)
        rest = self.plan("|bpm=120| |step=1| |ramp=240,4| ---- a")
        self.assertAlmostEqual(next(e.offset_ms for e in rest.events if e.keys), notes[-1].offset_ms)
        slow = self.plan("|bpm=240| |step=1| |ramp=120,4| ---- a")
        self.assertAlmostEqual(next(e.offset_ms for e in slow.events if e.keys), 2000*math.log(2))

    def test_fast_sequence_and_hold_do_not_block_a_tempo_change(self):
        plan = self.plan("|bpm=120| [as]<1500> |bpm=240| {dfg} h")
        self.assertEqual([e.offset_ms for e in plan.events if e.keys], [0, 125, 146.875, 168.75, 231.25])
        self.assertEqual(plan.duration_ms, 1500)

    def test_invalid_commands_are_highlighted_instead_of_becoming_keys(self):
        for source in ("|bpm=0|", "|bpm=nan|", "|step=1/0|", "|wait=-1|", "|delay=inf|", "|ramp=120,0|",
                       "|ramp=120|", "|what=1|", "|reset=1|", "|bpm=120", "[a|bpm=120|]"):
            with self.subTest(source=source), self.assertRaises(SheetSyntaxError):
                SheetParser().parse(source)


if __name__ == "__main__":
    unittest.main()
