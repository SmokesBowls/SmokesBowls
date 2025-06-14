# zw_mcp/blender_adapter.py
import sys
import json # For potential pretty printing if needed, not directly for to_zw
from pathlib import Path
import argparse
import math # Added for math.radians
from pathlib import Path # Ensure Path is imported for handle_zw_compose_block
from mathutils import Vector, Euler # For ZW-COMPOSE transforms

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
    from .zw_mesh import apply_material as imported_apply_material
    APPLY_ZW_MATERIAL_FUNC = imported_apply_material
    ZW_MESH_UTILS_IMPORTED = True # We only strictly need apply_material for ZW-COMPOSE material override
    print("Successfully imported apply_material from .zw_mesh (relative).")
except ImportError:

    print(f"{P_WARN} Could not import 'parse_zw' from 'zw_mcp.zw_parser'.")
    try:
        from zw_parser import parse_zw # Attempt direct import if in same folder for some reason
    except ImportError:
        print(f"{P_WARN} Fallback import of 'parse_zw' also failed.")
        print(f"{P_WARN} Ensure 'zw_parser.py' is accessible and zw_mcp is in PYTHONPATH or script is run appropriately.")
        def parse_zw(text: str) -> dict:
            print(f"{P_WARN} Dummy parse_zw called. Real parsing will not occur.")
            return {}
        # sys.exit(1) # Or exit if critical

ZW_INPUT_FILE_PATH = Path("zw_mcp/prompts/blender_scene.zw") # Default, can be overridden by args
=======
    try:
        from zw_mcp.zw_mesh import apply_material as pkg_imported_apply_material
        APPLY_ZW_MATERIAL_FUNC = pkg_imported_apply_material
        ZW_MESH_UTILS_IMPORTED = True
        print("Successfully imported apply_material from zw_mcp.zw_mesh (package).")
    except ImportError as e_pkg_utils:
        print(f"Failed package import of zw_mesh.apply_material: {e_pkg_utils}")
        try:
            from zw_mesh import apply_material as direct_imported_apply_material
            APPLY_ZW_MATERIAL_FUNC = direct_imported_apply_material
            ZW_MESH_UTILS_IMPORTED = True
            print("Successfully imported zw_mesh.apply_material (direct from script directory - fallback).")
        except ImportError as e_direct_utils:
            print(f"All import attempts for zw_mesh.apply_material failed: {e_direct_utils}")
            def APPLY_ZW_MATERIAL_FUNC(obj, material_def):
                print("[Critical Error] zw_mesh.apply_material was not imported. Cannot apply material override in ZW-COMPOSE.")

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
                 target_obj[f"ZW_{key.upper()}"] = value
            else:
                target_obj[f"ZW_{key.upper()}"] = str(value)
            print(f"    Set custom property ZW_{key.upper()} on {target_obj.name}")
        except Exception as e:
            print(f"    [Error] Failed to set custom property ZW_{key.upper()} on {target_obj.name}: {e}")

# --- New ZW-COMPOSE-TEMPLATE Handler ---
def handle_zw_compose_template_block(template_data: dict):
    if not bpy: return
    template_name = template_data.get("NAME", "UnnamedZWTemplate")
    print(f"  Storing ZW-COMPOSE-TEMPLATE: {template_name}")

    text_block_name = f"ZW_Template_{template_name}"
    text_block = bpy.data.texts.get(text_block_name)
    if not text_block:
        text_block = bpy.data.texts.new(name=text_block_name)

    try:
        template_json_string = json.dumps(template_data, indent=2)
        text_block.from_string(template_json_string)
        print(f"    Stored template '{template_name}' in Text block '{text_block_name}'.")
        scene_prop_name = f"ZW_TEMPLATE_{template_name.upper()}"
        bpy.context.scene[scene_prop_name] = template_json_string
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

        if len(mesh_obj.data.materials) == 0:
            mesh_obj.data.materials.append(mat)
        else:
            mesh_obj.data.materials[0] = mat

        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if not bsdf:
            bsdf = mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
            output_node = mat.node_tree.nodes.get('Material Output') or mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
            mat.node_tree.links.new(bsdf.outputs['BSDF'], output_node.inputs['Surface'])

        if "BASE_COLOR" in material_def: bsdf.inputs["Base Color"].default_value = parse_color(material_def["BASE_COLOR"])

        emission_strength = float(material_def.get("EMISSION", material_def.get("EMISSION_STRENGTH", 0.0)))
        bsdf.inputs["Emission Strength"].default_value = emission_strength
        if emission_strength > 0:
             bsdf.inputs["Emission Color"].default_value = parse_color(material_def.get("EMISSION_COLOR", (0,0,0,1)))

        if "ROUGHNESS" in material_def: bsdf.inputs["Roughness"].default_value = float(material_def["ROUGHNESS"])
        if "METALLIC" in material_def: bsdf.inputs["Metallic"].default_value = float(material_def["METALLIC"])
        if "TRANSMISSION" in material_def: bsdf.inputs["Transmission"].default_value = float(material_def["TRANSMISSION"])
        if "ALPHA" in material_def: bsdf.inputs["Alpha"].default_value = float(material_def["ALPHA"])
        if "SPECULAR" in material_def: bsdf.inputs["Specular IOR Level"].default_value = float(material_def["SPECULAR"])


    metadata_dict = mesh_data.get("METADATA")
    if isinstance(metadata_dict, dict):
        handle_zw_metadata_block(metadata_dict, target_obj_name=mesh_obj.name)

    explicit_coll_name = mesh_data.get("COLLECTION")
    target_collection = current_bpy_collection
    if explicit_coll_name:
        target_collection = get_or_create_collection(explicit_coll_name, bpy.context.scene.collection)

    current_obj_collections = [c for c in mesh_obj.users_collection]
    for c in current_obj_collections: c.objects.unlink(mesh_obj)
    if mesh_obj.name not in target_collection.objects: target_collection.objects.link(mesh_obj)
    print(f"    Linked '{mesh_obj.name}' to collection '{target_collection.name}'")

    print(f"    ✅ Successfully created ZW-MESH (integrated): {mesh_name}")
    return mesh_obj

# --- ZW-COMPOSE Handler (Refined for object duplication and custom props) ---
def handle_zw_compose_block(compose_data: dict, default_collection: bpy.types.Collection):
    if not bpy:
        print("[Error] bpy module not available in handle_zw_compose_block. Cannot process ZW-COMPOSE.")
        return

    compose_name = compose_data.get("NAME", "ZWComposition")
    print(f"[*] Processing ZW-COMPOSE assembly: {compose_name}")

    bpy.ops.object.empty_add(type='PLAIN_AXES')
    parent_empty = bpy.context.active_object
    if not parent_empty:
        print(f"    [Error] Failed to create parent Empty for {compose_name}. Aborting ZW-COMPOSE.")
        return
    parent_empty.name = compose_name

    parent_empty.location = safe_eval(compose_data.get("LOCATION", "(0,0,0)"), (0,0,0))
    rot_deg = safe_eval(compose_data.get("ROTATION", "(0,0,0)"), (0,0,0))
    parent_empty.rotation_euler = Euler([math.radians(a) for a in rot_deg], 'XYZ')
    scale_eval = safe_eval(compose_data.get("SCALE", "(1,1,1)"), (1,1,1))
    parent_empty.scale = (scale_eval if isinstance(scale_eval, tuple) else (float(scale_eval), float(scale_eval), float(scale_eval)))
    print(f"    Parent Empty '{parent_empty.name}' transform: L={parent_empty.location}, R={parent_empty.rotation_euler}, S={parent_empty.scale}")

    comp_coll_name = compose_data.get("COLLECTION")
    target_collection_for_empty = default_collection
    if comp_coll_name:
        target_collection_for_empty = get_or_create_collection(comp_coll_name, parent_collection=bpy.context.scene.collection)

    current_collections = [coll for coll in parent_empty.users_collection]
    for coll in current_collections: coll.objects.unlink(parent_empty)
    if parent_empty.name not in target_collection_for_empty.objects:
        target_collection_for_empty.objects.link(parent_empty)
    print(f"    Parent Empty '{parent_empty.name}' linked to collection '{target_collection_for_empty.name}'")

    parent_empty["ZW_COMPOSE_NAME"] = compose_name
    parent_empty["ZW_TEMPLATE_SOURCE"] = compose_data.get("TEMPLATE_SOURCE", "Direct ZW-COMPOSE")
    parent_empty["ZW_ATTACHMENT_COUNT"] = len(compose_data.get("ATTACHMENTS", []))

    base_model_name = compose_data.get("BASE_MODEL")
    if base_model_name:
        original_base_obj = bpy.data.objects.get(base_model_name)
        if original_base_obj:
            bpy.ops.object.select_all(action='DESELECT')
            original_base_obj.select_set(True)
            bpy.context.view_layer.objects.active = original_base_obj
            bpy.ops.object.duplicate(linked=False)
            base_model_obj = bpy.context.active_object
            base_model_obj.name = f"{base_model_name}_base_of_{compose_name}"
            target_collection_for_empty.objects.link(base_model_obj)
            base_model_obj.parent = parent_empty
            base_model_obj.location, base_model_obj.rotation_euler, base_model_obj.scale = (0,0,0), (0,0,0), (1,1,1)
            base_model_obj["ZW_SLOT_ID"] = "BASE_MODEL"
            base_model_obj["ZW_ROLE"] = compose_data.get("BASE_MODEL_ROLE", "base_model")
            base_model_obj["ZW_SOURCE_OBJECT"] = base_model_name
            print(f"    Added BASE_MODEL: '{base_model_name}' as '{base_model_obj.name}'")
        else: print(f"    [Warning] BASE_MODEL object '{base_model_name}' not found.")

    attachments_list = compose_data.get("ATTACHMENTS", [])
    for i, attach_def in enumerate(attachments_list):
        if not isinstance(attach_def, dict): continue
        attach_obj_source_name = attach_def.get("OBJECT")
        original_attach_obj = bpy.data.objects.get(attach_obj_source_name)
        if original_attach_obj:
            bpy.ops.object.select_all(action='DESELECT')
            original_attach_obj.select_set(True)
            bpy.context.view_layer.objects.active = original_attach_obj
            bpy.ops.object.duplicate(linked=False)
            attached_obj = bpy.context.active_object
            attached_obj.name = f"{attach_obj_source_name}_attach{i}_to_{compose_name}"
            target_collection_for_empty.objects.link(attached_obj)
            attached_obj.parent = parent_empty

            attached_obj.location = safe_eval(attach_def.get("LOCATION", "(0,0,0)"), (0,0,0))
            attach_rot_deg = safe_eval(attach_def.get("ROTATION", "(0,0,0)"), (0,0,0))
            attached_obj.rotation_euler = Euler([math.radians(a) for a in attach_rot_deg], 'XYZ')
            attach_scale_eval = safe_eval(attach_def.get("SCALE", "(1,1,1)"), (1,1,1))
            attached_obj.scale = (attach_scale_eval if isinstance(attach_scale_eval, tuple) else (float(attach_scale_eval), float(attach_scale_eval), float(attach_scale_eval)))

            attached_obj["ZW_SLOT_ID"] = attach_def.get("SLOT_ID", f"ATTACHMENT_{i}")
            attached_obj["ZW_ROLE"] = attach_def.get("ROLE", "attachment")
            attached_obj["ZW_SOURCE_OBJECT"] = attach_obj_source_name
            print(f"      Added ATTACHMENT: '{attach_obj_source_name}' as '{attached_obj.name}'")

            material_override_def = attach_def.get("MATERIAL_OVERRIDE")
            if isinstance(material_override_def, dict):
                if ZW_MESH_UTILS_IMPORTED and APPLY_ZW_MATERIAL_FUNC:
                    print(f"        Applying MATERIAL_OVERRIDE to '{attached_obj.name}'")
                    if 'NAME' not in material_override_def:
                        material_override_def['NAME'] = f"{attached_obj.name}_OverrideMat"
                    APPLY_ZW_MATERIAL_FUNC(attached_obj, material_override_def)
                else: print(f"        [Warning] MATERIAL_OVERRIDE for '{attached_obj.name}' but zw_mesh.apply_material not imported.")
        else: print(f"      [Warning] ATTACHMENT source object '{attach_obj_source_name}' not found.")

    export_def = compose_data.get("EXPORT")
    if export_def and isinstance(export_def, dict):
        export_format = export_def.get("FORMAT", "").lower()
        export_file_str = export_def.get("FILE")
        if export_format == "glb" and export_file_str:
            print(f"    Exporting composition '{compose_name}' to GLB: {export_file_str}")
            export_path = Path(export_file_str)
            if not export_path.is_absolute(): export_path = PROJECT_ROOT / export_path
            export_path.parent.mkdir(parents=True, exist_ok=True)

            bpy.ops.object.select_all(action='DESELECT')
            parent_empty.select_set(True)
            for child in parent_empty.children_recursive: child.select_set(True)
            bpy.context.view_layer.objects.active = parent_empty
            try:
                bpy.ops.export_scene.gltf(filepath=str(export_path.resolve()), export_format='GLB', use_selection=True, export_apply=True, export_materials='EXPORT', export_texcoords=True, export_normals=True, export_cameras=False, export_lights=False)
                print(f"      Successfully exported to '{export_path.resolve()}'")
            except RuntimeError as e_export: print(f"      [Error] Failed to export GLB for '{compose_name}': {e_export}")
        else: print(f"    [Warning] EXPORT for '{compose_name}' missing format/file or not 'glb'.")
    print(f"    ✅ Finished ZW-COMPOSE assembly: {compose_name}")

def safe_eval(str_val, default_val):
    if not isinstance(str_val, str):
        return default_val
    try:
        return eval(str_val)
    except (SyntaxError, NameError, TypeError, ValueError) as e:
        print(f"    [!] Warning: Could not evaluate string '{str_val}' for attribute: {e}. Using default: {default_val}")
        return default_val

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
                 target_obj[f"ZW_{key.upper()}"] = value
            else:
                target_obj[f"ZW_{key.upper()}"] = str(value)
            print(f"    Set custom property ZW_{key.upper()} on {target_obj.name}")
        except Exception as e:
            print(f"    [Error] Failed to set custom property ZW_{key.upper()} on {target_obj.name}: {e}")

