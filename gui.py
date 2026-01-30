import os
import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

# Import widgets
from widgets.start_widget import StartWidget
from widgets.installation_widget import InstallationWidget
from widgets.clone_widget import CloneShaderWidget
from widgets.wrapper_widget import WrapperWidget
from widgets.uninstall_widget import UninstallWidget

# Import constant
from scripts_core.download_core import LOCAL_RESHADE_DIR

# Manager related stuff
import scripts_core.manager_core

# l:    label
# c:    container
# ly:   layout
# b:    button

# To prevent failing on load the icon


def get_localdir():
    if getattr(sys, 'frozen', False):  # means that it is running with pyinstaller
        return sys._MEIPASS
    else:
        return os.path.dirname(os.path.abspath(__file__))


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # Set Widgets
        S_FIRST = StartWidget()
        S_SECOND = InstallationWidget()
        S_THIRD = CloneShaderWidget()
        S_WRAPPER = WrapperWidget()

        self.is_start_ready = False
        S_FIRST.process_finished.connect(self.on_start_finished)

        self.widgets = [S_FIRST, S_SECOND, S_THIRD, S_WRAPPER]
        self.widget_index = 0

        self.current_widget = self.widgets[0]

        self.is_uninstall = False

        self.current_api = None

        WINDOW_WIDTH = 620
        WINDOW_HEIGHT = 498

        self.setWindowTitle("LeShade")
        self.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        # Main container
        c_main = QWidget()
        c_main.setContentsMargins(40, 0, 40, 0)
        self.setCentralWidget(c_main)
        self.ly_main = QVBoxLayout(c_main)

        # Fixed text container and labels
        c_top_text = QWidget()
        c_top_text.setContentsMargins(0, 0, 0, 40)
        ly_top_text = QVBoxLayout(c_top_text)
        ly_top_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        l_title = QLabel("LeShade")
        l_title.setStyleSheet("font-size: 28pt; font-weight: 600; padding: 0")
        l_title.setAlignment(Qt.AlignmentFlag.AlignTop |
                             Qt.AlignmentFlag.AlignCenter)

        l_subtitle = QLabel("reshade manager")
        l_subtitle.setStyleSheet(
            "font-size: 12pt; font-weight: 100; padding: 0; margin: 0")
        l_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Fixed button container and thy self
        b_bottom_buttons = QWidget()
        b_bottom_buttons.setContentsMargins(0, 0, 0, 10)
        ly_bottom_buttons = QHBoxLayout(b_bottom_buttons)
        ly_bottom_buttons.setAlignment(
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter)

        self.b_next = QPushButton("Next", self)
        self.b_back = QPushButton("Back", self)

        self.b_uninstall = QPushButton("Uninstall", self)
        self.b_home = QPushButton("Home", self)
        self.b_home.hide()

        # AddWidgets
        self.ly_main.addWidget(c_top_text)
        self.ly_main.addWidget(self.current_widget)
        self.ly_main.addWidget(b_bottom_buttons)

        # Fixed text
        ly_top_text.addWidget(l_title)
        ly_top_text.addWidget(l_subtitle)

        ly_bottom_buttons.addWidget(self.b_uninstall)
        ly_bottom_buttons.addWidget(self.b_back)
        ly_bottom_buttons.addWidget(self.b_next)
        ly_bottom_buttons.addWidget(self.b_home)

        self.b_next.clicked.connect(self.on_next_clicked)
        self.b_back.clicked.connect(lambda: self.change_widget(-1))
        self.b_uninstall.clicked.connect(self.switch_to_uninstall)
        self.b_home.clicked.connect(self.switch_to_home)
        self.update_buttons()

    def on_next_clicked(self):
        if self.widget_index == 0:  # Start Widget
            reshade_path = LOCAL_RESHADE_DIR

            scripts_core.manager_core.create_manager()

            self.b_back.setEnabled(False)
            installation_widget = self.widgets[1]
            installation_widget.set_reshade_source(reshade_path)
            self.change_widget(1)
        elif self.widget_index == 1:  # Install Widget
            self.b_next.setEnabled(False)

            installation_widget = self.widgets[1]

            try:
                installation_widget.installation_finished.disconnect()
            except (RuntimeError, TypeError):
                pass

            installation_widget.installation_finished.connect(
                self.on_installation_step_finished)

            installation_widget.process_installation()
        elif self.widget_index == 2:  # Clone Widget
            self.b_next.setEnabled(False)
            self.b_back.setEnabled(False)

            clone_widget = self.widgets[2]

            try:
                clone_widget.cloning_finished.disconnect()
            except (RuntimeError, TypeError) as e:
                print(e)

            clone_widget.cloning_finished.connect(self.on_cloning_finished)

            clone_widget.process_cloning()

    def on_installation_step_finished(self, success):
        self.b_next.setEnabled(True)
        if success:
            # Grab game_dir and executable path
            installation_widget = self.widgets[1]
            self.game_exe_path = installation_widget.line_edit.text()
            self.game_dir = os.path.dirname(self.game_exe_path)
            game_api = installation_widget.selected_api

            self.current_api = game_api

            # pass to clone widget
            clone_widget = self.widgets[2]
            clone_widget.set_game_directory(self.game_dir)

            self.change_widget(1)

    def on_cloning_finished(self, success):
        if success and self.widget_index > 1:
            scripts_core.manager_core.add_game(
                self.game_exe_path, self.game_dir)

            if self.current_api == "D3D 8":
                self.change_widget(1)
                self.b_back.setEnabled(False)

            self.b_next.setText("Close")
            self.b_next.setEnabled(True)
            self.b_next.clicked.disconnect()
            self.b_next.clicked.connect(self.close)
        else:
            self.b_next.setEnabled(True)
            self.b_back.setEnabled(True)

    def change_widget(self, direction=1):
        # Deletes previous widget, if I change my mind...
        # self.ly_main.removeWidget(self.current_widget)
        # self.current_widget.deleteLater()

        self.current_widget.hide()

        if direction == 1:
            self.widget_index = self.widget_index + 1
        else:
            self.widget_index = self.widget_index - 1

        self.current_widget = self.widgets[self.widget_index]

        # Insert widget
        # 1 refers to self.current_widget [0: text, 1: dynamic_widget, 2: buttons]
        self.ly_main.removeWidget(self.current_widget)
        self.ly_main.insertWidget(1, self.current_widget)
        self.current_widget.show()

        self.update_buttons()

    def on_start_finished(self, success):
        if success:
            self.is_start_ready = True
            self.update_buttons()

    def update_buttons(self):

        # To fix closing on next text button
        try:
            self.b_next.clicked.disconnect()
        except (RuntimeError, TypeError):
            pass

        self.b_next.clicked.connect(self.on_next_clicked)

        if self.widget_index == 0:
            self.b_back.setEnabled(False)
        else:
            self.b_back.setEnabled(True)

        if self.widget_index == len(self.widgets) - 1:
            self.b_next.setEnabled(True)
            self.b_next.setText("Install")
        else:
            self.b_next.setEnabled(True)
            self.b_next.setText("Next")

            if self.widget_index == 0:
                self.b_next.setEnabled(self.is_start_ready)
            else:
                self.b_next.setEnabled(True)

        if self.is_uninstall:
            self.b_next.hide()
            self.b_back.hide()
            self.b_uninstall.hide()
            self.b_home.show()
        else:
            self.b_next.show()
            self.b_back.show()
            self.b_uninstall.show()
            self.b_home.hide()

    def switch_to_uninstall(self):
        self.is_uninstall = True
        self.current_widget.hide()
        self.ly_main.removeWidget(self.current_widget)
        self.current_widget = UninstallWidget()

        self.ly_main.insertWidget(1, self.current_widget)
        self.current_widget.show()

        self.update_buttons()

    def switch_to_home(self):
        self.is_uninstall = False
        self.widget_index = 0
        self.current_widget.hide()
        self.ly_main.removeWidget(self.current_widget)
        self.current_widget = self.widgets[0]

        self.ly_main.insertWidget(1, self.current_widget)
        self.current_widget.show()

        self.update_buttons()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setOrganizationName("Ishidawg")
    app.setApplicationName("ReshadeInstaller")

    local_dir = get_localdir()
    icon_path = os.path.join(local_dir, "assets", "logo.png")

    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
