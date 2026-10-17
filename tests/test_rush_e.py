"""Keep the complete Rush E rhythm while adapting one impossible key cluster."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import unittest

from player.humanization import humanize_plan
from player.parser import SheetParser
from player.plan_writer import build_plan
from player.song_library import load_song_library
from tools import build_rush_e as rush
from tools.render_song import KEY_TO_MIDI, collect_notes, physical_key


class RushETests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.song = next(song for song in load_song_library() if song.id == "rush-e")
        cls.source = rush.SOURCE.read_text(encoding="utf-8")
        cls.original = build_plan(SheetParser().parse(cls.source), 117, 90)
        cls.plan = build_plan(SheetParser().parse(cls.song.sheet), 117, 90)

    def test_full_hard_source_and_credited_preset(self):
        self.assertEqual((self.song.title, self.song.artist, self.song.difficulty),
                         ("Rush E (Full Version)", "Sheet Music Boss", "Hard"))
        self.assertEqual((self.song.note_delay_ms, self.song.key_hold_ms, self.song.start_delay_s), (117, 90, 3))
        self.assertTrue(self.source.startswith("u----\nu----\nu----\nu----"))
        self.assertTrue(self.source.rstrip().endswith("[^EP]--[^gJS]"))
        self.assertEqual(self.song.sheet, rush.make_sheet(self.source))
        self.assertIn("rush-e-full-version", self.song.practice_url)
        report = json.loads((rush.SOURCE.parent / "rush-e-adaptation.json").read_text(encoding="utf-8"))
        self.assertEqual(report["source_sha256"], hashlib.sha256(rush.SOURCE.read_bytes()).hexdigest())
        self.assertEqual(report["published_bpm"], 128)
        self.assertEqual(report["source_version_file"], "rush-e-full-version-hard.rps")

    def test_original_attack_times_and_all_other_pitches_are_preserved(self):
        def groups(plan):
            result = {}
            for e in plan.events:
                if e.keys:
                    result.setdefault(e.offset_ms, set()).update(e.keys)
            return result
        before, after = groups(self.original), groups(self.plan)
        self.assertEqual(len(before), 895)
        self.assertEqual(list(before), list(after))
        changed = [onset for onset in before if before[onset] != after[onset]]
        self.assertEqual(len(changed), 1)
        cluster = changed[0]
        self.assertEqual(len(before[cluster]), 41)
        self.assertEqual(len(after[cluster]), 32)
        for keys in (before[cluster], after[cluster]):
            self.assertEqual({KEY_TO_MIDI[chr(k)] % 12 for k in keys}, set(range(12)))
        for keys in after.values():
            self.assertEqual(len(keys), len({physical_key(chr(k)) for k in keys}))

    def test_written_intro_accelerates_and_final_chord_has_full_release(self):
        starts = [e.offset_ms for e in self.original.events if e.keys][:19]
        intervals = [b-a for a,b in zip(starts, starts[1:])]
        self.assertEqual(intervals[:4], [585] * 4)
        self.assertIn(351, intervals)
        self.assertIn(234, intervals)
        self.assertEqual(intervals[-5:], [117] * 5)
        notes, duration = collect_notes(self.song)
        self.assertEqual(len(notes), 1751)
        self.assertEqual(duration, 143_676)
        self.assertTrue(any(n.pitch < 60 and n.end_ms-n.start_ms == 214 for n in notes))
        final = [n for n in notes if n.start_ms == max(n.start_ms for n in notes)]
        self.assertTrue(all(n.end_ms - n.start_ms == 700 for n in final))
        self.assertGreaterEqual(duration - max(n.end_ms for n in notes), 750)

    def test_humanization_keeps_every_key_and_written_sustain(self):
        expected = Counter((e.source_start, key) for e in self.plan.events for key in e.keys)
        for seed in (1, 173, 20261017):
            actual = humanize_plan(self.plan, 117, 90, seed=seed)
            self.assertEqual(actual.duration_ms, self.plan.duration_ms)
            self.assertEqual(Counter((e.source_start, key) for e in actual.events for key in e.keys), expected)
            for original in self.plan.events:
                if original.hold_ms is not None:
                    self.assertTrue(all(e.hold_ms == original.hold_ms for e in actual.events
                                        if e.source_start == original.source_start and set(e.keys) <= set(original.keys)))


if __name__ == "__main__":
    unittest.main()