# --- New ZW-COMPOSE-TEMPLATE Handler ---
def handle_zw_compose_template_block(template_data: dict):
    if not bpy: return
    template_name = template_data.get("NAME", "UnnamedZWTemplate")
    print(f"  Storing ZW-COMPOSE-TEMPLATE: {template_name}")

    text_block_name = f"ZW_Template_{template_name}"
    text_block = bpy.data.texts.get(text_block_name)
    if not text_block:
        text_block = bpy.data.texts.new(name=text_block_name)

    try:
        template_json_string = json.dumps(template_data, indent=2)
        text_block.from_string(template_json_string)
        print(f"    Stored template '{template_name}' in Text block '{text_block_name}'.")
        scene_prop_name = f"ZW_TEMPLATE_{template_name.upper()}"
        bpy.context.scene[scene_prop_name] = template_json_string
        print(f"    Stored template '{template_name}' in Scene custom property '{scene_prop_name}'.")
    except Exception as e:
        print(f"    [Error] Failed to store ZW-COMPOSE-TEMPLATE '{template_name}': {e}")

# --- New Integrated ZW-MESH Handler (replaces external call) ---
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

    # Apply material properties (simplified from Phase 9.1 user prompt for this function)
    material_def = mesh_data.get("MATERIAL")
    if isinstance(material_def, dict):
        mat_name = material_def.get("NAME", f"{mesh_name}_Material")
        mat = bpy.data.materials.get(mat_name)
        if not mat: mat = bpy.data.materials.new(name=mat_name)

        if len(mesh_obj.data.materials) == 0:
            mesh_obj.data.materials.append(mat)
        else:
            mesh_obj.data.materials[0] = mat

        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if not bsdf:
            bsdf = mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
            output_node = mat.node_tree.nodes.get('Material Output') or mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
            mat.node_tree.links.new(bsdf.outputs['BSDF'], output_node.inputs['Surface'])

        if "BASE_COLOR" in material_def: bsdf.inputs["Base Color"].default_value = parse_color(material_def["BASE_COLOR"])

        emission_strength = float(material_def.get("EMISSION", material_def.get("EMISSION_STRENGTH", 0.0)))
        bsdf.inputs["Emission Strength"].default_value = emission_strength
        if emission_strength > 0:
             bsdf.inputs["Emission Color"].default_value = parse_color(material_def.get("EMISSION_COLOR", (0,0,0,1)))

        if "ROUGHNESS" in material_def: bsdf.inputs["Roughness"].default_value = float(material_def["ROUGHNESS"])
        if "METALLIC" in material_def: bsdf.inputs["Metallic"].default_value = float(material_def["METALLIC"])
        if "TRANSMISSION" in material_def: bsdf.inputs["Transmission"].default_value = float(material_def["TRANSMISSION"])
        if "ALPHA" in material_def: bsdf.inputs["Alpha"].default_value = float(material_def["ALPHA"])
        if "SPECULAR" in material_def: bsdf.inputs["Specular IOR Level"].default_value = float(material_def["SPECULAR"])


    metadata_dict = mesh_data.get("METADATA")
    if isinstance(metadata_dict, dict):
        handle_zw_metadata_block(metadata_dict, target_obj_name=mesh_obj.name)

    explicit_coll_name = mesh_data.get("COLLECTION")
    target_collection = current_bpy_collection
    if explicit_coll_name:
        target_collection = get_or_create_collection(explicit_coll_name, bpy.context.scene.collection)

    current_obj_collections = [c for c in mesh_obj.users_collection]
    for c in current_obj_collections: c.objects.unlink(mesh_obj)
    if mesh_obj.name not in target_collection.objects: target_collection.objects.link(mesh_obj)
    print(f"    Linked '{mesh_obj.name}' to collection '{target_collection.name}'")

    print(f"    ✅ Successfully created ZW-MESH (integrated): {mesh_name}")
    return mesh_obj

# --- ZW-COMPOSE Handler (Refined for object duplication and custom props) ---
def handle_zw_compose_block(compose_data: dict, default_collection: bpy.types.Collection):
    if not bpy:
        print("[Error] bpy module not available in handle_zw_compose_block. Cannot process ZW-COMPOSE.")
        return

    compose_name = compose_data.get("NAME", "ZWComposition")
    print(f"[*] Processing ZW-COMPOSE assembly: {compose_name}")

    bpy.ops.object.empty_add(type='PLAIN_AXES')
    parent_empty = bpy.context.active_object
    if not parent_empty:
        print(f"    [Error] Failed to create parent Empty for {compose_name}. Aborting ZW-COMPOSE.")
        return
    parent_empty.name = compose_name

    parent_empty.location = safe_eval(compose_data.get("LOCATION", "(0,0,0)"), (0,0,0))
    rot_deg = safe_eval(compose_data.get("ROTATION", "(0,0,0)"), (0,0,0))
    parent_empty.rotation_euler = Euler([math.radians(a) for a in rot_deg], 'XYZ')
    scale_eval = safe_eval(compose_data.get("SCALE", "(1,1,1)"), (1,1,1))
    parent_empty.scale = (scale_eval if isinstance(scale_eval, tuple) else (float(scale_eval), float(scale_eval), float(scale_eval)))
    print(f"    Parent Empty '{parent_empty.name}' transform: L={parent_empty.location}, R={parent_empty.rotation_euler}, S={parent_empty.scale}")

    comp_coll_name = compose_data.get("COLLECTION")
    target_collection_for_empty = default_collection
    if comp_coll_name:
        target_collection_for_empty = get_or_create_collection(comp_coll_name, parent_collection=bpy.context.scene.collection)

    current_collections = [coll for coll in parent_empty.users_collection]
    for coll in current_collections: coll.objects.unlink(parent_empty)
    if parent_empty.name not in target_collection_for_empty.objects:
        target_collection_for_empty.objects.link(parent_empty)
    print(f"    Parent Empty '{parent_empty.name}' linked to collection '{target_collection_for_empty.name}'")

    parent_empty["ZW_COMPOSE_NAME"] = compose_name
    parent_empty["ZW_TEMPLATE_SOURCE"] = compose_data.get("TEMPLATE_SOURCE", "Direct ZW-COMPOSE")
    parent_empty["ZW_ATTACHMENT_COUNT"] = len(compose_data.get("ATTACHMENTS", []))

    base_model_name = compose_data.get("BASE_MODEL")
    if base_model_name:
        original_base_obj = bpy.data.objects.get(base_model_name)
        if original_base_obj:
            bpy.ops.object.select_all(action='DESELECT')
            original_base_obj.select_set(True)
            bpy.context.view_layer.objects.active = original_base_obj
            bpy.ops.object.duplicate(linked=False)
            base_model_obj = bpy.context.active_object
            base_model_obj.name = f"{base_model_name}_base_of_{compose_name}"
            target_collection_for_empty.objects.link(base_model_obj)
            base_model_obj.parent = parent_empty
            base_model_obj.location, base_model_obj.rotation_euler, base_model_obj.scale = (0,0,0), (0,0,0), (1,1,1)
            base_model_obj["ZW_SLOT_ID"] = "BASE_MODEL" # Custom Property
            base_model_obj["ZW_ROLE"] = compose_data.get("BASE_MODEL_ROLE", "base_model") # Custom Property
            base_model_obj["ZW_SOURCE_OBJECT"] = base_model_name # Custom Property
            print(f"    Added BASE_MODEL: '{base_model_name}' as '{base_model_obj.name}'")
        else: print(f"    [Warning] BASE_MODEL object '{base_model_name}' not found.")

    attachments_list = compose_data.get("ATTACHMENTS", [])
    for i, attach_def in enumerate(attachments_list):
        if not isinstance(attach_def, dict): continue
        attach_obj_source_name = attach_def.get("OBJECT")
        original_attach_obj = bpy.data.objects.get(attach_obj_source_name)
        if original_attach_obj:
            bpy.ops.object.select_all(action='DESELECT')
            original_attach_obj.select_set(True)
            bpy.context.view_layer.objects.active = original_attach_obj
            bpy.ops.object.duplicate(linked=False)
            attached_obj = bpy.context.active_object
            attached_obj.name = f"{attach_obj_source_name}_attach{i}_to_{compose_name}"
            target_collection_for_empty.objects.link(attached_obj)
            attached_obj.parent = parent_empty

            attached_obj.location = safe_eval(attach_def.get("LOCATION", "(0,0,0)"), (0,0,0))
            attach_rot_deg = safe_eval(attach_def.get("ROTATION", "(0,0,0)"), (0,0,0))
            attached_obj.rotation_euler = Euler([math.radians(a) for a in attach_rot_deg], 'XYZ')
            attach_scale_eval = safe_eval(attach_def.get("SCALE", "(1,1,1)"), (1,1,1))
            attached_obj.scale = (attach_scale_eval if isinstance(attach_scale_eval, tuple) else (float(attach_scale_eval), float(attach_scale_eval), float(attach_scale_eval)))

            attached_obj["ZW_SLOT_ID"] = attach_def.get("SLOT_ID", f"ATTACHMENT_{i}")
            attached_obj["ZW_ROLE"] = attach_def.get("ROLE", "attachment")
            attached_obj["ZW_SOURCE_OBJECT"] = attach_obj_source_name
            print(f"      Added ATTACHMENT: '{attach_obj_source_name}' as '{attached_obj.name}'")

            material_override_def = attach_def.get("MATERIAL_OVERRIDE")
            if isinstance(material_override_def, dict):
                if ZW_MESH_UTILS_IMPORTED and APPLY_ZW_MATERIAL_FUNC:
                    print(f"        Applying MATERIAL_OVERRIDE to '{attached_obj.name}'")
                    if 'NAME' not in material_override_def:
                        material_override_def['NAME'] = f"{attached_obj.name}_OverrideMat"
                    APPLY_ZW_MATERIAL_FUNC(attached_obj, material_override_def)
                else: print(f"        [Warning] MATERIAL_OVERRIDE for '{attached_obj.name}' but zw_mesh.apply_material not imported.")
        else: print(f"      [Warning] ATTACHMENT source object '{attach_obj_source_name}' not found.")

    export_def = compose_data.get("EXPORT")
    if export_def and isinstance(export_def, dict):
        export_format = export_def.get("FORMAT", "").lower()
        export_file_str = export_def.get("FILE")
        if export_format == "glb" and export_file_str:
            print(f"    Exporting composition '{compose_name}' to GLB: {export_file_str}")
            export_path = Path(export_file_str)
            if not export_path.is_absolute(): export_path = PROJECT_ROOT / export_path
            export_path.parent.mkdir(parents=True, exist_ok=True)

            bpy.ops.object.select_all(action='DESELECT')
            parent_empty.select_set(True)
            for child in parent_empty.children_recursive: child.select_set(True)
            bpy.context.view_layer.objects.active = parent_empty
            try:
                bpy.ops.export_scene.gltf(filepath=str(export_path.resolve()), export_format='GLB', use_selection=True, export_apply=True, export_materials='EXPORT', export_texcoords=True, export_normals=True, export_cameras=False, export_lights=False)
                print(f"      Successfully exported to '{export_path.resolve()}'")
            except RuntimeError as e_export: print(f"      [Error] Failed to export GLB for '{compose_name}': {e_export}")
        else: print(f"    [Warning] EXPORT for '{compose_name}' missing format/file or not 'glb'.")
    print(f"    ✅ Finished ZW-COMPOSE assembly: {compose_name}")


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
                 target_obj[f"ZW_{key.upper()}"] = value
            else:
                target_obj[f"ZW_{key.upper()}"] = str(value)
            print(f"    Set custom property ZW_{key.upper()} on {target_obj.name}")
        except Exception as e:
            print(f"    [Error] Failed to set custom property ZW_{key.upper()} on {target_obj.name}: {e}")

# --- New ZW-COMPOSE-TEMPLATE Handler ---
def handle_zw_compose_template_block(template_data: dict):
    if not bpy: return
    template_name = template_data.get("NAME", "UnnamedZWTemplate")
    print(f"  Storing ZW-COMPOSE-TEMPLATE: {template_name}")

    text_block_name = f"ZW_Template_{template_name}"
    text_block = bpy.data.texts.get(text_block_name)
    if not text_block:
        text_block = bpy.data.texts.new(name=text_block_name)

    try:
        template_json_string = json.dumps(template_data, indent=2)
        text_block.from_string(template_json_string)
        print(f"    Stored template '{template_name}' in Text block '{text_block_name}'.")
        scene_prop_name = f"ZW_TEMPLATE_{template_name.upper()}"
        bpy.context.scene[scene_prop_name] = template_json_string
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

        if len(mesh_obj.data.materials) == 0:
            mesh_obj.data.materials.append(mat)
        else:
            mesh_obj.data.materials[0] = mat

        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if not bsdf:
            bsdf = mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
            output_node = mat.node_tree.nodes.get('Material Output') or mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
            mat.node_tree.links.new(bsdf.outputs['BSDF'], output_node.inputs['Surface'])

        if "BASE_COLOR" in material_def: bsdf.inputs["Base Color"].default_value = parse_color(material_def["BASE_COLOR"])

        emission_strength = float(material_def.get("EMISSION", material_def.get("EMISSION_STRENGTH", 0.0)))
        bsdf.inputs["Emission Strength"].default_value = emission_strength
        if emission_strength > 0:
             bsdf.inputs["Emission Color"].default_value = parse_color(material_def.get("EMISSION_COLOR", (0,0,0,1)))

        if "ROUGHNESS" in material_def: bsdf.inputs["Roughness"].default_value = float(material_def["ROUGHNESS"])
        if "METALLIC" in material_def: bsdf.inputs["Metallic"].default_value = float(material_def["METALLIC"])
        if "TRANSMISSION" in material_def: bsdf.inputs["Transmission"].default_value = float(material_def["TRANSMISSION"])
        if "ALPHA" in material_def: bsdf.inputs["Alpha"].default_value = float(material_def["ALPHA"])
        if "SPECULAR" in material_def: bsdf.inputs["Specular IOR Level"].default_value = float(material_def["SPECULAR"])


    metadata_dict = mesh_data.get("METADATA")
    if isinstance(metadata_dict, dict):
        handle_zw_metadata_block(metadata_dict, target_obj_name=mesh_obj.name)

    explicit_coll_name = mesh_data.get("COLLECTION")
    target_collection = current_bpy_collection
    if explicit_coll_name:
        target_collection = get_or_create_collection(explicit_coll_name, bpy.context.scene.collection)

    current_obj_collections = [c for c in mesh_obj.users_collection]
    for c in current_obj_collections: c.objects.unlink(mesh_obj)
    if mesh_obj.name not in target_collection.objects: target_collection.objects.link(mesh_obj)
    print(f"    Linked '{mesh_obj.name}' to collection '{target_collection.name}'")

    print(f"    ✅ Successfully created ZW-MESH (integrated): {mesh_name}")
    return mesh_obj

