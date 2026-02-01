from PySide6.QtWidgets import (
    QComboBox,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar
)

from PySide6.QtCore import Qt, Slot
from scripts_core.script_download import DownloadWorker


class PageDownload(QWidget):
    def __init__(self):
        super().__init__()

        self.reshade_versions = ["addon", "non-addon"]
        self.reshade_releases = ["6.7.1", "6.7.0",
                                 "6.6.2", "6.6.1", "6.6.0", "6.5.1", "6.5.0"]

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

    @Slot(bool)
    def click_download(self):
        DownloadWorker(self.reshade_version.currentText(),
                       self.reshade_release.currentText())
