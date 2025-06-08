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

def safe_eval(str_val, default_val):
    """Safely evaluates a string that should represent a tuple, list, or number."""
    if not isinstance(str_val, str):
        return default_val
    try:
        evaluated = eval(str_val)
        return evaluated
    except (SyntaxError, NameError, TypeError, ValueError) as e:
        print(f"    [!] Warning: Could not evaluate string '{str_val}' for attribute: {e}. Using default: {default_val}")
        return default_val

def parse_color(color_str_val, default_color=(0.8, 0.8, 0.8, 1.0)):
    if not isinstance(color_str_val, str):
        return default_color
    s = color_str_val.strip()
    if s.startswith("#"):
        hex_color = s.lstrip("#")
        try:
            if len(hex_color) == 6: # RRGGBB
                r, g, b = (int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
                return (r, g, b, 1.0)
            elif len(hex_color) == 8: # RRGGBBAA
                r, g, b, a = (int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4, 6))
                return (r, g, b, a)
        except ValueError: return default_color
        return default_color
    elif s.startswith("(") and s.endswith(")"):
        try:
            parts = [float(p.strip()) for p in s.strip("()").split(",")]
            if len(parts) == 3: return (parts[0], parts[1], parts[2], 1.0)
            if len(parts) == 4: return tuple(parts)
        except ValueError: return default_color
        return default_color
    return default_color

