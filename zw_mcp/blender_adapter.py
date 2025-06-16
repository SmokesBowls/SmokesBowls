# zw_mcp/blender_adapter.py
import sys
import json  # For potential pretty printing if needed, not directly for to_zw
from pathlib import Path
import argparse
import math  # Added for math.radians
from mathutils import Vector, Euler  # For ZW-COMPOSE transforms

from zw_mcp.utils import safe_eval


def parse_color(value, default=(0.8, 0.8, 0.8, 1.0)):
    """Convert a color definition to a 4-tuple usable by Blender."""
    if isinstance(value, (list, tuple)) and len(value) in (3, 4):
        return tuple(float(v) for v in value[:4]) + (
            (1.0,) if len(value) == 3 else ()
        )
    return default

# Standardized Prefixes
P_INFO = "[ZW->Blender][INFO]"
P_WARN = "[ZW->Blender][WARN]"
P_ERROR = "[ZW->Blender][ERROR]"
P_SUCCESS = "[ZW->Blender][SUCCESS]"

# Attempt to import bpy, handling the case where the script is not run within Blender
try:
    import bpy
except ImportError:
    print(f"{P_ERROR} bpy module not found. This script must be run within Blender's Python environment.")
    bpy = None # Define bpy as None so parts of the script can still be tested if needed

# Define PROJECT_ROOT early
try:
    # This works if the script is run as a file and __file__ is defined
    PROJECT_ROOT = Path(__file__).resolve().parent.parent # Assuming this script is in zw_mcp, so parent.parent is project root
    print(f"[*] PROJECT_ROOT defined using __file__: {PROJECT_ROOT}")
except NameError:
    # Fallback if __file__ is not defined (e.g., running from Blender Text Editor)
    print("[!] Warning: __file__ not defined. Attempting fallback for PROJECT_ROOT.")
    if bpy: # Check if bpy is available
        blend_file_path = bpy.data.filepath
        if blend_file_path:
            PROJECT_ROOT = Path(blend_file_path).parent
            print(f"[*] PROJECT_ROOT defined using bpy.data.filepath (blend file's dir): {PROJECT_ROOT}")
        else:
            try:
                # Fallback: try to use the path of the text block itself, if available
                text_block_path = bpy.context.space_data.text.filepath if bpy.context.space_data and bpy.context.space_data.text else ""
                if text_block_path:
                    # If script is /path/to/project/zw_mcp/blender_adapter.py, parent.parent is /path/to/project
                    PROJECT_ROOT = Path(text_block_path).parent.parent
                    print(f"[*] PROJECT_ROOT defined using text_block_path (script's dir's parent's parent): {PROJECT_ROOT}")
                else: # Last resort
                    PROJECT_ROOT = Path(".").resolve()
                    print(f"[!] Warning: PROJECT_ROOT set to current working directory (bpy available, no paths found): {PROJECT_ROOT}")
            except AttributeError:
                 PROJECT_ROOT = Path(".").resolve()
                 print(f"[!] Warning: PROJECT_ROOT set to current working directory (AttributeError fallback): {PROJECT_ROOT}")
    else: # bpy is not available (e.g. testing script parts outside Blender)
        PROJECT_ROOT = Path(".").resolve()
        print(f"[!] Warning: bpy not available. PROJECT_ROOT set to current working directory: {PROJECT_ROOT}")

# Ensure necessary paths are in sys.path for imports.
# This script (blender_adapter.py) is in zw_mcp/.
# zw_parser.py is also in zw_mcp/.
# To use `from zw_parser import parse_zw`, the directory zw_mcp/ must be in sys.path.
# PROJECT_ROOT is assumed to be the parent of zw_mcp/.
if 'PROJECT_ROOT' in locals() and PROJECT_ROOT is not None:
    zw_mcp_dir = PROJECT_ROOT / "zw_mcp"
    if zw_mcp_dir.is_dir():
        if str(zw_mcp_dir) not in sys.path:
            sys.path.append(str(zw_mcp_dir))
            print(f"[*] Appended zw_mcp_dir to sys.path: {zw_mcp_dir}")
    else:
        # If zw_mcp_dir isn't found relative to PROJECT_ROOT, maybe PROJECT_ROOT is already zw_mcp
        # This can happen if __file__ points to blender_adapter.py and it's in PROJECT_ROOT/ (not common for this project)
        # Or if text_block_path was PROJECT_ROOT/zw_mcp/blender_adapter.py, then parent.parent made PROJECT_ROOT.
        # A simpler case: if this script is in zw_mcp, its own directory needs to be in path for direct import.
        # Path(__file__).parent should be zw_mcp.
        try:
            current_script_dir = Path(__file__).resolve().parent
            if str(current_script_dir) not in sys.path:
                 sys.path.append(str(current_script_dir))
                 print(f"[*] Appended current_script_dir to sys.path: {current_script_dir}")
        except NameError: # __file__ not defined
            # If __file__ is not defined, this path adjustment might be difficult.
            # The earlier PROJECT_ROOT logic tries to handle this.
            # If PROJECT_ROOT itself (e.g. /app) is added, `from zw_mcp.zw_parser` would be the import style.
            # Since we use `from zw_parser`, `zw_mcp` dir must be in path.
            # The PROJECT_ROOT definition tries to set it to /app.
            # So, /app/zw_mcp should be what we add.
             pass # Covered by zw_mcp_dir logic if PROJECT_ROOT is parent of zw_mcp

# Now, try importing parse_zw
try:
    from zw_parser import parse_zw
    print(f"[*] Successfully imported 'parse_zw'.")
