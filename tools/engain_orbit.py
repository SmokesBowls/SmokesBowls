

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
        ensure_log_dir_exists() # Ensure dir exists before trying to log
        err_msg = f"File not found at startup: {args.zwx_file}"
        print(f"ERROR: {err_msg}")
        log_orbit_event(f"❌ Startup Error: {err_msg}")
        sys.exit(1)

    execute_orbit(args.zwx_file)

# ---- End of modified code for tools/engain_orbit.py ----

# Add zw_mcp to sys.path to allow direct import of zw_parser
# This assumes engain_orbit.py is in the root and zw_mcp is a subdirectory
sys.path.append(str(Path(__file__).parent.resolve() / "zw_mcp"))

try:
    from zw_parser import parse_zw, to_zw, prettify_zw
except ImportError:
    print("ERROR: Failed to import zw_parser. Ensure engain_orbit.py is in the project root.")
    sys.exit(1)

# Placeholder for BLENDER_EXECUTABLE_PATH
# Users might need to configure this. For CI/testing, a known path or env var would be used.
BLENDER_EXECUTABLE_PATH = "blender" # Assume blender is in PATH

def parse_zwx_file(filepath: Path) -> tuple[dict | None, str | None]:
    """
    Parses a .zwx file into ZW-INTENT (dictionary) and ZW-PAYLOAD (string).
    Handles ZWX (intent---payload) and direct ZW (pure payload) files.
    """
    try:
        content = filepath.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"ERROR: File not found: {filepath}")
        return None, None
    except Exception as e:
        print(f"ERROR: Could not read file {filepath}: {e}")
        return None, None

    parts = content.split("---", 1)
    first_part = parts[0].strip()
    explicit_payload = parts[1].strip() if len(parts) > 1 else None

    # Case 1: Clear ZWX format (ZW-INTENT block followed by --- and payload)
    if first_part.startswith("ZW-INTENT:") and explicit_payload is not None:
        print(f"INFO: Detected ZW-INTENT block and '---' separator. Processing as ZWX file: {filepath.name}")
        try:
            intent_dict_outer = parse_zw(first_part) # Parse the ZW-INTENT text
            intent_dict_inner = intent_dict_outer.get("ZW-INTENT")

            if not intent_dict_inner or not isinstance(intent_dict_inner, dict):
                print("ERROR: ZW-INTENT structure is malformed. 'ZW-INTENT:' key not found or its value is not a dictionary.")
                return None, explicit_payload # Return payload in case it's useful

            # Basic validation of essential intent fields (optional, but good practice)
            if not intent_dict_inner.get("TARGET_SYSTEM"):
                 print("WARNING: ZW-INTENT is missing 'TARGET_SYSTEM'. This might cause issues in processing.")

            return intent_dict_inner, explicit_payload
        except Exception as e:
            print(f"ERROR: Could not parse ZW-INTENT block from '{filepath.name}': {e}")
            return None, explicit_payload # Return payload in case it's useful

    # Case 2: No '---' separator, or no explicit payload after '---', or first part doesn't start with ZW-INTENT.
    # This means it's either a direct ZW payload file or a malformed ZWX file.
    else:
        if explicit_payload is None and first_part.startswith("ZW-INTENT:"):
            print(f"WARNING: File '{filepath.name}' starts with ZW-INTENT but is missing '---' separator and/or subsequent payload. Treating entire content as potential payload for a default intent.")

        print(f"INFO: Treating entire content of '{filepath.name}' as ZW-PAYLOAD and manufacturing a default intent for Blender.")
        # Assume the entire original content is the payload
        assumed_payload = content
        try:
            # Validate if the assumed payload is valid ZW
            parse_zw(assumed_payload) # This will raise an exception if not valid ZW

            # If valid, manufacture a default intent for Blender
            manufactured_intent = {
                "SOURCE": f"DirectZWFileOrMalformedZWX_{filepath.name}",
                "TARGET_SYSTEM": "blender", # Default target
                "ROUTE_FILE": "inline",
                "INTENT_TYPE": "ExecuteVisualSceneDescription_DirectOrMalformed"
            }
            print("INFO: Successfully parsed entire content as ZW. Proceeding with direct Blender payload and manufactured intent.")
            return manufactured_intent, assumed_payload
        except Exception as e_parse_payload:
            # If it's not valid ZW, then we can't process it as a direct payload.
            print(f"ERROR: Entire content of '{filepath.name}' could not be parsed as a direct ZW payload: {e_parse_payload}")
            return None, None # Cannot determine intent or valid payload

