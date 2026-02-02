import os
import glob
from pathlib import Path
from PySide6.QtCore import (
    QObject,
    QStandardPaths,
    Signal
)

import urllib.request
import ssl
import certifi

# URL examples
# https://reshade.me/downloads/ReShade_Setup_6.7.1.exe
# https://reshade.me/downloads/ReShade_Setup_6.7.1_Addon.exe

PATTERN: str = "ReShade_Setup*.exe"
DOWNLOAD_PATH: str = QStandardPaths.writableLocation(
    QStandardPaths.StandardLocation.DownloadLocation)
CACHE_PATH: str = QStandardPaths.writableLocation(
    QStandardPaths.StandardLocation.CacheLocation)


class DownloadWorker(QObject):
    reshade_found: Signal = Signal(bool)
    reshade_error: Signal = Signal(str)

    def __init__(self, version: str, release: str):
        super().__init__()
        self.local_reshade: list[str] = []

        self.reshade_url: str = ''

        self.version: str | None = version
        self.release: str | None = release

        self.reshade_dir: str = ''
        self.perhaps_dir: str = ''

        self.build_url()

    def run(self) -> None:
        self.search_reshade_on_download_dir()
        self.perhaps_dir = self.prevent_download()

        if self.perhaps_dir in self.local_reshade:
            self.reshade_dir = self.find_reshade()
            self.reshade_found.emit(True)

        if not self.reshade_dir:
            self.download_reshade()
            self.reshade_dir = self.find_reshade()
            self.reshade_found.emit(True)
        elif self.reshade_dir:
            if self.perhaps_dir not in self.local_reshade:
                self.download_reshade()
                self.reshade_dir = self.find_reshade()
                self.reshade_found.emit(True)
        else:
            self.reshade_error.emit("Reshade was not found")

        # debug matters
        print(f"dir: {self.reshade_dir.split("/")[-1]}")
        print(f"url: {self.reshade_url.split("/")[-1]}")

    def build_url(self) -> None:
        try:
            if self.version == "addon":
                self.reshade_url = f"https://reshade.me/downloads/ReShade_Setup_{self.release}_Addon.exe"
            else:
                self.reshade_url = f"https://reshade.me/downloads/ReShade_Setup_{self.release}.exe"
        except Exception as e:
            raise RuntimeError(f"Failed to build url: {e}") from e

    def prevent_download(self) -> str:
        file_name: str = self.reshade_url.split("/")[-1]
        perhaps_dir: str = os.path.join(DOWNLOAD_PATH, file_name)

        return perhaps_dir

    def search_reshade_on_download_dir(self) -> None:
        self.local_reshade = glob.glob(os.path.join(
            DOWNLOAD_PATH, PATTERN), recursive=True)

    def find_reshade(self) -> str:
        matches: list[Path] = []
        file_name: str = self.reshade_url.split("/")[-1]

        try:
            matches = list(Path(DOWNLOAD_PATH).rglob(file_name))
        except Exception as e:
            raise OSError(f"Failed to find ReShade: {e}") from e

        return str(matches[0])

    def download_reshade(self) -> None:
        if self.reshade_url != "":
            try:
                file_name: str = self.reshade_url.split('/')[-1]
                directory: str = os.path.join(DOWNLOAD_PATH, file_name)

                context: ssl.SSLContext = ssl.create_default_context(
                    cafile=certifi.where())
                req: urllib.request.Request = urllib.request.Request(self.reshade_url, headers={
                    'User-Agent': 'Chrome/120.0.0.0'})

                with urllib.request.urlopen(req, context=context) as res:
                    with open(directory, "wb") as file:
                        file.write(res.read())
            except Exception as e:
                raise IOError(f"Failed to download: {e}") from e
