# Compatibility
You can go [back here](https://github.com/Ishidawg/LeShade).
Here there'll be listed games that I (and users) have tested so far. It's obvious that I can't test on every distro out there, I don't have all the games and every hardware... Well, you can contribute here by testing and adding your experience:

> [!NOTE]
> Before submit a contribution, please certified that the game is supported by ReShade on [PCGW](https://www.pcgamingwiki.com/wiki/ReShade#Game_compatibility).
## How to contribute

1. Fork the repository
2. Clone the repository
3. Add your experience to `compatibility.md`
4. Commit them: `git add . && git commit -m "My changes" && git push origin compatibility`
5. Create a pull request following this pattern below
```md
## Contribution title

**Special notes:**
notes
```
## What those emoji are for?
Easier understanding _(I like the way RenoDX does)_.
- 🟩 = Work Flawless
- 🟧 = Work with tweaks
- 🟥 = Does not work


| Works   | Game name              		                 | API Used | Platform | OS used 	 | Notes:
|:------: |:-------------------------------------------|:--------:|:--------:|:----------|:------------
| 🟩      |Dark Souls: Remastered                      | DX11 	  |  Steam   | Cachy OS	|None
| 🟩      |Dark Souls III                      				 | DX11 	  |  Steam   | Cachy OS	|None
| 🟩      |Elden Ring                      						 | DX12 	  |  Steam   | Cachy OS	|None
| 🟩      |Garry's Mod                      					 | DX9 	    |  Steam   | Cachy OS	|Need to place the `d3d9.dll` inside bin directory
| 🟩      |Star Wars: Dark Forces Remastered           | Vulkan 	|  Heroic  | Cachy OS	|None
| 🟩      |Grand Theft Auto III            						 | DX8 	    |  Heroic  | Cachy OS	|None
| 🟩      |Hollow Knight            								   | DX11 	  |  Heroic  | Cachy OS	|None
| 🟧      |PEAK                      								   | Vulkan 	|  Steam   | Cachy OS	|Shaders makes screen darker than usual, use DX11 or D12 instead.
| 🟩      |Cyberpunk 2077                      				 | DX12 	  |  Steam   | Cachy OS	|No FrameGen, RT or Upscaling
| 🟧      |Death Stranding 2: On the Beach     				 | DX12 	  |  Steam   | Cachy OS	|Any upscaler besides PICO causes missing visuals, only HUD elements remain
| 🟩      |Red Dead Redemption 2                       | Vulkan 	|  Steam   | Cachy OS	|None
