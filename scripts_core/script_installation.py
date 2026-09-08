from pathlib import Path
from PySide6.QtCore import (
    QObject,
    Signal
)
from scripts_core.script_download_dll import (
    download_d3d8to9,
    download_hlsl_compiler
)
from scripts_core.script_vulkan import InstallVulkan
from utils.utils import EXTRACT_PATH

import textwrap
import struct
import shutil
import glob
import os
import re

MACHINE_TYPES = {
    0x014C: "32-bit",
    0x8664: "64-bit",
    0xAA64: "64-bit",
}


class InstallationWorker(QObject):
    install_progress: Signal = Signal(int)
    install_finished: Signal = Signal(bool)
    current_game_path: Signal = Signal(str)
    have_hlsl_compiler: Signal = Signal(bool)

    vulkan_paths: Signal = Signal(str, str, str)
    api_dll: Signal = Signal(str)

    def __init__(self, game_path: str, game_api: str, is_steam: bool):
        super().__init__()

        self.game_path: str = game_path
        self.game_api: str = game_api
        self.game_arch: str = ''
        self.reshade_path: str = EXTRACT_PATH
        self.game_path_parent: str = str(Path(game_path).resolve().parent)

        self.shader_dir: str = os.path.join(
            self.game_path_parent, 'reshade-shaders/Shaders')
        self.texture_dir: str = os.path.join(
            self.game_path_parent, 'reshade-shaders/Textures')

        self.reshade_ini: str = os.path.join(
            self.game_path_parent, "ReShade.ini")

        self.hlsl_compiler: bool | None = None
        self.is_steam: bool = is_steam

    def run(self) -> None:
        try:
            self.install_progress.emit(0)
            self.game_arch = self.get_executable_architecture(
                Path(self.game_path))
            self.install_progress.emit(40)
            self.ready_reshade_dll(self.is_steam)
            self.install_progress.emit(60)

            self.hlsl_compiler = download_hlsl_compiler(
                self.game_path_parent, self.game_arch)

            # means that game folder already had the d3dcompiler_47.dll - emit True or False
            self.have_hlsl_compiler.emit(self.hlsl_compiler)

            if self.game_api == "D3D 8":
                self.install_progress.emit(90)
                download_d3d8to9(self.game_path_parent)

            self.status_update()
        except Exception as e:
            print("Error on installation process: {e}")
            self.install_progress.emit(0)
            self.install_finished.emit(False)

    def status_update(self) -> None:
        if self.game_path and self.game_api and self.game_arch and self.reshade_path:
            self.install_progress.emit(100)
            self.install_finished.emit(True)
            self.current_game_path.emit(self.game_path_parent)
        else:
            self.install_progress.emit(0)
            self.install_finished.emit(False)

    def ready_reshade_dll(self, is_steam: bool) -> None:
        if self.game_api == "Vulkan":
            vulkan_install: InstallVulkan = InstallVulkan(
                self.game_path, is_steam)

            self.vulkan_paths.emit(
                vulkan_install.reshade_prefix,
                vulkan_install.system32_prefix,
                os.path.join(vulkan_install.drive_c_path,
                             "Program Files", "VulkanRT")
            )

            vulkan_install.run()
        else:
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

        ini_data: str = textwrap.dedent("""
            [GENERAL]
            EffectSearchPaths=.\\reshade-shaders\\Shaders\\**
            IntermediateCachePath=C:\\users\\steamuser\\AppData\\Local\\Temp\\ReShade
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
            TextureSearchPaths=.\\reshade-shaders\\Textures\\**
        """).strip()

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

        reshade_dll_renamed: str = get_api_dll_name(self.game_api)

        reshade_dll_renamed_destination: str = os.path.join(
            self.game_path_parent, reshade_dll_renamed)

        # just overwrite the file, cuz then reshade is updated, or even downgraded if needed
        shutil.copy(reshade_dll_dir, reshade_dll_renamed_destination)
        self.api_dll.emit(reshade_dll_renamed)

    def get_executable_architecture(self, path: Path) -> str:
        return get_executable_architecture(path)


def get_executable_architecture(path: Path) -> str:
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


def get_api_dll_name(game_api: str) -> str:
    match game_api:
        case "OpenGL":
            return "opengl32.dll"
        case "D3D 8" | "D3D 9":
            return "d3d9.dll"
        case "D3D 10":
            return "d3d10.dll"
        case "D3D 11":
            return "d3d11.dll"
        case "D3D 12":
            return "dxgi.dll"
        case _:
            return "dxgi.dll"


