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

from widgets.pages.page_download import PageDownload

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

    def __init__(self):
        super().__init__()

        self.page_download = PageDownload()

        self.reshade_url = ""
        self.version = ""
        self.release = ""

        self.page_download.version.connect(self.get_version)
        self.page_download.release.connect(self.get_release)

        try:
            self.get_version()
            self.get_release()

            if self.version == "addon":
                self.reshade_url = f"https://reshade.me/downloads/ReShade_Setup_{self.release}_Addon.exe"
            else:
                self.reshade_url = f"https://reshade.me/downloads/ReShade_Setup_{self.release}.exe"
        except Exception as e:
            print(e)

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

    @Slot(str)
    def get_version(self, value):
        self.version = value

    @Slot(str)
    def get_release(self, value):
        self.release = value
