

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

import datetime # Added for logging timestamp

# Corrected sys.path modification:
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.append(str(PROJECT_ROOT))

# Import the validator
from tools.intent_utils import validate_zw_intent_block
from zw_mcp.zw_parser import parse_zw, to_zw, prettify_zw

# Placeholder for BLENDER_EXECUTABLE_PATH
BLENDER_EXECUTABLE_PATH = "blender"

# --- Logging Setup ---
LOG_DIR = PROJECT_ROOT / "zw_mcp" / "logs"
LOG_FILE = LOG_DIR / "orbit_exec.log"

def ensure_log_dir_exists():
    LOG_DIR.mkdir(parents=True, exist_ok=True)

def log_orbit_event(message: str):
    ensure_log_dir_exists()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)
# --- End Logging Setup ---

def parse_zwx_file_and_extract_raw_intent(filepath: Path) -> tuple[str | None, dict, str | None]:
    try:
        content = filepath.read_text(encoding="utf-8")
    except FileNotFoundError:
        # No print here, caller will log
        return None, {}, None
    except Exception as e:
        # No print here, caller will log
        return None, {}, None

    parts = content.split("---", 1)
    first_part = parts[0].strip()
    payload_str = parts[1].strip() if len(parts) > 1 else ""
    raw_intent_str = None
    intent_dict = {}

    if "ZW-INTENT:" in first_part:
        raw_intent_str = first_part
        lines = first_part.strip().splitlines()
        for line in lines:
            if ":" in line:
                key, val = line.split(":", 1)
                intent_dict[key.strip()] = val.strip()
        if not payload_str and "ROUTE_FILE" not in intent_dict:
             # This warning can be logged if desired, or kept as print
             print("⚠️ Warning: No payload block found after ZW-INTENT and no ROUTE_FILE specified.")
    else:
        payload_str = content
    return raw_intent_str, intent_dict, payload_str


def route_to_blender(intent: dict, zw_payload: str, source_file_name: str): # Added source_file_name for logging
    print("[EngAIn-Orbit] Routing to Blender...")
    zw_payload_content = zw_payload if zw_payload is not None else ""
    with tempfile.NamedTemporaryFile("w", suffix=".zw", delete=False, encoding='utf-8') as temp:
        temp.write(zw_payload_content)
        temp_path = temp.name

    blender_adapter_path = str(PROJECT_ROOT / "zw_mcp" / "blender_adapter.py")

    try:

        subprocess.run([
            BLENDER_EXECUTABLE_PATH,
            "--background",
            "--python", blender_adapter_path,
            "--",
        "--input", temp_path
        ], check=True)

        log_orbit_event(f"✔ Routed: {source_file_name} → Blender")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Blender execution failed: {e}")
        log_orbit_event(f"❌ Execution FAILED: {source_file_name} → Blender - {e}")
    except FileNotFoundError:
        error_msg = f"Blender executable not found at '{BLENDER_EXECUTABLE_PATH}'."
        print(f"[ERROR] {error_msg} Please ensure it's installed and in PATH, or configure BLENDER_EXECUTABLE_PATH.")
        log_orbit_event(f"❌ Execution FAILED: {source_file_name} → Blender - {error_msg}")
    finally:
        Path(temp_path).unlink(missing_ok=True)


def route_to_godot(intent: dict, zw_payload: str, source_file_name: str): # Added source_file_name for logging
    # TODO: Implement Godot routing logic
    godot_message = "[EngAIn-Orbit] Routing to Godot not implemented yet."
    print(godot_message)
    log_orbit_event(f"🚧 Stubbed: {source_file_name} → Godot - Not implemented yet.")