def check_existing_installation(game_exe_path: str) -> dict:
    result = {
        "installed": False,
        "version": "",
        "api_dll": "",
        "api_dll_path": "",
        "detected_api": "",
        "has_ini": False,
        "has_shaders": False,
        "has_log": False,
        "addons": []
    }
    if not game_exe_path or not os.path.exists(game_exe_path):
        return result

    exe = Path(game_exe_path).resolve()
    game_dir = exe.parent if exe.is_file() else exe
    if not game_dir.is_dir():
        return result

    candidate_dlls = [
        ("dxgi.dll", "D3D 12"),
        ("d3d11.dll", "D3D 11"),
        ("d3d9.dll", "D3D 9"),
        ("d3d10.dll", "D3D 10"),
        ("d3d12.dll", "D3D 12"),
        ("opengl32.dll", "OpenGL"),
        ("d3d8.dll", "D3D 8")
    ]

    found_dll = None
    found_dll_path = None
    detected_api = ""
    version = ""

    for dll_name, api in candidate_dlls:
        dll_path = game_dir / dll_name
        if dll_path.is_file():
            try:
                with open(dll_path, "rb") as f:
                    data = f.read()
                m = re.search(rb"crosire\'s ReShade version \'([^\']+)\'", data)
                if m:
                    version = m.group(1).decode("latin1", errors="ignore")
                    found_dll = dll_name
                    found_dll_path = str(dll_path)
                    detected_api = api
                    break
                elif b"ReShade" in data:
                    found_dll = dll_name
                    found_dll_path = str(dll_path)
                    detected_api = api
                    break
            except Exception:
                pass

    has_ini = (game_dir / "ReShade.ini").is_file()
    has_shaders = (game_dir / "reshade-shaders").is_dir()
    has_log = (game_dir / "ReShade.log").is_file()

    # Read version from ReShade.log if not found in DLL
    if not version and has_log:
        try:
            with open(game_dir / "ReShade.log", "r", encoding="latin1", errors="ignore") as f:
                for _ in range(30):
                    line = f.readline()
                    if not line:
                        break
                    m = re.search(r"ReShade version \'([^\']+)\'", line)
                    if m:
                        version = m.group(1)
                        break
        except Exception:
            pass

    # Find addons
    addons = []
    for pattern in ("*.addon", "*.addon64", "*.addon32"):
        addons.extend([f.name for f in game_dir.glob(pattern)])

    installed = bool(found_dll or has_ini or has_shaders)
    return {
        "installed": installed,
        "version": version,
        "api_dll": found_dll or "",
        "api_dll_path": found_dll_path or "",
        "detected_api": detected_api,
        "has_ini": has_ini,
        "has_shaders": has_shaders,
        "has_log": has_log,
        "addons": addons
    }


def update_reshade_dll_only(
    game_exe_path: str,
    game_api: str = "",
    target_dll_name: str = "",
    reshade_source_dir: str = EXTRACT_PATH,
    is_steam: bool = True
) -> tuple[bool, str]:
    try:
        exe_path = Path(game_exe_path).resolve()
        game_dir = exe_path.parent if exe_path.is_file() else exe_path
        if not game_dir.is_dir():
            return False, f"Game directory does not exist: {game_dir}"

        if not os.path.exists(reshade_source_dir):
            return False, "ReShade binaries not found in cache. Please download ReShade first."

        if game_api == "Vulkan":
            vulkan_install = InstallVulkan(str(exe_path), is_steam)
            vulkan_install.run()
        else:
            arch = get_executable_architecture(exe_path)
            reshade_dll = "ReShade64.dll" if arch == "64-bit" else "ReShade32.dll"
            reshade_src = os.path.join(reshade_source_dir, reshade_dll)
            if not os.path.isfile(reshade_src):
                return False, f"Could not find {reshade_dll} in {reshade_source_dir}. Please download ReShade first."

            if not target_dll_name:
                existing = check_existing_installation(str(exe_path))
                if existing.get("api_dll"):
                    target_dll_name = existing["api_dll"]
                elif game_api:
                    target_dll_name = get_api_dll_name(game_api)
                else:
                    target_dll_name = "dxgi.dll"

            target_dll_dest = os.path.join(str(game_dir), target_dll_name)
            shutil.copy(reshade_src, target_dll_dest)

        # Download HLSL compiler if needed
        arch = get_executable_architecture(exe_path)
        download_hlsl_compiler(str(game_dir), arch)

        if game_api == "D3D 8":
            download_d3d8to9(str(game_dir))

        return True, "ReShade DLL updated successfully!"
    except Exception as e:
        return False, str(e)


def uninstall_game_reshade(game_exe_path: str, is_steam: bool = True) -> tuple[bool, str]:
    try:
        from scripts_core.script_manager import remove_game_by_dir, remove_game_by_path

        exe_path = Path(game_exe_path).resolve()
        game_dir = exe_path.parent if exe_path.is_file() else exe_path
        if not game_dir.is_dir():
            return False, f"Directory does not exist: {game_dir}"

        # 1. Delete ReShade candidate DLLs only if verified as ReShade
        candidate_dlls = ["dxgi.dll", "d3d11.dll", "d3d9.dll", "d3d8.dll", "d3d10.dll", "d3d12.dll", "opengl32.dll"]
        for dll_name in candidate_dlls:
            dll_path = game_dir / dll_name
            if dll_path.is_file():
                try:
                    with open(dll_path, "rb") as f:
                        data = f.read()
                    if b"ReShade" in data or b"crosire" in data:
                        dll_path.unlink()
                except Exception:
                    pass

        # 2. Delete configuration, presets, and logs
        for pattern in ("ReShade*.*", "reshade*.*", "renodx*.*"):
            for f in game_dir.glob(pattern):
                if f.is_file():
                    try:
                        f.unlink()
                    except Exception:
                        pass

        # 3. Delete reshade-shaders folder
        shaders_dir = game_dir / "reshade-shaders"
        if shaders_dir.is_dir():
            shutil.rmtree(shaders_dir, ignore_errors=True)

        # 4. Delete add-ons
        for pattern in ("*.addon", "*.addon64", "*.addon32"):
            for f in game_dir.glob(pattern):
                if f.is_file():
                    try:
                        f.unlink()
                    except Exception:
                        pass

        # 5. Clean Vulkan layer if relevant
        try:
            InstallVulkan(str(exe_path), is_steam, remove=True)
        except Exception:
            pass

        # 6. Remove from manager.json
        remove_game_by_dir(str(game_dir))
        remove_game_by_path(str(exe_path))

        return True, "ReShade uninstalled successfully!"
    except Exception as e:
        return False, str(e)
