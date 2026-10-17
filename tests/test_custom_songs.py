from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from player.song_library import load_song_library, save_custom_song


class CustomSongTests(unittest.TestCase):
    def test_named_sheets_persist_independently_even_with_identical_titles(self):
        with TemporaryDirectory() as folder:
            path = Path(folder)
            first = save_custom_song(path, "  My   song  ", "[asd]<1000> f", 300, 200, 2.5)
            second = save_custom_song(path, "My song", "a b c", 100, 35, 3)
            songs = {song.id: song for song in load_song_library(path)}
            self.assertNotEqual(first.id, second.id)
            self.assertEqual(first.title, "My song")
            self.assertEqual(songs[first.id], first)
            self.assertEqual(songs[second.id], second)
            self.assertEqual((first.note_delay_ms, first.key_hold_ms, first.start_delay_s), (300, 200, 2.5))

    def test_invalid_name_sheet_or_timing_never_creates_a_file(self):
        with TemporaryDirectory() as folder:
            path = Path(folder)
            for name, sheet, delay in [(" ", "a", 100), ("Title", "[abc", 100),
                                       ("Title", "---", 100), ("Title", "abc", 501)]:
                with self.subTest(name=name, sheet=sheet), self.assertRaises(ValueError):
                    save_custom_song(path, name, sheet, delay)
            self.assertEqual(list(path.iterdir()), [])
