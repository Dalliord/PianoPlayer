"""The short shuffle must retain its tune, swing, sustains and complete ending."""
import json
from pathlib import Path
import unittest

from player.humanization import humanize_plan
from player.parser import SheetParser
from player.plan_writer import build_plan
from player.song_library import load_song_library
from tools import compose_velvet_teeth as velvet
from tools.compose_moonlit_platform import PITCH_TO_KEY, pitch_number
from tools.render_song import KEY_TO_MIDI, physical_key

ROOT = Path(__file__).resolve().parents[1]


class VelvetTeethTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.song = next(song for song in load_song_library() if song.id == "velvet-teeth")
        cls.score = velvet.make_score()
        cls.plan = build_plan(SheetParser().parse(cls.song.sheet), cls.song.note_delay_ms, cls.song.key_hold_ms)

    def test_short_preset_and_complete_written_form(self):
        self.assertEqual((self.song.title, self.song.artist), ("Velvet Teeth", ""))
        self.assertEqual((self.song.note_delay_ms, self.song.key_hold_ms, self.song.start_delay_s), (80, 140, 3))
        self.assertEqual((self.song.source_url, self.song.practice_url, self.song.practice_transpose), ("", "", 0))
        self.assertEqual(len(self.score), 48)
        self.assertTrue(all(len(m["grid"]) == 24 for m in self.score))
        self.assertEqual(self.plan.duration_ms, 92_160)
        self.assertLess(self.plan.duration_ms, 100_000)
        self.assertEqual(self.song.sheet, velvet.make_sheet(self.score))
        document = json.loads((ROOT / "assets/originals/velvet-teeth-score.json").read_text(encoding="utf-8"))
        self.assertEqual(document["bars"], self.score)
        self.assertEqual((document["bpm"], document["meter"], document["swing_ratio"]), (125, "4/4", "2:1"))

    def test_sheet_preserves_every_written_pitch_onset_and_duration(self):
        expected = [((bar * 24 + slot) * 80, {pitch_number(p) for p in pitches}, m["holds_ms"][slot])
                    for bar, m in enumerate(self.score) for slot, pitches in enumerate(m["grid"]) if pitches]
        actual = [(e.offset_ms, {KEY_TO_MIDI[chr(key)] for key in e.keys},
                   e.hold_ms if e.hold_ms is not None else self.song.key_hold_ms)
                  for e in self.plan.events if e.keys]
        self.assertEqual(actual, expected)

    def test_written_swing_has_long_and_short_eighths_at_125_bpm(self):
        # An independently specified melody bar: 320/160 ms swing, not jitter.
        base = 11 * 1920
        melody = ("C5", "E5", "G5", "A5", "G5", "E5", "D5", "C5")
        offsets = (0, 320, 480, 800, 960, 1280, 1440, 1760)
        attacks = {e.offset_ms: set(e.keys) for e in self.plan.events if e.keys}
        for offset, pitch in zip(offsets, melody):
            self.assertIn(ord(PITCH_TO_KEY[pitch]), attacks[base + offset])
        self.assertEqual([right-left for left, right in zip(offsets, offsets[1:])], [320, 160, 320, 160, 320, 160, 320])

    def test_hook_returns_and_long_chords_support_following_melody(self):
        def tune(measure):
            return [(e["slot"], e["pitches"]) for e in measure["voices"]["lead"]]
        for original, reprise in ((2, 34), (3, 35), (4, 36)):
            self.assertEqual(tune(self.score[original]), tune(self.score[reprise]))
        self.assertEqual([m["section"] for m in self.score[:2]], ["Count-in riff"] * 2)
        self.assertEqual(sum(m["section"] == "Dancing on the edge" for m in self.score), 16)
        self.assertGreaterEqual(len({m["texture"] for m in self.score}), 8)
        held = [e for e in self.plan.events if len(e.keys) >= 3 and (e.hold_ms or 0) >= 400]
        self.assertTrue(held)
        self.assertTrue(any(e.offset_ms < following.offset_ms < e.offset_ms + e.hold_ms
                            for e in held for following in self.plan.events if following.keys))
        humanized = humanize_plan(self.plan, 80, 140, seed=20261016)
        self.assertEqual(humanized.duration_ms, 92_160)
        for original in held:
            groups = [e for e in humanized.events if e.source_start == original.source_start]
            self.assertTrue(all(e.hold_ms == original.hold_ms for e in groups))

    def test_chords_fit_seven_distinct_physical_keys(self):
        for event in self.plan.events:
            if event.keys:
                keys = [chr(key) for key in event.keys]
                self.assertLessEqual(len(keys), 7)
                self.assertEqual(len(keys), len({physical_key(key) for key in keys}))
                self.assertTrue(all(36 <= KEY_TO_MIDI[key] <= 96 for key in keys))

    def test_final_e_minor_resolution_keeps_full_release_tail(self):
        ending = self.score[-1]
        self.assertEqual(ending["harmony"][-1], "Em")
        final = next(e for e in reversed(self.plan.events) if e.keys)
        self.assertEqual({KEY_TO_MIDI[chr(key)] % 12 for key in final.keys}, {4, 7, 11})
        self.assertIn(ord("3"), final.keys)
        self.assertEqual(final.hold_ms, 800)
        self.assertGreaterEqual(self.plan.duration_ms - final.offset_ms - final.hold_ms, 750)
        humanized = humanize_plan(self.plan, 80, 140, seed=20261016)
        self.assertGreaterEqual(humanized.duration_ms - max(e.offset_ms + e.hold_ms
                                                           for e in humanized.events if e.keys), 750)


if __name__ == "__main__":
    unittest.main()
