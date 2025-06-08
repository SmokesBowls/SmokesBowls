# zw_mcp/blender_adapter.py
import sys
from pathlib import Path

# Attempt to import bpy, handling the case where the script is not run within Blender
try:
    import bpy
except ImportError:
    print("[!] bpy module not found. This script must be run within Blender's Python environment.")
    bpy = None # Define bpy as None so parts of the script can still be tested if needed

# Try to import parse_zw from zw_mcp.zw_parser
# This allows running the script directly if zw_mcp is in PYTHONPATH
# or if this script is in the parent directory of zw_mcp
try:
    from zw_parser import parse_zw
except ImportError:
    print("[!] Could not import 'parse_zw' from 'zw_mcp.zw_parser'.")
    # Attempt fallback for direct execution if script is in zw_mcp folder
    try:
        from zw_parser import parse_zw
    except ImportError:
        print("[!] Fallback import of 'parse_zw' also failed.")
        print("[!] Ensure 'zw_parser.py' is accessible and zw_mcp is in PYTHONPATH or script is run appropriately.")
        # Define a dummy parse_zw if it's absolutely critical for script structure,
        # though actual functionality will be missing.
        def parse_zw(text: str) -> dict:
            print("[!] Dummy parse_zw called. Real parsing will not occur.")
            return {}
        # Or, exit if parse_zw is essential for any execution path:
        # sys.exit(1)


ZW_INPUT_FILE_PATH = Path("zw_mcp/prompts/blender_scene.zw")

def handle_zw_object_creation(obj_type: str, obj_data: dict):
    """
    Handles the creation of a Blender object based on ZW type.
    obj_data is currently unused but reserved for future properties.
    """
    if not bpy:
        print("[!] bpy not available. Skipping object creation.")
        return

    print(f"[*] Attempting to create Blender object of ZW type: {obj_type}")

    # Basic mapping from ZW type string to Blender primitive creation ops
    # This will be very basic initially and can be expanded.
    obj_type_lower = obj_type.lower()

    try:
        if obj_type_lower == "sphere":
            bpy.ops.mesh.primitive_uv_sphere_add()
            print(f"    ✅ Created Sphere: {bpy.context.object.name}")
        elif obj_type_lower == "cube":
            bpy.ops.mesh.primitive_cube_add()
            print(f"    ✅ Created Cube: {bpy.context.object.name}")
        elif obj_type_lower == "plane":
            bpy.ops.mesh.primitive_plane_add()
            print(f"    ✅ Created Plane: {bpy.context.object.name}")
        elif obj_type_lower == "cone":
            bpy.ops.mesh.primitive_cone_add()
            print(f"    ✅ Created Cone: {bpy.context.object.name}")
        elif obj_type_lower == "cylinder":
            bpy.ops.mesh.primitive_cylinder_add()
            print(f"    ✅ Created Cylinder: {bpy.context.object.name}")
        elif obj_type_lower == "torus":
            bpy.ops.mesh.primitive_torus_add()
            print(f"    ✅ Created Torus: {bpy.context.object.name}")
        # Add more types as needed, e.g., "Text", "Light", "Camera"
        else:
            print(f"    [!] Warning: ZW object type '{obj_type}' not recognized or supported for direct creation.")
    except Exception as e:
        print(f"    [!] Error creating Blender object for type '{obj_type}': {e}")


def process_zw_structure(data: dict, parent_name: str = None):
    """
    Recursively processes the parsed ZW structure to find and create objects.
    """
    if not isinstance(data, dict):
        return

    for key, value in data.items():
        if key.upper() == "ZW-OBJECT" and isinstance(value, str): # e.g., ZW-OBJECT: Sphere
            # This is the case like "ZW-OBJECT: Sphere" where Sphere is the type
            # and the actual data for this object is expected in subsequent sibling keys
            # or in a nested dictionary if 'value' itself was a dict (handled below).
            # For now, we assume obj_data might be the parent dict containing this ZW-OBJECT key
            # or the data dict itself if the structure is `Sphere: { DETAILS: ... }`
            # This simple adapter will just use `value` as the type string.
            obj_type_str = value
            obj_specific_data = {} # Placeholder for now

            # Look for sibling keys that might contain the data for this object
            # This is a very basic assumption about structure.
            # A more robust parser might provide 'value' as a dictionary directly.
            if isinstance(data, dict): # parent_dict might be 'data'
                 # Check if the next level items are properties of this object
                 # This is a heuristic. If 'data' contains 'TITLE' and 'ZW-OBJECT',
                 # then 'TITLE' is not part of the object defined by 'ZW-OBJECT: Sphere'
                 # but if we have ZW-OBJECT: Sphere, NAME: MySphere, then NAME is a detail.
                 # The current zw_parser puts all sibling keys at the same level.
                 # Example:
                 # ZW-OBJECT: Sphere
                 #   NAME: MyStar -> This structure is handled by the recursive call.
                 #
                 # ZW-NARRATIVE-EVENT:
                 #   ZW-OBJECT: Sphere -> Here, data is the dict for ZW-NARRATIVE-EVENT
                 #   TITLE: MyTitle
                 #
                 # This needs refinement based on how zw_parser structures things like:
                 # ZW-OBJECT: Sphere
                 # NAME: MySphere
                 # SCALE: 2.0
                 # The current parser would make ZW-OBJECT, NAME, SCALE siblings.
                 # So, 'data' would be the parent dict.
                 # This part of the logic is tricky with the current parser output for flat ZW-OBJECT definitions.
                 # For now, we'll assume that if `key == "ZW-OBJECT"`, then `value` is the type string,
                 # and any *associated data* for that specific object is expected to be *within a dictionary
                 # that is the value of a key named after the object type*, e.g. Sphere: { NAME: ... }
                 # OR, the parser needs to be smarter to group them.
                 # The current parser output for the sample is:
                 # "ZW-OBJECT": "Sphere" (sibling to other ZW-OBJECT keys or ZW-NESTED-DETAILS)
                 # "Sphere": { "NAME": "CentralStar", ... } -> This is what we need to find.

                 # Let's assume the actual data for "Sphere" is in a key named "Sphere"
                 if obj_type_str in data and isinstance(data[obj_type_str], dict):
                     obj_specific_data = data[obj_type_str]
                 # else:
                     # print(f"[?] No specific data dict found for ZW-OBJECT type '{obj_type_str}' at this level. Creating basic object.")

            handle_zw_object_creation(obj_type_str, obj_specific_data)

        elif isinstance(value, dict):
            # If the key itself is a ZW-OBJECT type (e.g. "Sphere": { ...data... } )
            # This is a more direct way to define an object and its properties.
            # We'll consider common ZW object type names. This list can be expanded.
            common_object_types_for_keys = ["sphere", "cube", "plane", "cone", "cylinder", "torus"] # add more from handle_zw_object_creation
            if key.lower() in common_object_types_for_keys:
                 handle_zw_object_creation(key, value) # Key is type, value is data dict

            # Recursive call for nested structures
            new_parent_name = value.get("NAME", parent_name) if isinstance(value, dict) else parent_name
            process_zw_structure(value, new_parent_name)

        # Handle ZW-NESTED-DETAILS (basic pass-through for now)
        elif key.upper() == "ZW-NESTED-DETAILS" and isinstance(value, dict):
            # The 'PARENT' field inside ZW-NESTED-DETAILS is for semantic linking,
            # Blender parenting will require more advanced logic later.
            # For now, just process the contents of ZW-NESTED-DETAILS.
            print(f"[*] Processing ZW-NESTED-DETAILS (parent link: {value.get('PARENT')})...")
            process_zw_structure(value, value.get('PARENT', parent_name))


