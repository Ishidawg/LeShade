import os
import glob
import json
import re
import struct
from pathlib import Path


def get_pe_imports(path: str) -> list[str]:
    """
    Extracts imported DLL names from a PE (Windows executable) file
    without any external dependencies.
    """
    if not os.path.isfile(path):
        return []

    try:
        with open(path, "rb") as f:
            dos_header = f.read(64)
            if len(dos_header) < 64 or dos_header[:2] != b"MZ":
                return []

            e_lfanew = struct.unpack_from("<I", dos_header, 60)[0]
            f.seek(e_lfanew)
            if f.read(4) != b"PE\x00\x00":
                return []

            file_header = f.read(20)
            machine, num_sections, _, _, _, opt_size, _ = struct.unpack("<HHIIIHH", file_header)
            opt_header = f.read(opt_size)
            if len(opt_header) < 2:
                return []

            magic = struct.unpack_from("<H", opt_header, 0)[0]
            is_64 = (magic == 0x20b)
            data_dir_offset = 112 if is_64 else 96

            if len(opt_header) < data_dir_offset + 16:
                return []

            import_rva, import_size = struct.unpack_from("<II", opt_header, data_dir_offset + 8)
            if import_rva == 0:
                return []

            sections = []
            for _ in range(num_sections):
                sec = f.read(40)
                if len(sec) < 40:
                    break
                name = sec[:8].rstrip(b"\x00").decode("latin-1", errors="ignore")
                v_size, v_addr, raw_size, raw_ptr = struct.unpack_from("<IIII", sec, 8)
                sections.append((name, v_addr, v_size, raw_ptr, raw_size))

            def rva_to_offset(rva):
                for _, v_addr, v_size, raw_ptr, raw_size in sections:
                    if v_addr <= rva < v_addr + max(v_size, raw_size):
                        return raw_ptr + (rva - v_addr)
                return None

            import_offset = rva_to_offset(import_rva)
            if not import_offset:
                return []

            f.seek(import_offset)
            dlls = []
            while True:
                desc = f.read(20)
                if len(desc) < 20 or desc == b"\x00" * 20:
                    break
                name_rva = struct.unpack_from("<I", desc, 12)[0]
                if name_rva == 0:
                    break
                cur = f.tell()
                name_offset = rva_to_offset(name_rva)
                if name_offset:
                    f.seek(name_offset)
                    chars = []
                    while True:
                        b = f.read(1)
                        if not b or b == b"\x00":
                            break
                        chars.append(b)
                    dll_name = b"".join(chars).decode("latin-1", errors="ignore").lower().strip()
                    if dll_name and dll_name not in dlls:
                        dlls.append(dll_name)
                f.seek(cur)

            return dlls
    except Exception:
        return []


def detect_graphics_api(path: str) -> str:
    """
    Analyzes imported DLLs and returns the recommended ReShade API:
    'D3D 12', 'D3D 11', 'D3D 10', 'D3D 9', 'D3D 8', 'Vulkan', or 'OpenGL'.
    """
    imports = get_pe_imports(path)
    imports_lower = [i.lower() for i in imports]

    # Prioritize based on modern APIs:
    if "vulkan-1.dll" in imports_lower:
        return "Vulkan"

    if "d3d12.dll" in imports_lower:
        return "D3D 12"

    if "d3d11.dll" in imports_lower or "dxgi.dll" in imports_lower:
        return "D3D 11"

    if "d3d10.dll" in imports_lower or "d3d10_1.dll" in imports_lower:
        return "D3D 10"

    if "d3d9.dll" in imports_lower:
        return "D3D 9"

    if "d3d8.dll" in imports_lower:
        return "D3D 8"

    if "opengl32.dll" in imports_lower:
        return "OpenGL"

    # Many engines load the graphics DLL at runtime (LoadLibrary), so the import
    # table tells nothing. Return empty so the UI does not claim a detection.
    return ""


def get_extra_search_paths() -> list[str]:
    """
    Returns optional custom directories specified by the user via
    the LESHADE_EXTRA_PATHS environment variable (colon-separated).
    """
    paths = []
    extra_env = os.environ.get("LESHADE_EXTRA_PATHS", "")
    if extra_env:
        for p in extra_env.split(":"):
            p = p.strip()
            if p and os.path.isdir(p):
                paths.append(p)
    return paths


IGNORED_EXE_PREFIXES = (
    "uninstall", "unins", "setup", "dxsetup", "vc_redist", "vcredist",
    "crash", "unitycrashhandler", "ue4prereqsetup", "ueprereqsetup",
    "easyanticheat", "eac", "dotnet", "directx", "launcher_", "redist",
)
IGNORED_EXE_DIRS = {
    "engine", "redist", "_commonredist", "commonredist", "prerequisites",
    "directx", "vcredist", "dotnet", "support", "tools", "easyanticheat", "installers",
}