# --- ZW-COMPOSE Handler (Refined for object duplication and custom props) ---
def handle_zw_compose_block(compose_data: dict, default_collection: bpy.types.Collection):
    if not bpy:
        print("[Error] bpy module not available in handle_zw_compose_block. Cannot process ZW-COMPOSE.")
        return

    compose_name = compose_data.get("NAME", "ZWComposition")
    print(f"[*] Processing ZW-COMPOSE assembly: {compose_name}")

    bpy.ops.object.empty_add(type='PLAIN_AXES')
    parent_empty = bpy.context.active_object
    if not parent_empty:
        print(f"    [Error] Failed to create parent Empty for {compose_name}. Aborting ZW-COMPOSE.")
        return
    parent_empty.name = compose_name

    parent_empty.location = safe_eval(compose_data.get("LOCATION", "(0,0,0)"), (0,0,0))
    rot_deg = safe_eval(compose_data.get("ROTATION", "(0,0,0)"), (0,0,0))
    parent_empty.rotation_euler = Euler([math.radians(a) for a in rot_deg], 'XYZ')
    scale_eval = safe_eval(compose_data.get("SCALE", "(1,1,1)"), (1,1,1))
    parent_empty.scale = (scale_eval if isinstance(scale_eval, tuple) else (float(scale_eval), float(scale_eval), float(scale_eval)))
    print(f"    Parent Empty '{parent_empty.name}' transform: L={parent_empty.location}, R={parent_empty.rotation_euler}, S={parent_empty.scale}")

    comp_coll_name = compose_data.get("COLLECTION")
    target_collection_for_empty = default_collection
    if comp_coll_name:
        target_collection_for_empty = get_or_create_collection(comp_coll_name, parent_collection=bpy.context.scene.collection)

    current_collections = [coll for coll in parent_empty.users_collection]
    for coll in current_collections: coll.objects.unlink(parent_empty)
    if parent_empty.name not in target_collection_for_empty.objects:
        target_collection_for_empty.objects.link(parent_empty)
    print(f"    Parent Empty '{parent_empty.name}' linked to collection '{target_collection_for_empty.name}'")

    parent_empty["ZW_COMPOSE_NAME"] = compose_name
    parent_empty["ZW_TEMPLATE_SOURCE"] = compose_data.get("TEMPLATE_SOURCE", "Direct ZW-COMPOSE")
    parent_empty["ZW_ATTACHMENT_COUNT"] = len(compose_data.get("ATTACHMENTS", []))

    base_model_name = compose_data.get("BASE_MODEL")
    if base_model_name:
        original_base_obj = bpy.data.objects.get(base_model_name)
        if original_base_obj:
            bpy.ops.object.select_all(action='DESELECT')
            original_base_obj.select_set(True)
            bpy.context.view_layer.objects.active = original_base_obj
            bpy.ops.object.duplicate(linked=False)
            base_model_obj = bpy.context.active_object
            base_model_obj.name = f"{base_model_name}_base_of_{compose_name}"
            target_collection_for_empty.objects.link(base_model_obj)
            base_model_obj.parent = parent_empty
            base_model_obj.location, base_model_obj.rotation_euler, base_model_obj.scale = (0,0,0), (0,0,0), (1,1,1)
            base_model_obj["ZW_SLOT_ID"] = "BASE_MODEL"
            base_model_obj["ZW_ROLE"] = compose_data.get("BASE_MODEL_ROLE", "base_model")
            base_model_obj["ZW_SOURCE_OBJECT"] = base_model_name
            print(f"    Added BASE_MODEL: '{base_model_name}' as '{base_model_obj.name}'")
        else: print(f"    [Warning] BASE_MODEL object '{base_model_name}' not found.")

    attachments_list = compose_data.get("ATTACHMENTS", [])
    for i, attach_def in enumerate(attachments_list):
        if not isinstance(attach_def, dict): continue
        attach_obj_source_name = attach_def.get("OBJECT")
        original_attach_obj = bpy.data.objects.get(attach_obj_source_name)
        if original_attach_obj:
            bpy.ops.object.select_all(action='DESELECT')
            original_attach_obj.select_set(True)
            bpy.context.view_layer.objects.active = original_attach_obj
            bpy.ops.object.duplicate(linked=False)
            attached_obj = bpy.context.active_object
            attached_obj.name = f"{attach_obj_source_name}_attach{i}_to_{compose_name}"
            target_collection_for_empty.objects.link(attached_obj)
            attached_obj.parent = parent_empty

            attached_obj.location = safe_eval(attach_def.get("LOCATION", "(0,0,0)"), (0,0,0))
            attach_rot_deg = safe_eval(attach_def.get("ROTATION", "(0,0,0)"), (0,0,0))
            attached_obj.rotation_euler = Euler([math.radians(a) for a in attach_rot_deg], 'XYZ')
            attach_scale_eval = safe_eval(attach_def.get("SCALE", "(1,1,1)"), (1,1,1))
            attached_obj.scale = (attach_scale_eval if isinstance(attach_scale_eval, tuple) else (float(attach_scale_eval), float(attach_scale_eval), float(attach_scale_eval)))

            attached_obj["ZW_SLOT_ID"] = attach_def.get("SLOT_ID", f"ATTACHMENT_{i}")
            attached_obj["ZW_ROLE"] = attach_def.get("ROLE", "attachment")
            attached_obj["ZW_SOURCE_OBJECT"] = attach_obj_source_name
            print(f"      Added ATTACHMENT: '{attach_obj_source_name}' as '{attached_obj.name}'")

            material_override_def = attach_def.get("MATERIAL_OVERRIDE")
            if isinstance(material_override_def, dict):
                if ZW_MESH_UTILS_IMPORTED and APPLY_ZW_MATERIAL_FUNC:
                    print(f"        Applying MATERIAL_OVERRIDE to '{attached_obj.name}'")
                    if 'NAME' not in material_override_def:
                        material_override_def['NAME'] = f"{attached_obj.name}_OverrideMat"
                    APPLY_ZW_MATERIAL_FUNC(attached_obj, material_override_def)
                else: print(f"        [Warning] MATERIAL_OVERRIDE for '{attached_obj.name}' but zw_mesh.apply_material not imported.")
        else: print(f"      [Warning] ATTACHMENT source object '{attach_obj_source_name}' not found.")

    export_def = compose_data.get("EXPORT")
    if export_def and isinstance(export_def, dict):
        export_format = export_def.get("FORMAT", "").lower()
        export_file_str = export_def.get("FILE")
        if export_format == "glb" and export_file_str:
            print(f"    Exporting composition '{compose_name}' to GLB: {export_file_str}")
            export_path = Path(export_file_str)
            if not export_path.is_absolute(): export_path = PROJECT_ROOT / export_path
            export_path.parent.mkdir(parents=True, exist_ok=True)

            bpy.ops.object.select_all(action='DESELECT')
            parent_empty.select_set(True)
            for child in parent_empty.children_recursive: child.select_set(True)
            bpy.context.view_layer.objects.active = parent_empty
            try:
                bpy.ops.export_scene.gltf(filepath=str(export_path.resolve()), export_format='GLB', use_selection=True, export_apply=True, export_materials='EXPORT', export_texcoords=True, export_normals=True, export_cameras=False, export_lights=False)
                print(f"      Successfully exported to '{export_path.resolve()}'")
            except RuntimeError as e_export: print(f"      [Error] Failed to export GLB for '{compose_name}': {e_export}")
        else: print(f"    [Warning] EXPORT for '{compose_name}' missing format/file or not 'glb'.")
    pri
nt(f"    ✅ Finished ZW-COMPOSE assembly: {compose_name}")

def safe_eval(str_val, default_val):
    if not isinstance(str_val, str): return default_val
    try: return eval(str_val)
    except (SyntaxError, NameError, TypeError, ValueError) as e:
        print(f"    {P_WARN} Could not evaluate string '{str_val}' for attribute: {e}. Using default: {default_val}")
        return default_val

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
                 target_obj[f"ZW_{key.upper()}"] = value
            else:
                target_obj[f"ZW_{key.upper()}"] = str(value)
            print(f"    Set custom property ZW_{key.upper()} on {target_obj.name}")
        except Exception as e:
            print(f"    [Error] Failed to set custom property ZW_{key.upper()} on {target_obj.name}: {e}")

# --- New ZW-COMPOSE-TEMPLATE Handler ---
def handle_zw_compose_template_block(template_data: dict):
    if not bpy: return
    template_name = template_data.get("NAME", "UnnamedZWTemplate")
    print(f"  Storing ZW-COMPOSE-TEMPLATE: {template_name}")

    text_block_name = f"ZW_Template_{template_name}"
    text_block = bpy.data.texts.get(text_block_name)
    if not text_block:
        text_block = bpy.data.texts.new(name=text_block_name)

    try:
        template_json_string = json.dumps(template_data, indent=2)
        text_block.from_string(template_json_string)
        print(f"    Stored template '{template_name}' in Text block '{text_block_name}'.")
        scene_prop_name = f"ZW_TEMPLATE_{template_name.upper()}"
        bpy.context.scene[scene_prop_name] = template_json_string
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

        if len(mesh_obj.data.materials) == 0:
            mesh_obj.data.materials.append(mat)
        else:
            mesh_obj.data.materials[0] = mat

        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if not bsdf:
            bsdf = mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
            output_node = mat.node_tree.nodes.get('Material Output') or mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
            mat.node_tree.links.new(bsdf.outputs['BSDF'], output_node.inputs['Surface'])

        if "BASE_COLOR" in material_def: bsdf.inputs["Base Color"].default_value = parse_color(material_def["BASE_COLOR"])

        emission_strength = float(material_def.get("EMISSION", material_def.get("EMISSION_STRENGTH", 0.0)))
        bsdf.inputs["Emission Strength"].default_value = emission_strength
        if emission_strength > 0:
             bsdf.inputs["Emission Color"].default_value = parse_color(material_def.get("EMISSION_COLOR", (0,0,0,1)))

        if "ROUGHNESS" in material_def: bsdf.inputs["Roughness"].default_value = float(material_def["ROUGHNESS"])
        if "METALLIC" in material_def: bsdf.inputs["Metallic"].default_value = float(material_def["METALLIC"])
        if "TRANSMISSION" in material_def: bsdf.inputs["Transmission"].default_value = float(material_def["TRANSMISSION"])
        if "ALPHA" in material_def: bsdf.inputs["Alpha"].default_value = float(material_def["ALPHA"])
        if "SPECULAR" in material_def: bsdf.inputs["Specular IOR Level"].default_value = float(material_def["SPECULAR"])


    metadata_dict = mesh_data.get("METADATA")
    if isinstance(metadata_dict, dict):
        handle_zw_metadata_block(metadata_dict, target_obj_name=mesh_obj.name)

    explicit_coll_name = mesh_data.get("COLLECTION")
    target_collection = current_bpy_collection
    if explicit_coll_name:
        target_collection = get_or_create_collection(explicit_coll_name, bpy.context.scene.collection)

    current_obj_collections = [c for c in mesh_obj.users_collection]
    for c in current_obj_collections: c.objects.unlink(mesh_obj)
    if mesh_obj.name not in target_collection.objects: target_collection.objects.link(mesh_obj)
    print(f"    Linked '{mesh_obj.name}' to collection '{target_collection.name}'")

    print(f"    ✅ Successfully created ZW-MESH (integrated): {mesh_name}")
    return mesh_obj

