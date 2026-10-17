"""Export the hand-drawn vector logo for Windows shortcuts and app previews."""
from pathlib import Path
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer


def main():
    application = QGuiApplication.instance() or QGuiApplication([])
    directory = Path(__file__).resolve().parents[1] / "assets/icons"
    renderer = QSvgRenderer(str(directory / "piano-player.svg"))
    if not renderer.isValid():
        raise ValueError("Invalid Piano Player SVG")
    image = QImage(256, 256, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    renderer.render(painter)
    painter.end()
    png = directory / "piano-player.png"
    if not image.save(str(png)):
        raise OSError("Could not save the icon")
    with Image.open(png) as source:
        source.save(directory / "piano-player.ico", format="ICO",
                    sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(directory / "piano-player.ico")


if __name__ == "__main__":
    main()
