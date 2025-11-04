from pathlib import Path
from zipfile import ZipFile
import shutil
import os
import sys

class ReshadeInstaller:
  def __init__(self):
    self.reshade_source = None    # Means reshade directory that find_reshade returns
    self.game_api = None          # Means that we know what is the API: Vulkan, d3d9c...
    self.game_bits = None         # Means that we know if its 32bit or 64bit
    self.game_source = None       # Means game directory
    self.local_source = None      # Means the local source of the reshade, that we unziped
    self.new_dll = None           # Means that we copied the dll and rename it it correctly
    self.correct_dll = None       # Means that we have the directory of the new_dll

  def install(self):
    if not all([self.correct_dll, self.game_source, self.new_dll]):
      raise ValueError("ERROR: Builder failed to configures the properties")

    print(f"Copying {self.new_dll} to {self.game_source}")
    shutil.copyfile(self.correct_dll, f'{self.game_source}/{self.new_dll}')

    print("Copying shaders and textures")
    shutil.copytree('./reshade/effects/Shaders', f'{self.game_source}/Shaders', dirs_exist_ok=True)
    shutil.copytree('./reshade/effects/Textures', f'{self.game_source}/Textures', dirs_exist_ok=True)

    print("\nInstallation completed!")

  # Debug funtion
  def __str__(self):
    return (
      f"  reshade source:   {self.reshade_source}\n"
      f"  game source:      {self.game_source}\n"
      f"  architecture:     {self.game_bits}\n"
      f"  API:              {self.game_api}\n"
      f"  local dll:        {self.local_source}\n"
      f"  final dll:        {self.correct_dll}\n"
    )

class ReshadeInstallerBuilder:
  def __init__(self):
    self.reshade = ReshadeInstaller()  


  # Return an complete installation and resets the builder
  def get_reshade_product(self):
    reshade_product = self.reshade
    self.reshade = ReshadeInstaller()
    return reshade_product

  def find_and_unzip(self, start_path, exe_pattern):
    source_path = self._find_reshade(start_path, exe_pattern)

    if not source_path:
      raise FileNotFoundError(f"ERROR: Reshade was not found into the {source_path}")

    self.reshade.reshade_source = source_path
    self._unzip_reshade(source_path)

    return self

  def clone_shaders(self):
    self._git_clone_effects()
    return self

  def set_game_architecture(self, bits: str):
    self.reshade.game_bits = bits

    dll_name = "ReShade64.dll" if bits == "64bit" else "ReShade32.dll"

    self.reshade.local_source = self._find_reshade('./reshade', dll_name)

    if not self.reshade.local_source:
      raise FileNotFoundError(f"ERROR: {dll_name} was not found in ./reshade")

    return self

  def set_game_api(self, api: str):

    if not self.reshade.local_source:
      raise Exception("ERROR: error on function queue, set_game_architecture() MUST BE before of set_game_api()")

    self.reshade.game_api = api

    match api:
      case "Vulkan":
        new_name = "dxgi.dll"
      case "d3d9c":
        new_name = "d3d9.dll"
      case "d3d10":
        new_name = "d3d10.dll"
      case _:
        raise ValueError("ERROR: This dll is not supported YET")

    self._ready_dll(self.reshade.local_source, new_name)

    self.reshade.new_dll = new_name
    self.reshade.correct_dll = self._find_reshade('./reshade', new_name)
    
    return self

  def set_game_directory(self, game_path: str):

    if not os.path.isdir(game_path):
      raise NotADirectoryError(f"ERROR: Games directory is not valid -> {game_path}")

    self.reshade.game_source = game_path
    return self

  # PRIVATE METHODS! That's why it starts with a _something
  
  def _find_reshade(self, start_path, exe_pattern):
    start = Path(start_path)
    pattern = f'{exe_pattern}'

    try: 
      matches = list(start.rglob(pattern))
    except PermissionError:
      print("ERROR: Not allowed due to permission stuff")
      return None

    if not matches:
      return None

    return str(matches[0])

  def _unzip_reshade(self, source):
    if not os.path.isdir('./reshade'): # Check if directory exists
      with ZipFile(source, 'r') as zip_object:
        zip_object.extractall("./reshade")

  def _ready_dll(self, local, new_name):
    shutil.copyfile(local, f'./reshade/{new_name}')
    return new_name

  def _git_clone_effects(self):
    effects_dir = './reshade/effects'

    # Checks if directory exists
    os.makedirs(effects_dir, exist_ok=True)

    # Check if we already clone it
    if len(os.listdir(effects_dir)) == 0:
      os.system("git clone https://github.com/crosire/reshade-shaders.git ./reshade/effects")
    else:    
      print("We already have shaders downloaded.")

if __name__ == "__main__":
  builder = ReshadeInstallerBuilder()

  RESHADE_SEARCH_PATH = '/home'
  RESHADE_PATTERN = 'ReShade_Setup*.exe'

  user_game_dir = str(input("Qual o diretório do seu jogo: ")).strip()
  user_game_bits = "64bit"
  user_game_api = "Vulkan"

  try:
      builder.find_and_unzip(RESHADE_SEARCH_PATH, RESHADE_PATTERN)
      builder.clone_shaders()
      
      builder.set_game_architecture(user_game_bits)
      builder.set_game_api(user_game_api)
      builder.set_game_directory(user_game_dir)
  
      
      installer = builder.get_reshade_product()
      print(installer) 
      
      installer.install()

  except Exception as e:
      print(f"\n--- ERROR ---", file=sys.stderr)
      print(f"{e}", file=sys.stderr)
      sys.exit(1)