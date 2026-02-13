<div align="center">
	<img src="https://raw.githubusercontent.com/Ishidawg/LeShade/refs/heads/rebuild/assets/logo256.png">
	<h1>LeShade - A Reshade Manager</h1>
</div>

*This project started as a university project, and I already mentioned that in the old readme file. The project grew and became a passion project, and now I think it's good to have a new readme file.*
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/ishidawg/reshade-installer-linux/total)

LeShade is a reshade manager for linux, thinks of a mod manager, but specifically for reshade. It include features like:
- Common APIs support *(DX9, DX10, DX11, DX1/Vulkan, OpenGL)*
- Direct3D 8.x support
- ReShade with **addon** and **non-addon** versions
- ReShade with release versions support
- Uninstall ReShade per game basis from previous installations
- Many shaders repositories

## Usage
The program it self is very intuitive, so if you already used a mod manager or even the reshade installer *"à la"* Wizard you will no likely not have any problems. Even though I have made a [video guide](https://youtu.be/tM0oJEPixzk).
You can download the AppImage or Flatpak version on [release page](https://github.com/Ishidawg/LeShade/releases).

**AppImage Instructions:**
1. Select `LeShade-x86_64.AppImage` that you have download
2. Right click > Properties > Permissions > **Check: Allow executing file as program** _(or likely)_
3. Done!

**Flatpak Instructions:**
4. Open the terminal
5. Go to the folder that you have downloaded LeShade (eg: `cd ~/Downloads`)
6. Execute on terminal: `flatpak install ./LeShade-x86_64-x86_64.flatpak`
7. Done!

**Direct3D 8.0 instructions:**
If you are installing ReShade on game that uses Direct3D 8.0, you **must** add the environment variables on your game launcher *(Steam, Heroic Games Lancher, Lutris, Faugus Launcher)*. Here are two examples of how you can do to set those on Steam and Heroic.
<div align="center">
		<h3>Steam launch options</h3>
    <img alt="Steam launch options" src="https://i.imgur.com/HEq7U4X.png" width="800" />
</div>
<div align="center">
	<h3>Heroic launch options</h3>
    <img alt="Heroic games launcher" src="https://i.imgur.com/Ymj68nY.png" width="800" />
</div>

## Development
LeShade is built with PySide6 with default Qt widgets, so you can expect a **seamless theme integration with your system**. Qt was my choice to build the GUI because I've seen other awesome applications that uses it and I really like: *PCSX2, Duckstation and ShadPS4*. Also,  LeShade was developed exclusive by human hands, without any sort of AI bullshit.

I have tested each build *(AppImage and Flatpak)* on *Oracle Virtual* with those 3 distros: *Ubuntu 25.10, Ubuntu 24.04.3, Linux Mint 22.2*. Also, have tested on *CachyOS non-vm*. You can take a look into this [pull resquest](https://github.com/Ishidawg/LeShade/pull/9).
The logo was made by me on *Inkscape*.

## Contributing
If you want to contribute to LeShade, feel free to clone the repository, do the changes you want to do, and create pull requests. Every kind of contributions are very welcome!

Open issues when you encounter an... well - issue, is a real great contribution as well.

### How to contribute:
1. Fork the repository
2. Make your changes
3. Commit them: `git add . && git commit -m "My changes" && git push origin main`
4. Create a pull request following this pattern bellow
```md
## Contribution title

**Have you used IA to vibe coding?**
Response.
**Have you used IA as a research source?**
Response.
**Have you tested locally?**
Response.

### Fixes:
Description of what you have fixed.
```
### Sources:
- `d3dcompiler.dll` *64bit* from [Lutris](https://lutris.net/files/tools/dll/d3dcompiler_47.dll).
- `d3dcompiler.dll` *32bit* from [Mozzila](https://download-installer.cdn.mozilla.net/pub/firefox/releases/62.0.3/win32/ach/Firefox%20Setup%2062.0.3.exe).
- `d3d8to9.dll` from [crosire](https://github.com/crosire/d3d8to9?tab=readme-ov-file).
- [AppImage](https://github.com/crosire/d3d8to9?tab=readme-ov-file) Tool to build my one of my packages.

