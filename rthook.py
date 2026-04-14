import os
import sys
from pathlib import Path

base_path = Path(sys._MEIPASS)
plugins_path = str(base_path / "PySide6" / "Qt" / "plugins")

os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = plugins_path
os.environ["QT_QPA_PLATFORMTHEME"] = "xdgdesktopportal"
