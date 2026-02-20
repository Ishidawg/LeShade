import shutil
import os

from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget
)

from PySide6.QtCore import Qt
from scripts_core.script_manager import read_hlsl_flag, update_manager, read_manager_content


class PageUninstall(QWidget):

    def __init__(self):
        super().__init__()

        self.games: list[str] = read_manager_content("game")
        self.games_dir: list[str] = read_manager_content("dir")

        # create layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # create widgets
        label_description = QLabel("Select a game and click uninstall")
        label_description.setStyleSheet("font-size: 12pt; font-weight: 100")
        label_description.setWordWrap(True)

        self.game_list = QListWidget(self)
        self.add_items(self.games, self.game_list)

        self.btn_uninstall = QPushButton("Uninstall")

        self.btn_uninstall.clicked.connect(self.on_uninstall_clicked)

        # add widgets
        layout.addWidget(label_description)
        layout.addWidget(self.game_list)
        layout.addWidget(self.btn_uninstall)
        self.setLayout(layout)

    def on_uninstall_clicked(self) -> None:
        self.uninstall_reshade(self.game_list, self.games_dir)

    def add_items(self, games: list[str], widget_list: QListWidget):
        index: int = 1

        for game in games:
            newItem: QListWidgetItem = QListWidgetItem()
            newItem.setText(game)
            widget_list.insertItem(index, newItem)

            index = index + 1

    def uninstall_reshade(self, widget_list: QListWidget, dir_list: list[str]):
        try:
            current_row: int = widget_list.currentRow()
            game_path: str = dir_list[current_row]

            shaders_dir: str = os.path.join(game_path, "reshade-shaders")

            have_hlsl_compiler: str = read_hlsl_flag(
                current_row, "hlsl_compiler")

            files_tbr: list[str] = ["opengl32.dll", "d3d8.dll", "d3d9.dll", "d3d10.dll", "d3d11.dll", "dxgi.dll",
                                    "" if have_hlsl_compiler else "d3dcompiler_47.dll", "ReShade.ini", "ReShade.log", "ReShadePreset.ini", "ReShade*", "reshade*"]

            if os.path.exists(shaders_dir):
                shutil.rmtree(shaders_dir)

            for file in files_tbr:
                if file in os.listdir(game_path):
                    os.remove(os.path.join(game_path, file))

            # Remove game from list and reset
            widget_list.takeItem(current_row)
            widget_list.updateEditorData()
            widget_list.update()
            widget_list.reset()

            # update the values so we can get the correct game_path
            update_manager(current_row)
            self.games = read_manager_content("game")
            self.games_dir = read_manager_content("dir")
        except IndexError as e:
            print(e)
