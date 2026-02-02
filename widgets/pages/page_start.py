from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)

from PySide6.QtCore import Qt, Signal, Slot


class PageStart(QWidget):
    install: Signal = Signal(bool)
    uninstall: Signal = Signal(bool)

    def __init__(self):
        super().__init__()

        # create layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout_buttons = QHBoxLayout()

        # create widgets
        label_description = QLabel(
            "LeShade is a manager for reshade installations on Linux. It's a native tool that can manage multiple reshade versions across many games that uses Proton or Wine.")
        label_description.setStyleSheet("font-size: 12pt; font-weight: 100")
        label_description.setWordWrap(True)

        self.btn_install = QPushButton("Install")
        self.btn_uninstall = QPushButton("Uninstall")

        self.btn_install.clicked.connect(self.click_install)
        self.btn_uninstall.clicked.connect(self.click_uninstall)

        # add widgets
        layout.addWidget(label_description)

        layout_buttons.addWidget(self.btn_install)
        layout_buttons.addWidget(self.btn_uninstall)
        layout.addLayout(layout_buttons)

        self.setLayout(layout)

    @Slot(bool)
    def click_install(self) -> None:
        self.install.emit(True)

    @Slot(bool)
    def click_uninstall(self) -> None:
        self.uninstall.emit(True)
