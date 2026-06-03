import glob
import os
from pathlib import Path

from PySide6.QtCore import QObject, QStandardPaths, Signal

from utils.utils import (
    EXTRACT_PATH,
    download_nightly,
    extract_nightly,
    generic_download,
    get_reshade_tags,
    make_extract_dir,
    unzip_file,
)

# URL examples
# https://reshade.me/downloads/ReShade_Setup_6.7.1.exe
# https://reshade.me/downloads/ReShade_Setup_6.7.1_Addon.exe

# Nightly build urls are from nightly.link

PATTERN: str = "ReShade_Setup*.exe"
DOWNLOAD_PATH: str = QStandardPaths.writableLocation(
    QStandardPaths.StandardLocation.DownloadLocation
)


class DownloadWorker(QObject):
    reshade_found: Signal = Signal(bool)
    reshade_status: Signal = Signal(str)

    def __init__(self, version: str | None = None, release: str | None = None):
        super().__init__()
        self.local_reshade: list[str] = []

        self.reshade_url: str = ""
        self.nightly_url: list[str] = []

        self.version: str | None = version
        self.release: str | None = release

        self.reshade_dir: str = ""
        self.perhaps_dir: str = ""

        self.build_url()

    def run(self) -> None:
        make_extract_dir()
        self.search_reshade_on_download_dir()
        self.perhaps_dir = self.prevent_download()

        self.ensure_reshade()

    def build_url(self) -> None:
        try:
            if self.release == "nightly":
                tags = get_reshade_tags(None)
                latest_tag = tags[0] if tags else "6.7.3"  # HARDCODE a version

                self.reshade_url = (
                    f"https://reshade.me/downloads/ReShade_Setup_{latest_tag}_Addon.exe"
                )
                self.nightly_urls = [
                    "https://nightly.link/crosire/reshade/workflows/build/main/ReShade%20%2864-bit%29.zip",
                    "https://nightly.link/crosire/reshade/workflows/build/main/ReShade%20%2832-bit%29.zip",
                ]
                return

            if self.version == "addon":
                self.reshade_url = f"https://reshade.me/downloads/ReShade_Setup_{self.release}_Addon.exe"
            else:
                self.reshade_url = (
                    f"https://reshade.me/downloads/ReShade_Setup_{self.release}.exe"
                )
        except Exception as e:
            raise RuntimeError(f"Failed to build url: {e}") from e

    def ensure_reshade(self) -> None:
        if self.perhaps_dir in self.local_reshade:
            self.update_status(False, True, "Reshade already downloaded!")
            return

        if not self.reshade_dir:
            self.update_status(True, True, "Reshade downloaded!")
            return

        if self.reshade_dir and self.perhaps_dir not in self.local_reshade:
            self.update_status(True, True, "Reshade downloaded!")
        else:
            self.update_status(False, False, "Reshade was not found!")

    def update_status(self, download: bool, found: bool, message: str) -> None:
        if download:
            self.reshade_status.emit("Downloading...")
            self.download_reshade()

        self.reshade_dir = self.find_reshade()
        self.reshade_status.emit(message)
        self.reshade_found.emit(found)

        if found:
            self.unzip_reshade()

    def unzip_reshade(self) -> None:
        unzip_file(self.reshade_dir, EXTRACT_PATH)

        if self.release == "nightly":
            extract_nightly(self.nightly_urls, DOWNLOAD_PATH, EXTRACT_PATH)

    def prevent_download(self) -> str:
        file_name: str = self.reshade_url.split("/")[-1]
        perhaps_dir: str = os.path.join(DOWNLOAD_PATH, file_name)

        return perhaps_dir

    def search_reshade_on_download_dir(self) -> None:
        self.local_reshade = glob.glob(
            os.path.join(DOWNLOAD_PATH, PATTERN), recursive=True
        )

    def find_reshade(self) -> str:
        matches: list[Path] = []
        file_name: str = self.reshade_url.split("/")[-1]

        try:
            matches = list(Path(DOWNLOAD_PATH).rglob(file_name))
        except Exception as e:
            raise OSError(f"Failed to find ReShade: {e}") from e

        return str(matches[0])

    def download_reshade(self) -> None:
        if self.reshade_url:
            try:
                file_name: str = self.reshade_url.split("/")[-1]
                directory: str = os.path.join(DOWNLOAD_PATH, file_name)

                generic_download(self.reshade_url, directory)

                if self.release == "nightly":
                    self.reshade_status.emit("Downloading nightly dll")
                    download_nightly(self.nightly_url, DOWNLOAD_PATH)
            except Exception as e:
                raise IOError(f"Failed to download: {e}") from e
