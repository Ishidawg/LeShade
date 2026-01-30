import os
import shutil

from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from PySide6.QtCore import Qt

import scripts_core.manager_core

# l:    label
# c:    container
# ly:   layout
# b:    button
# p:    progress


class UninstallWidget(QWidget):

    def __init__(self):
        super().__init__()

        ly = QVBoxLayout()
        ly.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Subtitle
        l_subtitle = QLabel("Select a game and click uninstall")
        l_subtitle.setStyleSheet("font-size: 12pt; font-weight: 100;")
        l_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l_subtitle.setMargin(15)

        # List stuff
        self.games = scripts_core.manager_core.read_manager_content("game")
        self.games_dir = scripts_core.manager_core.read_manager_content("dir")

        self.game_list = QListWidget(self)
        self.add_items(self.games, self.game_list)
        # Button
        self.b_uninstall = QPushButton("Uninstall")
        self.b_uninstall.clicked.connect(
            lambda: self.uninstall_reshade(self.game_list, self.games_dir))

        # Add Widgets
        ly.addWidget(l_subtitle)
        ly.addSpacing(5)
        ly.addWidget(self.game_list)
        ly.addWidget(self.b_uninstall)

        self.setLayout(ly)

    def add_items(self, games, widget_list):
        index = 1

        for game in games:
            newItem = QListWidgetItem()
            newItem.setText(game)
            widget_list.insertItem(index, newItem)

            index = index + 1

    def uninstall_reshade(self, widget_list, dir_list):
        # current_game = widget_list.currentItem().text()

        try:
            current_row = widget_list.currentRow()
            game_path = dir_list[current_row]

            # Remove files and directories
            shutil.rmtree(f"{game_path}/Textures")
            shutil.rmtree(f"{game_path}/Shaders")

            # Remove game form list
            widget_list.takeItem(current_row)

            # Update manager.json
            scripts_core.manager_core.update_manager(current_row)

            print(current_row)
            print(game_path)
        except IndexError as e:
            print(e)
