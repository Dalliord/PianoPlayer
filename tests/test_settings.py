import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from app.settings import Settings, SettingsStore


class SettingsTests(unittest.TestCase):
    def test_deleted_song_ids_are_persistent_and_invalid_values_are_ignored(self):
        with TemporaryDirectory() as folder:
            store = SettingsStore(Path(folder) / "settings.json")
            store.path.write_text(json.dumps({"deleted_song_ids": ["rush-e", 5, None, "", "rush-e", "mr-sandman", "a\nb"]}))
            settings = store.load()
            self.assertEqual(settings.deleted_song_ids, ["rush-e", "mr-sandman"])
            self.assertEqual(store.load(), settings)
            store.path.write_text('{"deleted_song_ids": "rush-e", "note_delay_ms": 250}')
            settings = store.load()
            self.assertEqual(settings.deleted_song_ids, [])
            self.assertEqual(settings.note_delay_ms, 250)

    def test_defaults_and_roundtrip(self):
        with TemporaryDirectory() as folder:
            store = SettingsStore(Path(folder) / "settings.json")
            settings = store.load()
            self.assertTrue(settings.humanize)
            self.assertEqual((settings.note_delay_ms, settings.key_hold_ms, settings.start_delay_s), (100, 35, 3.0))
            settings.note_delay_ms = 222
            settings.key_hold_ms = 200
            settings.start_delay_s = 0.0
            settings.humanize = False
            store.save(settings)
            self.assertEqual(store.load(), settings)

    def test_corrupt_settings_repaired(self):
        for data in ("invalid", "[]", "null", '{"note_delay_ms": "bad", "start_delay_s": null}'):
            with self.subTest(data=data), TemporaryDirectory() as folder:
                path = Path(folder) / "settings.json"
                path.write_text(data)
                self.assertEqual(SettingsStore(path).load(), Settings())
                self.assertIsInstance(json.loads(path.read_text()), dict)

    def test_ranges_and_nonfinite_numbers(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "settings.json"
            path.write_text('{"note_delay_ms": 999, "key_hold_ms": 1, "start_delay_s": NaN}')
            settings = SettingsStore(path).load()
            self.assertEqual((settings.note_delay_ms, settings.key_hold_ms, settings.start_delay_s), (500, 5, 3.0))

    def test_old_extra_timing_fields_removed(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "settings.json"
            path.write_text('{"base_interval_ms": 150, "speed": 2, "chord_hold_ms": 80, "pause_duration": 200}')
            self.assertEqual(SettingsStore(path).load().note_delay_ms, 150)
            data = json.loads(path.read_text())
            self.assertFalse({"base_interval_ms", "speed", "chord_hold_ms", "pause_duration"} & data.keys())

    def test_old_roblox_restrictions_cannot_be_restored(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "settings.json"
            path.write_text('{"require_roblox_focus": true, "pause_when_focus_lost": true, "allowed_processes": ["RobloxPlayerBeta.exe"]}')
            settings = SettingsStore(path).load()
            self.assertEqual(settings.selected_song_id, "beastars-pf-solo")
            data = json.loads(path.read_text())
            self.assertFalse({"require_roblox_focus", "pause_when_focus_lost", "allowed_processes"} & data.keys())

    def test_song_overrides_roundtrip_and_invalid_values(self):
        with TemporaryDirectory() as folder:
            store = SettingsStore(Path(folder) / "settings.json")
            settings = Settings(song_timings={"beastars-pf-solo": {"note_delay_ms": 300, "key_hold_ms": 200, "start_delay_s": 3.0}},
                                sheet_overrides={"beastars-pf-solo": "[ejTu] S [dEuw]"})
            store.save(settings)
            self.assertEqual(store.load(), settings)
            store.path.write_text('{"song_timings": {"song": {"note_delay_ms": 900, "key_hold_ms": 0, "start_delay_s": NaN}, "bad": null}, "sheet_overrides": {"good": "abc", "bad": 7}}')
            loaded = store.load()
            self.assertEqual(loaded.song_timings["song"], {"note_delay_ms": 500, "key_hold_ms": 5, "start_delay_s": 3.0})
            self.assertEqual(loaded.sheet_overrides, {"good": "abc"})


if __name__ == "__main__":
    unittest.main()
