<div align="center">
	<img src="https://raw.githubusercontent.com/Ishidawg/LeShade/refs/heads/rebuild/assets/logo256.png">
	<h1>LeShade - A Reshade Manager</h1>
	<div display="flex">
		<img alt="GitHub License" src="https://img.shields.io/github/license/ishidawg/LeShade">
		<img alt="GitHub Downloads (all assets, all releases)" src="https://img.shields.io/github/downloads/ishidawg/LeShade/total">
		<img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/ishidawg/LeShade">
	</div>
	<div>
		<a href="https://copr.fedorainfracloud.org/coprs/ishidaw/leshade/package/leshade/"><img src="https://copr.fedorainfracloud.org/coprs/ishidaw/leshade/package/leshade/status_image/last_build.png" /></a>
		<img alt="AUR Version" src="https://img.shields.io/aur/version/leshade-git">
	</div>
</div>

*This project started as a university project, and I already mentioned that in the [old readme file](https://github.com/Ishidawg/LeShade/blob/main/OLD-README.md). The project grew and became a passion project, and now I think it's good to have a new readme file.*

LeShade is a reshade manager for linux. Think of a mod manager, but specifically for reshade. It includes features like:
- Common APIs support *(DX9, DX10, DX11, DX12, OpenGL)*
- Direct3D 8.x support
- ReShade with **addon** and **non-addon** versions
- ReShade with release versions support
- Uninstalling ReShade per game basis from previous installations
- Many shaders repositories

### Why is Vulkan not in the Common APIs support?
If you plan to install _ReShade_ on a _Vulkan_ game on Linux, I suggest you use [VkBasalt](https://github.com/DadSchoorse/vkBasalt). When using ReShade on a game that uses Vulkan, you can't just rename a `.dll` and place it in the game's directory, it uses a global directory for ReShade, usually at `C:\ProgramData\ReShade`, and requires those `.dll` files in that directory, along with `.json` files that have the path mentioned in a registry key so ReShade can work with the Vulkan API. On Linux this is not the case. I followed the manual steps and even tried to install `VulkanRT-X64-1.4.341.0-Installer.exe` with _protontricks_ and _WINEPREFIX_, but had no success. You can try to add it yourself and even download the runtimes from Vulkan and replace the `vulkan-1.dll` inside `System32` to see if you have more luck than I did, but I don't think so. If you are a developer who knows how to fix it, you are welcome to contribute to the project. Unfortunately, I can't support ReShade on games that use native Vulkan. Note that this does not apply to DXVK, which works fine.

You can get more information about it here: [issue](https://github.com/Ishidawg/LeShade/issues/16).

## Usage
The program itself is very intuitive, so if you already used a mod manager or even the ReShade installer *"à la"* wizard you will likely not have any problems. Even though I have made a [video guide](https://youtu.be/ge8558huYfE). You can download the AppImage or Flatpak version on the [release page](https://github.com/Ishidawg/LeShade/releases).

**AppImage Instructions:**
1. Select `LeShade-x86_64.AppImage` that you have downloaded
2. Right click > Properties > Permissions > **Check: Allow executing file as program** _(or likely)_
3. Done!

**Flatpak Instructions:**
1. Open the terminal
2. Go to the folder that you have downloaded LeShade in (default: `cd ~/Downloads`)
3. Execute in the terminal: `flatpak install ./LeShade-x86_64.flatpak`
4. Done!

### Arch Linux instructions:
You have some options on AUR, the `leshade-git` package that always gets the latest commit and the `leshade-bin` _(thanks to [@italoghost](https://github.com/italoghost))_ that gets the latest release _(not commit)_.

**Leshade-bin:**
1. Open the terminal
2. `paru -S leshade-bin` or `yay -S leshade-bin`
3. Done!

**Leshade-git:**
1. Open the terminal
2. `paru -S leshade-git` or `yay -S leshade-git`
3. Done!

### Gentoo Linux instructions:
Available in [GURU](https://wiki.gentoo.org/wiki/Project:GURU).

**games-util/leshade:**
1. Open the terminal
2. Add the GURU repository as described in [Project:GURU/Information for End Users](https://wiki.gentoo.org/wiki/Project:GURU/Information_for_End_Users)
3. `emerge --ask games-util/leshade`
4. Done!

### Fedora instructions:
I've managed to create a build to _Fedora copr_ with the latest release of LeShade.

**Leshade:**
1. Open the terminal
2. ```sudo dnf copr enable ishidaw/leshade```
3. ```sudo dnf install leshade```
4. Done!

**Direct3D 8.0 instructions:**
If you are installing ReShade on a game that uses Direct3D 8.0, you **must** add the environment variables on your game launcher *(Steam, Heroic Games Launcher, Lutris, Faugus Launcher)*. Here are two examples of how you can set those on Steam and Heroic.
<div align="center">
		<h3>Steam launch options</h3>
    <img alt="Steam launch options" src="https://i.imgur.com/HEq7U4X.png" width="800" />
</div>
<div align="center">
	<h3>Heroic launch options</h3>
    <img alt="Heroic games launcher" src="https://i.imgur.com/Ymj68nY.png" width="800" />
</div>

## Development
LeShade is built with PySide6 with default Qt widgets, so you can expect a **seamless theme integration with your system**. Qt was my choice to build the GUI because I've seen other awesome applications that use it and I really like: *PCSX2, Duckstation and ShadPS4*. Also, LeShade was developed exclusively by human hands, without any sort of AI bullshit.
I have tested each build *(AppImage and Flatpak)* on *Oracle Virtual* with those 3 distros: *Ubuntu 25.10, Ubuntu 24.04.3, Linux Mint 22.2*. Also, have tested on *CachyOS non-vm*. You can take a look into this [pull request](https://github.com/Ishidawg/LeShade/pull/9).
The logo was made by me on *Inkscape*.

### Files
LeShade creates a folder on the `config` with a json file called `manager.json`. It stores the path and the name of the game so it can be used to show the game name on the uninstall list as well as to uninstall the game properly by using the path stored inside the file.

There is a key difference between where the `leshade/manager.json` will be on your computer depending on the version that you're using.

For the AppImage version, as it uses system dependencies, you will find the file at: `~/.config/leshade/manager.json`.

For the Flatpak version, due to the sandbox system that the package uses, you can find the file at: `~/.var/app/io.github.ishidawg.LeShade/config/leshade/manager.json`.

## Contributing
If you want to contribute to LeShade, feel free to clone the repository, make the changes you want to make, and create pull requests. Every kind of contribution is very welcome!

Opening issues when you encounter an... well - issue, is a really great contribution as well.

### How to contribute:
1. Fork the repository
2. Make your changes
3. Commit them: `git add . && git commit -m "My changes" && git push origin main`
4. Create a pull request following this pattern below
```md
## Contribution title

**Have you used AI to vibe code?**
Response.
**Have you used AI as a research source?**
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
