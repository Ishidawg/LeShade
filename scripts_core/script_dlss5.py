import os
import re
import shutil
import subprocess
from pathlib import Path
from zipfile import ZipFile

from PySide6.QtCore import QObject, Signal

from scripts_core.script_prefix import (
    configure_heroic_game,
    find_heroic_game_config,
    find_wine_prefix,
    setup_prefix_system32_nvngx,
)
from scripts_core.script_scanner import get_pe_imports
from utils.utils import generic_download, unzip_file

CACHE_DIR = os.path.expanduser("~/.cache/leshade/dlss5")

# Optional directory with components that have no public download URL
# (renodx-dlss5.addon64, nvngx_dlssnr.dll, OptiScaler archive). When unset,
# those components are reported as missing instead of silently skipped.
LOCAL_COMPONENTS_ENV = "LESHADE_DLSS5_COMPONENTS_DIR"

# Component URLs
URL_FEEDER_ZIP = "https://github.com/jlrouzies-fr/DLSS5-Feeder/releases/download/v0.12.0/DLSS5-Feeder-0.12.0.zip"
URL_LUMENITE_ZIP = "https://codeload.github.com/umar-afzaal/LumeniteFX/zip/refs/heads/mainline"
URL_RESHADE_FXH = "https://raw.githubusercontent.com/crosire/reshade-shaders/slim/Shaders/ReShade.fxh"
URL_RESHADE_UI_FXH = "https://raw.githubusercontent.com/crosire/reshade-shaders/slim/Shaders/ReShadeUI.fxh"

FEEDER_ZIP_NAME = "DLSS5-Feeder-0.12.0.zip"
RENODX_ADDON_NAME = "renodx-dlss5.addon64"
RENODX_ZIP_NAME = "renodx-dlss5_4.5.zip"
DLSSNR_DLL_NAME = "nvngx_dlssnr.dll"
OPTISCALER_ARCHIVE_PATTERN = re.compile(r"^OptiScaler.*\.(7z|zip)$", re.IGNORECASE)

DLSS5_TECHNIQUES = [
    "Lumenite_Kernel@lumenite_Kernel.fx",
    "DLSS5_Feed@DLSS5_Feed.fx",
]
MV_PROVIDER_DEFINE = "DLSS5_MV_PROVIDER=3"


def get_local_components_dir() -> str | None:
    value = os.environ.get(LOCAL_COMPONENTS_ENV, "").strip()
    if value and os.path.isdir(value):
        return value
    return None


def find_local_component(file_name: str) -> str | None:
    base = get_local_components_dir()
    if not base:
        return None
    candidate = os.path.join(base, file_name)
    return candidate if os.path.isfile(candidate) else None


def find_local_optiscaler_archive() -> str | None:
    base = get_local_components_dir()
    if not base:
        return None
    for entry in sorted(os.listdir(base)):
        if OPTISCALER_ARCHIVE_PATTERN.match(entry):
            return os.path.join(base, entry)
    return None


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
            timeout=10,
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
        reason = "Native DLSS detected (OptiScaler route recommended)"
    elif has_fsr or has_xess:
        recommended = "optiscaler"
        reason = "Native FSR/XeSS detected (OptiScaler route recommended)"
    else:
        recommended = "feeder"
        reason = "No native DLSS (Feeder route with Lumenite motion vectors recommended)"

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


def backup_file(path: Path) -> Path | None:
    """
    Copies path to path + '.leshade.bak' (first backup only, never overwritten).
    """
    if not path.is_file():
        return None
    backup = path.with_name(path.name + ".leshade.bak")
    if backup.exists():
        return backup
    try:
        shutil.copy2(path, backup)
        return backup
    except Exception as e:
        print(f"Warning: could not back up {path}: {e}")
        return None


def merge_csv_values(existing: str, required: list[str], prepend: bool) -> str:
    current = [v.strip() for v in existing.split(",") if v.strip()]
    missing = [v for v in required if v not in current]
    merged = (missing + current) if prepend else (current + missing)
    return ",".join(merged)


