"""PySide6 UI; parsing is delegated to a background worker."""
from copy import deepcopy
import logging
from pathlib import Path

from PySide6.QtCore import QObject, QLocale, QRunnable, QSignalBlocker, QSize, QThreadPool, QTimer, Qt, Signal
from PySide6.QtGui import QColor, QCloseEvent, QIcon, QKeySequence, QShortcut, QTextCursor
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QDialogButtonBox,
                              QDoubleSpinBox, QFileDialog, QFormLayout, QFrame, QHBoxLayout,
                              QLabel, QLineEdit, QMainWindow, QMessageBox,
                              QPlainTextEdit, QProgressBar, QPushButton, QSpinBox,
                              QTextEdit, QVBoxLayout, QWidget)

from app.settings import Settings, SettingsStore
from app.branding import APP_ICON, APP_NAME, ui_icon
from app.midi_dialog import MidiImportDialog
from app.song_dialog import SongDialog
from app.i18n import LANGUAGES, tr, status_text, error_text, notation_text, install_qt_translator
from app.flags import flag_icon
from app.fonts import ensure_fonts
from app.styles import STYLE
from player.models import PlaybackPlan
from player.parser import SheetParser, SheetSyntaxError
from player.plan_writer import build_plan
from player.playback_controller import PlaybackController
from player.song_library import load_song_library, save_imported_song, save_custom_song


class ParseSignals(QObject):
    done = Signal(int, object, object)


class ParseJob(QRunnable):
    def __init__(self, revision: int, source: str, note_delay: int, hold: int):
        super().__init__()
        self.revision = revision
        self.source = source
        self.note_delay = note_delay
        self.hold = hold
        self.signals = ParseSignals()

    def run(self) -> None:
        try:
            parsed = SheetParser().parse(self.source)
            plan = build_plan(parsed, self.note_delay, self.hold)
            self.signals.done.emit(self.revision, plan, None)
        except Exception as error:
            self.signals.done.emit(self.revision, None, error)


def clock_text(milliseconds: float) -> str:
    seconds = max(0, int(milliseconds / 1000))
    return f"{seconds // 60:02}:{seconds % 60:02}"


class AdvancedDialog(QDialog):
    def __init__(self, settings: Settings, parent: QWidget):
        super().__init__(parent)
        self.t = lambda key, **values: tr(settings.language, key, **values)
        self.setWindowTitle(self.t("advanced"))
        self.resize(570, 330)
        self.settings = deepcopy(settings)
        form = QFormLayout(self)
        self.path = QLineEdit(settings.ahk_executable_path)
        self.path.setPlaceholderText(self.t("auto_ahk"))
        row = QHBoxLayout()
        row.addWidget(self.path)
        browse = QPushButton(self.t("browse"))
        browse.clicked.connect(self._browse)
        row.addWidget(browse)
        form.addRow("AutoHotkey v2", row)
        self.mode = QComboBox()
        self.mode.addItems(["Event", "Input"])
        self.mode.setCurrentText(settings.send_mode)
        form.addRow(self.t("send_mode"), self.mode)
        self.hotkeys = []
        for label, value in [(self.t("toggle"), settings.hotkey_toggle),
                             (self.t("stop"), settings.hotkey_stop), (self.t("emergency"), settings.hotkey_emergency)]:
            field = QLineEdit(value)
            self.hotkeys.append(field)
            form.addRow(label, field)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText(self.t("ok"))
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(self.t("cancel"))
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def _browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "AutoHotkey v2", "", "AutoHotkey (*.exe)",
                                             options=QFileDialog.Option.DontUseNativeDialog)
        if path:
            self.path.setText(path)

    def _accept(self) -> None:
        hotkeys = [field.text().strip() for field in self.hotkeys]
        # Restrict the editor to unambiguous non-piano function keys.
        allowed_keys = {f"F{number}" for number in range(1, 25)}
        if len(set(hotkeys)) != 3 or any(key not in allowed_keys for key in hotkeys):
            QMessageBox.warning(self, self.t("hotkeys"), self.t("hotkey_error"))
            return
        self.settings.ahk_executable_path = self.path.text().strip()
        self.settings.send_mode = self.mode.currentText()
        self.settings.hotkey_toggle, self.settings.hotkey_stop, self.settings.hotkey_emergency = hotkeys
        self.accept()


