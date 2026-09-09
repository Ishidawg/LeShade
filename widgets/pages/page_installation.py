from PySide6.QtCore import QThread, Qt, Signal, Slot, QStandardPaths
from scripts_core.script_installation import (
    InstallationWorker,
    LifecycleWorker,
    check_existing_installation,
    update_reshade_dll_only,
    uninstall_game_reshade,
    get_api_dll_name
)
from scripts_core.script_manager import add_game
from scripts_core.script_scanner import scan_all_games, detect_graphics_api
from utils.utils import dialog_box
from pathlib import Path
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGridLayout,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QRadioButton,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QCheckBox
)
import subprocess
import shutil
import os


HOME = QStandardPaths.writableLocation(
    QStandardPaths.StandardLocation.HomeLocation)


class PageInstallation(QWidget):
    install_finished: Signal = Signal(bool)
    current_game_directory: Signal = Signal(str)
    current_executable_path: Signal = Signal(str)
    is_dx8: Signal = Signal(bool)
    is_vulkan: Signal = Signal(bool)
    already_have_hlsl_compiler: Signal = Signal(bool)
    dll_api: Signal = Signal(str)
    request_page_clone: Signal = Signal()
    request_dlss5_page: Signal = Signal(str)

    forward_vulkan_paths: Signal = Signal(str, str, str)

    def __init__(self):
        super().__init__()

        self.game_path: str = ""
        self.game_api: str = ""
        self.is_steam: bool = True
        self.current_existing_info: dict = {}
        self.lifecycle_mode: str = "update"

        # create layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout_detected = QHBoxLayout()
        layout_browse = QHBoxLayout()
        layout_api = QGridLayout()
        layout_api.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_api.setSpacing(20)

        # create widgets
        label_detected = QLabel("Discovered games (Steam / Heroic)")
        label_detected.setStyleSheet("font-size: 12pt; font-weight: 100")
        label_detected.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.combo_games = QComboBox()
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.setFixedWidth(80)
        self.btn_refresh.setToolTip("Rescan installed games")

        layout_detected.addWidget(self.combo_games)
        layout_detected.addWidget(self.btn_refresh)

        label_exe = QLabel("Or select game executable manually")
        label_exe.setStyleSheet("font-size: 12pt; font-weight: 100")
        label_exe.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.browse_input = QLineEdit()
        self.browse_button = QPushButton("Browse")
        self.use_native_dialog = QCheckBox("Use native file dialog")

        self.label_api = QLabel("Select game API")
        self.label_api.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.label_api.setStyleSheet("font-size: 12pt; font-weight: 100")

        self.radio_opengl = QRadioButton("OpenGL")
        self.radio_d3d8 = QRadioButton("D3D 8")
        self.radio_d3d9 = QRadioButton("D3D 9")
        self.radio_d3d10 = QRadioButton("D3D 10")
        self.radio_d3d11 = QRadioButton("D3D 11")
        self.radio_d3d12 = QRadioButton("D3D 12")
        self.radio_vulkan = QRadioButton("Vulkan")
        self.radio_d3d12.setChecked(True)

        self.label_status_detected = QLabel()
        self.label_status_detected.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_status_detected.setWordWrap(True)
        self.label_status_detected.setStyleSheet(
            "background-color: rgba(76, 175, 80, 0.15); "
            "color: #4CAF50; "
            "border: 1px solid #4CAF50; "
            "border-radius: 4px; "
            "padding: 6px; "
            "font-size: 10pt; "
            "font-weight: bold;"
        )
        self.label_status_detected.hide()

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self.btn_install = QPushButton("Install")

        self.widget_lifecycle = QWidget()
        self.layout_lifecycle = QHBoxLayout(self.widget_lifecycle)
        self.layout_lifecycle.setContentsMargins(0, 0, 0, 0)
        self.layout_lifecycle.setSpacing(10)

        self.btn_update = QPushButton("Update ReShade")
        self.btn_update.setToolTip(
            "Update ReShade DLL to the downloaded version, keeping settings and presets intact"
        )
        self.btn_modify = QPushButton("Modify Shaders / Add-ons")
        self.btn_modify.setToolTip(
            "Update ReShade and customize installed shaders and add-ons"
        )
        self.btn_dlss5 = QPushButton("DLSS 5")
        self.btn_dlss5.setToolTip("Open the DLSS 5 Autopilot assistant for this game")
        self.btn_dlss5.setStyleSheet(
            "QPushButton { color: #81C784; border: 1px solid #81C784; } "
            "QPushButton:hover { background-color: rgba(129, 199, 132, 0.15); }"
        )
        self.btn_dlss5.clicked.connect(self.on_dlss5_clicked)

        self.btn_uninstall = QPushButton("Uninstall")
        self.btn_uninstall.setToolTip("Completely remove ReShade from this game")
        self.btn_uninstall.setStyleSheet(
            "QPushButton { color: #ff6b6b; border: 1px solid #ff6b6b; } "
            "QPushButton:hover { background-color: rgba(255, 107, 107, 0.15); }"
        )

        self.layout_lifecycle.addWidget(self.btn_update)
        self.layout_lifecycle.addWidget(self.btn_modify)
        self.layout_lifecycle.addWidget(self.btn_dlss5)
        self.layout_lifecycle.addWidget(self.btn_uninstall)
        self.widget_lifecycle.hide()

        # add widgets
        layout.addWidget(label_detected)
        layout.addLayout(layout_detected)
        layout.addSpacing(5)

        layout.addWidget(label_exe)
        layout_browse.addWidget(self.browse_input)
        layout_browse.addWidget(self.browse_button)
        layout.addLayout(layout_browse)
        layout.addWidget(self.use_native_dialog)
        layout.addSpacing(5)

        layout.addWidget(self.label_api)
        layout_api.addWidget(self.radio_opengl, 0, 0)
        layout_api.addWidget(self.radio_d3d8, 0, 1)
        layout_api.addWidget(self.radio_d3d9, 0, 2)
        layout_api.addWidget(self.radio_d3d10, 1, 0)
        layout_api.addWidget(self.radio_d3d11, 1, 1)
        layout_api.addWidget(self.radio_d3d12, 1, 2)
        layout_api.addWidget(self.radio_vulkan, 2, 1)
        layout.addLayout(layout_api)
        layout.addSpacing(5)

        layout.addWidget(self.label_status_detected)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.btn_install)
        layout.addWidget(self.widget_lifecycle)

        # Connect functions and signals
        self.browse_button.clicked.connect(self.on_browse_clicked)
        self.browse_input.textChanged.connect(self.on_browse_text_changed)
        self.combo_games.currentIndexChanged.connect(self.on_game_selected)
        self.btn_refresh.clicked.connect(self.populate_games)
        self.btn_install.clicked.connect(self.on_install_clicked)
        self.btn_update.clicked.connect(self.on_update_clicked)
        self.btn_modify.clicked.connect(self.on_modify_clicked)
        self.btn_uninstall.clicked.connect(self.on_uninstall_clicked)

        self.populate_games()

        self.setLayout(layout)

    def populate_games(self) -> None:
        self.combo_games.blockSignals(True)
        self.combo_games.clear()
        self.combo_games.addItem("-- Select detected game (Steam / Heroic) --", userData=None)

        games = scan_all_games()
        for game in games:
            title = game.get("title", "Unknown")
            source = game.get("source", "Game")
            label = f"[{source}] {title}"
            self.combo_games.addItem(label, userData=game)

        self.combo_games.blockSignals(False)

    def on_game_selected(self, index: int) -> None:
        if index <= 0:
            return

        game_data = self.combo_games.itemData(index)
        if not game_data or not isinstance(game_data, dict):
            return

        exe_path = game_data.get("exe", "")
        if exe_path and os.path.exists(exe_path):
            self.browse_input.setText(exe_path)
            self.set_executable_path(exe_path)
            if game_data.get("source") == "Steam":
                self.is_steam = True
            elif game_data.get("source") == "Heroic":
                self.is_steam = False

    def on_browse_text_changed(self, text: str) -> None:
        clean = text.strip().strip('"').strip("'")
        if os.path.isfile(clean) and clean.lower().endswith(".exe"):
            if clean != self.game_path:
                self.set_executable_path(clean)
        else:
            self.game_path = clean
            self.check_existing_reshade()

    def set_executable_path(self, exe_path: str) -> None:
        self.game_path = exe_path
        self.current_executable_path.emit(self.game_path)
        self.auto_select_api(exe_path)
        self.check_existing_reshade()
        self.progress_bar.reset()

    def auto_select_api(self, exe_path: str) -> None:
        if not exe_path or not os.path.exists(exe_path):
            return

        api = detect_graphics_api(exe_path)
        if not api:
            self.label_api.setText(
                "Select game API (could not auto-detect, pick it manually)")
            return

        self.label_api.setText(f"Select game API (Auto-detected: {api})")

        radio_map = {
            "OpenGL": self.radio_opengl,
            "D3D 8": self.radio_d3d8,
            "D3D 9": self.radio_d3d9,
            "D3D 10": self.radio_d3d10,
            "D3D 11": self.radio_d3d11,
            "D3D 12": self.radio_d3d12,
            "Vulkan": self.radio_vulkan,
        }

        if api in radio_map:
            radio_map[api].setChecked(True)
            self.game_api = api

    def on_browse_clicked(self) -> None:
        options = (
            QFileDialog.Option(0)
            if self.use_native_dialog.checkState() == Qt.CheckState.Checked
            else QFileDialog.Option.DontUseNativeDialog
        )

        file_name: tuple[str, str] = QFileDialog.getOpenFileName(
            self, "Select game executable", HOME, "Executables (*.exe)", options=options)

        if file_name and file_name[0]:
            self.browse_input.setText(file_name[0])
            self.set_executable_path(file_name[0])

    def start_installation(self) -> None:
        if self.game_api == "Vulkan":
            self.is_steam = dialog_box(
                parent=self,
                title="Vulkan Installation",
                icon=QMessageBox.Icon.Question,
                text="Is your game on Steam?",
                info_text="Steam uses a different path prefix.",
                buttons=True,
            )

        self.install_thread: QThread = QThread()
        self.install_worker: InstallationWorker = InstallationWorker(
            self.game_path, self.game_api, self.is_steam)

        self.install_worker.moveToThread(self.install_thread)

        # start and ath the end, finished, are built-in thread signals
        self.install_thread.started.connect(
            self.install_worker.run)

        self.install_worker.install_progress.connect(self.update_progress)
        self.install_worker.install_finished.connect(self.on_sucess)
        self.install_worker.install_finished.connect(self.on_error)
        self.install_worker.current_game_path.connect(self.get_game_dir)
        self.install_worker.have_hlsl_compiler.connect(self.get_hlsl_compiler)
        self.install_worker.api_dll.connect(self.get_api_dll)
        self.install_worker.vulkan_paths.connect(
            self.forward_vulkan_paths.emit)

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

    def is_api_vulkan(self) -> None:
        if self.game_api == self.radio_vulkan.text():
            self.is_vulkan.emit(True)
        else:
            self.is_vulkan.emit(False)

    def get_api_dll(self, value: str) -> None:
        if value:
            self.dll_api.emit(value)

    def get_game_dir(self, value: str) -> None:
        self.current_game_directory.emit(value)

    def get_hlsl_compiler(self, value: bool) -> None:
        self.already_have_hlsl_compiler.emit(value)

    def on_install_clicked(self) -> None:
        started: bool = self.installation()
        self.update_install_button()

        # Only lock the button when a worker is actually running
        if started:
            self.btn_install.setEnabled(False)

    def update_install_button(self) -> None:
        self.check_existing_reshade()

    def check_existing_reshade(self) -> None:
        if not self.game_path or not os.path.exists(self.game_path):
            self.current_existing_info = {}
            self.label_status_detected.hide()
            self.widget_lifecycle.hide()
            self.btn_install.show()
            self.btn_install.setEnabled(False)
            return

        self.current_existing_info = check_existing_installation(self.game_path)

        if self.current_existing_info.get("installed"):
            ver = self.current_existing_info.get("version")
            dll = self.current_existing_info.get("api_dll") or "ReShade"
            ver_text = f"v{ver}" if ver else "detected"
            self.label_status_detected.setText(
                f"Existing ReShade found: {ver_text} ({dll})"
            )
            self.label_status_detected.show()
            self.btn_install.hide()
            self.widget_lifecycle.show()
        else:
            self.label_status_detected.hide()
            self.widget_lifecycle.hide()
            self.btn_install.show()
            self.btn_install.setEnabled(True)

    def on_update_clicked(self) -> None:
        self.start_lifecycle_update("update")

    def on_modify_clicked(self) -> None:
        self.start_lifecycle_update("modify")

    def start_lifecycle_update(self, mode: str) -> None:
        self.api_selection()
        if not self.game_path or not os.path.exists(self.game_path):
            self.progress_bar.setFormat("Error: invalid game path")
            return

        if not self.verify_wine():
            return

        self.lifecycle_mode = mode
        self.set_lifecycle_busy(True, "Updating ReShade...")

        target_dll = self.current_existing_info.get("api_dll", "")
        self.run_lifecycle_operation(
            update_reshade_dll_only,
            self.on_lifecycle_update_finished,
            self.game_path,
            game_api=self.game_api,
            target_dll_name=target_dll,
            is_steam=self.is_steam,
        )

    def run_lifecycle_operation(self, operation, on_finished, *args, **kwargs) -> None:
        # Update and uninstall can download files and spawn wine; keep them off the UI thread.
        self.lifecycle_thread: QThread = QThread()
        self.lifecycle_worker: LifecycleWorker = LifecycleWorker(operation, *args, **kwargs)
        self.lifecycle_worker.moveToThread(self.lifecycle_thread)

        self.lifecycle_thread.started.connect(self.lifecycle_worker.run)
        self.lifecycle_worker.finished.connect(on_finished)
        self.lifecycle_worker.finished.connect(self.lifecycle_thread.quit)
        self.lifecycle_worker.finished.connect(self.lifecycle_worker.deleteLater)
        self.lifecycle_thread.finished.connect(self.lifecycle_thread.deleteLater)

        self.lifecycle_thread.start()

    def set_lifecycle_busy(self, busy: bool, message: str = "") -> None:
        self.widget_lifecycle.setEnabled(not busy)
        if busy:
            self.progress_bar.setRange(0, 0)
            self.progress_bar.setFormat(message)
        else:
            self.progress_bar.setRange(0, 100)

    @Slot(bool, str, object)
    def on_lifecycle_update_finished(self, success: bool, msg: str, have_hlsl) -> None:
        self.set_lifecycle_busy(False)

        if not success:
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat(f"Error: {msg}")
            self.install_finished.emit(False)
            return

        self.progress_bar.setValue(100)
        parent_dir = str(Path(self.game_path).resolve().parent)
        target_dll = self.current_existing_info.get("api_dll", "")
        api_dll_name = target_dll or get_api_dll_name(self.game_api)

        self.current_game_directory.emit(parent_dir)
        self.current_executable_path.emit(self.game_path)
        self.dll_api.emit(api_dll_name)
        self.is_api_dx8()
        self.is_api_vulkan()
        self.install_finished.emit(True)

        if self.lifecycle_mode == "modify":
            self.progress_bar.setFormat("Ready to modify shaders!")
            self.request_page_clone.emit()
            return

        self.progress_bar.setFormat("ReShade updated successfully!")
        try:
            add_game(
                parent_dir,
                self.game_path,
                have_hlsl,
                api_dll_name,
                self.game_api == "Vulkan",
                "",
                "",
                ""
            )
        except Exception as e:
            print(f"Could not register game in manager: {e}")
        self.check_existing_reshade()

    def on_dlss5_clicked(self) -> None:
        if self.game_path:
            self.request_dlss5_page.emit(self.game_path)

    def on_uninstall_clicked(self) -> None:
        if not self.game_path or not os.path.exists(self.game_path):
            return

        game_name = Path(self.game_path).name
        confirm = dialog_box(
            parent=self,
            title="Uninstall ReShade",
            icon=QMessageBox.Icon.Warning,
            text=f"Uninstall ReShade from {game_name}?",
            info_text="This will remove ReShade binaries, shaders, add-ons, and configuration files.",
            buttons=True
        )

        if not confirm:
            return

        self.api_selection()

        # None lets the manager entry decide whether this was a Vulkan install
        is_vulkan: bool | None = None
        if self.game_api == "Vulkan":
            is_vulkan = True

        self.set_lifecycle_busy(True, "Uninstalling...")
        self.run_lifecycle_operation(
            uninstall_game_reshade,
            self.on_lifecycle_uninstall_finished,
            self.game_path,
            is_steam=self.is_steam,
            is_vulkan=is_vulkan,
        )

    @Slot(bool, str, object)
    def on_lifecycle_uninstall_finished(self, success: bool, msg: str, _extra) -> None:
        self.set_lifecycle_busy(False)

        if success:
            self.progress_bar.setValue(100)
            self.progress_bar.setFormat(msg)
            self.check_existing_reshade()
        else:
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat(f"Error: {msg}")

    def api_selection(self) -> None:
        available_api: dict = {
            self.radio_opengl: self.radio_opengl.text(),
            self.radio_d3d8: self.radio_d3d8.text(),
            self.radio_d3d9: self.radio_d3d9.text(),
            self.radio_d3d10: self.radio_d3d10.text(),
            self.radio_d3d11: self.radio_d3d11.text(),
            self.radio_d3d12: self.radio_d3d12.text(),
            self.radio_vulkan: self.radio_vulkan.text()
        }

        for key, value in available_api.items():
            if key.isChecked():
                self.game_api = value
                break

    def verify_wine(self) -> bool:
        """
        Returns False (after warning the user) when the selected API needs wine
        and none is available. Callers must abort in that case.
        """
        if self.game_api == "Vulkan":
            has_wine: bool = False

            if os.path.exists("/.flatpak-info"):
                wine_native = subprocess.run(
                    ["flatpak-spawn", "--host", "wine", "--version"],
                    capture_output=True
                )

                wine_flatpak = subprocess.run(
                    ["flatpak-spawn", "--host", "flatpak",
                        "info", "org.winehq.Wine"],
                    capture_output=True
                )

                has_wine = (wine_native.returncode == 0) or (
                    wine_flatpak.returncode == 0)
            else:
                has_wine = shutil.which("wine") is not None

                if not has_wine and shutil.which("flatpak") is not None:
                    wine_flatpak = subprocess.run(
                        ["flatpak", "info", "org.winehq.Wine"],
                        capture_output=True
                    )

                    has_wine = (wine_flatpak.returncode == 0)

            if not has_wine:
                self.progress_bar.setFormat("Error: missing wine - dependency")
                dialog_box(
                    parent=self,
                    title="Missing Dependency",
                    icon=QMessageBox.Icon.Critical,
                    text="Wine is not installed on your system!",
                    info_text="LeShade requires 'wine' to manage Vulkan registry keys. Please install it!",
                    buttons=False
                )
                return False

        return True

    def installation(self) -> bool:
        self.api_selection()

        if not self.game_path or not os.path.exists(self.game_path):
            self.progress_bar.setFormat("Error: no game directory")
            return False

        if not self.game_api:
            self.progress_bar.setFormat("Error: no API selected")
            return False

        # Vulkan needs wine for the registry keys; abort before touching anything.
        if not self.verify_wine():
            return False

        self.is_api_dx8()
        self.is_api_vulkan()
        self.start_installation()
        return True

    @Slot(int)
    def update_progress(self, value: int) -> None:
        self.progress_bar.setValue(value)

    @Slot(bool)
    def on_sucess(self, value: bool) -> None:
        self.btn_install.setEnabled(value)
        if value:
            self.progress_bar.setFormat("Installation finished!")
            self.install_finished.emit(value)
            self.check_existing_reshade()

    @Slot(bool)
    def on_error(self, value: bool) -> None:
        self.btn_install.setEnabled(True)
        if not value:
            self.progress_bar.setFormat("Error while installing")
            self.install_finished.emit(value)
