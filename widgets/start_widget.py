import sys

from PySide6.QtWidgets import (
  QApplication,
  QLabel,
  QMainWindow,
  QPushButton,
  QVBoxLayout,
  QWidget,
  QProgressBar
)

from PySide6.QtCore import Qt, QThread, Signal

from scripts_core.download_core import DownloadWorker

# l:    label
# c:    container
# ly:   layout
# b:    button
# p:    progress

class StartWidget(QWidget):
  process_finished = Signal(bool)

  def __init__(self):
    super().__init__()

    # Create layout
    ly = QVBoxLayout()
    ly.setAlignment(Qt.AlignCenter | Qt.AlignmentFlag.AlignCenter)

    # Label
    l_description = QLabel("This is a unofficial reshade installer for linux, intented to be used with proton applications, but it may also work with wine games.")
    l_description.setWordWrap(True)
    l_description.setAlignment(Qt.AlignmentFlag.AlignCenter)
    l_description.setStyleSheet("font-size: 12pt; font-weight: 100;")
    l_description.setMargin(15) # Don't know if there is a better way than set a 'spacing' like this, cuz this was introduced in Qt 4.0

    # Progress bar
    self.p_bar = QProgressBar()
    self.p_bar.setFixedWidth(400)
    self.p_bar.setTextVisible(True)
    self.p_bar.setAlignment(Qt.AlignCenter)
    self.p_bar.setRange(0, 100)
    self.p_bar.setValue(0)

    # Add widgets
    ly.addWidget(l_description)
    ly.setSpacing(5)
    ly.addWidget(self.p_bar)
    self.setLayout(ly)

    self.start_automatic_download()

  def start_automatic_download(self):
    # Thread Setup
    self.thread = QThread()
    self.worker = DownloadWorker()
    self.worker.moveToThread(self.thread)

    self.thread.started.connect(self.start_animation)

    self.thread.started.connect(self.worker.run)

    self.worker.status_update.connect(self.update_bar_text)

    self.worker.finished.connect(self.on_success)
    self.worker.error.connect(self.on_error)

    self.worker.finished.connect(self.thread.quit)
    self.worker.finished.connect(self.worker.deleteLater)
    self.thread.finished.connect(self.thread.deleteLater)

    self.thread.start()

  def start_animation(self):
    self.p_bar.setRange(0, 0)

  def update_bar_text(self, text):
    self.p_bar.setFormat(text)

  def on_success(self, draft):
    self.p_bar.setRange(0, 100)
    self.p_bar.setValue(100)
    self.p_bar.setFormat("Reshade downloaded!")
    self.process_finished.emit(True)

  def on_error(self, err):
    self.p_bar.setRange(0, 100)
    self.p_bar.setValue(0)
    self.p_bar.setFormat(f"Error: {err}")
    self.process_finished.emit(False)

