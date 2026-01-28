from PySide6.QtCore import QObject, Signal
import os
import shutil
import zipfile

import urllib.request
import ssl
import certifi

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

      shaders_temp_dir = os.path.join(self.game_dir, ".reshade_installer_temp")
  
      if os.path.exists(shaders_temp_dir):
        shutil.rmtree(shaders_temp_dir)

      os.makedirs(shaders_temp_dir, exist_ok = True)

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

        zip_path = os.path.join(shaders_temp_dir, f"{repo_name}.zip")
        extract_path = os.path.join(shaders_temp_dir, repo_name)
        os.makedirs(extract_path, exist_ok = True)

        try:
          # Need to replace git with a python native because MINT 22.2 does not download
          context = ssl.create_default_context(cafile = certifi.where())

          req = urllib.request.Request(zip_url, headers = {'User-Agent': 'Chrome/121.0.0.0'})

          with urllib.request.urlopen(req, context = context) as res:
              with open(zip_path, 'wb') as out_file:
                  out_file.write(res.read())

          self.status_update.emit(f"Extracting {repo_name}...")

          with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

          self.status_update.emit(f"Installing {repo_name} files")
          self._organize_files(extract_path, shaders_dest, textures_dest)

        except Exception as e:
          self.status_update.emit(f"Failed to clone {repo_name}. Skipping.")
          continue

        current_repo += 1
        percentage = int((current_repo / total_repos) * 100)
        self.progress_update.emit(percentage)

      self.status_update.emit("Remove temp directory")
      if shaders_temp_dir and os.path.exists(shaders_temp_dir):
        shutil.rmtree(shaders_temp_dir, ignore_errors = True)

      self.status_update.emit("All shaders installed!")
      self.finished.emit()
    except Exception as e:
      self.error.emit(str(e))

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

