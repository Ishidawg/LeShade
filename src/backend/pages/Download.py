from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot, QStandardPaths
from ..utils import get_tags, generic_request

DOWNLOAD_PATH: str = QStandardPaths.writableLocation(
    QStandardPaths.StandardLocation.DownloadLocation)


class WorkerSignals(QObject):
    result: Signal = Signal(list)
    error: Signal = Signal(str)


class Worker(QRunnable):
    def __init__(self) -> None:
        super().__init__()
        self.signals = WorkerSignals()

    @Slot()
    def run(self) -> None:
        try:
            versions: list[str] = get_tags() or []
            self.signals.result.emit(versions)
        except Exception as e:
            self.signals.error.emit(str(e))


class DownloadBackend(QObject):
    release_version_ready: Signal = Signal(list)
    release_version_failed: Signal = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self.url: str = ""
        self.release_version: str = ""
        self.is_addon: bool = True

        self.threadpool: QThreadPool = QThreadPool()
        thread_count: int = self.threadpool.maxThreadCount()
        print("Threads: ", thread_count)

    # @Slot(result="QVariantList")
    @Slot()
    def feed_release_version(self) -> None:
        worker: Worker = Worker()
        worker.signals.result.connect(self._on_versions_ready)
        worker.signals.error.connect(self._on_versions_error)
        self.threadpool.start(worker)

    @Slot()
    def download(self) -> None:
        # TODO: try except, defensive statement
        if self.is_addon:
            self.url = f"https://reshade.me/downloads/ReShade_Setup_{self.release_version}_Addon.exe"
        else:
            self.url = f"https://reshade.me/downloads/ReShade_Setup_{self.release_version}.exe"

        generic_request(self.url, DOWNLOAD_PATH)

    @Slot(str, result=str)
    def get_version(self, info: str) -> None:
        self.is_addon = True if info.lower() == "addon" else False

    @Slot(str, result=str)
    def get_release(self, info: str) -> None:
        self.release_version = info

    # Private
    @Slot(list)
    def _on_versions_ready(self, versions: list[str]) -> None:
        self.release_version_ready.emit(versions)

    @Slot(str)
    def _on_versions_error(self, error: str) -> None:
        self.release_version_failed.emit(error)