# --- ZW-COMPOSE Handler (Refined for object duplication and custom props) ---
def handle_zw_compose_block(compose_data: dict, default_collection: bpy.types.Collection):
    if not bpy:
        print("[Error] bpy module not available in handle_zw_compose_block. Cannot process ZW-COMPOSE.")
        return

    compose_name = compose_data.get("NAME", "ZWComposition")
    print(f"[*] Processing ZW-COMPOSE assembly: {compose_name}")

    bpy.ops.object.empty_add(type='PLAIN_AXES')
    parent_empty = bpy.context.active_object
    if not parent_empty:
        print(f"    [Error] Failed to create parent Empty for {compose_name}. Aborting ZW-COMPOSE.")
        return
    parent_empty.name = compose_name

    parent_empty.location = safe_eval(compose_data.get("LOCATION", "(0,0,0)"), (0,0,0))
    rot_deg = safe_eval(compose_data.get("ROTATION", "(0,0,0)"), (0,0,0))
    parent_empty.rotation_euler = Euler([math.radians(a) for a in rot_deg], 'XYZ')
    scale_eval = safe_eval(compose_data.get("SCALE", "(1,1,1)"), (1,1,1))
    parent_empty.scale = (scale_eval if isinstance(scale_eval, tuple) else (float(scale_eval), float(scale_eval), float(scale_eval)))
    print(f"    Parent Empty '{parent_empty.name}' transform: L={parent_empty.location}, R={parent_empty.rotation_euler}, S={parent_empty.scale}")

    comp_coll_name = compose_data.get("COLLECTION")
    target_collection_for_empty = default_collection
    if comp_coll_name:
        target_collection_for_empty = get_or_create_collection(comp_coll_name, parent_collection=bpy.context.scene.collection)

    current_collections = [coll for coll in parent_empty.users_collection]
    for coll in current_collections: coll.objects.unlink(parent_empty)
    if parent_empty.name not in target_collection_for_empty.objects:
        target_collection_for_empty.objects.link(parent_empty)
    print(f"    Parent Empty '{parent_empty.name}' linked to collection '{target_collection_for_empty.name}'")

    parent_empty["ZW_COMPOSE_NAME"] = compose_name
    parent_empty["ZW_TEMPLATE_SOURCE"] = compose_data.get("TEMPLATE_SOURCE", "Direct ZW-COMPOSE")
    parent_empty["ZW_ATTACHMENT_COUNT"] = len(compose_data.get("ATTACHMENTS", []))

    base_model_name = compose_data.get("BASE_MODEL")
    if base_model_name:
        original_base_obj = bpy.data.objects.get(base_model_name)
        if original_base_obj:
            bpy.ops.object.select_all(action='DESELECT')
            original_base_obj.select_set(True)
            bpy.context.view_layer.objects.active = original_base_obj
            bpy.ops.object.duplicate(linked=False)
            base_model_obj = bpy.context.active_object
            base_model_obj.name = f"{base_model_name}_base_of_{compose_name}"
            target_collection_for_empty.objects.link(base_model_obj)
            base_model_obj.parent = parent_empty
            base_model_obj.location, base_model_obj.rotation_euler, base_model_obj.scale = (0,0,0), (0,0,0), (1,1,1)
            base_model_obj["ZW_SLOT_ID"] = "BASE_MODEL"
            base_model_obj["ZW_ROLE"] = compose_data.get("BASE_MODEL_ROLE", "base_model")
            base_model_obj["ZW_SOURCE_OBJECT"] = base_model_name
            print(f"    Added BASE_MODEL: '{base_model_name}' as '{base_model_obj.name}'")
        else: print(f"    [Warning] BASE_MODEL object '{base_model_name}' not found.")

    attachments_list = compose_data.get("ATTACHMENTS", [])
    for i, attach_def in enumerate(attachments_list):
        if not isinstance(attach_def, dict): continue
        attach_obj_source_name = attach_def.get("OBJECT")
        original_attach_obj = bpy.data.objects.get(attach_obj_source_name)
        if original_attach_obj:
            bpy.ops.object.select_all(action='DESELECT')
            original_attach_obj.select_set(True)
            bpy.context.view_layer.objects.active = original_attach_obj
            bpy.ops.object.duplicate(linked=False)
            attached_obj = bpy.context.active_object
            attached_obj.name = f"{attach_obj_source_name}_attach{i}_to_{compose_name}"
            target_collection_for_empty.objects.link(attached_obj)
            attached_obj.parent = parent_empty

            attached_obj.location = safe_eval(attach_def.get("LOCATION", "(0,0,0)"), (0,0,0))
            attach_rot_deg = safe_eval(attach_def.get("ROTATION", "(0,0,0)"), (0,0,0))
            attached_obj.rotation_euler = Euler([math.radians(a) for a in attach_rot_deg], 'XYZ')
            attach_scale_eval = safe_eval(attach_def.get("SCALE", "(1,1,1)"), (1,1,1))
            attached_obj.scale = (attach_scale_eval if isinstance(attach_scale_eval, tuple) else (float(attach_scale_eval), float(attach_scale_eval), float(attach_scale_eval)))

            attached_obj["ZW_SLOT_ID"] = attach_def.get("SLOT_ID", f"ATTACHMENT_{i}")
            attached_obj["ZW_ROLE"] = attach_def.get("ROLE", "attachment")
            attached_obj["ZW_SOURCE_OBJECT"] = attach_obj_source_name
            print(f"      Added ATTACHMENT: '{attach_obj_source_name}' as '{attached_obj.name}'")

            material_override_def = attach_def.get("MATERIAL_OVERRIDE")
            if isinstance(material_override_def, dict):
                if ZW_MESH_UTILS_IMPORTED and APPLY_ZW_MATERIAL_FUNC:
                    print(f"        Applying MATERIAL_OVERRIDE to '{attached_obj.name}'")
                    if 'NAME' not in material_override_def:
                        material_override_def['NAME'] = f"{attached_obj.name}_OverrideMat"
                    APPLY_ZW_MATERIAL_FUNC(attached_obj, material_override_def)
                else: print(f"        [Warning] MATERIAL_OVERRIDE for '{attached_obj.name}' but zw_mesh.apply_material not imported.")
        else: print(f"      [Warning] ATTACHMENT source object '{attach_obj_source_name}' not found.")

    export_def = compose_data.get("EXPORT")
    if export_def and isinstance(export_def, dict):
        export_format = export_def.get("FORMAT", "").lower()
        export_file_str = export_def.get("FILE")
        if export_format == "glb" and export_file_str:
            print(f"    Exporting composition '{compose_name}' to GLB: {export_file_str}")
            export_path = Path(export_file_str)
            if not export_path.is_absolute(): export_path = PROJECT_ROOT / export_path
            export_path.parent.mkdir(parents=True, exist_ok=True)

            bpy.ops.object.select_all(action='DESELECT')
            parent_empty.select_set(True)
            for child in parent_empty.children_recursive: child.select_set(True)
            bpy.context.view_layer.objects.active = parent_empty
            try:
                bpy.ops.export_scene.gltf(filepath=str(export_path.resolve()), export_format='GLB', use_selection=True, export_apply=True, export_materials='EXPORT', export_texcoords=True, export_normals=True, export_cameras=False, export_lights=False)
                print(f"      Successfully exported to '{export_path.resolve()}'")
            except RuntimeError as e_export: print(f"      [Error] Failed to export GLB for '{compose_name}': {e_export}")
        else: print(f"    [Warning] EXPORT for '{compose_name}' missing format/file or not 'glb'.")
    print(f"    ✅ Finished ZW-COMPOSE assembly: {compose_name}")

def get_or_create_collection(name: str, parent_collection=None):
    if not bpy: return None
    clean_name = name.strip('"\' ') # Clean name for collection
    if not clean_name: clean_name = "Unnamed_ZW_Collection"

    if parent_collection is None: parent_collection = bpy.context.scene.collection

    existing_collection = parent_collection.children.get(clean_name)
    if existing_collection:
        print(f"    {P_INFO} Using existing collection: '{clean_name}' in '{parent_collection.name}'")
        return existing_collection
    else:
        new_collection = bpy.data.collections.new(name=clean_name)
        parent_collection.children.link(new_collection)
        print(f"    {P_INFO} Created new collection: '{clean_name}' in '{parent_collection.name}'")
        return new_collection

def parse_color(color_input, default_color=(0.8, 0.8, 0.8, 1.0)):
    if isinstance(color_input, str):
        s = color_input.strip()
        if s.startswith("#"):
            hex_color = s.lstrip("#")
            try:
                if len(hex_color) == 6: r, g, b = (int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4)); return (r, g, b, 1.0)
                elif len(hex_color) == 8: r, g, b, a = (int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4, 6)); return (r, g, b, a)
                else: print(f"    {P_WARN} Invalid hex color string length for '{s}'. Using default."); return default_color
            except ValueError:
                print(f"    {P_WARN} Invalid hex color string '{s}'. Using default.")
                return default_color
        elif s.startswith("(") and s.endswith(")"):
            try:
                parts = [float(p.strip()) for p in s.strip("()").split(",")];
                if len(parts) == 3: return (parts[0], parts[1], parts[2], 1.0)
                if len(parts) == 4: return tuple(parts)
                else:
                    print(f"    {P_WARN} Tuple-like color string '{s}' must have 3 or 4 components. Using default.")
                    return default_color
            except ValueError:
                print(f"    {P_WARN} Invalid tuple-like color string '{s}'. Using default.")
                return default_color
        else: # Unrecognized string format
            print(f"    {P_WARN} Unrecognized string color format '{color_input}'. Using default.")
            return default_color

    elif isinstance(color_input, (list, tuple)):
        if not all(isinstance(num, (int, float)) for num in color_input):
            print(f"    {P_WARN} Color list/tuple '{color_input}' contains non-numeric values. Using default.")
            return default_color
        if len(color_input) == 3:
            return (float(color_input[0]), float(color_input[1]), float(color_input[2]), 1.0)
        elif len(color_input) == 4:
            return (float(color_input[0]), float(color_input[1]), float(color_input[2]), float(color_input[3]))
        else:
            print(f"    {P_WARN} Color list/tuple '{color_input}' must have 3 or 4 components. Using default.")
            return default_color
    else: # Not a string, list, or tuple
        print(f"    {P_WARN} Unrecognized color input type '{type(color_input)}' for value '{color_input}'. Using default.")
        return default_color


def _apply_bsdf_properties(bsdf_node, properties_dict: dict, object_name_for_logging: str = ""):
    if not bpy or not bsdf_node or not properties_dict:
        return False

    log_prefix_obj = f"for ZW-OBJECT '{object_name_for_logging}'" if object_name_for_logging else "for material"
    print(f"    {P_INFO} Applying BSDF properties {log_prefix_obj}: {properties_dict}")
    base_color_set = False
    for key, value_any in properties_dict.items():
        bsdf_input_name = key.replace("_", " ").strip().title()
        if key.upper() == "ALPHA": bsdf_input_name = "Alpha"

        if bsdf_node.inputs.get(bsdf_input_name):
            try:
                if "Color" in bsdf_input_name:
                    parsed_color_val = parse_color(value_any)
                    bsdf_node.inputs[bsdf_input_name].default_value = parsed_color_val
                    if bsdf_input_name == "Base Color": base_color_set = True
                    print(f"        {P_INFO} Set BSDF.{bsdf_input_name} to {parsed_color_val}")
                elif isinstance(value_any, (int, float, str)):
                    try:
                        float_val = float(str(value_any).strip('"\' ')) # Strip quotes for string-numbers too
                        bsdf_node.inputs[bsdf_input_name].default_value = float_val
                        print(f"        {P_INFO} Set BSDF.{bsdf_input_name} to {float_val}")
                    except ValueError:
                        print(f"        {P_WARN} Could not convert value '{value_any}' to float for BSDF input {bsdf_input_name}.")
                else:
                    print(f"        {P_WARN} Unsupported value type '{type(value_any)}' for BSDF input {bsdf_input_name}.")
            except Exception as e_bsdf:
                print(f"        {P_WARN} Failed to set BSDF input {bsdf_input_name} with value '{value_any}': {e_bsdf}")
        else:
            print(f"        {P_WARN} BSDF input '{bsdf_input_name}' not found on node.")
    return base_color_set

def handle_zw_object_creation(obj_attributes: dict, parent_bpy_obj=None):
    if not bpy: return None
    obj_type_raw = obj_attributes.get("TYPE", "").strip('"\' ')
    if not obj_type_raw: print(f"    {P_WARN} Missing or invalid 'TYPE' in ZW-OBJECT attributes after stripping. Skipping."); return None
    obj_type_normalized = obj_type_raw.title()

    obj_name_default = obj_type_normalized
    obj_name = obj_attributes.get("NAME", obj_name_default).strip('"\' ')
    if not obj_name: obj_name = obj_name_default

    loc_tuple = safe_eval(obj_attributes.get("LOCATION", "(0,0,0)"), (0,0,0))
    scale_str = obj_attributes.get("SCALE", "(1,1,1)")

    PRIMITIVE_MAP = {
        "Cube": bpy.ops.mesh.primitive_cube_add, "Sphere": bpy.ops.mesh.primitive_uv_sphere_add,
        "Plane": bpy.ops.mesh.primitive_plane_add, "Cone": bpy.ops.mesh.primitive_cone_add,
        "Cylinder": bpy.ops.mesh.primitive_cylinder_add, "Torus": bpy.ops.mesh.primitive_torus_add,
        "Grid": bpy.ops.mesh.primitive_grid_add, "Monkey": bpy.ops.mesh.primitive_monkey_add,
    }

    if isinstance(scale_str, (int, float)): scale_tuple = (float(scale_str), float(scale_str), float(scale_str))
    elif isinstance(scale_str, str):
        eval_scale = safe_eval(scale_str, (1,1,1))
        if isinstance(eval_scale, (int, float)): scale_tuple = (float(eval_scale), float(eval_scale), float(eval_scale))
        elif isinstance(eval_scale, tuple) and len(eval_scale) == 3: scale_tuple = eval_scale
        else: scale_tuple = (1,1,1); print(f"    {P_WARN} Invalid SCALE format '{scale_str}'. Defaulting to (1,1,1).")
    else: scale_tuple = (1,1,1); print(f"    {P_WARN} Invalid SCALE type '{type(scale_str)}'. Defaulting to (1,1,1).")

    created_bpy_obj = None
    operator_func = PRIMITIVE_MAP.get(obj_type_normalized)
    original_requested_type = obj_type_normalized # Store for logging in case of fallback

    try:
        if operator_func:
            print(f"{P_INFO} Creating ZW-OBJECT: NAME='{obj_name}', TYPE='{obj_type_normalized}' (Operator: {operator_func.__name__}), LOC={loc_tuple}, SCALE={scale_tuple}")
            operator_func(location=loc_tuple)
        else:
            print(f"    {P_WARN} Unrecognized ZW-OBJECT TYPE='{original_requested_type}'. Defaulting to 'Cube'.")
            print(f"{P_INFO} Creating ZW-OBJECT: NAME='{obj_name}', TYPE='Cube' (fallback for '{original_requested_type}'), LOC={loc_tuple}, SCALE={scale_tuple}")
            bpy.ops.mesh.primitive_cube_add(location=loc_tuple)
            obj_type_normalized = "Cube"

        created_bpy_obj = bpy.context.object
        if created_bpy_obj:
            created_bpy_obj.name = obj_name; created_bpy_obj.scale = scale_tuple
            actual_blender_type = created_bpy_obj.data.name.split('.')[0] if '.' in created_bpy_obj.data.name else created_bpy_obj.data.name
            print(f"    {P_SUCCESS} Created Blender object: '{created_bpy_obj.name}' (Blender Type: '{actual_blender_type}', Requested ZW TYPE: '{original_requested_type}')")

            if parent_bpy_obj:
                bpy.ops.object.select_all(action='DESELECT'); created_bpy_obj.select_set(True); parent_bpy_obj.select_set(True)
                bpy.context.view_layer.objects.active = parent_bpy_obj
                try: bpy.ops.object.parent_set(type='OBJECT', keep_transform=True); print(f"        {P_INFO} Parented '{created_bpy_obj.name}' to '{parent_bpy_obj.name}'")
                except RuntimeError as e: print(f"        {P_ERROR} Parenting failed: {e}")

            if hasattr(created_bpy_obj.data, 'materials'):
                material_attr = obj_attributes.get("MATERIAL")
                inline_material_data = None; final_mat_name = None
                color_set_by_material_processing = False

                if isinstance(material_attr, dict):
                    print(f"    {P_INFO} Processing inline MATERIAL definition for '{obj_name}'")
                    inline_material_data = material_attr
                    explicit_material_name_str = obj_attributes.get("MATERIAL_NAME")
                    if isinstance(explicit_material_name_str, str) and explicit_material_name_str.strip('"\' '):
                        final_mat_name = explicit_material_name_str.strip('"\' ')
                        print(f"        {P_INFO} Using explicit MATERIAL_NAME: '{final_mat_name}' for inline material.")
                    else: final_mat_name = f"{obj_name}_InlineMat"; print(f"        {P_INFO} Generated material name: '{final_mat_name}' for inline material.")
                elif isinstance(material_attr, str): final_mat_name = material_attr.strip('"\' ')
                else: final_mat_name = f"{obj_name}_Mat"
                if not final_mat_name: final_mat_name = f"{obj_name}_FallbackMat" # Ensure name if stripping leads to empty

                mat = bpy.data.materials.get(final_mat_name) or bpy.data.materials.new(name=final_mat_name)
                print(f"    {P_INFO} Using material: '{final_mat_name}' (New: {final_mat_name not in bpy.data.materials})")

                mat.use_nodes = True; nodes = mat.node_tree.nodes; links = mat.node_tree.links
                bsdf = nodes.get("Principled BSDF") or nodes.new(type='ShaderNodeBsdfPrincipled')
                out_node = nodes.get('Material Output') or nodes.new(type='ShaderNodeOutputMaterial')
                if not any(link.from_node == bsdf and link.to_node == out_node for link in links):
                    links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])

                if inline_material_data:
                    color_set_by_material_processing = _apply_bsdf_properties(bsdf, inline_material_data, obj_name)
                else:
                    bsdf_data_attr = obj_attributes.get("BSDF")
                    if isinstance(bsdf_data_attr, dict):
                        color_set_by_material_processing = _apply_bsdf_properties(bsdf, bsdf_data_attr, obj_name)
                    if not color_set_by_material_processing:
                        color_str_attr = obj_attributes.get("COLOR")
                        if isinstance(color_str_attr, str):
                            pc_val = parse_color(color_str_attr)
                            bsdf.inputs["Base Color"].default_value = pc_val
                            print(f"        {P_INFO} Set Base Color to {pc_val} (from ZW-OBJECT.COLOR attribute)")

                if not created_bpy_obj.data.materials: created_bpy_obj.data.materials.append(mat)
                else: created_bpy_obj.data.materials[0] = mat
                print(f"    {P_INFO} Assigned material '{final_mat_name}' to '{created_bpy_obj.name}'")

                bpy.ops.object.select_all(action='DESELECT'); created_bpy_obj.select_set(True)
                elif shade_str_processed == "Flat": bpy.ops.object.shade_flat(); print(f"        {P_INFO} Set shading to Flat.")
        else: print(f"    {P_ERROR} Object creation did not result in an active object."); return None
    except Exception as e: print(f"    {P_ERROR} Error creating Blender object '{obj_name}': {e}"); return None
    return created_bpy_obj

