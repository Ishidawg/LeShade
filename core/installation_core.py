from PySide6.QtCore import QObject
from zipfile import ZipFile
from pathlib import Path
import os

from download_core.ReshadeDraft import reshade_path

START_PATH = "/home"
PATTERN = "ReShade_Setup*.exe"
LOCAL_RESHADE_DIR = './reshade'

class InstallationDraft:
  def __init__(self):
    self.reshade_local = reshade_path
    self.game_exe_path = None
    self.game_arch = None
    self.game_api = None

  def draft_complete(self):
    if not all([self.reshade_local, self,game_exe_path, self.game_arch, self.game_api]):
      raise ValueError("ERROR: Failed to draft")

class InstallationDraftBuilder(QObject):
  def __init__(self):
    self.draft = InstallationDraft()

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
  def set_game_architecture(self, game_executable_path):
    
    # Workaround to fix a parsing error that was string
    converted_path = Path(game_executable_path)

    try:
      bits: Architecture = self._get_executable_architecture(converted_path)
      self.reshade.game_bits = bits
    except Exception as e:
        print(f"ERROR: {e}")

    dll_name = "ReShade64.dll" if bits == "64-bit" else "ReShade32.dll"

    self.reshade.local_source = self._find_reshade(LOCAL_RESHADE_DIR, dll_name)

    if not self.reshade.local_source:
      raise FileNotFoundError(f"ERROR: {dll_name} was not found in ./reshade")

    return self

  def set_game_api(self, api: str):

    if not self.reshade.local_source:
      raise Exception("ERROR: error on function queue, set_game_architecture() MUST BE before of set_game_api()")

    self.reshade.game_api = api

    match api:
      case "Vulkan":
        new_name = "dxgi.dll"
      case "d3d9":
        new_name = "d3d9.dll"
      case "d3d10":
        new_name = "d3d10.dll"
      case _:
        raise ValueError("ERROR: This dll is not supported YET")

    self._ready_dll(self.reshade.local_source, new_name)

    self.reshade.new_dll = new_name
    self.reshade.correct_dll = self._find_reshade('./reshade', new_name)
    
    return self

  def find_reshade(self):
    try:
      self.draft.reshade_path = self._find_reshade(START_PATH, PATTERN)
      print("SEARCH SUCCESS!")
    except Exception as error:
      print("SEARCH FAILED!")

  # Private methods

  # Jhen code snippet (https://github.com/Dzavoy)
  # Indentify binary achitecture, so user do not have to do it manually.
  def _get_executable_architecture(self, path: Path) -> Architecture:
    if not path.exists():
      raise FileNotFoundError(f"File not found: {path}")

    with path.open("rb") as f:
      dos_header: bytes = f.read(64)
      if len(dos_header) < 64 or dos_header[:2] != b"MZ":
          raise ValueError("Not a valid DOS/PE executable (missing MZ header)")

      e_lfanew: int = struct.unpack_from("<I", dos_header, 60)[0]

      f.seek(e_lfanew)
      pe_signature: bytes = f.read(4)
      if pe_signature != b"PE\x00\x00":
          raise ValueError("Invalid PE signature")

      machine_bytes: bytes = f.read(2)
      machine: int = struct.unpack("<H", machine_bytes)[0]

    MACHINE_TYPES: Final[dict[int, Architecture]] = {
      0x014C: "32-bit",
      0x8664: "64-bit",
      0xAA64: "64-bit",
    }

    architecture: Architecture = MACHINE_TYPES.get(machine, "unknown")
    return architecture

    def _ready_dll(self, local, new_name):
      shutil.copyfile(local, f'./reshade/{new_name}')
      return new_name

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

if __name__ == "__main__":
  builder = ReshadeDraftBuilder()
  builder.run_draft()
  
  draft = builder.draft
  draft.draft_complete()
  print(f"final executable: {draft.reshade_path}")
