from PySide6.QtWidgets import (
    QComboBox,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar
)

from PySide6.QtCore import Qt, Signal, Slot, QThread
from scripts_core.script_download_re import DownloadWorker
from utils.utils import get_reshade_tags


class PageDownload(QWidget):
    download_finished: Signal = Signal(bool)
    is_addon: Signal = Signal(bool)

    def __init__(self):
        super().__init__()

        self.reshade_versions: list[str] = ["addon", "non-addon"]
        self.reshade_releases: list[str] = ["6.7.1", "6.7.0",
                                            "6.6.2", "6.6.1", "6.6.0", "6.5.1", "6.5.0"]
        self.more: str = "More"

        self.search_available_versions(None)

        self.more: str = "More"
        self.search_available_versions(None)

        # create layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout_selection = QHBoxLayout()

        # create widgets
        label_description = QLabel(
            "You can select if reshade has addon support or not, and choose the version.")
        label_description.setStyleSheet("font-size: 12pt; font-weight: 100")
        label_description.setWordWrap(True)

        self.reshade_version = QComboBox()
        self.reshade_release = QComboBox()
        self.reshade_release.activated.connect(self.on_release_selected)

        for item in self.reshade_versions:
            self.reshade_version.addItem(item)

        for item in self.reshade_releases:
            self.reshade_release.addItem(item)

        self.btn_download = QPushButton("Download")
        self.btn_download.clicked.connect(self.click_download)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        # add widgets
        layout.addWidget(label_description)

        layout_selection.addWidget(self.reshade_version)
        layout_selection.addWidget(self.reshade_release)
        layout.addLayout(layout_selection)

        layout.addWidget(self.btn_download)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def start_download(self) -> None:
        self.download_thread: QThread = QThread()
        self.download_worker: DownloadWorker = DownloadWorker(
            self.reshade_version.currentText(), self.reshade_release.currentText())

        self.download_worker.moveToThread(self.download_thread)

        # start and at the end, finished, are built-in thread signals
        self.download_thread.started.connect(self.download_worker.run)

        # reshade_found and reshade_error
        # both are signals from scrips_download_re.py
        self.download_worker.reshade_status.connect(self.update_text)
        self.download_worker.reshade_found.connect(self.on_success)
        self.download_worker.reshade_found.connect(self.on_error)

        self.download_worker.reshade_found.connect(self.download_thread.quit)
        self.download_worker.reshade_found.connect(
            self.download_worker.deleteLater)
        self.download_thread.finished.connect(self.download_thread.deleteLater)

        self.download_thread.start()

    def start_animation(self) -> None:
        self.progress_bar.setRange(0, 0)

    @Slot(str)
    def update_text(self, value: str) -> None:
        self.progress_bar.setFormat(value)

    @Slot(bool)
    def on_success(self, value: bool) -> None:
        self.btn_download.setEnabled(True)

        if self.reshade_version.currentText() == "addon":
            self.is_addon.emit(True)
        else:
            self.is_addon.emit(False)

        if value:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)
            self.download_finished.emit(value)

    @Slot(bool)
    def on_error(self, value: bool) -> None:
        self.btn_download.setEnabled(True)
        if not value:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
            self.download_finished.emit(value)

    def click_download(self) -> None:
        self.start_animation()
        self.start_download()
        self.btn_download.setEnabled(False)

    def on_release_selected(self, index: int) -> None:
        # Search for more releases if the user clicked in the "More" item.
        # It should always be the last item, but might not be present if there was an error when searching the first tags page in reshade's github
        if self.reshade_release.itemText(index) == self.more:
            self.search_available_versions(self.reshade_releases[-2])
            # Set the selection to the last known value before "More" was selected
            self.reshade_release.setCurrentIndex(index-1)
            # Insert new items before "More"
            self.reshade_release.insertItems(
                index, self.reshade_releases[index:-1])

    def search_available_versions(self, after: str | None) -> None:
        tags: list[str] | None = get_reshade_tags(after)
        if not tags:
            # Don't change list in case of error. This will keep the hardcoded list as is if it happens on startup.
            return
        if not after:
            # Special handling for first page of tags.
            # Clean hardcoded list and add a "More" entry for manually searching other pages.
            self.reshade_releases = [self.more]
        for tag in tags:
            # Make sure the "More" entry is always the last one
            self.reshade_releases.insert(len(self.reshade_releases) - 1, tag)