def apply_array_gn(source_obj: bpy.types.Object, params: dict):
    if not bpy or not source_obj: print(f"{P_WARN} ARRAY: bpy or source_obj missing. Skipping."); return
    print(f"{P_INFO} Applying ARRAY GN to '{source_obj.name}' with {params}")
    host_name = f"{source_obj.name}_ArrayHost"; host_obj = bpy.data.objects.new(host_name, None)
    src_coll = source_obj.users_collection[0] if source_obj.users_collection else bpy.context.scene.collection
    src_coll.objects.link(host_obj); print(f"    {P_INFO} Created ARRAY host '{host_name}' in '{src_coll.name}'")
    mod = host_obj.modifiers.new(name="ZW_Array", type='NODES')
    tree_name = f"ZW_Array_{source_obj.name}_GN"; gn_tree = bpy.data.node_groups.get(tree_name)
    if not gn_tree:
        gn_tree = bpy.data.node_groups.new(name=tree_name, type='GeometryNodeTree'); print(f"    {P_INFO} Created GN Tree: {tree_name}")
        nodes = gn_tree.nodes; links = gn_tree.links; nodes.clear()
        inp = nodes.new(type='NodeGroupInput'); inp.location=(-400,0); outp = nodes.new(type='NodeGroupOutput'); outp.location=(400,0)
        gn_tree.outputs.new('NodeSocketGeometry', 'Geometry')
        obj_info = nodes.new('GeometryNodeObjectInfo'); obj_info.location=(-200,200); obj_info.inputs['Object'].default_value=source_obj
        line = nodes.new('NodeGeometryMeshLine'); line.location=(-200,-100)
        line.mode = 'OFFSET'; line.inputs['Count'].default_value = int(str(params.get("COUNT",5)).strip('"\' '))
        line.inputs['Offset'].default_value = safe_eval(str(params.get("OFFSET","(0,0,1)")),"(0,0,1)")
        inst = nodes.new('GeometryNodeInstanceOnPoints'); inst.location=(0,0)
        links.new(line.outputs['Mesh'], inst.inputs['Points']); links.new(obj_info.outputs['Geometry'], inst.inputs['Instance'])
        mode_str = str(params.get("MODE","INSTANCE")).strip('"\' ').upper()
        if mode_str == "REALIZE":
            realize = nodes.new('GeometryNodeRealizeInstances'); realize.location=(200,0)
            links.new(inst.outputs['Instances'],realize.inputs['Geometry']); links.new(realize.outputs['Geometry'],outp.inputs['Geometry'])
        else: links.new(inst.outputs['Instances'],outp.inputs['Geometry'])
    else: print(f"    {P_INFO} Reusing GN Tree: {tree_name}")
    mod.node_group = gn_tree; bpy.context.view_layer.objects.active = host_obj; host_obj.select_set(True)
    print(f"    {P_SUCCESS} Applied ARRAY to '{host_name}'")

def apply_displace_noise_gn(target_obj: bpy.types.Object, params: dict):
                bpy.context.view_layer.objects.active = created_bpy_obj
                shade_str_raw = obj_attributes.get("SHADING", "Smooth")
                shade_str_processed = str(shade_str_raw).strip('"\' ').strip().title() if isinstance(shade_str_raw, str) else "Smooth"
                if shade_str_processed == "Smooth": bpy.ops.object.shade_smooth(); print(f"        {P_INFO} Set shading to Smooth.")
    if not bpy or not target_obj or target_obj.type != 'MESH': print(f"{P_WARN} DISPLACE: Target '{target_obj.name if target_obj else 'None'}' not a MESH. Skipping."); return
    print(f"{P_INFO} Applying DISPLACE_NOISE GN to '{target_obj.name}' with {params}")
    mod = target_obj.modifiers.new(name="ZW_DisplaceNoise", type='NODES')
    tree_name = f"ZW_Displace_{target_obj.name}_GN"; gn_tree = bpy.data.node_groups.get(tree_name)
    if not gn_tree:
        gn_tree = bpy.data.node_groups.new(name=tree_name, type='GeometryNodeTree'); print(f"    {P_INFO} Created GN Tree: {tree_name}")
        nodes=gn_tree.nodes; links=gn_tree.links; nodes.clear()
        inp=nodes.new('NodeGroupInput'); inp.location=(-600,0); outp=nodes.new('NodeGroupOutput'); outp.location=(400,0)
        gn_tree.inputs.new('NodeSocketGeometry','Geometry'); gn_tree.outputs.new('NodeSocketGeometry','Geometry')
        set_pos=nodes.new('GeometryNodeSetPosition'); set_pos.location=(0,0)
        noise=nodes.new('ShaderNodeTexNoise'); noise.location=(-400,-200); noise.noise_dimensions='3D'
        noise.inputs['Scale'].default_value=float(str(params.get("SCALE",5.0)).strip('"\' '))
        noise.inputs['W'].default_value=float(str(params.get("SEED",0.0)).strip('"\' '))
        norm=nodes.new('GeometryNodeInputNormal'); norm.location=(-400,0)
        str_scale=nodes.new('ShaderNodeMath'); str_scale.operation='MULTIPLY'; str_scale.location=(-200,-200)
        str_scale.inputs[1].default_value=float(str(params.get("STRENGTH",0.5)).strip('"\' ')); links.new(noise.outputs['Fac'],str_scale.inputs[0])
        axis=str(params.get("AXIS","NORMAL")).strip('"\' ').upper(); offset_src_node=None
        if axis in ['X','Y','Z']:
            comb_xyz=nodes.new('ShaderNodeCombineXYZ'); comb_xyz.location=(-200,200)
            if axis=='X': links.new(str_scale.outputs['Value'],comb_xyz.inputs['X'])
            elif axis=='Y': links.new(str_scale.outputs['Value'],comb_xyz.inputs['Y'])
            else: links.new(str_scale.outputs['Value'],comb_xyz.inputs['Z'])
            offset_src_node=comb_xyz
        else: # NORMAL
            vec_mult=nodes.new('ShaderNodeVectorMath'); vec_mult.operation='MULTIPLY'; vec_mult.location=(-200,0)
            links.new(norm.outputs['Normal'],vec_mult.inputs[0]); links.new(str_scale.outputs['Value'],vec_mult.inputs[1])
            offset_src_node=vec_mult; print(f"    {P_INFO} Displacing along Normal.")
        links.new(offset_src_node.outputs['Vector'],set_pos.inputs['Offset'])
        links.new(inp.outputs['Geometry'],set_pos.inputs['Geometry']); links.new(set_pos.outputs['Geometry'],outp.inputs['Geometry'])
    else: print(f"    {P_INFO} Reusing GN Tree: {tree_name}")
    mod.node_group=gn_tree; bpy.context.view_layer.objects.active=target_obj; target_obj.select_set(True)
    print(f"    {P_SUCCESS} Applied DISPLACE_NOISE to '{target_obj.name}'")

def handle_zw_animation_block(anim_data: dict):
    if not bpy: return
    target_obj_name = str(anim_data.get("TARGET_OBJECT","")).strip('"\' ')
    prop_path = str(anim_data.get("PROPERTY_PATH","")).strip('"\' ')
    idx_str = anim_data.get("INDEX")
    unit = str(anim_data.get("UNIT","")).strip('"\' ').lower()
    interp_str = str(anim_data.get("INTERPOLATION","BEZIER")).strip('"\' ').upper()
    kf_list = anim_data.get("KEYFRAMES")

    default_anim_name_base_obj = target_obj_name if target_obj_name else "UnnamedTarget"
    default_anim_name_base_prop = prop_path if prop_path else "UnnamedProp"
    default_anim_name_for_log = f"{default_anim_name_base_obj}_{default_anim_name_base_prop}_Action"
    anim_name_for_log_raw = anim_data.get('NAME', default_anim_name_for_log)
    anim_name_for_log = str(anim_name_for_log_raw).strip('"\' ')
    if not anim_name_for_log: anim_name_for_log = default_anim_name_for_log

    if not target_obj_name:
        print(f"{P_WARN} ZW-ANIMATION '{anim_name_for_log}': Missing 'TARGET_OBJECT'. Skipping.")
        return
    if not prop_path:
        print(f"{P_WARN} ZW-ANIMATION '{anim_name_for_log}' for target '{target_obj_name}': Missing 'PROPERTY_PATH'. Skipping.")
        return
    if not kf_list:
        print(f"{P_WARN} ZW-ANIMATION '{anim_name_for_log}' for target '{target_obj_name}': 'KEYFRAMES' list is missing or empty. Skipping.")
        return
    if not isinstance(kf_list, list):
        print(f"{P_WARN} ZW-ANIMATION '{anim_name_for_log}' for target '{target_obj_name}': 'KEYFRAMES' is not a list (found type: {type(kf_list)}). Skipping.")
        return

    target_obj = bpy.data.objects.get(target_obj_name)
    if not target_obj: print(f"{P_WARN} ZW-ANIMATION target '{target_obj_name}' for animation '{anim_name_for_log}' not found. Skipping."); return

    if not target_obj.animation_data: target_obj.animation_data_create()

    act_name = anim_name_for_log
    if not target_obj.animation_data.action or \
       (target_obj.animation_data.action.name != act_name and anim_data.get("NAME")):
        target_obj.animation_data.action = bpy.data.actions.new(name=act_name)

    action = target_obj.animation_data.action
    prop_idx = None
    if idx_str is not None:
        try: prop_idx = int(idx_str)
        except ValueError: print(f"    {P_WARN} ZW-ANIMATION '{act_name}': Invalid INDEX '{idx_str}'. Ignoring."); prop_idx = None

    print(f"    {P_INFO} Animating '{target_obj.name}.{prop_path}' (Idx:{prop_idx if prop_idx is not None else 'All'}) using '{interp_str}' for action '{act_name}'")

    for kf_data in kf_list:
        if not isinstance(kf_data, dict):
            print(f"        {P_WARN} ZW-ANIMATION '{act_name}': Keyframe item is not a dictionary. Skipping item: {kf_data}")
            continue
        frame = kf_data.get("FRAME")
        val_in = kf_data.get("VALUE")

        if frame is None or val_in is None: print(f"        {P_WARN} ZW-ANIMATION '{act_name}': Keyframe missing FRAME/VALUE. Skipping: {kf_data}"); continue
        frame = float(frame)
        if prop_idx is not None:
            try:
                val = float(val_in)
                if unit=="degrees" and "rotation" in prop_path.lower(): val = math.radians(val)
                fc = action.fcurves.find(prop_path,index=prop_idx) or action.fcurves.new(prop_path,index=prop_idx,action_group=target_obj.name)
                kp = fc.keyframe_points.insert(frame,val); kp.interpolation = interp_str
            except ValueError: print(f"        {P_WARN} Invalid scalar VALUE '{val_in}'. Skipping KF.")
        else:
            pt = safe_eval(str(val_in),None)
            if isinstance(pt,tuple) and (len(pt)==3 or len(pt)==4):
                vals = [math.radians(c) if unit=="degrees" and "rotation" in prop_path.lower() else c for c in pt]
                for i,comp_v in enumerate(vals):
                    fc = action.fcurves.find(prop_path,index=i) or action.fcurves.new(prop_path,index=i,action_group=target_obj.name)
                    kp = fc.keyframe_points.insert(frame,comp_v); kp.interpolation = interp_str
            else: print(f"        {P_WARN} Invalid vector VALUE '{val_in}'. Skipping KF.")
    print(f"    {P_SUCCESS} Finished animation: {act_name}")

