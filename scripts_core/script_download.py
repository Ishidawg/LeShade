import os
from PySide6.QtCore import (
    QObject,
    Signal,
    QStandardPaths,
    Slot
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

LOCAL_RESHADE_DIR = os.path.join(CACHE_PATH, "reshade_extracted")


class DownloadWorker(QObject):
    download_finish = Signal(bool)

    def __init__(self, version, release):
        super().__init__()

        self.reshade_url = ""
        self.version = version
        self.release = release

        self.build_url()
        self.download_reshade()

    def build_url(self):
        try:
            if self.version == "addon":
                self.reshade_url = f"https://reshade.me/downloads/ReShade_Setup_{self.release}_Addon.exe"
            else:
                self.reshade_url = f"https://reshade.me/downloads/ReShade_Setup_{self.release}.exe"
        except Exception as e:
            print(e)

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
