import os
import re
import urllib.request
import ssl
import certifi
from typing import Any
import requests

from PySide6.QtCore import QStandardPaths

CACHE_PATH: str = QStandardPaths.writableLocation(
    QStandardPaths.StandardLocation.CacheLocation)
EXTRACT_PATH: str = os.path.join(CACHE_PATH, "reshade_extracted")
TAGS_URL: str = "https://github.com/crosire/reshade/tags"
RENODX_SNAPSHOT_URL: str = "https://api.github.com/repos/clshortfuse/renodx/releases/tags/snapshot"


def generic_download(url: str, directory: str | None) -> None | str:
    context: ssl.SSLContext = ssl.create_default_context(
        cafile=certifi.where())
    req: urllib.request.Request = urllib.request.Request(
        url, headers={'User-Agent': 'Chrome/120.0.0.0'})

    try:
        with urllib.request.urlopen(req, context=context) as res:
            if directory:
                with open(directory, "wb") as file:
                    file.write(res.read())
            else:
                # If no directory was provided, we want the page's HTML decoded as text
                return res.read().decode('utf-8')
    except Exception as e:
        raise IOError(f"Failed to download: {e}") from e


def format_game_name(game_dir: str) -> str:
    game_base_name = os.path.basename(game_dir)
    game_name = os.path.splitext(game_base_name)[0]
    return game_name


def get_reshade_tags(after: str | None) -> list[str] | None:
    try:
        if after:
            # Other pages
            tag_page: str | None = generic_download(
                f"{TAGS_URL}?after=v{after}", None)
        else:
            # First page
            tag_page: str | None = generic_download(TAGS_URL, None)

        return re.findall(r'(?<=releases/tag/v)[0-9.]+', str(tag_page))
    except IOError:
        return None


def get_renodx_assets() -> list[str] | None:
    renodx_response: requests.Request.data = requests.get(RENODX_SNAPSHOT_URL)
    assets_names: list[str] = ["None"]

    try:
        if renodx_response.status_code == 200:
            release: dict[str, Any] = renodx_response.json()
            assets: list[dict[str, Any]] = release.get("assets", [])

            for asset in assets:
                assets_names.append(asset["name"])

            return assets_names

    except Exception as e:
        raise requests.RequestException(f"Failed to fetch assets: {e}") from e
