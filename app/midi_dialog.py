"""Choose MIDI tracks and review keyboard adaptations before saving a song."""
from functools import partial
from pathlib import Path
from PySide6.QtCore import QObject, QRunnable, QThreadPool, QTimer, Qt, Signal
from PySide6.QtWidgets import (QCheckBox, QDialog, QDialogButtonBox, QLabel, QLineEdit,
                              QListWidget, QListWidgetItem, QVBoxLayout)
from player.midi_import import convert_midi, read_midi
from player.parser import SheetParser
from player.plan_writer import build_plan
from app.i18n import tr, error_text


class JobSignals(QObject):
    done = Signal(int, object, object)


class ImportJob(QRunnable):
    def __init__(self, revision, function):
        super().__init__()
        self.revision, self.function = revision, function
        self.signals = JobSignals()

    def run(self):
        try:
            result = self.function()
            self.signals.done.emit(self.revision, result, None)
        except Exception as error:
            self.signals.done.emit(self.revision, None, error)


def prepare_score(document, selected, sustain, adapt):
    result = convert_midi(document, selected, sustain=sustain, adapt=adapt)
    plan = build_plan(SheetParser().parse(result.sheet), 100, 35)
    if abs(plan.duration_ms - result.duration_ms) > .01:
        raise ValueError("Не удалось сохранить тайминг MIDI.")
    return result


class MidiImportDialog(QDialog):
    def __init__(self, path: Path, parent=None):
        super().__init__(parent)
        self.language = getattr(getattr(parent, "settings", None), "language", "ru")
        self.t = lambda key, **values: tr(self.language, key, **values)
        self.setWindowTitle(self.t("import_midi"))
        self.resize(700, 600)
        self.document = self.result_score = None
        self._revision = 0
        self._closed = self._converting = False
        self._jobs = {}
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addWidget(QLabel(self.t("title")))
        self.title = QLineEdit(path.stem)
        self.title.setMaxLength(120)
        layout.addWidget(self.title)
        layout.addWidget(QLabel(self.t("tracks")))
        self.tracks = QListWidget()
        self.tracks.setMinimumHeight(120)
        layout.addWidget(self.tracks, 1)
        self.sustain = QCheckBox(self.t("sustain"))
        self.sustain.setChecked(True)
        layout.addWidget(self.sustain)
        self.adapt = QCheckBox(self.t("adapt"))
        self.adapt.setChecked(True)
        layout.addWidget(self.adapt)
        self.summary = QLabel(self.t("reading_midi"))
        self.summary.setTextFormat(Qt.TextFormat.PlainText)
        self.summary.setWordWrap(True)
        self.summary.setMinimumHeight(90)
        layout.addWidget(self.summary)
        detail = QLabel(self.t("midi_detail"))
        detail.setObjectName("muted")
        detail.setWordWrap(True)
        layout.addWidget(detail)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText(self.t("add"))
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(self.t("cancel"))
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        self.title.textChanged.connect(self._update_accept)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(150)
        self.timer.timeout.connect(self._convert)
        job = ImportJob(-1, partial(read_midi, path))
        job.signals.done.connect(self._loaded)
        self._jobs[-1] = job
        QThreadPool.globalInstance().start(job)

    def _loaded(self, revision, document, error):
        self._jobs.pop(revision, None)
        if self._closed:
            return
        if error:
            self.summary.setText(error_text(self.language, str(error)))
            return
        self.document = document
        for track in document.tracks:
            if not track.notes and not track.drums:
                continue
            name = track.name or self.t("track_name", number=track.index + 1)
            item = QListWidgetItem(self.t("track_notes", name=name, count=track.notes)
                                   + (" " + self.t("drums", count=track.drums).lstrip() if track.drums else ""))
            item.setData(Qt.ItemDataRole.UserRole, track.index)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if track.notes else Qt.CheckState.Unchecked)
            if not track.notes:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            self.tracks.addItem(item)
        self.tracks.itemChanged.connect(self._queue)
        self.sustain.toggled.connect(self._queue)
        self.adapt.toggled.connect(self._queue)
        self._queue()

    def _queue(self, *_):
        self._revision += 1
        self.result_score = None
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        self.summary.setText(self.t("preparing"))
        self.timer.start()

    def _convert(self):
        if self._converting or self._closed or self.document is None:
            return
        selected = {self.tracks.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.tracks.count())
                    if self.tracks.item(i).checkState() == Qt.CheckState.Checked}
        job = ImportJob(self._revision, partial(prepare_score, self.document, selected,
                                               self.sustain.isChecked(), self.adapt.isChecked()))
        job.signals.done.connect(self._converted)
        self._jobs[self._revision] = job
        self._converting = True
        QThreadPool.globalInstance().start(job)

    def _converted(self, revision, result, error):
        self._jobs.pop(revision, None)
        self._converting = False
        if self._closed:
            return
        if revision != self._revision:
            self._convert()
            return
        self.result_score = result
        if error:
            self.summary.setText(error_text(self.language, str(error)))
        else:
            changes = result.changes
            self.summary.setText(self.t("midi_stats", played=result.played_notes, source=result.source_notes,
                seconds=result.duration_ms / 1000, tempo=self.document.tempo_changes,
                octaves=changes.get("range", 0) + changes.get("revoiced", 0), merged=changes.get("merged", 0),
                omitted=changes.get("omitted", 0), retriggered=changes.get("retriggered", 0),
                holds=changes.get("holds", 0), repairs=result.repairs))
        self._update_accept()

    def _update_accept(self, *_):
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(
            self.result_score is not None and bool(self.title.text().strip()))

    def accept(self):
        if self.result_score is not None and self.title.text().strip():
            self._closed = True
            self.timer.stop()
            super().accept()

    def reject(self):
        self._closed = True
        self.timer.stop()
        super().reject()
