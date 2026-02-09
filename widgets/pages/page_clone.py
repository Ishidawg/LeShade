from PySide6.QtWidgets import (
    QCheckBox,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget
)

from PySide6.QtCore import QThread, Qt, Signal

from scripts_core.script_shaders import ShadersWorker


class PageClone(QWidget):
    clone_finished: Signal = Signal(bool)

    def __init__(self):
        super().__init__()

        self.selections: list[str] = []

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

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self.btn_install = QPushButton("Install")

        # add widgets
        layout.addWidget(label_description)
        layout.addWidget(self.scroll_area)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.btn_install)
        self.setLayout(layout)

    def on_install(self, game_dir: str) -> None:
        self.start_animation()
        self.append_selections(self.selections)
        self.start_clone(game_dir)

    def append_selections(self, selections: list[str]):
        for checkbox in self.cxb_list:
            if checkbox.isChecked():
                selections.append(checkbox.text())

    def start_clone(self, game_dir: str) -> None:
        if not self.selections:
            return

        self.clone_thread: QThread = QThread()
        self.clone_worker: ShadersWorker = ShadersWorker(
            self.selections, game_dir)

        self.clone_worker.moveToThread(self.clone_thread)

        # start and at the end, finished, are built-in threads signals
        self.clone_thread.started.connect(self.clone_worker.run)

        # clone_finished
        self.clone_worker.clone_finished.connect(self.on_success)
        self.clone_worker.clone_finished.connect(self.on_error)

        self.clone_worker.clone_finished.connect(self.clone_thread.quit)
        self.clone_worker.clone_finished.connect(self.clone_worker.deleteLater)
        self.clone_thread.finished.connect(self.clone_thread.deleteLater)

        self.clone_thread.start()

    def start_animation(self) -> None:
        self.progress_bar.setRange(0, 0)

    def on_success(self, value: bool) -> None:
        if value:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)
            self.progress_bar.setFormat("Installation finished!")
            self.clone_finished.emit(value)

            for checkbox in self.cxb_list:
                checkbox.setChecked(False)

    def on_error(self, value: bool) -> None:
        if not value:
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("Failed shader proccess")
            self.clone_finished.emit(value)
