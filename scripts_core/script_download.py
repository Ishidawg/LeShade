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

PATTERN = "ReShade_Setup*.exe"
DOWNLOAD_PATH = QStandardPaths.writableLocation(
    QStandardPaths.StandardLocation.DownloadLocation)
CACHE_PATH = QStandardPaths.writableLocation(
    QStandardPaths.StandardLocation.CacheLocation)


class DownloadWorker(QObject):
    reshade_found = Signal(bool)
    reshade_error = Signal(str)

    def __init__(self, version, release):
        super().__init__()
        self.local_reshade = []

        self.reshade_url = ""
        self.version = version
        self.release = release
        self.reshade_dir = ""
        self.maybe_dir = ""

        self.build_url()
        self.run()

    def run(self):
        self.search_reshade()
        self.maybe_dir = self.prevent_download()
        self.reshade_dir = self.find_reshade()

        if not self.reshade_dir:
            self.download_reshade()
            self.reshade_dir = self.find_reshade()
            self.reshade_found.emit(True)
        elif self.reshade_dir:
            if self.maybe_dir not in self.local_reshade:
                self.download_reshade()
                self.reshade_dir = self.find_reshade()
                self.reshade_found.emit(True)
        else:
            self.reshade_error.emit("Reshade was not found")

    def build_url(self):
        try:
            if self.version == "addon":
                self.reshade_url = f"https://reshade.me/downloads/ReShade_Setup_{self.release}_Addon.exe"
            else:
                self.reshade_url = f"https://reshade.me/downloads/ReShade_Setup_{self.release}.exe"
        except Exception as e:
            print(e)

    def prevent_download(self):
        file_name = self.reshade_url.split("/")[-1]
        maybe_dir = os.path.join(DOWNLOAD_PATH, file_name)

        return maybe_dir

    def search_reshade(self):
        self.local_reshade = glob.glob(os.path.join(
            DOWNLOAD_PATH, PATTERN), recursive=True)
        print(self.local_reshade)

    def find_reshade(self):
        matches = ""

        try:
            matches = list(Path(DOWNLOAD_PATH).rglob(PATTERN))

        except Exception as e:
            print(e)

        if matches:
            return str(matches[0])

    def download_reshade(self):
        if self.reshade_url != "":
            try:
                file_name = self.reshade_url.split('/')[-1]
                directory = os.path.join(DOWNLOAD_PATH, file_name)

                context = ssl.create_default_context(cafile=certifi.where())
                req = urllib.request.Request(self.reshade_url, headers={
                                             'User-Agent': 'Chrome/120.0.0.0'})

                with urllib.request.urlopen(req, context=context) as res:
                    with open(directory, "wb") as file:
                        file.write(res.read())

            except Exception as e:
                print(e)
