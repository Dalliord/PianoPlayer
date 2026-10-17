"""Shared application identity and small vector interface icons."""
from functools import lru_cache
from pathlib import Path

from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

APP_NAME = "Piano Player"
APP_ID = "PianoPlayer.Desktop"
ICON_DIRECTORY = Path(__file__).resolve().parents[1] / "assets/icons"
APP_ICON = ICON_DIRECTORY / "piano-player.svg"

PATHS = {
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "trash": '<path d="M4 6h16M9 6V3h6v3M6 6l1 15h10l1-15M10 10v7M14 10v7"/>',
    "play": '<path d="M8 5L19 12L8 19Z" fill="{color}" stroke="none"/>',
    "pause": '<path d="M8 6v12M16 6v12" stroke-width="3"/>',
    "stop": '<rect x="6" y="6" width="12" height="12" rx="2" fill="{color}" stroke="none"/>',
    "folder": '<path d="M3 8V6a2 2 0 0 1 2-2h5l2 3h7a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8Z"/>',
    "save": '<path d="M5 3h12l4 4v13H3V3h2ZM7 3v6h10V3M7 20v-7h10v7"/>',
    "restore": '<path d="M4 9a8 8 0 1 1 0 7M4 4v5h5"/>',
    "settings": '<path d="m9 3-.6 3-2 1.2L3.5 6.4l-2 3.5L4 12l-.1 2.3-2 2.3 2.1 3.5 2.8-1 2 1.1.7 2.8h4l.7-2.8 2-1.1 2.8 1 2.1-3.5-2.1-2.3V12l2.4-2.1-2-3.5-2.8.8-2-1.2L14 3Z" transform="translate(1 -1) scale(.92)"/><circle cx="12" cy="12" r="3"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7v.2"/>',
}


@lru_cache(maxsize=32)
def ui_icon(name: str, color: str = "#a8bcb3") -> QIcon:
    path = PATHS[name].replace("{color}", color)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{path}</svg>'
    renderer = QSvgRenderer(QByteArray(svg.encode()))
    icon = QIcon()
    for size in (16, 20, 24, 32, 48):
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        icon.addPixmap(pixmap)
    return icon
