# UE-ModDeployer
A lightweight Python utility script for UE4/5 automated post-build deployment of chunk assigned mods. </br>
The script waits for a successful build then moves the mods files and launches the game for rapid mod deployment and testing.

Click [here](https://github.com/Dmgvol/UE-ModDeployer/releases/latest/download/UE-ModDeployer.py) to download the latest script version.

![](/deploy.gif)

### Features
- **Monitors the packaging log** for successful mod builds.
- **Moves and renmaes** the generated mod files (`.pak`, `.ucas`, and `.utoc`) files to the game's Paks folder.
- **Launches the game automatically** after files are in place.
- **Continuous monitoring** allows the tool to handle future builds.

> [!NOTE]  
> The mod only moves the packaged files and doesn't support UnrealPak.

## Installation:
1. Download the script (link above).
2. Configure the script with the correct folders (see below for more info).
3. Create a JSON file named `mods.json` within the same folder as the script, and add the JSON structure as shown below.
4. Execute the script by running `python UE-ModDeployer.py`


All configuration is done directly in the script via a few key constants.

## Configuration
#### Required:
- `PROJECT_DIR`: Path to project root folder.
- `PROJECT_NAME`: The project's name (used for locating the log and build output). 
- `PAK_SOURCE_DIR`: The project build path (I usually have it in `Build` within the project folder)
- `PAK_TARGET_ROOT`: The game's `Paks` folder.
- `GAME_EXE_PATH`: Path to the game's executable.

#### Optional:
- `WAIT_FOR_NEW_BUILD = True`: Trigger only on the next detected successful build.
- `CONTINUOUS_MODE = True`: Continue waiting for future builds.
- `LAUNCH_GAME_AFTER = True`: Launch the game after all files are moved and renamed.

> [!TIP]
> Having trouble? check out the [example script](https://github.com/Dmgvol/UE-ModDeployer/blob/main/UE-ModDeployer_Example.py) used for game called RooftopsAndAlleys.

### JSON File
All mod mappings are defined in a simple json file, as shown below: <br>

```json
[
  {
    "chunk_id": 1206,
    "mod_name": "jetpack_p",
    "relative_path": "outfits"
  },
  {
    "chunk_id": 1207,
    "mod_name": "mymod_P",
    "relative_path": ""
  }
]
```


> [!TIP]
> Empty `relative_path` will place the mod inside the game's Paks folder.<br>
> Relative paths are concatinated after the game's Paks folder -> `.../Paks/outfits/` (example 1)

---
> [!NOTE]
> This is a private-use script for automating the most common procedure of modding.