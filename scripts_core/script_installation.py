import os
import struct
import shutil
from pathlib import Path
from PySide6.QtCore import (
    QObject,
    Signal
)

from scripts_core.script_download_dll import (
    download_d3d8to9,
    download_hlsl_compiler
)

from scripts_core.script_prepare_re import EXTRACT_PATH

MACHINE_TYPES = {
    0x014C: "32-bit",
    0x8664: "64-bit",
    0xAA64: "64-bit",
}


class InstallationWorker(QObject):
    install_progress: Signal = Signal(int)
    install_finished: Signal = Signal(bool)
    current_game_path: Signal = Signal(str)

    def __init__(self, game_path: str, game_api: str):
        super().__init__()

        self.game_path: str = game_path
        self.game_api: str = game_api
        self.game_arch: str = ''
        self.reshade_path: str = EXTRACT_PATH
        self.game_path_parent: str = str(Path(game_path).resolve().parent)

        self.shader_dir: str = os.path.join(self.game_path_parent, 'Shaders')
        self.texture_dir: str = os.path.join(self.game_path_parent, 'Textures')

        self.reshade_ini: str = os.path.join(
            self.game_path_parent, "ReShade.ini")

    def run(self) -> None:
        self.install_progress.emit(0)
        self.game_arch = self.get_executable_architecture(
            Path(self.game_path))
        self.install_progress.emit(40)
        self.ready_reshade_dll()
        self.install_progress.emit(60)

        # d3d8 wrapper and hlsl compiler
        download_hlsl_compiler(self.game_path_parent, self.game_arch)
        if self.game_api == "D3D 8":
            self.install_progress.emit(90)
            download_d3d8to9(self.game_path_parent)

        self.status_update()

    def status_update(self) -> None:
        if self.game_path and self.game_api and self.game_arch and self.reshade_path:
            self.install_progress.emit(100)
            self.install_finished.emit(True)
            self.current_game_path.emit(self.game_path_parent)
        else:
            self.install_progress.emit(0)
            self.install_finished.emit(False)

    def ready_reshade_dll(self) -> None:
        self.prepare_dll()
        self.create_reshade_directories()
        self.create_reshade_ini()
        self.write_reshade_ini()

    def create_reshade_directories(self) -> None:
        os.makedirs(os.path.join(self.game_path_parent,
                    self.shader_dir), exist_ok=True)
        os.makedirs(os.path.join(self.game_path_parent,
                    self.texture_dir), exist_ok=True)

    def create_reshade_ini(self) -> None:
        try:
            # I tried do a open with "x" only and did not work, always goes to exception
            if not Path(self.reshade_ini).exists():
                open(self.reshade_ini, "x")
        except FileExistsError as e:
            raise FileExistsError(f"Failed to create ReShade.ini: {e}") from e

    def write_reshade_ini(self) -> None:
        reshade_ini_content: str | None = None

        ini_data: str = """
            [GENERAL]
            EffectSearchPaths=.\\Shaders
            NoDebugInfo=1
            NoEffectCache=0
            NoReloadOnInit=0
            PerformanceMode=0
            PreprocessorDefinitions=RESHADE_DEPTH_LINEARIZATION_FAR_PLANE=1000.0,RESHADE_DEPTH_INPUT_IS_UPSIDE_DOWN=0,RESHADE_DEPTH_INPUT_IS_REVERSED=0,RESHADE_DEPTH_INPUT_IS_LOGARITHMIC=0
            PresetPath=.\\ReShadePreset.ini
            PresetShortcutKeys=
            PresetShortcutPaths=
            PresetTransitionDuration=1000
            SkipLoadingDisabledEffects=0
            StartupPresetPath=
            TextureSearchPaths=.\\Textures
        """

        with open(self.reshade_ini) as file:
            reshade_ini_content = file.read()

        if len(reshade_ini_content) <= 0:
            with open(self.reshade_ini, "w") as file:
                file.write(ini_data)

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
            case "D3D 8" | "D3D 9":
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

        if not Path(reshade_dll_renamed_destination).exists():
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
