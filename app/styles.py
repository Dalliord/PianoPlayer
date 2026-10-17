from app.branding import ICON_DIRECTORY

STYLE = """
QWidget { color: #e8efea; font-family: 'Segoe UI'; font-size: 13px; }
QMainWindow, QWidget#appBody, QDialog, QMessageBox { background: #0d1513; }
QLabel { background: transparent; border: none; }
QLabel#title { font-size: 26px; font-weight: 700; }
QLabel#muted { color: #91a69c; font-size: 12px; }
QLabel#caption { color: #a3b8ad; font-size: 11px; font-weight: 700; }
QLabel#badge { color: #bdd3c7; background: #1a2b23; border: 1px solid #2b4135;
 border-radius: 14px; padding: 6px 12px; font-size: 12px; }
QLabel#sourceLink { font-size: 12px; }
QLabel#clock { color: #e5efe8; font-family: Consolas; font-size: 18px; }
QLabel#status { color: #c1d2c8; font-size: 12px; }
QLabel#statusDot { color: #bde8d2; font-size: 11px; }
QLabel#hotkeys { color: #728c7f; font-size: 11px; }
QFrame[panel="true"] { background: #151f1a; border: 1px solid #2a3a30; border-radius: 16px; }
QFrame#timingCard { background: #19271f; border-color: #304638; }
QFrame#transportCard { background: #17241d; }
QPlainTextEdit { background: #101a15; border: 1px solid #293e30; border-radius: 10px;
 padding: 13px; color: #d3e8d9; font-family: Consolas; font-size: 16px;
 selection-background-color: #41674f; selection-color: #ffffff; }
QPlainTextEdit:focus { border-color: #719e83; }
QListWidget { background: #111c16; border: 1px solid #344b3c; border-radius: 9px; padding: 8px; }
QListWidget::item { padding: 8px; }
QListWidget::item:selected { background: #365a43; border-radius: 5px; }
QSpinBox, QDoubleSpinBox, QLineEdit, QComboBox { background: #111c16; border: 1px solid #344b3c;
 border-radius: 9px; padding: 9px 12px; min-height: 22px; selection-background-color: #41674f; }
QSpinBox:focus, QDoubleSpinBox:focus, QLineEdit:focus, QComboBox:focus { border-color: #bde8d2; }
QComboBox#songSelector { font-size: 16px; font-weight: 600; padding: 6px 38px 6px 12px; }
QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: top right;
 width: 34px; border: none; }
QComboBox::down-arrow { image: url("@ICONS@/chevron-down.svg"); width: 14px; height: 14px; }
QComboBox QAbstractItemView { background: #1b2c22; color: #e8efea; border: 1px solid #3a5142;
 outline: 0; selection-background-color: #365a43; padding: 5px; }
QComboBox QAbstractItemView::item { min-height: 32px; padding: 5px 8px; }
QSpinBox#timing, QDoubleSpinBox#timing { font-size: 27px; font-weight: 600;
 padding: 10px 14px; border-radius: 10px; min-height: 42px; }
QSpinBox#timing::up-button, QDoubleSpinBox#timing::up-button {
 subcontrol-origin: border; subcontrol-position: top right; width: 32px;
 border: none; border-top-right-radius: 9px; background: #22392a; }
QSpinBox#timing::down-button, QDoubleSpinBox#timing::down-button {
 subcontrol-origin: border; subcontrol-position: bottom right; width: 32px;
 border: none; border-bottom-right-radius: 9px; background: #22392a; }
QSpinBox#timing::up-button:hover, QDoubleSpinBox#timing::up-button:hover,
QSpinBox#timing::down-button:hover, QDoubleSpinBox#timing::down-button:hover { background: #36523e; }
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow { image: url("@ICONS@/chevron-up.svg"); width: 12px; height: 12px; }
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow { image: url("@ICONS@/chevron-down.svg"); width: 12px; height: 12px; }
QPushButton { background: #243b2c; border: 1px solid #36513e; border-radius: 9px;
 padding: 9px 15px; font-weight: 600; }
QPushButton:hover { background: #304e39; border-color: #5a7c65; }
QPushButton:pressed { background: #3b5b45; }
QPushButton:focus { border-color: #bde8d2; }
QPushButton#secondary, QPushButton#toolButton, QPushButton#iconButton { background: transparent; }
QPushButton#secondary:hover, QPushButton#toolButton:hover, QPushButton#iconButton:hover { background: #263e2e; }
QPushButton#toolButton { padding: 6px 8px; border-color: transparent; font-size: 12px; }
QPushButton#iconButton { padding: 8px; }
QPushButton#play { background: #bde8d2; color: #152c21; border-color: #bde8d2; font-size: 15px; }
QPushButton#play:hover { background: #d1f4e0; border-color: #d1f4e0; }
QPushButton#play:pressed { background: #9ac8ac; }
QPushButton#transportButton { background: #203329; }
QPushButton:disabled, QPushButton#play:disabled { color: #657e6f; background: #1b2b22; border-color: #2b3d31; }
QCheckBox { spacing: 9px; }
QCheckBox::indicator { width: 18px; height: 18px; border: 1px solid #577863; border-radius: 5px; background: #101c15; }
QCheckBox::indicator:checked { background: #bde8d2; border-color: #bde8d2; image: url("@ICONS@/check.svg"); }
QCheckBox::indicator:disabled { border-color: #3e5545; background: #455f4f; }
QProgressBar { background: #2b4233; border: none; border-radius: 3px; }
QProgressBar::chunk { background: #bde8d2; border-radius: 3px; }
QScrollBar:vertical { background: transparent; width: 9px; margin: 4px 0; }
QScrollBar::handle:vertical { background: #3b5544; min-height: 26px; border-radius: 4px; }
QScrollBar::handle:vertical:hover { background: #64846e; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
QToolTip { color: #e6f0e9; background: #24382b; border: 1px solid #4e705a; padding: 8px; }
""".replace("@ICONS@", ICON_DIRECTORY.as_posix())