class MainWindow(QMainWindow):
    def __init__(self, root: Path):
        super().__init__()
        ensure_fonts()
        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon(str(APP_ICON)))
        self.resize(1120, 840)
        self.setMinimumSize(880, 720)
        self.setStyleSheet(STYLE)
        self.store = SettingsStore(root / "data/settings.json")
        self.settings = self.store.load()
        install_qt_translator(self.settings.language)
        self._translated = []
        self._status_source = "Ready"
        self._validation_state = ("checking", {})
        self.library_directory = root / "data/library"
        self.songs = load_song_library(self.library_directory, self.settings.deleted_song_ids)
        self.current_song = next((song for song in self.songs if song.id == self.settings.selected_song_id),
                                 self.songs[0] if self.songs else None)
        self._last_deleted = None
        self.plan: PlaybackPlan | None = None
        self.revision = 0
        self.jobs: dict[int, ParseJob] = {}
        self.parse_running = False
        self.parse_pending = False
        self.pool = QThreadPool(self)
        self.pool.setMaxThreadCount(1)
        self.controller = PlaybackController(root, self.settings, self)
        self._build_ui()
        self.debounce = QTimer(self)
        self.debounce.setSingleShot(True)
        self.debounce.setInterval(180)
        self.debounce.timeout.connect(self._parse)
        self.save_timer = QTimer(self)
        self.save_timer.setSingleShot(True)
        self.save_timer.setInterval(400)
        self.save_timer.timeout.connect(self._persist)
        self.song_selector.currentIndexChanged.connect(self._select_song)
        self.editor.textChanged.connect(self._sheet_changed)
        self.note.valueChanged.connect(self._timing_changed)
        self.hold.valueChanged.connect(self._timing_changed)
        self.start.valueChanged.connect(self._timing_changed)
        self.humanize.toggled.connect(self._humanize_changed)
        self.controller.state_changed.connect(self._state_changed)
        self.controller.progress.connect(self._progress)
        self.controller.toggle_requested.connect(self._toggle)
        self.controller.worker_ready.connect(lambda _: self._update_buttons())
        self.controller.error.connect(self._worker_error)
        self._install_shortcuts()
        self._select_song(self.song_selector.currentIndex())
        self.language_selector.currentIndexChanged.connect(self._language_changed)
        QTimer.singleShot(0, self.controller.launch_worker)

    def t(self, key, **values):
        return tr(self.settings.language, key, **values)

    def _translate(self, widget, key, method="setText"):
        self._translated.append((widget, key, method))
        getattr(widget, method)(self.t(key))
        return widget

    def _language_changed(self, _):
        self.settings.language = self.language_selector.currentData()
        install_qt_translator(self.settings.language)
        for widget, key, method in self._translated:
            getattr(widget, method)(self.t(key))
        self.library_count.setText(self.t("count", count=len(self.songs)))
        self._update_hotkey_hint()
        self._show_validation()
        self.status.setText(status_text(self.settings.language, self._status_source))
        self.pause.setText(self.t("resume" if self.controller.state == "PAUSED" else "pause"))
        self._refresh_notation_link()
        self._persist()

    def _refresh_notation_link(self):
        self._notation_label.setText('<a href="notation" style="color: #bde8d2; text-decoration: none">'
                                     + self.t("notation") + ' ↗</a>')

    def _set_validation(self, key, **values):
        self._validation_state = (key, values)
        self._show_validation()

    def _show_validation(self):
        key, values = self._validation_state
        values = dict(values)
        if "error" in values:
            values["error"] = error_text(self.settings.language, values["error"])
        self.validation.setText(self.t(key, **values))

    def _build_ui(self) -> None:
        body = QWidget()
        body.setObjectName("appBody")
        self.setCentralWidget(body)
        layout = QVBoxLayout(body)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(16)

        def panel(name):
            frame = QFrame()
            frame.setObjectName(name)
            frame.setProperty("panel", True)
            return frame

        def caption(text):
            label = self._translate(QLabel(), text)
            label.setObjectName("caption")
            return label

        header = QHBoxLayout()
        header.setSpacing(12)
        logo = QLabel()
        logo.setObjectName("brandMark")
        logo.setPixmap(self.windowIcon().pixmap(48, 48))
        logo.setFixedSize(48, 48)
        header.addWidget(logo)
        brand = QVBoxLayout()
        brand.setSpacing(1)
        self.app_title = QLabel(APP_NAME)
        self.app_title.setObjectName("title")
        brand.addWidget(self.app_title)
        subtitle = self._translate(QLabel(), "subtitle")
        subtitle.setObjectName("muted")
        brand.addWidget(subtitle)
        header.addLayout(brand)
        header.addStretch()
        self.library_count = QLabel(self.t("count", count=len(self.songs)))
        self.library_count.setObjectName("badge")
        self.language_selector = QComboBox()
        self.language_selector.setObjectName("languageSelector")
        self.language_selector.setIconSize(QSize(24, 16))
        self.language_selector.setMinimumWidth(165)
        self.language_selector.setMaxVisibleItems(len(LANGUAGES))
        for code, name, country in LANGUAGES:
            self.language_selector.addItem(flag_icon(country), name, code)
        self.language_selector.setCurrentIndex(self.language_selector.findData(self.settings.language))
        self._translate(self.language_selector, "language", "setAccessibleName")
        self._translate(self.language_selector, "language", "setToolTip")
        header.addWidget(self.language_selector)
        self.import_midi_button = self._translate(QPushButton(), "import_midi")
        self.import_midi_button.setIcon(ui_icon("folder"))
        self.import_midi_button.clicked.connect(self._import_midi)
        self.advanced = self._translate(QPushButton(), "advanced")
        self.advanced.setObjectName("secondary")
        self.advanced.setIcon(ui_icon("settings"))
        self.advanced.setIconSize(QSize(18, 18))
        self._translate(self.advanced, "advanced_tip", "setToolTip")
        self.advanced.clicked.connect(self._advanced)
        header.addWidget(self.advanced)
        layout.addLayout(header)

        workspace = QHBoxLayout()
        workspace.setSpacing(16)
        score_column = QVBoxLayout()
        score_column.setSpacing(14)
        library = panel("libraryCard")
        library_layout = QVBoxLayout(library)
        library_layout.setContentsMargins(18, 15, 18, 15)
        library_layout.setSpacing(8)
        library_heading = QHBoxLayout()
        library_heading.addWidget(caption("library"))
        library_heading.addStretch()
        library_heading.addWidget(self.library_count)
        library_layout.addLayout(library_heading)
        self.song_selector = QComboBox()
        self.song_selector.setObjectName("songSelector")
        self.song_selector.setEditable(False)
        self.song_selector.setMinimumHeight(44)
        self.song_selector.setMaxVisibleItems(12)
        self._translate(self.song_selector, "library_empty", "setPlaceholderText")
        self._translate(self.song_selector, "song", "setAccessibleName")
        for song in self.songs:
            self.song_selector.addItem(song.title, song.id)
        self.song_selector.setCurrentIndex(next((index for index, song in enumerate(self.songs)
                                               if self.current_song and song.id == self.current_song.id), -1))
        selector_row = QHBoxLayout()
        selector_row.setSpacing(8)
        selector_row.addWidget(self.song_selector, 1)
        self.undo_delete_button = QPushButton()
        self.undo_delete_button.setIcon(ui_icon("restore"))
        self.delete_song_button = QPushButton()
        self.delete_song_button.setIcon(ui_icon("trash"))
        for button, key, callback in ((self.undo_delete_button, "undo_delete", self._undo_delete),
                                      (self.delete_song_button, "delete_song", self._delete_song)):
            button.setObjectName("iconButton")
            button.setFixedSize(38, 38)
            button.setIconSize(QSize(18, 18))
            self._translate(button, key, "setToolTip")
            self._translate(button, key, "setAccessibleName")
            button.clicked.connect(callback)
            selector_row.addWidget(button)
        self.undo_delete_button.hide()
        library_layout.addLayout(selector_row)
        library_actions = QHBoxLayout()
        self.add_song_button = self._translate(QPushButton(), "new_song")
        self.add_song_button.setIcon(ui_icon("plus"))
        self.add_song_button.clicked.connect(self._new_song)
        library_actions.addWidget(self.add_song_button)
        library_actions.addWidget(self.import_midi_button)
        library_actions.addStretch()
        library_layout.addLayout(library_actions)
        score_column.addWidget(library)

        score_card = panel("scoreCard")
        self.score_card = score_card
        score_layout = QVBoxLayout(score_card)
        score_layout.setContentsMargins(18, 14, 18, 14)
        score_layout.setSpacing(10)
        sheet_toolbar = QHBoxLayout()
        sheet_toolbar.setSpacing(6)
        sheet_toolbar.addWidget(caption("sheet"))
        sheet_toolbar.addStretch()
        self.file_buttons = []
        for text, icon, callback in (("open", "folder", self._open), ("save", "save", self._save),
                                     ("original", "restore", self._restore_sheet)):
            button = self._translate(QPushButton(), text)
            button.setObjectName("toolButton")
            button.setIcon(ui_icon(icon))
            button.setIconSize(QSize(16, 16))
            button.clicked.connect(callback)
            sheet_toolbar.addWidget(button)
            self.file_buttons.append(button)
        score_layout.addLayout(sheet_toolbar)
        self.editor = QPlainTextEdit()
        self.editor.setObjectName("sheetEditor")
        self._translate(self.editor, "sheet", "setAccessibleName")
        self._translate(self.editor, "placeholder", "setPlaceholderText")
        self.editor.setAcceptDrops(True)
        self.editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        score_layout.addWidget(self.editor, 1)
        hold_hint = self._translate(QLabel(), "notation")
        hold_hint.setTextFormat(Qt.TextFormat.RichText)
        self._notation_label = hold_hint
        self._refresh_notation_link()
        hold_hint.linkActivated.connect(self._notation_help)
        hold_hint.setObjectName("muted")
        hold_hint.setWordWrap(True)
        score_layout.addWidget(hold_hint)
        self.validation = QLabel(self.t("checking"))
        self.validation.setObjectName("muted")
        self.validation.setWordWrap(True)
        score_layout.addWidget(self.validation)
        score_column.addWidget(score_card, 1)
        workspace.addLayout(score_column, 1)

        timing_card = panel("timingCard")
        self.timing_card = timing_card
        timing_card.setFixedWidth(300)
        timing_layout = QVBoxLayout(timing_card)
        timing_layout.setContentsMargins(20, 20, 20, 18)
        timing_layout.setSpacing(12)
        timing_layout.addWidget(caption("timing"))
        self.note = QSpinBox()
        self.note.setRange(20, 500)
        self.note.setSuffix(" ms")
        self.note.setValue(self.settings.note_delay_ms)
        self.note.setToolTip("- = 100% · {…} = 35%")
        self.hold = QSpinBox()
        self.hold.setRange(5, 200)
        self.hold.setSuffix(" ms")
        self.hold.setValue(self.settings.key_hold_ms)
        self.hold.setToolTip("[asd]<1000> · [a<1000>s<200>]")
        self.start = QDoubleSpinBox()
        self.start.setLocale(QLocale.c())
        self.start.setRange(0.0, 10.0)
        self.start.setDecimals(1)
        self.start.setSingleStep(0.1)
        self.start.setSuffix(" s")
        self.start.setValue(self.settings.start_delay_s)
        for field in (self.note, self.hold, self.start):
            field.setObjectName("timing")
            field.setMinimumHeight(64)
            field.setKeyboardTracking(False)
        for label, field in [("note_delay", self.note), ("key_hold", self.hold), ("start_delay", self.start)]:
            column = QVBoxLayout()
            column.setSpacing(7)
            column.addWidget(self._translate(QLabel(), label))
            column.addWidget(field)
            timing_layout.addLayout(column)
        self.humanize = self._translate(QCheckBox(), "humanize")
        self.humanize.setChecked(self.settings.humanize)
        self._translate(self.humanize, "humanize_tip", "setToolTip")
        timing_layout.addWidget(self.humanize)
        timing_layout.addStretch(1)
        preset_row = QHBoxLayout()
        preset_row.setSpacing(8)
        self.reset_timing = self._translate(QPushButton(), "reset_timing")
        self.reset_timing.setObjectName("secondary")
        self.reset_timing.setIcon(ui_icon("restore"))
        self._translate(self.reset_timing, "reset_tip", "setToolTip")
        self.reset_timing.clicked.connect(self._reset_timing)
        preset_row.addWidget(self.reset_timing, 1)
        timing_layout.addLayout(preset_row)
        workspace.addWidget(timing_card)
        layout.addLayout(workspace, 1)

        transport = panel("transportCard")
        self.transport_card = transport
        transport_layout = QVBoxLayout(transport)
        transport_layout.setContentsMargins(20, 15, 20, 14)
        transport_layout.setSpacing(10)
        progress_row = QHBoxLayout()
        self.position = QLabel("0%")
        self.position.setObjectName("muted")
        self.time = QLabel("00:00 / 00:00")
        self.time.setObjectName("clock")
        progress_row.addWidget(self.position)
        progress_row.addStretch()
        progress_row.addWidget(self.time)
        transport_layout.addLayout(progress_row)
        self.bar = QProgressBar()
        self.bar.setRange(0, 1000)
        self.bar.setValue(0)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(6)
        transport_layout.addWidget(self.bar)
        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        self.status_dot = QLabel("●")
        self.status_dot.setObjectName("statusDot")
        buttons.addWidget(self.status_dot)
        self.status = QLabel(self.t("ready"))
        self.status.setObjectName("status")
        self.status.setWordWrap(True)
        buttons.addWidget(self.status, 1)
        self.play = self._translate(QPushButton(), "play")
        self.play.setObjectName("play")
        self.play.setIcon(ui_icon("play", "#152c21"))
        self.play.setMinimumWidth(142)
        self.play.clicked.connect(self._play)
        self.pause = self._translate(QPushButton(), "pause")
        self.pause.setObjectName("transportButton")
        self.pause.setIcon(ui_icon("pause"))
        self.pause.setMinimumWidth(112)
        self.pause.clicked.connect(self._pause_resume)
        self.stop = self._translate(QPushButton(), "stop")
        self.stop.setObjectName("transportButton")
        self.stop.setIcon(ui_icon("stop"))
        self.stop.setMinimumWidth(100)
        self.stop.clicked.connect(lambda: self.controller.stop())
        for button in (self.play, self.pause, self.stop):
            button.setMinimumHeight(42)
            button.setIconSize(QSize(18, 18))
            buttons.addWidget(button)
        transport_layout.addLayout(buttons)
        self.hotkeys_hint = QLabel()
        self.hotkeys_hint.setObjectName("hotkeys")
        self.hotkeys_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(transport)
        layout.addWidget(self.hotkeys_hint)
        self._update_hotkey_hint()
        self._update_buttons()

    def _install_shortcuts(self) -> None:
        # AHK implements global shortcuts. These provide local Stop when it is unavailable.
        self.shortcuts = []
        for key, callback in [(self.settings.hotkey_toggle, self._toggle),
                              (self.settings.hotkey_stop, lambda: self.controller.stop()),
                              (self.settings.hotkey_emergency, lambda: self.controller.stop(True))]:
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(lambda callback=callback: callback() if not self.controller.ready else None)
            self.shortcuts.append(shortcut)

    def _update_hotkey_hint(self) -> None:
        self.hotkeys_hint.setText(f'{self.settings.hotkey_toggle}  {self.t("toggle")}     '
                                 f'{self.settings.hotkey_stop}  {self.t("stop")}     '
                                 f'{self.settings.hotkey_emergency}  {self.t("emergency")}')
        self.hotkeys_hint.setWordWrap(True)

    def _select_song(self, index: int) -> None:
        if self.controller.state in self.controller.ACTIVE:
            return
        if not self.songs:
            self._clear_selection()
            return
        if not 0 <= index < len(self.songs):
            return
        self.current_song = self.songs[index]
        song = self.current_song
        self.settings.selected_song_id = song.id
        values = self.settings.song_timings.get(song.id, {})
        self.settings.note_delay_ms = int(values.get("note_delay_ms", song.note_delay_ms))
        self.settings.key_hold_ms = int(values.get("key_hold_ms", song.key_hold_ms))
        self.settings.start_delay_s = float(values.get("start_delay_s", song.start_delay_s))
        for field, value in ((self.note, self.settings.note_delay_ms), (self.hold, self.settings.key_hold_ms), (self.start, self.settings.start_delay_s)):
            with QSignalBlocker(field):
                field.setValue(value)
        with QSignalBlocker(self.editor):
            self.editor.setPlainText(self.settings.sheet_overrides.get(song.id, song.sheet))
        self.editor.setExtraSelections([])
        self.bar.setValue(0)
        self.position.setText("0%")
        self._persist()
        self._invalidate()

    def _clear_selection(self):
        self.current_song = None
        self.settings.selected_song_id = ""
        self.revision += 1
        self.plan = None
        self.parse_pending = False
        self.debounce.stop()
        with QSignalBlocker(self.editor):
            self.editor.clear()
        self.editor.setExtraSelections([])
        self.bar.setValue(0)
        self.position.setText("0%")
        self.time.setText("00:00 / 00:00")
        self._set_validation("library_empty")
        self._update_buttons()
        self._persist()

    def _humanize_changed(self, checked: bool) -> None:
        self.settings.humanize = checked
        self._persist()

    def _timing_changed(self) -> None:
        if self.current_song is None:
            return
        self.settings.note_delay_ms = self.note.value()
        self.settings.key_hold_ms = self.hold.value()
        self.settings.start_delay_s = self.start.value()
        self.settings.song_timings[self.current_song.id] = {
            "note_delay_ms": self.settings.note_delay_ms,
            "key_hold_ms": self.settings.key_hold_ms,
            "start_delay_s": self.settings.start_delay_s,
        }
        self._persist()
        self._invalidate()

    def _reset_timing(self) -> None:
        if self.current_song is None:
            return
        self.settings.song_timings.pop(self.current_song.id, None)
        self._select_song(self.song_selector.currentIndex())

    def _notation_help(self, *_):
        dialog = QDialog(self)
        dialog.setWindowTitle(self.t("notation"))
        dialog.resize(650, 530)
        layout = QVBoxLayout(dialog)
        text = QPlainTextEdit()
        text.setReadOnly(True)
        text.setPlainText(notation_text(self.settings.language))
        layout.addWidget(text)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.button(QDialogButtonBox.StandardButton.Close).setText(self.t("close"))
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        dialog.exec()
        dialog.deleteLater()

    def _sheet_changed(self) -> None:
        if self.current_song is None:
            return
        source = self.editor.toPlainText()
        if source == self.current_song.sheet:
            self.settings.sheet_overrides.pop(self.current_song.id, None)
        else:
            self.settings.sheet_overrides[self.current_song.id] = source
        self.save_timer.start()
        self._invalidate()

    def _persist(self) -> None:
        try:
            self.store.save(self.settings)
        except OSError as error:
            logging.exception("Cannot save settings")
            self.status.setText(self.t("save_error", error=error))

    def _invalidate(self) -> None:
        self.revision += 1
        self.plan = None
        self._set_validation("checking")
        self._update_buttons()
        self.debounce.start()

    def _parse(self) -> None:
        if self.current_song is None:
            return
        if self.parse_running:
            self.parse_pending = True
            return
        job = ParseJob(self.revision, self.editor.toPlainText(), self.settings.note_delay_ms, self.settings.key_hold_ms)
        job.signals.done.connect(self._parsed)
        self.jobs[self.revision] = job
        self.parse_running = True
        self.pool.start(job)

    def _parsed(self, revision: int, plan: PlaybackPlan | None, error: Exception | None) -> None:
        self.jobs.pop(revision, None)
        self.parse_running = False
        if self.current_song is None:
            self.parse_pending = False
            return
        if revision == self.revision:
            self.plan = plan
            if error:
                if isinstance(error, SheetSyntaxError):
                    self._set_validation("syntax_error", position=error.start + 1, error=str(error))
                    self._highlight(error.start, error.end, "#783645")
                else:
                    self._set_validation("error", error=str(error))
                logging.info("Parser error: %s", error)
            elif plan and plan.events:
                self._set_validation("valid", count=len(plan.events))
                if self.controller.state not in self.controller.ACTIVE:
                    self.editor.setExtraSelections([])
                    self.time.setText(f"00:00 / {clock_text(plan.duration_ms)}")
            else:
                self._set_validation("empty")
                self.editor.setExtraSelections([])
            self._update_buttons()
        if self.parse_pending or revision != self.revision:
            self.parse_pending = False
            self.debounce.stop()
            self._parse()

    def _play(self) -> None:
        if self.controller.state == "PAUSED":
            self.controller.resume()
        elif self.plan and self.plan.events:
            try:
                self.controller.play(self.plan)
            except OSError as error:
                self.status.setText(self.t("plan_error", error=error))

    def _pause_resume(self) -> None:
        if self.controller.state == "PLAYING":
            self.controller.pause()
        else:
            self.controller.resume()

    def _toggle(self) -> None:
        if self.controller.state == "PLAYING":
            self.controller.pause()
        elif self.controller.state != "COUNTDOWN":
            self._play()

    def _state_changed(self, state: str, text: str) -> None:
        self._status_source = text or state
        self.status.setText(status_text(self.settings.language, self._status_source))
        self.pause.setText(self.t("resume" if state == "PAUSED" else "pause"))
        self.pause.setIcon(ui_icon("play") if state == "PAUSED" else ui_icon("pause"))
        color = "#edb96b" if state in {"COUNTDOWN", "PAUSED"} else "#ed8e8e" if state == "ERROR" else "#bde8d2"
        self.status_dot.setStyleSheet(f"color: {color}")
        if state in {"IDLE", "STOPPED", "FINISHED", "ERROR"}:
            self.editor.setExtraSelections([])
        self._update_buttons()

    def _worker_error(self, message: str) -> None:
        self._status_source = message
        self.status.setText(error_text(self.settings.language, message))
        self._update_buttons()

    def _update_buttons(self) -> None:
        state = self.controller.state
        active = state in self.controller.ACTIVE
        editable = not active and self.current_song is not None
        self.advanced.setEnabled(not active)
        self.import_midi_button.setEnabled(not active)
        self.add_song_button.setEnabled(not active)
        self.humanize.setEnabled(not active)
        self.song_selector.setEnabled(not active and bool(self.songs))
        self.delete_song_button.setEnabled(editable)
        self.undo_delete_button.setEnabled(not active and self._last_deleted is not None)
        self.editor.setReadOnly(not editable)
        self.reset_timing.setEnabled(editable)
        for field in (self.note, self.hold, self.start):
            field.setEnabled(self.current_song is not None)
        for button in self.file_buttons:
            button.setEnabled(editable)
        paused = state == "PAUSED"
        self.play.setEnabled(self.controller.ready and not self.controller.stopping and (paused or (state not in self.controller.ACTIVE and bool(self.plan and self.plan.events))))
        self.pause.setEnabled(state in {"PLAYING", "PAUSED"})
        self.stop.setEnabled(state in self.controller.ACTIVE)

    def _progress(self, current: int, total: int, elapsed: float) -> None:
        plan = self.controller.plan
        duration = plan.duration_ms if plan else 0
        fraction = min(1.0, elapsed / duration) if duration else 0.0
        self.bar.setValue(round(fraction * 1000))
        self.position.setText(f"{round(fraction * 100)}%  ·  {current} / {total}")
        self.time.setText(f"{clock_text(elapsed)} / {clock_text(duration)}")
        if plan and 0 < current <= len(plan.events):
            event = plan.events[current - 1]
            self._highlight(event.source_start, event.source_end, "#315644", scroll=True)
        else:
            self.editor.setExtraSelections([])

    def _highlight(self, start: int, end: int, color: str, scroll: bool = False) -> None:
        selection = QTextEdit.ExtraSelection()
        cursor = QTextCursor(self.editor.document())
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        selection.cursor = cursor
        selection.format.setBackground(QColor(color))
        self.editor.setExtraSelections([selection])
        if scroll:
            rect = self.editor.cursorRect(cursor)
            if not self.editor.viewport().rect().contains(rect):
                # Playback editor is read-only, so moving this cursor cannot alter text.
                self.editor.setTextCursor(cursor)
                self.editor.ensureCursorVisible()

    def _advanced(self) -> None:
        dialog = AdvancedDialog(self.settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.settings = dialog.settings
            self.controller.settings = self.settings
            self._persist()
            for shortcut in self.shortcuts:
                shortcut.setEnabled(False)
                shortcut.deleteLater()
            self._install_shortcuts()
            self._update_hotkey_hint()
            self.controller.restart_worker()

    def _open(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, self.t("open_sheet"), "", self.t("text_files") + ";;" + self.t("all_files"),
                                             options=QFileDialog.Option.DontUseNativeDialog)
        if path:
            try:
                self.editor.setPlainText(Path(path).read_text(encoding="utf-8-sig"))
            except (OSError, UnicodeError) as error:
                QMessageBox.warning(self, self.t("open_sheet"), str(error))

    def _new_song(self):
        if self.controller.state in self.controller.ACTIVE:
            return
        dialog = SongDialog(self.settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                self._add_custom_song(dialog.title.text(), dialog.sheet.toPlainText())
            except (OSError, ValueError) as error:
                QMessageBox.warning(self, self.t("new_song"), error_text(self.settings.language, str(error)))
        dialog.deleteLater()

    def _add_custom_song(self, title, sheet):
        song = save_custom_song(self.library_directory, title, sheet,
                                self.note.value(), self.hold.value(), self.start.value())
        self._append_song(song)

    def _append_song(self, song):
        self._replace_library(self.songs + (song,), len(self.songs))
        self._status_source = "Song added to the library"
        self.status.setText(self.t("song_added"))

    def _replace_library(self, songs, selected_index):
        self.songs = tuple(songs)
        with QSignalBlocker(self.song_selector):
            self.song_selector.clear()
            for song in self.songs:
                self.song_selector.addItem(song.title, song.id)
            self.song_selector.setCurrentIndex(selected_index)
        self.library_count.setText(self.t("count", count=len(self.songs)))
        self._select_song(selected_index)

    def _save_deletion_state(self, deleted_ids, selected_id):
        # Commit preferences before changing the UI; failed writes leave the song available.
        settings = deepcopy(self.settings)
        settings.deleted_song_ids = deleted_ids
        settings.selected_song_id = selected_id
        try:
            self.store.save(settings)
        except OSError as error:
            logging.exception("Cannot save library change")
            self.status.setText(self.t("save_error", error=error))
            return False
        self.settings = settings
        self.controller.settings = settings
        return True

    def _delete_song(self):
        if self.current_song is None or self.controller.state in self.controller.ACTIVE:
            return
        index = self.song_selector.currentIndex()
        song = self.current_song
        remaining = tuple(item for item in self.songs if item.id != song.id)
        next_index = min(index, len(remaining) - 1)
        next_id = remaining[next_index].id if remaining else ""
        deleted = list(dict.fromkeys([*self.settings.deleted_song_ids, song.id]))
        if not self._save_deletion_state(deleted, next_id):
            return
        self._last_deleted = (song, index)
        self.undo_delete_button.show()
        self._replace_library(remaining, next_index)
        self._status_source = "Song deleted from the library"
        self.status.setText(self.t("song_deleted"))

    def _undo_delete(self):
        if self._last_deleted is None or self.controller.state in self.controller.ACTIVE:
            return
        song, index = self._last_deleted
        deleted = [song_id for song_id in self.settings.deleted_song_ids if song_id != song.id]
        if not self._save_deletion_state(deleted, song.id):
            return
        songs = list(self.songs)
        index = min(index, len(songs))
        songs.insert(index, song)
        self._last_deleted = None
        self.undo_delete_button.hide()
        self._replace_library(songs, index)
        self._status_source = "Song restored"
        self.status.setText(self.t("song_restored"))

    def _import_midi(self) -> None:
        if self.controller.state in self.controller.ACTIVE:
            return
        path, _ = QFileDialog.getOpenFileName(self, self.t("import_midi"), "", "MIDI (*.mid *.midi)",
                                             options=QFileDialog.Option.DontUseNativeDialog)
        if not path:
            return
        dialog = MidiImportDialog(Path(path), self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.result_score is not None:
            try:
                self._add_imported_song(dialog.title.text(), dialog.result_score)
            except (OSError, ValueError) as error:
                QMessageBox.warning(self, self.t("import_midi"), error_text(self.settings.language, str(error)))
        dialog.deleteLater()

    def _add_imported_song(self, title, result):
        song = save_imported_song(self.library_directory, title, result.sheet, result.summary)
        self._append_song(song)

    def _save(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, self.t("save_sheet"), "sheet.txt", self.t("text_files"),
                                             options=QFileDialog.Option.DontUseNativeDialog)
        if path:
            try:
                Path(path).write_text(self.editor.toPlainText(), encoding="utf-8")
            except OSError as error:
                QMessageBox.warning(self, self.t("save_sheet"), str(error))

    def _restore_sheet(self) -> None:
        if self.current_song is not None:
            self.editor.setPlainText(self.current_song.sheet)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.debounce.stop()
        self.save_timer.stop()
        self.controller.shutdown()
        self.pool.waitForDone(3000)
        self._persist()
        event.accept()
