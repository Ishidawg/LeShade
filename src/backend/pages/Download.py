from PySide6.QtCore import QObject, Slot

from ..utils import get_tags


class DownloadBackend(QObject):

    @Slot(result="QVariantList")
    def feed_release_version(self):
        return get_tags()

    @Slot()
    def download(self):
        print("clicou!!", flush=True)
