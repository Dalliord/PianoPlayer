"""Long sheet holds overlap subsequent notes without changing the note clock."""
from collections import Counter
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from player.humanization import humanize_plan
from player.parser import SheetParser, SheetSyntaxError
from player.plan_writer import build_plan, write_plan


class SustainTests(unittest.TestCase):
    def plan(self, source, delay=100, hold=35):
        return build_plan(SheetParser().parse(source), delay, hold)

    def test_chord_stays_down_while_following_notes_start_on_time(self):
        source = "[asd]<1000> f g h"
        parsed = SheetParser().parse(source)
        self.assertEqual([source[e.source_start:e.source_end] for e in parsed.events],
                         ["[asd]<1000>", "f", "g", "h"])
        plan = self.plan(source)
        self.assertEqual([e.offset_ms for e in plan.events], [0, 100, 200, 300])
        self.assertEqual([e.hold_ms for e in plan.events], [1000, None, None, None])
        self.assertEqual(plan.events[0].keys, tuple(map(ord, "asd")))
        self.assertEqual(plan.duration_ms, 1000)

    def test_independent_early_holds_keep_longest_release_at_end(self):
        plan = self.plan("a<2000> [sd]<700> f<1500> g")
        self.assertEqual([(e.offset_ms, e.hold_ms) for e in plan.events],
                         [(0, 2000), (100, 700), (200, 1500), (300, None)])
        self.assertEqual(plan.duration_ms, 2000)
        self.assertEqual(self.plan("a<60000>").duration_ms, 60000)
        self.assertEqual(self.plan("a<5>").duration_ms, 100)
        # Ordinary pauses remain part of the score, independent of key release.
        self.assertEqual(self.plan("a<1000>" + "-" * 20).duration_ms, 2100)

    def test_fast_sequence_holds_each_note_without_slowing_it(self):
        plan = self.plan("{asd}<800> f")
        self.assertEqual([(e.offset_ms, e.hold_ms) for e in plan.events],
                         [(0, 800), (35, 800), (70, 800), (170, None)])
        self.assertEqual(plan.duration_ms, 870)

    def test_invalid_hold_annotations_are_highlighted_instead_of_played(self):
        for source in ("a<>", "a<4>", "a<60001>", "a<-1>", "a<1.5>",
                       "a<NaN>", "a<1000ms>", "a<１２>", "a<1000", "a<1000><200>",
                       "<1000>a", "a <1000>", "-<1000>", "[a <1000>s]", "{a<4>b}"):
            with self.subTest(source=source), self.assertRaises(SheetSyntaxError):
                SheetParser().parse(source)
        with self.assertRaises(SheetSyntaxError) as caught:
            SheetParser().parse("ab [sd]<0> f")
        self.assertEqual((caught.exception.start, caught.exception.end), (7, 10))

    def test_individual_chord_holds_release_separately_on_one_shared_onset(self):
        source = "[a<1000>s<200>d]<500> f"
        parsed = SheetParser().parse(source)
        self.assertEqual(parsed.events[0].key_holds_ms, (1000, 200, None))
        plan = build_plan(parsed)
        self.assertEqual([(e.offset_ms, e.keys, e.hold_ms) for e in plan.events], [
            (0, (ord('a'),), 1000), (0, (ord('s'),), 200),
            (0, (ord('d'),), 500), (100, (ord('f'),), None),
        ])
        self.assertEqual(plan.duration_ms, 1000)
        self.assertTrue(all(e.source_start == 0 and e.source_end == len(source)-2 for e in plan.events[:3]))
        fast = self.plan("{a<700>s<200>d}<400> f")
        self.assertEqual([(e.offset_ms, e.hold_ms) for e in fast.events],
                         [(0, 700), (35, 200), (70, 400), (170, None)])

    def test_humanization_retains_explicit_holds_and_all_following_keys(self):
        original = self.plan("[asd]<1500> f g h j k l z x c v b n m --")
        expected = Counter((e.source_start, key) for e in original.events for key in e.keys)
        for seed in range(12):
            actual = humanize_plan(original, 100, 35, seed=seed)
            self.assertEqual(actual.duration_ms, original.duration_ms)
            self.assertEqual(Counter((e.source_start, key) for e in actual.events for key in e.keys), expected)
            held = [e for e in actual.events if e.source_start == 0]
            self.assertTrue(all(e.hold_ms == 1500 for e in held))
            self.assertTrue(all(e.offset_ms + e.hold_ms <= actual.duration_ms
                                for e in actual.events if e.keys))
        # If the held chord is the final sound, its full duration still fits.
        tail = humanize_plan(self.plan("[asd]<60000>"), 100, 35, seed=9)
        self.assertTrue(all(e.hold_ms == 60000 for e in tail.events if e.keys))
        self.assertTrue(all(e.offset_ms == 0 for e in tail.events if e.keys))

    def test_plan_versions_keep_existing_formats_and_export_long_holds(self):
        with TemporaryDirectory() as directory:
            for source, version in (("[asd] f", "1"), ("a<150> f", "2"), ("[asd]<1000> f", "3")):
                plan = self.plan(source)
                path = Path(directory) / "plan.tsv"
                write_plan(plan, path, 35)
                rows = [row.split("\t") for row in path.read_text().splitlines()]
                self.assertEqual(rows[0][1], version)
                if version == "3":
                    self.assertEqual(rows[1], ["0.000", "CHORD", "97,115,100", "0", "11", "1000.000"])
                    self.assertEqual(rows[2][5], "35.000")

    def test_audio_note_deadlines_keep_sustain_and_partial_retriggers(self):
        try:
            from tools.render_song import collect_notes
        except ImportError:
            self.skipTest("Optional renderer needs numpy")
        from player.song_library import load_song_library
        song = replace(load_song_library()[0], sheet="[1tf]<1000> h t j", note_delay_ms=100, key_hold_ms=35)
        notes, duration = collect_notes(song)
        self.assertEqual([(n.pitch, n.start_ms, n.end_ms) for n in notes], [
            (36, 0, 1000), (60, 0, 200), (76, 0, 1000),
            (79, 100, 135), (60, 200, 235), (81, 300, 335),
        ])
        self.assertEqual(duration, 1000)


if __name__ == "__main__":
    unittest.main()
