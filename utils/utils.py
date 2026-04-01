import os
import urllib.request
import ssl
import certifi

from PySide6.QtCore import QStandardPaths

CACHE_PATH: str = QStandardPaths.writableLocation(
    QStandardPaths.StandardLocation.CacheLocation)
EXTRACT_PATH: str = os.path.join(CACHE_PATH, "reshade_extracted")


def generic_download(url: str, directory: str) -> None:
    context: ssl.SSLContext = ssl.create_default_context(
        cafile=certifi.where())
    req: urllib.request.Request = urllib.request.Request(
        url, headers={'User-Agent': 'Chrome/120.0.0.0'})

    try:
        with urllib.request.urlopen(req, context=context) as res:
            with open(directory, "wb") as file:
                file.write(res.read())
    except Exception as e:
        raise IOError(f"Failed to download: {e}") from e


def format_game_name(game_dir: str) -> str:
    game_base_name = os.path.basename(game_dir)
    game_name = os.path.splitext(game_base_name)[0]
    return game_name
