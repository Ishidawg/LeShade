from utils.utils import EXTRACT_PATH, download, get_clean_env, get_game_directory_name, get_steam_appid, get_gamebase_directory, get_wine_command, unzip_file
from pathlib import Path
import subprocess
import textwrap
import shutil
import glob
import os

VULKAN_COMPONENTS_URL: str = "https://sdk.lunarg.com/sdk/download/1.4.341.0/windows/VulkanRT-X64-1.4.341.0-Components.zip"
ICU_URL: str = "https://raw.githubusercontent.com/Ishidawg/LeShade/refs/heads/main/icu_dll/icu_dll.zip"

# Distination directories for download stuff
VULKAN_COMPONENTS_PATH: str = os.path.join(
    EXTRACT_PATH, "vulkan_components.zip")
VULKAN_COMPONENTS_DIR: str = os.path.join(EXTRACT_PATH, "VULKAN_COMPONENTS")
ICU_PATH: str = os.path.join(EXTRACT_PATH, "icu.zip")
ICU_DIR: str = os.path.join(EXTRACT_PATH, "ICU")

ADD_REG_PATH: str = os.path.join(EXTRACT_PATH, "leshade.reg")
REMOVE_REG_PATH: str = os.path.join(EXTRACT_PATH, "remove.reg")


