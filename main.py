"""Piano Player entry point."""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from app.main_window import MainWindow
from app.branding import APP_ICON, APP_ID, APP_NAME


def main() -> int:
    root = Path(__file__).resolve().parent
    (root / "logs").mkdir(exist_ok=True)
    handler = RotatingFileHandler(root / "logs/app.log", maxBytes=1_000_000,
                                 backupCount=2, encoding="utf-8")
    logging.basicConfig(level=logging.INFO, handlers=[handler],
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.info("Application start; Python %s", sys.version)
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
    application = QApplication(sys.argv)
    application.setApplicationName(APP_NAME)
    application.setApplicationDisplayName(APP_NAME)
    application.setWindowIcon(QIcon(str(APP_ICON)))
    window = MainWindow(root)
    window.show()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