def handle_zw_driver_block(driver_data: dict):
    if not bpy: return
    src_name = str(driver_data.get("SOURCE_OBJECT","")).strip('"\' ')
    src_prop = str(driver_data.get("SOURCE_PROPERTY","")).strip('"\' ')
    tgt_name = str(driver_data.get("TARGET_OBJECT","")).strip('"\' ')
    tgt_prop = str(driver_data.get("TARGET_PROPERTY","")).strip('"\' ')
    expr = str(driver_data.get("EXPRESSION","var")).strip('"\' ')

    default_drv_name_base_tgt = tgt_name if tgt_name else "UnnamedTarget"
    default_drv_name_base_prop = tgt_prop if tgt_prop else "UnnamedProp"
    default_driver_name = f"ZWDriver_{default_drv_name_base_tgt}_{default_drv_name_base_prop}"

    drv_name_raw = driver_data.get("NAME", default_driver_name)
    drv_name = str(drv_name_raw).strip('"\' ')
    if not drv_name: drv_name = default_driver_name

    if not all([src_name,src_prop,tgt_name,tgt_prop]): print(f"{P_WARN} ZW-DRIVER '{drv_name}': Missing required fields. Skipping."); return

    src_obj = bpy.data.objects.get(src_name)
    tgt_obj = bpy.data.objects.get(tgt_name)
    if not src_obj: print(f"{P_WARN} ZW-DRIVER '{drv_name}': Source obj '{src_name}' not found. Skipping."); return
    if not tgt_obj: print(f"{P_WARN} ZW-DRIVER '{drv_name}': Target obj '{tgt_name}' not found. Skipping."); return
    print(f"{P_INFO} Creating ZW-DRIVER '{drv_name}': {src_name}.{src_prop} -> {tgt_name}.{tgt_prop}")
    try:
        path = tgt_prop; idx = -1
        if '[' in tgt_prop and tgt_prop.endswith(']'):
            parts = tgt_prop.split('['); path=parts[0]
            try: idx = int(parts[1].rstrip(']'))
            except ValueError: print(f"    {P_ERROR} Invalid index in TARGET_PROPERTY: {tgt_prop}. Skipping."); return
        fc = tgt_obj.driver_add(path,idx) if idx!=-1 else tgt_obj.driver_add(path)
        drv = fc.driver; drv.type='SCRIPTED'; drv.expression=expr
        var = drv.variables.new(); var.name="var"; var.type='SINGLE_PROP'
        var.targets[0].id_type='OBJECT'; var.targets[0].id=src_obj; var.targets[0].data_path=src_prop
        print(f"    {P_SUCCESS} Successfully created driver: '{drv_name}'")
    except Exception as e: print(f"    {P_ERROR} Error setting up driver '{drv_name}': {e}")

def handle_property_anim_track(target_obj: bpy.types.Object, track_data: dict):
    if not bpy: return
    track_name_for_log = str(track_data.get('NAME','UnnamedPropertyAnim')).strip('"\' ')
    if not target_obj:
        print(f"    {P_WARN} PROPERTY_ANIM '{track_name_for_log}': Target object is None. Skipping.")
        return

    property_path_str = str(track_data.get("PROPERTY_PATH","")).strip('"\' ')
    keyframes_list = track_data.get("KEYFRAMES")
    index_str = track_data.get("INDEX")
    unit_str = str(track_data.get("UNIT", "")).strip('"\' ').lower()
    interpolation_str = str(track_data.get("INTERPOLATION", "BEZIER")).strip('"\' ').upper()

    if not all([property_path_str, keyframes_list]):
        print(f"    {P_WARN} PROPERTY_ANIM '{track_name_for_log}' for '{target_obj.name}': Missing PROPERTY_PATH or KEYFRAMES. Skipping.")
        return
    if not isinstance(keyframes_list, list):
        print(f"    {P_WARN} PROPERTY_ANIM '{track_name_for_log}' for '{target_obj.name}': KEYFRAMES is not a list. Skipping.")
        return

    if not target_obj.animation_data: target_obj.animation_data_create()
    action_name_from_data_raw = track_data.get("ACTION_NAME")
    action_name_from_data = str(action_name_from_data_raw).strip('"\' ') if action_name_from_data_raw is not None else None

    default_action_name = f"{target_obj.name}_{property_path_str.replace('.','_').replace('[','_').replace(']','')}_PropAnimAction"
    final_action_name = action_name_from_data if action_name_from_data else default_action_name

    if not target_obj.animation_data.action or \
       (action_name_from_data and target_obj.animation_data.action.name != final_action_name):
        target_obj.animation_data.action = bpy.data.actions.new(name=final_action_name)
    action = target_obj.animation_data.action

    prop_idx = None
    if index_str is not None:
        try: prop_idx = int(str(index_str).strip('"\' ')) # Strip if index is accidentally quoted string
        except ValueError:
            print(f"    {P_WARN} PROPERTY_ANIM '{track_name_for_log}' for '{target_obj.name}': Invalid INDEX '{index_str}'. Assuming non-indexed property.")
            prop_idx = None

    print(f"    {P_INFO} Animating '{target_obj.name}.{property_path_str}' (Index: {prop_idx if prop_idx is not None else 'All Components'}) using {interpolation_str} for action '{final_action_name}'")

    for kf_data in keyframes_list:
        if not isinstance(kf_data, dict):
            print(f"        {P_WARN} PROPERTY_ANIM '{track_name_for_log}': Keyframe data is not a dictionary. Skipping KF: {kf_data}")
            continue
        frame_input = kf_data.get("FRAME"); value_input = kf_data.get("VALUE")
        if frame_input is None or value_input is None:
            print(f"        {P_WARN} PROPERTY_ANIM '{track_name_for_log}': Keyframe missing FRAME or VALUE. Skipping KF: {kf_data}")
            continue
        try: frame = float(str(frame_input).strip('"\' '))
        except ValueError: print(f"        {P_WARN} PROPERTY_ANIM '{track_name_for_log}': Invalid FRAME '{frame_input}'. Skipping KF."); continue

        if prop_idx is not None:
            try:
                current_value = float(str(value_input).strip('"\' '))
                if unit_str == "degrees" and "rotation" in property_path_str.lower(): current_value = math.radians(current_value)
                fcurve = action.fcurves.find(property_path_str, index=prop_idx) or action.fcurves.new(property_path_str, index=prop_idx, action_group=target_obj.name)
                kf_point = fcurve.keyframe_points.insert(frame, current_value); kf_point.interpolation = interpolation_str
            except ValueError: print(f"        {P_WARN} PROPERTY_ANIM '{track_name_for_log}': Invalid scalar VALUE '{value_input}'. Skipping KF.")
            except Exception as e: print(f"        {P_ERROR} PROPERTY_ANIM '{track_name_for_log}': Failed to insert scalar keyframe for {property_path_str}[{prop_idx}]: {e}")
        else:
            value_tuple = safe_eval(str(value_input), None)
            if not isinstance(value_tuple, (tuple, list)):
                try: # Try as single float if not a tuple/list string
                    current_value = float(str(value_input).strip('"\' '))
                    fcurve = action.fcurves.find(property_path_str) or action.fcurves.new(property_path_str, action_group=target_obj.name)
                    kf_point = fcurve.keyframe_points.insert(frame, current_value); kf_point.interpolation = interpolation_str
                except ValueError: print(f"        {P_WARN} PROPERTY_ANIM '{track_name_for_log}': VALUE '{value_input}' is not a valid tuple/list or single float. Skipping KF.")
                except Exception as e: print(f"        {P_ERROR} PROPERTY_ANIM '{track_name_for_log}': Failed to insert non-indexed keyframe for {property_path_str}: {e}")
                continue
            if isinstance(value_tuple, (tuple, list)):
                for i, component_val in enumerate(value_tuple):
                    try:
                        current_comp_value = float(str(component_val).strip('"\' '))
                        if unit_str == "degrees" and "rotation" in property_path_str.lower(): current_comp_value = math.radians(current_comp_value)
                        fcurve = action.fcurves.find(property_path_str, index=i) or action.fcurves.new(property_path_str, index=i, action_group=target_obj.name)
                        kf_point = fcurve.keyframe_points.insert(frame, current_comp_value); kf_point.interpolation = interpolation_str
                    except ValueError: print(f"        {P_WARN} PROPERTY_ANIM '{track_name_for_log}': Invalid component VALUE '{component_val}' in '{value_tuple}'. Skipping component.")
                    except Exception as e: print(f"        {P_ERROR} PROPERTY_ANIM '{track_name_for_log}': Failed to insert component keyframe for {property_path_str}[{i}]: {e}")
    print(f"    {P_SUCCESS} Finished property animation for: {target_obj.name}.{property_path_str}")

def handle_material_override_track(target_obj: bpy.types.Object, track_data: dict):
    if not bpy: return
    track_name_for_log = str(track_data.get('NAME','UnnamedMaterialOverride')).strip('"\' ')
    if not target_obj:
        print(f"    {P_WARN} MATERIAL_OVERRIDE '{track_name_for_log}': Target object is None. Skipping.")
        return

    material_name_to_assign_str = str(track_data.get("MATERIAL_NAME","")).strip('"\' ')
    start_frame_str = str(track_data.get("START_FRAME", "0")).strip('"\' ')
    end_frame_raw = track_data.get("END_FRAME")
    end_frame_int_str = str(end_frame_raw).strip('"\' ') if end_frame_raw is not None else None
    restore_on_end_str = str(track_data.get("RESTORE_ON_END", "false")).strip('"\' ').lower()

    if not material_name_to_assign_str:
        print(f"    {P_WARN} MATERIAL_OVERRIDE '{track_name_for_log}' for '{target_obj.name}': Missing MATERIAL_NAME. Skipping.")
        return
    try: start_frame_int = int(start_frame_str)
    except ValueError: print(f"    {P_WARN} MATERIAL_OVERRIDE '{track_name_for_log}' for '{target_obj.name}': Invalid START_FRAME '{start_frame_str}'. Using 0."); start_frame_int = 0
    end_frame_int = None
    if end_frame_int_str is not None:
        try: end_frame_int = int(end_frame_int_str)
        except ValueError: print(f"    {P_WARN} MATERIAL_OVERRIDE '{track_name_for_log}' for '{target_obj.name}': Invalid END_FRAME '{end_frame_int_str}'. Restoration may not occur.")
    restore = (restore_on_end_str == 'true')

    if not target_obj.material_slots:
        print(f"    {P_INFO} MATERIAL_OVERRIDE '{track_name_for_log}' for '{target_obj.name}': Object has no material slots. Appending one.")
        target_obj.material_slots.new('')
    if not target_obj.material_slots:
        print(f"    {P_ERROR} MATERIAL_OVERRIDE '{track_name_for_log}' for '{target_obj.name}': Failed to ensure material slot. Skipping.")
        return

    new_mat = bpy.data.materials.get(material_name_to_assign_str)
    if not new_mat:
        new_mat = bpy.data.materials.new(name=material_name_to_assign_str); new_mat.use_nodes = True
        print(f"    {P_INFO} MATERIAL_OVERRIDE '{track_name_for_log}' for '{target_obj.name}': Created new material '{material_name_to_assign_str}'.")
    else: print(f"    {P_INFO} MATERIAL_OVERRIDE '{track_name_for_log}' for '{target_obj.name}': Using existing material '{material_name_to_assign_str}'.")
    original_mat = None
    if restore and target_obj.material_slots[0].material:
        original_mat = target_obj.material_slots[0].material
        print(f"    {P_INFO} MATERIAL_OVERRIDE '{track_name_for_log}' for '{target_obj.name}': Original material '{original_mat.name}' stored for restoration.")
    elif restore: print(f"    {P_INFO} MATERIAL_OVERRIDE '{track_name_for_log}' for '{target_obj.name}': Restoration requested, but no original material in slot 0.")
    slot_path = "material_slots[0].material"
    if restore and original_mat and start_frame_int > 0:
        pre_switch_frame = start_frame_int - 1
        if pre_switch_frame < 0: pre_switch_frame = 0
        if target_obj.material_slots[0].material != original_mat or \
           (target_obj.material_slots[0].material == original_mat and not target_obj.animation_data):
            target_obj.material_slots[0].material = original_mat
            try:
                kp = target_obj.keyframe_insert(data_path=slot_path, frame=pre_switch_frame)
                if kp: kp.interpolation = 'CONSTANT'
                print(f"        {P_INFO} Keyframed original material '{original_mat.name}' at frame {pre_switch_frame} for '{target_obj.name}'.")
            except RuntimeError as e: print(f"        {P_WARN} Failed to keyframe original material at pre-switch frame for '{target_obj.name}': {e}")
    target_obj.material_slots[0].material = new_mat
    try:
        kp = target_obj.keyframe_insert(data_path=slot_path, frame=start_frame_int)
        if kp: kp.interpolation = 'CONSTANT'
        print(f"    {P_INFO} Set and keyframed material of '{target_obj.name}' to '{new_mat.name}' at frame {start_frame_int}.")
    except RuntimeError as e: print(f"    {P_WARN} Failed to keyframe new material for '{target_obj.name}': {e}")
    if restore and original_mat and end_frame_int is not None and end_frame_int > start_frame_int:
        target_obj.material_slots[0].material = original_mat
        try:
            kp = target_obj.keyframe_insert(data_path=slot_path, frame=end_frame_int)
            if kp: kp.interpolation = 'CONSTANT'
            print(f"    {P_INFO} Restored and keyframed material of '{target_obj.name}' to '{original_mat.name}' at frame {end_frame_int}.")
        except RuntimeError as e: print(f"    {P_WARN} Failed to keyframe restored material for '{target_obj.name}': {e}")
    print(f"    {P_SUCCESS} Finished material override '{track_name_for_log}' for: {target_obj.name}")

