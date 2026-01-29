from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget
)

# l:    label
# c:    container
# ly:   layout
# b:    button
# p:    progress


class HomeWidget(QWidget):

    def __init__(self):
        super().__init__()

        ly = QVBoxLayout()
        ly.setAlignment(Qt.AlignTop | Qt.AlignmentFlag.AlignCenter)

        ly_buttons = QHBoxLayout()
        ly_buttons.setAlignment(Qt.AlignTop | Qt.AlignmentFlag.AlignCenter)

        # Subtitle
        l_subtitle = QLabel(
            "LeShade is a manager for reshade installations on linux. It's a native tool that can install and uninstall reshade across many games that uses proton or WINE, also it supports Direct3D 8.0.")
        l_subtitle.setWordWrap(True)
        l_subtitle.setStyleSheet("font-style: 12pt; font-weight: 100;")
        l_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l_subtitle.setMargin(15)

        # Buttons
        self.b_install = QPushButton("Install")
        self.b_uninstall = QPushButton("Uninstall")

        # Add Widgets
        ly.addWidget(l_subtitle)
        ly.addSpacing(5)

        ly_buttons.addWidget(self.b_uninstall)
        ly_buttons.addWidget(self.b_install)

        ly.addLayout(ly_buttons)

        self.setLayout(ly)
