import os
import struct
import shutil
import glob
from pathlib import Path
from PySide6.QtCore import (
    QObject,
    QStandardPaths,
    Signal
)

from scripts_core.script_prepare_re import EXTRACT_PATH

MACHINE_TYPES = {
    0x014C: "32-bit",
    0x8664: "64-bit",
    0xAA64: "64-bit",
}

URL_COMPILER = "https://github.com/Ishidawg/reshade-installer-linux/raw/main/d3dcompiler_dll"
URL_D3D8TO9 = "https://github.com/crosire/d3d8to9/releases/download/v1.13.0/d3d8.dll"


class InstallationWorker(QObject):

    def __init__(self, game_path: str, game_api: str):
        super().__init__()

        self.game_path: str = game_path
        self.game_api: str = game_api
        self.game_arch: str = ''
        self.reshade_path: str = EXTRACT_PATH
        self.game_path_parent: str = str(Path(game_path).resolve().parent)

        self.shader_dir: str = os.path.join(self.game_path_parent, 'Shaders')
        self.texture_dir: str = os.path.join(self.game_path_parent, 'Textures')

        self.run()

    def run(self) -> None:
        self.game_arch = self.get_executable_architecture(Path(self.game_path))
        self.ready_reshade_dll()

    def ready_reshade_dll(self) -> None:
        self.prepare_dll()
        self.create_reshade_directories()

        # NEED TO INSTALL THE COMPILER

    def create_reshade_directories(self):
        os.makedirs(os.path.join(self.game_path_parent,
                    self.shader_dir), exist_ok=True)
        os.makedirs(os.path.join(self.game_path_parent,
                    self.texture_dir), exist_ok=True)

    def prepare_dll(self) -> None:
        reshade_dll: str = "ReShade64.dll" if self.game_arch == "64-bit" else "ReShade32.dll"
        reshade_dll_dir: str = os.path.join(self.reshade_path, reshade_dll)

        if not reshade_dll_dir:
            raise FileNotFoundError(
                f"Could not find {reshade_dll} in {self.reshade_path}")

        reshade_dll_renamed: str = ''

        match self.game_api:
            case "OpenGL":
                reshade_dll_renamed = "opengl32.dll"
            case "D3D 8":
                reshade_dll_renamed = "d3d9.dll"
                # self._d3d8_wrapper(game_dir)
            case "D3D 9":
                reshade_dll_renamed = "d3d9.dll"
            case "D3D 10":
                reshade_dll_renamed = "d3d10.dll"
            case "D3D 11":
                reshade_dll_renamed = "d3d11.dll"
            case "Vulkan/D3D 12":
                reshade_dll_renamed = "dxgi.dll"
            case _:
                raise ValueError(f"YET an nsupported API!")

        reshade_dll_renamed_destination: str = os.path.join(
            self.game_path_parent, reshade_dll_renamed)

        shutil.copy(reshade_dll_dir, reshade_dll_renamed_destination)

    def get_executable_architecture(self, path: Path) -> str:
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
