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
from PySide6.QtGui import QFont

# Import widgets
from widgets.start_widget import StartWidget
from widgets.installation_widget import InstallationWidget
from widgets.clone_widget import CloneShaderWidget

# l:    label
# c:    container
# ly:   layout
# b:    button

class MainWindow(QMainWindow): 

  def __init__(self):
    super().__init__()

    # Set Widgets
    S_FIRST = StartWidget()
    S_SECOND = InstallationWidget()
    S_THIRD = CloneShaderWidget()

    self.widgets = [S_FIRST, S_SECOND, S_THIRD]
    self.widget_index = 0

    self.current_widget = self.widgets[0]

    WINDOW_WIDTH = 620
    WINDOW_HEIGHT = 400

    self.setWindowTitle("Reshade Installer")
    self.setFixedWidth(WINDOW_WIDTH)
    self.setFixedHeight(WINDOW_HEIGHT)

    # Main container
    c_main = QWidget()
    c_main.setContentsMargins(40, 0, 40, 0)
    self.setCentralWidget(c_main)
    self.ly_main = QVBoxLayout(c_main)

    # Fixed text container and labels
    c_top_text = QWidget()
    c_top_text.setContentsMargins(0, 0, 0, 40)
    ly_top_text = QVBoxLayout(c_top_text)
    ly_top_text.setAlignment(Qt.AlignTop | Qt.AlignmentFlag.AlignCenter)

    l_title = QLabel("Reshade Installer")
    l_title.setStyleSheet("font-size: 22pt;")
    l_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

    l_subtitle = QLabel("Intended for proton games")
    l_subtitle.setStyleSheet("font-size: 12pt; font-weight: 100;")
    l_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

    # Fixed button container and thy self
    b_bottom_buttons = QWidget()
    b_bottom_buttons.setContentsMargins(0, 0, 0, 10)
    ly_bottom_buttons = QHBoxLayout(b_bottom_buttons)
    ly_bottom_buttons.setAlignment(Qt.AlignBottom | Qt.AlignmentFlag.AlignCenter)

    self.b_next = QPushButton("Next", self)
    self.b_back = QPushButton("Back", self)

    # AddWidgets
    self.ly_main.addWidget(c_top_text)
    self.ly_main.addWidget(self.current_widget)
    self.ly_main.addWidget(b_bottom_buttons)

    # Fixed text
    ly_top_text.addWidget(l_title)
    ly_top_text.addWidget(l_subtitle)
    ly_bottom_buttons.addWidget(self.b_back)
    ly_bottom_buttons.addWidget(self.b_next)
    
    self.b_next.clicked.connect(lambda: self.change_widget(1)) 
    self.b_back.clicked.connect(lambda: self.change_widget(-1))
    self.update_buttons()

  def change_widget(self, direction = 1):
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

  def update_buttons(self):
    if self.widget_index == 0:
      self.b_back.setEnabled(False)
    else:
      self.b_back.setEnabled(True)

    if self.widget_index == len(self.widgets) - 1:
      self.b_next.setEnabled(False)
      self.b_next.setText("Install")
    else:
      self.b_next.setEnabled(True)
      self.b_next.setText("Next")

if __name__ == "__main__":
  app = QApplication(sys.argv)

  window = MainWindow()
  window.show()
  sys.exit(app.exec())