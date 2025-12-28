import sys

from PySide6.QtWidgets import (
  QApplication,
  QLabel,
  QMainWindow,
  QPushButton,
  QVBoxLayout,
  QHBoxLayout,
  QWidget,
  QLineEdit,
  QRadioButton,
  QFileDialog
)

from PySide6.QtCore import Qt

# l:    label
# c:    container
# ly:   layout
# b:    button
# r:    radio

class InstallationWidget(QWidget):

  def __init__(self):
    super().__init__()

    # Create layout and containers
    ly = QVBoxLayout()
    ly.setAlignment(Qt.AlignTop | Qt.AlignmentFlag.AlignLeft)

    c_browse = QWidget()
    c_browse.setContentsMargins(0, 0, 0, 40)
    ly_browse = QHBoxLayout(c_browse)

    c_api = QWidget()
    ly_api = QHBoxLayout(c_api)
    ly_api.setAlignment(Qt.AlignCenter | Qt.AlignmentFlag.AlignCenter)
    ly_api.setSpacing(40)

    # Widgets
    l_exe = QLabel("Select games executable")
    l_exe.setContentsMargins(10, 0, 0, 0)
    l_exe.setWordWrap(True)
    l_exe.setAlignment(Qt.AlignmentFlag.AlignLeft)
    l_exe.setStyleSheet("font-size: 12pt; font-weight: 100;")

    self.line_edit = QLineEdit()
    self.browse_button = QPushButton("Browse")

    l_api = QLabel("Select games API")
    l_api.setContentsMargins(10, 0, 0, 0)
    l_api.setWordWrap(True)
    l_api.setAlignment(Qt.AlignmentFlag.AlignLeft)
    l_api.setStyleSheet("font-size: 12pt; font-weight: 100;")

    self.r_vulkan = QRadioButton("Vulkan")
    self.r_d3d9 = QRadioButton("DirectX 9")
    self.r_d3d10 = QRadioButton("DirectX 10")
    self.r_vulkan.setChecked(True)

    # Connect Functions
    self.browse_button.clicked.connect(self.on_browse_clicked)

    # Add widgets
    ly.addWidget(l_exe)
    ly.addWidget(c_browse)
    ly.addWidget(l_api)
    ly.addWidget(c_api)

    ly_browse.addWidget(self.line_edit)
    ly_browse.addWidget(self.browse_button)

    for api in (self.r_vulkan, self.r_d3d9, self.r_d3d10):
      ly_api.addWidget(api)

    self.setLayout(ly)

  def on_browse_clicked(self):
    directory = QFileDialog.getOpenFileName(self, "Select the game executable")

    if directory:
      self.line_edit.setText(directory[0])

  def on_next_clicked(self):
    try:
      game_dir = self.line_edit.text().strip()

      if not game_dir:
        raise ValueError("ERROR: Game directory cannot be empty")

      api = None

      if self.vulkan_radio.isChecked():
        api = "Vulkan"
      elif self.d3d9_radio.isChecked():
        api = "d3d9"
      elif self.d3d10_radio.isChecked():
        api = "d3d10"

      self.install_button.setEnabled(False) # Prevents double click that can be fuck stuff up
      self.update_status("Starting Installation...")

      # Calling builder that will emit signals to the update_status
      self.builder.set_game_architecture(game_dir)
      self.builder.set_game_api(api)
      self.builder.set_game_directory(os.path.dirname(game_dir)) # Sendind the entire path

      reshade_installer = self.builder.get_reshade_product()
      self.update_status(f"Used settings: {reshade_installer}")

      for message in reshade_installer.install():
        self.update_status(message)
    except Exception as error:
      self.update_status(f"ERROR: {error}")
    finally:
      self.install_button.setEnabled(True) # Enables the button when the installation ends





