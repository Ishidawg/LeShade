import sys

from PySide6.QtWidgets import (
  QApplication,
  QLabel,
  QMainWindow,
  QPushButton,
  QVBoxLayout,
  QWidget,
  QCheckBox
)

from PySide6.QtCore import Qt

# l:    label
# c:    container
# ly:   layout
# b:    button
# cb:   checkbox

class CloneShaderWidget(QWidget):

  def __init__(self):
    super().__init__()

    # Create layout
    ly = QVBoxLayout()
    ly.setAlignment(Qt.AlignTop | Qt.AlignmentFlag.AlignLeft)

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
    l_default = QLabel("Default shaders from crosire repository.")
    l_default.setStyleSheet("font-size: 10pt; font-weight: 100;")

    self.ch_prod80 = QCheckBox("Prod80")
    l_prod80 = QLabel("Highly advanced Color Effects, constrast, brightness...")
    l_prod80.setStyleSheet("font-size: 10pt; font-weight: 100;")

    self.ch_quint = QCheckBox("qUINT")
    l_quint = QLabel("General-purpose effects: bloom, deband, MXAO...")
    l_quint.setStyleSheet("font-size: 10pt; font-weight: 100;")

    # Add widgets
    ly.addWidget(l_description)
    ly.addWidget(c_checkboxes)

    ly_checkboxes.addWidget(self.ch_default)
    ly_checkboxes.addWidget(l_default)
    ly_checkboxes.addWidget(self.ch_prod80)
    ly_checkboxes.addWidget(l_prod80)
    ly_checkboxes.addWidget(self.ch_quint)
    ly_checkboxes.addWidget(l_quint)

    self.setLayout(ly)





