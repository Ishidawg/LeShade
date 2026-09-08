import glob
import json
import os
import re
import shutil
import ssl
import subprocess
import urllib.request
from pathlib import Path
from zipfile import ZipFile

import certifi
from PySide6.QtCore import QObject, Signal

from scripts_core.script_prefix import (
    configure_heroic_game,
    find_heroic_game_config,
    find_wine_prefix,
    setup_prefix_system32_nvngx,
)
from scripts_core.script_scanner import get_pe_imports
from utils.utils import EXTRACT_PATH, download, unzip_file

CACHE_DIR = os.path.expanduser("~/.cache/leshade/dlss5")
LOCAL_DOWNLOADS_DIR = "/home/cado/Downloads/DLSS5"

# Component URLs
URL_FEEDER_ZIP = "https://github.com/jlrouzies-fr/DLSS5-Feeder/releases/download/v0.12.0/DLSS5-Feeder-0.12.0.zip"
URL_LUMENITE_ZIP = "https://codeload.github.com/umar-afzaal/LumeniteFX/zip/refs/heads/mainline"
URL_RESHADE_FXH = "https://raw.githubusercontent.com/crosire/reshade-shaders/slim/Shaders/ReShade.fxh"
URL_RESHADE_UI_FXH = "https://raw.githubusercontent.com/crosire/reshade-shaders/slim/Shaders/ReShadeUI.fxh"


def detect_nvidia_gpu() -> dict:
    """
    Detects the installed NVIDIA GPU and maps compute capability to architecture.
    """
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,compute_cap", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            check=True,
        )
        line = out.stdout.strip().split("\n")[0]
        parts = [x.strip() for x in line.split(",")]
        name = parts[0]
        cap_str = parts[1] if len(parts) > 1 else "0.0"
        cap = float(cap_str)

        if cap >= 12.0:
            arch = "Blackwell"
            build = "310.8.0"
            cost = "full speed (FP8 native)"
            supported = True
        elif cap >= 8.9:
            arch = "Ada Lovelace"
            build = "310.8.0-RTX40"
            cost = "moderate (sm_89)"
            supported = True
        elif cap >= 8.6:
            arch = "Ampere"
            build = "310.8.SF-v2"
            cost = "heavy (FP16)"
            supported = True
        elif cap >= 7.5:
            arch = "Turing"
            build = "310.8.SF-v2"
            cost = "heavy (FP16)"
            supported = True
        else:
            arch = "Legacy / Pascal"
            build = None
            cost = "unsupported"
            supported = False

        return {
            "name": name,
            "compute_cap": cap_str,
            "arch": arch,
            "supported": supported,
            "recommended_build": build,
            "cost": cost,
        }
    except Exception as e:
        return {
            "name": "NVIDIA GPU Not Detected",
            "compute_cap": "0.0",
            "arch": "Unknown",
            "supported": False,
            "recommended_build": None,
            "cost": "N/A",
            "error": str(e),
        }


def detect_game_dlss_capability(exe_path: str) -> dict:
    """
    Analyzes game directory and executable imports to determine if the game has
    native DLSS, FSR, or XeSS, and recommends the best DLSS 5 route.
    """
    if not exe_path or not os.path.exists(exe_path):
        return {
            "has_dlss": False,
            "has_fsr": False,
            "has_xess": False,
            "recommended_route": "feeder",
            "reason": "Executable not found",
        }

    game_dir = Path(exe_path).resolve().parent

    has_dlss = False
    has_fsr = False
    has_xess = False

    # Check DLLs in directory
    dlss_files = ["nvngx_dlss.dll", "sl.dlss.dll", "sl.interposer.dll"]
    for f in dlss_files:
        if (game_dir / f).is_file():
            has_dlss = True
            break

    fsr_files = ["ffx_fsr2_api_x64.dll", "ffx_fsr3_api_x64.dll", "amd_fidelityfx_dx12.dll"]
    for f in fsr_files:
        if (game_dir / f).is_file():
            has_fsr = True
            break

    if (game_dir / "libxess.dll").is_file():
        has_xess = True

    # Check PE imports if DLLs not found directly
    if not (has_dlss or has_fsr or has_xess):
        imports = [i.lower() for i in get_pe_imports(exe_path)]
        if any("nvngx" in i or "streamline" in i for i in imports):
            has_dlss = True
        if any("ffx_fsr" in i for i in imports):
            has_fsr = True
        if any("xess" in i for i in imports):
            has_xess = True

    if has_dlss:
        recommended = "optiscaler"
        reason = "Jogo possui DLSS nativo detectado (Rota OptiScaler recomendada)"
    elif has_fsr or has_xess:
        recommended = "optiscaler"
        reason = "Jogo possui FSR/XeSS nativo detectado (Rota OptiScaler recomendada)"
    else:
        recommended = "feeder"
        reason = "Jogo sem DLSS nativo (Rota Feeder com vetores de movimento Lumenite recomendada)"

    return {
        "has_dlss": has_dlss,
        "has_fsr": has_fsr,
        "has_xess": has_xess,
        "recommended_route": recommended,
        "reason": reason,
    }