def process_intent(intent_data: dict, payload_text: str, zwx_filepath: Path) -> None:
    """
    Processes the intent and routes the payload accordingly.
    """
    if not intent_data:
        print("ERROR: No intent data to process.")
        return

    target_system_raw = intent_data.get("TARGET_SYSTEM")
    route_file_policy_raw = intent_data.get("ROUTE_FILE", "inline") # Default to inline

    # Strip potential quotes from string values coming from ZW parsing
    target_system = target_system_raw.strip('"') if isinstance(target_system_raw, str) else target_system_raw
    route_file_policy = route_file_policy_raw.strip('"') if isinstance(route_file_policy_raw, str) else route_file_policy_raw

    print(f"Intent: TARGET_SYSTEM='{target_system}', ROUTE_FILE='{route_file_policy}'")

    if target_system == "blender":
        if not payload_text:
            print("ERROR: ZW-INTENT targets Blender, but no ZW-PAYLOAD found in the .zwx file.")
            return

        # Write the ZW payload to a temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".zw", delete=False, encoding="utf-8") as tmp_payload_file:
            tmp_payload_file.write(payload_text)
            temp_payload_filepath = tmp_payload_file.name

        print(f"ZW Payload written to temporary file: {temp_payload_filepath}")

        blender_adapter_script_path = Path(__file__).parent / "zw_mcp" / "blender_adapter.py"

        if not blender_adapter_script_path.exists():
            print(f"ERROR: Blender adapter script not found at {blender_adapter_script_path}")
            Path(temp_payload_filepath).unlink(missing_ok=True)
            return

        # Command to run Blender with the adapter script and the temporary payload file
        # The '--' is crucial to separate Blender's own args from args for the Python script.
        command = [
            BLENDER_EXECUTABLE_PATH,
            "--background", # Run Blender in background (no UI)
            "--python", str(blender_adapter_script_path),
            "--", # Pass subsequent arguments to the Python script
            "--input", str(temp_payload_filepath) # Argument for blender_adapter.py
        ]

        # Optional: Add scene file if you want to load into a specific .blend
        # blend_file_path = intent_data.get("BLENDER_SCENE_FILE")
        # if blend_file_path:
        # command.insert(1, str(Path(blend_file_path).resolve())) # Insert after BLENDER_EXECUTABLE_PATH

        print(f"Executing Blender command: {' '.join(command)}")

        try:
            # It's often better to capture output for debugging
            result = subprocess.run(command, capture_output=True, text=True, check=False) # check=False to inspect output even on error
            print("\n--- Blender Output ---")
            print(result.stdout)
            if result.stderr:
                print("--- Blender Errors ---")
                print(result.stderr)
            if result.returncode == 0:
                print("Blender script executed successfully.")
            else:
                print(f"Blender script execution failed with code {result.returncode}.")

        except FileNotFoundError:
            print(f"ERROR: Blender executable not found at '{BLENDER_EXECUTABLE_PATH}'. Please configure it.")
        except Exception as e:
            print(f"ERROR: Failed to run Blender: {e}")
        finally:
            # Clean up the temporary file
            Path(temp_payload_filepath).unlink(missing_ok=True)
            print(f"Temporary payload file {temp_payload_filepath} removed.")

    elif target_system == "ollama":
        # Placeholder for Ollama integration
        # from zw_mcp.ollama_handler import query_ollama
        # print("INFO: TARGET_SYSTEM is 'ollama'. Processing with Ollama...")
        # combined_prompt = f"ZW-INTENT:\n{to_zw({'ZW-INTENT': intent_data})}\n\nZW-PAYLOAD:\n{payload_text if payload_text else ''}"
        # print(f"INFO: Sending combined prompt to Ollama:\n{prettify_zw(combined_prompt)}")
        # ollama_response_zw = query_ollama(combined_prompt)
        # if ollama_response_zw.startswith("ERROR:"):
        #     print(f"ERROR: Ollama query failed: {ollama_response_zw}")
        #     return
        # print(f"INFO: Ollama response (expected ZW for Blender):\n{prettify_zw(ollama_response_zw)}")
        # # Now, this response needs to be sent to Blender.
        # # This creates a recursive call pattern or a need for a more sophisticated state machine.
        # # For now, let's assume Ollama's output is a ZW payload for Blender.
        # temp_intent_for_blender = {
        #     "SOURCE": f"OllamaGenerated_from_{zwx_filepath.name}",
        #     "TARGET_SYSTEM": "blender",
        #     "ROUTE_FILE": "inline",
        #     "INTENT_TYPE": "ExecuteVisualSceneDescription_OllamaGenerated"
        # }
        # process_intent(temp_intent_for_blender, ollama_response_zw, zwx_filepath)
        print("INFO: Ollama target system processing is not fully implemented yet.")

    else:
        print(f"WARNING: Unknown TARGET_SYSTEM: '{target_system}'. No action taken.")