def run_blender_adapter():
    """
    Main function to run the Blender adapter.
    Reads a ZW file, parses it, and attempts to create Blender objects.
    """
    print("--- Starting ZW Blender Adapter ---")

    if not bpy:
        print("[X] Blender Python environment (bpy) not detected. Cannot proceed with Blender operations.")
        print("--- ZW Blender Adapter Finished (with errors) ---")
        return

    # Ensure we are in Object Mode
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Optional: Clear existing mesh objects for a clean slate (be careful with this)
    # bpy.ops.object.select_all(action='DESELECT')
    # bpy.ops.object.select_by_type(type='MESH')
    # bpy.ops.object.delete()
    # print("[*] Cleared existing mesh objects from the scene.")

    try:
        with open(ZW_INPUT_FILE_PATH, "r", encoding="utf-8") as f:
            zw_text_content = f.read()
        print(f"[*] Successfully read ZW file: {ZW_INPUT_FILE_PATH}")
    except FileNotFoundError:
        print(f"[X] Error: ZW input file not found at '{ZW_INPUT_FILE_PATH}'")
        print("--- ZW Blender Adapter Finished (with errors) ---")
        return
    except Exception as e:
        print(f"[X] Error reading ZW file '{ZW_INPUT_FILE_PATH}': {e}")
        print("--- ZW Blender Adapter Finished (with errors) ---")
        return

    if not zw_text_content.strip():
        print("[X] Error: ZW input file is empty.")
        print("--- ZW Blender Adapter Finished (with errors) ---")
        return

    try:
        print("[*] Parsing ZW text...")
        parsed_zw_data = parse_zw(zw_text_content)
        if not parsed_zw_data:
            print("[!] Warning: Parsed ZW data is empty. No objects will be created.")
        # print(f"[*] Parsed data (preview): {str(parsed_zw_data)[:500]}") # For debugging
    except Exception as e:
        print(f"[X] Error parsing ZW text: {e}")
        print("--- ZW Blender Adapter Finished (with errors) ---")
        return

    try:
        print("[*] Processing ZW structure for Blender object creation...")
        process_zw_structure(parsed_zw_data)
        print("[*] Finished processing ZW structure.")
    except Exception as e:
        print(f"[X] Error during ZW structure processing for Blender: {e}")
        print("--- ZW Blender Adapter Finished (with errors) ---")
        return

    print("--- ZW Blender Adapter Finished Successfully ---")

if __name__ == "__main__":
    # This script is intended to be run from within Blender's Python environment.
    # Running it directly with 'python3 blender_adapter.py' will likely show
    # "bpy module not found" errors, but the file reading and parsing
    # parts can be tested if zw_parser is available.

    # For direct testing of parsing without Blender:
    # if bpy is None:
    #     print("\n[*] bpy not found. Running in standalone test mode (no Blender operations)...")
    #     # We can still test the file reading and parsing part
    #     try:
    #         with open(ZW_INPUT_FILE_PATH, "r", encoding="utf-8") as f:
    #             zw_text_content = f.read()
    #         parsed_data = parse_zw(zw_text_content)
    #         print("[*] Standalone parsing successful. Parsed data:")
    #         import json
    #         print(json.dumps(parsed_data, indent=2))
    #         # process_zw_structure(parsed_data) # This would still try bpy ops
    #     except Exception as e:
    #         print(f"[!] Standalone test error: {e}")
    # else:
    #     run_blender_adapter()

    run_blender_adapter() # Standard execution path
```