except ImportError as e_final:
    print(f"[!!!] CRITICAL: Failed to import 'parse_zw' after sys.path modifications: {e_final}")
    print(f"    Current sys.path: {sys.path}")
    def parse_zw(text: str) -> dict: # Define dummy for script to not crash before argparse
        print("[!] Dummy parse_zw called due to CRITICAL import failure. Real parsing will not occur.")
        return {}

# Imports for zw_mesh utilities needed by ZW-COMPOSE (specifically material override)
APPLY_ZW_MATERIAL_FUNC = None
ZW_MESH_UTILS_IMPORTED = False
try:
    # Package style import
    from zw_mcp.zw_mesh import apply_material as imported_apply_material
    APPLY_ZW_MATERIAL_FUNC = imported_apply_material
    ZW_MESH_UTILS_IMPORTED = True
    print("Successfully imported apply_material from zw_mcp.zw_mesh.")
except ImportError:
    try:
        # Relative import when running from within package
        from .zw_mesh import apply_material as imported_apply_material
        APPLY_ZW_MATERIAL_FUNC = imported_apply_material
        ZW_MESH_UTILS_IMPORTED = True
        print("Successfully imported apply_material from .zw_mesh.")
    except Exception:
        try:
            # Fallback for direct execution from repo root
            from zw_mesh import apply_material as imported_apply_material
            APPLY_ZW_MATERIAL_FUNC = imported_apply_material
            ZW_MESH_UTILS_IMPORTED = True
            print("Successfully imported apply_material from zw_mesh (script directory).")
        except ImportError as e_direct:
            print(f"All import attempts for zw_mesh.apply_material failed: {e_direct}")
            def APPLY_ZW_MATERIAL_FUNC(obj, material_def):
                print("[Critical Error] zw_mesh.apply_material was not imported. Cannot apply material override in ZW-COMPOSE.")

ZW_INPUT_FILE_PATH = Path("zw_mcp/prompts/blender_scene.zw")  # Default, can be overridden by args
# Holds the currently processed ZW file path during execution
current_zw_input_file = None


# --- Utility Functions ---

def get_or_create_collection(name: str, parent_collection=None):
    """Retrieve or create a Blender collection by name."""
    if not bpy:
        return None

    if not name:
        return bpy.context.scene.collection

    parent = parent_collection or bpy.context.scene.collection
    collection = bpy.data.collections.get(name)
    if not collection:
        collection = bpy.data.collections.new(name)
        parent.children.link(collection)
        print(f"{P_INFO} Created collection '{name}' under '{parent.name}'")
    elif parent not in collection.users_collection:
        try:
            parent.children.link(collection)
        except Exception:
            pass
    return collection

def handle_zw_object_creation(obj_data: dict, parent_bpy_obj=None):
    """Create a Blender object from a ZW-OBJECT definition."""
    if not bpy:
        return None

    if not isinstance(obj_data, dict):
        print(f"{P_WARN} ZW-OBJECT data should be a dict, got {type(obj_data)}")
        return None

    obj_type = str(obj_data.get("TYPE", "Cube")).strip('"\' ').lower()
    obj_name = str(obj_data.get("NAME", f"ZW_{obj_type}")).strip('"\' ')

    loc = safe_eval(obj_data.get("LOCATION", "(0,0,0)"), (0, 0, 0))
    rot_deg = safe_eval(obj_data.get("ROTATION", "(0,0,0)"), (0, 0, 0))
    scale_val = safe_eval(obj_data.get("SCALE", "(1,1,1)"), (1, 1, 1))
    if isinstance(scale_val, (int, float)):
        scale = (float(scale_val), float(scale_val), float(scale_val))
    else:
        scale = tuple(scale_val)

    # Create primitive based on type
    primitive_func = {
        "cube": bpy.ops.mesh.primitive_cube_add,
        "sphere": bpy.ops.mesh.primitive_uv_sphere_add,
        "plane": bpy.ops.mesh.primitive_plane_add,
        "cone": bpy.ops.mesh.primitive_cone_add,
        "cylinder": bpy.ops.mesh.primitive_cylinder_add,
        "torus": bpy.ops.mesh.primitive_torus_add,
        "grid": bpy.ops.mesh.primitive_grid_add,
        "monkey": bpy.ops.mesh.primitive_monkey_add,
    }.get(obj_type, bpy.ops.mesh.primitive_cube_add)

    primitive_func(location=loc)
    new_obj = bpy.context.active_object
    if not new_obj:
        print(f"{P_ERROR} Failed to create object of type '{obj_type}'.")
        return None

    new_obj.name = obj_name
    new_obj.scale = scale
    new_obj.rotation_euler = Euler([math.radians(a) for a in rot_deg], 'XYZ')
    new_obj["ZW_TYPE"] = obj_type.capitalize()

    # Material handling
    material_name = obj_data.get("MATERIAL")
    color_def = obj_data.get("COLOR")
    bsdf_dict = obj_data.get("BSDF", {}) if isinstance(obj_data.get("BSDF"), dict) else {}
    if material_name or color_def or bsdf_dict:
        mat_name = material_name or f"{new_obj.name}_Material"
        mat = bpy.data.materials.get(mat_name)
        if not mat:
            mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        bsdf = nodes.get("Principled BSDF")
        if not bsdf:
            bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
            out_node = nodes.get('Material Output') or nodes.new('ShaderNodeOutputMaterial')
            links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])

        for k, v in bsdf_dict.items():
            key = k.replace("_", " ").title()
            if key in bsdf.inputs:
                if "Color" in key:
                    bsdf.inputs[key].default_value = parse_color(str(v), bsdf.inputs[key].default_value)
                else:
                    try:
                        bsdf.inputs[key].default_value = float(v)
                    except Exception:
                        pass

        if color_def and 'Base Color' not in bsdf_dict:
            bsdf.inputs['Base Color'].default_value = parse_color(color_def, bsdf.inputs['Base Color'].default_value)

        if new_obj.data.materials:
            new_obj.data.materials[0] = mat
        else:
            new_obj.data.materials.append(mat)

    shading = str(obj_data.get("SHADING", "Smooth")).lower()
    if shading == "flat":
        bpy.ops.object.shade_flat()
    else:
        bpy.ops.object.shade_smooth()

    if parent_bpy_obj:
        try:
            new_obj.parent = parent_bpy_obj
            bpy.ops.object.select_all(action='DESELECT')
            new_obj.select_set(True)
            parent_bpy_obj.select_set(True)
            bpy.context.view_layer.objects.active = parent_bpy_obj
            bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        except Exception as e:
            print(f"{P_WARN} Failed to parent '{new_obj.name}' to '{parent_bpy_obj.name}': {e}")

    return new_obj

