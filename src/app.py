#!/usr/bin/env python3

import os
import sys
import signal
from importlib.resources import files
from importlib.resources.abc import Traversable

from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlApplicationEngine

def main():
    app: QGuiApplication = QGuiApplication(sys.argv)
    engine: QQmlApplicationEngine = QQmlApplicationEngine()

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    if not os.environ.get("QT_QUICK_CONTROLS_STYLE"):
        os.environ["QT_QUICK_CONTROLS_STYLE"] = "org.kde.desktop"

    base_path: Traversable = files('LeShade').joinpath('qml', 'Main.qml')
    url: str = (str(base_path))
    engine.load(url)

    app.exec()

    if __name__ == "__main__":
        main()
