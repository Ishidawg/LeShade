import json
import os
import re
import shutil
import ssl
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Match
from zipfile import BadZipfile, ZipFile

import certifi
from PySide6.QtCore import QStandardPaths
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QMessageBox, QWidget

CACHE_PATH: str = QStandardPaths.writableLocation(
    QStandardPaths.StandardLocation.CacheLocation
)
EXTRACT_PATH: str = os.path.join(CACHE_PATH, "reshade_extracted")
TAGS_URL: str = "https://github.com/crosire/reshade/tags"
RENODX_SNAPSHOT_URL: str = (
    "https://api.github.com/repos/clshortfuse/renodx/releases/tags/snapshot"
)


def make_extract_dir() -> None:
    os.makedirs(EXTRACT_PATH, exist_ok=True)


def dialog_box(
    parent: QWidget,
    title: str,
    icon: QMessageBox.Icon,
    text: str,
    info_text: str,
    buttons: bool,
) -> bool:
    dialog = QMessageBox(parent)
    dialog.setWindowModality(Qt.WindowModality.WindowModal)
    dialog.setWindowTitle(title)
    dialog.setIcon(icon)
    dialog.setText(text)
    dialog.setInformativeText(info_text)

    if buttons:
        dialog.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        button = dialog.exec()

        if button == QMessageBox.StandardButton.No:
            return False
    else:
        dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        dialog.exec()

    return True


def get_wine_command() -> list[str]:
    # I want to priorize native wine
    if not os.path.exists("/.flatpak-info"):
        if shutil.which("wine") is not None:
            return ["wine"]
        else:
            return ["flatpak", "run", "org.winehq.Wine"]
    else:
        if (
            subprocess.run(
                ["flatpak-spawn", "--host", "wine", "--version"], capture_output=True
            ).returncode
            == 0
        ):
            return ["flatpak-spawn", "--host", "wine"]
        else:
            return ["flatpak-spawn", "--host", "flatpak", "run", "org.winehq.Wine"]


def get_game_directory_name(executable_path: Path) -> str:
    split_path: tuple[str, ...] = executable_path.parts

    if "common" in split_path:
        common_index: int = split_path.index("common")
        if common_index + 1 < len(split_path):
            # Game directory (ex: DARK SOULS REMASTERED)
            return split_path[common_index + 1]

    parent: Path = executable_path.parent

    # Some games that uses unreal (or other GE), they have the executable into bin directory...
    probably_directories: set[str] = {
        "bin",
        "x64",
        "x86",
        "win64",
        "win32",
        "system32",
        "release",
    }
    if parent.name.lower() in probably_directories and parent.parent:
        return parent.parent.name

    return parent.name


# Can be steamapps or drive_c (for non-steam games)
def get_gamebase_directory(executable_path: Path, is_steam: bool) -> str:
    game_base: str = ""

    for parent in executable_path.parents:
        if is_steam:
            if parent.name == "steamapps":
                game_base = str(parent)
                break
        else:
            if parent.name == "drive_c":
                game_base = str(parent)
                break

    if not game_base:
        raise ValueError("Error: steamapps dir was not found")

    return game_base


def unzip_file(src_file: str, destination_path: str) -> None:
    try:
        with ZipFile(src_file, "r") as zip_file:
            zip_file.extractall(destination_path)
    except Exception as e:
        raise BadZipfile(f"Failed to unzip: {e}")


def get_steam_appid(steamapps_dir: str, game_name: str) -> str:
    app_manifest_pattern: str = "appmanifest_*acf"
    app_manifest_regex: str = r"appmanifest_(\d+)\.acf"
    app_id: str = ""

    for manifest_file in Path(steamapps_dir).glob(app_manifest_pattern):
        try:
            manifest_data: str = manifest_file.read_text(encoding="utf-8")
            pattern: str = rf'"installdir"\s+"{re.escape(game_name)}"'

            if re.search(pattern, manifest_data, re.IGNORECASE):
                match: Match[str] | None = re.search(
                    app_manifest_regex, manifest_file.name
                )

                if match:
                    app_id = match.group(1)
                    break
        except Exception as e:
            raise Exception(f"Error getting the app_id: {e}")

    if not app_id:
        raise ValueError("Error: app_id is empty")

    return app_id