# --- New ZW-METADATA Handler ---
def handle_zw_metadata_block(metadata_data: dict, target_obj_name: str = None):
    if not bpy: return

    target_name = target_obj_name or metadata_data.get("TARGET")
    if not target_name:
        print("  [Warning] ZW-METADATA: No TARGET specified and no target_obj_name passed. Skipping.")
        return

    target_obj = bpy.data.objects.get(target_name)
    if not target_obj:
        print(f"  [Warning] ZW-METADATA: Target object '{target_name}' not found. Skipping.")
        return

    print(f"  Processing ZW-METADATA for: {target_obj.name}")
    for key, value in metadata_data.items():
        if key == "TARGET": continue # Already used
        try:
            if isinstance(value, (list, dict)):
                target_obj[f"ZW_{key.upper()}"] = json.dumps(value)
            elif isinstance(value, (str, int, float, bool)):
                 target_obj[f"ZW_{key.upper()}"] = value # Store simple types directly
            else: # Attempt to convert to string if unknown type
                target_obj[f"ZW_{key.upper()}"] = str(value)
            print(f"    Set custom property ZW_{key.upper()} on {target_obj.name}")
        except Exception as e:
            print(f"    [Error] Failed to set custom property ZW_{key.upper()} on {target_obj.name}: {e}")

# --- New ZW-COMPOSE-TEMPLATE Handler ---
def handle_zw_compose_template_block(template_data: dict):
    if not bpy: return
    template_name = template_data.get("NAME", "UnnamedZWTemplate")
    print(f"  Storing ZW-COMPOSE-TEMPLATE: {template_name}")

    # Store as Blender Text block
    text_block_name = f"ZW_Template_{template_name}"
    text_block = bpy.data.texts.get(text_block_name)
    if not text_block:
        text_block = bpy.data.texts.new(name=text_block_name)

    try:
        template_json_string = json.dumps(template_data, indent=2)
        text_block.from_string(template_json_string)
        print(f"    Stored template '{template_name}' in Text block '{text_block_name}'.")

        # Store as Scene custom property (for easier access by other scripts if needed, or as a flag)
        scene_prop_name = f"ZW_TEMPLATE_{template_name.upper()}"
        bpy.context.scene[scene_prop_name] = template_json_string # Storing full JSON string
        print(f"    Stored template '{template_name}' in Scene custom property '{scene_prop_name}'.")
    except Exception as e:
        print(f"    [Error] Failed to store ZW-COMPOSE-TEMPLATE '{template_name}': {e}")

# --- New Integrated ZW-MESH Handler ---
def handle_zw_mesh_block(mesh_data: dict, current_bpy_collection: bpy.types.Collection):
    if not bpy: return None
    mesh_name = mesh_data.get("NAME", "UnnamedZWMesh")
    print(f"  Processing ZW-MESH (integrated): {mesh_name}")

    base_type = mesh_data.get("TYPE", "cube").lower()
    params = mesh_data.get("PARAMS", {})

    # Create base primitive
    if base_type == "cube":
        bpy.ops.mesh.primitive_cube_add(size=float(params.get("SIZE", 1.0)))
    elif base_type == "ico_sphere":
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=int(params.get("SUBDIVISIONS", 2)),
            radius=float(params.get("RADIUS", 1.0)) )
    elif base_type == "cylinder":
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=int(params.get("VERTICES", 32)),
            radius=float(params.get("RADIUS", 1.0)),
            depth=float(params.get("DEPTH", 2.0)) )
    elif base_type == "cone":
        bpy.ops.mesh.primitive_cone_add(
            vertices=int(params.get("VERTICES", 32)),
            radius1=float(params.get("RADIUS1", params.get("RADIUS", 1.0))),
            depth=float(params.get("DEPTH", 2.0)) )
    elif base_type == "plane":
        bpy.ops.mesh.primitive_plane_add(size=float(params.get("SIZE", 2.0)))
    else:
        print(f"    [Warning] Unknown ZW-MESH base TYPE '{base_type}'. Defaulting to Cube.")
        bpy.ops.mesh.primitive_cube_add(size=1.0)

    mesh_obj = bpy.context.active_object
    if not mesh_obj:
        print(f"    [Error] Failed to create base primitive for ZW-MESH '{mesh_name}'.")
        return None
    mesh_obj.name = mesh_name

    # Apply material properties
    material_def = mesh_data.get("MATERIAL")
    if isinstance(material_def, dict):
        mat_name = material_def.get("NAME", f"{mesh_name}_Material")
        mat = bpy.data.materials.get(mat_name)
        if not mat: mat = bpy.data.materials.new(name=mat_name)
        mesh_obj.data.materials.append(mat)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if not bsdf:
            bsdf = mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
            # Link to output if it's a new BSDF
            output_node = mat.node_tree.nodes.get('Material Output')
            if not output_node: output_node = mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
            mat.node_tree.links.new(bsdf.outputs['BSDF'], output_node.inputs['Surface'])

        if "BASE_COLOR" in material_def: bsdf.inputs["Base Color"].default_value = parse_color(material_def["BASE_COLOR"])
        if "EMISSION_STRENGTH" in material_def: bsdf.inputs["Emission Strength"].default_value = float(material_def["EMISSION_STRENGTH"]) # Legacy name
        elif "EMISSION" in material_def: bsdf.inputs["Emission Strength"].default_value = float(material_def["EMISSION"])
        if "EMISSION_COLOR" in material_def: bsdf.inputs["Emission Color"].default_value = parse_color(material_def["EMISSION_COLOR"])
        if "ROUGHNESS" in material_def: bsdf.inputs["Roughness"].default_value = float(material_def["ROUGHNESS"])
        if "METALLIC" in material_def: bsdf.inputs["Metallic"].default_value = float(material_def["METALLIC"])
        if "TRANSMISSION" in material_def: bsdf.inputs["Transmission"].default_value = float(material_def["TRANSMISSION"])
        if "ALPHA" in material_def: bsdf.inputs["Alpha"].default_value = float(material_def["ALPHA"])
        if "SPECULAR" in material_def: bsdf.inputs["Specular IOR Level"].default_value = float(material_def["SPECULAR"]) # Assuming SPECULAR means IOR Level for Principled

    # Apply Metadata (if any)
    metadata_dict = mesh_data.get("METADATA")
    if isinstance(metadata_dict, dict):
        handle_zw_metadata_block(metadata_dict, target_obj_name=mesh_obj.name)

    # Link to collection
    explicit_coll_name = mesh_data.get("COLLECTION")
    target_collection = current_bpy_collection
    if explicit_coll_name:
        target_collection = get_or_create_collection(explicit_coll_name, bpy.context.scene.collection)

    current_obj_collections = [c for c in mesh_obj.users_collection]
    for c in current_obj_collections: c.objects.unlink(mesh_obj) # Unlink from default
    if mesh_obj.name not in target_collection.objects: target_collection.objects.link(mesh_obj)
    print(f"    Linked '{mesh_obj.name}' to collection '{target_collection.name}'")

    print(f"    ✅ Successfully created ZW-MESH (integrated): {mesh_name}")
    return mesh_obj


