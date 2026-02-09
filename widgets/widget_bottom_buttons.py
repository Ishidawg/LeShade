from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QWidget,
    QPushButton
)

from PySide6.QtCore import Qt


class WidgetBottomButtons(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignBottom |
                            Qt.AlignmentFlag.AlignCenter)

        self.btn_back = QPushButton("Back")
        self.btn_next = QPushButton("Next")

        self.btn_back.setEnabled(True)
        self.btn_next.setEnabled(False)

        self.btn_back.hide()
        self.btn_next.hide()

        layout.addWidget(self.btn_back)
        layout.addWidget(self.btn_next)

        self.setLayout(layout)