def handle_shader_switch_track(target_obj: bpy.types.Object, track_data: dict):
    if not bpy: return
    track_name_for_log = str(track_data.get('NAME','UnnamedShaderSwitch')).strip('"\' ')
    if not target_obj:
        print(f"    {P_WARN} SHADER_SWITCH '{track_name_for_log}': Target object is None. Skipping.")
        return

    material_name_str_raw = track_data.get("MATERIAL_NAME")
    material_name_str = str(material_name_str_raw).strip('"\' ') if material_name_str_raw is not None else None
    target_node_name_str = str(track_data.get("TARGET_NODE","")).strip('"\' ')
    input_name_str = str(track_data.get("INPUT_NAME","")).strip('"\' ')
    new_value_any_type = track_data.get("NEW_VALUE")
    frame_str = str(track_data.get("FRAME", "0")).strip('"\' ')

    if not all([target_node_name_str, input_name_str, new_value_any_type is not None]):
        print(f"    {P_WARN} SHADER_SWITCH '{track_name_for_log}' for '{target_obj.name}': Missing TARGET_NODE, INPUT_NAME, or NEW_VALUE. Skipping.")
        return
    try: frame_int = int(frame_str)
    except ValueError: print(f"    {P_WARN} SHADER_SWITCH '{track_name_for_log}' for '{target_obj.name}': Invalid FRAME '{frame_str}'. Using 0."); frame_int = 0
    mat_to_modify = None
    if material_name_str:
        mat_candidate = bpy.data.materials.get(material_name_str)
        if mat_candidate:
            is_on_object = any(slot.material == mat_candidate for slot in target_obj.material_slots)
            if is_on_object: mat_to_modify = mat_candidate
            else: print(f"    {P_WARN} SHADER_SWITCH '{track_name_for_log}': Material '{material_name_str}' found but not on object '{target_obj.name}'. Trying active/first.")
        else: print(f"    {P_WARN} SHADER_SWITCH '{track_name_for_log}': Specified MATERIAL_NAME '{material_name_str}' not found. Trying active/first.")
    if not mat_to_modify and target_obj.active_material:
        mat_to_modify = target_obj.active_material; print(f"    {P_INFO} SHADER_SWITCH '{track_name_for_log}': Using active material '{mat_to_modify.name}' of '{target_obj.name}'.")
    if not mat_to_modify and target_obj.material_slots and target_obj.material_slots[0].material:
        mat_to_modify = target_obj.material_slots[0].material; print(f"    {P_INFO} SHADER_SWITCH '{track_name_for_log}': Using material '{mat_to_modify.name}' from slot 0 of '{target_obj.name}'.")
    if not mat_to_modify: print(f"    {P_WARN} SHADER_SWITCH '{track_name_for_log}' for '{target_obj.name}': No suitable material found. Skipping."); return
    if not mat_to_modify.use_nodes or not mat_to_modify.node_tree:
        print(f"    {P_WARN} SHADER_SWITCH '{track_name_for_log}': Material '{mat_to_modify.name}' on '{target_obj.name}' does not use nodes or has no node tree. Skipping."); return
    target_node = mat_to_modify.node_tree.nodes.get(target_node_name_str)
    if not target_node: print(f"    {P_WARN} SHADER_SWITCH '{track_name_for_log}': Target node '{target_node_name_str}' not found in material '{mat_to_modify.name}'. Skipping."); return
    socket_input = target_node.inputs.get(input_name_str)
    if not socket_input: print(f"    {P_WARN} SHADER_SWITCH '{track_name_for_log}': Input socket '{input_name_str}' not found on node '{target_node_name_str}'. Skipping."); return
    parsed_value = None
    try:
        if socket_input.type == 'RGBA': parsed_value = parse_color(new_value_any_type) # Already handles str() if needed
        elif socket_input.type == 'VALUE': parsed_value = float(str(new_value_any_type).strip('"\' '))
        elif socket_input.type == 'VECTOR':
            if isinstance(new_value_any_type, str): parsed_value = safe_eval(new_value_any_type, (0,0,0))
            elif isinstance(new_value_any_type, (list, tuple)) and len(new_value_any_type) == 3 and all(isinstance(n, (int,float)) for n in new_value_any_type):
                parsed_value = tuple(float(n) for n in new_value_any_type)
            else: print(f"    {P_WARN} SHADER_SWITCH '{track_name_for_log}': Vector value '{new_value_any_type}' for '{input_name_str}' is not valid. Using (0,0,0)."); parsed_value = (0,0,0)
        elif socket_input.type == 'INT': parsed_value = int(str(new_value_any_type).strip('"\' '))
        elif socket_input.type == 'BOOLEAN':
            if isinstance(new_value_any_type, str): parsed_value = new_value_any_type.strip('"\' ').lower() == 'true'
            else: parsed_value = bool(new_value_any_type)
        else: print(f"    {P_WARN} SHADER_SWITCH '{track_name_for_log}': Unsupported socket type '{socket_input.type}' for input '{input_name_str}'. Skipping."); return
    except ValueError as e: print(f"    {P_WARN} SHADER_SWITCH '{track_name_for_log}': Error parsing NEW_VALUE '{new_value_any_type}' for socket type '{socket_input.type}': {e}. Skipping."); return
    if parsed_value is None and socket_input.type != 'BOOLEAN':
         print(f"    {P_WARN} SHADER_SWITCH '{track_name_for_log}': Parsed value is None for NEW_VALUE '{new_value_any_type}'. This might be an error. Proceeding if socket allows.")
    try:
        socket_input.default_value = parsed_value
        kp = socket_input.keyframe_insert(data_path="default_value", frame=frame_int)
        if kp: kp.interpolation = 'CONSTANT'
        print(f"    {P_INFO} Set and keyframed material '{mat_to_modify.name}' node '{target_node_name_str}'.{input_name_str} to {parsed_value} at frame {frame_int}.")
    except Exception as e: print(f"    {P_ERROR} SHADER_SWITCH '{track_name_for_log}': Failed to set/keyframe socket '{input_name_str}': {e}")
    print(f"    {P_SUCCESS} Finished shader switch '{track_name_for_log}' for: {target_obj.name} on material {mat_to_modify.name}")

def handle_zw_camera_block(camera_data: dict, current_bpy_collection: bpy.types.Collection):
    if not bpy: return
    name = str(camera_data.get("NAME","ZWCamera")).strip('"\' ')
    if not name: name = "ZWCamera"
    loc_str=camera_data.get("LOCATION","(0,0,0)"); rot_str=camera_data.get("ROTATION","(0,0,0)")
    fov=float(str(camera_data.get("FOV",50.0)).strip('"\' '))
    clip_start=float(str(camera_data.get("CLIP_START",0.1)).strip('"\' '))
    clip_end=float(str(camera_data.get("CLIP_END",1000.0)).strip('"\' '))
    track_tgt_name_raw = camera_data.get("TRACK_TARGET")
    track_tgt_name = str(track_tgt_name_raw).strip('"\' ') if track_tgt_name_raw is not None else None
    explicit_coll_raw = camera_data.get("COLLECTION")
    explicit_coll = str(explicit_coll_raw).strip('"\' ') if explicit_coll_raw is not None else None
    loc=safe_eval(loc_str,(0,0,0)); rot_deg=safe_eval(rot_str,(0,0,0)); rot_rad=tuple(math.radians(a) for a in rot_deg)
    print(f"{P_INFO} Creating Camera '{name}': LOC={loc}, ROT_RAD={rot_rad}, FOV_MM={fov}")
    try:
        bpy.ops.object.camera_add(location=loc,rotation=rot_rad); cam_obj=bpy.context.active_object
        if not cam_obj: print(f"    {P_ERROR} Failed to create camera object '{name}'."); return
        cam_obj.name=name; cam_data=cam_obj.data; cam_data.lens=fov; cam_data.clip_start=clip_start; cam_data.clip_end=clip_end
        print(f"    {P_INFO} Set camera data for '{name}'.")
        final_coll = get_or_create_collection(explicit_coll, bpy.context.scene.collection) if explicit_coll else current_bpy_collection
        if final_coll:
            for c in cam_obj.users_collection: c.objects.unlink(cam_obj)
            final_coll.objects.link(cam_obj); print(f"    {P_INFO} Linked '{name}' to collection '{final_coll.name}'")
        if track_tgt_name:
            track_to=bpy.data.objects.get(track_tgt_name)
            if track_to:
                constr=cam_obj.constraints.new(type='TRACK_TO'); constr.target=track_to
                constr.track_axis='TRACK_NEGATIVE_Z'; constr.up_axis='UP_Y'; print(f"    {P_INFO} Added 'TRACK_TO' constraint to '{track_tgt_name}'")
            else: print(f"    {P_WARN} Track target '{track_tgt_name}' not found.")
        print(f"    {P_SUCCESS} Successfully created camera '{name}'.")
    except Exception as e: print(f"    {P_ERROR} Failed to create/configure camera '{name}': {e}")

def handle_zw_light_block(light_data: dict, current_bpy_collection: bpy.types.Collection):
    if not bpy: return
    name=str(light_data.get("NAME","ZWLight")).strip('"\' ')
    if not name: name = "ZWLight"
    loc_str=light_data.get("LOCATION","(0,0,0)"); rot_str=light_data.get("ROTATION","(0,0,0)")
    type_str_raw = light_data.get("TYPE","POINT")
    type_str_normalized = str(type_str_raw).strip('"\' ').upper()
    color_input=light_data.get("COLOR","#FFFFFF")
    energy_raw = light_data.get("ENERGY",100.0 if type_str_normalized=="POINT" else 10.0 if type_str_normalized=="SPOT" else 1.0)
    energy=float(str(energy_raw).strip('"\' '))
    shadow_raw = str(light_data.get("SHADOW","true"))
    shadow=shadow_raw.strip('"\' ').lower()=="true"
    size_raw = light_data.get("SIZE",0.25 if type_str_normalized in ["POINT","SPOT"] else (0.1 if type_str_normalized=="SUN" else 1.0))
    size=float(str(size_raw).strip('"\' '))
    explicit_coll_raw=light_data.get("COLLECTION")
    explicit_coll = str(explicit_coll_raw).strip('"\' ') if explicit_coll_raw is not None else None
    loc=safe_eval(loc_str,(0,0,0)); rot_deg=safe_eval(rot_str,(0,0,0))
    rot_rad=tuple(math.radians(a) for a in rot_deg);
    color_rgba = parse_color(color_input)
    print(f"{P_INFO} Creating Light '{name}': TYPE={type_str_normalized}, LOC={loc}, ROT_RAD={rot_rad}, COLOR={color_rgba[:3]}, ENERGY={energy}")
    try:
        bpy_light_data=bpy.data.lights.new(name=f"{name}_data",type=type_str_normalized)
        bpy_light_data.color=color_rgba[:3]; bpy_light_data.energy=energy
        if hasattr(bpy_light_data,'use_shadow'): bpy_light_data.use_shadow=shadow
        if type_str_normalized in ['POINT','SPOT']: bpy_light_data.shadow_soft_size=size
        elif type_str_normalized=='AREA': bpy_light_data.size=size
        elif type_str_normalized=='SUN': bpy_light_data.angle=size
        light_obj=bpy.data.objects.new(name=name,object_data=bpy_light_data)
        light_obj.location=loc; light_obj.rotation_euler=rot_rad
        final_coll=get_or_create_collection(explicit_coll,bpy.context.scene.collection) if explicit_coll else current_bpy_collection
        if final_coll: final_coll.objects.link(light_obj); print(f"    {P_INFO} Linked '{name}' to collection '{final_coll.name}'")
        else: print(f"    {P_WARN} No target collection for light '{name}'.")
        print(f"    {P_SUCCESS} Successfully created light '{name}'.")
    except Exception as e: print(f"    {P_ERROR} Failed to create/configure light '{name}': {e}")

def handle_zw_stage_block(stage_data: dict):
    if not bpy: return
    tracks_list = stage_data.get("TRACKS")
    stage_name_raw = stage_data.get('NAME', 'UnnamedStage')
    stage_name = str(stage_name_raw).strip('"\' ')
    if not stage_name: stage_name = "UnnamedStage"

    print(f"{P_INFO} Processing ZW-STAGE: '{stage_name}'")
    if not isinstance(tracks_list, list) or not tracks_list:
        print(f"    {P_WARN} No TRACKS found or TRACKS is not a list in ZW-STAGE '{stage_name}'. Skipping.")
        return
    for track_item_dict in tracks_list:
        if not isinstance(track_item_dict, dict):
            print(f"    {P_WARN} Track item is not a dictionary in ZW-STAGE '{stage_name}'. Skipping track: {track_item_dict}")
            continue

        track_type_raw = track_item_dict.get("TYPE")
        track_type = str(track_type_raw).strip('"\' ') if track_type_raw is not None else None

        target_name_raw = track_item_dict.get("TARGET")
        target_name = str(target_name_raw).strip('"\' ') if target_name_raw is not None else None

        start_frame_str_raw = track_item_dict.get("START", "1")
        start_frame_str = str(start_frame_str_raw).strip('"\' ')
        try: start_frame = int(start_frame_str)
        except ValueError: print(f"    {P_WARN} Invalid START frame '{start_frame_str}' for track '{track_type}'. Defaulting to 1."); start_frame = 1

        end_frame_str_raw = track_item_dict.get("END")
        end_frame_str = str(end_frame_str_raw).strip('"\' ') if end_frame_str_raw is not None else None
        end_frame = None
        if end_frame_str is not None:
            try: end_frame = int(end_frame_str)
            except ValueError: print(f"    {P_WARN} Invalid END frame '{end_frame_str}' for track '{track_type}'. END frame ignored.")

        target_obj = bpy.data.objects.get(target_name) if target_name else None

        print(f"  {P_INFO} Processing track: TYPE='{track_type}', TARGET='{target_name}', START={start_frame}")

        if track_type == "CAMERA":
            if target_obj and target_obj.type == 'CAMERA':
                bpy.context.scene.camera = target_obj
                bpy.context.scene.keyframe_insert(data_path="camera", frame=start_frame)
                print(f"    {P_INFO} Set active camera to '{target_obj.name}' at frame {start_frame}")
            else: print(f"    {P_WARN} Target '{target_name}' for CAMERA track is not valid or not found.")
        elif track_type == "VISIBILITY":
            if target_obj:
                state_str_raw = track_item_dict.get("STATE", "SHOW")
                state_str = str(state_str_raw).strip('"\' ').upper()
                hide_val = True if state_str == "HIDE" else False
                target_obj.hide_viewport = hide_val; target_obj.keyframe_insert(data_path="hide_viewport", frame=start_frame)
                target_obj.hide_render = hide_val; target_obj.keyframe_insert(data_path="hide_render", frame=start_frame)
                print(f"    {P_INFO} Set visibility of '{target_obj.name}' to {'HIDDEN' if hide_val else 'VISIBLE'} at frame {start_frame}")
            else: print(f"    {P_WARN} Target object '{target_name}' for VISIBILITY track not found.")
        elif track_type == "LIGHT_INTENSITY":
            if target_obj and target_obj.type == 'LIGHT':
                light_data_block = target_obj.data; value_at_start_str = track_item_dict.get("VALUE")
                if value_at_start_str is not None:
                    try:
                        value_at_start = float(str(value_at_start_str).strip('"\' '))
                        light_data_block.energy = value_at_start
                        light_data_block.keyframe_insert(data_path="energy", frame=start_frame)
                        print(f"    {P_INFO} Set energy of light '{target_obj.name}' to {value_at_start} at frame {start_frame}")
                    except ValueError: print(f"    {P_WARN} Invalid VALUE '{value_at_start_str}' for LIGHT_INTENSITY on '{target_name}'.")
                else: print(f"    {P_WARN} Missing VALUE for LIGHT_INTENSITY on '{target_name}' at frame {start_frame}.")
                end_value_str = track_item_dict.get("END_VALUE")
                if end_frame is not None and end_value_str is not None:
                    try:
                        value_at_end = float(str(end_value_str).strip('"\' '))
                        light_data_block.energy = value_at_end
                        light_data_block.keyframe_insert(data_path="energy", frame=end_frame)
                        print(f"    {P_INFO} Animated energy of light '{target_obj.name}' to {value_at_end} at frame {end_frame}")
                    except ValueError: print(f"    {P_WARN} Invalid END_VALUE '{end_value_str}' for LIGHT_INTENSITY on '{target_name}'.")
            else: print(f"    {P_WARN} Target '{target_name}' for LIGHT_INTENSITY track is not valid or not found.")
        elif track_type == "PROPERTY_ANIM":
            if target_obj:
                print(f"    {P_INFO} Dispatching to handle_property_anim_track for {target_name}")
                handle_property_anim_track(target_obj, track_item_dict)
            else: print(f"    {P_WARN} Target object '{target_name}' not found for PROPERTY_ANIM track.")
        elif track_type == "MATERIAL_OVERRIDE":
            if target_obj:
                print(f"    {P_INFO} Dispatching to handle_material_override_track for {target_name}")
                track_data_for_handler = track_item_dict.copy()
                track_data_for_handler["START_FRAME"] = start_frame
                if end_frame is not None: track_data_for_handler["END_FRAME"] = end_frame
                handle_material_override_track(target_obj, track_data_for_handler)
            else: print(f"    {P_WARN} Target object '{target_name}' not found for MATERIAL_OVERRIDE track.")
        elif track_type == "SHADER_SWITCH":
            if target_obj:
                print(f"    {P_INFO} Dispatching to handle_shader_switch_track for {target_name}")
                track_data_for_handler = track_item_dict.copy()
                track_data_for_handler["FRAME"] = track_item_dict.get("FRAME", start_frame)
                handle_shader_switch_track(target_obj, track_data_for_handler)
            else: print(f"    {P_WARN} Target object '{target_name}' not found for SHADER_SWITCH track.")
        else:
            print(f"    {P_WARN} Unknown ZW-STAGE track TYPE: '{track_type}'")
    print(f"{P_INFO} Finished processing ZW-STAGE: '{stage_name}'")

