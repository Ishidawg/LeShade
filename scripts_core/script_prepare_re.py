import os
from zipfile import BadZipfile, ZipFile

from utils.utils import EXTRACT_PATH

# Prepare reshade will contains any functions to help script_download_.re.py


def unzip_reshade(reshade_path: str) -> None:
    os.makedirs(EXTRACT_PATH, exist_ok=True)

    try:
        with ZipFile(reshade_path, "r") as zip_file:
            zip_file.extractall(EXTRACT_PATH)
    except Exception as e:
        raise BadZipfile(f"Failed to unzip: {e}")
