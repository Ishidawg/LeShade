from pathlib import Path
import os
from zipfile import ZipFile
import shutil
import sys
import struct

# CORE
RESHADE_URL = "https://reshade.me/downloads/ReShade_Setup_6.6.2.exe"

reshade_path = ''

START_PATH = "/home"
PATTERN = "ReShade_Setup*.exe"

def find_reshade(start_path: Path, exe_pattern: str):
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

def download_reshade(url: str):
  if not find_reshade(START_PATH, PATTERN):
    try:
      os.system(f"wget {url}")
    except Exception as e:
      print(f"ERROR: {e}")
      return None
    finally:
      return True

reshade_path = find_reshade(START_PATH, PATTERN)

def unzip_reshade(reshade_path):
  if not os.path.isdir('./reshade'):
    with ZipFile(reshade_path, 'r') as zip_object:
      zip_object.extractall("./reshade")

def clone_default_shaders():
  effects_dir = './reshade/effects'
  os.makedirs(effects_dir, exist_ok=True)

  if len(os.listdir(effects_dir)) == 0:
    os.system("git clone https://github.com/crosire/reshade-shaders.git ./reshade/effects")
  else:    
    print("We already have shaders downloaded.")

# Function Calls
download_reshade(RESHADE_URL)
unzip_reshade(reshade_path)
clone_default_shaders()

# Debug strings
print(RESHADE_URL)
print(reshade_path)
