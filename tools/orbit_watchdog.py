# ---- Python code for tools/orbit_watchdog.py ----

import time
import subprocess
from pathlib import Path
import argparse
import datetime
import sys # For sys.exit

# --- Path Definitions ---
# To make this script runnable from anywhere, and robust to file system structure
try:
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
except IndexError:
    # Fallback if __file__ is not available or script is not in expected location
    # This might happen if the script is run in a context where __file__ is not tools/orbit_watchdog.py
    # For example, if it's executed as a string.
    # In a typical file-based execution, Path(__file__).resolve().parents[1] should work.
    print("Warning: Could not determine PROJECT_ROOT reliably using Path(__file__). Assuming current working directory or requiring manual adjustment if paths fail.", file=sys.stderr)
    PROJECT_ROOT = Path(".").resolve() # Default to current dir, might need user adjustment if issues arise


WATCH_DIR_NAME = "zw_drop_folder/validated_patterns"
EXECUTED_DIR_NAME = "zw_drop_folder/executed"
FAILED_DIR_NAME = "zw_drop_folder/failed"
LOG_DIR_NAME = "zw_mcp/logs"
LOG_FILE_NAME = "orbit_watchdog.log"
ENGAIN_ORBIT_SCRIPT_NAME = "tools/engain_orbit.py"

WATCH_DIR = PROJECT_ROOT / WATCH_DIR_NAME
EXECUTED_DIR = PROJECT_ROOT / EXECUTED_DIR_NAME
FAILED_DIR = PROJECT_ROOT / FAILED_DIR_NAME
LOG_DIR = PROJECT_ROOT / LOG_DIR_NAME
LOG_FILE = LOG_DIR / LOG_FILE_NAME
ENGAIN_ORBIT_SCRIPT = PROJECT_ROOT / ENGAIN_ORBIT_SCRIPT_NAME

POLL_INTERVAL = 3  # seconds

# --- Logging Setup ---
def ensure_logging_setup():
    LOG_DIR.mkdir(parents=True, exist_ok=True)

def log_watchdog_event(message: str):
    ensure_logging_setup()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Error writing to log file {LOG_FILE}: {e}", file=sys.stderr)

