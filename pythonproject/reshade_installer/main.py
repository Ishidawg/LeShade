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

  while True:
    game_bits = int((input("Your game is 32bit or 64bit? [1] - [2]: ")))

    if game_bits <= 2:
      break

  if game_bits == 1:
    local_source = find_reshade('./reshade', 'ReShade32.dll')
  else:
    local_source = find_reshade('./reshade', 'ReShade64.dll')
  
  print("local_source: " + local_source)

  while True:
    game_api = int(input("Is your game api Vulkan or openGL? [1] - [2]: "))

    if game_api <= 2:
      break

  if game_api == 1:
    print("Cooking a Vulkan dll...")
    new_dll = ready_dll(local_source, 'dxgi.dll',)
    correct_dll = find_reshade('./reshade', 'dxgi.dll')
  else:
    print("Cooking a openGL dll...")
    new_dll = ready_dll(local_source, 'opengl.dll')
    correct_dll = find_reshade('./reshade', 'opengl.dll')

  print(correct_dll)

  game_source = str(input("What is your game directory: "))
  print(game_source)

  # copy to games folders
  shutil.copyfile(correct_dll, f'{game_source}/{new_dll}')

def ready_dll(local, new_name):
  os.system(f'cp {local} reshade/{new_name}')
  return new_name

print("Path:", find_reshade('/home', 'ReShade_Setup*.exe'))
unzip_reshade(find_reshade('/home', 'ReShade_Setup*.exe'))
user_input()