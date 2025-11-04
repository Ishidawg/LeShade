from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QHBoxLayout, QVBoxLayout, QFileDialog, QLineEdit, QPushButton, QRadioButton
from core import ReshadeInstallerBuilder
from PySide6.QtCore import Qt
import sys

class TitleLabel(QLabel):
  def __init__(self, text):
    super().__init__(f"<font size=6>{text}</font>")
    self.setAlignment(Qt.AlignCenter)
    self.setContentsMargins(0, 20, 0, 0)

class SubTitleLabel(QLabel):
  def __init__(self, text):
    super().__init__(f"<font size=5>{text}</font>")
    self.setAlignment(Qt.AlignLeft)
    self.setContentsMargins(0, 20, 0, -18)

class BodyLabel(QLabel):
  def __init__(self, text):
    super().__init__(f"{text}")
    self.setAlignment(Qt.AlignJustify)
    self.setWordWrap(True)

class LabelFactory():
  def createLabel(self, label_type, text):
    match label_type:
      case "title":       return TitleLabel(text)
      case "sub_title":   return SubTitleLabel(text)
      case "body":        return BodyLabel(text)

    return print("You did not use a valid label_type")


class MainWindow(QMainWindow):

  def __init__(self):
    super().__init__()

    self.labelFactory = LabelFactory()

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

    # Main label stuff
    label1 = self.labelFactory.createLabel("title", "Reshade installer for proton games!")
    label2 = self.labelFactory.createLabel("body", "This is a <i>university project</i> that kinda works! The porpuse is to make reshade installation a bit easier. You just need to select the <b>root directory</b> <i>(where the .exe is)</i>, the application architecture and the rendering API. <font color=#ee2c2c><b>This is only intended for proton games.</b></font>")
    label3 = self.labelFactory.createLabel("sub_title", "Select the game directory")

    # Brose stuff NEW!!
    self.line_edit = QLineEdit()
    self.line_edit.setPlaceholderText("Your game root directory")
    self.browse_button = QPushButton("Browse")

    # Browse stuff OLD
    #line_edit = QLineEdit()
    #line_edit.setPlaceholderText("You game directory")
    #browse_button = QPushButton("Browse")
    #file_dialog = QFileDialog()

    # Game architecture
    label4 = self.labelFactory.createLabel("sub_title", "Select the game architecture")
    label5 = self.labelFactory.createLabel("body", "As this is still in <b>early development state</b>, you need to know if you game is 32 or 64 bit. <i>Later on I will check it on PCGW. For now you will need to select the matter</i>. If you don't know nothing about, check on <a href='https://www.pcgamingwiki.com/wiki/Home'>PCGamingWiki</a>.")
    self.bit_32_radio = QRadioButton("32bit")
    self.bit_64_radio = QRadioButton("64bit")
    self.bit_64_radio.setChecked(True)

    # Rendering API
    label6 = self.labelFactory.createLabel("sub_title", "Select the rendering API")
    self.vulkan_radio = QRadioButton("Vulkan")
    self.d3d9_radio = QRadioButton("DirectX 9")
    self.d3d10_radio = QRadioButton("DirectX 10")
    self.vulkan_radio.setChecked(True)

    # Install
    self.install_button = QPushButton("Install")

    # Status: means what's going on under the hood
    self.status_label = self.labelFactory.createLabel("body", "Installed!")
    self.status_label.setAlignment(Qt.AlignCenter)
    self.status_label.setContentsMargins(0, 10, 0, 10)

    # Draw stuff
    main_layout.addWidget(label1)
    main_layout.addWidget(label2)
    main_layout.addWidget(label3)

    main_layout.addWidget(browse_container)
    browse_layout.addWidget(self.line_edit)
    browse_layout.addWidget(self.browse_button)

    main_layout.addWidget(label4)
    main_layout.addWidget(label5)
    main_layout.addWidget(architecture_container)
    architecture_layout.addWidget(self.bit_32_radio)
    architecture_layout.addWidget(self.bit_64_radio)

    main_layout.addWidget(label6)
    main_layout.addWidget(rendering_container)
    
    for rendering in (self.vulkan_radio, self.d3d9_radio, self.d3d10_radio):
      rendering_layout.addWidget(rendering)

    main_layout.addWidget(self.install_button)
    main_layout.addWidget(self.status_label)

    # Create a 'core' instance
    self.builder = ReshadeInstallerBuilder()

    self.builder.installation_progress_updated.connect(self.update_status)

    # Connect UI to observable slots
    self.install_button.clicked.connect(self.on_install_clicked)
    self.browse_button.clicked.connect(self.on_browse_clicked)

    self.run_initial_setup()

  def update_status(self, message: str):
    self.status_label.setText(message)
    QApplication.processEvents() # Ensure the UI updates

  def on_browse_clicked(self):
    directory = QFileDialog.getExistingDirectory(self, "Select the game root directory")

    if directory:
      self.line_edit.setText(directory)

  def on_install_clicked(self):
    try:
      game_dir = self.line_edit.text().strip()

      if not game_dir:
        raise ValueError("ERROR: Game directory cannot be empty")

      bit = "64bit" if self.bit_64_radio.isChecked() else "32bit"

      api = None

      match api:
        case self.vulkan_radio.isChecked(): api = "Vulkan"
        case self.d3d9_radio.isChecked(): api = "d3d9"
        case self.d3d10_radio.isChecked(): api = "d3d10"

      self.install_button.setEnabled(False) # Prevents double click that can be fuck stuff up
      self.update_status("Starting Installation...")

      # Calling builder that will emit signals to the update_status
      self.builder.set_game_architecture(bit)
      self.builder.set_game_api(api)
      self.builder.set_game_directory(game_dir)

      reshade_installer = self.builder.get_reshade_product()
      self.update_status(f"Used settings: {reshade_installer}")

      for message in reshade_installer.install():
        self.update_status(message)
    except Exception as error:
      self.update_status(f"ERROR: {error}")
    finally:
      self.install_button.setEnabled(True) # Enables the button when the installation ends

  def run_initial_setup(self):
    try:
      self.update_status("Searching for reshade.exe")
      self.builder.find_and_unzip('/home', 'ReShade_Setup*.exe')
      self.builder.clone_shaders()
      self.update_status("Ready to install!")
    except Exception as error:
      self.update_status(f"ERROR: setup failed: {error}")

if __name__ == "__main__":
  app = QApplication(sys.argv)
  window = MainWindow()
  window.show()
  sys.exit(app.exec())