def main():
    parser = argparse.ArgumentParser(description="Engain Orbit: Process ZWX files for targeted execution.")
    parser.add_argument("zwx_file", help="Path to the .zwx file to process.")

    # Optional: Allow overriding Blender path via command line
    parser.add_argument("--blender-path", help="Path to the Blender executable.", default=None)

    args = parser.parse_args()

    global BLENDER_EXECUTABLE_PATH
    if args.blender_path:
        BLENDER_EXECUTABLE_PATH = args.blender_path
        print(f"INFO: Using Blender executable from command line: {BLENDER_EXECUTABLE_PATH}")
    else:
        # Here you could also check an environment variable if no command line arg is given
        # e.g. BLENDER_EXECUTABLE_PATH = os.environ.get("BLENDER_PATH", "blender")
        print(f"INFO: Using default Blender executable path: {BLENDER_EXECUTABLE_PATH} (ensure it's in PATH or set --blender-path)")


    zwx_filepath = Path(args.zwx_file)
    if not zwx_filepath.is_file():
        print(f"ERROR: ZWX file not found or is not a file: {zwx_filepath}")
        sys.exit(1)

    print(f"Processing ZWX file: {zwx_filepath.name}")
    intent_data, payload_text = parse_zwx_file(zwx_filepath)

    if intent_data is None and payload_text is None: # Critical error during parsing
        print(f"Could not parse ZWX file {zwx_filepath.name}. Aborting.")
        sys.exit(1)

    if intent_data is None and payload_text is not None :
        print(f"INFO: No ZW-INTENT block successfully parsed, but payload text is present.")
        # This case should ideally be handled by the improved fallback in parse_zwx_file.
        # If intent_data is still None here, it means the file was neither a valid ZWX
        # nor successfully treated as a direct ZW payload by the fallback logic.
        # However, if parse_zwx_file *did* return a manufactured intent for a direct ZW,
        # then intent_data would not be None.
        # This 'if' block might now be redundant or only catch very specific parsing failures.
        if not intent_data: # If intent is still None after parse_zwx_file
             print("WARNING: Could not determine a clear intent from the file. Manufacturing a default Blender intent as a last resort.")
             intent_data = { # Fallback intent
                 "SOURCE": f"DirectZWFile_Fallback_{zwx_filepath.name}",
                 "TARGET_SYSTEM": "blender", # Default assumption
                 "ROUTE_FILE": "inline",
                 "INTENT_TYPE": "ExecuteVisualSceneDescription_Fallback"
             }
             # It's crucial to also ensure payload_text is indeed the full content if we reach here
             # and parse_zwx_file failed to set it for a non-ZWX file.
             # However, parse_zwx_file's fallback logic is now more robust.

    if intent_data:
        process_intent(intent_data, payload_text, zwx_filepath)
    else:
        # This means parse_zwx_file returned (None, None) or (None, some_payload_that_couldnt_form_intent)
        print("ERROR: No valid ZW-INTENT data could be parsed or constructed. Cannot proceed.")
        sys.exit(1)

    print(f"\nFinished processing {zwx_filepath.name}")

if __name__ == "__main__":
    main()



