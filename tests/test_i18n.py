from pathlib import Path
from tempfile import TemporaryDirectory
from string import Formatter
import unittest

from app.i18n import LANGUAGES, TRANSLATIONS, tr, notation_text, error_text
from app.settings import SettingsStore


class TranslationTests(unittest.TestCase):
    def test_all_languages_have_matching_keys_and_format_arguments(self):
        self.assertEqual({code for code, _, _ in LANGUAGES}, {"ru", "en", "es", "pt", "ja", "ko", "zh", "fr", "de"})
        base = TRANSLATIONS["ru"]
        fields = lambda text: {field for _, field, _, _ in Formatter().parse(text) if field}
        for code, messages in TRANSLATIONS.items():
            self.assertEqual(set(messages), set(base))
            for key, message in messages.items():
                with self.subTest(language=code, key=key):
                    self.assertTrue(message.strip())
                    self.assertEqual(fields(message), fields(base[key]))
                    tr(code, key, **{field: 1 for field in fields(message)})
            self.assertIn("|ramp=180,8|", notation_text(code))
            if code != "ru":
                self.assertNotIn("скобка", error_text(code, "Не закрыта скобка [."))

    def test_language_roundtrip_and_invalid_locale_preserve_other_settings(self):
        import json
        with TemporaryDirectory() as folder:
            store = SettingsStore(Path(folder) / "settings.json")
            settings = store.load()
            settings.language = "ja"
            store.save(settings)
            self.assertEqual(store.load().language, "ja")
            for language in ["unknown", [], None]:
                store.path.write_text(json.dumps({"language": language, "sheet_overrides": {"song": "abc"}}), encoding="utf-8")
                loaded = store.load()
                self.assertEqual(loaded.language, "ru")
                self.assertEqual(loaded.sheet_overrides, {"song": "abc"})
