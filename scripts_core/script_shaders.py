import asyncio
import configparser
import os
import shutil
import urllib.request
from pathlib import Path

from PySide6.QtCore import QObject, QStandardPaths, Signal

from scripts_core.script_addons import install_addon
from utils.utils import generic_download, unzip_file

EFFECT_PACKAGES_URL = (
    "https://raw.githubusercontent.com/crosire/reshade-shaders/list/EffectPackages.ini"
)

REPO_SHADERS = {
    "Crosire slim": {
        "url": "https://github.com/crosire/reshade-shaders",
        "branch": "slim",
    },
    "Crosire legacy": {
        "url": "https://github.com/crosire/reshade-shaders",
        "branch": "legacy",
    },
    "Sweet FX": {"url": "https://github.com/CeeJayDK/SweetFX", "branch": "master"},
    "Prod80": {
        "url": "https://github.com/prod80/prod80-ReShade-Repository",
        "branch": "master",
    },
    "qUINT": {"url": "https://github.com/martymcmodding/qUINT", "branch": "master"},
    "iMMERSE": {"url": "https://github.com/martymcmodding/iMMERSE", "branch": "main"},
    "MLUT": {"url": "https://github.com/TheGordinho/MLUT", "branch": "master"},
    "Insane shaders": {
        "url": "https://github.com/LordOfLunacy/Insane-Shaders",
        "branch": "master",
    },
    "RS Retro Arch": {
        "url": "https://github.com/Matsilagi/RSRetroArch",
        "branch": "main",
    },
    "CRT Royale": {
        "url": "https://github.com/akgunter/crt-royale-reshade",
        "branch": "master",
    },
    "Glamarye Fast Effects": {
        "url": "https://github.com/rj200/Glamarye_Fast_Effects_for_ReShade",
        "branch": "main",
    },
    "ReShade HDR Shaders": {
        "url": "https://github.com/EndlesslyFlowering/ReShade_HDR_shaders",
        "branch": "master",
    },
    "Pumbo Auto HDR": {
        "url": "https://github.com/Filoppi/PumboAutoHDR",
        "branch": "master",
    },
    "PotatoFX": {
        "url": "https://github.com/GimleLarpes/potatoFX",
        "branch": "main",
    },
    "ReShade Simple HDR Shaders": {
        "url": "https://github.com/MaxG2D/ReshadeSimpleHDRShaders",
        "branch": "main",
    },
}


