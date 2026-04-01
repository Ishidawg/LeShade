from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)

from PySide6.QtCore import Qt


class PageDX8(QWidget):
    def __init__(self, game_param: str | None = None):
        super().__init__()

        self.clipboard = QApplication.clipboard()
        # game_name: str = game_name_param if game_name_param else "Your game"

        self.game_name: str | None = game_param

        # create layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout_steam = QHBoxLayout()
        layout_other = QHBoxLayout()

        layout_steam.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout_other.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Set style
        style_code = "color: #E83C91; padding: 5px; font-style: italic;"
        style_font = "font 12pt; font-weight: 600; padding: 5px; margin: 5px;"

        # create widgets
        label_description = QLabel(
            f"<html><strong>{self.game_name}</strong> uses Direct3D 8.0 as rendering api, so you need to set environment varibles on steam, heroic games or whatever the launcher you use. If your game is on steam, you just need to set the command bellow as launch options.</hmtl>")
        label_description.setStyleSheet("font-size: 12pt; font-weight: 100")
        label_description.setWordWrap(True)
        label_description.setAlignment(Qt.AlignmentFlag.AlignJustify)

        self.steam_command = QLabel(
            f"<html><strong>Steam: <span style='{style_code}'>WINEDLLOVERRIDES='d3d8=n,b' %command%</span></strong></html>")
        self.steam_command.setStyleSheet(style_font)
        self.other_command = QLabel(
            f"<html><strong>Other: <span style='{style_code}'>WINEDLLOVERRIDES=d3d8=n,b</span></strong></html>")
        self.other_command.setStyleSheet(style_font)

        self.btn_steam = QPushButton("Steam copy")
        self.btn_other = QPushButton("Other copy")

        self.btn_steam.clicked.connect(lambda: self.copy_command(True))
        self.btn_other.clicked.connect(lambda: self.copy_command(False))

        # add widgets
        layout.addWidget(label_description)
        layout.addSpacing(12)

        layout_steam.addWidget(self.steam_command)
        layout_steam.addWidget(self.btn_steam)

        layout_other.addWidget(self.other_command)
        layout_other.addWidget(self.btn_other)

        layout.addLayout(layout_steam)
        layout.addLayout(layout_other)

        self.setLayout(layout)

    def copy_command(self, is_steam: bool) -> None:
        if is_steam:
            self.clipboard.setText("WINEDLLOVERRIDES='d3d8=n,b' %command%")
        else:
            self.clipboard.setText("WINEDLLOVERRIDES=d3d8=n,b")