# --- Stub Handlers for unimplemented ZW blocks ---
def handle_zw_light_block(value, current_bpy_collection=None):
    """Stub for future ZW-LIGHT implementation."""
    print(f"{P_INFO} [Stub] Skipping ZW-LIGHT block.")

def handle_zw_function_block(value):
    """Stub for future ZW-FUNCTION implementation."""
    print(f"{P_INFO} [Stub] Skipping ZW-FUNCTION block.")

def handle_zw_driver_block(value):
    """Stub for future ZW-DRIVER implementation."""
    print(f"{P_INFO} [Stub] Skipping ZW-DRIVER block.")

def handle_zw_animation_block(value):
    """Stub for future ZW-ANIMATION implementation."""
    print(f"{P_INFO} [Stub] Skipping ZW-ANIMATION block.")

def handle_zw_camera_block(value, current_bpy_collection=None):
    """Stub for future ZW-CAMERA implementation."""
    print(f"{P_INFO} [Stub] Skipping ZW-CAMERA block.")

def handle_zw_stage_block(value):
    """Stub for future ZW-STAGE implementation."""
    print(f"{P_INFO} [Stub] Skipping ZW-STAGE block.")




# --- Main Processing Logic ---
def process_zw_structure(data_dict: dict, parent_bpy_obj=None, current_bpy_collection=None):
    if not bpy: return
    if current_bpy_collection is None: current_bpy_collection = bpy.context.scene.collection
    if not isinstance(data_dict, dict): return

    for key, value in data_dict.items():

        created_bpy_object_for_current_zw_object = None
        obj_attributes_for_current_zw_object = None
        target_collection_for_this_object = current_bpy_collection

        if key.upper().startswith("ZW-COLLECTION"):
            collection_name_raw = key.split(":", 1)[1].strip() if ":" in key else key.replace("ZW-COLLECTION", "").strip()
            collection_name = collection_name_raw.strip('"\' ')

        # Convert key to uppercase for case-insensitive matching of top-level ZW blocks
        zw_block_type = key.upper()

        if zw_block_type.startswith("ZW-COLLECTION"): # Handles ZW-COLLECTION: Name format
            collection_name = key.split(":", 1)[1].strip() if ":" in key else key.replace("ZW-COLLECTION", "").strip()

            if not collection_name: collection_name = "Unnamed_ZW_Collection"
            print(f"{P_INFO} Processing ZW-COLLECTION block: '{collection_name}' under '{current_bpy_collection.name}'")
            block_bpy_collection = get_or_create_collection(collection_name, parent_collection=current_bpy_collection)
            if isinstance(value, dict): # Process children within this new collection context
                process_zw_structure(value, parent_bpy_obj=parent_bpy_obj, current_bpy_collection=block_bpy_collection)
            continue

        elif key.upper() == "ZW-FUNCTION":
            fn_name = str(value.get('NAME', 'Unnamed Function') if isinstance(value, dict) else 'Unnamed Function').strip('"\' ')
            if isinstance(value, dict):
                print(f"{P_INFO} Processing ZW-FUNCTION block: '{fn_name}'")
                handle_zw_function_block(value) # Assumed exists or will be added
            else: print(f"{P_WARN} ZW-FUNCTION value is not a dictionary: {value}")
            continue
        elif key.upper() == "ZW-DRIVER":
            drv_name = str(value.get('NAME', 'Unnamed Driver') if isinstance(value, dict) else 'Unnamed Driver').strip('"\' ')
            if isinstance(value, dict):
                print(f"{P_INFO} Processing ZW-DRIVER block: '{drv_name}'")
                handle_zw_driver_block(value)
            else: print(f"{P_WARN} ZW-DRIVER value is not a dictionary: {value}")
            continue
        elif key.upper() == "ZW-ANIMATION":
            anim_name = str(value.get('NAME', 'UnnamedAnimation') if isinstance(value, dict) else 'UnnamedAnimation').strip('"\' ')
            if isinstance(value, dict):
                print(f"    {P_INFO} Processing ZW-ANIMATION block: '{anim_name}'")
                handle_zw_animation_block(value)
            else: print(f"    {P_WARN} Value for 'ZW-ANIMATION' key is not a dictionary. Value: {value}")
            continue
        elif key.upper() == "ZW-CAMERA":
            cam_name = str(value.get('NAME', 'UnnamedCamera') if isinstance(value, dict) else 'UnnamedCamera').strip('"\' ')
            if isinstance(value, dict):
                print(f"    {P_INFO} Processing ZW-CAMERA block for: '{cam_name}'")
                handle_zw_camera_block(value, current_bpy_collection)
            else: print(f"    {P_WARN} Value for 'ZW-CAMERA' key is not a dictionary. Value: {value}")
            continue
        elif key.upper() == "ZW-LIGHT":
            light_name = str(value.get('NAME', 'UnnamedLight') if isinstance(value, dict) else 'UnnamedLight').strip('"\' ')
            if isinstance(value, dict):
                print(f"    {P_INFO} Processing ZW-LIGHT block for: '{light_name}'")
                handle_zw_light_block(value, current_bpy_collection)
            else: print(f"    {P_WARN} Value for 'ZW-LIGHT' key is not a dictionary. Value: {value}")
            continue
        elif key.upper() == "ZW-STAGE":
            stage_name = str(value.get('NAME', 'UnnamedStage') if isinstance(value, dict) else 'UnnamedStage').strip('"\' ')
            if isinstance(value, dict):
                print(f"    {P_INFO} Processing ZW-STAGE block: '{stage_name}'")
                handle_zw_stage_block(value)
            else: print(f"    {P_WARN} Value for 'ZW-STAGE' key is not a dictionary. Value: {value}")
            continue

        # Object creation from ZW-OBJECT or shorthand type keys
        key_type_candidate = key.strip('"\' ').strip().title()
        if key.upper() == "ZW-OBJECT":
            if isinstance(value, dict): obj_attributes_for_current_zw_object = value
            elif isinstance(value, str): obj_attributes_for_current_zw_object = {"TYPE": value.strip('"\' ')} # Strip here too
        elif key_type_candidate in ["Sphere", "Cube", "Plane", "Cone", "Cylinder", "Torus", "Grid", "Monkey"] and isinstance(value, dict):
            obj_attributes_for_current_zw_object = value.copy()
            obj_attributes_for_current_zw_object["TYPE"] = key_type_candidate

        if obj_attributes_for_current_zw_object:
            created_bpy_object_for_current_zw_object = handle_zw_object_creation(obj_attributes_for_current_zw_object, parent_bpy_obj)
            if created_bpy_object_for_current_zw_object:
                explicit_collection_name_raw = obj_attributes_for_current_zw_object.get("COLLECTION")
                if isinstance(explicit_collection_name_raw, str):
                    explicit_collection_name_stripped = explicit_collection_name_raw.strip('"\' ')
                    if explicit_collection_name_stripped:
                        target_collection_for_this_object = get_or_create_collection(explicit_collection_name_stripped, parent_collection=bpy.context.scene.collection)

                if target_collection_for_this_object and target_collection_for_this_object != created_bpy_object_for_current_zw_object.users_collection[0]: # Check if not already in it
                    for coll in created_bpy_object_for_current_zw_object.users_collection:
                        coll.objects.unlink(created_bpy_object_for_current_zw_object)
                    target_collection_for_this_object.objects.link(created_bpy_object_for_current_zw_object)
                    print(f"    {P_INFO} Linked '{created_bpy_object_for_current_zw_object.name}' to collection '{target_collection_for_this_object.name}'")

                children_list = obj_attributes_for_current_zw_object.get("CHILDREN")
                if children_list and isinstance(children_list, list):
                    print(f"{P_INFO} Processing CHILDREN for '{created_bpy_object_for_current_zw_object.name}' in collection '{target_collection_for_this_object.name}'")
                    for child_item_definition in children_list:
                        if isinstance(child_item_definition, dict):
                            process_zw_structure(child_item_definition,
                                                 parent_bpy_obj=created_bpy_object_for_current_zw_object,
                                                 current_bpy_collection=target_collection_for_this_object)
                        else: print(f"    {P_WARN} Item in CHILDREN list is not a dictionary: {child_item_definition}")
                elif children_list is not None: print(f"    {P_WARN} CHILDREN attribute for an object is not a list: {type(children_list)}")
            continue
        elif isinstance(value, dict): # Fallback for other nested structures
            if key.upper() == "ZW-NESTED-DETAILS":  # Example of a specific nested block type
                parent_link = value.get('PARENT', 'None')
                print(f"{P_INFO} Processing ZW-NESTED-DETAILS (semantic parent link: {parent_link}). Using collection '{current_bpy_collection.name}'")


        # Specific ZW block handlers
        if zw_block_type == "ZW-INTENT":
            print(f"  [INFO] Encountered ZW-INTENT block ('{key}'). This block is for orchestrators and will be ignored by blender_adapter.py.")
            continue # or pass
        elif zw_block_type == "ZW-OBJECT":
            if isinstance(value, dict):
                handle_zw_object_creation(value, parent_bpy_obj=parent_bpy_obj) # Assuming it handles its own collection logic based on its attributes
            else: print(f"    [Warning] Value for 'ZW-OBJECT' key is not a dictionary. Value: {value}")
            continue
        elif zw_block_type == "ZW-MESH": # Uses the new integrated handler
            if isinstance(value, dict):
                handle_zw_mesh_block(value, current_bpy_collection)
            else: print(f"    [Warning] Value for 'ZW-MESH' key is not a dictionary. Value: {value}")
            continue
        elif zw_block_type == "ZW-FUNCTION":
            if isinstance(value, dict): handle_zw_function_block(value)
            else: print(f"[!] Warning: ZW-FUNCTION value is not a dictionary: {value}")
            continue
        elif zw_block_type == "ZW-DRIVER":
            if isinstance(value, dict): handle_zw_driver_block(value)
            else: print(f"[!] Warning: ZW-DRIVER value is not a dictionary: {value}")
            continue
        elif zw_block_type == "ZW-ANIMATION":
            if isinstance(value, dict): handle_zw_animation_block(value)
            else: print(f"    [Warning] Value for 'ZW-ANIMATION' key is not a dictionary. Value: {value}")
            continue
        elif zw_block_type == "ZW-CAMERA":
            if isinstance(value, dict): handle_zw_camera_block(value, current_bpy_collection)
            else: print(f"    [Warning] Value for 'ZW-CAMERA' key is not a dictionary. Value: {value}")
            continue
        elif zw_block_type == "ZW-LIGHT":
            if isinstance(value, dict): handle_zw_light_block(value, current_bpy_collection)
            else: print(f"    [Warning] Value for 'ZW-LIGHT' key is not a dictionary. Value: {value}")
            continue
        elif zw_block_type == "ZW-STAGE":
            if isinstance(value, dict): handle_zw_stage_block(value) # Assumes stage handles its own object targeting
            else: print(f"    [Warning] Value for 'ZW-STAGE' key is not a dictionary. Value: {value}")
            continue
        elif zw_block_type == "ZW-METADATA": # Standalone metadata block
            if isinstance(value, dict): handle_zw_metadata_block(value) # Target is inside 'value'
            else: print(f"    [Warning] Value for 'ZW-METADATA' key is not a dictionary. Value: {value}")
            continue
        elif zw_block_type == "ZW-COMPOSE-TEMPLATE":
            if isinstance(value, dict): handle_zw_compose_template_block(value)
            else: print(f"    [Warning] Value for 'ZW-COMPOSE-TEMPLATE' key is not a dictionary. Value: {value}")
            continue
        elif zw_block_type == "ZW-COMPOSE":
            if isinstance(value, dict): handle_zw_compose_block(value, current_bpy_collection)
            else: print(f"    [Warning] Value for 'ZW-COMPOSE' key is not a dictionary. Value: {value}")
            continue

        # Fallback for generic dictionary (potential nested ZW structures or object attributes if key is not a ZW block type)
        # This part needs to be careful not to re-process ZW-OBJECT attributes if key was like "Cube"
        # The current structure with `obj_attributes_for_current_zw_object` handles ZW-OBJECT definitions correctly.
        # This is more for generic, non-ZW-block-keyworded dictionaries.
        elif isinstance(value, dict):
            # If the key itself is not a recognized ZW block type, but the value is a dictionary,
            # it might be a nested structure or a definition where key is the name (e.g. "MyCube: TYPE: Cube...")
            # This recursive call should use the current_bpy_collection.
            # print(f"[*] Recursively processing generic dict key: '{key}' in collection '{current_bpy_collection.name}'")

            process_zw_structure(value, parent_bpy_obj=parent_bpy_obj, current_bpy_collection=current_bpy_collection)
        # else:
            # print(f"  Skipping non-dictionary, non-ZW-block value for key '{key}'")


