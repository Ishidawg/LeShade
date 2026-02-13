import shutil
import sys
import os

from enum import IntEnum
from pathlib import Path

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QMainWindow,
    QApplication,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from widgets.widget_title import WidgetTitle
from widgets.pages.page_start import PageStart
from widgets.pages.page_download import PageDownload
from widgets.pages.page_installation import PageInstallation
from widgets.pages.page_clone import PageClone
from widgets.pages.page_dx8 import PageDX8
from widgets.pages.page_uninstall import PageUninstall
from widgets.widget_bottom_buttons import WidgetBottomButtons

from utils.utils import EXTRACT_PATH, format_game_name
from scripts_core.script_manager import create_manager, add_game


class Pages(IntEnum):
    START = 0
    DOWNLOAD = 1
    INSTALLATION = 2
    CLONE = 3
    WRAPPER = 4


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        WINDOW_SIZE: list[int] = [600, 500]

        self.setWindowTitle("LeShade")
        self.setMinimumSize(WINDOW_SIZE[0], WINDOW_SIZE[1])

        # main widget and main layout (page)
        widget_main = QWidget()
        self.setCentralWidget(widget_main)
        self.layout_main = QVBoxLayout(widget_main)

        # dinamic widget with stacked layout (pages)
        widget_dinamic = QWidget()
        self.layout_dynamic = QStackedLayout()
        widget_dinamic.setLayout(self.layout_dynamic)
        widget_dinamic.setContentsMargins(50, 0, 50, 0)

        # Instance widgets, set widget and related
        self.action_buttons: WidgetBottomButtons = WidgetBottomButtons()
        self.page_start: PageStart = PageStart()
        self.page_download: PageDownload = PageDownload()
        self.page_installation: PageInstallation = PageInstallation()
        self.page_clone: PageClone = PageClone()
        self.page_dx8: PageDX8 = PageDX8()

        self.pages: list[QWidget] = [self.page_start,
                                     self.page_download, self.page_installation, self.page_clone]
        self.pages_index: int = 0
        self.current_page: QWidget = self.pages[0]

        self.download_finished: bool = False
        self.install_finished: bool = False
        self.clone_finished: bool = False
        self.is_dx8: bool = False

        # tracks uninstall page
        self.is_uninstall: bool = False

        self.layout_dynamic.addWidget(self.page_start)

        # Connect signals (if there is signals)
        self.page_start.install.connect(self.on_install_clicked)
        self.page_start.uninstall.connect(self.on_uninstall_clicked)
        self.action_buttons.btn_home.clicked.connect(self.on_home_clicked)
        self.action_buttons.btn_back.clicked.connect(self.on_back_clicked)
        self.action_buttons.btn_next.clicked.connect(self.on_next_clicked)
        self.page_download.download_finished.connect(self.on_download_finished)
        self.page_installation.install_finished.connect(
            self.on_install_finished)
        self.page_installation.current_game_directory.connect(
            self.get_game_directory)
        self.page_installation.is_dx8.connect(self.get_is_dx8)
        self.page_clone.clone_finished.connect(self.on_clone_finished)

        # Clone work around, I get the game_dir and pass as param here, executing the on_clone that has game_dir as a param sequencially.
        self.game_directory: str = ''
        self.page_clone.btn_install.clicked.connect(self.on_clone)

        # add widgets
        self.layout_main.addWidget(WidgetTitle())
        self.layout_main.addWidget(widget_dinamic)
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

        # 0 - Page Start
        # 1 - Page Download
        # 2 - Page Installation
        # 3 - Page Clone
        # 4 - Page DX8

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

                    add_game(self.game_directory)

                    if self.is_dx8:
                        self.manage_dx8_page(True)
                    else:
                        self.manage_dx8_page(False)
            case Pages.WRAPPER:
                self.enable_next_button()
            case _:
                raise ValueError(
                    "The page that your trying to access does not exist")

    def manage_dx8_page(self, append:  bool) -> None:
        if append:
            self.pages.append(self.page_dx8)
            return

        if not append and len(self.pages) == 5:
            self.pages.pop()
            return

    def manage_uninstall_page(self, value: bool) -> None:
        if value:
            self.is_uninstall = value
            self.page_uninstall: PageUninstall = PageUninstall()
            self.insert_page(self.page_uninstall)
            return

        if not value:
            self.insert_page(self.current_page)
            return

    def update_next_button(self) -> None:
        if self.pages_index == Pages.CLONE and not self.is_dx8 or self.pages_index == Pages.WRAPPER:
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
        self.layout_dynamic.removeWidget(self.current_page)

        match direction:
            case 0:
                if self.pages_index > 0:
                    self.pages_index -= 1
            case 1:
                if self.pages_index < len(self.pages) - 1:
                    self.pages_index += 1
            case _:
                print("Error trying to change pages")

        self.current_page = self.pages[self.pages_index]
        self.update_buttons()
        self.insert_page()

    def insert_page(self, page: QWidget | None = None) -> None:
        self.layout_dynamic.removeWidget(self.current_page)
        self.layout_dynamic.removeWidget(self.page_start)
        self.layout_dynamic.removeWidget(self.page_download)

        if self.is_uninstall:
            self.layout_dynamic.removeWidget(self.page_uninstall)

        if page:
            self.layout_dynamic.addWidget(page)
        else:
            self.layout_dynamic.addWidget(self.current_page)

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

    @Slot(bool)
    def on_download_finished(self, value: bool) -> None:
        if value:
            self.download_finished = value
            self.update_buttons()

    @Slot(bool)
    def on_install_finished(self, value: bool) -> None:
        if value:
            self.install_finished = value
            self.update_buttons()

    @Slot(bool)
    def on_clone_finished(self, value: bool) -> None:
        if value:
            self.clone_finished = value
            self.update_buttons()

    @Slot(bool)
    def get_is_dx8(self, value: bool) -> None:
        if value:
            self.is_dx8 = value
            return

        if not value:
            self.is_dx8 = value
            return

    @Slot(str)
    def get_game_directory(self, value: str) -> None:
        self.game_directory = value
        self.page_dx8 = PageDX8(format_game_name(self.game_directory))

    @Slot()
    def closeEvent(self, event) -> None:
        self.clean_cache()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setOrganizationName("Ishidawg")
    app.setApplicationName("LeShade")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
