import os

from PySide6.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QLineEdit,
    QRadioButton,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)

from PySide6.QtCore import Qt, Signal, Slot, QStandardPaths

from scripts_core.script_installation import InstallationWorker

HOME = QStandardPaths.writableLocation(
    QStandardPaths.StandardLocation.HomeLocation)


class PageInstallation(QWidget):
    can_install = Signal(bool)
    install_finished = Signal(bool)

    def __init__(self):
        super().__init__()

        self.game_path: str = ""
        self.game_api: str = ""

        # create layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout_browse = QHBoxLayout()
        layout_api = QGridLayout()
        layout_api.setSpacing(10)

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

        self.btn_install = QPushButton("Install")

        # add widgets
        layout.addWidget(label_exe)

        layout_browse.addWidget(self.browse_input)
        layout_browse.addWidget(self.browse_button)
        layout.addLayout(layout_browse)

        layout_api.addWidget(self.radio_opengl, 0, 0)
        layout_api.addWidget(self.radio_d3d8, 0, 1)
        layout_api.addWidget(self.radio_d3d9, 0, 2)
        layout_api.addWidget(self.radio_d3d10, 1, 0)
        layout_api.addWidget(self.radio_d3d11, 1, 1)
        layout_api.addWidget(self.radio_vulkan, 1, 2)
        layout.addLayout(layout_api)

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
            print(self.game_path)

    def on_install_clicked(self):
        self.api_selection()
        self.installation()
        self.install_test = InstallationWorker(self.game_path, self.game_api)

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
                print(self.game_api)
                break

    def installation(self) -> None:
        self.api_selection()

        if not self.game_path or not os.path.exists(self.game_path):
            self.can_install.emit(False)
            return

        if not self.game_api:
            self.can_install.emit(False)
            return

        self.can_install.emit(True)
