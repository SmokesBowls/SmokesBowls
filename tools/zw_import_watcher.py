# tools/zw_import_watcher.py
# Purpose: Monitors a local folder for new ZW templates and routes them to the ZW Transformer for validation/testing

import os
import time
import shutil
from pathlib import Path # Added for robust paths
import sys # Import sys for sys.exit()

# Define root for drop folders relative to this script's location or project root
# Assuming this script is in tools/, project_root is one level up.
# zw_drop_folder will be at the project root.
try:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
except NameError:
    PROJECT_ROOT = Path(".").resolve() # Fallback if __file__ is not defined

DROP_FOLDER_ROOT = PROJECT_ROOT / "zw_drop_folder"
WATCH_FOLDER = DROP_FOLDER_ROOT / "experimental_patterns"
VALIDATED_FOLDER = DROP_FOLDER_ROOT / "validated_patterns"
RESEARCH_LOG_DIR = DROP_FOLDER_ROOT / "research_notes" # Changed from os.path.dirname
RESEARCH_LOG = RESEARCH_LOG_DIR / "what_worked.md"

# Placeholder validation logic (replace with real ZWValidator call)
def validate_zw_template(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f: # Added encoding
            lines = f.readlines()
            if any("ENTROPY:" in line for line in lines): # User's original check
                return True, "Entropy field detected."
            else:
                # More specific feedback based on user's original else condition
                return False, "Missing entropy logic (placeholder validation)."
    except Exception as e:
        return False, f"Error reading/validating file: {str(e)}"

def watch_folder():
    print(f"Watching folder: {WATCH_FOLDER.resolve()}") # Using .resolve() for absolute path
    seen_files = set(os.listdir(WATCH_FOLDER)) # Initialize with current files
    print(f"Initially found {len(seen_files)} files in watch folder. Monitoring for new .zw files...")


    while True:
        try: # Added try for the main loop actions
            current_filenames_in_watch = os.listdir(WATCH_FOLDER)
            new_zw_files = []
            for filename in current_filenames_in_watch:
                if filename.endswith(".zw") and filename not in seen_files:
                    new_zw_files.append(filename)

            for filename in new_zw_files:
                full_path = WATCH_FOLDER / filename # Use Path object
                print(f"\n🧪 New file detected: {filename}")

                valid, message = validate_zw_template(full_path)

                if valid:
                    print(f"  ✅ Validated: {message}")
                    dest_path = VALIDATED_FOLDER / filename # Use Path object
                    try:
                        shutil.copy(full_path, dest_path)
                        print(f"    Copied to: {dest_path.resolve()}")
                        append_log(f"✅ VALIDATED & COPIED: {filename} - {message}")
                    except Exception as e_copy:
                        print(f"    [ERROR] Could not copy {filename}: {e_copy}")
                        append_log(f"❌ ERROR COPYING: {filename} - {message} - Copy error: {e_copy}")
                else:
                    print(f"  ❌ Rejected: {message}")
                    append_log(f"❌ REJECTED: {filename} - {message}")

                seen_files.add(filename) # Add to seen after processing

            # Update seen_files for files that might have been removed
            current_seen_set = set(os.listdir(WATCH_FOLDER))
            files_removed_from_watch = seen_files - current_seen_set
            if files_removed_from_watch:
                seen_files = current_seen_set

        except Exception as e_loop: # Catch errors in the loop's main logic
            print(f"[ERROR] Watch loop iteration failed: {e_loop}")
            append_log(f"🔥 WATCHER ERROR: Loop iteration failed - {e_loop}")

        time.sleep(3)

def append_log(entry):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(RESEARCH_LOG, 'a', encoding='utf-8') as log: # Added encoding
            log.write(f"[{timestamp}] {entry}\n")
    except Exception as e_log_append:
        print(f"[ERROR] Failed to append to log {RESEARCH_LOG}: {e_log_append}")


if __name__ == "__main__":
    print("[*] Initializing ZW Import Watcher...")
    # Create directories if they don't exist
    try:
        WATCH_FOLDER.mkdir(parents=True, exist_ok=True)
        VALIDATED_FOLDER.mkdir(parents=True, exist_ok=True)
        RESEARCH_LOG_DIR.mkdir(parents=True, exist_ok=True) # Ensure research_notes dir exists
        print(f"[*] Ensured directories exist:\n    Watch: {WATCH_FOLDER}\n    Validated: {VALIDATED_FOLDER}\n    Log Dir: {RESEARCH_LOG_DIR}") # Pythonic newline
    except Exception as e_mkdir_main:
        print(f"[FATAL ERROR] Could not create watcher directories: {e_mkdir_main}. Exiting.")
        sys.exit(1) # Exit if basic setup fails

    try:
        watch_folder()
    except KeyboardInterrupt:
        print("\n[*] Watcher stopped by user (Ctrl+C).")
    except Exception as e_main_watch: # Catch any other unexpected errors from watch_folder
        print(f"[FATAL ERROR] Watcher failed unexpectedly: {e_main_watch}")
        append_log(f"💀 WATCHER CRASHED UNEXPECTEDLY: {e_main_watch}")
    finally:
        print("[*] ZW Import Watcher shut down.")
