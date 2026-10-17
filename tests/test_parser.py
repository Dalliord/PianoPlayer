import unittest
from player.models import EventKind
from player.parser import SheetParser, SheetSyntaxError


class ParserTests(unittest.TestCase):
    def setUp(self):
        self.parser = SheetParser()

    def test_notes_preserve_case_and_shift_characters(self):
        source = "aAZ09!@#$%^&*()=;,./"
        sheet = self.parser.parse(source)
        self.assertEqual([event.keys[0] for event in sheet.events], list(map(ord, source)))
        self.assertTrue(all(event.kind == EventKind.NOTE for event in sheet.events))

    def test_chord_and_fast_sequence(self):
        sheet = self.parser.parse("[aSd]{asdf}")
        self.assertEqual(sheet.events[0].kind, EventKind.CHORD)
        self.assertEqual(sheet.events[0].keys, tuple(map(ord, "aSd")))
        self.assertEqual(sheet.events[1].kind, EventKind.FAST_SEQUENCE)
        self.assertEqual((sheet.events[1].source_start, sheet.events[1].source_end), (5, 11))

    def test_pauses_count_units(self):
        for count in (1, 2, 3, 30):
            with self.subTest(count=count):
                event = self.parser.parse("-" * count).events[0]
                self.assertEqual(event.pause_count, count)
                self.assertEqual(event.kind, EventKind.PAUSE)

    def test_real_sheets_with_group_hyphens(self):
        sheet = self.parser.parse("[f-8][d-e]{a-b}--")
        self.assertEqual(sheet.events[0].keys, tuple(map(ord, "f-8")))
        self.assertEqual(sheet.events[1].keys, tuple(map(ord, "d-e")))
        self.assertEqual(sheet.events[2].keys, tuple(map(ord, "a-b")))
        self.assertEqual(sheet.events[3].pause_count, 2)

    def test_whitespace_and_source_ranges(self):
        sheet = self.parser.parse(" \na\t [ipf]--{asdf}\r\n")
        self.assertEqual([event.kind for event in sheet.events],
                         [EventKind.NOTE, EventKind.CHORD, EventKind.PAUSE, EventKind.FAST_SEQUENCE])
        for event in sheet.events:
            self.assertTrue(sheet.source[event.source_start:event.source_end])

    def test_malformed_groups(self):
        for source in ("[abc", "{abc", "abc]", "abc}", "[]", "{}", "[ ]", "{\n}", "[a{b}]", "{a]}", "[a}"):
            with self.subTest(source=source), self.assertRaises(SheetSyntaxError):
                self.parser.parse(source)

    def test_error_position(self):
        with self.assertRaises(SheetSyntaxError) as error:
            self.parser.parse("abc[def")
        self.assertEqual((error.exception.start, error.exception.end), (3, 7))

    def test_unsupported_unicode(self):
        with self.assertRaises(SheetSyntaxError):
            self.parser.parse("abcЖ")

    def test_long_sheet(self):
        source = "[ipf]--{asdf}\na " * 8000
        self.assertGreater(len(source), 100_000)
        self.assertEqual(len(self.parser.parse(source).events), 32_000)


if __name__ == "__main__":
    unittest.main()
