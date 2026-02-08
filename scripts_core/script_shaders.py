import os
from pathlib import Path
import shutil
import zipfile

from PySide6.QtCore import (
    QObject,
    QStandardPaths,
    Signal
)

import urllib.request
import ssl
import certifi

REPO_SHADERS = {
    "crosire_slim": {
        "url": "https://github.com/crosire/reshade-shaders",
        "branch": "slim"
    },
    "crosire_legacy": {
        "url": "https://github.com/crosire/reshade-shaders",
        "branch": "legacy"
    },
    "sweet_fx": {
        "url": "https://github.com/CeeJayDK/SweetFX",
        "branch": "master"
    },
    "prod80": {
        "url": "https://github.com/prod80/prod80-ReShade-Repository",
        "branch": "master"
    },
    "quint": {
        "url": "https://github.com/martymcmodding/qUINT",
        "branch": "master"
    },
    "immerse": {
        "url": "https://github.com/martymcmodding/iMMERSE",
        "branch": "main"
    },
    "MLUT": {
        "url": "https://github.com/TheGordinho/MLUT",
        "branch": "master"
    },
    "insane": {
        "url": "https://github.com/LordOfLunacy/Insane-Shaders",
        "branch": "master"
    },
    "retro_arch": {
        "url": "https://github.com/Matsilagi/RSRetroArch",
        "branch": "main"
    },
    "crt_royale": {
        "url": "https://github.com/akgunter/crt-royale-reshade",
        "branch": "master"
    },
    "gramarye": {
        "url": "https://github.com/rj200/Glamarye_Fast_Effects_for_ReShade",
        "branch": "main"
    }
}


class ShadersWorker(QObject):
    def __init__(self, selections: list[str]):
        super().__init__()

        self.game_path: str = "/home/ishidaw/SteamDirectory/steamapps/common/DARK SOULS REMASTERED"
        self.selected_repos: list[str] = selections
        self.total_repos: int = 0

        """
        "shader_repo": {
            "files": ["file1.fx, file2.fx"],
        }

        """

        self.downloaded_shaders = {

        }

    def run(self) -> None:
        self.download_shaders()

    def get_selected(self) -> None:
        pass

    def unzip_shader(self, shader_temp_dir: str, repo_name: str, zipped_dir: str) -> None:
        extracted_shader_dir: str = os.path.join(shader_temp_dir, repo_name)
        os.makedirs(extracted_shader_dir, exist_ok=True)

        with zipfile.ZipFile(zipped_dir, 'r') as zip_ref:
            zip_ref.extractall(extracted_shader_dir)

    def download_shaders(self) -> None:
        if not self.game_path:
            raise ValueError("Path error")

        shader_temp_directory: str = os.path.join(
            self.game_path, ".shaders_temp")

        os.makedirs(shader_temp_directory, exist_ok=True)

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
                    shader_temp_directory, f"{repo_name}.zip")

                try:
                    context = ssl.create_default_context(
                        cafile=certifi.where())

                    req = urllib.request.Request(
                        shader_url, headers={'User-Agent': 'Chrome/121.0.0.0'})

                    with urllib.request.urlopen(req, context=context) as res:
                        with open(zipped_shader_dir, 'wb') as out_file:
                            out_file.write(res.read())

                    self.unzip_shader(shader_temp_directory,
                                      repo_name, zipped_shader_dir)
                except Exception as e:
                    continue

                current_repo += 1
        except Exception as e:
            pass

    def _organize_files(self, source_root, shaders_dest, textures_dest):
        for root, dirs, files in os.walk(source_root):
            if ".git" in root:
                continue

            for file in files:
                file_lower = file.lower()
                src_file = os.path.join(root, file)

                if file_lower.endswith(('.fx', '.fxh')):
                    shutil.copy2(src_file, os.path.join(shaders_dest, file))

                elif file_lower.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tga')):
                    shutil.copy2(src_file, os.path.join(textures_dest, file))
