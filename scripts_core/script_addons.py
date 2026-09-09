import configparser
import os
import shutil
from PySide6.QtCore import QStandardPaths
from utils.utils import generic_download, unzip_file

ADDONS_URL = "https://raw.githubusercontent.com/crosire/reshade-shaders/list/Addons.ini"


def get_addons_cache_dir() -> str:
    cache_base = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.CacheLocation
    )
    cache_dir = os.path.join(cache_base, "leshade")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def fetch_addons(is_64bit: bool = True, use_cache: bool = True) -> list[dict]:
    """
    Downloads and parses the official ReShade Addons.ini list.
    Caches the file locally in ~/.cache/leshade/Addons.ini.
    Resolves the appropriate download URL according to is_64bit.
    """
    cache_file = os.path.join(get_addons_cache_dir(), "Addons.ini")
    content = ""

    try:
        content = generic_download(ADDONS_URL, None, timeout=10) or ""
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception:
            pass
    except Exception:
        if use_cache and os.path.isfile(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                content = ""

    addons = []
    if content:
        config = configparser.ConfigParser(interpolation=None)
        config.read_string(content)
        for sec in config.sections():
            name = config.get(sec, "PackageName", fallback="").strip()
            if not name:
                continue

            desc = config.get(sec, "PackageDescription", fallback="").strip()
            repo_url = config.get(sec, "RepositoryUrl", fallback="").strip()
            effect_path = config.get(sec, "EffectInstallPath", fallback="").strip()

            url = config.get(sec, "DownloadUrl", fallback="").strip()
            if not url:
                if is_64bit:
                    url = config.get(sec, "DownloadUrl64", fallback="").strip()
                else:
                    url = config.get(sec, "DownloadUrl32", fallback="").strip()

            if not url:
                continue

            addons.append({
                "id": sec,
                "name": name,
                "description": desc,
                "download_url": url,
                "repository_url": repo_url,
                "effect_install_path": effect_path,
                "enabled": False,
            })

    return addons


def install_addon(addon: dict, game_dir: str, temp_dir: str) -> None:
    """
    Downloads and installs a single ReShade addon to game_dir.
    Handles .addon, .addon32, .addon64, and .zip archives.
    """
    url = addon.get("download_url", "")
    if not url:
        return

    os.makedirs(temp_dir, exist_ok=True)
    filename = url.split("/")[-1].split("?")[0]
    download_path = os.path.join(temp_dir, filename)

    generic_download(url, download_path)

    ext = os.path.splitext(filename)[1].lower()
    if ext in {".addon", ".addon32", ".addon64"}:
        shutil.copy2(download_path, os.path.join(game_dir, filename))
    elif ext == ".zip":
        extract_path = os.path.join(temp_dir, f"addon_{addon.get('id', 'pkg')}")
        os.makedirs(extract_path, exist_ok=True)
        unzip_file(download_path, extract_path)

        for root, _, files in os.walk(extract_path):
            for f in files:
                f_ext = os.path.splitext(f)[1].lower()
                if f_ext in {".addon", ".addon32", ".addon64"}:
                    shutil.copy2(os.path.join(root, f), os.path.join(game_dir, f))
