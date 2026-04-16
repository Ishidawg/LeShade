# All related to the wrapper page. Style, text...
# Text needs to be on the list, follwing the parameter order bellow
# order: description_text, steam_text, other_text, steam_cmd, other_cmd, style_code, style_font

STYLE_CODE: str = "color: #E83C91; padding: 5px; font-style: italic;"
STYLE_FONT: str = "font 12pt; font-weight: 600; padding: 5px; margin: 5px;"

DX8_WRAPPER: list[str] = [
    " uses Direct3D 8.0 as rendering api, so you need to set environment varibles on steam, heroic games or whatever the launcher you use. If your game is on steam, you just need to set the command bellow as launch options.",
    f'<html><strong>Steam: <span style="{STYLE_CODE}">WINEDLLOVERRIDES="d3d8=n,b" %command%</span></strong></html>',
    f'<html><strong>Other: <span style="{STYLE_CODE}">WINEDLLOVERRIDES=d3d8=n,b</span></strong></html>',
    'WINEDLLOVERRIDES="d3d8=n,b" %command%',
    'WINEDLLOVERRIDES=d3d8=n,b'
]

VULKAN_WRAPPER: list[str] = [
    " uses Vulkan as rendering api, so you need to set environment variables on steam launch options, heroic games launcher or whatever you use.",
    f'<html><strong>Steam: <span style="{STYLE_CODE}">WINEDLLOVERRIDES="vulkan-1=n" %command%</span></strong></html>',
    f'<html><strong>Other: <span style="{STYLE_CODE}">WINEDLLOVERRIDES=vulkan-1=n</span></strong></html>',
    'WINEDLLOVERRIDES="vulkan-1=n" %command%',
    'WINEDLLOVERRIDES=vulkan-1=n'
]