# --- ZW-COMPOSE Handler (refined) ---
def handle_zw_compose_block(compose_data: dict, default_collection: bpy.types.Collection):
    if not bpy:
        print("[Error] bpy module not available in handle_zw_compose_block. Cannot process ZW-COMPOSE.")
        return

    compose_name = compose_data.get("NAME", "ZWComposition")
    print(f"[*] Processing ZW-COMPOSE assembly: {compose_name}")

    bpy.ops.object.empty_add(type='PLAIN_AXES')
    parent_empty = bpy.context.active_object
    if not parent_empty:
        print(f"    [Error] Failed to create parent Empty for {compose_name}. Aborting ZW-COMPOSE.")
        return
    parent_empty.name = compose_name

    parent_empty.location = safe_eval(compose_data.get("LOCATION", "(0,0,0)"), (0,0,0))
    rot_deg = safe_eval(compose_data.get("ROTATION", "(0,0,0)"), (0,0,0))
    parent_empty.rotation_euler = Euler([math.radians(a) for a in rot_deg], 'XYZ')
    scale_eval = safe_eval(compose_data.get("SCALE", "(1,1,1)"), (1,1,1))
    parent_empty.scale = (scale_eval if isinstance(scale_eval, tuple) else (float(scale_eval), float(scale_eval), float(scale_eval)))
    print(f"    Parent Empty '{parent_empty.name}' transform: L={parent_empty.location}, R={parent_empty.rotation_euler}, S={parent_empty.scale}")

    comp_coll_name = compose_data.get("COLLECTION")
    target_collection_for_empty = default_collection
    if comp_coll_name:
        target_collection_for_empty = get_or_create_collection(comp_coll_name, parent_collection=bpy.context.scene.collection)

    # Link parent_empty to its target collection
    current_collections = [coll for coll in parent_empty.users_collection]
    for coll in current_collections: coll.objects.unlink(parent_empty)
    if parent_empty.name not in target_collection_for_empty.objects:
        target_collection_for_empty.objects.link(parent_empty)
    print(f"    Parent Empty '{parent_empty.name}' linked to collection '{target_collection_for_empty.name}'")

    # Store metadata on the parent empty
    parent_empty["ZW_COMPOSE_NAME"] = compose_name
    parent_empty["ZW_TEMPLATE_SOURCE"] = compose_data.get("TEMPLATE_SOURCE", "Direct ZW-COMPOSE") # If generated from template
    parent_empty["ZW_ATTACHMENT_COUNT"] = len(compose_data.get("ATTACHMENTS", []))


    base_model_name = compose_data.get("BASE_MODEL")
    base_model_obj = None
    if base_model_name:
        original_base_obj = bpy.data.objects.get(base_model_name)
        if original_base_obj:
            bpy.ops.object.select_all(action='DESELECT')
            original_base_obj.select_set(True)
            bpy.context.view_layer.objects.active = original_base_obj
            bpy.ops.object.duplicate(linked=False) # Duplicate object and data
            base_model_obj = bpy.context.active_object
            base_model_obj.name = f"{base_model_name}_base_of_{compose_name}"
            target_collection_for_empty.objects.link(base_model_obj)
            base_model_obj.parent = parent_empty
            base_model_obj.location, base_model_obj.rotation_euler, base_model_obj.scale = (0,0,0), (0,0,0), (1,1,1)
            base_model_obj["ZW_SLOT_ID"] = "BASE_MODEL"
            base_model_obj["ZW_ROLE"] = compose_data.get("BASE_MODEL_ROLE", "base_model") # Example role
            base_model_obj["ZW_SOURCE_OBJECT"] = base_model_name
            print(f"    Added BASE_MODEL: '{base_model_name}' as '{base_model_obj.name}'")
        else:
            print(f"    [Warning] BASE_MODEL object '{base_model_name}' not found.")

    attachments_list = compose_data.get("ATTACHMENTS", [])
    for i, attach_def in enumerate(attachments_list):
        if not isinstance(attach_def, dict): continue
        attach_obj_source_name = attach_def.get("OBJECT")
        original_attach_obj = bpy.data.objects.get(attach_obj_source_name)
        if original_attach_obj:
            bpy.ops.object.select_all(action='DESELECT')
            original_attach_obj.select_set(True)
            bpy.context.view_layer.objects.active = original_attach_obj
            bpy.ops.object.duplicate(linked=False)
            attached_obj = bpy.context.active_object
            attached_obj.name = f"{attach_obj_source_name}_attach{i}_to_{compose_name}"
            target_collection_for_empty.objects.link(attached_obj)
            attached_obj.parent = parent_empty

            attached_obj.location = safe_eval(attach_def.get("LOCATION", "(0,0,0)"), (0,0,0))
            attach_rot_deg = safe_eval(attach_def.get("ROTATION", "(0,0,0)"), (0,0,0))
            attached_obj.rotation_euler = Euler([math.radians(a) for a in attach_rot_deg], 'XYZ')
            attach_scale_eval = safe_eval(attach_def.get("SCALE", "(1,1,1)"), (1,1,1))
            attached_obj.scale = (attach_scale_eval if isinstance(attach_scale_eval, tuple) else (float(attach_scale_eval), float(attach_scale_eval), float(attach_scale_eval)))

            # Custom Properties for attachments
            attached_obj["ZW_SLOT_ID"] = attach_def.get("SLOT_ID", f"ATTACHMENT_{i}")
            attached_obj["ZW_ROLE"] = attach_def.get("ROLE", "attachment")
            attached_obj["ZW_SOURCE_OBJECT"] = attach_obj_source_name
            print(f"      Added ATTACHMENT: '{attach_obj_source_name}' as '{attached_obj.name}'")

            material_override_def = attach_def.get("MATERIAL_OVERRIDE")
            if isinstance(material_override_def, dict):
                if ZW_MESH_UTILS_IMPORTED and APPLY_ZW_MATERIAL_FUNC: # Use the aliased import
                    print(f"        Applying MATERIAL_OVERRIDE to '{attached_obj.name}'")
                    if 'NAME' not in material_override_def:
                        material_override_def['NAME'] = f"{attached_obj.name}_OverrideMat"
                    APPLY_ZW_MATERIAL_FUNC(attached_obj, material_override_def) # Call the imported function
                else:
                    print(f"        [Warning] MATERIAL_OVERRIDE for '{attached_obj.name}' but zw_mesh.apply_material not imported.")
        else:
            print(f"      [Warning] ATTACHMENT source object '{attach_obj_source_name}' not found.")

    export_def = compose_data.get("EXPORT")
    if export_def and isinstance(export_def, dict):
        export_format = export_def.get("FORMAT", "").lower()
        export_file_str = export_def.get("FILE")
        if export_format == "glb" and export_file_str:
            print(f"    Exporting composition '{compose_name}' to GLB: {export_file_str}")
            export_path = Path(export_file_str)
            if not export_path.is_absolute(): export_path = PROJECT_ROOT / export_path
            export_path.parent.mkdir(parents=True, exist_ok=True)

            bpy.ops.object.select_all(action='DESELECT')
            parent_empty.select_set(True)
            for child in parent_empty.children_recursive: child.select_set(True)
            bpy.context.view_layer.objects.active = parent_empty
            try:
                bpy.ops.export_scene.gltf(filepath=str(export_path), export_format='GLB', use_selection=True, export_apply=True, export_materials='EXPORT', export_texcoords=True, export_normals=True, export_cameras=False, export_lights=False)
                print(f"      Successfully exported to '{export_path.resolve()}'")
            except RuntimeError as e_export:
                print(f"      [Error] Failed to export GLB for '{compose_name}': {e_export}")
        else:
            print(f"    [Warning] EXPORT for '{compose_name}' missing format/file or not 'glb'.")
    print(f"    ✅ Finished ZW-COMPOSE assembly: {compose_name}")

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
            if key.upper() == "ZW-NESTED-DETAILS": # Example of a specific nested block type
                print(f"{P_INFO} Processing ZW-NESTED-DETAILS (semantic parent link: {str(value.get('PARENT','None')).strip('\"\\' ')}). Using collection '{current_bpy_collection.name}'")


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

ure/intent-routing-enhancements
def run_blender_adapter():
    print(f"{P_INFO} --- Starting ZW Blender Adapter ---")
    if not bpy: print(f"{P_ERROR} Blender Python environment (bpy) not detected. Cannot proceed."); print(f"{P_INFO} --- ZW Blender Adapter Finished (with errors) ---"); return
    if bpy.context.object and bpy.context.object.mode != 'OBJECT': bpy.ops.object.mode_set(mode='OBJECT')

    # Argument parsing for input file
    parser = argparse.ArgumentParser(description="Blender adapter for ZW MCP")
    parser.add_argument('--input', type=str, help="Path to the ZW input file", default=str(ZW_INPUT_FILE_PATH))

    # Blender's Python interpreter passes arguments after '--'
    args_to_parse = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    args = parser.parse_args(args_to_parse)

    current_zw_input_file = Path(args.input)

    try:
        with open(current_zw_input_file, "r", encoding="utf-8") as f: zw_text_content = f.read()
        print(f"{P_INFO} Successfully read ZW file: {current_zw_input_file}")
    except FileNotFoundError: print(f"{P_ERROR} ZW input file not found at '{current_zw_input_file}'"); print(f"{P_INFO} --- ZW Blender Adapter Finished (with errors) ---"); return
    except Exception as e: print(f"{P_ERROR} Error reading ZW file '{current_zw_input_file}': {e}"); print(f"{P_INFO} --- ZW Blender Adapter Finished (with errors) ---"); return
    if not zw_text_content.strip(): print(f"{P_ERROR} ZW input file is empty: '{current_zw_input_file}'."); print(f"{P_INFO} --- ZW Blender Adapter Finished (with errors) ---"); return

def run_blender_adapter(input_filepath_str: str = None):
    print("--- Starting ZW Blender Adapter ---")
    if not bpy:
        print("[X] Blender Python environment (bpy) not detected. Cannot proceed.")
        print("--- ZW Blender Adapter Finished (with errors) ---")
        return

    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Determine the input file path
    if input_filepath_str:
        current_input_file_path = Path(input_filepath_str)
        print(f"[*] Using input file from argument: {current_input_file_path}")
    else:
        # Fallback to the global ZW_INPUT_FILE_PATH if no argument is provided
        # This maintains compatibility if the script is run directly without the --input arg
        current_input_file_path = ZW_INPUT_FILE_PATH
        print(f"[*] Using default input file (no --input argument): {current_input_file_path}")

    try:
        with open(current_input_file_path, "r", encoding="utf-8") as f:
            zw_text_content = f.read()
        print(f"[*] Successfully read ZW file: {current_input_file_path}")
    except FileNotFoundError:
        print(f"[X] Error: ZW input file not found at '{current_input_file_path}'")
        print("--- ZW Blender Adapter Finished (with errors) ---")
        return
    except Exception as e:
        print(f"[X] Error reading ZW file '{current_input_file_path}': {e}")
        print("--- ZW Blender Adapter Finished (with errors) ---")
        return

    if not zw_text_content.strip():
        print("[X] Error: ZW input file is empty.")
        print("--- ZW Blender Adapter Finished (with errors) ---")
        return


    try:
        print(f"{P_INFO} Parsing ZW text from '{current_zw_input_file}'..."); parsed_zw_data = parse_zw(zw_text_content)
        if not parsed_zw_data: print(f"{P_WARN} Parsed ZW data from '{current_zw_input_file}' is empty. No objects will be created.")
    except Exception as e: print(f"{P_ERROR} Error parsing ZW text from '{current_zw_input_file}': {e}"); print(f"{P_INFO} --- ZW Blender Adapter Finished (with errors) ---"); return

    try:
        print(f"{P_INFO} Processing ZW structure for Blender object creation...")
        process_zw_structure(parsed_zw_data, current_bpy_collection=bpy.context.scene.collection)
        print(f"{P_INFO} Finished processing ZW structure from '{current_zw_input_file}'.")
    except Exception as e: print(f"{P_ERROR} Error during ZW structure processing for Blender from '{current_zw_input_file}': {e}"); print(f"{P_INFO} --- ZW Blender Adapter Finished (with errors) ---"); return

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
                if ZW_MESH_UTILS_IMPORTED and APPLY_ZW_MESH_MATERIAL_FUNC:
                    print(f"          Applying MATERIAL_OVERRIDE to '{attached_obj.name}'")
                    if 'NAME' not in material_override_def:
                        material_override_def['NAME'] = f"{attached_obj.name}_OverrideMat"
                    APPLY_ZW_MESH_MATERIAL_FUNC(attached_obj, material_override_def)
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
