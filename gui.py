from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QHBoxLayout, QVBoxLayout, QFileDialog, QLineEdit, QPushButton, QRadioButton
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):


  def __init__(self):
    super().__init__()

    WINDOW_WIDTH = 620

    self.setWindowTitle("Reshade Installer")
    self.setFixedWidth(WINDOW_WIDTH)

    # Main container
    container = QWidget()
    self.setCentralWidget(container)
    main_layout = QVBoxLayout(container)

    # Inner Containers
    browse_container = QWidget()
    browse_layout = QHBoxLayout(browse_container)

    architecture_container = QWidget()
    architecture_layout = QHBoxLayout(architecture_container)
    architecture_layout.setAlignment(Qt.AlignCenter)

    rendering_container = QWidget()
    rendering_layout = QHBoxLayout(rendering_container)
    rendering_layout.setAlignment(Qt.AlignCenter)

    # Main text stuff
    label1 = QLabel("<font size=5>Reshade installer for proton games!<font>")
    label1.setAlignment(Qt.AlignCenter)

    label2 = QLabel("This is a <i>university project</i> that kinda works! The porpuse is to make reshade installation a bit easier. You just need to select the <b>root directory</b> <i>(where the .exe is)</i>, the application architecture and the rendering API. <font color=#ee2c2c><b>This is only intended for proton games.</b></font>")
    label2.setAlignment(Qt.AlignJustify)
    label2.setMaximumWidth(WINDOW_WIDTH)
    label2.setWordWrap(True)


    label3 = QLabel("<font size=5>Select the game directory</font>")
    label3.setAlignment(Qt.AlignLeft)
    label3.setContentsMargins(0, 20, 0, -40) # (left: int, top: int, right: int, bottom: int)

    # Browse stuff
    line_edit = QLineEdit()
    line_edit.setPlaceholderText("You game directory")

    browse_button = QPushButton("Browse")

    # file_dialog = QFileDialog()

    # Game architecture
    label4 = QLabel("<font size=5>Select the game architecture</font>")
    label4.setAlignment(Qt.AlignLeft)
    label4.setContentsMargins(0, 20, 0, -20)

    label5 = QLabel("As this is still in <b>early development state</b>, you need to know if you game is 32 or 64 bit. <i>Later on I will check it on PCGW. For now you will need to select the matter</i>. If you don't know nothing about, check on <a href='https://www.pcgamingwiki.com/wiki/Home'>PCGamingWiki</a>.")
    label5.setAlignment(Qt.AlignJustify)
    label5.setMaximumWidth(WINDOW_WIDTH)
    label5.setWordWrap(True)

    bit_32_radio = QRadioButton("32bit")
    bit_64_radio = QRadioButton("64bit")

    # Rendering API
    label6 = QLabel("<font size=5>Select the rendering API</font>")
    label6.setAlignment(Qt.AlignLeft)
    label6.setContentsMargins(0, 20, 0, -20)

    vulkan_radio = QRadioButton("Vulkan")
    d3d9_radio = QRadioButton("DirectX 9c")
    d3d10_radio = QRadioButton("DirectX 10")

    # Install
    install_button = QPushButton("Install")
    # install_button.setFixedSize(WINDOW_WIDTH / 2, WINDOW_WIDTH / 4)

    # Draw stuff
    main_layout.addWidget(label1)
    main_layout.addWidget(label2)
    main_layout.addWidget(label3)

    main_layout.addWidget(browse_container)
    browse_layout.addWidget(line_edit)
    browse_layout.addWidget(browse_button)

    main_layout.addWidget(label4)
    main_layout.addWidget(label5)
    main_layout.addWidget(architecture_container)
    architecture_layout.addWidget(bit_32_radio)
    architecture_layout.addWidget(bit_64_radio)

    main_layout.addWidget(label6)
    main_layout.addWidget(rendering_container)
    
    for rendering in (vulkan_radio, d3d9_radio, d3d10_radio):
      rendering_layout.addWidget(rendering)

    main_layout.addWidget(install_button)


app = QApplication()

window = MainWindow()
window.show()

app.exec()
