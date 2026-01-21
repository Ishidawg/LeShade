from PySide6.QtCore import QObject, Signal, QStandardPaths
from zipfile import ZipFile
from pathlib import Path
import os

# solve download on Fedora based (bazzite)
import urllib.request
import ssl

# I know that this is a force security, probably a security issue to force download withous SSL...
ssl._create_default_https_context = ssl._create_unverified_context

RESHADE_URL = "https://reshade.me/downloads/ReShade_Setup_6.6.2.exe"
START_PATH = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DownloadLocation)
CACHE_PATH = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.CacheLocation)
PATTERN = "ReShade_Setup*.exe"
LOCAL_RESHADE_DIR = os.path.join(CACHE_PATH, "reshade_extracted")
#LOCAL_RESHADE_DIR = './reshade'

class ReshadeDraft:
  def __init__(self):
    self.reshade_path = None

  def draft_complete(self):
    if not self.reshade_path:
      raise ValueError("ERROR: Failed to draft")

class DownloadWorker(QObject):
  finished = Signal(object)
  status_update = Signal(str)
  error = Signal(str)

  def __init__(self):
    super().__init__()
    self.builder = ReshadeDraftBuilder()

  def run(self):
    try:
      self.status_update.emit("Checking/Downloading Reshade...")
      self.builder.run_draft()

      draft = self.builder.draft
      if draft.reshade_path:
        self.status_update.emit("Download/Search Complete!")
        self.finished.emit(draft)
      elif START_PATH:
        self.error.emit("The Downloads folder should be writeable and readable.")
      else:
        self.error.emit("Could not find ReShade executable.")
    except Exception as e:
      self.error.emit(str(e))

class ReshadeDraftBuilder(QObject):
  def __init__(self):
    super().__init__()
    self.draft = ReshadeDraft()
    self.reshade_temp_path = None

  def run_draft(self):
    try:
      self.download_reshade(RESHADE_URL)

      # Not good at all... sorry future me
      if self.reshade_temp_path:
        self.unzip_reshade(self.reshade_temp_path)
        self.draft.reshade_path = self.reshade_temp_path
      elif self._find_reshade(START_PATH, PATTERN):
        self.reshade_temp_path = self._find_reshade(START_PATH, PATTERN)
        self.unzip_reshade(self.reshade_temp_path)
        self.draft.reshade_path = self.reshade_temp_path
      else:
        self.find_reshade()
    except Exception as error:
      pass


  # Public methods
  def download_reshade(self, url: str):
    try:
      self._download_reshade(url)

    except Exception as error:
      pass

    return self

  def unzip_reshade(self, reshade_path):
    try:
      self._unzip_reshade(reshade_path)

    except Exception as error:
      pass

    return self

  def find_reshade(self):
    try:
      self.draft.reshade_path = self._find_reshade(START_PATH, PATTERN)
    except Exception as error:
      pass

    return self

  # Private methods
  def _find_reshade(self, start_path: Path, exe_pattern: str):
    start = Path(start_path)
    pattern = f'{exe_pattern}'

    if start_path is None:
        return None

    try:
      matches = list(start.rglob(pattern))
    except PermissionError:
      return None

    if not matches:
      return None

    return str(matches[0])

  def _download_reshade(self, url: str):
    if not self._find_reshade(START_PATH, PATTERN):
      try:
        file_name = url.split('/')[-1]

        destination = os.path.join(START_PATH, file_name)
        urllib.request.urlretrieve(url, destination)

        self.reshade_temp_path = self._find_reshade(START_PATH, PATTERN)
      except Exception as e:
        print(f"ERROR: {e}")
        return None

  def _unzip_reshade(self, reshade_path):
    if not os.path.exists(LOCAL_RESHADE_DIR):
        os.makedirs(LOCAL_RESHADE_DIR, exist_ok = True)

    try:
        with ZipFile(reshade_path, 'r') as zip_object:
            zip_object.extractall(LOCAL_RESHADE_DIR)
    except Exception as e:
        print(f"shit happens: {e}")

