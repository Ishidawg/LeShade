from pathlib import Path
from zipfile import ZipFile
import shutil
import os

def find_reshade(start_path, exe_pattern):
  start = Path(start_path)
  pattern = f'{exe_pattern}'
  matches = list(start.rglob(pattern))

  if not matches:
      return "Reshade was not found"
  return str(matches[0])

def unzip_reshade(source):
  with ZipFile(source, 'r') as zip_object:
    zip_object.extractall("./reshade")

def user_input():
  # Unzip the reshaded that was downloaded
  unzip_reshade(find_reshade('/home', 'ReShade_Setup*.exe'))

  # Clone default shaders to copy it later on to the games folder
  git_clone_effects()

  while True:
    game_bits = abs(int((input("Your game is 32bit or 64bit? [1] - [2]: "))))

    if game_bits <= 2:
      break

  if game_bits == 1:
    local_source = find_reshade('./reshade', 'ReShade32.dll')
  else:
    local_source = find_reshade('./reshade', 'ReShade64.dll')

  while True:
    print("What is your game API?")
    print("[1] - Vulkan")
    print("[2] - OpenGL")
    print("[3] - d3d9")
    print("[4] - d3d10")

    game_api = abs(int(input("Choice: ")))

    if game_api <= 4:
      break

  # Match "switch case"
  match game_api:
    case 1:
      new_dll = ready_dll(local_source, 'dxgi.dll',)
      correct_dll = find_reshade('./reshade', 'dxgi.dll')
    case 2:
      new_dll = ready_dll(local_source, 'opengl.dll')
      correct_dll = find_reshade('./reshade', 'opengl.dll')
    case 3:
      new_dll = ready_dll(local_source, 'd3d9.dll',)
      correct_dll = find_reshade('./reshade', 'd3d9.dll')
    case 4:
      new_dll = ready_dll(local_source, 'd3d10.dll',)
      correct_dll = find_reshade('./reshade', 'd3d10.dll')

  # Old if statement
  # if game_api == 1:
  #   new_dll = ready_dll(local_source, 'dxgi.dll',)
  #   correct_dll = find_reshade('./reshade', 'dxgi.dll')
  # else:
  #   new_dll = ready_dll(local_source, 'opengl.dll')
  #   correct_dll = find_reshade('./reshade', 'opengl.dll')

  game_source = str(input("What is your game directory: "))

  # copy reshade files to games folder
  copy_reshade_to_games_folder(correct_dll, game_source, new_dll)

def ready_dll(local, new_name):
  os.system(f'cp {local} reshade/{new_name}')
  return new_name

def copy_reshade_to_games_folder(correct_dll, game_source, new_dll):
  shutil.copyfile(correct_dll, f'{game_source}/{new_dll}')

  # if len(os.listdir('./reshade/effects')) == 0:
  #   os.system("git clone https://github.com/crosire/reshade-shaders.git ./reshade/effects")
  # else:    
  #   print("We already have shaders downloaded.")

  shutil.copytree('./reshade/effects/Shaders', f'{game_source}/Shaders', dirs_exist_ok=True)
  shutil.copytree('./reshade/effects/Textures', f'{game_source}/Textures', dirs_exist_ok=True)

def git_clone_effects():
  if len(os.listdir('./reshade/effects')) == 0:
    os.system("git clone https://github.com/crosire/reshade-shaders.git ./reshade/effects")
  else:    
    print("We already have shaders downloaded.")

user_input()