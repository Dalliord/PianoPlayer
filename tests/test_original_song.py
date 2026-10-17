"""The written score and the player must agree on pitch, measure and rhythm."""
import json
from pathlib import Path
import unittest

from player.parser import SheetParser
from player.plan_writer import build_plan
from player.song_library import load_song_library
from tests.library_archive import load_historical_library
from tools.compose_moonlit_platform import (
    BARS, PITCH_TO_KEY, make_score, make_sheet, pitch_number,
)
from tools import compose_starlight_chase as starlight
from tools import compose_wolf_last_dawn as dawn


class OriginalSongTests(unittest.TestCase):
    def test_written_score_matches_all_player_onsets_and_pitches(self):
        song = next(song for song in load_historical_library() if song.id == "moonlit-platform")
        score = make_score()
        self.assertEqual(song.sheet, make_sheet(score))
        self.assertEqual((song.note_delay_ms, song.key_hold_ms, song.start_delay_s), (150, 200, 3))
        self.assertEqual(song.source_url, "")
        self.assertEqual(song.practice_url, "")
        self.assertEqual(len(BARS), 40)
        plan = build_plan(SheetParser().parse(song.sheet), song.note_delay_ms, song.key_hold_ms)
        actual = [(event.offset_ms, set(event.keys)) for event in plan.events if event.keys]
        expected = [((bar * 16 + slot) * 150, {ord(PITCH_TO_KEY[pitch]) for pitch in pitches})
                    for bar, measure in enumerate(score)
                    for slot, pitches in enumerate(measure["grid"]) if pitches]
        self.assertEqual(actual, expected)
        self.assertEqual(plan.duration_ms, 96_000)
        self.assertEqual([measure["section"] for measure in score[::4]],
                         ["Intro", "A", "A", "A variation", "A variation", "B", "B", "A return", "A return", "Coda"])
        sounding = [event for event in plan.events if event.keys]
        self.assertGreater(sum(len(event.keys) > 1 for event in sounding) / len(sounding), 0.55)

    def test_untransposed_keyboard_pitch_anchors(self):
        # Independent anchors at octave boundaries and black keys, not generated expected data.
        for pitch, key, midi in [("C2", "1", 36), ("C3", "8", 48), ("C4", "t", 60),
                                 ("A4", "p", 69), ("C5", "s", 72), ("C6", "l", 84),
                                 ("C7", "m", 96), ("G#3", "W", 56), ("F#5", "G", 78)]:
            with self.subTest(pitch=pitch):
                self.assertEqual(PITCH_TO_KEY[pitch], key)
                self.assertEqual(pitch_number(pitch), midi)

    def test_starlight_chase_score_matches_player_and_requested_duration(self):
        song = next(song for song in load_historical_library() if song.id == "starlight-chase")
        score = starlight.make_score()
        self.assertEqual(song.sheet, make_sheet(score))
        self.assertEqual((song.note_delay_ms, song.key_hold_ms, song.start_delay_s), (125, 200, 3))
        self.assertEqual((song.source_url, song.practice_url), ("", ""))
        self.assertEqual(len(score), 80)
        self.assertTrue(all(len(measure["grid"]) == 16 for measure in score))
        plan = build_plan(SheetParser().parse(song.sheet), song.note_delay_ms, song.key_hold_ms)
        actual = [(event.offset_ms, set(event.keys)) for event in plan.events if event.keys]
        expected = [((bar * 16 + slot) * 125, {ord(PITCH_TO_KEY[pitch]) for pitch in pitches})
                    for bar, measure in enumerate(score)
                    for slot, pitches in enumerate(measure["grid"]) if pitches]
        self.assertEqual(actual, expected)
        self.assertEqual(plan.duration_ms, 160_000)
        self.assertTrue(150_000 <= plan.duration_ms <= 180_000)
        # The contrasting bridge preserves room around the lead instead of
        # extending a continuously busy pattern to reach the requested length.
        bridge_bar = score[36]
        self.assertEqual(bridge_bar["section"], "Bridge")
        self.assertTrue(all(not bridge_bar["grid"][slot] for slot in (1, 2, 3, 5, 7, 9, 10, 11, 13, 15)))

    def test_original_song_has_its_english_title(self):
        songs = {song.id: song for song in load_song_library()}
        self.assertNotIn("neon-express", songs)
        self.assertNotIn("moonlit-platform", songs)
        self.assertNotIn("starlight-chase", songs)
        self.assertEqual(songs["wolf-last-dawn"].title, "Until We Reach the Dawn")
        self.assertTrue(songs["wolf-last-dawn"].title.isascii())

    def test_dawn_written_32nd_note_score_matches_exact_five_minute_plan(self):
        song = next(song for song in load_song_library() if song.id == "wolf-last-dawn")
        score = dawn.make_score()
        self.assertEqual(song.title, "Until We Reach the Dawn")
        self.assertEqual(song.sheet, dawn.make_sheet(score))
        self.assertEqual((song.note_delay_ms, song.key_hold_ms, song.start_delay_s), (75, 150, 3))
        self.assertEqual(len(score), 125)
        self.assertTrue(all(len(measure["grid"]) == 32 for measure in score))
        plan = build_plan(SheetParser().parse(song.sheet), song.note_delay_ms, song.key_hold_ms)
        actual = sorted((event.offset_ms, key, event.hold_ms or 150)
                        for event in plan.events for key in event.keys)
        expected = sorted(((bar * 32 + slot) * 75, ord(PITCH_TO_KEY[pitch]), measure["holds_ms"][slot][pitch])
                    for bar, measure in enumerate(score)
                    for slot, pitches in enumerate(measure["grid"]) for pitch in pitches)
        self.assertEqual(actual, expected)
        self.assertEqual(plan.duration_ms, 300_000)
        self.assertLessEqual(max(event.offset_ms for event in plan.events if event.keys), 298_950)

    def test_dawn_has_independent_lines_and_transformed_happy_ending(self):
        score = dawn.make_score()
        sounding = [pitches for measure in score[:75] for pitches in measure["grid"] if pitches]
        # Running voices remain intact while chord voicings are made smaller.
        self.assertGreater(sum(len(pitches) == 1 for pitches in sounding) / len(sounding), 0.65)
        self.assertLess(sum(len(pitches) >= 4 for pitches in sounding) / len(sounding), 0.08)
        self.assertGreaterEqual(len({measure["texture"] for measure in score}), 9)
        self.assertEqual([measure["section"] for measure in score[44:56]], ["Two voices one path"] * 12)
        self.assertTrue(all(measure["voices"]["counter"] for measure in score[44:55]))
        # The opening minor third becomes E natural, with the love theme in a
        # separately timed countervoice, rather than changing only the last chord.
        arrival = score[116]
        lead = {event["slot"]: event["pitches"] for event in arrival["voices"]["lead"]}
        self.assertEqual([lead[slot] for slot in (0, 6, 8, 14)], [["G5"], ["C6"], ["E6"], ["D6"]])
        self.assertTrue(arrival["voices"]["counter"])
        self.assertEqual(score[-1]["harmony"], ["C"])
        for ending in (score[74], score[-1]):
            final_chord = next(notes for notes in reversed(ending["grid"]) if notes)
            self.assertEqual({pitch_number(pitch) % 12 for pitch in final_chord}, {0, 4, 7})
            self.assertIn("C2", final_chord)

    def test_dawn_false_ending_is_followed_by_silence_and_compact_chord_drop(self):
        score = dawn.make_score()
        self.assertTrue(all(measure["section"] == "False dawn" for measure in score[68:75]))
        self.assertEqual(score[74]["harmony"], ["C"])
        self.assertEqual(score[75]["section"], "Silent breath")
        self.assertFalse(any(score[75]["grid"]))
        drop = score[76:100]
        self.assertTrue(all(measure["section"] == "Drop" for measure in drop))
        self.assertEqual(76 * 32 * 75, 182_400)
        last_false_attack = max((index * 32 + slot) * 75 for index, measure in enumerate(score[:76])
                                for slot, notes in enumerate(measure["grid"]) if notes)
        self.assertEqual(last_false_attack, 178_800)
        self.assertEqual(score[74]["holds_ms"][16], {pitch: 400 for pitch in score[74]["grid"][16]})
        self.assertEqual(182_400 - last_false_attack - 400, 3_200)
        sizes = [len(notes) for measure in drop for notes in measure["grid"] if notes]
        chord_sizes = [size for size in sizes if size > 1]
        self.assertGreaterEqual(len(chord_sizes), 250)
        self.assertTrue(3.5 < sum(chord_sizes) / len(chord_sizes) < 5)
        self.assertGreaterEqual(sum(size >= 6 for size in sizes), 25)
        self.assertEqual(max(sizes), 7)
        self.assertLessEqual(max(len(notes) for measure in score[76:] for notes in measure["grid"]), 7)
        self.assertGreaterEqual(len({measure["texture"] for measure in drop}), 6)
        self.assertLess(sum(len(notes) for measure in score[100:108] for notes in measure["grid"] if notes)
                        / sum(bool(notes) for measure in score[100:108] for notes in measure["grid"]), 3)

    def test_dawn_restoration_preserves_original_voices_and_all_chord_attacks(self):
        score = dawn.make_score()
        # This reference was recovered from the pre-regression composition,
        # not generated from the current composer. Compacting chord voicings
        # must never delete a phrase, accompaniment line or chord attack.
        reference = json.loads((Path(__file__).parent / "fixtures/dawn-phrase-reference.json")
                               .read_text(encoding="utf-8"))
        self.assertEqual(len(score), len(reference))
        for original, restored in zip(reference, score):
            with self.subTest(bar=restored["bar"]):
                self.assertEqual(restored["harmony"], original["harmony"])
                for voice, events in original["voices"].items():
                    self.assertEqual(restored["voices"][voice], events)
                self.assertEqual([event["slot"] for event in restored["voices"]["mass"]],
                                 original["chord_slots"])
                self.assertEqual([slot for slot, notes in enumerate(restored["grid"]) if notes],
                                 original["attack_slots"])
        # Preserve the added cadential answers, including the low final C.
        self.assertEqual({event["slot"]: event["pitches"] for event in score[74]["voices"]["lead"]},
                         {0: ["G5"], 4: ["C6"], 8: ["E6"], 12: ["D6"], 14: ["B5"], 16: ["C6"]})
        self.assertEqual({event["slot"]: event["pitches"] for event in score[124]["voices"]["lead"]},
                         {0: ["E6"], 4: ["D6"], 8: ["G5"], 12: ["B5"], 14: ["C6"], 16: ["C5"]})


if __name__ == "__main__":
    unittest.main()
