import os
from pathlib import Path

from utils.utils import generic_download

URL_COMPILER = "https://github.com/Ishidawg/reshade-installer-linux/raw/main/d3dcompiler_dll"
URL_D3D8TO9 = "https://github.com/crosire/d3d8to9/releases/download/v1.13.0/d3d8.dll"


def download_d3d8to9(game_path: str) -> None:
    directory: str = os.path.join(game_path, "d3d8.dll")

    if Path(directory).exists():
        return

    generic_download(URL_D3D8TO9, directory)


def download_hlsl_compiler(game_path: str, game_arch: str) -> None:
    directory: str = os.path.join(game_path, "d3dcompiler_47.dll")

    if Path(directory).exists():
        return

    arch: str = "win64" if game_arch == "64-bit" else "win32"
    furl: str = f"{URL_COMPILER}/{arch}/d3dcompiler_47.dll"

    generic_download(furl, directory)
