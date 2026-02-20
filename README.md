<div align="center">
	<img src="https://raw.githubusercontent.com/Ishidawg/LeShade/refs/heads/rebuild/assets/logo256.png">
	<h1>LeShade - A Reshade Manager</h1>
	<div display="flex">
		<img alt="GitHub License" src="https://img.shields.io/github/license/ishidawg/LeShade">
		<img alt="GitHub Downloads (all assets, all releases)" src="https://img.shields.io/github/downloads/ishidawg/LeShade/total">
		<img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/ishidawg/LeShade">
	</div>
</div>

*This project started as a university project, and I already mentioned that in the [old readme file](https://github.com/Ishidawg/LeShade/blob/main/OLD-README.md). The project grew and became a passion project, and now I think it's good to have a new readme file.*

LeShade is a reshade manager for linux, thinks of a mod manager, but specifically for reshade. It include features like:
- Common APIs support *(DX9, DX10, DX11, DX12/Vulkan, OpenGL)*
- Direct3D 8.x support
- ReShade with **addon** and **non-addon** versions
- ReShade with release versions support
- Uninstall ReShade per game basis from previous installations
- Many shaders repositories

## Usage
The program it self is very intuitive, so if you already used a mod manager or even the reshade installer *"à la"* Wizard you will no likely not have any problems. Even though I have made a [video guide](https://youtu.be/ge8558huYfE). You can download the AppImage or Flatpak version on [release page](https://github.com/Ishidawg/LeShade/releases).

**AppImage Instructions:**
1. Select `LeShade-x86_64.AppImage` that you have download
2. Right click > Properties > Permissions > **Check: Allow executing file as program** _(or likely)_
3. Done!

**Flatpak Instructions:**
1. Open the terminal
2. Go to the folder that you have downloaded LeShade (eg: `cd ~/Downloads`)
3. Execute on terminal: `flatpak install ./LeShade-x86_64.flatpak`
4. Done!

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

### Files
LeShade createas folder on the `config`with a json file called `manager.json`. It stores the path and the name of the game so it can be used to show the game name on uninstall list as well to uninstall the game properly by using the path stored inside the file.

There is a key difference between where the `leshade/manager.json` will be on your computer depending on the version that you're using.

For the appImage version, as it uses system dependencies, you will find the file into: `~/.config/leshade/manager.json`.

For flatpak version, due to sandbox system that the package uses, you will find the file into: `~/.var/app/io.github.ishidawg.LeShade/config/leshade/manager.json`.

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
- `d3dcompiler_47.dll` *64bit* and *32bit* from [WindowsSDK 10.0.26100.0](https://learn.microsoft.com/en-us/windows/apps/windows-sdk/downloads)
- `d3d8to9.dll` from [crosire](https://github.com/crosire/d3d8to9?tab=readme-ov-file).
- [AppImage](https://github.com/crosire/d3d8to9?tab=readme-ov-file) Tool to build my one of my packages.

