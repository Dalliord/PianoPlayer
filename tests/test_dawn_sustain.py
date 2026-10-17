"""Written sustains enrich Dawn without the earlier missing-phrase regression."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import unittest

from player.humanization import humanize_plan
from player.parser import SheetParser
from player.plan_writer import build_plan
from player.song_library import load_song_library
from tools import compose_wolf_last_dawn as dawn
from tools.render_song import collect_notes


class DawnSustainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.song = next(s for s in load_song_library() if s.id == "wolf-last-dawn")
        cls.score = dawn.make_score()
        cls.plan = build_plan(SheetParser().parse(cls.song.sheet), 75, 150)
        cls.notes, cls.duration = collect_notes(cls.song)

    def test_all_3541_original_attacks_keep_their_exact_pitch_and_onset(self):
        # Digest recorded from the complete pre-sustain sheet on 2026-10-16.
        # Independent of the updated composer and its new release annotations.
        attacks = sorted((note.start_ms, note.pitch) for note in self.notes)
        self.assertEqual(len(attacks), 3541)
        self.assertEqual(hashlib.sha256(json.dumps(attacks, separators=(",", ":")).encode()).hexdigest(),
                         "8e8c382d954a1df33ac589b67e627a5a6b79f21b30aadcb51370e6b28cc35028")
        stored = json.loads((Path(__file__).resolve().parents[1] / "assets/originals/wolf-last-dawn-score.json")
                            .read_text(encoding="utf-8"))
        self.assertEqual(stored["bars"], self.score)
        self.assertEqual(self.song.sheet, dawn.make_sheet(self.score))

    def test_long_bass_and_bell_chords_support_the_independent_lead(self):
        opening_bass = next(n for n in self.notes if n.start_ms == 0 and n.pitch == 36)
        self.assertEqual(opening_bass.end_ms, 1125)
        opening_bells = [n for n in self.notes if n.start_ms == 300]
        self.assertEqual({n.pitch: n.end_ms for n in opening_bells}, {63: 1200, 72: 588})
        # C5 releases before the lead rearticulates it at 600 ms; Eb4 keeps
        # ringing underneath both that note and the following melodic attack.
        self.assertTrue(any(300 < n.start_ms < 1125 and n.pitch >= 60 for n in self.notes))
        self.assertGreater(sum(n.end_ms - n.start_ms > 200 for n in self.notes), 1700)
        # Lead C5 and bass C2 enter together but release independently.
        entrance = [n for n in self.notes if n.start_ms == 9600]
        self.assertGreater(len({n.end_ms for n in entrance}), 1)

    def test_harmonic_changes_and_real_silence_have_no_lingering_keys(self):
        self.assertEqual(self.duration, 300_000)
        before_breath = [n for n in self.notes if n.start_ms < 180_000]
        self.assertEqual(max(n.end_ms for n in before_breath), 179_200)
        self.assertTrue(all(not 180_000 <= n.start_ms < 182_400 for n in self.notes))
        self.assertTrue(all(n.end_ms <= 182_400 for n in before_breath))
        self.assertEqual(min(n.start_ms for n in self.notes if n.start_ms >= 180_000), 182_400)
        final = [n for n in self.notes if n.start_ms == 298_800]
        self.assertEqual({n.pitch % 12 for n in final}, {0, 4, 7})
        self.assertTrue(all(n.end_ms == 299_200 for n in final))
        self.assertGreaterEqual(300_000 - max(n.end_ms for n in self.notes), 750)
        for n in self.notes:
            bar = int(n.start_ms // 2400)
            measure = self.score[bar]
            if len(measure["harmony"]) > 1:
                boundary = bar * 2400 + (1200 if n.start_ms % 2400 < 1200 else 2400)
                self.assertLessEqual(n.end_ms, boundary)

    def test_second_half_keeps_at_most_seven_held_keys_even_with_long_tails(self):
        active = 0
        maximum = 0
        timeline = sorted([(n.start_ms, 1) for n in self.notes] + [(n.end_ms, -1) for n in self.notes])
        for offset, delta in timeline:
            active += delta
            if offset >= 182_400:
                maximum = max(maximum, active)
        self.assertEqual(maximum, 7)

    def test_humanization_keeps_sustain_lengths_attacks_and_release_room(self):
        expected = Counter((event.source_start, key, event.hold_ms) for event in self.plan.events for key in event.keys)
        for seed in (1, 173, 20261016):
            plan = humanize_plan(self.plan, 75, 150, seed=seed)
            self.assertEqual(plan.duration_ms, 300_000)
            # Unannotated 150 ms articulation can vary; written holds cannot.
            actual = Counter((event.source_start, key, event.hold_ms) for event in plan.events for key in event.keys)
            explicit = Counter({key: count for key, count in expected.items() if key[2] is not None})
            self.assertTrue(all(actual[key] == count for key, count in explicit.items()))
            self.assertEqual(Counter((e.source_start, key) for e in self.plan.events for key in e.keys),
                             Counter((e.source_start, key) for e in plan.events for key in e.keys))
            self.assertLessEqual(max(e.offset_ms + (e.hold_ms or 150) for e in plan.events if e.keys), 299_250)
            self.assertLessEqual(max(e.offset_ms + (e.hold_ms or 150) for e in plan.events
                                     if e.keys and e.offset_ms < 180_000), 179_250)


if __name__ == "__main__":
    unittest.main()
