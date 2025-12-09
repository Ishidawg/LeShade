from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QHBoxLayout, QVBoxLayout, QFileDialog, QLineEdit, QPushButton, QRadioButton
from PySide6.QtGui import QFont, QPixmap
from core import ReshadeInstallerBuilder
from PySide6.QtCore import Qt, QThread
import sys
import os

class TitleLabel(QLabel):
  def __init__(self, font, text):
    super().__init__(f"{text}")
    self.setAlignment(Qt.AlignCenter)
    self.setContentsMargins(0, 30, 0, 0)
    self.setFont(font)

class SubTitleLabel(QLabel):
  def __init__(self, font, text):
    super().__init__(f"{text}")
    self.setAlignment(Qt.AlignLeft)
    self.setFont(font)
    self.setContentsMargins(34, 0, 0, 0)
    self.setFixedHeight(28)

class BodyLabel(QLabel):
  def __init__(self, font, text):
    super().__init__(f"{text}")
    self.setAlignment(Qt.AlignCenter)
    self.setWordWrap(True)
    self.setFont(font)

class LabelFactory():
  def createLabel(self, label_type, font, text):
    match label_type:
      case "title":       return TitleLabel(font, text)
      case "sub_title":   return SubTitleLabel(font, text)
      case "body":        return BodyLabel(font, text)

    return print("You did not use a valid label_type")


