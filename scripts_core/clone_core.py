from PySide6.QtCore import QObject, Signal, QStandardPaths
import os
import shutil
import urllib.request
import zipfile
from pathlib import Path
import ssl
import tempfile

# I know that this is a force security, probably a security issue to force download withous SSL... 
ssl._create_default_https_context = ssl._create_unverified_context

REPO_INFO = {
  "default": {
     "url": "https://github.com/crosire/reshade-shaders",
     "branch": "slim"
  },
  "prod80": {
    "url": "https://github.com/prod80/prod80-ReShade-Repository",
    "branch": "master"
  },
  "quint": {
    "url": "https://github.com/martymcmodding/qUINT",
    "branch": "master"
  }
}

CACHE_PATH = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.CacheLocation)
# TEMP_DIR = "./reshade/temp_clones"
TEMP_DIR = os.path.join(CACHE_PATH, "reshade_temp_clones")

class CloneWorker(QObject):
  finished = Signal()
  status_update = Signal(str)
  progress_update = Signal(int)
  error = Signal(str)

  def __init__(self):
    super().__init__()
    self.game_dir = None
    self.selected_repos = []

  def setup(self, game_dir, selections):
    self.game_dir = game_dir
    self.selected_repos = selections

  def run(self):
    try:
      if not self.game_dir or not os.path.isdir(self.game_dir):
        raise ValueError("Invalid game directory.")

      shaders_dest = os.path.join(self.game_dir, "Shaders")
      textures_dest = os.path.join(self.game_dir, "Textures")

      os.makedirs(shaders_dest, exist_ok=True)
      os.makedirs(textures_dest, exist_ok=True)

      os.makedirs(TEMP_DIR, exist_ok=True)

      total_repos = len(self.selected_repos)
      current_repo = 0
      self.progress_update.emit(0)

      for repo_key in self.selected_repos:
        repo_data = REPO_INFO.get(repo_key)
        if not repo_data: continue

        repo_name = repo_key
        repo_branch = repo_data["branch"]
        repo_url = repo_data["url"]

        zip_url = f"{repo_url}/archive/refs/heads/{repo_branch}.zip"

        self.status_update.emit(f"Cloning {repo_name} repository")

        zip_path = os.path.join(TEMP_DIR, f"{repo_name}.zip")
        extract_path = os.path.join(TEMP_DIR, repo_name)

        if os.path.exists(extract_path):
          shutil.rmtree(extract_path)

        try:
          # Need to replace git with a python native because MINT 22.2 does not download
          urllib.request.urlretrieve(zip_url, zip_path)

          self.status_update.emit(f"Extracting {repo_name}...")

          with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(TEMP_DIR)

          extracted_folder_name = self._find_extracted_folder(TEMP_DIR, repo_key)

          if extracted_folder_name:
            full_extracted_path = os.path.join(TEMP_DIR, extracted_folder_name)
            shutil.move(full_extracted_path, extract_path)

          if os.path.exists(zip_path):
            os.remove(zip_path)

          self.status_update.emit(f"Installing {repo_name} files")
          self._organize_files(extract_path, shaders_dest, textures_dest)

        except Exception as e:
          self.status_update.emit(f"Failed to clone {repo_name}. Skipping.")
          continue

        current_repo += 1
        percentage = int((current_repo / total_repos) * 100)
        self.progress_update.emit(percentage)

      if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR, ignore_errors=True)

      self.status_update.emit("All shaders installed!")
      self.finished.emit()
    except Exception as e:
      self.error.emit(str(e))

  def _find_extracted_folder(self, base_path, keyword):
    for item in os.listdir(base_path):
      full_path = os.path.join(base_path, item)

      if os.path.isdir(full_path):
        if item == keyword: continue
        return item
    return None

  def _organize_files(self, source_root, shaders_dest, textures_dest):
    for root, dirs, files in os.walk(source_root):
      if ".git" in root: continue

      for file in files:
        file_lower = file.lower()
        src_file = os.path.join(root, file)

        if file_lower.endswith(('.fx', '.fxh')):
          shutil.copy2(src_file, os.path.join(shaders_dest, file))

        elif file_lower.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tga')):
          shutil.copy2(src_file, os.path.join(textures_dest, file))
