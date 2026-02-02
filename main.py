import sys

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QMainWindow,
    QApplication,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from widgets.pages.page_installation import PageInstallation
from widgets.widget_title import WidgetTitle
from widgets.pages.page_start import PageStart
from widgets.pages.page_download import PageDownload
from widgets.widget_bottom_buttons import WidgetBottomButtons


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

        # Instance widgets and set widget
        self.action_buttons = WidgetBottomButtons()
        self.page_start = PageStart()
        self.page_download = PageDownload()
        self.page_installation = PageInstallation()

        self.pages: list[QWidget] = [self.page_start, self.page_installation]
        self.current_page: QWidget = self.pages[0]

        self.layout_dynamic.addWidget(self.current_page)

        # Connect signals (if there is signals)
        self.page_start.install.connect(self.on_install_clicked)
        self.page_start.uninstall.connect(self.on_uninstall_clicked)

        # add widgets
        self.layout_main.addWidget(WidgetTitle())
        self.layout_main.addWidget(widget_dinamic)
        self.layout_main.addWidget(self.action_buttons)

    # Signals connections
    @Slot(bool)
    def on_install_clicked(self, value) -> None:
        if value:
            self.layout_dynamic.removeWidget(self.current_page)
            self.layout_dynamic.addWidget(self.page_download)
            self.action_buttons.btn_back.show()
            self.action_buttons.btn_next.show()

    @Slot(bool)
    def on_uninstall_clicked(self, value) -> None:
        print(f"Clicked {value}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setOrganizationName("Ishidawg")
    app.setApplicationName("LeShade")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
