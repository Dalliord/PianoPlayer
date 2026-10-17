"""Humanization changes articulation without changing the score or its clock.

These checks only inspect numeric plans; they never launch AHK or send keys.
"""
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from player.humanization import humanize_plan
from player.models import EventKind
from player.parser import SheetParser
from player.plan_writer import build_plan, write_plan
from player.song_library import load_song_library


class HumanizationTests(unittest.TestCase):
    @staticmethod
    def plan(source, delay=100, hold=35):
        return build_plan(SheetParser().parse(source), delay, hold)

    @staticmethod
    def score_keys(plan, *, deduplicate=False):
        """Count pitches with their source, including repeated fast notes."""
        return Counter(
            (event.source_start, event.source_end, key)
            for event in plan.events
            for key in (dict.fromkeys(event.keys) if deduplicate else event.keys)
        )

    def assert_valid_articulation(self, original, actual, delay, hold):
        self.assertEqual(actual.duration_ms, original.duration_ms)
        self.assertEqual(self.score_keys(actual), self.score_keys(original, deduplicate=True))
        self.assertEqual(
            [(event.offset_ms, event.source_start, event.source_end)
             for event in actual.events if event.kind == EventKind.PAUSE],
            [(event.offset_ms, event.source_start, event.source_end)
             for event in original.events if event.kind == EventKind.PAUSE],
        )
        offsets = [event.offset_ms for event in actual.events]
        self.assertEqual(offsets, sorted(offsets))
        sources = [event.source_start for event in actual.events]
        self.assertEqual(sources, sorted(sources))
        hold_variation = max(2, hold * 0.07)
        for event in actual.events:
            with self.subTest(offset=event.offset_ms, source=event.source_start):
                self.assertGreaterEqual(event.offset_ms, 0)
                self.assertLessEqual(event.offset_ms, actual.duration_ms)
                if not event.keys:
                    continue
                self.assertIsNotNone(event.hold_ms)
                self.assertLessEqual(event.offset_ms + event.hold_ms,
                                     actual.duration_ms + 1e-8)
                # Splitting chords may add up to 6 ms after the base onset.
                originals = [candidate for candidate in original.events
                             if candidate.source_start == event.source_start
                             and candidate.source_end == event.source_end
                             and set(event.keys).issubset(candidate.keys)]
                jitter = min(10, delay * 0.06)
                self.assertTrue(any(
                    -jitter - 1e-8 <= event.offset_ms - candidate.offset_ms
                    <= jitter + 6 + 1e-8 for candidate in originals
                ))
                # Only the global articulation varies. Written per-key holds
                # retain their exact duration, including values above 200 ms.
                self.assertTrue(any(
                    event.hold_ms == candidate.hold_ms if candidate.hold_ms is not None
                    else max(5, hold - hold_variation) - 1e-8 <= event.hold_ms <= min(200, hold + hold_variation) + 1e-8
                    for candidate in originals
                ))

    def test_seed_repeats_a_performance_and_different_seeds_vary_it(self):
        original = self.plan("a[sdGh]f{jklz}--[xCvb]n" * 3, 100, 100)
        first = humanize_plan(original, 100, 100, seed=1234)
        self.assertEqual(first, humanize_plan(original, 100, 100, seed=1234))
        self.assertNotEqual(first, humanize_plan(original, 100, 100, seed=4321))
        self.assertNotEqual(first, original)
        self.assertGreater(len({event.hold_ms for event in first.events if event.keys}), 1)
        self.assertTrue(any(event.offset_ms != source.offset_ms
                            for source in original.events if source.keys
                            for event in first.events
                            if event.source_start == source.source_start))
        self.assert_valid_articulation(original, first, 100, 100)

    def test_default_seed_produces_fresh_performances(self):
        original = self.plan("asdfghjkl" * 4)
        versions = {humanize_plan(original, 100, 35) for _ in range(4)}
        self.assertGreater(len(versions), 1)

    def test_chord_is_rolled_slightly_and_repeated_character_is_pressed_once(self):
        original = self.plan("[aasdffghjk]")
        actual = humanize_plan(original, 100, 35, seed=42)
        groups = [event for event in actual.events if event.keys]
        self.assertIn(len(groups), (2, 3))
        spread = groups[-1].offset_ms - groups[0].offset_ms
        self.assertGreater(spread, 0)
        self.assertLessEqual(spread, 6)
        self.assertEqual(tuple(key for event in groups for key in event.keys),
                         tuple(dict.fromkeys(original.events[0].keys)))
        self.assert_valid_articulation(original, actual, 100, 35)

    def test_mixed_shift_chords_and_fast_repeated_notes_keep_their_characters(self):
        original = self.plan("[ejTu] [dEuw] [!Sgp] [aa] {aAAa}", 20, 200)
        actual = humanize_plan(original, 20, 200, seed=74)
        self.assert_valid_articulation(original, actual, 20, 200)
        fast = original.events[-1]
        fast_keys = tuple(key for event in actual.events
                          if event.source_start == fast.source_start
                          for key in event.keys)
        self.assertEqual(fast_keys, tuple(map(ord, "aAAa")))

    def test_dense_fast_passage_keeps_onset_order_at_timing_extremes(self):
        source = "[asdfghjkl]{qwe}[zxcv][tyu]------[oip]a"
        for delay in (20, 500):
            for hold in (5, 200):
                original = self.plan(source, delay, hold)
                for seed in range(8):
                    with self.subTest(delay=delay, hold=hold, seed=seed):
                        actual = humanize_plan(original, delay, hold, seed=seed)
                        self.assert_valid_articulation(original, actual, delay, hold)

    def test_long_pause_is_not_shortened_or_retimed(self):
        original = self.plan("a" + "-" * 80 + "[sDfH]", 100, 35)
        for seed in range(5):
            actual = humanize_plan(original, 100, 35, seed=seed)
            self.assert_valid_articulation(original, actual, 100, 35)
            pause = next(event for event in actual.events if not event.keys)
            after = next(event for event in actual.events
                         if event.source_start > pause.source_start)
            self.assertGreaterEqual(after.offset_ms, 8094)
            self.assertEqual(pause.offset_ms, 100)

    def test_input_plan_is_immutable_and_empty_or_pause_only_scores_are_unchanged(self):
        original = self.plan("[asd]{fgh}---j")
        before = self.plan("[asd]{fgh}---j")
        humanize_plan(original, 100, 35, seed=3)
        self.assertEqual(original, before)
        self.assertTrue(all(event.hold_ms is None for event in original.events))
        for source in ("", "---", "-- --"):
            plan = self.plan(source)
            self.assertEqual(humanize_plan(plan, 100, 35, seed=3), plan)

    def test_five_minute_song_and_false_ending_keep_their_absolute_clock(self):
        song = next(song for song in load_song_library() if song.id == "wolf-last-dawn")
        original = self.plan(song.sheet, song.note_delay_ms, song.key_hold_ms)
        actual = humanize_plan(original, song.note_delay_ms, song.key_hold_ms, seed=2026)
        self.assertEqual(actual.duration_ms, 300_000)
        self.assert_valid_articulation(original, actual, song.note_delay_ms, song.key_hold_ms)
        # The silent breath before the drop remains an explicit score event.
        breath = [event for event in original.events if not event.keys
                  and 178_000 <= event.offset_ms < 182_400]
        self.assertTrue(breath)
        for event in breath:
            self.assertIn(event, actual.events)

    def test_invalid_timing_is_rejected(self):
        original = self.plan("a")
        for delay, hold in ((19, 35), (501, 35), (100, 4), (100, 201)):
            with self.subTest(delay=delay, hold=hold), self.assertRaises(ValueError):
                humanize_plan(original, delay, hold, seed=0)

    def test_worker_plan_retains_the_humanized_hold_for_every_group(self):
        original = self.plan("[ejTu]--{asdf}", 100, 35)
        actual = humanize_plan(original, 100, 35, seed=314)
        with TemporaryDirectory() as directory:
            path = Path(directory) / "humanized.tsv"
            write_plan(actual, path, 35)
            rows = [line.split("\t") for line in path.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(rows[0], ["ROBLOXSHEETS", "2", "35", "505.000"])
        self.assertEqual(len(rows) - 1, len(actual.events))
        for row, event in zip(rows[1:], actual.events):
            self.assertEqual(len(row), 6)
            self.assertAlmostEqual(float(row[0]), event.offset_ms, places=3)
            self.assertEqual(row[1], event.kind.value)
            self.assertEqual(row[2], ",".join(map(str, event.keys)) or "0")
            self.assertEqual((int(row[3]), int(row[4])), (event.source_start, event.source_end))
            self.assertAlmostEqual(float(row[5]), event.hold_ms if event.keys else 0, places=3)


if __name__ == "__main__":
    unittest.main()
