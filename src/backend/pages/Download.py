from pathlib import Path

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot, QStandardPaths
from ..utils import get_tags, generic_request

DOWNLOAD_PATH: str = QStandardPaths.writableLocation(
    QStandardPaths.StandardLocation.DownloadLocation)


class WorkerSignals(QObject):
    result: Signal = Signal(list)
    error: Signal = Signal(str)


class WorkerRelease(QRunnable):
    def __init__(self) -> None:
        super().__init__()
        self.signals: WorkerSignals = WorkerSignals()

    @Slot()
    def run(self) -> None:
        try:
            versions: list[str] = get_tags() or []
            self.signals.result.emit(versions)
        except Exception as e:
            self.signals.error.emit(str(e))


class DownloadSignals(QObject):
    finished: Signal = Signal(bool)
    error: Signal = Signal(str)


class WorkerDownload(QRunnable):
    def __init__(self, url: str, directory: str) -> None:
        super().__init__()
        self.url: str = url
        self.directory: str = directory
        self.signals: DownloadSignals = DownloadSignals()

    def run(self) -> None:
        try:
            path: str | None = generic_request(self.url, self.directory)
            if path is not None:
                self.signals.finished.emit(True)
        except Exception as e:
            self.signals.error.emit(str(e))


class DownloadBackend(QObject):
    release_version_ready: Signal = Signal(list)
    release_version_failed: Signal = Signal(str)
    reshade_download_finished: Signal = Signal(bool)
    reshade_download_failed: Signal = Signal(str)

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
        worker: WorkerRelease = WorkerRelease()
        worker.signals.result.connect(self._on_versions_ready)
        worker.signals.error.connect(self._on_versions_error)
        self.threadpool.start(worker)

    @Slot()
    def download(self) -> None:
        if self.is_addon:
            self.url = f"https://reshade.me/downloads/ReShade_Setup_{self.release_version}_Addon.exe"
        else:
            self.url = f"https://reshade.me/downloads/ReShade_Setup_{self.release_version}.exe"

        if self.find_reshade():
            self.reshade_download_finished.emit(True)
            return

        worker: WorkerDownload = WorkerDownload(self.url, DOWNLOAD_PATH)
        worker.signals.finished.connect(self._on_download_finished)
        worker.signals.error.connect(self._on_download_failed)
        self.threadpool.start(worker)

    @Slot(str, result=str)
    def get_version(self, info: str) -> None:
        self.is_addon = True if info.lower() == "addon" else False

    @Slot(str, result=str)
    def get_release(self, info: str) -> None:
        self.release_version = info

    # No Slot
    def find_reshade(self) -> bool:
        matches: list[Path] = []
        filename: str = self.url.split("/")[-1]

        try:
            matches: list[Path] = list(Path(DOWNLOAD_PATH).rglob(filename))
        except Exception as e:
            raise OSError from e

        return True if matches else False

    # Private
    @Slot(list)
    def _on_versions_ready(self, versions: list[str]) -> None:
        self.release_version_ready.emit(versions)

    @Slot(str)
    def _on_versions_error(self, error: str) -> None:
        self.release_version_failed.emit(error)

    @Slot(bool)
    def _on_download_finished(self, value: bool) -> None:
        self.reshade_download_finished.emit(value)

    @Slot(str)
    def _on_download_failed(self, error: str) -> None:
        self.reshade_download_failed.emit(error)