# --- Directory Setup ---
def ensure_directories():
    WATCH_DIR.mkdir(parents=True, exist_ok=True)
    EXECUTED_DIR.mkdir(parents=True, exist_ok=True)
    FAILED_DIR.mkdir(parents=True, exist_ok=True)
    ensure_logging_setup() # Also ensure log directory is ready
    print(f"Watchdog using PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"Watching: {WATCH_DIR}")
    print(f"Executed files will be moved to: {EXECUTED_DIR}")
    print(f"Failed files will be moved to: {FAILED_DIR}")
    print(f"Logging to: {LOG_FILE}")


# --- File Routing ---
def route_file(file_path: Path):
    log_watchdog_event(f"Processing: {file_path.name}")
    print(f"🛰️  Routing: {file_path.name}")

    if not ENGAIN_ORBIT_SCRIPT.exists():
        error_msg = f"EngAIn-Orbit script not found at {ENGAIN_ORBIT_SCRIPT}"
        print(f"❌ Error: {error_msg}")
        log_watchdog_event(f"Error: {error_msg} for file {file_path.name}")
        # Decide if to move to FAILED_DIR or leave in place if critical component missing
        # For now, let's move to failed.
        try:
            file_path.rename(FAILED_DIR / file_path.name)
            log_watchdog_event(f"Moved: {file_path.name} to {FAILED_DIR} due to missing EngAIn-Orbit script.")
        except Exception as e:
            log_watchdog_event(f"Error moving {file_path.name} to {FAILED_DIR}: {e}")
        return

    try:
        # Using python3 explicitly. If not available, FileNotFoundError will be caught.
        process = subprocess.run(
            ["python3", str(ENGAIN_ORBIT_SCRIPT), str(file_path)],
            capture_output=True, text=True, check=False # check=False to inspect returncode manually
        )

        if process.returncode == 0:
            print(f"✅ Success: {file_path.name}")
            log_watchdog_event(f"Routed: {file_path.name} → SUCCESS")
            file_path.rename(EXECUTED_DIR / file_path.name)
        else:
            print(f"❌ Failed: {file_path.name} (Return Code: {process.returncode})")
            if process.stdout:
                print(f"Stdout:\n{process.stdout}")
            if process.stderr:
                print(f"Stderr:\n{process.stderr}")
            log_watchdog_event(f"Failed: {file_path.name} → FAILED (Return Code: {process.returncode}). Stderr: {process.stderr.strip()}")
            file_path.rename(FAILED_DIR / file_path.name)

    except FileNotFoundError as e: # Catches if 'python3' or ENGAIN_ORBIT_SCRIPT (if it were directly executed) is not found
        error_msg = f"Execution error for {file_path.name}: {e}. Ensure 'python3' is in PATH and '{ENGAIN_ORBIT_SCRIPT}' is executable."
        print(f"❌ Error: {error_msg}")
        log_watchdog_event(f"Error: {error_msg}")
        try:
            file_path.rename(FAILED_DIR / file_path.name)
        except Exception as move_e:
            log_watchdog_event(f"Error moving {file_path.name} to {FAILED_DIR} after execution error: {move_e}")

    except OSError as e: # Broader OS errors during subprocess.run
        error_msg = f"OS error during execution for {file_path.name}: {e}."
        print(f"❌ Error: {error_msg}")
        log_watchdog_event(f"Error: {error_msg}")
        try:
            file_path.rename(FAILED_DIR / file_path.name)
        except Exception as move_e:
            log_watchdog_event(f"Error moving {file_path.name} to {FAILED_DIR} after OS error: {move_e}")

    except Exception as e: # Catch any other unexpected errors during routing
        error_msg = f"Unexpected error routing {file_path.name}: {e}"
        print(f"❌ Error: {error_msg}")
        log_watchdog_event(f"Error: {error_msg}")
        try:
            file_path.rename(FAILED_DIR / file_path.name)
        except Exception as move_e:
            log_watchdog_event(f"Error moving {file_path.name} to {FAILED_DIR} after unexpected error: {move_e}")


# --- Watch Loop ---
def watch_loop(once: bool):
    print(f"🔭 Watching for .zwx files in {WATCH_DIR.resolve()}")
    log_watchdog_event(f"Watchdog started. Watching: {WATCH_DIR}. Mode: {'once' if once else 'continuous'}.")

    seen_in_current_run = set() # For --once mode or single pass of continuous

    # In continuous mode, 'seen_in_current_run' acts to process each file once per watchdog startup.
    # If files are added while watchdog is running, they will be picked up.
    # If files are processed and moved, they won't be in WATCH_DIR anymore.
    # This 'seen' is more for ensuring a file isn't processed multiple times if it somehow remains
    # in WATCH_DIR across quick iterations of the loop before being moved.
    # Given files are moved, its primary role is for the --once scenario or clean startup.

    while True:
        try:
            zwx_files = list(WATCH_DIR.glob("*.zwx"))
        except Exception as e:
            print(f"Error accessing watch directory {WATCH_DIR}: {e}", file=sys.stderr)
            log_watchdog_event(f"Error accessing watch directory {WATCH_DIR}: {e}")
            if once: break
            time.sleep(POLL_INTERVAL)
            continue

        processed_this_iteration = False
        for file_path in zwx_files:
            if file_path.name not in seen_in_current_run:
                seen_in_current_run.add(file_path.name) # Add before processing
                route_file(file_path)
                processed_this_iteration = True

        if once:
            if not processed_this_iteration and not zwx_files:
                 print("No new .zwx files found in this run.")
            elif not processed_this_iteration and zwx_files: # Files were present but already seen
                 print("No new .zwx files to process in this run (all previously seen).")
            break  # Exit after one pass if --once is specified

        time.sleep(POLL_INTERVAL)

# --- Main Execution ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EngAIn-Orbit Watchdog: Monitors a directory for .zwx files and routes them.")
    parser.add_argument("--once", action="store_true", help="Run the check once and then exit.")
    args = parser.parse_args()

    try:
        ensure_directories()
        watch_loop(args.once)
    except KeyboardInterrupt:
        print("\n🐶 Watchdog peacefully put to sleep. Goodbye!")
        log_watchdog_event("Watchdog stopped by user (KeyboardInterrupt).")
        sys.exit(0)
    except Exception as e:
        # Catch-all for unexpected errors during startup or main loop setup
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        log_watchdog_event(f"Watchdog failed with unexpected error: {e}")
        sys.exit(1)

# ---- End of Python code ----