def execute_orbit(zwx_file: Path):
    raw_intent_str, parsed_intent_dict, payload_str = parse_zwx_file_and_extract_raw_intent(zwx_file)

    source_file_name = str(zwx_file) # For logging

    if raw_intent_str is None and parsed_intent_dict == {} and payload_str is None:
        # This case implies a file read error in parse_zwx_file_and_extract_raw_intent
        # The error would have been printed by the original user code, let's log it too
        log_orbit_event(f"❌ File Error: Could not read or access {source_file_name}.")
        # Original prints are kept in parse_zwx_file_and_extract_raw_intent,
        # but they could be removed if logging is considered sufficient.
        # For now, to match user's code, let's assume the print happened, or we add one:
        # print(f"ERROR: File not found or could not be read: {source_file_name}")
        return

    current_intent_dict = parsed_intent_dict

    if raw_intent_str:
        validation_result = validate_zw_intent_block(raw_intent_str)
        if isinstance(validation_result, str):
            error_message = f"Validation FAILED: {source_file_name} - {validation_result}"
            print(f"[ZW-INTENT VALIDATION FAILED] {validation_result} for file {zwx_file}")
            log_orbit_event(f"❌ {error_message}")
            return
        current_intent_dict = validation_result
    elif not payload_str:
        error_message = f"No ZW-INTENT block and no ZW-PAYLOAD found in {source_file_name}."
        print(f"[ERROR] {error_message}")
        log_orbit_event(f"❌ Validation FAILED: {source_file_name} - No intent and no payload.")
        return

    target_system = current_intent_dict.get("TARGET_SYSTEM", "").lower()

    if not target_system:
        if payload_str and not raw_intent_str:
            print("[EngAIn-Orbit] Running direct ZW payload (no explicit ZW-INTENT block, defaulting to Blender)...")
            # Log for direct payload routing will be handled by route_to_blender
            route_to_blender(current_intent_dict, payload_str, source_file_name)
            return
        else:
            error_message = f"No TARGET_SYSTEM found in intent block: {source_file_name}"
            print(f"[ERROR] {error_message}")
            log_orbit_event(f"❌ Validation FAILED: {source_file_name} - {error_message}")
            return

    if not payload_str and "ROUTE_FILE" not in current_intent_dict:
        error_message = f"No ZW-PAYLOAD found for TARGET_SYSTEM '{target_system}' in {source_file_name} and no ROUTE_FILE specified."
        print(f"[ERROR] {error_message}")
        log_orbit_event(f"❌ Validation FAILED: {source_file_name} - {error_message}")
        return

    actual_payload_for_routing = payload_str if payload_str is not None else ""

    if target_system == "blender":
        route_to_blender(current_intent_dict, actual_payload_for_routing, source_file_name)
    elif target_system == "godot":
        route_to_godot(current_intent_dict, actual_payload_for_routing, source_file_name)
    else:
        error_message = f"Unknown TARGET_SYSTEM '{target_system}' in intent block for {source_file_name}."
        print(f"[ERROR] {error_message}")
        log_orbit_event(f"❌ Routing FAILED: {source_file_name} - {error_message}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EngAIn-Orbit ZWX Execution Router")
    parser.add_argument("zwx_file", type=Path, help="Path to the .zwx or .zw file to execute")
    # Optional: Add --no-log flag if desired
    # parser.add_argument("--no-log", action="store_true", help="Disable logging to orbit_exec.log")
    args = parser.parse_args()

    # Global flag for logging, can be controlled by CLI arg if added
    # ENABLE_LOGGING = not args.no_log if hasattr(args, 'no_log') else True
    # For now, logging is always on. If log_orbit_event is called, it logs.

    if not args.zwx_file.exists():
        # Log this critical startup error too
        ensure_log_dir_exists()  # Ensure dir exists before trying to log
        err_msg = f"File not found at startup: {args.zwx_file}"
        print(f"ERROR: {err_msg}")
        log_orbit_event(f"❌ Startup Error: {err_msg}")
        sys.exit(1)

    execute_orbit(args.zwx_file)

# ---- End of modified code for tools/engain_orbit.py ----
