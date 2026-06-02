from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from scripts_core.script_shaders import ShadersWorker
from utils.utils import get_renodx_assets


class PageClone(QWidget):
    clone_finished: Signal = Signal(bool)

    def __init__(self, is_addon_param: bool):
        super().__init__()

        self.selections: list[str] = []
        self.is_addon: bool = is_addon_param
        self.game_name: str = ""

        # create layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        widget_checkboxes = QWidget()
        layout_checkboxes = QVBoxLayout(widget_checkboxes)
        layout_checkboxes.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # create widgets
        label_description = QLabel("Select as many repositories you want.")
        label_description.setStyleSheet("font-size: 12pt; font-weight: 100")
        label_description.setWordWrap(True)

        self.scroll_area = QScrollArea()

        self.cxb_crosire_slim = QCheckBox("Crosire slim")
        self.lbl_crosire_slim = QLabel(
            "Default crosire, eg: Deband, UIMask...")

        self.cxb_crosire_legacy = QCheckBox("Crosire legacy")
        self.lbl_crosire_legacy = QLabel(
            "Legacy shaders from crosire, eg: AmbientLight."
        )

        self.cxb_sweet_fx = QCheckBox("Sweet FX")
        self.lbl_sweet_fx = QLabel("SMAA, FXAA, CAS...")

        self.cxb_prod80 = QCheckBox("Prod80")
        self.lbl_prod80 = QLabel("Color grading shaders.")

        self.cxb_quint = QCheckBox("qUINT")
        self.lbl_quint = QLabel("MXAO, Lightroom, DOF, Bloom...")

        self.cxb_immerse = QCheckBox("iMMERSE")
        self.lbl_immerse = QLabel("MXAO, Sharpen and SMAA.")

        self.cxb_mlut = QCheckBox("MLUT")
        self.lbl_mlut = QLabel(
            "<html>Big collection of multi-LUT. <span style='color: #FF5112'><strong>This repo have over 2GB</strong></span></html>"
        )

        self.cxb_insane = QCheckBox("Insane shaders")
        self.lbl_insane = QLabel("Utility shaders, eg: Fog Removal.")

        self.cxb_retro_arch = QCheckBox("RS Retro Arch")
        self.lbl_retro_arch = QLabel("Shaders from RetroArch.")

        self.cxb_crt_royale = QCheckBox("CRT Royale")
        self.lbl_crt_royale = QLabel("CRT emulation shaders.")

        self.cxb_glamarye = QCheckBox("Glamarye Fast Effects")
        self.lbl_glamarye = QLabel("Faster shaders, eg: FXAA, AO, SHARPEN...")

        self.cxb_reshade_hdr_shaders = QCheckBox("ReShade HDR Shaders")
        self.lbl_reshade_hdr_shaders = QLabel(
            "Democratisation of HDR analysis and other HDR things."
        )

        self.cxb_pumbo_auto_hdr = QCheckBox("Pumbo Auto HDR")
        self.lbl_pumbo_auto_hdr = QLabel("Advanced ReShade AutoHDR.")

        self.cxb_potato_fx = QCheckBox("PotatoFX")
        self.lbl_potato_fx = QLabel(
            "pCamera, pColorNoise, pColors, pPalletePopsterize..."
        )

        self.cxb_reshade_simple_hdr_shaders = QCheckBox(
            "ReShade Simple HDR Shaders")
        self.lbl_reshade_simple_hdr_shaders = QLabel(
            "HDR-Compatible shaders that focus on eye-candy effects and basic adjustments."
        )

        self.cxb_list: list[QCheckBox] = [
            self.cxb_crosire_slim,
            self.cxb_crosire_legacy,
            self.cxb_sweet_fx,
            self.cxb_prod80,
            self.cxb_quint,
            self.cxb_immerse,
            self.cxb_mlut,
            self.cxb_insane,
            self.cxb_retro_arch,
            self.cxb_crt_royale,
            self.cxb_glamarye,
            self.cxb_reshade_hdr_shaders,
            self.cxb_pumbo_auto_hdr,
            self.cxb_potato_fx,
            self.cxb_reshade_simple_hdr_shaders,
        ]

        self.cxb_dict: dict[str, dict[str, QCheckBox | QLabel]] = {
            "crosire_slim": {
                "checkbox": self.cxb_crosire_slim,
                "label": self.lbl_crosire_slim,
            },
            "crosire_legacy": {
                "checkbox": self.cxb_crosire_legacy,
                "label": self.lbl_crosire_legacy,
            },
            "sweet_fx": {"checkbox": self.cxb_sweet_fx, "label": self.lbl_sweet_fx},
            "prod80": {"checkbox": self.cxb_prod80, "label": self.lbl_prod80},
            "quint": {"checkbox": self.cxb_quint, "label": self.lbl_quint},
            "immerse": {"checkbox": self.cxb_immerse, "label": self.lbl_immerse},
            "mlut": {"checkbox": self.cxb_mlut, "label": self.lbl_mlut},
            "insane": {"checkbox": self.cxb_insane, "label": self.lbl_insane},
            "retro_arch": {
                "checkbox": self.cxb_retro_arch,
                "label": self.lbl_retro_arch,
            },
            "crt_royale": {
                "checkbox": self.cxb_crt_royale,
                "label": self.lbl_crt_royale,
            },
            "glamarye": {"checkbox": self.cxb_glamarye, "label": self.lbl_glamarye},
            "reshade_hdr_shaders": {
                "checkbox": self.cxb_reshade_hdr_shaders,
                "label": self.lbl_reshade_hdr_shaders,
            },
            "pumbo_auto_hdr": {
                "checkbox": self.cxb_pumbo_auto_hdr,
                "label": self.lbl_pumbo_auto_hdr,
            },
            "potato_fx": {"checkbox": self.cxb_potato_fx, "label": self.lbl_potato_fx},
            "reshade_siple_hdr_shaders": {
                "checkbox": self.cxb_reshade_simple_hdr_shaders,
                "label": self.lbl_reshade_simple_hdr_shaders,
            },
        }

        # Makes it comes checked because of ReShade.fxh
        self.cxb_crosire_slim.setChecked(True)

        for values in self.cxb_dict:
            for key, value in self.cxb_dict[values].items():
                if isinstance(value, QLabel):
                    value.setStyleSheet("font-weight: 100;")
                layout_checkboxes.addWidget(value)

        # RenoDX
        self.renodx_assets: list[str] | None = None
        self.lbl_renodx = QLabel("RenoDX - Select game addon")
        self.renodx_addon = QComboBox()

        layout_checkboxes.addSpacing(15)
        layout_checkboxes.addWidget(self.lbl_renodx)
        layout_checkboxes.addWidget(self.renodx_addon)

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

    # Have commented an option that returns the reno-dx item with the same first letter as the game
    # cuz, tbh, there is no point to make it enabled by default. If someone enables addon, does not
    # mean he wants to use reno_dx. Uncomment to implement again.
    def update_renodx(self) -> None:
        if not self.is_addon:
            self.renodx_addon.addItem("None")
            self.renodx_addon.setEnabled(False)
            return

        self.renodx_addon.setEnabled(True)

        if self.renodx_assets is None:
            self.renodx_assets = get_renodx_assets()

            self.renodx_addon.clear()

            if self.renodx_assets:
                self.renodx_addon.addItems(self.renodx_assets)

        # if self.renodx_assets and self.game_name:
        #     self.set_renodx_selector_value(
        #         self.game_name, self.renodx_assets, self.renodx_addon
        #     )

    # def set_renodx_selector_value(
    #     self, game_name: str, asset_list: list[str] | None, selector: QComboBox
    # ) -> None:
    #     if not asset_list or not game_name:
    #         return

    #     first_char: str = game_name[0].lower()
    #     pattern: str = "renodx-"
    #     pattern_size: int = len(pattern)

    #     for index, asset in enumerate(asset_list):
    #         if (
    #             asset.startswith(pattern)
    #             and len(asset) > pattern_size
    #             and asset[pattern_size] == first_char
    #         ):
    #             selector.setCurrentIndex(index)
    #             return

    def set_game_name(self, value: str) -> None:
        self.game_name = value
        self.update_renodx()

    def set_is_addon(self, value: bool) -> None:
        self.is_addon = value
        self.update_renodx()
        self.update_renodx_selector()

    def update_renodx_selector(self) -> None:
        # is_addon = True or False
        self.renodx_addon.setEnabled(self.is_addon)
        self.renodx_addon.updatesEnabled()

    def on_install(self, game_dir: str) -> None:
        self.start_animation()
        self.append_selections(self.selections)
        self.start_clone(game_dir)
        self.btn_install.setEnabled(False)

    def append_selections(self, selections: list[str]):
        for checkbox in self.cxb_list:
            if checkbox.isChecked():
                selections.append(checkbox.text())

    def start_clone(self, game_dir: str) -> None:
        if not self.selections:
            return

        self.clone_thread: QThread = QThread()
        self.clone_worker: ShadersWorker = ShadersWorker(
            self.selections, self.renodx_addon.currentText(), game_dir
        )

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

    @Slot(bool)
    def on_success(self, value: bool) -> None:
        self.btn_install.setEnabled(True)
        if value:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)
            self.progress_bar.setFormat("Installation finished!")
            self.clone_finished.emit(value)

            for checkbox in self.cxb_list:
                checkbox.setChecked(False)

    @Slot(bool)
    def on_error(self, value: bool) -> None:
        self.btn_install.setEnabled(True)
        if not value:
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("Failed shader proccess")
            self.clone_finished.emit(value)
