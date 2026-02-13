import os

from PySide6.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QLineEdit,
    QProgressBar,
    QRadioButton,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)

from PySide6.QtCore import QThread, Qt, Signal, Slot, QStandardPaths

from scripts_core.script_installation import InstallationWorker

HOME = QStandardPaths.writableLocation(
    QStandardPaths.StandardLocation.HomeLocation)


class PageInstallation(QWidget):
    install_finished: Signal = Signal(bool)
    current_game_directory: Signal = Signal(str)
    is_dx8: Signal = Signal(bool)

    def __init__(self):
        super().__init__()

        self.game_path: str = ""
        self.game_api: str = ""

        # create layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout_browse = QHBoxLayout()
        layout_api = QGridLayout()
        layout_api.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_api.setSpacing(20)

        # create widgets
        label_exe = QLabel("Select game executable")
        label_exe.setStyleSheet("font-size: 12pt; font-weight: 100")
        label_exe.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.browse_input = QLineEdit()
        self.browse_button = QPushButton("browse")

        label_api = QLabel("Select game api")
        label_api.setAlignment(Qt.AlignmentFlag.AlignLeft)
        label_api.setStyleSheet("font-size: 12pt; font-weight: 100")

        self.radio_opengl = QRadioButton("OpenGL")
        self.radio_d3d8 = QRadioButton("D3D 8")
        self.radio_d3d9 = QRadioButton("D3D 9")
        self.radio_d3d10 = QRadioButton("D3D 10")
        self.radio_d3d11 = QRadioButton("D3D 11")
        self.radio_vulkan = QRadioButton("Vulkan/D3D 12")
        self.radio_vulkan.setChecked(True)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self.btn_install = QPushButton("Install")

        # add widgets
        layout.addWidget(label_exe)

        layout_browse.addWidget(self.browse_input)
        layout_browse.addWidget(self.browse_button)
        layout.addLayout(layout_browse)
        layout.addSpacing(10)

        layout_api.addWidget(self.radio_opengl, 0, 0)
        layout_api.addWidget(self.radio_d3d8, 0, 1)
        layout_api.addWidget(self.radio_d3d9, 0, 2)
        layout_api.addWidget(self.radio_d3d10, 1, 0)
        layout_api.addWidget(self.radio_d3d11, 1, 1)
        layout_api.addWidget(self.radio_vulkan, 1, 2)
        layout.addLayout(layout_api)
        layout.addSpacing(10)

        layout.addWidget(self.progress_bar)
        layout.addWidget(self.btn_install)

        # Connect functions and signals (if there's)
        self.browse_button.clicked.connect(self.on_browse_clicked)
        self.btn_install.clicked.connect(self.on_install_clicked)

        self.setLayout(layout)

    def on_browse_clicked(self) -> None:
        file_name: tuple[str, str] = QFileDialog.getOpenFileName(
            self, "Select game executable", HOME, options=QFileDialog.Option.DontUseNativeDialog)

        if file_name:
            self.browse_input.setText(file_name[0])
            self.game_path = file_name[0]

    def start_installation(self) -> None:
        self.install_thread: QThread = QThread()
        self.install_worker: InstallationWorker = InstallationWorker(
            self.game_path, self.game_api)

        self.install_worker.moveToThread(self.install_thread)

        # start and ath the end, finished, are built-in thread signals
        self.install_thread.started.connect(self.install_worker.run)

        # install_progress and install_finished
        # both are signals from script_installation.py
        self.install_worker.install_progress.connect(self.update_progress)
        self.install_worker.install_finished.connect(self.on_sucess)
        self.install_worker.install_finished.connect(self.on_error)
        self.install_worker.current_game_path.connect(self.get_game_dir)

        self.install_worker.install_finished.connect(self.install_thread.quit)
        self.install_worker.install_finished.connect(
            self.install_worker.deleteLater)
        self.install_thread.finished.connect(self.install_thread.deleteLater)

        self.install_thread.start()

    def is_api_dx8(self) -> None:
        if self.game_api == self.radio_d3d8.text():
            self.is_dx8.emit(True)
        else:
            self.is_dx8.emit(False)

    def get_game_dir(self, value: str) -> None:
        self.current_game_directory.emit(value)

    def on_install_clicked(self) -> None:
        self.installation()

    @Slot(int)
    def update_progress(self, value: int) -> None:
        self.progress_bar.setValue(value)

    @Slot(bool)
    def on_sucess(self, value: bool) -> None:
        if value:
            self.progress_bar.setFormat("Installation finished!")
            self.install_finished.emit(value)

    @Slot(bool)
    def on_error(self, value: bool) -> None:
        if not value:
            self.progress_bar.setFormat("Error while installing")
            self.install_finished.emit(value)

    def api_selection(self) -> None:
        available_api: dict = {
            self.radio_opengl: self.radio_opengl.text(),
            self.radio_d3d8: self.radio_d3d8.text(),
            self.radio_d3d9: self.radio_d3d9.text(),
            self.radio_d3d10: self.radio_d3d10.text(),
            self.radio_d3d11: self.radio_d3d11.text(),
            self.radio_vulkan: self.radio_vulkan.text()
        }

        for key, value in available_api.items():
            if key.isChecked():
                self.game_api = value
                break

    def installation(self) -> None:
        self.api_selection()

        if not self.game_path or not os.path.exists(self.game_path):
            self.progress_bar.setFormat("Error: no game directory")
            return

        if not self.game_api:
            self.progress_bar.setFormat("Error: no api selected")
            return

        self.is_api_dx8()
        self.start_installation()
