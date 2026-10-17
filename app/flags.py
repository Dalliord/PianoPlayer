"""Small vector flags, independent of Windows emoji/font support."""
from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer


def flag_icon(country: str) -> QIcon:
    stripes = lambda colors: ''.join(
        f'<rect y="{i * 20 / len(colors)}" width="30" height="{20 / len(colors)}" fill="{color}"/>'
        for i, color in enumerate(colors))
    vertical = lambda colors: ''.join(
        f'<rect x="{i * 10}" width="10" height="20" fill="{color}"/>'
        for i, color in enumerate(colors))
    drawings = {
        "ru": stripes(["#fff", "#0039a6", "#d52b1e"]),
        "de": stripes(["#111", "#d00", "#ffce00"]),
        "fr": vertical(["#002654", "#fff", "#ed2939"]),
        "jp": '<rect width="30" height="20" fill="white"/><circle cx="15" cy="10" r="6" fill="#bc002d"/>',
        "es": '<rect width="30" height="20" fill="#aa151b"/><rect y="5" width="30" height="10" fill="#f1bf00"/>'
              '<path d="M8 8h4v4q-2 3-4 0z" fill="#aa151b" stroke="#fff" stroke-width=".4"/><path d="M7 7h6l-1-2-1 1-1-2-1 2-1-1z" fill="#bd8f30"/>',
        "pt": '<rect width="30" height="20" fill="#f00"/><rect width="12" height="20" fill="#006600"/>'
              '<circle cx="12" cy="10" r="5" fill="none" stroke="#ff0" stroke-width="1.2"/>'
              '<path d="M9 6h6v6q-3 4-6 0z" fill="white" stroke="#c00" stroke-width="1"/>'
              '<path d="M11 7h2v6h-2zM10 9h4v2h-4z" fill="#039"/>',
        "cn": '<rect width="30" height="20" fill="#de2910"/>'
              '<path d="m5 3 1 2h2l-1.6 1.4.6 2.2L5 7.3 3 8.6l.6-2.2L2 5h2z" fill="#ffde00"/>'
              + ''.join(f'<text x="{x}" y="{y}" fill="#ffde00" font-size="3">★</text>' for x, y in [(9, 3), (11, 6), (11, 9), (9, 12)]),
        "kr": '<rect width="30" height="20" fill="white"/>'
              '<circle cx="15" cy="10" r="4.4" fill="#cd2e3a"/>'
              '<path d="M10.6 10a4.4 4.4 0 0 0 8.8 0q-2.2-4.4-4.4 0t-4.4 0" fill="#0047a0"/>'
              + ''.join(f'<path d="M-2 -1.5h4M-2 0h4M-2 1.5h4" stroke="#111" stroke-width=".75" transform="translate({x} {y}) rotate({angle})"/>'
                        for x, y, angle in [(6, 5, -50), (24, 15, -50), (6, 15, 50), (24, 5, 50)])
              + '<path d="m4 15 3 2m15-12 3 2m-3 8 3 2" stroke="white" stroke-width=".7"/>',
        "us": stripes(["#b22234" if i % 2 == 0 else "white" for i in range(13)])
              + '<rect width="12" height="10.8" fill="#3c3b6e"/>'
              + ''.join(f'<circle cx="{1 + i * 2 + (j % 2)}" cy="{1 + j * 1.1}" r=".32" fill="white"/>'
                        for j in range(9) for i in range(6 if j % 2 == 0 else 5)),
    }
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="30" height="20" viewBox="0 0 30 20">' + drawings[country] + '</svg>'
    pixmap = QPixmap(60, 40)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    QSvgRenderer(QByteArray(svg.encode("utf-8"))).render(painter)
    painter.end()
    pixmap.setDevicePixelRatio(2)
    return QIcon(pixmap)
