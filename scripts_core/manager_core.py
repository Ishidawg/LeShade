import json
import os

from PySide6.QtCore import QStandardPaths

HOME_PATH = QStandardPaths.writableLocation(
    QStandardPaths.StandardLocation.HomeLocation)
LESHADE_PATH = os.path.join(HOME_PATH, ".leshade")
MANAGER_PATH = os.path.join(LESHADE_PATH, "manager.json")

os.makedirs(LESHADE_PATH, exist_ok=True)


def create_manager():
    try:
        open(MANAGER_PATH, "x")
    except FileExistsError as e:
        print(e)


def add_game(game_name, game_path):
    current_data = []
    game_name = format_game_name(game_name)

    if os.path.exists(MANAGER_PATH):
        try:
            with open(MANAGER_PATH, "r") as file:
                current_data = json.load(file)

                if not isinstance(current_data, list):
                    current_data = [current_data] if current_data else []
        except Exception as e:
            print(e)
            current_data = []

    new_entry = {
        "game": game_name,
        "dir": game_path
    }

    if new_entry not in current_data:
        current_data.append(new_entry)

    with open(MANAGER_PATH, "w") as file:
        json.dump(current_data, file, indent=4)


def format_game_name(game_name):
    game_basename = os.path.basename(game_name)
    game_name = os.path.splitext(game_basename)[0]
    return game_name
