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

    # Fallback to D3D 11 as the safest modern default
    return "D3D 11"


def scan_heroic_games() -> list[dict]:
    """
    Scans Heroic Games Launcher install configs across host, flatpak, and distrobox paths.
    """
    games = []
    seen_exes = set()

    candidate_bases = [
        os.path.expanduser("~/.config/heroic"),
        os.path.expanduser("~/.var/app/com.heroicgameslauncher.hgl/config/heroic"),
    ] + glob.glob("/mnt/data/distrobox/*/.config/heroic")

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
    Scans Steam libraries and manifests across host, flatpak, and distrobox paths.
    """
    games = []
    seen_exes = set()

    candidate_bases = [
        os.path.expanduser("~/.local/share/Steam"),
        os.path.expanduser("~/.steam/steam"),
        os.path.expanduser("~/.var/app/com.valvesoftware.Steam/data/Steam"),
    ] + glob.glob("/mnt/data/distrobox/*/.local/share/Steam")

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
                                        for root, _, files in os.walk(g_dir):
                                            for file in files:
                                                if file.lower().endswith(".exe") and not file.lower().startswith("uninstall"):
                                                    exe_path = os.path.join(root, file)
                                                    if exe_path not in seen_exes:
                                                        seen_exes.add(exe_path)
                                                        games.append({
                                                            "title": g_name,
                                                            "exe": exe_path,
                                                            "source": "Steam"
                                                        })
                                                    break
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
