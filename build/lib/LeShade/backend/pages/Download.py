from PySide6.QtCore import QObject, Slot, QStandardPaths
from ..utils import get_tags, generic_request

DOWNLOAD_PATH: str = QStandardPaths.writableLocation(
    QStandardPaths.StandardLocation.DownloadLocation)


class DownloadBackend(QObject):
    url: str = ""
    release_version: str = ""
    is_addon: bool = True

    @Slot(result="QVariantList")
    def feed_release_version(self):
        return get_tags()

    @Slot()
    def download(self):
        # TODO: try except, defensive statement
        if self.is_addon:
            self.url = f"https://reshade.me/downloads/ReShade_Setup_{self.release_version}_Addon.exe"
        else:
            self.url = f"https://reshade.me/downloads/ReShade_Setup_{self.release_version}.exe"

        generic_request(self.url, DOWNLOAD_PATH)

        print(self.is_addon)
        print(self.release_version)

    @Slot(str, result=str)
    def getVersion(self, info: str):
        self.is_addon = True if info.lower() == "addon" else False

    @Slot(str, result=str)
    def getRelease(self, info: str):
        self.release_version = info

    @Slot()
    def fodase(self):
        print("foda-se")
