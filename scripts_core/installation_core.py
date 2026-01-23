from PySide6.QtCore import QObject, QThread, Signal
from zipfile import ZipFile
from pathlib import Path
import os
import struct
import shutil

# solve download on Fedora based (bazzite)
import urllib.request
import ssl
import certifi

# I know that this is a force security, probably a security issue to force download withous SSL...
# ssl._create_default_https_context = ssl._create_unverified_context

MACHINE_TYPES = {
  0x014C: "32-bit",
  0x8664: "64-bit",
  0xAA64: "64-bit",
}

URL_COMPILER = "https://github.com/Ishidawg/reshade-installer-linux/raw/main/d3dcompiler_dll"
URL_D3D8TO9 = "https://github.com/crosire/d3d8to9/releases/download/v1.13.0/d3d8.dll"

class InstallationWorker(QObject):
  finished = Signal()
  error = Signal(str)
  status_update = Signal(str)
  progress_update = Signal(int)

  def __init__(self):
    super().__init__()
    self.reshade_dir_path = None
    self.game_exe_path = None
    self.api_choice = None

  def setup(self, reshade_dir, game_exe, api):
    self.reshade_dir_path = reshade_dir
    self.game_exe_path = game_exe
    self.api_choice = api

  def run(self):
    try:
      if not all([self.reshade_dir_path, self.game_exe_path, self.api_choice]):
        raise ValueError("Missing info for installation.")

      self.progress_update.emit(0)
      self.status_update.emit("Checking game architecture")

      game_path = Path(self.game_exe_path)

      arch = self._get_executable_architecture(game_path)
      self.status_update.emit(f"Architecture detected (bits): {arch}")
      self.progress_update.emit(20)

      dll_source_name = "ReShade64.dll" if arch == "64-bit" else "ReShade32.dll"
      source_dll_path = Path(self.reshade_dir_path) / dll_source_name

      if not source_dll_path.exists():
        raise FileNotFoundError(f"Could not find {dll_source_name} in {self.reshade_dir_path}")

      # Need to set game dir here at the top so I can use d3d8 wrapper into switch case
      game_dir = game_path.parent

      dll_dest_name = ""
      match self.api_choice:
        case "OpenGL":
          dll_dest_name = "opengl32.dll"
        case "D3D 8":
          dll_dest_name = "d3d9.dll"
          self._d3d8_wrapper(game_dir)
        case "D3D 9":
          dll_dest_name = "d3d9.dll"
        case "D3D 10":
          dll_dest_name = "d3d10.dll"
        case "D3D 11":
          dll_dest_name = "d3d11.dll"
        case "Vulkan/D3D 12":
          dll_dest_name = "dxgi.dll"
        case _:
          raise ValueError(f"YET an nsupported API!")

      dest_path = game_dir / dll_dest_name

      self.status_update.emit(f"Installing {dll_dest_name}")
      shutil.copyfile(source_dll_path, dest_path)
      self.progress_update.emit(60)

      self.status_update.emit("Downloading d3dcompiler_47.dll")
      self._install_compiler(game_dir, arch)
      self.progress_update.emit(90)

      # Create Shader and Texture forlder to later on drop cloned files
      if not os.path.exists(f"{game_dir}/Shaders") and not os.path.exists(f"{game_dir}/Textures"):
        os.mkdir(f"{game_dir}/Shaders")
        os.mkdir(f"{game_dir}/Textures")

      self.status_update.emit("DLL Installed successfully.")
      self.finished.emit()
    except Exception as e:
      self.error.emit(str(e))

  def _install_compiler(self, game_dir, arch):
    target_file = game_dir / "d3dcompiler_47.dll"

    # Prevent from downloading again...
    if target_file.exists():
      return

    subfolder = "win64" if arch == "64-bit" else "win32"
    final_url = f"{URL_COMPILER}/{subfolder}/d3dcompiler_47.dll"

    try:
      # urllib.request.urlretrieve(final_url, target_file)

      context = ssl.create_default_context(cafile = certifi.where())

      req = urllib.request.Request(final_url, headers = {'User-Agent': 'Chrome/120.0.0.0'})

      with urllib.request.urlopen(req, context = context) as res:
          with open(target_file, 'wb') as out_file:
                out_file.write(res.read())

    except Exception as e:
      pass

  def _d3d8_wrapper(self, game_dir):
    target_file = game_dir / "d3d8.dll"

    if target_file.exists():
      return

    try:
      # urllib.request.urlretrieve(URL_D3D8TO9, target_file)

      context = ssl.create_default_context(cafile = certifi.where())

      req = urllib.request.Request(URL_D3D8TO9, headers = {'User-Agent': 'Chrome/120.0.0.0'})

      with urllib.request.urlopen(req, context = context) as res:
          with open(target_file, 'wb') as out_file:
                out_file.write(res.read())

    except Exception as e:
      pass

  # Jhen code snippet (https://github.com/Dzavoy)
  # Indentify binary achitecture, so user do not have to do it manually.
  def _get_executable_architecture(self, path: Path) -> str:
    if not path.exists():
      raise FileNotFoundError(f"File not found: {path}")

    with path.open("rb") as f:
      dos_header: bytes = f.read(64)
      if len(dos_header) < 64 or dos_header[:2] != b"MZ":
        raise ValueError("Not a valid executable (missing MZ header)")

      e_lfanew: int = struct.unpack_from("<I", dos_header, 60)[0]

      f.seek(e_lfanew)
      pe_signature: bytes = f.read(4)
      if pe_signature != b"PE\x00\x00":
        raise ValueError("Invalid PE signature")

      machine_bytes: bytes = f.read(2)
      machine: int = struct.unpack("<H", machine_bytes)[0]

    return MACHINE_TYPES.get(machine, "unknown")
