import os
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget
)

from PySide6.QtCore import QThread, Qt

from scripts_core.script_shaders import ShadersWorker


class PageClone(QWidget):

    def __init__(self):
        super().__init__()

        # create layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        widget_checkboxes = QWidget()
        layout_checkboxes = QVBoxLayout(widget_checkboxes)
        layout_checkboxes.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # create widgets
        label_description = QLabel(
            "Select as many repositories you want.")
        label_description.setStyleSheet("font-size: 12pt; font-weight: 100")
        label_description.setWordWrap(True)

        self.scroll_area = QScrollArea()

        # self.game_list = QListWidget()
        self.cxb_crosire_slim = QCheckBox("Crosire slim")
        self.cxb_crosire_legacy = QCheckBox("Crosire legacy")
        self.cxb_sweet_fx = QCheckBox("Sweet FX")
        self.cxb_prod80 = QCheckBox("Prod80")
        self.cxb_quint = QCheckBox("qUINT")
        self.cxb_immerse = QCheckBox("iMMERSE")
        self.cxb_mlut = QCheckBox("MLUT")
        self.cxb_insane = QCheckBox("Insane shaders")
        self.cxb_retro_arch = QCheckBox("RS Retro Arch")
        self.cxb_crt_royale = QCheckBox("CRT Royale")
        self.cxb_glamarye = QCheckBox("Glamarye Fast Effects")

        self.cxb_list: list[QCheckBox] = [self.cxb_crosire_slim, self.cxb_crosire_legacy, self.cxb_sweet_fx, self.cxb_prod80,
                                          self.cxb_quint, self.cxb_immerse, self.cxb_mlut, self.cxb_insane, self.cxb_retro_arch, self.cxb_crt_royale, self.cxb_glamarye]

        for cxb in self.cxb_list:
            layout_checkboxes.addWidget(cxb)

        self.scroll_area.setWidget(widget_checkboxes)

        self.btn_install = QPushButton("Install")
        self.btn_install.clicked.connect(self.on_install)

        # add widgets
        layout.addWidget(label_description)
        layout.addWidget(self.scroll_area)
        layout.addWidget(self.btn_install)
        self.setLayout(layout)

    def on_install(self):
        self.test()

    def test(self):
        selections = []
        if self.cxb_crosire_slim.isChecked():
            selections.append("crosire_slim")

        if not selections:
            return

        self.clone_thread = QThread()
        self.clone_worker = ShadersWorker(selections)

        self.clone_thread.moveToThread(self.clone_thread)

        self.clone_thread.started.connect(self.clone_worker.run)
        self.clone_thread.start()
