"""Create a named song without overwriting the selected library entry."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QDialogButtonBox, QLabel, QLineEdit,
                              QPlainTextEdit, QVBoxLayout)
from app.i18n import tr
from player.parser import SheetParser, SheetSyntaxError
from player.plan_writer import build_plan


class SongDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.t = lambda key, **values: tr(settings.language, key, **values)
        self.setWindowTitle(self.t("new_song"))
        self.resize(700, 550)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addWidget(QLabel(self.t("title")))
        self.title = QLineEdit()
        self.title.setMaxLength(120)
        self.title.setPlaceholderText(self.t("title_hint"))
        layout.addWidget(self.title)
        layout.addWidget(QLabel(self.t("sheet")))
        self.sheet = QPlainTextEdit()
        self.sheet.setPlaceholderText("[asd]<1000> f g h\n|bpm=120| |step=1/4| a b [df]")
        layout.addWidget(self.sheet, 1)
        self.validation = QLabel()
        self.validation.setTextFormat(Qt.TextFormat.PlainText)
        self.validation.setWordWrap(True)
        layout.addWidget(self.validation)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText(self.t("add"))
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(self.t("cancel"))
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        self.title.setFocus()

    def accept(self):
        if not self.title.text().strip():
            self.validation.setText(self.t("name_required"))
            self.title.setFocus()
            return
        try:
            plan = build_plan(SheetParser().parse(self.sheet.toPlainText()),
                              self.settings.note_delay_ms, self.settings.key_hold_ms)
        except (ValueError, SheetSyntaxError) as error:
            from app.i18n import error_text
            self.validation.setText(self.t("error", error=error_text(self.settings.language, str(error))))
            return
        if not any(event.keys for event in plan.events):
            self.validation.setText(self.t("empty"))
            return
        super().accept()
