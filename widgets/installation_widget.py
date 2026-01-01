import sys
import os
import struct

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
  QFileDialog,
  QProgressBar
)

from PySide6.QtCore import Qt, QThread, Signal

from scripts_core.installation_core import InstallationWorker

# l:    label
# c:    container
# ly:   layout
# b:    button
# r:    radio
# p:    progress

class InstallationWidget(QWidget):
  installation_finished = Signal(bool)

  def __init__(self):
    super().__init__()

    self.reshade_source_dir = None

    # Create layout and containers
    ly = QVBoxLayout()
    ly.setAlignment(Qt.AlignTop | Qt.AlignmentFlag.AlignCenter)

    # Creates only a layout instead of container to fix widgets not appearing in GTK
    ly_browse = QHBoxLayout()

    c_api = QWidget()
    ly_api = QHBoxLayout(c_api)
    ly_api.setAlignment(Qt.AlignCenter | Qt.AlignmentFlag.AlignCenter)
    ly_api.setSpacing(40)

    # Widgets
    l_exe = QLabel("Select game executable")
    l_exe.setContentsMargins(10, 0, 0, 0)
    l_exe.setWordWrap(True)
    l_exe.setAlignment(Qt.AlignmentFlag.AlignLeft)
    l_exe.setStyleSheet("font-size: 12pt; font-weight: 100;")

    self.line_edit = QLineEdit()
    self.browse_button = QPushButton("Browse")

    l_api = QLabel("Select game API")
    l_api.setContentsMargins(10, 0, 0, 0)
    l_api.setWordWrap(True)
    l_api.setAlignment(Qt.AlignmentFlag.AlignLeft)
    l_api.setStyleSheet("font-size: 12pt; font-weight: 100;")

    self.r_vulkan = QRadioButton("Vulkan")
    self.r_d3d9 = QRadioButton("DirectX 9")
    self.r_d3d10 = QRadioButton("DirectX 10")
    self.r_vulkan.setChecked(True)

    # Progress bar
    self.p_bar = QProgressBar()
    self.p_bar.setTextVisible(True)
    self.p_bar.setAlignment(Qt.AlignCenter | Qt.AlignmentFlag.AlignCenter)
    self.p_bar.setRange(0, 100)
    self.p_bar.setValue(0)

    # Add widgets
    ly.addWidget(l_exe)

    ly_browse.addWidget(self.line_edit)
    ly_browse.addWidget(self.browse_button)
    ly.addLayout(ly_browse)
    ly.addSpacing(20)

    ly.addWidget(l_api)
    ly.addWidget(c_api)


    for api in (self.r_vulkan, self.r_d3d9, self.r_d3d10):
      ly_api.addWidget(api)

    ly.addWidget(self.p_bar)

    self.setLayout(ly)

    # Connect Functions
    self.browse_button.clicked.connect(self.on_browse_clicked)

  # public function
  def on_browse_clicked(self):
    file_name, _ = QFileDialog.getOpenFileName(self, "Select game executable", os.path.expanduser("~"), "Executables (*.exe)")
    
    if file_name:
      self.line_edit.setText(file_name)

  def set_reshade_source(self, path):
    self.reshade_source_dir = path

  def process_installation(self):
    game_exe = self.line_edit.text()

    if not game_exe or not os.path.exists(game_exe):
      self.p_bar.setFormat("Error: Invalid game path!")
      self.p_bar.setValue(0)
      self.installation_finished.emit(False)
      return

    if not self.reshade_source_dir:
      self.p_bar.setFormat("Error: Reshade was not found!")
      self.installation_finished.emit(False)
      return

    api = "Vulkan"
    if self.r_d3d9.isChecked(): api = "DirectX 9"
    elif self.r_d3d10.isChecked(): api = "DirectX 10"

    # Thread Setup
    self.thread = QThread()
    self.worker = InstallationWorker()
    self.worker.setup(self.reshade_source_dir, game_exe, api)
    self.worker.moveToThread(self.thread)

    self.thread.started.connect(self.worker.run)

    self.worker.status_update.connect(self.update_bar_text)
    self.worker.progress_update.connect(self.p_bar.setValue)
    
    self.worker.finished.connect(self.on_success)
    self.worker.error.connect(self.on_error)

    self.worker.finished.connect(self.thread.quit)
    self.worker.finished.connect(self.worker.deleteLater)
    self.thread.finished.connect(self.thread.deleteLater)

    self.thread.start()

  def update_bar_text(self, text):
    self.p_bar.setFormat(f"{text} (%p%)")

  def on_success(self):
    self.p_bar.setValue(100)
    self.p_bar.setFormat("Installation Successful!")
    self.installation_finished.emit(True)

  def on_error(self, err_msg):
    self.p_bar.setValue(0)
    self.p_bar.setFormat("Error")
    self.p_bar.setToolTip(f"Detail: {err_msg}")
    self.installation_finished.emit(False)
    