def detect_anticheat(exe_path: str) -> list[str]:
    """
    Checks the game directory and imports for known anti-cheat software.
    """
    if not exe_path or not os.path.exists(exe_path):
        return []

    game_dir = Path(exe_path).resolve().parent
    detected = []

    signatures = {
        "Easy Anti-Cheat": ["easyanticheat", "eac_server.dll", "easyanticheat_eos_setup.exe", "start_protected_game.exe"],
        "BattlEye": ["beservice.exe", "battleye", "belauncher.exe"],
        "Vanguard": ["vgk.sys", "vgc.exe"],
        "Denuvo Anti-Cheat": ["denuvo"],
        "Ricochet": ["ricochet"],
        "PunkBuster": ["pnkbstra.exe", "pnkbstrb.exe"],
        "GameGuard": ["gameguard"],
        "XIGNCODE3": ["xigncode"],
    }

    # Scan game directory files and parent directory for anti-cheat files
    all_files = []
    try:
        for f in game_dir.glob("*"):
            all_files.append(f.name.lower())
        if game_dir.parent:
            for f in game_dir.parent.glob("*"):
                all_files.append(f.name.lower())
    except Exception:
        pass

    for ac_name, patterns in signatures.items():
        for pattern in patterns:
            if any(pattern in fname for fname in all_files):
                if ac_name not in detected:
                    detected.append(ac_name)
                    break

    return detected


def generate_dlss5_feed_cfg(preset: str = "balanced") -> str:
    """
    Generates the dlss5-feed.cfg content based on the selected performance preset.
    """
    if preset == "performance":
        work_res = 50
        work_up = 1
        sharpness = 0.50
    elif preset == "quality":
        work_res = 100
        work_up = 0
        sharpness = 0.00
    else:  # balanced
        work_res = 70
        work_up = 1
        sharpness = 0.35

    return f"""enabled=1
mode=2
hdr=-1
depth_inverted=-1
flags=-1
reset_every=0
warmup_rebuild=180
rebuild=0
log_frames=3
create_delay=120
preset=0
work_resolution={work_res}
work_upscale={work_up}
work_sharpness={sharpness:.2f}
"""


def clean_conflicting_files(game_dir: Path) -> None:
    """
    Removes files that conflict with DLSS 5 operation on Linux/Proton.
    """
    # 1. Host NVNGX should reside in prefix windows/system32, not in game directory
    for f in ["_nvngx.dll", "nvngx.dll"]:
        p = game_dir / f
        if p.is_file():
            try:
                p.unlink()
            except Exception:
                pass

    # 2. Disable older RenoDX DLSS add-on if present
    old_addon = game_dir / "renodx-dlss.addon64"
    if old_addon.is_file():
        try:
            old_addon.rename(game_dir / "renodx-dlss.addon64.disabled")
        except Exception:
            pass

    # 3. Backup DLSS-D and DLSS-G if present
    for extra_dll in ["nvngx_dlssd.dll", "nvngx_dlssg.dll"]:
        p = game_dir / extra_dll
        if p.is_file():
            try:
                p.rename(game_dir / f"{extra_dll}.bak")
            except Exception:
                pass

    # 4. Clean old logs
    for log_name in ["ReShade.log", "dlss5-feed.log"]:
        p = game_dir / log_name
        if p.is_file():
            try:
                p.unlink()
            except Exception:
                pass


def update_reshade_preset_order(game_dir: Path) -> None:
    """
    Ensures ReShadePreset.ini places Lumenite_Kernel.fx before DLSS5_Feed.fx.
    """
    preset_path = game_dir / "ReShadePreset.ini"
    techniques = [
        "Lumenite_Kernel@lumenite_Kernel.fx",
        "DLSS5_Feed@DLSS5_Feed.fx",
    ]

    content = f"""[General]
PreprocessorDefinitions=DLSS5_MV_PROVIDER=3

Techniques={','.join(techniques)}
TechniqueSorting={','.join(techniques)}
"""
    try:
        preset_path.write_text(content, encoding="utf-8")
    except Exception as e:
        print(f"Error updating ReShadePreset.ini: {e}")


