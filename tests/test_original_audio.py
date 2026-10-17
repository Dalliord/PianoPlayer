"""Check offline media against the keyboard/hold contract without audio devices."""
from dataclasses import replace
import importlib.util
from pathlib import Path
import struct
from tempfile import TemporaryDirectory
import unittest
import wave


@unittest.skipUnless(importlib.util.find_spec("numpy"), "Optional media renderer needs numpy")
class OriginalAudioTests(unittest.TestCase):
    def test_renderer_pitch_map_agrees_with_written_composition(self):
        from tools.compose_moonlit_platform import PITCH_TO_KEY, pitch_number
        from tools.render_song import KEY_TO_MIDI

        self.assertEqual(len(PITCH_TO_KEY), len(KEY_TO_MIDI))
        for pitch, key in PITCH_TO_KEY.items():
            with self.subTest(pitch=pitch, key=key):
                self.assertEqual(KEY_TO_MIDI[key], pitch_number(pitch))
        self.assertEqual(KEY_TO_MIDI["1"], 36)
        self.assertEqual(KEY_TO_MIDI["t"], 60)
        self.assertEqual(KEY_TO_MIDI["p"], 69)

    def test_media_preserves_same_physical_key_retriggers_and_valid_pcm(self):
        import numpy as np
        from player.song_library import load_song_library
        from tools.render_song import collect_notes, write_midi, write_wav

        song = replace(load_song_library()[0], title="Media fixture", sheet="[1tp] p P p --",
                       note_delay_ms=150, key_hold_ms=200)
        notes, duration = collect_notes(song)
        self.assertEqual([(n.pitch, n.start_ms, n.end_ms) for n in notes], [
            (36, 0, 200), (60, 0, 200), (69, 0, 150),
            (69, 150, 300), (70, 300, 450), (69, 450, 650),
        ])
        self.assertEqual(duration, 900)
        with TemporaryDirectory(prefix="original-audio-") as directory:
            midi = Path(directory) / "fixture.mid"
            audio = Path(directory) / "fixture.wav"
            write_midi(midi, song, notes, duration)
            write_wav(audio, notes, duration)
            data = midi.read_bytes()
            self.assertEqual(data[:4], b"MThd")
            self.assertEqual(struct.unpack(">IHHH", data[4:14]), (6, 0, 1, 9600))
            self.assertEqual(data[14:18], b"MTrk")
            self.assertEqual(struct.unpack(">I", data[18:22])[0], len(data) - 22)

            # Read Standard MIDI events independently rather than reusing the
            # writer's encoder, and check note-off ordering at a retrigger.
            cursor, tick = 22, 0
            note_events = []
            meta = {}

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
                    meta[kind] = (tick, data[cursor:cursor + size])
                    cursor += size
                elif status == 0xc0:
                    self.assertEqual(data[cursor], 0)  # GM acoustic grand.
                    cursor += 1
                else:
                    self.assertIn(status, (0x80, 0x90))
                    pitch, velocity = data[cursor:cursor + 2]
                    cursor += 2
                    note_events.append((tick, status, pitch))
                    self.assertEqual(velocity, 88 if status == 0x90 else 0)
            self.assertEqual(meta[0x51][1], (600000).to_bytes(3, "big"))
            self.assertEqual(meta[0x2f], (14400, b""))
            self.assertEqual(note_events, [
                (0, 0x90, 36), (0, 0x90, 60), (0, 0x90, 69),
                (2400, 0x80, 69), (2400, 0x90, 69),
                (3200, 0x80, 36), (3200, 0x80, 60),
                (4800, 0x80, 69), (4800, 0x90, 70),
                (7200, 0x80, 70), (7200, 0x90, 69), (10400, 0x80, 69),
            ])
            with wave.open(str(audio)) as reader:
                self.assertEqual((reader.getnchannels(), reader.getsampwidth(),
                                  reader.getframerate(), reader.getnframes()), (1, 2, 24000, 39600))
                pcm = np.frombuffer(reader.readframes(reader.getnframes()), dtype="<i2")
            peak = int(np.max(np.abs(pcm)))
            self.assertGreater(peak, 20000)
            self.assertLess(peak, 30000)
            self.assertGreater(float(np.sqrt(np.mean(pcm.astype(np.float64) ** 2))), 100)
            self.assertTrue(np.all(pcm[-4800:] == 0))


if __name__ == "__main__":
    unittest.main()
