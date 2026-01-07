

# Reshade Installer
> *Intented to be used with proton applications, but it may also work with Wine*

## About
This is a university project that needs to have **three design patterns** of my choice *(Factory, Builder and Observer)*. The idea behind was to do reshade installation a bit easier on linux, as well understand about the design patterns. In fact it is intended to work with proton applications, but it may also work with apps that uses Wine. Also, no IA generated code.

## Why python?
_Why not?..._ I actually started the development in Java _(21)_ but due to limited time, python was a great choice because I write less and do _almost_ the same. **I dislike the sytax tho..**

## Why Qt?
_Why n-..._ I never built any GUI with **Qt** or **GTK**, so as I use *GNOME* on my daily drive machine, I thought of using it, but I could not get it to work in due time, so I choose Qt that I have seen awesome applications using it too, like: _PCSX2, Duckstation and ShadPS4..._

## Important
Reshade on linux works because it overrides wine dll `d3dcompiler_47.dll` _(that I clone from Lutris repo)_, so it is **recommended to have winetricks** installed, I thought of place the dll alongside the game executable to workaround this... Also, it is recommended to add command to steam games launch options, why I'm say that _'is recommended'_? Because **I do not add them**, just have winetricks installed and works perfectly. Let's say that you are installing reshade on a game that uses *DXVK* like **Dark Souls: Remastered**, then the dll will be `dxgi.dll`, so you put: `WINEDLLOVERRIDES="d3dcompiler_47=n;dxgi=n,b;"`.

<div align="center">
    <img alt="Windows Folder" src="https://i.imgur.com/B0V7ocQ.png" width="800" />
</div>

## Usage
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/ishidawg/reshade-installer-linux/total)


I think that th program is very intuitive, so if you already installed reshade before you will likely not have any problems. Even though, here is a video guide: https://youtu.be/tM0oJEPixzk

**Download on [releases page](https://github.com/Ishidawg/reshade-installer-linux/releases).** 


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
 - [x] Add OpenGL, DirecX 10/11/12
 - [ ] add an Uninstall feature
 - [ ] Add suport to DirecX 8 games with d3d8to9
 - [ ] Improve shaders download so the user can select many more shader repositories
 - [ ] Flatpak

 ## Sources
 I have uploaded the `d3dcompiler.dll` here so it never fails to download!
 - d3dcompiler.dll 64bit: https://lutris.net/files/tools/dll/d3dcompiler_47.dll
 - d3dcompiler.dll 32bit: https://download-installer.cdn.mozilla.net/pub/firefox/releases/62.0.3/win32/ach/Firefox%20Setup%2062.0.3.exe

 To package as AppImage I've used [appimagetool](https://github.com/AppImage/appimagetool?tab=readme-ov-file).