def pick_game_executable(game_dir: str) -> str | None:
    """
    Returns the most likely main executable of a game directory: skips helper
    and redistributable binaries, then prefers the shallowest remaining .exe.
    """
    candidates: list[tuple[int, int, str]] = []

    for root, dirs, files in os.walk(game_dir):
        dirs[:] = [d for d in dirs if d.lower() not in IGNORED_EXE_DIRS]
        depth = os.path.relpath(root, game_dir).count(os.sep)
        for file in files:
            lower = file.lower()
            if not lower.endswith(".exe") or lower.startswith(IGNORED_EXE_PREFIXES):
                continue
            # Unreal games: "Game.exe" at the root is a bootstrap, the real
            # binary is "*-Shipping.exe" a few levels down.
            priority = 0 if "shipping" in lower else 1
            candidates.append((priority, depth, os.path.join(root, file)))

    if not candidates:
        return None

    candidates.sort()
    return candidates[0][2]


def scan_heroic_games() -> list[dict]:
    """
    Scans Heroic Games Launcher install configs across host, flatpak, and custom paths.
    """
    games = []
    seen_exes = set()

    candidate_bases = [
        os.path.expanduser("~/.config/heroic"),
        os.path.expanduser("~/.var/app/com.heroicgameslauncher.hgl/config/heroic"),
    ]

    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config:
        candidate_bases.append(os.path.join(xdg_config, "heroic"))

    for extra in get_extra_search_paths():
        candidate_bases.append(os.path.join(extra, ".config", "heroic"))
        candidate_bases.append(extra)

    for base in candidate_bases:
        cache_dir = os.path.join(base, "store_cache")
        if not os.path.exists(cache_dir):
            continue

        for info_file in glob.glob(os.path.join(cache_dir, "*_install_info.json")):
            try:
                with open(info_file, "r", encoding="utf-8", errors="ignore") as f:
                    data = json.load(f)

                for app_id, info in data.items():
                    if app_id == "__timestamp" or not isinstance(info, dict):
                        continue

                    title = info.get("game", {}).get("title") or app_id
                    install_path = info.get("install", {}).get("install_path")
                    exe = info.get("manifest", {}).get("launch_exe")

                    if install_path and exe:
                        exe_path = os.path.join(install_path, exe)
                        if os.path.exists(exe_path) and exe_path not in seen_exes:
                            seen_exes.add(exe_path)
                            games.append({
                                "title": title,
                                "exe": exe_path,
                                "source": "Heroic"
                            })
            except Exception:
                continue

    return games


def scan_steam_games() -> list[dict]:
    """
    Scans Steam libraries and manifests across host, flatpak, and custom paths.
    """
    games = []
    seen_exes = set()

    candidate_bases = [
        os.path.expanduser("~/.local/share/Steam"),
        os.path.expanduser("~/.steam/steam"),
        os.path.expanduser("~/.steam/root"),
        os.path.expanduser("~/.var/app/com.valvesoftware.Steam/data/Steam"),
    ]

    xdg_data = os.environ.get("XDG_DATA_HOME")
    if xdg_data:
        candidate_bases.append(os.path.join(xdg_data, "Steam"))

    for extra in get_extra_search_paths():
        candidate_bases.append(os.path.join(extra, ".local", "share", "Steam"))
        candidate_bases.append(os.path.join(extra, ".steam", "steam"))
        candidate_bases.append(extra)

    for base in candidate_bases:
        vdf = os.path.join(base, "config", "libraryfolders.vdf")
        if not os.path.exists(vdf):
            vdf = os.path.join(base, "steamapps", "libraryfolders.vdf")

        if os.path.exists(vdf):
            try:
                with open(vdf, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                for match in re.finditer(r"\"path\"\s+\"([^\"]+)\"", content):
                    lib_path = match.group(1).replace("\\\\", "/")
                    apps_dir = os.path.join(lib_path, "steamapps")

                    if os.path.exists(apps_dir):
                        for acf in glob.glob(os.path.join(apps_dir, "appmanifest_*.acf")):
                            try:
                                with open(acf, "r", encoding="utf-8", errors="ignore") as af:
                                    acontent = af.read()

                                name_match = re.search(r"\"name\"\s+\"([^\"]+)\"", acontent)
                                dir_match = re.search(r"\"installdir\"\s+\"([^\"]+)\"", acontent)

                                if name_match and dir_match:
                                    g_name = name_match.group(1)
                                    g_dir = os.path.join(apps_dir, "common", dir_match.group(1))

                                    if os.path.exists(g_dir):
                                        exe_path = pick_game_executable(g_dir)
                                        if exe_path and exe_path not in seen_exes:
                                            seen_exes.add(exe_path)
                                            games.append({
                                                "title": g_name,
                                                "exe": exe_path,
                                                "source": "Steam"
                                            })
                            except Exception:
                                continue
            except Exception:
                continue

    return games


def scan_all_games() -> list[dict]:
    """
    Returns an aggregated, deduplicated, sorted list of games discovered on the system.
    """
    all_games = scan_heroic_games() + scan_steam_games()
    all_games.sort(key=lambda x: x["title"].lower())
    return all_games
