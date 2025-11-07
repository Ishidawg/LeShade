

# Reshade Installer
> *Intented to be used with proton applications*

## About
This is a university project that needs to have **three design patterns** of my choice *(Factory, Builder and Observer)*. The idea behind was to do reshade installation a bit easier on linux, as well understand about the design patterns. In fact it is intended to work with proton applications, but it may also work with apps that uses Wine. Also, no IA.

## Why python?
_Why not?..._ I actually started the development in Java _(21)_ but due to limited time, python was a great choice because I write less and do _almost_ the same. **I dislike the sytax tho..**

## Why Qt?
_Why n-..._ I never built any GUI with **Qt** or **GTK**, so as I use *GNOME* on my daily drive machine, I thought of using it, but I could not get it to work in due time, so I choose Qt that I have seen awesome applications using it too, like: _PCSX2, Duckstation and ShadPS4..._

## Usage
*This will only be necessary until I have any packages, appImage or Flatpak.*

 1. Download Reshade from the official website: https://reshade.me/
I did this because I saw this next to the download button: **Do NOT share the binaries or shader files. Link users to this website instead.**

 2. As this project was made in python with Qt, you will need to run `pip install PySide6` to install the lib for Qt **globally**, or you can do it on a **venv** if you want, so inside of the project folder:
- create a venv: `python -m venv env`
- activate it: `source env/bin/activate`
- lib installation: `pip install PySide6`
- run it: `python gui.py` or `python3 gui.py`

## Roadmap
The project of course is not currently done, look at monstrosity of GUI... Also as my goal is to do reshade installation easier on linux, it would be fabulous if I reduce user steps, like selecting the application architecture and even cloning the repo. Why not do a flatpak of it also?

 - [x] Basic functionalities
 - [x] Redo GUI
 - [ ] Automatically verify the application architecture: it can be done by looking into some of the first bytes of the game executable binary, they are located  on the COFF Header.
 - [ ] Flatpak
 - [ ] appImage

### New UI
I have spent some time on UI/UX software trying to make it look not to bad, this is what I want to do:
<img width="1467" height="919" alt="image" src="https://github.com/user-attachments/assets/b5947595-d14e-4799-9b46-204bb56dc3f8" />
