"""Check the 32nd-note export grid and the exact-duration release boundary."""
from dataclasses import replace
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import wave


@unittest.skipUnless(importlib.util.find_spec("numpy"), "Optional media renderer needs numpy")
class SymphonicMediaTests(unittest.TestCase):
    def test_exact_duration_export_removes_only_silence(self):
        from tools.render_song import Note
        from tools.render_wolf_last_dawn import write_exact_wav

        with TemporaryDirectory(prefix="symphonic-audio-") as directory:
            audio = Path(directory) / "fixture.wav"
            peak, rms = write_exact_wav(audio, [Note(60, 0, 150)], 1200, 8000)
            with wave.open(str(audio), "rb") as reader:
                self.assertEqual((reader.getnchannels(), reader.getsampwidth(),
                                  reader.getframerate(), reader.getnframes()), (1, 2, 8000, 9600))
                reader.setpos(8000)
                self.assertFalse(any(reader.readframes(1600)))
            self.assertTrue(0 < rms < peak < 1)
            with self.assertRaisesRegex(ValueError, "more final silence"):
                write_exact_wav(audio, [Note(60, 0, 150)], 200, 8000)

    def test_midi_32nd_note_grid_has_100_bpm_and_exact_five_minute_end(self):
        from player.song_library import load_song_library
        from tools.render_song import Note, write_midi

        song = replace(load_song_library()[0], title="32nd-note fixture", note_delay_ms=75)
        with TemporaryDirectory(prefix="symphonic-midi-") as directory:
            path = Path(directory) / "fixture.mid"
            write_midi(path, song, [Note(60, 75, 225)], 300_000, notes_per_beat=8)
            data = path.read_bytes()
        cursor, tick = 22, 0
        metas = {}
        notes = []

        def read_variable():
            nonlocal cursor
            value = 0
            while True:
                byte = data[cursor]
                cursor += 1
                value = value * 128 + (byte & 127)
                if byte < 128:
                    return value

        while cursor < len(data):
            tick += read_variable()
            status = data[cursor]
            cursor += 1
            if status == 0xff:
                kind = data[cursor]
                cursor += 1
                size = read_variable()
                metas[kind] = (tick, data[cursor:cursor + size])
                cursor += size
            elif status == 0xc0:
                cursor += 1
            else:
                self.assertIn(status, (0x80, 0x90))
                notes.append((tick, status, data[cursor]))
                cursor += 2
        self.assertEqual(metas[0x51], (0, (600_000).to_bytes(3, "big")))
        self.assertEqual(metas[0x2f], (4_800_000, b""))
        self.assertEqual(notes, [(1200, 0x90, 60), (3600, 0x80, 60)])


if __name__ == "__main__":
    unittest.main()