def handle_zw_object_creation(obj_attributes: dict, parent_bpy_obj=None):
    """
    Handles the creation of a Blender object based on ZW attributes.
    Optionally parents it to parent_bpy_obj.
    Returns the created Blender object reference or None.
    """
    if not bpy:
        print("[!] bpy not available. Skipping object creation.")
        return None

    obj_type = obj_attributes.get("TYPE")
    if not obj_type or not isinstance(obj_type, str):
        print(f"    [!] Warning: Missing or invalid 'TYPE' in ZW-OBJECT attributes: {obj_attributes}. Skipping.")
        return None

    obj_name = obj_attributes.get("NAME", obj_type) # Default name to type if not specified

    # Location: default to (0,0,0)
    location_str = obj_attributes.get("LOCATION", "(0,0,0)")
    location_tuple = safe_eval(location_str, (0,0,0))
    if not isinstance(location_tuple, tuple) or len(location_tuple) != 3:
        print(f"    [!] Warning: Invalid LOCATION format '{location_str}'. Defaulting to (0,0,0).")
        location_tuple = (0,0,0)

    # Scale: default to (1,1,1)
    scale_str = obj_attributes.get("SCALE", "(1,1,1)")
    # Handle single number scale as well as tuple
    if isinstance(scale_str, (int, float)): # Direct number like SCALE: 2.0
        scale_tuple = (float(scale_str), float(scale_str), float(scale_str))
    elif isinstance(scale_str, str): # String like SCALE: "(1,1,1)" or SCALE: "2.0"
        evaluated_scale = safe_eval(scale_str, (1,1,1))
        if isinstance(evaluated_scale, (int, float)):
            scale_tuple = (float(evaluated_scale), float(evaluated_scale), float(evaluated_scale))
        elif isinstance(evaluated_scale, tuple) and len(evaluated_scale) == 3:
            scale_tuple = evaluated_scale
        else: # Default if malformed tuple string
            print(f"    [!] Warning: Invalid SCALE format '{scale_str}'. Defaulting to (1,1,1).")
            scale_tuple = (1,1,1)
    else: # Default if not string or number
        print(f"    [!] Warning: Invalid SCALE type '{type(scale_str)}'. Defaulting to (1,1,1).")
        scale_tuple = (1,1,1)


    print(f"[*] Creating Blender object: TYPE='{obj_type}', NAME='{obj_name}', LOC={location_tuple}, SCALE={scale_tuple}")

    obj_type_lower = obj_type.lower()
    created_bpy_obj = None # Renamed from created_obj for clarity

    try:
        if obj_type_lower == "sphere":
            bpy.ops.mesh.primitive_uv_sphere_add(location=location_tuple)
        elif obj_type_lower == "cube":
            bpy.ops.mesh.primitive_cube_add(location=location_tuple)
        elif obj_type_lower == "plane":
            bpy.ops.mesh.primitive_plane_add(location=location_tuple)
        elif obj_type_lower == "cone":
            bpy.ops.mesh.primitive_cone_add(location=location_tuple)
        elif obj_type_lower == "cylinder":
            bpy.ops.mesh.primitive_cylinder_add(location=location_tuple)
        elif obj_type_lower == "torus":
            bpy.ops.mesh.primitive_torus_add(location=location_tuple)
        else:
            print(f"    [!] Warning: ZW object TYPE '{obj_type}' not recognized. Skipping creation.")
            return None

        created_bpy_obj = bpy.context.object
        if created_bpy_obj:
            created_bpy_obj.name = obj_name
            created_bpy_obj.scale = scale_tuple
            print(f"    ✅ Created and configured: {created_bpy_obj.name} (Type: {obj_type})")

            if parent_bpy_obj:
                # Deselect all, select child, then parent, then parent.
                bpy.ops.object.select_all(action='DESELECT')
                created_bpy_obj.select_set(True)
                parent_bpy_obj.select_set(True)
                bpy.context.view_layer.objects.active = parent_bpy_obj # Parent must be active
                try:
                    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True) # Keep world transform then parent
                    print(f"    Parented '{created_bpy_obj.name}' to '{parent_bpy_obj.name}'")
                except RuntimeError as e:
                    print(f"    [Error] Parenting failed for '{created_bpy_obj.name}' to '{parent_bpy_obj.name}': {e}")

            # --- Material Handling ---
            if hasattr(created_bpy_obj.data, 'materials'): # Check if object can have materials
                material_name_str = obj_attributes.get("MATERIAL")
                color_str = obj_attributes.get("COLOR")
                shading_str = obj_attributes.get("SHADING", "Smooth").lower() # Default to Smooth
                bsdf_data = obj_attributes.get("BSDF")

                obj_name_for_mat = created_bpy_obj.name # Use the actual object name for material default
                final_material_name = material_name_str or f"{obj_name_for_mat}_Mat"

                mat = bpy.data.materials.get(final_material_name)
                if not mat:
                    mat = bpy.data.materials.new(name=final_material_name)
                    print(f"    Created new material: {final_material_name}")
                else:
                    print(f"    Using existing material: {final_material_name}")

                mat.use_nodes = True
                nodes = mat.node_tree.nodes
                links = mat.node_tree.links

                principled_bsdf = nodes.get("Principled BSDF")
                if not principled_bsdf:
                    principled_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
                    principled_bsdf.location = (0,0)
                    print(f"    Created Principled BSDF node for {final_material_name}")

                material_output = nodes.get('Material Output')
                if not material_output:
                    material_output = nodes.new(type='ShaderNodeOutputMaterial')
                    material_output.location = (200,0)
                    print(f"    Created Material Output node for {final_material_name}")

                if principled_bsdf and material_output:
                    is_linked = False
                    for link_item in links: # Renamed link to link_item to avoid conflict
                        if link_item.from_node == principled_bsdf and link_item.from_socket == principled_bsdf.outputs.get("BSDF") and \
                           link_item.to_node == material_output and link_item.to_socket == material_output.inputs.get("Surface"):
                            is_linked = True
                            break
                    if not is_linked:
                        links.new(principled_bsdf.outputs["BSDF"], material_output.inputs["Surface"])
                        print(f"    Linked Principled BSDF to Material Output for {final_material_name}")

                base_color_set_by_bsdf = False
                if isinstance(bsdf_data, dict) and principled_bsdf:
                    print(f"    Applying BSDF properties for {final_material_name}: {bsdf_data}")
                    for key, value_any_type in bsdf_data.items():
                        bsdf_input_name = key.replace("_", " ").title()
                        if key.lower() == "alpha": bsdf_input_name = "Alpha"

                        if principled_bsdf.inputs.get(bsdf_input_name):
                            try:
                                if "Color" in bsdf_input_name and (isinstance(value_any_type, str) or isinstance(value_any_type, tuple)):
                                     parsed_c = parse_color(value_any_type if isinstance(value_any_type, str) else str(value_any_type))
                                     principled_bsdf.inputs[bsdf_input_name].default_value = parsed_c
                                     if bsdf_input_name == "Base Color": base_color_set_by_bsdf = True
                                     print(f"      Set BSDF.{bsdf_input_name} to {parsed_c}")
                                else:
                                    val_float = float(value_any_type)
                                    principled_bsdf.inputs[bsdf_input_name].default_value = val_float
                                    print(f"      Set BSDF.{bsdf_input_name} to {val_float}")
                            except Exception as e_bsdf:
                                print(f"      [Warning] Failed to set BSDF input {bsdf_input_name} with value {value_any_type}: {e_bsdf}")
                        else:
                            print(f"      [Warning] BSDF input '{bsdf_input_name}' (from ZW key '{key}') not found on Principled BSDF node.")

                if color_str and not base_color_set_by_bsdf and principled_bsdf:
                    parsed_color_val = parse_color(color_str) # Renamed variable
                    principled_bsdf.inputs["Base Color"].default_value = parsed_color_val
                    print(f"    Set Base Color to {parsed_color_val} for {final_material_name} (from COLOR attribute)")

                if created_bpy_obj.data.materials:
                    created_bpy_obj.data.materials[0] = mat
                else:
                    created_bpy_obj.data.materials.append(mat)
                print(f"    Assigned material '{final_material_name}' to object '{created_bpy_obj.name}'")

                bpy.ops.object.select_all(action='DESELECT')
                created_bpy_obj.select_set(True)
                bpy.context.view_layer.objects.active = created_bpy_obj
                if shading_str == "smooth":
                    bpy.ops.object.shade_smooth()
                    print(f"    Set shading to Smooth for '{created_bpy_obj.name}'")
                elif shading_str == "flat":
                    bpy.ops.object.shade_flat()
                    print(f"    Set shading to Flat for '{created_bpy_obj.name}'")
        else:
            print(f"    [!] Error: Object creation did not result in an active object (Type: {obj_type}).")
            return None

    except Exception as e:
        print(f"    [!] Error creating Blender object for TYPE '{obj_type}', NAME '{obj_name}': {e}")
        return None
    return created_bpy_obj


