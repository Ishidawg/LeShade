import os
import shutil
import zipfile
import asyncio

from pathlib import Path
from PySide6.QtCore import (
    QObject,
    Signal
)

import urllib.request
import ssl
import certifi

REPO_SHADERS = {
    "Crosire slim": {
        "url": "https://github.com/crosire/reshade-shaders",
        "branch": "slim"
    },
    "Crosile legacy": {
        "url": "https://github.com/crosire/reshade-shaders",
        "branch": "legacy"
    },
    "Sweet FX": {
        "url": "https://github.com/CeeJayDK/SweetFX",
        "branch": "master"
    },
    "Prod80": {
        "url": "https://github.com/prod80/prod80-ReShade-Repository",
        "branch": "master"
    },
    "qUINT": {
        "url": "https://github.com/martymcmodding/qUINT",
        "branch": "master"
    },
    "iMMERSE": {
        "url": "https://github.com/martymcmodding/iMMERSE",
        "branch": "main"
    },
    "MLUT": {
        "url": "https://github.com/TheGordinho/MLUT",
        "branch": "master"
    },
    "Insane shaders": {
        "url": "https://github.com/LordOfLunacy/Insane-Shaders",
        "branch": "master"
    },
    "RS Retro Arch": {
        "url": "https://github.com/Matsilagi/RSRetroArch",
        "branch": "main"
    },
    "CRT Royale": {
        "url": "https://github.com/akgunter/crt-royale-reshade",
        "branch": "master"
    },
    "Glamarye Fast Effects": {
        "url": "https://github.com/rj200/Glamarye_Fast_Effects_for_ReShade",
        "branch": "main"
    }
}


class ShadersWorker(QObject):
    clone_finished: Signal = Signal(bool)

    def __init__(self, selections: list[str], game_dir):
        super().__init__()

        self.game_path: str = game_dir
        self.selected_repos: list[str] = selections
        self.total_repos: int = 0

        self.shader_temp_directory: str = os.path.join(
            self.game_path, ".shaders_temp")
        self.shader_dir: str = os.path.join(self.game_path, "Shaders")
        self.texture_dir: str = os.path.join(self.game_path, "Textures")

    def run(self) -> None:
        self.clean_temp()
        asyncio.run(self.install_shaders())
        self.organize_files(self.shader_temp_directory,
                            self.shader_dir, self.texture_dir)
        self.clean_temp()

    def clean_temp(self) -> None:
        if Path(self.shader_temp_directory).exists():
            shutil.rmtree(self.shader_temp_directory)

    async def unzip_shader(self, shader_temp_dir: str, repo_name: str, zipped_dir: str) -> None:
        extracted_shader_dir: str = os.path.join(shader_temp_dir, repo_name)
        os.makedirs(extracted_shader_dir, exist_ok=True)

        try:
            with zipfile.ZipFile(zipped_dir, 'r') as zip_ref:
                zip_ref.extractall(extracted_shader_dir)
        except Exception as e:
            raise IOError(f"Failed to unzip: {e}") from e

    async def download_shaders(self, shader_url: str, zipped_shader_dir: str) -> None:
        try:
            context: ssl.SSLContext = ssl.create_default_context(
                cafile=certifi.where())

            req: urllib.request.Request = urllib.request.Request(
                shader_url, headers={'User-Agent': 'Chrome/121.0.0.0'})

            with urllib.request.urlopen(req, context=context) as res:
                with open(zipped_shader_dir, 'wb') as file:
                    file.write(res.read())
        except Exception as e:
            raise IOError(f"Clone reshade failed: {e}") from e

    async def install_shaders(self) -> None:
        if not self.game_path:
            raise ValueError("Path error")

        os.makedirs(self.shader_temp_directory, exist_ok=True)

        try:
            self.total_repos = len(self.selected_repos)
            current_repo: int = 0

            for repo_key in self.selected_repos:
                repo_data: dict[str, str] | None = REPO_SHADERS.get(repo_key)

                if not repo_data:
                    continue

                repo_name: str = repo_key
                repo_branch: str = repo_data["branch"]
                repo_url: str = repo_data["url"]

                shader_url: str = f"{repo_url}/archive/refs/heads/{repo_branch}.zip"

                zipped_shader_dir: str = os.path.join(
                    self.shader_temp_directory, f"{repo_name}.zip")

                await asyncio.gather(self.download_shaders(shader_url, zipped_shader_dir), self.unzip_shader(self.shader_temp_directory, repo_name, zipped_shader_dir))

                current_repo += 1
        except Exception as e:
            raise IOError(f"Download shaders failed: {e}") from e

    def organize_files(self, shader_temp_dir: str, shaders_dir: str, textures_dir: str) -> None:
        try:
            for root, dirs, files in os.walk(shader_temp_dir):
                if ".git" in root:
                    continue

                try:
                    for dir in dirs:
                        src_dir: str = os.path.join(root, dir)

                        if dir == "Shaders":
                            shutil.copytree(
                                src_dir, shaders_dir, dirs_exist_ok=True)

                        if dir == "Textures":
                            shutil.copytree(
                                src_dir, textures_dir, dirs_exist_ok=True)

                    # I will leave it here, maybe I will need it someday, who knows...
                    '''
                    for file in files:
                        file_lower: str = file.lower()
                        src_file: str = os.path.join(root, file)

                        if file_lower.endswith(('.fx', '.fxh')):
                            if not Path(os.path.join(shaders_dir, file)).exists():
                                shutil.copy2(
                                    src_file, os.path.join(shaders_dir, file))

                        if file_lower.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tga')):
                            if not Path(os.path.join(textures_dir, file)).exists():
                                shutil.copy2(src_file, os.path.join(
                                    textures_dir, file))
                    '''
                except Exception as e:
                    raise IOError(f"Failed to organize files: {e}") from e
            self.clone_finished.emit(True)
        except Exception as e:
            # I've already over the except on the inner try
            print(e)
            self.clone_finished.emit(False)
