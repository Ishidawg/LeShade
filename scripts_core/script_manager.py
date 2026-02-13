import json
import os

from pathlib import Path

from PySide6.QtCore import QStandardPaths

from utils.utils import format_game_name

CONFIG_PATH = QStandardPaths.writableLocation(
    QStandardPaths.StandardLocation.ConfigLocation)
LESHADE_PATH = os.path.join(CONFIG_PATH, "leshade")
MANAGER_PATH = os.path.join(LESHADE_PATH, "manager.json")

os.makedirs(LESHADE_PATH, exist_ok=True)


def create_manager() -> None:
    if not Path(MANAGER_PATH).exists():
        try:
            with open(MANAGER_PATH, "w") as file:
                file.write("[]")
        except FileExistsError as e:
            print(e)


def add_game(game_dir: str) -> None:
    current_data: list[dict] = []
    game_name: str = format_game_name(game_dir)

    if os.path.exists(MANAGER_PATH):
        try:
            with open(MANAGER_PATH, "r") as file:
                current_data = json.load(file)

        except Exception as e:
            print(e)
            current_data = []

    new_entry: dict = {
        "game": game_name,
        "dir": game_dir
    }

    if new_entry not in current_data:
        current_data.append(new_entry)

    with open(MANAGER_PATH, "w") as file:
        json.dump(current_data, file, indent=4)


def read_manager_content(key: str) -> list[str]:
    game_content: list[str] = []

    create_manager()

    with open(MANAGER_PATH, "r") as file:
        current_file: tuple = json.load(file)

    for item in current_file:
        game_content.append(item.get(key))

    return game_content


def update_manager(index) -> None:
    new_data: list[str] = []

    with open(MANAGER_PATH, "r") as file:
        current_file = json.load(file)

    for game in current_file:
        new_data.append(game)

    new_data.remove(new_data[index])

    with open(MANAGER_PATH, "w") as file:
        json.dump(new_data, file, indent=4)