def run_blender_adapter(input_filepath_str: str = None):
    print("--- Starting ZW Blender Adapter ---")
    if not bpy:
        print("[X] Blender Python environment (bpy) not detected. Cannot proceed.")
        print("--- ZW Blender Adapter Finished (with errors) ---")
        return

    global current_zw_input_file
    current_zw_input_file = input_filepath_str if input_filepath_str else str(ZW_INPUT_FILE_PATH)

    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    print(f"[*] Using ZW input file: {current_zw_input_file}")

    try:
        with open(current_zw_input_file, "r", encoding="utf-8") as f:
            zw_text_content = f.read()
        print(f"{P_INFO} Successfully read ZW file: {current_zw_input_file}")
    except FileNotFoundError:
        print(f"{P_ERROR} ZW input file not found at '{current_zw_input_file}'")
        print("--- ZW Blender Adapter Finished (with errors) ---")
        return
    except Exception as e:
        print(f"{P_ERROR} Error reading ZW file '{current_zw_input_file}': {e}")
        print("--- ZW Blender Adapter Finished (with errors) ---")
        return

    if not zw_text_content.strip():
        print(f"{P_ERROR} ZW input file is empty.")
        print("--- ZW Blender Adapter Finished (with errors) ---")
        return


    try:
        print(f"{P_INFO} Parsing ZW text from '{current_zw_input_file}'...")
        parsed_zw_data = parse_zw(zw_text_content)
        if not parsed_zw_data:
            print(f"{P_WARN} Parsed ZW data from '{current_zw_input_file}' is empty. No objects will be created.")
    except Exception as e:
        print(f"{P_ERROR} Error parsing ZW text from '{current_zw_input_file}': {e}")
        print(f"{P_INFO} --- ZW Blender Adapter Finished (with errors) ---")
        return

    try:
        print(f"{P_INFO} Processing ZW structure for Blender object creation...")
        process_zw_structure(parsed_zw_data, current_bpy_collection=bpy.context.scene.collection)
        print(f"{P_INFO} Finished processing ZW structure from '{current_zw_input_file}'.")
    except Exception as e:
        print(f"{P_ERROR} Error during ZW structure processing for Blender from '{current_zw_input_file}': {e}")
        print(f"{P_INFO} --- ZW Blender Adapter Finished (with errors) ---")
        return

    print(f"{P_SUCCESS} --- ZW Blender Adapter Finished Successfully ---")


