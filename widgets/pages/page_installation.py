from PySide6.QtWidgets import (
    QGridLayout,
    QLineEdit,
    QRadioButton,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)

from PySide6.QtCore import Qt, Signal, Slot


class PageInstallation(QWidget):
    install: Signal = Signal(bool)
    uninstall: Signal = Signal(bool)

    def __init__(self):
        super().__init__()

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

        # self.btn_install = QPushButton("Install")
        # self.btn_uninstall = QPushButton("Uninstall")

        # self.btn_install.clicked.connect(self.click_install)
        # self.btn_uninstall.clicked.connect(self.click_uninstall)

        self.setLayout(layout)

    @Slot(bool)
    def click_install(self) -> None:
        self.install.emit(True)

    @Slot(bool)
    def click_uninstall(self) -> None:
        self.uninstall.emit(True)
