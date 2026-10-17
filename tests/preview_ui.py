"""Render an offscreen preview without launching AHK or sending input."""
import os
from pathlib import Path
from unittest.mock import patch
import time
import argparse
from tempfile import TemporaryDirectory

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from PySide6.QtGui import QFontDatabase
from app.main_window import MainWindow


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--song", default="wolf-last-dawn")
    parser.add_argument("--width", type=int, default=1120)
    parser.add_argument("--height", type=int, default=840)
    parser.add_argument("--language", default="ru")
    parser.add_argument("--output", type=Path, default=root / "assets/piano-player-preview.png")
    args = parser.parse_args()
    application = QApplication([])
    for font in ("segoeui.ttf", "segoeuib.ttf", "consola.ttf"):
        QFontDatabase.addApplicationFont(str(Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / font))
    with TemporaryDirectory() as folder, patch("player.playback_controller.PlaybackController.launch_worker"):
        window = MainWindow(Path(folder))
        window.language_selector.setCurrentIndex(window.language_selector.findData(args.language))
        window.controller.ready = True
        window.resize(args.width, args.height)
        index = window.song_selector.findData(args.song)
        if index < 0:
            raise ValueError(f"Unknown song: {args.song}")
        window.song_selector.setCurrentIndex(index)
        window.show()
        deadline = time.monotonic() + 4
        while window.plan is None and time.monotonic() < deadline:
            application.processEvents()
            time.sleep(0.01)
        if window.plan is None:
            raise RuntimeError("Preview parser did not finish")
        application.processEvents()
        window.status.setText(window.t("ready"))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        window.grab().save(str(args.output))
        print(f"Preview {window.width()}x{window.height()}: {args.output}")
        window.close()
        application.processEvents()
