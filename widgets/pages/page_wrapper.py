from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)
from PySide6.QtCore import Qt


class PageWrapper(QWidget):
    def __init__(self, game_name: str, description_text: str, steam_text: str, other_text: str, steam_cmd: str, other_cmd: str):
        super().__init__()

        self.clipboard = QApplication.clipboard()

        self.game_name: str = game_name

        # create layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout_steam = QHBoxLayout()
        layout_other = QHBoxLayout()

        layout_steam.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout_other.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # create widgets
        label_description = QLabel(
            f'<html><strong>{game_name}</strong></html>' + description_text)
        label_description.setStyleSheet("font-size: 12pt; font-weight: 100")
        label_description.setWordWrap(True)
        label_description.setAlignment(Qt.AlignmentFlag.AlignJustify)

        self.steam_command = QLabel(steam_text)
        self.other_command = QLabel(other_text)

        self.btn_steam = QPushButton("Steam copy")
        self.btn_other = QPushButton("Other copy")

        self.btn_steam.clicked.connect(
            lambda: self.copy_command(True, steam_cmd))
        self.btn_other.clicked.connect(
            lambda: self.copy_command(False, other_cmd))

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

    def copy_command(self, is_steam: bool, command: str) -> None:
        if is_steam:
            self.clipboard.setText(command)
        else:
            self.clipboard.setText(command)
