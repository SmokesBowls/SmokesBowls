# zw_import_watcher.py
# Purpose: Monitors a local folder for new ZW templates and routes them to the ZW Transformer for validation/testing

import os
import time
import shutil
from pathlib import Path
import sys # For sys.exit, if fatal errors occur

WATCH_FOLDER = Path("zw_drop_folder/experimental_patterns")
VALIDATED_FOLDER = Path("zw_drop_folder/validated_patterns")
RESEARCH_LOG = Path("zw_drop_folder/research_notes/what_worked.md")

# Placeholder validation logic (replace with real ZWValidator call)
def validate_zw_template(file_path):
    try:
        with file_path.open("r", encoding="utf-8") as f:
            lines = f.readlines()
            if any("ENTROPY:" in line for line in lines):
                return True, "Entropy field detected."
            # Corrected iteration for tags: check if any tag is present in any line
            elif any(tag in line for line in lines for tag in ("ZW-OBJECT:", "TYPE:", "ZW-STAGE:")):
                return True, "Basic ZW structure detected."
            else:
                return False, "Missing entropy or structural tags."
    except Exception as e:
        return False, f"Error: {str(e)}"

def watch_folder():
    print(f"🔍 Watching folder: {WATCH_FOLDER.resolve()}")
    seen_files = set()
    # Initialize seen_files with .zw files currently in the watch folder
    if WATCH_FOLDER.exists():
        seen_files = {f.name for f in WATCH_FOLDER.glob("*.zw")}
        print(f"[*] Initially found {len(seen_files)} .zw files. Monitoring for new ones...")
    else:
        # This case should ideally be handled by setup_directories or the main block ensuring folders exist.
        # If WATCH_FOLDER doesn't exist here, globbing will fail.
        print(f"[*] Watch folder {WATCH_FOLDER} not found. It should have been created by main setup.")
        # Attempting to create it here if it's missing, though it's better practice to ensure it in main.
        try:
            WATCH_FOLDER.mkdir(parents=True, exist_ok=True)
            print(f"[*] Created missing watch folder: {WATCH_FOLDER}")
        except Exception as e_create_watch:
            print(f"[ERROR] Could not create watch folder {WATCH_FOLDER} during watch_folder init: {e_create_watch}")
            append_log(f"🔥 WATCHER ERROR: Could not create watch folder {WATCH_FOLDER} - {e_create_watch}")
            return # Exit watch_folder if it cannot ensure its main target exists

    while True:
        try:
            # Ensure WATCH_FOLDER still exists in case it was deleted during runtime
            if not WATCH_FOLDER.exists():
                print(f"[ERROR] Watch folder {WATCH_FOLDER} has disappeared. Attempting to recreate...")
                append_log(f"🔥 WATCHER ERROR: Watch folder {WATCH_FOLDER} disappeared.")
                try:
                    WATCH_FOLDER.mkdir(parents=True, exist_ok=True)
                    print(f"[*] Recreated watch folder: {WATCH_FOLDER}")
                    seen_files.clear() # Reset seen files as the folder was recreated
                except Exception as e_recreate_watch:
                    print(f"[ERROR] Could not recreate watch folder {WATCH_FOLDER}. Stopping watcher thread/loop: {e_recreate_watch}")
                    append_log(f"🔥 WATCHER ERROR: Could not recreate watch folder {WATCH_FOLDER}. Stopping. - {e_recreate_watch}")
                    break # Exit the loop

            for file_path_obj in WATCH_FOLDER.glob("*.zw"): # Iterate directly on Path objects
                if file_path_obj.name not in seen_files:
                    print(f"\n🧪 New file detected: {file_path_obj.name}")

                    valid, message = validate_zw_template(file_path_obj)

                    if valid:
                        print(f"  ✅ Validated: {message}")
                        dest = VALIDATED_FOLDER / file_path_obj.name
                        try:
                            shutil.copy(file_path_obj, dest)
                            print(f"    Copied to: {dest.resolve()}")
                            append_log(f"✅ {file_path_obj.name} - {message}")
                        except Exception as e_copy:
                            print(f"    [ERROR] Could not copy {file_path_obj.name}: {e_copy}")
                            append_log(f"❌ ERROR COPYING: {file_path_obj.name} - {message} - {e_copy}")
                    else:
                        print(f"  ❌ Rejected: {message}")
                        append_log(f"❌ {file_path_obj.name} - {message}")

                    seen_files.add(file_path_obj.name) # Add to seen after processing attempt

            # Optional: Prune seen_files if files are removed from WATCH_FOLDER
            # This ensures that if a file is deleted and re-added, it's processed again.
            current_filenames_in_watch_set = {f.name for f in WATCH_FOLDER.glob("*.zw")}
            if not seen_files.issubset(current_filenames_in_watch_set):
                removed_files = seen_files - current_filenames_in_watch_set
                if removed_files:
                    # print(f"[*] Files removed from watch folder: {removed_files}. Updating seen set.")
                    seen_files = seen_files.intersection(current_filenames_in_watch_set)

        except Exception as e_loop:
            print(f"[ERROR] Watch loop iteration failed: {e_loop}")
            append_log(f"🔥 WATCHER ERROR: Loop iteration failed - {e_loop}")

        time.sleep(3)

def append_log(entry):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        RESEARCH_LOG.parent.mkdir(parents=True, exist_ok=True) # Ensure log directory exists
        with RESEARCH_LOG.open("a", encoding="utf-8") as log:
            log.write(f"[{timestamp}] {entry}\n")
    except Exception as e_log:
        print(f"[ERROR] Failed to append to log {RESEARCH_LOG}: {e_log}")

if __name__ == "__main__":
    print("[*] Initializing ZW Import Watcher...")
    try:
        WATCH_FOLDER.mkdir(parents=True, exist_ok=True)
        VALIDATED_FOLDER.mkdir(parents=True, exist_ok=True)
        RESEARCH_LOG.parent.mkdir(parents=True, exist_ok=True) # Ensures research_notes dir
        print(f"[*] Ensured directories exist:\n    Watch:     {WATCH_FOLDER.resolve()}\n    Validated: {VALIDATED_FOLDER.resolve()}\n    Log File:  {RESEARCH_LOG.resolve()}")
    except Exception as e_setup:
        print(f"[FATAL ERROR] Could not set up watcher directories: {e_setup}. Exiting.")
        # Consider using sys.exit(1) if Python version is known and sys is imported.
        # For now, just printing and letting it potentially fail in watch_folder() if dirs are critical.
        # If directories are absolutely critical for the script to even start, uncomment:
        # import sys
        # sys.exit(1)
        # For this exercise, we'll let it proceed and potentially log errors if watch_folder fails.

    try:
        watch_folder()
    except KeyboardInterrupt:
        print("\n[*] Watcher stopped by user (Ctrl+C).")
    except Exception as e_main_watch:
        print(f"[FATAL ERROR] Watcher failed unexpectedly: {e_main_watch}")
        append_log(f"💀 WATCHER CRASHED: {e_main_watch}") # Log the crash
    finally:
        print("[*] ZW Import Watcher shut down.")
