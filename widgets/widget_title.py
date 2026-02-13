from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QWidget,
    QLabel
)

from PySide6.QtCore import Qt


class WidgetTitle(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop |
                            Qt.AlignmentFlag.AlignCenter)

        title = QLabel("LeShade")
        title.setStyleSheet("font-size: 28pt; font-weight: 600")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        subtitle = QLabel("ReShade Manager")
        subtitle.setStyleSheet("font-size: 12pt; font-weight: 100")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        layout.addWidget(title)
        layout.addWidget(subtitle)

        self.setLayout(layout)
