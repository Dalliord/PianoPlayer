import unittest

from player.parser import SheetParser
from player.plan_writer import build_plan
from player.song_library import load_song_library
from tests.library_archive import load_historical_library


class SongLibraryTests(unittest.TestCase):
    def test_excluded_songs_can_leave_an_empty_library_without_changing_the_catalog(self):
        songs = load_song_library()
        self.assertEqual(load_song_library(excluded_ids=[song.id for song in songs]), ())
        self.assertEqual(load_song_library(), songs)

    def test_active_catalog_contains_only_the_requested_five_songs(self):
        songs = load_song_library()
        self.assertEqual({song.id for song in songs},
                         {"beastars-pf-solo", "mr-sandman", "wolf-last-dawn", "wild-side-piano", "rush-e"})
        self.assertEqual(len(songs), 5)

    def test_selected_song_has_complete_bundled_sheet_and_preset(self):
        songs = load_song_library()
        self.assertTrue({"beastars-pf-solo", "mr-sandman"}.issubset({song.id for song in songs}))
        song = next(song for song in songs if song.id == "beastars-pf-solo")
        self.assertEqual(song.id, "beastars-pf-solo")
        self.assertEqual(song.title, "BEASTARS -pf solo-")
        self.assertTrue(song.sheet.startswith("f g h"))
        self.assertTrue(" ".join(song.sheet.split()).endswith("[69Qy] q"))
        self.assertGreater(len(song.sheet), 700)
        self.assertEqual((song.note_delay_ms, song.key_hold_ms, song.start_delay_s), (300, 200, 3.0))
        self.assertIn("проверке пользователя", song.timing_basis)
        self.assertEqual(song.practice_url, "https://playpianosheets.com/practice-online/beastars-pf-solo")

    def test_mr_sandman_is_complete_and_uses_source_timing(self):
        song = next(song for song in load_song_library() if song.id == "mr-sandman")
        self.assertEqual((song.title, song.artist, song.difficulty), ("Mr. Sandman", "The Chordettes", "Hard"))
        self.assertTrue(song.sheet.startswith("p S f H G f S p a d"))
        self.assertTrue(" ".join(song.sheet.split()).endswith("[0eG] [6j] [6]"))
        self.assertGreater(len(song.sheet), 2500)
        plan = build_plan(SheetParser().parse(song.sheet), song.note_delay_ms, song.key_hold_ms)
        self.assertEqual(len(plan.events), 501)
        self.assertEqual(plan.duration_ms, 150_300)
        self.assertEqual((song.note_delay_ms, song.key_hold_ms, song.start_delay_s), (300, 200, 3.0))
        self.assertIn("ещё не проверена", song.timing_basis)
        self.assertEqual(song.practice_url, "https://playpianosheets.com/practice-online/mr-sandman")

    def test_all_bundled_songs_parse_and_build_a_playable_plan(self):
        for song in load_song_library():
            with self.subTest(song=song.id):
                plan = build_plan(SheetParser().parse(song.sheet), song.note_delay_ms, song.key_hold_ms)
                self.assertGreater(len(plan.events), 100)
                self.assertGreater(plan.duration_ms, 10_000)

    def test_ten_song_batch_has_complete_plans(self):
        expected = {
            "river-flows-in-you": 601, "fur-elise": 795, "interstellar": 1315,
            "fallen-down": 288, "golden-hour": 558, "minecraft-sweden": 166,
            "another-love": 856, "pirates-of-the-caribbean": 177,
            "experience-ludovico-einaudi": 1626, "unravel": 355,
        }
        songs = {song.id: song for song in load_historical_library()}
        self.assertGreaterEqual(len(songs), 12)
        for song_id, events in expected.items():
            with self.subTest(song=song_id):
                song = songs[song_id]
                plan = build_plan(SheetParser().parse(song.sheet), song.note_delay_ms, song.key_hold_ms)
                self.assertEqual(len(plan.events), events)
                self.assertEqual(song.source_url, f"https://playpianosheets.com/sheets/{song_id}")
                self.assertEqual(song.practice_url, f"https://playpianosheets.com/practice-online/{song_id}")
                self.assertTrue(all(character.isascii() for character in song.sheet))
        self.assertEqual(songs["golden-hour"].practice_transpose, 4)

    def test_rich_arrangements_have_chordal_accompaniment(self):
        songs = {song.id: song for song in load_historical_library()}
        expected = {"pirates-of-the-caribbean-hard": 429, "the-entertainer": 972, "la-vie-en-rose": 242}
        for song_id, event_count in expected.items():
            with self.subTest(song=song_id):
                song = songs[song_id]
                parsed = SheetParser().parse(song.sheet)
                plan = build_plan(parsed, song.note_delay_ms, song.key_hold_ms)
                sounding = [event for event in parsed.events if event.keys]
                chords = [event for event in sounding if len(set(event.keys)) > 1]
                self.assertEqual(song.difficulty, "Hard")
                self.assertEqual(len(plan.events), event_count)
                self.assertGreaterEqual(len(chords) / len(sounding), 0.55)
                self.assertGreaterEqual(sum(len(set(event.keys)) for event in sounding) / len(sounding), 2.3)
        self.assertEqual(songs["pirates-of-the-caribbean"].difficulty, "Easy")
        self.assertNotEqual(songs["pirates-of-the-caribbean"].sheet, songs["pirates-of-the-caribbean-hard"].sheet)
