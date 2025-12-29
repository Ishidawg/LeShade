from PySide6.QtCore import QObject
from zipfile import ZipFile
from pathlib import Path
import os

RESHADE_URL = "https://reshade.me/downloads/ReShade_Setup_6.6.2.exe"
START_PATH = "/home"
PATTERN = "ReShade_Setup*.exe"
LOCAL_RESHADE_DIR = './reshade'

class ReshadeDraft:
  def __init__(self):
    self.reshade_path = None

  def draft_complete(self):
    if not self.reshade_path:
      raise ValueError("ERROR: Failed to draft")

class ReshadeDraftBuilder(QObject):
  def __init__(self):
    self.draft = ReshadeDraft()
    self.reshade_temp_path = None

  def run_draft(self):
    try:
      self.download_reshade(RESHADE_URL)
      self.unzip_reshade(self.reshade_temp_path)

      if self.reshade_temp_path == None:
        self.find_reshade()
      else:
        self.draft.reshade_path = self.reshade_temp_path
    except Exception as error:
      print(f"ERROR: {error}")

  # Public methods
  def download_reshade(self, url: str):
    try:
      self._download_reshade(url)
      print("DOWNLOAD SUCCESS!")
    except Exception as error:
      print("DOWNLOAD FAILED!")

    return self

  def unzip_reshade(self, reshade_path):
    try:
      self._unzip_reshade(reshade_path)
      print("UNZIP SUCCESS!")
    except Exception as error:
      print("UNZIP FAILED!")

    return self

  def find_reshade(self):
    try:
      self.draft.reshade_path = self._find_reshade(START_PATH, PATTERN)
      print("SEARCH SUCCESS!")
    except Exception as error:
      print("SEARCH FAILED!")

  # Private methods
  def _find_reshade(self, start_path: Path, exe_pattern: str):
    start = Path(start_path)
    pattern = f'{exe_pattern}'

    try: 
      matches = list(start.rglob(pattern))
    except PermissionError:
      print("ERROR: Not allowed due to permission stuff")
      return None

    if not matches:
      return None

    return str(matches[0])

  def _download_reshade(self, url: str):
    if not self._find_reshade(START_PATH, PATTERN):
      try:
        os.system(f"wget {url}")
        self.reshade_temp_path = self._find_reshade(START_PATH, PATTERN)
      except Exception as e:
        print(f"ERROR: {e}")
        return None
      finally:
        return True

  def _unzip_reshade(self, reshade_path):
    if not os.path.isdir(LOCAL_RESHADE_DIR):
      with ZipFile(reshade_path, 'r') as zip_object:
        zip_object.extractall(LOCAL_RESHADE_DIR)

if __name__ == "__main__":
  builder = ReshadeDraftBuilder()
  builder.run_draft()
  
  draft = builder.draft
  draft.draft_complete()
  print(f"final executable: {draft.reshade_path}")