def process_zw_structure(data_dict: dict, parent_bpy_obj=None): # Renamed data to data_dict
    """
    Recursively processes the parsed ZW structure to find and create objects.
    Passes parent_bpy_obj for parenting.
    """
    if not isinstance(data_dict, dict):
        return

    for key, value in data_dict.items():
        current_bpy_object_for_children = None # Will hold the Blender obj created at this level

        # Case 1: ZW-OBJECT: { TYPE: Cube, NAME: MyCube ... }
        if key.upper() == "ZW-OBJECT" and isinstance(value, dict):
            obj_attributes = value
            current_bpy_object_for_children = handle_zw_object_creation(obj_attributes, parent_bpy_obj)

        # Case 2: ZW-OBJECT: Sphere (simple type string)
        elif key.upper() == "ZW-OBJECT" and isinstance(value, str):
            obj_attributes = {"TYPE": value}
            current_bpy_object_for_children = handle_zw_object_creation(obj_attributes, parent_bpy_obj)

        # Case 3: Key itself is an object type, e.g. Cube: { NAME: MyCube ... }
        elif key.lower() in ["sphere", "cube", "plane", "cone", "cylinder", "torus"] and isinstance(value, dict):
            obj_attributes = value.copy()
            obj_attributes["TYPE"] = key
            current_bpy_object_for_children = handle_zw_object_creation(obj_attributes, parent_bpy_obj)

        # After potential object creation, check for CHILDREN in its definition dict (value)
        # This applies if 'value' was the dict containing attributes, including CHILDREN.
        # This is relevant for Case 1 and Case 3 where 'value' is a dict.
        if isinstance(value, dict) and current_bpy_object_for_children: # Check if an object was created from this 'value'
            children_list = value.get("CHILDREN")
            if children_list and isinstance(children_list, list):
                print(f"[*] Processing CHILDREN for '{current_bpy_object_for_children.name}'...")
                for child_item_definition in children_list:
                    if isinstance(child_item_definition, dict):
                        # The child_item_definition is expected to be a ZW-OBJECT structure itself,
                        # e.g., {"ZW-OBJECT": {"TYPE": "Sphere", ...}} or directly {"TYPE": "Sphere", ...}
                        # process_zw_structure will handle these forms.
                        process_zw_structure(child_item_definition, parent_bpy_obj=current_bpy_object_for_children)
                    else:
                        print(f"    [!] Warning: Item in CHILDREN list is not a dictionary: {child_item_definition}")
            elif children_list is not None: # Exists but not a list
                 print(f"    [!] Warning: CHILDREN attribute for '{current_bpy_object_for_children.name}' is not a list: {type(children_list)}")


        # Recursive call for other nested structures (like ZW-NESTED-DETAILS or other general groups)
        # These groups don't create their own Blender objects to become parents, so pass original parent_bpy_obj
        elif isinstance(value, dict) and not current_bpy_object_for_children: # If no object was created at this key-value pair
            if key.upper() == "ZW-NESTED-DETAILS":
                print(f"[*] Processing ZW-NESTED-DETAILS (semantic parent link: {value.get('PARENT')})...")

            process_zw_structure(value, parent_bpy_obj=parent_bpy_obj) # Pass original parent


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
