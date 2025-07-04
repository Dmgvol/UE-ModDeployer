# UE-ModDeployer
# Automated mod deployment IOStore UE4/5 projects

import os
import time
import shutil
import json
import subprocess

# ====== Project Configuration=====
PROJECT_DIR = "<project_root_directory>"  # Replace with your project root directory
PROJECT_NAME = "<project_name>"  # Replace with your project name
LOG_DIR = os.path.join(PROJECT_DIR, "Saved", "Logs")
LOG_FILE_PATH = os.path.join(LOG_DIR, f"{PROJECT_NAME}.log")

# Config JSON
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_JSON_PATH = os.path.join(SCRIPT_DIR, "mods.json") # Same folder as this script

# PAK Files
WAIT_FOR_NEW_BUILD = True
CONTINUOUS_MODE = True
PAK_SOURCE_DIR = os.path.join(PROJECT_DIR, "Build", "Windows", PROJECT_NAME, "Content", "Paks")
PAK_TARGET_ROOT = f"C:\\Program Files (x86)\\Steam\\steamapps\\common\\{PROJECT_NAME}\\{PROJECT_NAME}\\Content\\Paks" # Replace with game's Paks directory
FILE_EXTENSIONS = ["pak", "ucas", "utoc"] # for for IOStore: "pak", "ucas", "utoc"; for legacy: "pak"

# Launch game after moving files
LAUNCH_GAME_AFTER = True 
GAME_EXE_PATH = f"C:\\Program Files (x86)\\Steam\\steamapps\\common\\{PROJECT_NAME}\\{PROJECT_NAME}\\Binaries\\Win64\\{PROJECT_NAME}-Win64-Shipping.exe"


# Monitor UE packaging log for successful builds
def monitor_packaging_log():
    print("[...] Monitoring UE packaging log...")

    while not os.path.exists(LOG_FILE_PATH):
        print("[!] Log file not found. Waiting...")
        time.sleep(2)

    last_file_size = os.path.getsize(LOG_FILE_PATH)
    last_mod_time = os.path.getmtime(LOG_FILE_PATH)
    last_success_time = 0

    # Check if to skip "waiting for new build"
    if not WAIT_FOR_NEW_BUILD:
        with open(LOG_FILE_PATH, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        for line in reversed(lines):
            # Check existing successful build in log
            if "Packaging (Windows): BuildCookRun time: " in line:
                print("[Success] Detected existing successful build in log.")
                handle_successful_build()
                if not CONTINUOUS_MODE:
                    return
                last_success_time = os.path.getmtime(LOG_FILE_PATH)
                break
        else:
            print("[Error] No successful build found in existing log.")
            if not CONTINUOUS_MODE:
                return

    # Monitor log file for new successful build(s)
    while True:
        try:
            current_size = os.path.getsize(LOG_FILE_PATH)
            current_mod_time = os.path.getmtime(LOG_FILE_PATH)

            # Check if log file has been updated
            if current_size > last_file_size or current_mod_time > last_mod_time:
                with open(LOG_FILE_PATH, "r", encoding="utf-8", errors="ignore") as f:
                    f.seek(last_file_size)
                    new_data = f.read()
                    new_lines = new_data.splitlines()

                # Check for new successful build entries
                for line in new_lines:
                    if "Packaging (Windows): BuildCookRun time: " in line:
                        if current_mod_time > last_success_time:
                            print("[Success] Detected new successful packaging.")
                            handle_successful_build()
                            last_success_time = current_mod_time

                            # If in continuous mode, keep monitoring
                            if not CONTINUOUS_MODE:
                                return
                            print("[...] Monitoring UE packaging log...")
                            break

                last_file_size = current_size
                last_mod_time = current_mod_time

            time.sleep(5)

        except Exception as e:
            print(f"[Error] Error reading log: {e}")
            time.sleep(10)

# Handle successful build by moving and renaming chunk files
def handle_successful_build():
    chunk_map = read_chunk_map(CONFIG_JSON_PATH)
    for chunk in chunk_map:
        move_and_rename_chunk(chunk)
    print("[Success] All specified chunk files moved.")
    # Optionally: launch game after moving files
    if LAUNCH_GAME_AFTER:
        launch_game()

# Read JSON configuration for chunk mappings
def read_chunk_map(json_path):
    if not os.path.exists(json_path):
        print(f"[Error] Config file not found at {json_path}")
        return []
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
        print(f"[Info] Loaded config for {len(data)} chunks.")
        return data
    except Exception as e:
        print(f"[Error] Failed to parse config JSON: {e}")
        return []

# Find chunk files in source directory
def find_chunk_files(chunk_id):
    found_files = []
    for ext in FILE_EXTENSIONS:
        base_name = f"pakchunk{chunk_id}-Windows.{ext}"
        full_path = os.path.join(PAK_SOURCE_DIR, base_name)
        # Check if file exists in source directory
        if os.path.exists(full_path):
            found_files.append((full_path, ext))
        else:
            print(f"[Warning] Missing file: {full_path}")
    return found_files

# Move and rename chunk files to target directory
def move_and_rename_chunk(chunk_info):
    found_files = find_chunk_files(chunk_info["chunk_id"])

    # Check if any files found
    if not found_files:
        print(f"[Error] No pak files found for chunk id {chunk_info['chunk_id']}")
        return

    target_dir = os.path.join(PAK_TARGET_ROOT, chunk_info.get("relative_path", ""))
    os.makedirs(target_dir, exist_ok=True)
    print(f"[Info] Moving chunk id {chunk_info['chunk_id']} files to {os.path.basename(target_dir)}")

    # Copy each found file to target directory with new name
    for src_path, ext in found_files:
        dst_filename = f"{chunk_info['mod_name']}.{ext}"
        dst_path = os.path.join(target_dir, dst_filename)
        try:
            # Copy file to target directory
            shutil.copy2(src_path, dst_path)
            print(f"[Success] Copied {os.path.basename(src_path)} -> {os.path.basename(dst_path)}")
        except Exception as e:
            print(f"[Error] Failed to copy {os.path.basename(src_path)} to {os.path.basename(dst_path)}: {e}")

# Launch game executable
def launch_game():
    if not os.path.exists(GAME_EXE_PATH):
        print(f"[Error] Cannot launch game. Executable not found at: {GAME_EXE_PATH}")
        return
    try:
        print(f"[Success] Launching game: {GAME_EXE_PATH}")
        subprocess.Popen(GAME_EXE_PATH) 
    except Exception as e:
        print(f"[Error] Failed to launch game: {e}")

# Run the monitor
monitor_packaging_log()