def update_reshade_ini_mv(game_dir: Path) -> None:
    """
    Ensures ReShade.ini contains DLSS5_MV_PROVIDER=3 preprocessor definition.
    """
    ini_path = game_dir / "ReShade.ini"
    if not ini_path.is_file():
        return

    try:
        text = ini_path.read_text(encoding="utf-8", errors="ignore")
        if "DLSS5_MV_PROVIDER" not in text:
            if "PreprocessorDefinitions=" in text:
                text = text.replace(
                    "PreprocessorDefinitions=",
                    "PreprocessorDefinitions=DLSS5_MV_PROVIDER=3,",
                )
            else:
                text += "\n[GENERAL]\nPreprocessorDefinitions=DLSS5_MV_PROVIDER=3\n"
            ini_path.write_text(text, encoding="utf-8")
    except Exception as e:
        print(f"Error updating ReShade.ini MV definition: {e}")


class DLSS5InstallWorker(QObject):
    """
    Worker for installing DLSS 5 Autopilot asynchronously.
    """
    progress: Signal = Signal(int, str)
    finished: Signal = Signal(bool, str)

    def __init__(
        self,
        game_exe_path: str,
        route: str = "feeder",
        performance_preset: str = "balanced",
        is_steam: bool = False,
        wine_prefix: str = "",
    ):
        super().__init__()
        self.game_exe = Path(game_exe_path).resolve()
        self.game_dir = self.game_exe.parent
        self.route = route
        self.preset = performance_preset
        self.is_steam = is_steam
        self.wine_prefix = wine_prefix

    def run(self) -> None:
        try:
            os.makedirs(CACHE_DIR, exist_ok=True)
            self.progress.emit(10, "Detectando hardware e prefixo...")

            # 1. Locate Wine Prefix and configure
            prefix = self.wine_prefix or find_wine_prefix(str(self.game_exe), self.is_steam)
            if prefix:
                self.progress.emit(20, f"Configurando prefixo Wine ({prefix})...")
                setup_prefix_system32_nvngx(prefix)

            # 2. Configure Heroic if applicable
            heroic_cfg, cfg_file, app_id = find_heroic_game_config(str(self.game_exe))
            if cfg_file:
                self.progress.emit(30, "Injetando variáveis no Heroic Games Launcher...")
                configure_heroic_game(cfg_file, app_id)

            # 3. Clean conflicting files
            self.progress.emit(40, "Limpando DLLs e arquivos conflitantes...")
            clean_conflicting_files(self.game_dir)

            # 4. Download and setup components
            if self.route == "feeder":
                self.setup_feeder_route()
            else:
                self.setup_optiscaler_route()

            self.progress.emit(90, "Gravando configurações de performance...")
            cfg_content = generate_dlss5_feed_cfg(self.preset)
            (self.game_dir / "dlss5-feed.cfg").write_text(cfg_content, encoding="utf-8")

            update_reshade_preset_order(self.game_dir)
            update_reshade_ini_mv(self.game_dir)

            self.progress.emit(100, "DLSS 5 Autopilot instalado com sucesso!")
            self.finished.emit(True, "DLSS 5 Autopilot instalado com sucesso!")
        except Exception as e:
            self.finished.emit(False, f"Erro na instalação: {e}")

    def download_url(self, url: str, dest_path: str) -> None:
        if os.path.exists(dest_path):
            return
        context = ssl.create_default_context(cafile=certifi.where())
        req = urllib.request.Request(url, headers={"User-Agent": "LeShade/DLSS5"})
        with urllib.request.urlopen(req, context=context) as resp, open(dest_path, "wb") as f:
            f.write(resp.read())

    def setup_feeder_route(self) -> None:
        self.progress.emit(50, "Obtendo DLSS 5 Feeder e shaders...")
        feeder_zip = os.path.join(CACHE_DIR, "DLSS5-Feeder-0.12.0.zip")
        lumenite_zip = os.path.join(CACHE_DIR, "lumenite.zip")

        # Use local downloads if available, otherwise fetch
        local_feeder = os.path.join(LOCAL_DOWNLOADS_DIR, "DLSS5-Feeder-0.12.0.zip")
        if os.path.isfile(local_feeder):
            shutil.copy2(local_feeder, feeder_zip)
        else:
            self.download_url(URL_FEEDER_ZIP, feeder_zip)

        local_lumenite = os.path.join(LOCAL_DOWNLOADS_DIR, "lumenite.zip")
        if os.path.isfile(local_lumenite):
            shutil.copy2(local_lumenite, lumenite_zip)
        else:
            self.download_url(URL_LUMENITE_ZIP, lumenite_zip)

        feeder_extract = os.path.join(CACHE_DIR, "feeder_tmp")
        lumenite_extract = os.path.join(CACHE_DIR, "lumenite_tmp")
        os.makedirs(feeder_extract, exist_ok=True)
        os.makedirs(lumenite_extract, exist_ok=True)

        unzip_file(feeder_zip, feeder_extract)
        unzip_file(lumenite_zip, lumenite_extract)

        # Install shaders & textures
        shaders_dir = self.game_dir / "reshade-shaders" / "Shaders"
        textures_dir = self.game_dir / "reshade-shaders" / "Textures"
        shaders_dir.mkdir(parents=True, exist_ok=True)
        textures_dir.mkdir(parents=True, exist_ok=True)

        # Download slim headers
        self.download_url(URL_RESHADE_FXH, str(shaders_dir / "ReShade.fxh"))
        self.download_url(URL_RESHADE_UI_FXH, str(shaders_dir / "ReShadeUI.fxh"))

        # Copy Feeder shader
        src_feed = os.path.join(feeder_extract, "reshade-shaders", "Shaders", "DLSS5_Feed.fx")
        if os.path.isfile(src_feed):
            shutil.copy2(src_feed, str(shaders_dir / "DLSS5_Feed.fx"))

        # Copy Lumenite shaders
        lumenite_src_dir = os.path.join(lumenite_extract, "LumeniteFX-mainline", "Shaders")
        if os.path.isdir(lumenite_src_dir):
            shutil.copytree(lumenite_src_dir, str(shaders_dir), dirs_exist_ok=True)

        lumenite_tex_src = os.path.join(
            lumenite_extract, "LumeniteFX-mainline", "Textures", "lumenite_bluenoise256.png"
        )
        if os.path.isfile(lumenite_tex_src):
            shutil.copy2(lumenite_tex_src, str(textures_dir / "lumenite_bluenoise256.png"))

        # Copy dlss5-feed.addon64
        src_addon = os.path.join(feeder_extract, "dlss5-feed.addon64")
        if os.path.isfile(src_addon):
            shutil.copy2(src_addon, str(self.game_dir / "dlss5-feed.addon64"))

        # Copy renodx-dlss5.addon64 (v4.1.5 stable)
        self.progress.emit(70, "Instalando RenoDX DLSS 5 estável (v4.1.5)...")
        local_renodx = os.path.join(LOCAL_DOWNLOADS_DIR, "renodx-dlss5.addon64")
        local_renodx_zip = os.path.join(LOCAL_DOWNLOADS_DIR, "renodx-dlss5_4.5.zip")

        if os.path.isfile(local_renodx):
            shutil.copy2(local_renodx, str(self.game_dir / "renodx-dlss5.addon64"))
        elif os.path.isfile(local_renodx_zip):
            with ZipFile(local_renodx_zip, "r") as z:
                z.extract("renodx-dlss5.addon64", str(self.game_dir))

        # Copy nvngx_dlssnr.dll
        self.progress.emit(80, "Instalando runtime DLSS Neural (nvngx_dlssnr.dll)...")
        local_dlssnr = os.path.join(LOCAL_DOWNLOADS_DIR, "nvngx_dlssnr.dll")
        if os.path.isfile(local_dlssnr):
            shutil.copy2(local_dlssnr, str(self.game_dir / "nvngx_dlssnr.dll"))

    def setup_optiscaler_route(self) -> None:
        self.progress.emit(60, "Configurando Rota OptiScaler...")
        # Copies OptiScaler runtime DLLs
        local_optiscaler = os.path.join(LOCAL_DOWNLOADS_DIR, "OptiScaler_v10.0.0-pre1_20260903.7z")
        local_dlssnr = os.path.join(LOCAL_DOWNLOADS_DIR, "nvngx_dlssnr.dll")
        if os.path.isfile(local_dlssnr):
            shutil.copy2(local_dlssnr, str(self.game_dir / "nvngx_dlssnr.dll"))