# --- ZW-COMPOSE Handler ---
def handle_zw_compose_block(compose_data: dict, default_collection: bpy.types.Collection):
    if not bpy:
        print("[Error] bpy module not available in handle_zw_compose_block. Cannot process ZW-COMPOSE.")
        return

    compose_name = compose_data.get("NAME", "ZWComposition")
    print(f"    Creating ZW-COMPOSE assembly: {compose_name}")

    # Create parent Empty for the composition
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    parent_empty = bpy.context.active_object
    if not parent_empty: # Should not happen if ops.empty_add worked
        print(f"      [Error] Failed to create parent Empty for {compose_name}. Aborting ZW-COMPOSE.")
        return
    parent_empty.name = compose_name

    # Handle transform for the parent_empty itself
    loc_str = compose_data.get("LOCATION", "(0,0,0)")
    rot_str = compose_data.get("ROTATION", "(0,0,0)")
    scale_str = compose_data.get("SCALE", "(1,1,1)")
    parent_empty.location = safe_eval(loc_str, (0,0,0))
    rot_deg = safe_eval(rot_str, (0,0,0))
    parent_empty.rotation_euler = Euler([math.radians(a) for a in rot_deg], 'XYZ')

    scale_eval = safe_eval(scale_str, (1,1,1))
    if isinstance(scale_eval, (int, float)): # Uniform scale
        parent_empty.scale = (float(scale_eval), float(scale_eval), float(scale_eval))
    else: # Tuple scale
        parent_empty.scale = scale_eval
    print(f"      Parent Empty '{parent_empty.name}' transform: L={parent_empty.location}, R={parent_empty.rotation_euler}, S={parent_empty.scale}")


    # Assign parent_empty to a collection
    comp_coll_name = compose_data.get("COLLECTION")
    target_collection_for_empty = default_collection # Default to the collection context from process_zw_structure

    if comp_coll_name: # If a specific collection is named for the ZW-COMPOSE root
        target_collection_for_empty = get_or_create_collection(comp_coll_name, parent_collection=bpy.context.scene.collection)

    # Link parent_empty to its target collection, ensure it's not in others (like default scene collection)
    current_collections = [coll for coll in parent_empty.users_collection]
    for coll in current_collections:
        coll.objects.unlink(parent_empty)
    if parent_empty.name not in target_collection_for_empty.objects: # Check to avoid duplicate link error
        target_collection_for_empty.objects.link(parent_empty)
    print(f"      Parent Empty '{parent_empty.name}' linked to collection '{target_collection_for_empty.name}'")


    # Process BASE_MODEL
    base_model_name = compose_data.get("BASE_MODEL")
    base_model_obj = None
    if base_model_name:
        original_base_obj = bpy.data.objects.get(base_model_name)
        if original_base_obj:
            # Duplicate the object and its data to make it independent for this composition
            base_model_obj = original_base_obj.copy()
            if original_base_obj.data:
                base_model_obj.data = original_base_obj.data.copy()
            base_model_obj.name = f"{base_model_name}_base_of_{compose_name}"

            # Link duplicated base_model_obj to the same collection as parent_empty
            target_collection_for_empty.objects.link(base_model_obj)

            base_model_obj.parent = parent_empty
            base_model_obj.location = (0,0,0) # Reset local transforms relative to parent_empty
            base_model_obj.rotation_euler = (0,0,0)
            base_model_obj.scale = (1,1,1)
            print(f"      Added BASE_MODEL: '{base_model_name}' as '{base_model_obj.name}', parented to '{parent_empty.name}'")
        else:
            print(f"      [Warning] BASE_MODEL object '{base_model_name}' not found in scene.")

    # Process ATTACHMENTS
    attachments_list = compose_data.get("ATTACHMENTS", [])
    if not isinstance(attachments_list, list): attachments_list = []

    for i, attach_def in enumerate(attachments_list):
        if not isinstance(attach_def, dict):
            print(f"        [Warning] Attachment item {i} is not a dictionary, skipping.")
            continue

        attach_obj_source_name = attach_def.get("OBJECT")
        original_attach_obj = bpy.data.objects.get(attach_obj_source_name)

        if original_attach_obj:
            attached_obj = original_attach_obj.copy()
            if original_attach_obj.data:
                attached_obj.data = original_attach_obj.data.copy()
            attached_obj.name = f"{attach_obj_source_name}_attach{i}_to_{compose_name}"
            target_collection_for_empty.objects.link(attached_obj) # Link to same collection as parent_empty

            attached_obj.parent = parent_empty # Parent to the main composition Empty

            # Apply local transforms for the attachment
            attach_loc_str = attach_def.get("LOCATION", "(0,0,0)")
            attach_rot_str = attach_def.get("ROTATION", "(0,0,0)")
            attach_scale_str = attach_def.get("SCALE", "(1,1,1)")

            attached_obj.location = safe_eval(attach_loc_str, (0,0,0))
            attach_rot_deg = safe_eval(attach_rot_str, (0,0,0))
            attached_obj.rotation_euler = Euler([math.radians(a) for a in attach_rot_deg], 'XYZ')

            attach_scale_eval = safe_eval(attach_scale_str, (1,1,1))
            if isinstance(attach_scale_eval, (int, float)):
                attached_obj.scale = (float(attach_scale_eval), float(attach_scale_eval), float(attach_scale_eval))
            else:
                attached_obj.scale = attach_scale_eval
            print(f"        Added ATTACHMENT: '{attach_obj_source_name}' as '{attached_obj.name}', parented to '{parent_empty.name}'")
            print(f"          Local Transform: L={attached_obj.location}, R={attached_obj.rotation_euler}, S={attached_obj.scale}")


            # Handle MATERIAL_OVERRIDE for this attachment
            material_override_def = attach_def.get("MATERIAL_OVERRIDE")
            if isinstance(material_override_def, dict):
                if ZW_MESH_UTILS_IMPORTED and APPLY_ZW_MATERIAL_FUNC:
                    print(f"          Applying MATERIAL_OVERRIDE to '{attached_obj.name}'")
                    if 'NAME' not in material_override_def:
                        material_override_def['NAME'] = f"{attached_obj.name}_OverrideMat"
                    APPLY_ZW_MATERIAL_FUNC(attached_obj, material_override_def)
                else:
                    print(f"          [Warning] MATERIAL_OVERRIDE found for '{attached_obj.name}', but zw_mesh.apply_material function was not imported.")
        else:
            print(f"        [Warning] ATTACHMENT source object '{attach_obj_source_name}' not found.")

    # Process EXPORT for the entire assembly
    export_def = compose_data.get("EXPORT")
    if export_def and isinstance(export_def, dict):
        export_format = export_def.get("FORMAT", "").lower()
        export_file_str = export_def.get("FILE")
        if export_format == "glb" and export_file_str:
            print(f"      Exporting composition '{compose_name}' to GLB: {export_file_str}")

            export_path = Path(export_file_str)
            # Attempt to make path absolute relative to a project root if not already.
            # This part assumes PROJECT_ROOT might be defined globally in blender_adapter.py or passed.
            # For now, we'll rely on Blender's relative path handling or user providing absolute paths.
            # if not export_path.is_absolute() and 'PROJECT_ROOT' in globals():
            #     export_path = PROJECT_ROOT / export_path

            try:
                export_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e_mkdir_export:
                print(f"        [Warning] Could not create directory for GLB export '{export_path.parent}': {e_mkdir_export}")

            # Select parent_empty and all its children for export
            bpy.ops.object.select_all(action='DESELECT')
            parent_empty.select_set(True) # Select the parent empty
            # Also select all children recursively
            for child in parent_empty.children_recursive:
                child.select_set(True)
            bpy.context.view_layer.objects.active = parent_empty # Ensure parent is active for some export options

            try:
                bpy.ops.export_scene.gltf(
                    filepath=str(export_path), # Use str() for older Blender versions if Path object not fully supported by op
                    export_format='GLB',
                    use_selection=True,
                    export_apply=True,  # Apply modifiers
                    export_materials='EXPORT',
                    export_texcoords=True,
                    export_normals=True,
                    export_cameras=False, # Usually False for component exports
                    export_lights=False   # Usually False for component exports
                )
                print(f"        Successfully exported composition '{compose_name}' to '{export_path.resolve() if export_path.exists() else export_path}'") # Check if resolve() is safe if file creation failed
            except RuntimeError as e_export:
                print(f"        [Error] Failed to export composition '{compose_name}' to GLB: {e_export}")
        else:
            print(f"      [Warning] EXPORT block for '{compose_name}' is missing format/file or format not 'glb'.")
    print(f"    ✅ Finished ZW-COMPOSE assembly: {compose_name}")


