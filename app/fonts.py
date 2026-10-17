"""Make Windows' CJK fonts available even with Qt's offscreen renderer."""
from functools import lru_cache
import os
from pathlib import Path
from PySide6.QtGui import QFontDatabase


@lru_cache(maxsize=1)
def ensure_fonts():
    directory = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
    for filename in ("segoeui.ttf", "segoeuib.ttf", "consola.ttf", "YuGothR.ttc", "YuGothB.ttc",
                     "malgun.ttf", "malgunbd.ttf", "msyh.ttc", "msyhbd.ttc"):
        path = directory / filename
        if path.is_file():
            QFontDatabase.addApplicationFont(str(path))