def update_reshade_preset_order(game_dir: Path) -> None:
    """
    Ensures ReShadePreset.ini enables Lumenite_Kernel.fx before DLSS5_Feed.fx
    and defines DLSS5_MV_PROVIDER, preserving any existing user preset.
    A backup is written before the first modification.
    """
    preset_path = game_dir / "ReShadePreset.ini"

    if not preset_path.is_file():
        content = (
            "[General]\n"
            f"PreprocessorDefinitions={MV_PROVIDER_DEFINE}\n"
            "\n"
            f"Techniques={','.join(DLSS5_TECHNIQUES)}\n"
            f"TechniqueSorting={','.join(DLSS5_TECHNIQUES)}\n"
        )
        try:
            preset_path.write_text(content, encoding="utf-8")
        except Exception as e:
            print(f"Error writing ReShadePreset.ini: {e}")
        return

    backup_file(preset_path)

    try:
        lines = preset_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception as e:
        print(f"Error reading ReShadePreset.ini: {e}")
        return

    seen = {"Techniques": False, "TechniqueSorting": False, "PreprocessorDefinitions": False}
    general_index = -1
    result: list[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped.lower() == "[general]":
            general_index = len(result)
            result.append(line)
            continue

        key, sep, value = line.partition("=")
        key = key.strip()
        if sep and key in seen:
            seen[key] = True
            if key == "PreprocessorDefinitions":
                line = f"{key}={merge_csv_values(value, [MV_PROVIDER_DEFINE], prepend=False)}"
            else:
                line = f"{key}={merge_csv_values(value, DLSS5_TECHNIQUES, prepend=True)}"
        result.append(line)

    additions = []
    if not seen["PreprocessorDefinitions"]:
        additions.append(f"PreprocessorDefinitions={MV_PROVIDER_DEFINE}")
    if not seen["Techniques"]:
        additions.append(f"Techniques={','.join(DLSS5_TECHNIQUES)}")
    if not seen["TechniqueSorting"]:
        additions.append(f"TechniqueSorting={','.join(DLSS5_TECHNIQUES)}")

    if additions:
        if general_index == -1:
            result = ["[General]"] + additions + [""] + result
        else:
            result[general_index + 1:general_index + 1] = additions

    try:
        preset_path.write_text("\n".join(result) + "\n", encoding="utf-8")
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
        if "DLSS5_MV_PROVIDER" in text:
            return

        backup_file(ini_path)

        if "PreprocessorDefinitions=" in text:
            text = text.replace(
                "PreprocessorDefinitions=",
                f"PreprocessorDefinitions={MV_PROVIDER_DEFINE},",
                1,
            )
        elif re.search(r"^\[GENERAL\]\s*$", text, flags=re.IGNORECASE | re.MULTILINE):
            text = re.sub(
                r"(^\[GENERAL\]\s*\n)",
                rf"\1PreprocessorDefinitions={MV_PROVIDER_DEFINE}\n",
                text,
                count=1,
                flags=re.IGNORECASE | re.MULTILINE,
            )
        else:
            text += f"\n[GENERAL]\nPreprocessorDefinitions={MV_PROVIDER_DEFINE}\n"
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
        self.warnings: list[str] = []

    def run(self) -> None:
        try:
            os.makedirs(CACHE_DIR, exist_ok=True)
            self.progress.emit(10, "Detecting hardware and Wine prefix...")

            # 1. Locate Wine Prefix and configure
            prefix = self.wine_prefix or find_wine_prefix(str(self.game_exe), self.is_steam)
            if prefix:
                self.progress.emit(20, f"Configuring Wine prefix ({prefix})...")
                ok, msg = setup_prefix_system32_nvngx(prefix)
                if not ok:
                    self.warnings.append(msg)
            else:
                self.warnings.append(
                    "Wine prefix not found: nvngx.dll was not copied to system32."
                )

            # 2. Configure Heroic if applicable
            heroic_cfg, cfg_file, app_id = find_heroic_game_config(str(self.game_exe))
            if cfg_file:
                self.progress.emit(30, "Injecting environment variables into Heroic Games Launcher...")
                if not configure_heroic_game(cfg_file, app_id):
                    self.warnings.append("Failed to update the Heroic game configuration.")

            # 3. Clean conflicting files
            self.progress.emit(40, "Cleaning conflicting DLLs and files...")
            clean_conflicting_files(self.game_dir)

            # 4. Download and setup components
            if self.route == "feeder":
                self.setup_feeder_route()
            else:
                self.setup_optiscaler_route()

            self.progress.emit(90, "Writing performance settings...")
            cfg_content = generate_dlss5_feed_cfg(self.preset)
            (self.game_dir / "dlss5-feed.cfg").write_text(cfg_content, encoding="utf-8")

            update_reshade_preset_order(self.game_dir)
            update_reshade_ini_mv(self.game_dir)

            if self.warnings:
                message = "DLSS 5 Autopilot installed with warnings:\n- " + "\n- ".join(self.warnings)
            else:
                message = "DLSS 5 Autopilot installed successfully!"

            self.progress.emit(100, "DLSS 5 Autopilot installed.")
            self.finished.emit(True, message)
        except Exception as e:
            self.finished.emit(False, f"Installation error: {e}")

    def download_url(self, url: str, dest_path: str) -> None:
        if os.path.exists(dest_path):
            return
        generic_download(url, dest_path)

    def install_dlssnr(self) -> None:
        local_dlssnr = find_local_component(DLSSNR_DLL_NAME)
        if local_dlssnr:
            shutil.copy2(local_dlssnr, str(self.game_dir / DLSSNR_DLL_NAME))
        else:
            self.warnings.append(
                f"{DLSSNR_DLL_NAME} not found. Place it in the directory pointed to by "
                f"{LOCAL_COMPONENTS_ENV} and reinstall."
            )

    def setup_feeder_route(self) -> None:
        self.progress.emit(50, "Fetching DLSS 5 Feeder and shaders...")
        feeder_zip = os.path.join(CACHE_DIR, FEEDER_ZIP_NAME)
        lumenite_zip = os.path.join(CACHE_DIR, "lumenite.zip")

        local_feeder = find_local_component(FEEDER_ZIP_NAME)
        if local_feeder and not os.path.exists(feeder_zip):
            shutil.copy2(local_feeder, feeder_zip)
        else:
            self.download_url(URL_FEEDER_ZIP, feeder_zip)

        local_lumenite = find_local_component("lumenite.zip")
        if local_lumenite and not os.path.exists(lumenite_zip):
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
        else:
            raise FileNotFoundError("DLSS5_Feed.fx not found in the Feeder package.")

        # Copy Lumenite shaders
        lumenite_src_dir = os.path.join(lumenite_extract, "LumeniteFX-mainline", "Shaders")
        if os.path.isdir(lumenite_src_dir):
            shutil.copytree(lumenite_src_dir, str(shaders_dir), dirs_exist_ok=True)
        else:
            raise FileNotFoundError("Shaders folder not found in the LumeniteFX package.")

        lumenite_tex_src = os.path.join(
            lumenite_extract, "LumeniteFX-mainline", "Textures", "lumenite_bluenoise256.png"
        )
        if os.path.isfile(lumenite_tex_src):
            shutil.copy2(lumenite_tex_src, str(textures_dir / "lumenite_bluenoise256.png"))

        # Copy dlss5-feed.addon64
        src_addon = os.path.join(feeder_extract, "dlss5-feed.addon64")
        if os.path.isfile(src_addon):
            shutil.copy2(src_addon, str(self.game_dir / "dlss5-feed.addon64"))
        else:
            raise FileNotFoundError("dlss5-feed.addon64 not found in the Feeder package.")

        # Copy renodx-dlss5.addon64 (no public URL; must come from the local components dir)
        self.progress.emit(70, "Installing RenoDX DLSS 5...")
        local_renodx = find_local_component(RENODX_ADDON_NAME)
        local_renodx_zip = find_local_component(RENODX_ZIP_NAME)

        if local_renodx:
            shutil.copy2(local_renodx, str(self.game_dir / RENODX_ADDON_NAME))
        elif local_renodx_zip:
            with ZipFile(local_renodx_zip, "r") as z:
                z.extract(RENODX_ADDON_NAME, str(self.game_dir))
        else:
            self.warnings.append(
                f"{RENODX_ADDON_NAME} not found. Place it in the directory pointed to by "
                f"{LOCAL_COMPONENTS_ENV} and reinstall."
            )

        self.progress.emit(80, "Installing DLSS Neural runtime (nvngx_dlssnr.dll)...")
        self.install_dlssnr()

    def setup_optiscaler_route(self) -> None:
        self.progress.emit(60, "Configuring OptiScaler route...")

        archive = find_local_optiscaler_archive()
        if not archive:
            raise FileNotFoundError(
                "OptiScaler package not found. The OptiScaler route does not download "
                f"automatically yet: place an OptiScaler*.zip file in the directory pointed to by "
                f"{LOCAL_COMPONENTS_ENV} or use the Feeder route."
            )

        if not archive.lower().endswith(".zip"):
            raise ValueError(
                f"Unsupported OptiScaler archive format: {os.path.basename(archive)}. "
                "Extract the .7z and repackage it as .zip."
            )

        extract_dir = os.path.join(CACHE_DIR, "optiscaler_tmp")
        os.makedirs(extract_dir, exist_ok=True)
        unzip_file(archive, extract_dir)

        copied = 0
        for root, _, files in os.walk(extract_dir):
            for name in files:
                if name.lower().endswith((".dll", ".ini", ".asi")):
                    shutil.copy2(os.path.join(root, name), str(self.game_dir / name))
                    copied += 1

        if copied == 0:
            raise FileNotFoundError("The OptiScaler package contains no installable files.")

        self.progress.emit(80, "Installing DLSS Neural runtime (nvngx_dlssnr.dll)...")
        self.install_dlssnr()