def download(
    url: str, game_path: str = "", game_arch: str = "", file_name: str = ""
) -> None | bool:
    file_path: str = os.path.join(game_path, file_name)

    if Path(file_path).exists():
        print(
            f"Game folder already has the {file_name}. For safety reasons it will not be replaced."
        )

        return True if file_name == "d3dcompiler_47.dll" else None

    if game_arch:
        arch: str = "win64" if game_arch == "64-bit" else "win32"
        furl: str = f"{url}/{arch}/d3dcompiler_47.dll"
        generic_download(furl, file_path)
        return False

    generic_download(url, file_path)


def generic_download(url: str, directory: str | None) -> None | str:
    context: ssl.SSLContext = ssl.create_default_context(cafile=certifi.where())
    req: urllib.request.Request = urllib.request.Request(
        url, headers={"User-Agent": "Chrome/120.0.0.0"}
    )

    try:
        with urllib.request.urlopen(req, context=context) as res:
            if directory:
                with open(directory, "wb") as file:
                    file.write(res.read())
            else:
                # If no directory was provided, we want the page's HTML decoded as text
                return res.read().decode("utf-8")
    except Exception as e:
        raise IOError(f"Failed to download: {e}") from e


# DOWNLOAD_PATH is on script_download_re.py
def download_nightly(nightly_urls: list[str], download_path) -> None:
    for url in nightly_urls:
        file_name: str = urllib.parse.unquote(url.split("/")[-1])
        file_directory: str = os.path.join(download_path, file_name)
        generic_download(url, file_directory)


def extract_nightly(
    nightly_urls: list[str], download_path: str, extract_path: str
) -> None:
    for url in nightly_urls:
        file_name: str = urllib.parse.unquote(url.split("/")[-1])
        zip_path: str = os.path.join(download_path, file_name)

        if os.path.exists(zip_path):
            unzip_file(zip_path, extract_path)


def get_reshade_tags(after: str | None) -> list[str] | None:
    tag_page: str | None = None
    try:
        if after:
            # Other pages
            tag_page = generic_download(f"{TAGS_URL}?after=v{after}", None)
        else:
            # First page
            tag_page = generic_download(TAGS_URL, None)

        return re.findall(r"(?<=releases/tag/v)[0-9.]+", str(tag_page))
    except IOError:
        return None


def get_renodx_assets() -> list[str] | None:
    assets_names: list[str] = ["None"]

    context = ssl.create_default_context(cafile=certifi.where())
    req = urllib.request.Request(
        RENODX_SNAPSHOT_URL,
        headers={"User-Agent": "Chrome/120.0.0", "Accept": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, context=context) as response:
            release: dict[str, Any] = json.loads(response.read())
            assets: list[dict[str, Any]] = release.get("assets", [])

            for asset in assets:
                assets_names.append(asset["name"])

            return assets_names if assets_names else None
    except urllib.error.HTTPError as e:
        raise urllib.error.HTTPError(
            f"Failed to fetch assets: {e.code}. ", e.code, e.msg, e.hdrs, e.fp
        ) from e
    except Exception as e:
        raise RuntimeError(f"Failed to fetch assets: {e}") from e


def get_clean_env() -> dict[str, str]:
    env: dict[str, str] = os.environ.copy()

    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)

    if "LD_LIBRARY_PATH_ORIG" in env:
        env["LD_LIBRARY_PATH"] = env["LD_LIBRARY_PATH_ORIG"]
    elif "APPDIR_ORIG_LD_LIBRARY_PATH" in env:
        env["LD_LIBRARY_PATH"] = env["APPDIR_ORIG_LD_LIBRARY_PATH"]
    else:
        env.pop("LD_LIBRARY_PATH", None)

    return env