class MainWindow(QMainWindow):

  def __init__(self):
    super().__init__()

    WINDOW_WIDTH = 620
    WINDOW_HEIGHT = 760

    # Fonts style (where it used - what font is - font wheight)
    TITLE_OVERPASS_FONT = QFont("Overpass", 24, QFont.Bold)
    TITLE_OVERPASS_FONT_200 = QFont("Overpass", 13, QFont.ExtraLight)
    SUBTITLE_OVERPASS_FONT_400 = QFont("Overpass", 18, QFont.Normal)
    GLOBAL_OVERPASS_FONT = QFont("Overpass", 11)

    self.labelFactory = LabelFactory()

    self.setWindowTitle("Reshade Installer")
    self.setFixedWidth(WINDOW_WIDTH)
    self.setFixedHeight(WINDOW_HEIGHT)
    self.setFont(GLOBAL_OVERPASS_FONT)

    # Main container
    container = QWidget()
    container.setContentsMargins(40, 0, 40, 0) # Set vertical margins
    self.setCentralWidget(container)
    main_layout = QVBoxLayout(container)

    # Inner Containers
    browse_container = QWidget()
    browse_container.setContentsMargins(0, 0, 0, 40)
    browse_layout = QHBoxLayout(browse_container)

    #architecture_container = QWidget()
    #architecture_container.setContentsMargins(0, 0, 0, 40)
    #architecture_layout = QHBoxLayout(architecture_container)
    #architecture_layout.setAlignment(Qt.AlignLeft)

    rendering_container = QWidget()
    rendering_container.setContentsMargins(0, 0, 0, 40)
    rendering_layout = QHBoxLayout(rendering_container)
    rendering_layout.setAlignment(Qt.AlignLeft)

    # Main label stuff
    ## Title
    label_title = self.labelFactory.createLabel("title", TITLE_OVERPASS_FONT, "Reshade installer")
    label_title.setFixedHeight(60)
    label_title_bottom = self.labelFactory.createLabel("body", TITLE_OVERPASS_FONT_200, "intended just for pronton games")
    label_title_bottom.setFixedHeight(28)
    
    ## Project description
    label_description = self.labelFactory.createLabel("body", TITLE_OVERPASS_FONT_200, "This is a unofficial reshade installer for linux, intented to be used with\nproton applications, but it may also work with wine games.")
    label_description.setFixedHeight(120)

    ## Directory step
    label_directory_step = self.labelFactory.createLabel("sub_title", SUBTITLE_OVERPASS_FONT_400, "Select games executable")
    self.line_edit = QLineEdit()
    self.browse_button = QPushButton("Browse")

    folder_icon_draw = QLabel(self)
    folder_icon = QPixmap("./images/step_icons/folder_icon.png")
    folder_icon_draw.setPixmap(folder_icon)
    folder_icon_draw.setGeometry(56, 230, folder_icon_draw.width(), folder_icon_draw.height())

    # Game architecture step
    #label_arch_step = self.labelFactory.createLabel("sub_title", SUBTITLE_OVERPASS_FONT_400, "Select games architecture")
    #self.bit_32_radio = QRadioButton("32bit")
    #self.bit_64_radio = QRadioButton("64bit")
    #self.bit_64_radio.setChecked(True)

    #arch_icon_draw = QLabel(self)
    #arch_icon = QPixmap("./images/step_icons/arch_icon.png")
    #arch_icon_draw.setPixmap(arch_icon)
    #arch_icon_draw.setGeometry(56, 362, arch_icon_draw.width(), arch_icon_draw.height())

    # Rendering API step
    label_api_step = self.labelFactory.createLabel("sub_title", SUBTITLE_OVERPASS_FONT_400, "Select games rendering API")
    self.vulkan_radio = QRadioButton("Vulkan")
    self.d3d9_radio = QRadioButton("DirectX 9")
    self.d3d10_radio = QRadioButton("DirectX 10")
    self.vulkan_radio.setChecked(True)

    api_icon_draw = QLabel(self)
    api_icon = QPixmap("./images/step_icons/api_icon.png")
    api_icon_draw.setPixmap(api_icon)
    api_icon_draw.setGeometry(56, 405, api_icon_draw.width(), api_icon_draw.height())

    # Install
    self.install_button = QPushButton("Install Reshade")

    # Status: means what's going on under the hood
    self.status_label = self.labelFactory.createLabel("body", GLOBAL_OVERPASS_FONT, "Installed!")
    self.status_label.setAlignment(Qt.AlignCenter)
    self.status_label.setContentsMargins(0, 40, 0, 5)

    # Draw stuff
    main_layout.addWidget(label_title)
    main_layout.addWidget(label_title_bottom)
    main_layout.addWidget(label_description)
    main_layout.addWidget(label_directory_step)

    main_layout.addWidget(browse_container)
    browse_layout.addWidget(self.line_edit)
    browse_layout.addWidget(self.browse_button)

    # main_layout.addWidget(label_arch_step)
    # main_layout.addWidget(architecture_container)
    #architecture_layout.addWidget(self.bit_32_radio)
    #architecture_layout.addWidget(self.bit_64_radio)

    main_layout.addWidget(label_api_step)
    main_layout.addWidget(rendering_container)
    
    for rendering in (self.vulkan_radio, self.d3d9_radio, self.d3d10_radio):
      rendering_layout.addWidget(rendering)

    main_layout.addWidget(self.install_button)
    main_layout.addWidget(self.status_label)

    # Create a 'core' instance
    self.builder = ReshadeInstallerBuilder()

    # Connects the installation progress to the update_status label
    self.builder.installation_progress_updated.connect(self.update_status)

    # Creates a thread and moves the builder to it
    self.installation_thread = QThread()
    self.builder.moveToThread(self.installation_thread)

    # Connects the signal to the thread
    self.installation_thread.started.connect(self.builder.run_initial_setup)

    # Makes thread stop when installetion completes ALSO clean memory where the thread was
    self.builder.finished.connect(self.installation_thread.quit)
    self.builder.finished.connect(self.builder.deleteLater) # self.builder DELETES THE builder, otherwise the application will close
    self.installation_thread.finished.connect(self.installation_thread.deleteLater)

    # Connect UI to observable slots
    self.install_button.clicked.connect(self.on_install_clicked)
    self.browse_button.clicked.connect(self.on_browse_clicked)

    self.installation_thread.start()

  def update_status(self, message: str):
    self.status_label.setText(message)
    QApplication.processEvents() # Ensure the UI updates

  def on_browse_clicked(self):
    # directory = QFileDialog.getExistingDirectory(self, "Select the game executable")
    directory = QFileDialog.getOpenFileName(self, "Select the game executable")

    if directory:
      self.line_edit.setText(directory[0])

  def on_install_clicked(self):
    try:
      game_dir = self.line_edit.text().strip()

      if not game_dir:
        raise ValueError("ERROR: Game directory cannot be empty")

      #bit = "64bit" if self.bit_64_radio.isChecked() else "32bit"


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
      # self.builder.set_game_architecture(bit)
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

if __name__ == "__main__":
  app = QApplication(sys.argv)
  
  with open("style.css", "r") as file:
    app.setStyleSheet(file.read())

  window = MainWindow()
  window.show()
  sys.exit(app.exec())