class InstallVulkan():
    def __init__(self, game_dir: str, is_steam: bool, remove: bool = False) -> None:
        super().__init__()
        self.is_steam: bool = is_steam

        self.executable_path: Path = Path(game_dir)
        self.gamebase_dir: str = get_gamebase_directory(
            self.executable_path, self.is_steam)
        self.app_id: str = ""
        self.drive_c_path: str = ""

        if is_steam:
            self.game_name: str = get_game_directory_name(self.executable_path)
            self.app_id = get_steam_appid(
                self.gamebase_dir, self.game_name)

            self.drive_c_path = os.path.join(
                self.gamebase_dir,
                "compatdata",
                self.app_id,
                "pfx",
                "drive_c"
            )
        else:
            self.drive_c_path = self.gamebase_dir
            self.app_id = ""

        self.system32_prefix: str = os.path.join(
            self.drive_c_path,
            "windows",
            "system32"
        )

        self.reshade_prefix: str = os.path.join(
            self.drive_c_path,
            "ProgramData",
            "ReShade"
        )

        if remove:
            os.makedirs(EXTRACT_PATH, exist_ok=True)
            self.create_remove_leshade_reg(REMOVE_REG_PATH, remove=True)
            self.add_remove_registry_keys(REMOVE_REG_PATH, remove=True)
            return

    def run(self) -> None:
        self.run_ICU()
        self.run_vulkanRT()
        self.run_reshade_actions(self.reshade_prefix, self.executable_path)

    def download_ICU(self) -> None:
        download(url=ICU_URL, file_name=ICU_PATH)

    def extract_icu(self) -> None:
        os.makedirs(ICU_DIR, exist_ok=True)
        unzip_file(ICU_PATH, ICU_DIR)

    def download_vulkan_components(self) -> None:
        download(url=VULKAN_COMPONENTS_URL, file_name=VULKAN_COMPONENTS_PATH)

    def extract_vulkan_components(self) -> None:
        os.makedirs(VULKAN_COMPONENTS_DIR, exist_ok=True)
        unzip_file(VULKAN_COMPONENTS_PATH, VULKAN_COMPONENTS_DIR)

    def move_icu_files_to_sys32(self, system32_path: str) -> None:
        try:
            shutil.copytree(ICU_DIR, system32_path, dirs_exist_ok=True)
        except Exception as e:
            raise IOError(f"Failed to move ICU files to system32: {e}")

    def move_vulkan_dll_to_sys32(self, system32_path: str) -> None:
        try:
            vulkan_dll: Path | None = self.get_vulkan_dll(
                Path(VULKAN_COMPONENTS_DIR))

            if vulkan_dll is None:
                raise FileNotFoundError(
                    "vulkan-1.dll was not found in the given path")

            vulkan_dll_destination: str = os.path.join(
                system32_path, "vulkan-1.dll")

            shutil.copy(vulkan_dll, vulkan_dll_destination)
            print("copiou!!")
        except Exception as e:
            raise IOError(f"Failed to move vulkan-1.dll to system32: {e}")

    def get_vulkan_dll(self, base_dir: Path) -> Path | None:
        for vulkan_dll in base_dir.rglob("vulkan-1.dll"):

            if vulkan_dll.parent.name == "x64":
                return vulkan_dll

        return None

    def run_ICU(self) -> None:
        self.download_ICU()
        self.extract_icu()
        self.move_icu_files_to_sys32(self.system32_prefix)

    def run_vulkanRT(self) -> None:
        self.download_vulkan_components()
        self.extract_vulkan_components()
        self.move_vulkan_dll_to_sys32(self.system32_prefix)

    def move_reshade_files(self, reshade_prefix: str) -> None:
        os.makedirs(reshade_prefix, exist_ok=True)

        reshade_files: list[str] = glob.glob(
            os.path.join(EXTRACT_PATH, "ReShade*"), recursive=True)

        for file in reshade_files:
            shutil.copy(file, reshade_prefix)

    def create_reshade_apps(self, reshade_prefix: str, game_executable_path: Path) -> None:
        reshade_apps: str = os.path.join(reshade_prefix, "ReShadeApps.ini")
        fix_game_exe_path: str = str(game_executable_path).replace("/", "\\")

        app_data: str = f"Apps=Z:{fix_game_exe_path}"

        if not os.path.exists(reshade_apps):
            try:
                with open(reshade_apps, "w") as file:
                    file.write(app_data)
            except FileExistsError as e:
                print(e)

    def create_remove_leshade_reg(self, reg_path: str, remove: bool = False) -> None:
        registry_add_content: str = textwrap.dedent(r"""
            Windows Registry Editor Version 5.00

            [HKEY_CURRENT_USER\Software\Khronos\Vulkan\ImplicitLayers]
            "C:\\ProgramData\\ReShade\\ReShade64.json"=dword:00000000

            [HKEY_LOCAL_MACHINE\Software\Khronos\Vulkan\ImplicitLayers]
            "C:\\ProgramData\\ReShade\\ReShade64.json"=dword:00000000

            [HKEY_LOCAL_MACHINE\Software\Wow6432Node\Khronos\Vulkan\ImplicitLayers]
            "C:\\ProgramData\\ReShade\\ReShade32.json"=dword:00000000

            [HKEY_CURRENT_USER\Software\Wine\DllOverrides]
            "vulkan-1"="native"
        """).strip()

        registry_remove_content: str = textwrap.dedent(r"""
            Windows Registry Editor Version 5.00

            [-HKEY_CURRENT_USER\Software\Khronos\Vulkan\ImplicitLayers]
            [-HKEY_LOCAL_MACHINE\Software\Khronos\Vulkan\ImplicitLayers]
            [-HKEY_LOCAL_MACHINE\Software\Wow6432Node\Khronos\Vulkan\ImplicitLayers]
            [HKEY_CURRENT_USER\Software\Wine\DllOverrides]
            "vulkan-1"=-
        """).strip()

        with open(reg_path, "w", encoding="utf-8") as file:
            if remove:
                file.write(registry_remove_content)
            else:
                file.write(registry_add_content)

    def add_remove_registry_keys(self, registry_path: str, remove: bool = False) -> None:
        custom_env: dict[str, str] = get_clean_env()
        custom_env["WINEPREFIX"] = os.path.dirname(self.drive_c_path)
        custom_env["WINEDLLOVERRIDES"] = "mscoree,mshtml="

        wine_command: list[str] = get_wine_command()

        # If this work I make this a little better...

        if "flatpak-spawn" in wine_command:
            wine_command.insert(
                2, f"--env=WINEPREFIX={os.path.dirname(self.drive_c_path)}")
            wine_command.insert(3, "--env=WINEDLLOVERRIDES=mscoree,mshtml=")

        if "org.winehq.Wine" in wine_command and "run" in wine_command:
            index: int = wine_command.index("run")
            wine_command.insert(
                index + 1, f"--env=WINEPREFIX={os.path.dirname(self.drive_c_path)}")
            wine_command.insert(
                index + 2, "--env=WINEDLLOVERRIDES=mscoree,mshtml=")

        full_command = wine_command + ["regedit", "/S", registry_path]

        base_prefix: list[str] = wine_command[:-1]

        if "org.winehq.Wine" in wine_command:
            sync_command: list[str] = base_prefix + \
                ["--command=wineserver", "org.winehq.Wine", "-w"]
        else:
            sync_command: list[str] = base_prefix + ["wineserver", "-w"]

        try:
            subprocess.run(full_command,
                           check=True,
                           capture_output=True,
                           text=True,
                           env=custom_env
                           )

            subprocess.run(sync_command,
                           check=True,
                           capture_output=True,
                           text=True,
                           env=custom_env
                           )
            print("regedit runs!!")
        except subprocess.CalledProcessError as e:
            if remove:
                raise Exception(f"Failed to remove keys: {e.stderr}")
            else:
                raise Exception(f"Failed to write on registry: {e.stderr}")

    def run_reshade_actions(self, reshade_prefix: str, game_executable: Path) -> None:
        self.move_reshade_files(reshade_prefix)
        self.create_reshade_apps(reshade_prefix, game_executable)
        self.create_remove_leshade_reg(ADD_REG_PATH)
        self.add_remove_registry_keys(ADD_REG_PATH)
