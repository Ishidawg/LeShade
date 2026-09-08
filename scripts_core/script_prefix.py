import glob
import json
import os
import shutil
from pathlib import Path

from scripts_core.script_scanner import get_extra_search_paths
from utils.utils import get_gamebase_directory, get_steam_appid, get_game_directory_name


def find_heroic_game_config(exe_path: str) -> tuple[dict | None, str | None, str | None]:
    """
    Locates the Heroic GamesConfig JSON file corresponding to the given executable.
    Returns (config_dict, config_file_path, app_id) or (None, None, None).
    """
    if not exe_path or not os.path.exists(exe_path):
        return None, None, None

    exe_real = os.path.realpath(exe_path)
    game_dir_real = os.path.realpath(os.path.dirname(exe_path))

    candidate_bases = [
        os.path.expanduser("~/.config/heroic"),
        os.path.expanduser("~/.var/app/com.heroicgameslauncher.hgl/config/heroic"),
        "/mnt/data/distrobox/gaming/.config/heroic",
    ]

    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config:
        candidate_bases.append(os.path.join(xdg_config, "heroic"))

    for extra in get_extra_search_paths():
        candidate_bases.extend([os.path.join(extra, ".config", "heroic"), extra])

    for base in candidate_bases:
        cache_dir = os.path.join(base, "store_cache")
        games_cfg_dir = os.path.join(base, "GamesConfig")
        if not os.path.exists(cache_dir) or not os.path.exists(games_cfg_dir):
            continue

        for info_file in glob.glob(os.path.join(cache_dir, "*_install_info.json")):
            try:
                with open(info_file, "r", encoding="utf-8", errors="ignore") as f:
                    data = json.load(f)

                for app_id, info in data.items():
                    if app_id == "__timestamp" or not isinstance(info, dict):
                        continue

                    install_path = info.get("install", {}).get("install_path", "")
                    if not install_path:
                        continue

                    if os.path.realpath(install_path) == game_dir_real:
                        cfg_file = os.path.join(games_cfg_dir, f"{app_id}.json")
                        if os.path.exists(cfg_file):
                            with open(cfg_file, "r", encoding="utf-8") as cf:
                                cfg_data = json.load(cf)
                            return cfg_data, cfg_file, app_id
            except Exception:
                continue

    return None, None, None


def configure_heroic_game(json_path: str, app_id: str | None = None) -> bool:
    """
    Updates a Heroic GamesConfig JSON file to inject:
      - PROTON_ENABLE_NVAPI=1
      - PROTON_ENABLE_NGX_UPDATER=0
      - WINEDLLOVERRIDES="dxgi=n,b"
    Preserves all existing user settings and options.
    """
    if not json_path or not os.path.exists(json_path):
        return False

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        target_key = app_id
        if not target_key or target_key not in data:
            for k, v in data.items():
                if k not in ("version", "explicit") and isinstance(v, dict):
                    target_key = k
                    break

        if not target_key or target_key not in data:
            return False

        game_cfg = data[target_key]
        env_options = game_cfg.get("enviromentOptions", [])

        needed_vars = {
            "PROTON_ENABLE_NVAPI": "1",
            "PROTON_ENABLE_NGX_UPDATER": "0",
            "WINEDLLOVERRIDES": "dxgi=n,b",
        }

        existing_keys = {item.get("key"): idx for idx, item in enumerate(env_options) if isinstance(item, dict)}

        for k, v in needed_vars.items():
            if k in existing_keys:
                idx = existing_keys[k]
                curr_val = env_options[idx].get("value", "")
                if k == "WINEDLLOVERRIDES" and "dxgi" not in curr_val:
                    env_options[idx]["value"] = f"{curr_val};dxgi=n,b" if curr_val else "dxgi=n,b"
                else:
                    env_options[idx]["value"] = v
            else:
                env_options.append({"key": k, "value": v})

        game_cfg["enviromentOptions"] = env_options

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return True
    except Exception as e:
        print(f"Error configuring Heroic game JSON: {e}")
        return False


def find_wine_prefix(exe_path: str, is_steam: bool = False) -> str | None:
    """
    Attempts to discover the Wine or Proton prefix for the given executable.
    """
    if not exe_path or not os.path.exists(exe_path):
        return None

    exe = Path(exe_path).resolve()

    # 1. Check Heroic config
    heroic_cfg, _, app_id = find_heroic_game_config(str(exe))
    if heroic_cfg and app_id and app_id in heroic_cfg:
        prefix = heroic_cfg[app_id].get("winePrefix")
        if prefix and os.path.isdir(prefix):
            return prefix

    # 2. Check Steam compatdata
    if is_steam or "steamapps" in str(exe):
        try:
            gamebase_dir = get_gamebase_directory(exe, is_steam=True)
            game_name = get_game_directory_name(exe)
            app_id_steam = get_steam_appid(gamebase_dir, game_name)
            pfx = os.path.join(gamebase_dir, "compatdata", app_id_steam, "pfx")
            if os.path.isdir(pfx):
                return pfx
        except Exception:
            pass

    # 3. Check for drive_c in ancestors
    for parent in exe.parents:
        if parent.name == "drive_c" and parent.parent:
            return str(parent.parent)

    return None


def find_host_nvidia_wine_dlls() -> tuple[str | None, str | None]:
    """
    Finds the host NVIDIA Wine integration DLLs (nvngx.dll and _nvngx.dll).
    """
    search_dirs = [
        "/usr/lib/x86_64-linux-gnu/nvidia/wine",
        "/usr/lib/nvidia/wine",
        "/usr/lib64/nvidia/wine",
    ]

    for d in search_dirs:
        nvngx = os.path.join(d, "nvngx.dll")
        _nvngx = os.path.join(d, "_nvngx.dll")
        if os.path.isfile(nvngx) and os.path.isfile(_nvngx):
            return nvngx, _nvngx

    return None, None


def setup_prefix_system32_nvngx(prefix_path: str) -> tuple[bool, str]:
    """
    Copies host nvngx.dll and _nvngx.dll to the prefix's windows/system32 directory.
    """
    if not prefix_path or not os.path.isdir(prefix_path):
        return False, f"Invalid prefix directory: {prefix_path}"

    sys32 = os.path.join(prefix_path, "drive_c", "windows", "system32")
    if not os.path.isdir(sys32):
        return False, f"system32 directory not found inside prefix: {sys32}"

    host_nvngx, host__nvngx = find_host_nvidia_wine_dlls()
    if not host_nvngx or not host__nvngx:
        return False, "Host NVIDIA wine DLLs (nvngx.dll, _nvngx.dll) were not found in /usr/lib"

    try:
        shutil.copy2(host_nvngx, os.path.join(sys32, "nvngx.dll"))
        shutil.copy2(host__nvngx, os.path.join(sys32, "_nvngx.dll"))
        return True, f"NVIDIA Wine DLLs successfully installed in {sys32}"
    except Exception as e:
        return False, f"Failed to copy DLLs to system32: {e}"


def get_steam_launch_options() -> str:
    """
    Returns the ready-to-copy launch options string for Steam.
    """
    return 'WINEDLLOVERRIDES="dxgi=n,b" PROTON_ENABLE_NVAPI=1 PROTON_ENABLE_NGX_UPDATER=0 %command%'
