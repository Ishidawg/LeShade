# Reshade Installer
> *Intented to be used with proton applications, but it may also work with Wine*

## About
This is a university project that needs to have **three design patterns** of my choice *(Factory, Builder and Observer)*. The idea behind was to do reshade installation a bit easier on linux, as well understand about the design patterns. In fact it is intended to work with proton applications, but it may also work with apps that uses Wine. Also, no IA generated code.

## Why python?
_Why not?..._ I actually started the development in Java _(21)_ but due to limited time, python was a great choice because I write less and do _almost_ the same. **I dislike the sytax tho..**

## Why Qt?
_Why n-..._ I never built any GUI with **Qt** or **GTK**, so as I've used *GNOME* on my daily drive machine, I thought of using it, but I could not get it to work in due time, so I choose Qt that I have seen awesome applications using it too, like: _PCSX2, Duckstation and ShadPS4..._

## Important
Reshade on linux works because it overrides wine dll `d3dcompiler_47.dll` _(that I clone from Lutris repo)_, so it is **recommended to have winetricks** installed, I thought of place the dll alongside the game executable to workaround this... and it works. If you are installing reshade on a Direct3D 8.x game, you **must** add `WINEDLLOVERRIDES="d3d8=n,b;" %command%` to steam launch options or any of the game launcher available like Lutris, Heroic Games and stuff, I personally have tested on Grand Theft Auto 3 Legacy Version. 

**Steam Launch options for Direct3D 8.x**
<div align="center">
    <img alt="Steam launch options" src="https://i.imgur.com/HEq7U4X.png" width="800" />
</div>

**Heroic Games Launcher environment variabel for Direct3D 8.x**
<div align="center">
    <img alt="Heroic games launcher" src="https://i.imgur.com/Ymj68nY.png" width="800" />
</div>


## Usage
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/ishidawg/reshade-installer-linux/total)


I think that the program is very intuitive, so if you already installed reshade before you will likely not have any problems. Even though, here is a video guide: https://youtu.be/tM0oJEPixzk

**Download the AppImage or Flatpak on [releases page](https://github.com/Ishidawg/reshade-installer-linux/releases).**

**AppImage Instructions:**
1. Right click > Properties > Permissions > **Check: Allow executing file as program** _(or likely)_

**Flatpak Instructions:**
1. On terminal, go to where the file you download is, like: `cd ~/Downloads`
2. `flatpak install Reshade_Installer-x86_64.AppImage`

### Descriptive guide:

1. At first, the program will download the reshade from the official website, so you just **click next**.
2. Select the game executable and the graphic API, you will likely want to **choose vulkan and click on next**. You can check [pcgamingwiki](https://www.pcgamingwiki.com/wiki/Home) if necessary.
3. Select the shaders pack that you want and **click on install**.

**After the installation process, open your game up, press the `HOME` key to open up reshade menu and go to `settings` tab, then add the folder `Shaders` and `Textures`.**

## Roadmap
The project of course is not currently done, look at monstrosity of GUI... Also as my goal is to do reshade installation easier on linux, it would be fabulous if I reduce user steps, like selecting the application architecture and even cloning the repo. Why not do a flatpak of it also?

 - [x] Basic functionalities
 - [x] Redo GUI
 - [x] Automatically verify the application architecture: it can be done by looking into some of the first bytes of the game executable binary, they are located  on the COFF Header. (Thanks to Jhen - https://github.com/Dzavoy)
 - [x] Rewrite whole app with new pages
 - [x] appImage
 - [x] Add OpenGL, DirectX 10/11/12
 - [x] Add suport to DirectX 8 games with d3d8to9
 - [x] Flatpak
 - [x] add an Uninstall feature
 - [ ] add the possibility to select reshade with addon-support
 - [ ] user can select the reshade version
 - [ ] Improve shaders download so the user can select many more shader repositories
 
### Flathub?
I tried to upload into flathub, have open a PR and aparently, my app can't be on flathub because they say that I can't add _installer for a windows app_... - Does not make any sense to me.

## Contributing
If you want to contribute to Reshade Installer, feel free to for the repository, do the changes you want to do, and create pull requests. Every kind of contributions are very welcome!

### How to contribute:
 1. Fork the repository
 2. Make your changes
 3. Commit them: `git add . && git commit -m "My changes" && git push origin main`
 4. Create a pull request. Please add into the PR if you have used IA for any kinda stuff, studying, coding...

 ## Sources
 - `d3dcompiler.dll` _64bit_: https://lutris.net/files/tools/dll/d3dcompiler_47.dll
 - `d3dcompiler.dll` _32bit_: https://download-installer.cdn.mozilla.net/pub/firefox/releases/62.0.3/win32/ach/Firefox%20Setup%2062.0.3.exe
 - `d3d8to9` from _crossire_: https://github.com/crosire/d3d8to9?tab=readme-ov-file
 To package as AppImage I've used [appimagetool](https://github.com/AppImage/appimagetool?tab=readme-ov-file).
