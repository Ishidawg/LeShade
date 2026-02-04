import os
from PySide6.QtCore import QStandardPaths
from zipfile import BadZipfile, ZipFile

CACHE_PATH: str = QStandardPaths.writableLocation(
    QStandardPaths.StandardLocation.CacheLocation)
EXTRACT_PATH: str = os.path.join(CACHE_PATH, "reshade_extracted")

# Prepare reshade will contains any functions to help script_download_.re.py


def unzip_reshade(reshade_path: str) -> None:
    os.makedirs(EXTRACT_PATH, exist_ok=True)

    try:
        with ZipFile(reshade_path, "r") as zip_file:
            zip_file.extractall(EXTRACT_PATH)
    except Exception as e:
        raise BadZipfile(f"Failed to unzip: {e}")
