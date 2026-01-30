from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton
)

from PySide6.QtCore import Qt, Slot


class WrapperWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.clipboard = QApplication.clipboard()

        ly = QVBoxLayout()
        ly.setAlignment(Qt.AlignmentFlag.AlignCenter)

        ly_steam_command = QHBoxLayout()
        ly_steam_command.setAlignment(Qt.AlignmentFlag.AlignLeft)

        ly_other_command = QHBoxLayout()
        ly_other_command.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Description
        l_description = QLabel(
            "As you are installing reshade on a DirectX 8.0 game, you need to set environment variables on steam  or heroic games launcher.")
        l_description.setAlignment(Qt.AlignmentFlag.AlignJustify)
        l_description.setWordWrap(True)

        # CSS style to command label
        # Yellow = FACE68
        s_code = "color: #E83C91; padding: 5px; font-style: italic;"
        s_font = "font 12pt; font-weight: 600; padding: 5px; margin: 5px;"

        # Command widget
        self.l_steam_command = QLabel(
            f"<html><strong>Steam: <span style='{s_code}'>WINEDLLOVERRIDES='d3d8=n,b' %command%</span></strong></html>")
        self.l_steam_command.setStyleSheet(s_font)
        self.l_steam_command.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.l_other_command = QLabel(
            f"<html><strong>Other: <span style='{s_code}'>WINEDLLOVERRIDES=d3d8=n,b</span></strong></html>")
        self.l_other_command.setStyleSheet(s_font)
        self.l_other_command.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Buttons
        self.b_steam = QPushButton("Copy steam")
        self.b_other = QPushButton("Copy other")

        # Connect Functions
        self.b_steam.clicked.connect(self.copy_steam)
        self.b_other.clicked.connect(self.copy_other)

        # Add widgets
        ly.addWidget(l_description)
        ly.addSpacing(5)

        ly_steam_command.addWidget(self.l_steam_command)
        ly_steam_command.addWidget(self.b_steam)

        ly_other_command.addWidget(self.l_other_command)
        ly_other_command.addWidget(self.b_other)

        ly.addLayout(ly_steam_command)
        ly.addLayout(ly_other_command)

        self.setLayout(ly)

    # Functions to copy commands to clipboard
    @Slot()
    def copy_steam(self):
        self.clipboard.setText("WINEDLLOVERRIDES='d3d8=n,b' %command%")

    @Slot()
    def copy_other(self):
        self.clipboard.setText("WINEDLLOVERRIDES=d3d8=n,b")