def get_shaders_cache_dir() -> str:
    cache_base = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.CacheLocation
    )
    cache_dir = os.path.join(cache_base, "leshade")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def fetch_effect_packages(use_cache: bool = True) -> list[dict]:
    """
    Downloads and parses the official ReShade EffectPackages.ini.
    Caches the list in ~/.cache/leshade/EffectPackages.ini for offline resilience.
    Falls back to built-in list if offline and cache is missing.
    """
    cache_file = os.path.join(get_shaders_cache_dir(), "EffectPackages.ini")
    content = ""

    try:
        req = urllib.request.Request(
            EFFECT_PACKAGES_URL,
            headers={"User-Agent": "LeShade/2.5.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
            try:
                with open(cache_file, "w", encoding="utf-8") as f:
                    f.write(content)
            except Exception:
                pass
    except Exception:
        if use_cache and os.path.isfile(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                content = ""

    packages = []
    if content:
        config = configparser.ConfigParser(interpolation=None)
        config.read_string(content)
        for sec in config.sections():
            name = config.get(sec, "PackageName", fallback="").strip()
            download_url = config.get(sec, "DownloadUrl", fallback="").strip()
            if not name or not download_url:
                continue

            desc = config.get(sec, "PackageDescription", fallback="").strip()
            install_path = config.get(
                sec, "InstallPath", fallback=r".\reshade-shaders\Shaders"
            ).strip()
            texture_install_path = config.get(
                sec, "TextureInstallPath", fallback=r".\reshade-shaders\Textures"
            ).strip()
            repo_url = config.get(sec, "RepositoryUrl", fallback="").strip()
            enabled = config.get(sec, "Enabled", fallback="0").strip() == "1"
            required = config.get(sec, "Required", fallback="0").strip() == "1"

            deny_raw = config.get(sec, "DenyEffectFiles", fallback="").strip()
            deny_files = [f.strip() for f in deny_raw.split(",") if f.strip()]

            packages.append({
                "id": sec,
                "name": name,
                "description": desc,
                "install_path": install_path,
                "texture_install_path": texture_install_path,
                "download_url": download_url,
                "repository_url": repo_url,
                "enabled": enabled,
                "required": required,
                "deny_effect_files": deny_files,
            })

    if not packages:
        for name, data in REPO_SHADERS.items():
            packages.append({
                "id": name,
                "name": name,
                "description": f"Repository from {data['url']}",
                "install_path": r".\reshade-shaders\Shaders",
                "texture_install_path": r".\reshade-shaders\Textures",
                "download_url": f"{data['url']}/archive/refs/heads/{data['branch']}.zip",
                "repository_url": data["url"],
                "enabled": (name == "Crosire slim"),
                "required": False,
                "deny_effect_files": [],
            })

    return packages


class ShadersWorker(QObject):
    clone_finished: Signal = Signal(bool)

    def __init__(
        self,
        selections: list[dict | str],
        renodx_asset: str,
        game_dir: str,
        selected_addons: list[dict] | None = None,
    ):
        super().__init__()

        self.selected_renodx_asset: str = renodx_asset
        self.game_path: str = game_dir
        self.selected_repos: list[dict | str] = selections
        self.selected_addons: list[dict] = selected_addons or []
        self.total_repos: int = 0

        self.shader_temp_directory: str = os.path.join(self.game_path, ".shaders_temp")
        self.shader_dir: str = os.path.join(self.game_path, "reshade-shaders/Shaders")
        self.texture_dir: str = os.path.join(self.game_path, "reshade-shaders/Textures")

    def run(self) -> None:
        self.clean_temp()
        try:
            asyncio.run(self.install_all())
            self.clean_temp()
            self.clone_finished.emit(True)
        except Exception as e:
            print(f"Error during installation: {e}")
            self.clean_temp()
            self.clone_finished.emit(False)

    def clean_temp(self) -> None:
        if Path(self.shader_temp_directory).exists():
            shutil.rmtree(self.shader_temp_directory)

    async def download_shaders(self, shader_url: str, zipped_shader_dir: str) -> None:
        try:
            generic_download(shader_url, zipped_shader_dir)
        except Exception as e:
            raise IOError(f"Downloading shader package failed: {e}") from e

    async def download_renodx_asset(self, asset_url: str, game_dir: str) -> None:
        if not self.selected_renodx_asset or self.selected_renodx_asset == "None":
            return

        try:
            generic_download(asset_url, game_dir)
        except Exception as e:
            raise IOError(f"Downloading renodx asset failed: {e}") from e

    async def install_all(self) -> None:
        if not self.game_path:
            raise ValueError("Invalid game path")

        os.makedirs(self.shader_temp_directory, exist_ok=True)

        # 1. Download RenoDX asset if selected
        if self.selected_renodx_asset and self.selected_renodx_asset != "None":
            renodx_url: str = f"https://github.com/clshortfuse/renodx/releases/download/snapshot/{self.selected_renodx_asset}"
            renodx_asset_dir: str = os.path.join(
                self.game_path, renodx_url.split("/")[-1].strip()
            )
            await self.download_renodx_asset(renodx_url, renodx_asset_dir)

        # 2. Install official ReShade add-ons if selected
        for addon in self.selected_addons:
            try:
                install_addon(addon, self.game_path, self.shader_temp_directory)
            except Exception as e:
                print(f"Warning: Failed to install addon {addon.get('name')}: {e}")

        # 3. Install shader packages
        for item in self.selected_repos:
            if isinstance(item, dict):
                await self.install_package_dict(item)
            elif isinstance(item, str):
                await self.install_legacy_or_named_package(item)

    async def install_package_dict(self, pkg: dict) -> None:
        safe_id = "".join(c for c in pkg.get("id", pkg["name"]) if c.isalnum() or c in "_-")
        zip_path = os.path.join(self.shader_temp_directory, f"{safe_id}.zip")
        extract_dir = os.path.join(self.shader_temp_directory, safe_id)

        await self.download_shaders(pkg["download_url"], zip_path)

        os.makedirs(extract_dir, exist_ok=True)
        unzip_file(zip_path, extract_dir)

        install_rel = (
            pkg.get("install_path", r".\reshade-shaders\Shaders")
            .replace("\\", "/")
            .lstrip("./")
        )
        texture_rel = (
            pkg.get("texture_install_path", r".\reshade-shaders\Textures")
            .replace("\\", "/")
            .lstrip("./")
        )

        target_shaders_dir = os.path.join(self.game_path, install_rel)
        target_textures_dir = os.path.join(self.game_path, texture_rel)

        os.makedirs(target_shaders_dir, exist_ok=True)
        os.makedirs(target_textures_dir, exist_ok=True)

        deny_files = set(f.lower() for f in pkg.get("deny_effect_files", []))
        self.copy_package_contents(
            extract_dir, target_shaders_dir, target_textures_dir, deny_files
        )

    async def install_legacy_or_named_package(self, repo_key: str) -> None:
        repo_data = REPO_SHADERS.get(repo_key)
        if not repo_data:
            return

        repo_name = repo_key
        repo_branch = repo_data["branch"]
        repo_url = repo_data["url"]
        shader_url = f"{repo_url}/archive/refs/heads/{repo_branch}.zip"

        zipped_shader_dir = os.path.join(
            self.shader_temp_directory, f"{repo_name}.zip"
        )
        extracted_shader_dir = os.path.join(self.shader_temp_directory, repo_name)

        await self.download_shaders(shader_url, zipped_shader_dir)

        os.makedirs(extracted_shader_dir, exist_ok=True)
        unzip_file(zipped_shader_dir, extracted_shader_dir)

        os.makedirs(self.shader_dir, exist_ok=True)
        os.makedirs(self.texture_dir, exist_ok=True)

        self.copy_package_contents(
            extracted_shader_dir, self.shader_dir, self.texture_dir, set()
        )

    def copy_package_contents(
        self,
        extract_dir: str,
        target_shaders: str,
        target_textures: str,
        deny_files: set[str],
    ) -> None:
        shaders_source = None
        textures_source = None

        for root, dirs, _ in os.walk(extract_dir):
            if ".git" in root:
                continue
            for d in dirs:
                if d.lower() == "shaders" and shaders_source is None:
                    shaders_source = os.path.join(root, d)
                elif d.lower() == "textures" and textures_source is None:
                    textures_source = os.path.join(root, d)

        # Copy shaders
        if shaders_source and os.path.isdir(shaders_source):
            for root, _, files in os.walk(shaders_source):
                rel = os.path.relpath(root, shaders_source)
                dest = os.path.join(target_shaders, rel) if rel != "." else target_shaders
                os.makedirs(dest, exist_ok=True)
                for f in files:
                    if f.lower() not in deny_files:
                        shutil.copy2(os.path.join(root, f), os.path.join(dest, f))
        else:
            for root, _, files in os.walk(extract_dir):
                if ".git" in root:
                    continue
                for f in files:
                    if (
                        f.lower().endswith(".fx") or f.lower().endswith(".fxh")
                    ) and f.lower() not in deny_files:
                        shutil.copy2(os.path.join(root, f), os.path.join(target_shaders, f))

        # Copy textures
        if textures_source and os.path.isdir(textures_source):
            for root, _, files in os.walk(textures_source):
                rel = os.path.relpath(root, textures_source)
                dest = os.path.join(target_textures, rel) if rel != "." else target_textures
                os.makedirs(dest, exist_ok=True)
                for f in files:
                    shutil.copy2(os.path.join(root, f), os.path.join(dest, f))
        else:
            img_exts = {".png", ".dds", ".bmp", ".jpg", ".jpeg"}
            for root, _, files in os.walk(extract_dir):
                if ".git" in root:
                    continue
                for f in files:
                    ext = os.path.splitext(f)[1].lower()
                    if ext in img_exts:
                        shutil.copy2(os.path.join(root, f), os.path.join(target_textures, f))

