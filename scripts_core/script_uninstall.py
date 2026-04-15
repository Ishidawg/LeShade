from scripts_core.script_manager import read_boolean_flags, read_manager_content
from scripts_core.script_vulkan import InstallVulkan
from PySide6.QtCore import QObject, Signal
import shutil
import glob
import os


class UninstallWorker(QObject):
    finished: Signal = Signal(bool)
    error: Signal = Signal(str)

    def __init__(self, current_row: int, game_path: str):
        super().__init__()

        self.current_row: int = current_row
        self.game_path: str = game_path

    def run(self) -> None:
        try:
            shaders_dir: str = os.path.join(self.game_path, "reshade-shaders")

            # I dont remember what I did to this string be a bool
            have_hlsl_compiler: str = read_boolean_flags(
                self.current_row,
                "hlsl_compiler"
            )
            is_vulkan: str = read_boolean_flags(self.current_row, "vulkan")

            remove_files_complete: list[str] = []

            if not is_vulkan:
                game_api_dll: str = read_manager_content("api_dll")[0]
                remove_files_complete.append(game_api_dll)

            if not have_hlsl_compiler:
                remove_files_complete.append("d3dcompiler_47.dll")

            print(remove_files_complete)

            remove_files_pattern: list[str] = [
                "ReShade*.*",
                "reshade*.*",
                "renodx*.*"
            ]

            if os.path.exists(self.game_path):
                if os.path.exists(shaders_dir):
                    shutil.rmtree(shaders_dir)

                file_path: str = ""
                for file in remove_files_complete:
                    file_path = os.path.join(self.game_path, file)
                    if os.path.exists(file_path):
                        os.remove(file_path)

                for pattern in remove_files_pattern:
                    file_match: str = os.path.join(self.game_path, pattern)
                    glob_result: list[str] = glob.glob(file_match)

                    for file_found in glob_result:
                        if os.path.exists(file_found):
                            os.remove(file_found)

                if is_vulkan:
                    reshade_dir: str = read_manager_content(
                        "reshade_prx_dir")[self.current_row]
                    system32_dir: str = read_manager_content(
                        "system32_prx_dir")[self.current_row]
                    vulkanrt_dir: str = read_manager_content(
                        "vulkanrt_prx_dir")[self.current_row]

                    if reshade_dir and os.path.exists(reshade_dir):
                        shutil.rmtree(reshade_dir)

                    if vulkanrt_dir and os.path.exists(vulkanrt_dir):
                        shutil.rmtree(vulkanrt_dir)

                    if system32_dir and os.path.exists(system32_dir):
                        icu_file_path: str = ""

                        icu_files: list[str] = ["derb.exe", "genbrk.exe", "genccode.exe", "genu.exe",
                                                "gencmn.exe", "gencnval.exe", "gendict.exe", "gennorm2.exe",
                                                "genrb.exe", "gensprep.exe", "icudt.dll", "icudt78.dll",
                                                "icuexportdata.exe", "icuin.dll", "icuin78.dll", "icuinfo.exe",
                                                "icuio.dll", "icuio78.dll", "icupkg.exe", "icutest.exe",
                                                "icutest78.exe", "icutu.dll", "icutu78.dll", "icuuc.dll",
                                                "icuuc78.dll", "makeconv.exe", "pkgdata.exe", "testplug.dll",
                                                "uconv.exe"]

                        for file in icu_files:
                            icu_file_path = os.path.join(system32_dir, file)

                            if os.path.isfile(icu_file_path):
                                os.remove(icu_file_path)

                    is_steam: bool = "steamapps" in self.game_path

                    InstallVulkan(self.game_path, is_steam, True)

            self.finished.emit(True)
        except Exception as e:
            self.error.emit(e)
            self.finished.emit(False)
            raise IndexError(f"Error while deleting files: {e}")
