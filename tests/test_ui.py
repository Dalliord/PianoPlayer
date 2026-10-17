"""Optional Qt checks; AHK launches are mocked and no keyboard events are sent."""
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import time
import unittest
from unittest.mock import patch


@unittest.skipUnless(os.environ.get("RUN_QT_TESTS") == "1", "Set RUN_QT_TESTS=1 with PySide6 installed")
class UiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        from PySide6.QtWidgets import QApplication
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self):
        from app.main_window import MainWindow
        self.folder = TemporaryDirectory()
        self.launch_mock = patch("player.playback_controller.PlaybackController.launch_worker")
        self.launch_mock.start()
        self.window = MainWindow(Path(self.folder.name))
        self.window.show()
        self.window.controller.ready = True

    def wait_until(self, condition, timeout=4):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            self.application.processEvents()
            if condition():
                return
            time.sleep(0.01)
        self.fail("Qt condition did not become true")

    def valid_sheet(self):
        self.wait_until(lambda: self.window.plan is not None)

    def test_only_three_timing_fields_with_requested_ranges(self):
        from PySide6.QtWidgets import QSpinBox, QDoubleSpinBox
        self.assertEqual(len(self.window.findChildren(QSpinBox)), 2)
        self.assertEqual(len(self.window.findChildren(QDoubleSpinBox)), 1)
        self.assertEqual((self.window.note.minimum(), self.window.note.maximum(), self.window.note.value()), (20, 500, 300))
        self.assertEqual((self.window.hold.minimum(), self.window.hold.maximum(), self.window.hold.value()), (5, 200, 200))
        self.assertEqual((self.window.start.minimum(), self.window.start.maximum(), self.window.start.value()), (0, 10, 3))
        self.assertTrue(all(field.minimumHeight() >= 64 for field in (self.window.note, self.window.hold, self.window.start)))

    def test_piano_player_identity_and_removed_description_controls(self):
        self.valid_sheet()
        self.assertEqual(self.window.windowTitle(), "Piano Player")
        self.assertFalse(self.window.windowIcon().isNull())
        self.assertFalse(hasattr(self.window, "preset_info"))
        self.assertFalse(hasattr(self.window, "song_info"))
        self.assertFalse(hasattr(self.window, "practice_link"))
        self.assertEqual(self.window.song_selector.count(), 5)

    def test_native_languages_have_flags_and_switch_without_resetting_music(self):
        from app.i18n import LANGUAGES, tr
        from app.main_window import MainWindow
        self.window.editor.setPlainText("[asd]<1000> f g")
        self.window.note.setValue(250)
        self.valid_sheet()
        song_id = self.window.current_song.id
        for index, (code, name, _) in enumerate(LANGUAGES):
            with self.subTest(language=code):
                self.assertEqual(self.window.language_selector.itemText(index), name)
                self.assertFalse(self.window.language_selector.itemIcon(index).isNull())
                self.window.language_selector.setCurrentIndex(index)
                self.assertEqual(self.window.play.text(), tr(code, "play"))
                self.assertEqual(self.window.add_song_button.text(), tr(code, "new_song"))
                self.assertEqual(self.window.delete_song_button.toolTip(), tr(code, "delete_song"))
                self.assertEqual(self.window.undo_delete_button.toolTip(), tr(code, "undo_delete"))
                self.assertEqual(self.window.validation.text(), tr(code, "valid", count=len(self.window.plan.events)))
                self.assertEqual(self.window.editor.toPlainText(), "[asd]<1000> f g")
                self.assertEqual(self.window.note.value(), 250)
                self.assertEqual(self.window.current_song.id, song_id)
        self.window.close()
        self.window.deleteLater()
        self.application.processEvents()
        self.window = MainWindow(Path(self.folder.name))
        self.assertEqual(self.window.settings.language, "de")
        self.assertEqual(self.window.language_selector.currentText(), "Deutsch")
        self.assertEqual(self.window.play.text(), "Abspielen")

    def test_manual_song_dialog_validation_and_persistent_independent_song(self):
        from app.song_dialog import SongDialog
        from app.main_window import MainWindow
        from PySide6.QtWidgets import QDialog
        dialog = SongDialog(self.window.settings, self.window)
        dialog.accept()
        self.assertNotEqual(dialog.result(), QDialog.DialogCode.Accepted)
        dialog.title.setText("My own song")
        dialog.sheet.setPlainText("[abc")
        dialog.accept()
        self.assertNotEqual(dialog.result(), QDialog.DialogCode.Accepted)
        dialog.sheet.setPlainText("[asd]<1250> f g h")
        dialog.accept()
        self.assertEqual(dialog.result(), QDialog.DialogCode.Accepted)
        self.window.note.setValue(240)
        self.window._add_custom_song(dialog.title.text(), dialog.sheet.toPlainText())
        dialog.deleteLater()
        song_id = self.window.current_song.id
        self.assertTrue(self.window.current_song.custom)
        self.assertEqual(self.window.current_song.title, "My own song")
        self.assertEqual(self.window.note.value(), 240)
        self.valid_sheet()
        self.assertEqual(self.window.plan.events[0].hold_ms, 1250)
        self.window.close()
        self.window.deleteLater()
        self.application.processEvents()
        self.window = MainWindow(Path(self.folder.name))
        self.assertEqual(self.window.current_song.id, song_id)
        self.assertEqual(self.window.song_selector.count(), 6)
        self.assertEqual(self.window.editor.toPlainText(), "[asd]<1250> f g h")
        self.assertEqual(self.window.note.value(), 240)

    def test_midi_import_is_saved_as_a_new_song_and_restored_after_restart(self):
        from app.main_window import MainWindow
        from player.midi_import import convert_midi, read_midi
        from tests.test_midi_import import make_midi
        from PySide6.QtWidgets import QDialogButtonBox
        from app.midi_dialog import MidiImportDialog
        path = Path(self.folder.name) / "My song.mid"
        make_midi(path)
        dialog = MidiImportDialog(path, self.window)
        dialog.show()
        self.wait_until(lambda: dialog.result_score is not None)
        self.assertTrue(dialog.buttons.button(QDialogButtonBox.StandardButton.Ok).isEnabled())
        dialog.title.clear()
        self.assertFalse(dialog.buttons.button(QDialogButtonBox.StandardButton.Ok).isEnabled())
        dialog.title.setText("My song")
        self.assertTrue(dialog.buttons.button(QDialogButtonBox.StandardButton.Ok).isEnabled())
        self.assertEqual(dialog.result_score.source_notes, 3)
        # Changing the track selection must discard the previous preview.
        from PySide6.QtCore import Qt
        dialog.tracks.item(1).setCheckState(Qt.CheckState.Unchecked)
        self.assertIsNone(dialog.result_score)
        self.wait_until(lambda: dialog.result_score is not None)
        self.assertEqual(dialog.result_score.source_notes, 2)
        self.window._add_imported_song("My song", dialog.result_score)
        dialog.reject()
        dialog.deleteLater()
        song_id = self.window.current_song.id
        self.wait_until(lambda: self.window.plan is not None)
        self.assertTrue(self.window.current_song.imported)
        self.assertEqual(self.window.current_song.title, "My song")
        self.window.close()
        self.window.deleteLater()
        self.application.processEvents()
        self.window = MainWindow(Path(self.folder.name))
        self.window.controller.ready = True
        self.wait_until(lambda: self.window.plan is not None)
        self.assertEqual(self.window.current_song.id, song_id)
        self.assertEqual(self.window.current_song.title, "My song")
        with patch.object(self.window.controller, "_send"):
            self.window._play()
            self.assertFalse(self.window.import_midi_button.isEnabled())
            self.window.controller.stop()

    def test_tempo_commands_are_editable_and_keep_three_main_controls(self):
        self.window.editor.setPlainText("|bpm=120| |step=1/3| a b c |bpm=240| [sd]<1000.5>")
        self.wait_until(lambda: self.window.plan is not None)
        notes = [e for e in self.window.plan.events if e.keys]
        self.assertAlmostEqual(notes[1].offset_ms, 500/3)
        self.assertAlmostEqual(notes[-1].offset_ms, 500)
        self.assertEqual(notes[-1].hold_ms, 1000.5)

    def test_bundled_song_deletion_survives_restart(self):
        from app.main_window import MainWindow
        from player.song_library import load_song_library
        removed_id = self.window.current_song.id
        self.window.delete_song_button.click()
        self.assertEqual(self.window.song_selector.findData(removed_id), -1)
        self.assertEqual(self.window.song_selector.count(), 4)
        self.assertEqual(self.window.current_song.id, "mr-sandman")
        self.assertEqual(len(load_song_library()), 5)
        self.window.close()
        self.window.deleteLater()
        self.application.processEvents()
        self.window = MainWindow(Path(self.folder.name))
        self.assertEqual(self.window.song_selector.findData(removed_id), -1)
        self.assertEqual(self.window.song_selector.count(), 4)
        self.assertEqual(self.window.current_song.id, "mr-sandman")

    def test_undo_deletion_restores_song_position_edits_and_timing(self):
        self.window.song_selector.setCurrentIndex(2)
        original_ids = [song.id for song in self.window.songs]
        song_id = self.window.current_song.id
        self.window.editor.setPlainText("[asd]<1200> f g")
        self.window.note.setValue(240)
        self.window.hold.setValue(170)
        self.window.delete_song_button.click()
        self.assertTrue(self.window.undo_delete_button.isVisible())
        self.window.undo_delete_button.click()
        self.assertEqual([song.id for song in self.window.songs], original_ids)
        self.assertEqual(self.window.current_song.id, song_id)
        self.assertEqual(self.window.editor.toPlainText(), "[asd]<1200> f g")
        self.assertEqual((self.window.note.value(), self.window.hold.value()), (240, 170))
        self.assertNotIn(song_id, self.window.store.load().deleted_song_ids)
        self.assertTrue(self.window.undo_delete_button.isHidden())

    def test_manual_and_midi_songs_can_be_deleted_independently(self):
        from player.song_library import save_imported_song, load_song_library
        self.window._add_custom_song("Same title", "a b c")
        manual_id = self.window.current_song.id
        midi = save_imported_song(self.window.library_directory, "Same title", "[asd]<1000> f", "")
        self.window._append_song(midi)
        self.window.delete_song_button.click()
        self.assertNotEqual(self.window.song_selector.findData(manual_id), -1)
        self.assertEqual(self.window.song_selector.findData(midi.id), -1)
        self.window.song_selector.setCurrentIndex(self.window.song_selector.findData(manual_id))
        self.window.delete_song_button.click()
        saved = self.window.store.load()
        visible = load_song_library(self.window.library_directory, saved.deleted_song_ids)
        self.assertEqual(len(visible), 5)
        self.assertFalse({manual_id, midi.id} & {song.id for song in visible})

    def test_empty_library_survives_pending_parse_and_restart_and_accepts_new_songs(self):
        from app.main_window import MainWindow
        self.window._parse()
        while self.window.songs:
            self.window.delete_song_button.click()
        self.wait_until(lambda: not self.window.parse_running)
        self.assertIsNone(self.window.current_song)
        self.assertIsNone(self.window.plan)
        self.assertEqual(self.window.editor.toPlainText(), "")
        self.assertEqual(self.window.validation.text(), self.window.t("library_empty"))
        self.assertFalse(self.window.play.isEnabled())
        self.assertFalse(self.window.delete_song_button.isEnabled())
        self.assertFalse(self.window.note.isEnabled())
        self.assertTrue(self.window.add_song_button.isEnabled())
        self.window.close()
        self.window.deleteLater()
        self.application.processEvents()
        self.window = MainWindow(Path(self.folder.name))
        self.assertIsNone(self.window.current_song)
        self.assertEqual(self.window.song_selector.count(), 0)
        self.window._add_custom_song("Fresh start", "a b [sd]<1000>")
        self.valid_sheet()
        self.assertEqual(self.window.current_song.title, "Fresh start")
        self.assertFalse(self.window.editor.isReadOnly())
        self.assertTrue(self.window.delete_song_button.isEnabled())
        self.assertEqual(self.window.song_selector.count(), 1)

    def test_failed_deletion_write_leaves_library_unchanged(self):
        songs = self.window.songs
        selected = self.window.current_song
        with patch.object(self.window.store, "save", side_effect=OSError("Disk unavailable")), self.assertLogs(level="ERROR"):
            self.window.delete_song_button.click()
        self.assertEqual(self.window.songs, songs)
        self.assertEqual(self.window.current_song, selected)
        self.assertEqual(self.window.settings.deleted_song_ids, [])
        self.assertIn("Disk unavailable", self.window.status.text())

    def test_delete_and_undo_are_blocked_during_countdown_playback_and_pause(self):
        self.window.delete_song_button.click()
        self.valid_sheet()
        with patch.object(self.window.controller, "_send"):
            self.window._play()
            song_ids = [song.id for song in self.window.songs]
            for state in ("COUNTDOWN", "PLAYING", "PAUSED"):
                self.window.controller._set_state(state, state)
                self.assertFalse(self.window.delete_song_button.isEnabled())
                self.assertFalse(self.window.undo_delete_button.isEnabled())
                self.window._delete_song()
                self.window._undo_delete()
                self.assertEqual([song.id for song in self.window.songs], song_ids)
            self.window.controller.stop()
        self.assertTrue(self.window.delete_song_button.isEnabled())
        self.assertTrue(self.window.undo_delete_button.isEnabled())

    def test_invalid_sheet_disables_play_and_highlights(self):
        self.window.editor.setPlainText("abc[def")
        self.wait_until(lambda: "Ошибка" in self.window.validation.text())
        self.assertFalse(self.window.play.isEnabled())
        self.assertEqual(len(self.window.editor.extraSelections()), 1)

    def test_bundled_song_selected_and_sheet_can_be_edited(self):
        from PySide6.QtTest import QTest
        from PySide6.QtWidgets import QPushButton
        self.valid_sheet()
        self.assertEqual(self.window.song_selector.count(), len(self.window.songs))
        self.assertEqual(self.window.song_selector.currentText(), "BEASTARS -pf solo-")
        self.assertFalse(self.window.song_selector.isEditable())
        self.assertFalse(self.window.editor.isReadOnly())
        self.assertTrue(self.window.editor.acceptDrops())
        self.window.editor.selectAll()
        self.window.editor.setFocus()
        QTest.keyClicks(self.window.editor, "[asd]-{asdf}")
        self.wait_until(lambda: self.window.plan is not None and len(self.window.plan.events) == 6)
        self.assertEqual(self.window.editor.toPlainText(), "[asd]-{asdf}")
        labels = {button.text() for button in self.window.findChildren(QPushButton)}
        self.assertTrue({"Открыть…", "Сохранить…", "Оригинал"} <= labels)

    def test_song_selection_keeps_user_settings_and_preset_button_resets(self):
        self.valid_sheet()
        self.window.note.setValue(250)
        self.window.hold.setValue(100)
        self.window.start.setValue(5)
        self.window._select_song(0)
        self.wait_until(lambda: self.window.plan is not None)
        self.assertEqual((self.window.note.value(), self.window.hold.value(), self.window.start.value()), (250, 100, 5))
        self.window._reset_timing()
        self.wait_until(lambda: self.window.plan is not None)
        self.assertEqual((self.window.note.value(), self.window.hold.value(), self.window.start.value()), (300, 200, 3.0))
        self.assertEqual(self.window.settings.selected_song_id, "beastars-pf-solo")

    def test_edits_and_timing_survive_application_restart(self):
        from app.main_window import MainWindow
        self.window.editor.setPlainText("a-[dEuw]-{asdf}")
        self.window.note.setValue(350)
        self.window.hold.setValue(150)
        self.window.humanize.setChecked(False)
        self.window.close()
        self.window.deleteLater()
        self.application.processEvents()
        self.window = MainWindow(Path(self.folder.name))
        self.window.controller.ready = True
        self.wait_until(lambda: self.window.plan is not None)
        self.assertEqual(self.window.editor.toPlainText(), "a-[dEuw]-{asdf}")
        self.assertEqual((self.window.note.value(), self.window.hold.value()), (350, 150))
        self.assertFalse(self.window.humanize.isChecked())
        self.window._restore_sheet()
        self.assertEqual(self.window.editor.toPlainText(), self.window.current_song.sheet)
        self.assertNotIn(self.window.current_song.id, self.window.settings.sheet_overrides)

    def test_explicit_sustain_is_editable_saved_and_exported_with_three_controls(self):
        source = "[asd]<1500> f g h"
        self.window.note.setValue(100)
        self.window.start.setValue(0)
        self.window.editor.setPlainText(source)
        self.wait_until(lambda: self.window.plan is not None
                        and self.window.plan.events[0].hold_ms == 1500)
        self.assertEqual(self.window.plan.duration_ms, 1500)
        self.assertEqual([event.offset_ms for event in self.window.plan.events], [0, 100, 200, 300])
        song_id = self.window.current_song.id
        controller = self.window.controller
        with patch.object(controller, "_send"):
            self.window._play()
            self.assertTrue(any(event.hold_ms == 1500 for event in controller.plan.events))
            path = Path(controller._temporary.name) / "plan.tsv"
            self.assertEqual(path.read_text().splitlines()[0].split("\t")[1], "3")
            controller.stop()
        self.window.close()
        from app.main_window import MainWindow
        self.window = MainWindow(Path(self.folder.name))
        self.assertEqual(self.window.settings.sheet_overrides[song_id], source)
        self.assertEqual(self.window.editor.toPlainText(), source)

    def test_humanize_toggle_changes_only_next_performance_and_freezes_on_pause(self):
        self.window.start.setValue(0)
        self.window.humanize.setChecked(False)
        self.valid_sheet()
        controller = self.window.controller
        with patch.object(controller, "_send"):
            self.window._play()
            self.assertIs(controller.plan, self.window.plan)
            path = Path(controller._temporary.name) / "plan.tsv"
            self.assertEqual(path.read_text(encoding="utf-8").splitlines()[0].split("\t")[1], "1")
            controller.stop()
            self.window.humanize.setChecked(True)
            self.window._play()
            performance = controller.plan
            self.assertIsNot(performance, self.window.plan)
            self.assertEqual(performance.duration_ms, self.window.plan.duration_ms)
            self.assertTrue(any(event.hold_ms is not None for event in performance.events))
            self.assertFalse(self.window.humanize.isEnabled())
            path = Path(controller._temporary.name) / "plan.tsv"
            self.assertEqual(path.read_text(encoding="utf-8").splitlines()[0].split("\t")[1], "2")
            controller._handle_message(["STATE", "PAUSED"])
            self.window._play()
            self.assertIs(controller.plan, performance)
            controller.stop()
            self.assertTrue(self.window.humanize.isEnabled())

    def test_song_switching_keeps_separate_sheets_and_settings(self):
        self.valid_sheet()
        self.window.editor.setPlainText("[asd]-a")
        self.window.note.setValue(350)
        self.window.hold.setValue(150)
        sandman_index = self.window.song_selector.findData("mr-sandman")
        beastars_index = self.window.song_selector.findData("beastars-pf-solo")
        self.window.song_selector.setCurrentIndex(sandman_index)
        self.wait_until(lambda: self.window.plan is not None)
        self.assertEqual(self.window.current_song.title, "Mr. Sandman")
        self.assertEqual(len(self.window.plan.events), 501)
        self.assertEqual((self.window.note.value(), self.window.hold.value()), (300, 200))
        self.window.editor.setPlainText("[ejTu]S")
        self.window.note.setValue(280)
        self.window.hold.setValue(180)
        self.window.song_selector.setCurrentIndex(beastars_index)
        self.wait_until(lambda: self.window.plan is not None)
        self.assertEqual(self.window.editor.toPlainText(), "[asd]-a")
        self.assertEqual((self.window.note.value(), self.window.hold.value()), (350, 150))
        self.window.song_selector.setCurrentIndex(sandman_index)
        self.wait_until(lambda: self.window.plan is not None)
        self.assertEqual(self.window.editor.toPlainText(), "[ejTu]S")
        self.assertEqual((self.window.note.value(), self.window.hold.value()), (280, 180))
        self.window._reset_timing()
        self.assertEqual((self.window.note.value(), self.window.hold.value()), (300, 200))
        self.assertEqual(self.window.settings.song_timings["beastars-pf-solo"]["note_delay_ms"], 350)

    def test_no_roblox_focus_controls_in_advanced(self):
        from app.main_window import AdvancedDialog
        from PySide6.QtWidgets import QCheckBox
        dialog = AdvancedDialog(self.window.settings, self.window)
        self.assertEqual(dialog.findChildren(QCheckBox), [])
        self.assertFalse(hasattr(dialog, "processes"))
        dialog.deleteLater()

    def test_all_five_songs_load_without_descriptions(self):
        for index, song in enumerate(self.window.songs):
            with self.subTest(song=song.id):
                self.window.song_selector.setCurrentIndex(index)
                self.valid_sheet()
                self.assertEqual(self.window.current_song.id, song.id)
                self.assertEqual(self.window.editor.toPlainText(), song.sheet)
                self.assertEqual(self.window.song_selector.itemText(index), song.title)

    def test_dawn_keeps_its_five_minute_preset(self):
        self.window.song_selector.setCurrentIndex(self.window.song_selector.findData("wolf-last-dawn"))
        self.valid_sheet()
        self.assertEqual(self.window.current_song.title, "Until We Reach the Dawn")
        self.assertEqual((self.window.note.value(), self.window.hold.value(), self.window.start.value()), (75, 150, 3))
        self.assertEqual(self.window.plan.duration_ms, 300_000)

    def test_wild_side_has_reference_credit_and_loads_individual_note_holds(self):
        self.window.song_selector.setCurrentIndex(self.window.song_selector.findData("wild-side-piano"))
        self.wait_until(lambda: self.window.plan is not None)
        self.assertEqual(self.window.current_song.title, "Wild Side — Piano")
        self.assertEqual((self.window.note.value(), self.window.hold.value(), self.window.start.value()), (20, 100, 3))
        self.assertEqual(self.window.plan.duration_ms, 90_000)
        self.window.editor.setPlainText("[a<1000>s<200>d<500>] f")
        self.wait_until(lambda: self.window.plan is not None and self.window.plan.duration_ms == 1000)
        self.assertEqual([e.offset_ms for e in self.window.plan.events[:3]], [0, 0, 0])

    def test_countdown_stop_and_no_late_start(self):
        self.valid_sheet()
        with patch.object(self.window.controller, "_send") as send:
            self.window._play()
            self.assertEqual(self.window.status.text(), "Начало через 3…")
            self.assertTrue(self.window.stop.isEnabled())
            self.assertFalse(self.window.song_selector.isEnabled())
            self.window.controller.stop()
            self.window.controller._deadline = time.monotonic() - 1
            self.window.controller._countdown()
            self.assertFalse(self.window.controller.timer.isActive())
            self.assertFalse(any(call.args[0].startswith("PLAY") for call in send.call_args_list))
            self.assertEqual(self.window.controller.state, "STOPPED")
            self.assertTrue(self.window.song_selector.isEnabled())
            self.assertFalse(self.window.editor.isReadOnly())
            self.assertFalse(list((Path(self.folder.name) / "data/sessions").glob("*/plan.tsv")))

    def test_zero_delay_and_session_snapshot(self):
        self.window.start.setValue(0)
        self.valid_sheet()
        with patch.object(self.window.controller, "_send") as send:
            self.window._play()
            self.assertEqual(self.window.controller.state, "PLAYING")
            self.assertTrue(send.call_args.args[0].startswith("PLAY\t"))
            active_plan = self.window.controller.plan
            self.window.note.setValue(400)
            self.wait_until(lambda: self.window.plan is not None)
            self.assertIs(self.window.controller.plan, active_plan)
            self.assertGreater(self.window.plan.duration_ms, active_plan.duration_ms)

    def test_countdown_whole_seconds(self):
        self.valid_sheet()
        controller = self.window.controller
        controller.play(self.window.plan)
        for remaining, text in [(2.5, "Начало через 3…"), (1.5, "Начало через 2…"), (0.5, "Начало через 1…")]:
            controller._deadline = time.monotonic() + remaining
            controller._countdown()
            self.assertEqual(self.window.status.text(), text)
        controller.stop()

    def tearDown(self):
        self.window.close()
        self.application.processEvents()
        self.window.deleteLater()
        self.application.processEvents()
        self.launch_mock.stop()
        self.folder.cleanup()


if __name__ == "__main__":
    unittest.main()
