import sys
import os
import struct

from PySide6.QtWidgets import (
  QApplication,
  QLabel,
  QMainWindow,
  QVBoxLayout,
  QHBoxLayout,
  QWidget
)

from PySide6.QtCore import Qt

class WrapperWidget(QWidget):

  def __init__(self):
    super().__init__()

    ly = QVBoxLayout()
    ly.setAlignment(Qt.AlignTop | Qt.AlignmentFlag.AlignCenter)

    # Description
    # l_description = QLabel("As you are installing reshade on a Direct3D 8.0 game, please add the command bellow to your environment variables or steam launch options.")
    l_description = QLabel("As you are installing reshade on a DirectX 8.0 game, you need to set environment variables on steam  or heroic games launcher.")
    l_description.setAlignment(Qt.AlignmentFlag.AlignJustify)
    l_description.setWordWrap(True)

    # CSS style to command label
    s_code = "background-color: #2b2b2b; color: #ffffff; padding: 5px;"
    s_font = "font 12pt; font-weight: 600; padding: 5px"

    # Command widget
    self.l_steam_command = QLabel(f"<html>Steam: <span style='{s_code}'>WINEDLLOVERRIDES='d3d8=n,b' %command%</span></html>")
    self.l_steam_command.setStyleSheet(s_font)
    self.l_steam_command.setAlignment(Qt.AlignmentFlag.AlignLeft)

    self.l_other_command = QLabel(f"<html>Other: <span style='{s_code}'>WINEDLLOVERRIDES='d3d8=n,b</span></html>")
    self.l_other_command.setStyleSheet(s_font)
    self.l_other_command.setAlignment(Qt.AlignmentFlag.AlignLeft)


    # Add widgets
    ly.addWidget(l_description)
    ly.addSpacing(5)
    ly.addWidget(self.l_steam_command)
    ly.addSpacing(5)
    ly.addWidget(self.l_other_command)

    self.setLayout(ly)
