#!/usr/bin/env python3
import gc
import os
import shutil
import sys
from enum import IntEnum
from pathlib import Path

from PySide6.QtCore import Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from scripts_core.script_manager import add_game, create_manager
from utils.utils import EXTRACT_PATH, get_game_directory_name
from utils.wrapper_text import DX8_WRAPPER, VULKAN_WRAPPER
from widgets.pages.page_clone import PageClone
from widgets.pages.page_download import PageDownload
from widgets.pages.page_installation import PageInstallation
from widgets.pages.page_start import PageStart
from widgets.pages.page_uninstall import PageUninstall
from widgets.pages.page_wrapper import PageWrapper
from widgets.widget_bottom_buttons import WidgetBottomButtons
from widgets.widget_title import WidgetTitle

app_version: str = "2.4.9"
build_type: str = "Release"


def get_localdir():
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))

    if getattr(sys, "frozen", False):
        return base_path
    else:
        return os.path.dirname(os.path.abspath(__file__))


class Pages(IntEnum):
    START = 0
    DOWNLOAD = 1
    INSTALLATION = 2
    CLONE = 3
    WRAPPER = 4


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        WINDOW_SIZE: list[int] = [620, 500]

        window_title: str = f"LeShade {app_version}"

        if build_type == "Nightly":
            window_title += " Nightly"

        self.setWindowTitle(window_title)
        self.setFixedSize(WINDOW_SIZE[0], WINDOW_SIZE[1])

        # main widget and main layout (page)
        widget_main = QWidget()
        self.setCentralWidget(widget_main)
        self.layout_main = QVBoxLayout(widget_main)

        # dinamic stack
        self.stack = QStackedWidget()
        self.stack.setContentsMargins(50, 0, 50, 0)

        self.is_addon: bool = False  # tracks reshade version (addon or not)

        # Instance widgets, set widget and related
        self.action_buttons: WidgetBottomButtons = WidgetBottomButtons()
        self.page_start: PageStart = PageStart()
        self.page_download: PageDownload = PageDownload()
        self.page_installation: PageInstallation = PageInstallation()
        self.page_clone: PageClone = PageClone(self.is_addon)
        self.page_wrapper: PageWrapper

        self.pages: list[QWidget] = [
            self.page_start,
            self.page_download,
            self.page_installation,
            self.page_clone,
        ]

        for page in self.pages:
            self.stack.addWidget(page)

        self.pages_index: int = 0

        self.download_finished: bool = False
        self.install_finished: bool = False
        self.clone_finished: bool = False
        self.is_dx8: bool = False
        self.is_vulkan: bool = False

        self.game_api_dll: str = ""
        self.game_name: str = ""

        # prefix directories signals
        self.reshade_prx_dir: str = ""
        self.system32_prx_dir: str = ""
        self.vulkanrt_prx_dir: str = ""

        self.is_uninstall: bool = False  # tracks uninstall page

        # Connect signals (if there is signals)
        self.page_start.install.connect(self.on_install_clicked)
        self.page_start.uninstall.connect(self.on_uninstall_clicked)

        self.action_buttons.btn_home.clicked.connect(self.on_home_clicked)
        self.action_buttons.btn_back.clicked.connect(self.on_back_clicked)
        self.action_buttons.btn_next.clicked.connect(self.on_next_clicked)

        self.page_download.is_addon.connect(self.get_is_addon)
        self.page_download.download_finished.connect(
            lambda value: self.on_action_finished("download", value)
        )
        self.page_installation.install_finished.connect(
            lambda value: self.on_action_finished("install", value)
        )
        self.page_clone.clone_finished.connect(
            lambda value: self.on_action_finished("clone", value)
        )
        self.page_installation.is_dx8.connect(
            lambda value: self.get_wrapper_api("dx8", value)
        )
        self.page_installation.is_vulkan.connect(
            lambda value: self.get_wrapper_api("vulkan", value)
        )
        self.page_installation.dll_api.connect(
            lambda value: self.get_simple_value("api", value)
        )
        self.page_installation.already_have_hlsl_compiler.connect(
            lambda value: self.get_simple_value("hlsl_compiler", value)
        )
        self.page_installation.current_game_directory.connect(
            lambda value: self.get_simple_value("game_dir", value)
        )
        self.page_installation.current_executable_path.connect(
            lambda str_value: self.get_simple_value("exe_path", str_value)
        )
        self.page_installation.forward_vulkan_paths.connect(self.get_vulkan_paths)

        # Clone work around, I get the game_dir and pass as param here, executing the on_clone that has game_dir as a param sequencially.
        self.game_directory: str = ""
        self.page_clone.btn_install.clicked.connect(self.on_clone)

        # So I can set the correct name at uninstall list
        self.game_exe_path: str = ""

        # This variable is usefull so I know if the game directory already have hlsl compiler, then I do not overwrite neither delete it at uninstall process
        self.have_hlsl: bool | None = None

        # add widgets
        self.layout_main.addWidget(WidgetTitle())
        self.layout_main.addWidget(self.stack)
        self.layout_main.addWidget(self.action_buttons)

    def on_clone(self) -> None:
        self.page_clone.on_install(self.game_directory)

    def on_home_clicked(self) -> None:
        self.manage_uninstall_page(False)
        self.action_buttons.btn_home.hide()

    def on_back_clicked(self) -> None:
        self.change_page(0)

    def on_next_clicked(self) -> None:
        self.change_page(1)

    def update_buttons(self) -> None:
        self.action_buttons.btn_next.setEnabled(False)
        self.update_next_button()

        match self.pages_index:
            case Pages.START:
                self.change_button_visibilty(False)
                create_manager()
            case Pages.DOWNLOAD:
                if self.download_finished:
                    self.enable_next_button()
                self.change_button_visibilty(True)
            case Pages.INSTALLATION:
                if self.install_finished:
                    self.enable_next_button()
            case Pages.CLONE:
                if self.clone_finished:
                    self.enable_next_button()
            case Pages.WRAPPER:
                self.enable_next_button()
            case _:
                raise ValueError("The page that you're trying to access does not exist")

    def manage_extra_page(self, append: bool, page: QWidget) -> None:
        if append:
            self.stack.addWidget(page)
        else:
            # Grabs the index, so I can remove it
            index: int = self.stack.indexOf(page)
            if index != -1:
                self.stack.removeWidget(page)
                page.deleteLater()

    def manage_uninstall_page(self, value: bool) -> None:
        self.is_uninstall = value
        if value:
            self.page_uninstall: PageUninstall = PageUninstall()
            self.stack.addWidget(self.page_uninstall)
            self.stack.setCurrentWidget(self.page_uninstall)
        else:
            self.stack.setCurrentIndex(self.pages_index)

            # Clean page uninstall from memory
            if hasattr(self, "page_uninstall"):
                self.stack.removeWidget(self.page_uninstall)
                self.page_uninstall.deleteLater()

    def update_next_button(self) -> None:
        # See if needs extra page on Clone widget
        clone_is_end = (
            (self.pages_index == Pages.CLONE) and not self.is_dx8 and not self.is_vulkan
        )

        # See if we are oany extra page
        wrapper_is_end = self.pages_index == Pages.WRAPPER

        if clone_is_end or wrapper_is_end:
            self.action_buttons.btn_next.setText("Close")
            self.action_buttons.btn_next.clicked.disconnect()
            self.action_buttons.btn_next.clicked.connect(self.close)
        else:
            self.action_buttons.btn_next.setText("Next")
            self.action_buttons.btn_next.clicked.disconnect()
            self.action_buttons.btn_next.clicked.connect(self.on_next_clicked)

    def change_button_visibilty(self, show: bool) -> None:
        if show:
            self.action_buttons.btn_back.show()
            self.action_buttons.btn_next.show()
        else:
            self.action_buttons.btn_back.hide()
            self.action_buttons.btn_next.hide()

    def enable_next_button(self) -> None:
        self.action_buttons.btn_next.setEnabled(True)

    def change_page(self, direction: int = 1) -> None:
        if direction == 1 and self.pages_index < self.stack.count() - 1:
            self.pages_index += 1
        elif direction == 0 and self.pages_index > 0:
            self.pages_index -= 1

        self.stack.setCurrentIndex(self.pages_index)
        self.update_buttons()

    def clean_cache(self) -> None:
        if Path(EXTRACT_PATH).exists():
            shutil.rmtree(EXTRACT_PATH)

    # Signals connections
    @Slot(bool)
    def on_install_clicked(self, value: bool) -> None:
        if value:
            self.change_page(1)

    @Slot(bool)
    def on_uninstall_clicked(self, value: bool) -> None:
        if value:
            self.manage_uninstall_page(True)
            self.action_buttons.btn_home.show()

    @Slot(str, bool)
    def on_action_finished(self, action: str, value: bool) -> None:
        if not value:
            return

        match action:
            case "download":
                self.download_finished = value
            case "install":
                self.install_finished = value
            case "clone":
                self.clone_finished = value

                # Add game to the uninstall list widget
                add_game(
                    self.game_directory,
                    self.game_exe_path,
                    self.have_hlsl,
                    self.game_api_dll,
                    self.is_vulkan,
                    self.reshade_prx_dir,
                    self.system32_prx_dir,
                    self.vulkanrt_prx_dir,
                )

                if self.is_dx8:
                    self.page_wrapper = PageWrapper(
                        self.game_name,
                        DX8_WRAPPER[0],
                        DX8_WRAPPER[1],
                        DX8_WRAPPER[2],
                        DX8_WRAPPER[3],
                        DX8_WRAPPER[4],
                    )

                if self.is_vulkan:
                    self.page_wrapper = PageWrapper(
                        self.game_name,
                        VULKAN_WRAPPER[0],
                        VULKAN_WRAPPER[1],
                        VULKAN_WRAPPER[2],
                        VULKAN_WRAPPER[3],
                        VULKAN_WRAPPER[4],
                    )

                if self.is_dx8 or self.is_vulkan:
                    self.manage_extra_page(True, self.page_wrapper)

            case _:
                print("use a valid action!")

        self.update_buttons()
        gc.collect()

    @Slot(str, bool)
    def get_wrapper_api(self, is_api: str, value: bool) -> None:
        match is_api:
            case "dx8":
                self.is_dx8 = value
            case "vulkan":
                self.is_vulkan = value
            case _:
                print("use a valid api!")

    @Slot(bool)
    def get_is_addon(self, value: bool) -> None:
        if value:
            self.is_addon = value
        else:
            self.is_addon = False

        self.page_clone.set_is_addon(self.is_addon)

    @Slot(str, str, str)
    def get_vulkan_paths(self, reshade: str, sys32: str, vulkanrt: str) -> None:
        self.reshade_prx_dir = reshade
        self.system32_prx_dir = sys32
        self.vulkanrt_prx_dir = vulkanrt

    @Slot(str, bool)
    # I didn't typed the value by porpuse.
    def get_simple_value(self, get: str, value) -> None:
        match get:
            case "exe_path":
                self.game_exe_path = value
            case "api":
                self.game_api_dll = value
            case "hlsl_compiler":
                self.have_hlsl = value
            case "game_dir":
                self.game_directory = value
                self.game_name = get_game_directory_name(Path(value))
                self.page_clone.set_game_name(self.game_name)
            case _:
                print("use a valid 'get'!")

    @Slot()
    def closeEvent(self, event) -> None:
        self.clean_cache()


def main() -> None:
    app = QApplication(sys.argv)

    app.setOrganizationName("Ishidawg")
    app.setApplicationName("LeShade")

    local_dir: str = get_localdir()
    icon_path: str = os.path.join(local_dir, "assets", "logo.png")

    sys_icon_path: str = "/usr/share/icons/hicolor/256x256/apps/leshade.png"

    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    else:
        app.setWindowIcon(QIcon(sys_icon_path))

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
