import sys

from PySide6.QtWidgets import (
  QApplication,
  QLabel,
  QMainWindow,
  QPushButton,
  QVBoxLayout,
  QWidget,
  QCheckBox,
  QProgressBar
)

from PySide6.QtCore import Qt, QThread, Signal

from scripts_core.clone_core import CloneWorker

# l:    label
# c:    container
# ly:   layout
# b:    button
# cb:   checkbox
# p:    progress

class CloneShaderWidget(QWidget):
  cloning_finished = Signal(bool)

  def __init__(self):
    super().__init__()

    self.game_directory = None

    # Create layout
    ly = QVBoxLayout()
    ly.setAlignment(Qt.AlignTop | Qt.AlignmentFlag.AlignCenter)

    c_checkboxes = QWidget()
    ly_checkboxes = QVBoxLayout(c_checkboxes)
    ly_checkboxes.setAlignment(Qt.AlignTop | Qt.AlignmentFlag.AlignLeft)

    # Label
    l_description = QLabel("Select shaders you want to install:")
    l_description.setStyleSheet("font-size: 12pt; font-weight: 100;")
    l_description.setContentsMargins(10, 0, 0, 0)
    l_description.setAlignment(Qt.AlignmentFlag.AlignLeft)

    # Checkboxes and descriptions
    self.ch_default = QCheckBox("Crosire defaults")
    self.ch_default.setChecked(True)
    l_default = QLabel("Default shaders from crosire repository.")
    l_default.setStyleSheet("font-size: 10pt; font-weight: 100;")

    self.ch_prod80 = QCheckBox("Prod80")
    l_prod80 = QLabel("Highly advanced Color Effects, constrast, brightness...")
    l_prod80.setStyleSheet("font-size: 10pt; font-weight: 100;")

    self.ch_quint = QCheckBox("qUINT")
    l_quint = QLabel("General-purpose effects: bloom, deband, MXAO...")
    l_quint.setStyleSheet("font-size: 10pt; font-weight: 100;")

    # Progress bar
    self.p_bar = QProgressBar()
    self.p_bar.setFixedWidth(400)
    self.p_bar.setTextVisible(True)
    self.p_bar.setAlignment(Qt.AlignCenter)
    self.p_bar.setRange(0, 100)
    self.p_bar.setValue(0)

    # Add widgets
    ly.addWidget(l_description)
    ly.addWidget(c_checkboxes)

    ly_checkboxes.addWidget(self.ch_default)
    ly_checkboxes.addWidget(l_default)
    ly_checkboxes.addWidget(self.ch_prod80)
    ly_checkboxes.addWidget(l_prod80)
    ly_checkboxes.addWidget(self.ch_quint)
    ly_checkboxes.addWidget(l_quint)

    ly.addWidget(self.p_bar)

    self.setLayout(ly)

  def set_game_directory(self, path):
    self.game_directory = path

  def process_cloning(self):
    selections = []
    if self.ch_default.isChecked(): selections.append("default")
    if self.ch_prod80.isChecked(): selections.append("prod80")
    if self.ch_quint.isChecked(): selections.append("quint")

    if not selections:
      self.p_bar.setFormat("No shaders pack selected!")
      self.cloning_finished.emit(True)
      return

    if not self.game_directory:
      self.p_bar.setFormat("Error: There is no game directory!")
      self.cloning_finished.emit(False)
      return

    # Thread Setup
    self.thread = QThread()
    self.worker = CloneWorker()

    self.worker.setup(self.game_directory, selections)
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
    self.p_bar.setRange(0, 100)
    self.p_bar.setValue(100)
    self.p_bar.setFormat("Installation complete!")
    self.cloning_finished.emit(True)

  def on_error(self, err):
    self.p_bar.setRange(0, 100)
    self.p_bar.setValue(0)
    self.p_bar.setFormat(f"Error: {err}")
    self.cloning_finished.emit(False)