if __name__ == "__main__":
    # This part is crucial for scripts run with `blender --python script.py -- <args>`
    # Blender's Python interpreter passes arguments after '--' to the script.
    # We need to parse them.

    # Make sure PROJECT_ROOT is defined for potential use in export paths.
    # If __file__ is not defined (e.g. running from Blender's text editor without saving),
    # this will try to use bpy.data.filepath (path of the .blend file) or default to current dir.
    # This was moved up to be near other path configurations.

    adapter_parser = argparse.ArgumentParser(description="ZW Blender Adapter Script")
    adapter_parser.add_argument(
        "--input",
        type=str,
        help="Path to the ZW input file to process.",
        default=None # Default to None, run_blender_adapter will use ZW_INPUT_FILE_PATH
    )

    # Blender's python interpreter will pass args after '--'
    # sys.argv will contain all args passed to Blender if not run with --python.
    # If run with --python script.py -- args, then script.py's sys.argv start after --
    # We need to find where our script's arguments begin.
    argv = sys.argv
    try:
        # If '--' is present, arguments for this script start after it
        idx = argv.index("--") + 1
        script_args = argv[idx:]
    except ValueError:
        # If '--' is not present, it means the script might be run directly
        # or Blender didn't pass args in a way that separated them.
        # We'll assume no specific args were meant for this script beyond Blender's own.
        script_args = [] # Or parse all of sys.argv if that's the desired behavior

    # Check if running inside Blender first
    if bpy:
        args = adapter_parser.parse_args(args=script_args)
        run_blender_adapter(input_filepath_str=args.input)
    else:
        # This case is if the script is somehow run by a Python interpreter outside Blender
        # but __name__ == "__main__" is true.
        print("This script is intended to be run from within Blender.")
        print("Example: blender --background --python blender_adapter.py -- --input /path/to/scene.zw")
        # You could still parse args for testing parts of the script that don't need bpy
        # args = adapter_parser.parse_args(args=script_args)
        # if args.input:
        #     print(f"Would attempt to process: {args.input} (but bpy is not available)")
        # else:
        #     print(f"Would attempt to process default ZW_INPUT_FILE_PATH (but bpy is not available)")
