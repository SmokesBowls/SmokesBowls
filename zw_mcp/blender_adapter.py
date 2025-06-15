# zw_mcp/blender_adapter.py
import sys
import json # For potential pretty printing if needed, not directly for to_zw
from pathlib import Path
import argparse
import math # Added for math.radians
# from pathlib import Path # Already imported
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
    bpy = None

# Define PROJECT_ROOT early
try:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    print(f"{P_INFO} PROJECT_ROOT defined using __file__: {PROJECT_ROOT}") # Corrected print
except NameError:
    print(f"{P_WARN} __file__ not defined. Attempting fallback for PROJECT_ROOT.") # Corrected print
    if bpy:
        blend_file_path = bpy.data.filepath
        if blend_file_path:
            PROJECT_ROOT = Path(blend_file_path).parent
            print(f"{P_INFO} PROJECT_ROOT defined using bpy.data.filepath (blend file's dir): {PROJECT_ROOT}") # Corrected print
        else:
            try:
                text_block_path = bpy.context.space_data.text.filepath if bpy.context.space_data and bpy.context.space_data.text else ""
                if text_block_path:
                    PROJECT_ROOT = Path(text_block_path).parent.parent
                    print(f"{P_INFO} PROJECT_ROOT defined using text_block_path: {PROJECT_ROOT}") # Corrected print
                else:
                    PROJECT_ROOT = Path(".").resolve()
                    print(f"{P_WARN} PROJECT_ROOT set to current working directory (bpy available, no paths found): {PROJECT_ROOT}") # Corrected print
            except AttributeError:
                 PROJECT_ROOT = Path(".").resolve()
                 print(f"{P_WARN} PROJECT_ROOT set to current working directory (AttributeError fallback): {PROJECT_ROOT}") # Corrected print
    else:
        PROJECT_ROOT = Path(".").resolve()
        print(f"{P_WARN} bpy not available. PROJECT_ROOT set to current working directory: {PROJECT_ROOT}") # Corrected print

if 'PROJECT_ROOT' in locals() and PROJECT_ROOT is not None:
    zw_mcp_dir = PROJECT_ROOT / "zw_mcp"
    if zw_mcp_dir.is_dir():
        if str(zw_mcp_dir) not in sys.path:
            sys.path.append(str(zw_mcp_dir))
            print(f"{P_INFO} Appended zw_mcp_dir to sys.path: {zw_mcp_dir}") # Corrected print
    else:
        try:
            current_script_dir = Path(__file__).resolve().parent
            if str(current_script_dir) not in sys.path:
                 sys.path.append(str(current_script_dir))
                 print(f"{P_INFO} Appended current_script_dir to sys.path: {current_script_dir}") # Corrected print
            if str(PROJECT_ROOT) not in sys.path:
                 sys.path.append(str(PROJECT_ROOT))
                 print(f"{P_INFO} Appended PROJECT_ROOT to sys.path: {PROJECT_ROOT}") # Corrected print
        except NameError:
             if str(PROJECT_ROOT) not in sys.path:
                 sys.path.append(str(PROJECT_ROOT))
                 print(f"{P_INFO} Appended PROJECT_ROOT to sys.path (fallback): {PROJECT_ROOT}") # Corrected print

try:
    from zw_parser import parse_zw
    print(f"{P_INFO} Successfully imported 'parse_zw'.")
except ImportError as e_final:
    print(f"{P_ERROR} CRITICAL: Failed to import 'parse_zw' after sys.path modifications: {e_final}")
    print(f"    Current sys.path: {sys.path}")
    def parse_zw(text: str) -> dict:
        print(f"{P_WARN} Dummy parse_zw called due to CRITICAL import failure. Real parsing will not occur.")
        return {}

# Corrected APPLY_ZW_MATERIAL_FUNC import block
APPLY_ZW_MATERIAL_FUNC = None
ZW_MESH_UTILS_IMPORTED = False
try:
    from .zw_mesh import apply_material as imported_apply_material
    APPLY_ZW_MATERIAL_FUNC = imported_apply_material
    ZW_MESH_UTILS_IMPORTED = True
    print(f"{P_INFO} Successfully imported 'apply_material' from .zw_mesh (relative).")
except ImportError as e_rel:
    print(f"{P_WARN} Relative import of '.zw_mesh.apply_material' failed: {e_rel}")
    try:
        from zw_mcp.zw_mesh import apply_material as pkg_imported_apply_material
        APPLY_ZW_MATERIAL_FUNC = pkg_imported_apply_material
        ZW_MESH_UTILS_IMPORTED = True
        print(f"{P_INFO} Successfully imported 'apply_material' from zw_mcp.zw_mesh (package).")
    except ImportError as e_pkg:
        print(f"{P_WARN} Package import of 'zw_mcp.zw_mesh.apply_material' failed: {e_pkg}")
        def APPLY_ZW_MATERIAL_FUNC(obj, material_def):
            print(f"{P_ERROR} CRITICAL: zw_mesh.apply_material was not imported. Cannot apply material override in ZW-COMPOSE.")
        print(f"{P_ERROR} All import attempts for zw_mesh.apply_material failed. Using dummy function.")

ZW_INPUT_FILE_PATH = Path("zw_mcp/prompts/blender_scene.zw")

def safe_eval(str_val, default_val):
    if not isinstance(str_val, str): return default_val
    try: return eval(str_val)
    except (SyntaxError, NameError, TypeError, ValueError) as e:
        print(f"    {P_WARN} Could not evaluate string '{str_val}' for attribute: {e}. Using default: {default_val}")
        return default_val

def handle_zw_metadata_block(metadata_data: dict, target_obj_name: str = None):
    if not bpy: return
    target_name = target_obj_name or metadata_data.get("TARGET")
    if not target_name:
        print(f"  {P_WARN} ZW-METADATA: No TARGET specified and no target_obj_name passed. Skipping.")
        return
    target_obj = bpy.data.objects.get(target_name)
    if not target_obj:
        print(f"  {P_WARN} ZW-METADATA: Target object '{target_name}' not found. Skipping.")
        return
    print(f"  {P_INFO} Processing ZW-METADATA for: {target_obj.name}")
    for key, value in metadata_data.items():
        if key == "TARGET": continue
        try:
            if isinstance(value, (list, dict)): target_obj[f"ZW_{key.upper()}"] = json.dumps(value)
            elif isinstance(value, (str, int, float, bool)): target_obj[f"ZW_{key.upper()}"] = value
            else: target_obj[f"ZW_{key.upper()}"] = str(value)
            print(f"    {P_INFO} Set custom property ZW_{key.upper()} on {target_obj.name}")
        except Exception as e:
            print(f"    {P_ERROR} Failed to set custom property ZW_{key.upper()} on {target_obj.name}: {e}")

def handle_zw_compose_template_block(template_data: dict):
    if not bpy: return
    template_name = template_data.get("NAME", "UnnamedZWTemplate")
    print(f"  {P_INFO} Storing ZW-COMPOSE-TEMPLATE: {template_name}")
    text_block_name = f"ZW_Template_{template_name}"
    text_block = bpy.data.texts.get(text_block_name) or bpy.data.texts.new(name=text_block_name)
    try:
        template_json_string = json.dumps(template_data, indent=2)
        text_block.from_string(template_json_string)
        print(f"    {P_INFO} Stored template '{template_name}' in Text block '{text_block_name}'.")
        bpy.context.scene[f"ZW_TEMPLATE_{template_name.upper()}"] = template_json_string
        print(f"    {P_INFO} Stored template '{template_name}' in Scene custom property.")
    except Exception as e:
        print(f"    {P_ERROR} Failed to store ZW-COMPOSE-TEMPLATE '{template_name}': {e}")

def handle_zw_mesh_block(mesh_data: dict, current_bpy_collection: bpy.types.Collection):
    if not bpy: return None
    mesh_name = str(mesh_data.get("NAME", "UnnamedZWMesh")).strip('"\' ')
    if not mesh_name: mesh_name = "UnnamedZWMesh"
    print(f"  {P_INFO} Processing ZW-MESH: {mesh_name}")
    base_type = str(mesh_data.get("TYPE", "cube")).strip('"\' ').lower()
    params = mesh_data.get("PARAMS", {})
    bpy.ops.object.select_all(action='DESELECT')
    if base_type == "cube": bpy.ops.mesh.primitive_cube_add(size=float(str(params.get("SIZE", 1.0)).strip('"\' ')))
    elif base_type == "ico_sphere": bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=int(str(params.get("SUBDIVISIONS", 2)).strip('"\' ')), radius=float(str(params.get("RADIUS", 1.0)).strip('"\' ')))
    elif base_type == "cylinder": bpy.ops.mesh.primitive_cylinder_add(vertices=int(str(params.get("VERTICES", 32)).strip('"\' ')), radius=float(str(params.get("RADIUS", 1.0)).strip('"\' ')), depth=float(str(params.get("DEPTH", 2.0)).strip('"\' ')))
    elif base_type == "cone": bpy.ops.mesh.primitive_cone_add(vertices=int(str(params.get("VERTICES", 32)).strip('"\' ')), radius1=float(str(params.get("RADIUS1", params.get("RADIUS", 1.0))).strip('"\' ')), depth=float(str(params.get("DEPTH", 2.0)).strip('"\' ')))
    elif base_type == "plane": bpy.ops.mesh.primitive_plane_add(size=float(str(params.get("SIZE", 2.0))).strip('"\' '))
    else: print(f"    {P_WARN} Unknown ZW-MESH base TYPE '{base_type}'. Defaulting to Cube."); bpy.ops.mesh.primitive_cube_add(size=1.0)
    mesh_obj = bpy.context.active_object
    if not mesh_obj: print(f"    {P_ERROR} Failed to create base primitive for ZW-MESH '{mesh_name}'."); return None
    mesh_obj.name = mesh_name
    material_def = mesh_data.get("MATERIAL")
    if isinstance(material_def, dict):
        if ZW_MESH_UTILS_IMPORTED and APPLY_ZW_MATERIAL_FUNC:
            print(f"    {P_INFO} Applying material definition to ZW-MESH '{mesh_name}' using zw_mesh.apply_material.")
            APPLY_ZW_MATERIAL_FUNC(mesh_obj, material_def)
        else: print(f"    {P_WARN} zw_mesh.apply_material not imported. Cannot apply MATERIAL block for ZW-MESH '{mesh_name}'.")
    metadata_dict = mesh_data.get("METADATA")
    if isinstance(metadata_dict, dict): handle_zw_metadata_block(metadata_dict, target_obj_name=mesh_obj.name)
    explicit_coll_name = str(mesh_data.get("COLLECTION","")).strip('"\' ')
    target_collection = current_bpy_collection
    if explicit_coll_name: target_collection = get_or_create_collection(explicit_coll_name, bpy.context.scene.collection)
    current_obj_collections = [c for c in mesh_obj.users_collection]
    for c in current_obj_collections: c.objects.unlink(mesh_obj)
    if target_collection and mesh_obj.name not in target_collection.objects: target_collection.objects.link(mesh_obj)
    print(f"    {P_INFO} Linked '{mesh_obj.name}' to collection '{target_collection.name if target_collection else 'None'}'.")
    print(f"    {P_SUCCESS} Successfully processed ZW-MESH: {mesh_name}")
    return mesh_obj

def handle_zw_compose_block(compose_data: dict, default_collection: bpy.types.Collection):
    if not bpy:
        print(f"{P_ERROR} bpy module not available in handle_zw_compose_block. Cannot process ZW-COMPOSE.")
        return
    compose_name = str(compose_data.get("NAME", "ZWComposition")).strip('"\' ')
    if not compose_name: compose_name = "ZWComposition"
    print(f"{P_INFO} Processing ZW-COMPOSE assembly: {compose_name}")
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    parent_empty = bpy.context.active_object
    if not parent_empty:
        print(f"    {P_ERROR} Failed to create parent Empty for {compose_name}. Aborting ZW-COMPOSE.")
        return
    parent_empty.name = compose_name
    parent_empty.location = safe_eval(compose_data.get("LOCATION", "(0,0,0)"), (0,0,0))
    rot_deg = safe_eval(compose_data.get("ROTATION", "(0,0,0)"), (0,0,0))
    parent_empty.rotation_euler = Euler([math.radians(a) for a in rot_deg], 'XYZ')
    scale_eval = safe_eval(compose_data.get("SCALE", "(1,1,1)"), (1,1,1))
    if isinstance(scale_eval, (int, float)): parent_empty.scale = (float(scale_eval), float(scale_eval), float(scale_eval))
    else: parent_empty.scale = scale_eval
    print(f"    {P_INFO} Parent Empty '{parent_empty.name}' transform: L={parent_empty.location}, R={parent_empty.rotation_euler}, S={parent_empty.scale}")
    comp_coll_name = str(compose_data.get("COLLECTION","")).strip('"\' ')
    target_collection_for_empty = default_collection
    if comp_coll_name: target_collection_for_empty = get_or_create_collection(comp_coll_name, parent_collection=bpy.context.scene.collection)
    current_collections = [coll for coll in parent_empty.users_collection]
    for coll in current_collections: coll.objects.unlink(parent_empty)
    if target_collection_for_empty and parent_empty.name not in target_collection_for_empty.objects:
        target_collection_for_empty.objects.link(parent_empty)
        print(f"    {P_INFO} Parent Empty '{parent_empty.name}' linked to collection '{target_collection_for_empty.name}'")
    parent_empty["ZW_COMPOSE_NAME"] = compose_name
    parent_empty["ZW_TEMPLATE_SOURCE"] = str(compose_data.get("TEMPLATE_SOURCE", "Direct ZW-COMPOSE")).strip('"\' ')
    parent_empty["ZW_ATTACHMENT_COUNT"] = len(compose_data.get("ATTACHMENTS", []))
    base_model_name = str(compose_data.get("BASE_MODEL","")).strip('"\' ')
    if base_model_name:
        original_base_obj = bpy.data.objects.get(base_model_name)
        if original_base_obj:
            bpy.ops.object.select_all(action='DESELECT'); original_base_obj.select_set(True)
            bpy.context.view_layer.objects.active = original_base_obj
            bpy.ops.object.duplicate(linked=False)
            base_model_obj = bpy.context.active_object
            base_model_obj.name = f"{original_base_obj.name}_base_of_{compose_name}"
            if target_collection_for_empty and base_model_obj.name not in target_collection_for_empty.objects: target_collection_for_empty.objects.link(base_model_obj)
            base_model_obj.parent = parent_empty
            base_model_obj.location, base_model_obj.rotation_euler, base_model_obj.scale = (0,0,0), (0,0,0), (1,1,1)
            base_model_obj["ZW_SLOT_ID"] = "BASE_MODEL"
            base_model_obj["ZW_ROLE"] = str(compose_data.get("BASE_MODEL_ROLE", "base_model")).strip('"\' ')
            base_model_obj["ZW_SOURCE_OBJECT"] = original_base_obj.name
            print(f"    {P_INFO} Added BASE_MODEL: '{original_base_obj.name}' as '{base_model_obj.name}'")
        else: print(f"    {P_WARN} BASE_MODEL object '{base_model_name}' not found.")
    attachments_list = compose_data.get("ATTACHMENTS", [])
    for i, attach_def in enumerate(attachments_list):
        if not isinstance(attach_def, dict): continue
        attach_obj_source_name = str(attach_def.get("OBJECT","")).strip('"\' ')
        if not attach_obj_source_name: print(f"      {P_WARN} ATTACHMENT {i} missing OBJECT reference."); continue
        original_attach_obj = bpy.data.objects.get(attach_obj_source_name)
        if original_attach_obj:
            bpy.ops.object.select_all(action='DESELECT'); original_attach_obj.select_set(True)
            bpy.context.view_layer.objects.active = original_attach_obj
            bpy.ops.object.duplicate(linked=False)
            attached_obj = bpy.context.active_object
            attached_obj.name = f"{original_attach_obj.name}_attach{i}_to_{compose_name}"
            if target_collection_for_empty and attached_obj.name not in target_collection_for_empty.objects: target_collection_for_empty.objects.link(attached_obj)
            attached_obj.parent = parent_empty
            attached_obj.location = safe_eval(attach_def.get("LOCATION", "(0,0,0)"), (0,0,0))
            attach_rot_deg = safe_eval(attach_def.get("ROTATION", "(0,0,0)"), (0,0,0))
            attached_obj.rotation_euler = Euler([math.radians(a) for a in attach_rot_deg], 'XYZ')
            attach_scale_eval = safe_eval(attach_def.get("SCALE", "(1,1,1)"), (1,1,1))
            if isinstance(attach_scale_eval, (int, float)): attached_obj.scale = (float(attach_scale_eval), float(attach_scale_eval), float(attach_scale_eval))
            else: attached_obj.scale = attach_scale_eval
            attached_obj["ZW_SLOT_ID"] = str(attach_def.get("SLOT_ID", f"ATTACHMENT_{i}")).strip('"\' ')
            attached_obj["ZW_ROLE"] = str(attach_def.get("ROLE", "attachment")).strip('"\' ')
            attached_obj["ZW_SOURCE_OBJECT"] = original_attach_obj.name
            print(f"      {P_INFO} Added ATTACHMENT: '{original_attach_obj.name}' as '{attached_obj.name}'")
            material_override_def = attach_def.get("MATERIAL_OVERRIDE")
            if isinstance(material_override_def, dict):
                if ZW_MESH_UTILS_IMPORTED and APPLY_ZW_MATERIAL_FUNC:
                    print(f"        {P_INFO} Applying MATERIAL_OVERRIDE to '{attached_obj.name}'")
                    if 'NAME' not in material_override_def: material_override_def['NAME'] = f"{attached_obj.name}_OverrideMat"
                    APPLY_ZW_MATERIAL_FUNC(attached_obj, material_override_def)
                else: print(f"        {P_WARN} MATERIAL_OVERRIDE for '{attached_obj.name}' but zw_mesh.apply_material not imported/functional.")
        else: print(f"      {P_WARN} ATTACHMENT source object '{attach_obj_source_name}' not found.")
    export_def = compose_data.get("EXPORT")
    if export_def and isinstance(export_def, dict):
        export_format = str(export_def.get("FORMAT", "")).strip('"\' ').lower()
        export_file_str = str(export_def.get("FILE","")).strip('"\' ')
        if export_format == "glb" and export_file_str:
            print(f"    {P_INFO} Exporting composition '{compose_name}' to GLB: {export_file_str}")
            export_path = Path(export_file_str)
            if not export_path.is_absolute(): export_path = PROJECT_ROOT / export_path
            export_path.parent.mkdir(parents=True, exist_ok=True)
            bpy.ops.object.select_all(action='DESELECT'); parent_empty.select_set(True)
            for child in parent_empty.children_recursive: child.select_set(True)
            bpy.context.view_layer.objects.active = parent_empty
            try:
                bpy.ops.export_scene.gltf(filepath=str(export_path.resolve()), export_format='GLB', use_selection=True, export_apply=True, export_materials='EXPORT', export_texcoords=True, export_normals=True, export_cameras=False, export_lights=False)
                print(f"      {P_SUCCESS} Successfully exported to '{export_path.resolve()}'")
            except RuntimeError as e_export: print(f"      {P_ERROR} Failed to export GLB for '{compose_name}': {e_export}")
        else: print(f"    {P_WARN} EXPORT for '{compose_name}' missing format/file or not 'glb'.")
    print(f"    {P_SUCCESS} Finished ZW-COMPOSE assembly: {compose_name}")

def parse_color(color_input, default_color=(0.8, 0.8, 0.8, 1.0)):
    if isinstance(color_input, str):
        s = color_input.strip()
        if s.startswith("#"):
            hex_color = s.lstrip("#")
            try:
                if len(hex_color) == 6: r, g, b = (int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4)); return (r, g, b, 1.0)
                elif len(hex_color) == 8: r, g, b, a = (int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4, 6)); return (r, g, b, a)
                else: print(f"    {P_WARN} Invalid hex color string length for '{s}'. Using default."); return default_color
            except ValueError: print(f"    {P_WARN} Invalid hex color string '{s}'. Using default."); return default_color
        elif s.startswith("(") and s.endswith(")"):
            try:
                parts = [float(p.strip()) for p in s.strip("()").split(",")];
                if len(parts) == 3: return (parts[0], parts[1], parts[2], 1.0)
                if len(parts) == 4: return tuple(parts)
                else: print(f"    {P_WARN} Tuple-like color string '{s}' must have 3 or 4 components. Using default."); return default_color
            except ValueError: print(f"    {P_WARN} Invalid tuple-like color string '{s}'. Using default."); return default_color
        else: print(f"    {P_WARN} Unrecognized string color format '{color_input}'. Using default."); return default_color
    elif isinstance(color_input, (list, tuple)):
        if not all(isinstance(num, (int, float)) for num in color_input): print(f"    {P_WARN} Color list/tuple '{color_input}' contains non-numeric values. Using default."); return default_color
        if len(color_input) == 3: return (float(color_input[0]), float(color_input[1]), float(color_input[2]), 1.0)
        elif len(color_input) == 4: return (float(color_input[0]), float(color_input[1]), float(color_input[2]), float(color_input[3]))
        else: print(f"    {P_WARN} Color list/tuple '{color_input}' must have 3 or 4 components. Using default."); return default_color
    else: print(f"    {P_WARN} Unrecognized color input type '{type(color_input)}' for value '{color_input}'. Using default."); return default_color

def _apply_bsdf_properties(bsdf_node, properties_dict: dict, object_name_for_logging: str = ""):
    if not bpy or not bsdf_node or not properties_dict: return False
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
                        float_val = float(str(value_any).strip('"' '))
                        bsdf_node.inputs[bsdf_input_name].default_value = float_val
                        print(f"        {P_INFO} Set BSDF.{bsdf_input_name} to {float_val}")
                    except ValueError: print(f"        {P_WARN} Could not convert value '{value_any}' to float for BSDF input {bsdf_input_name}.")
                else: print(f"        {P_WARN} Unsupported value type '{type(value_any)}' for BSDF input {bsdf_input_name}.")
            except Exception as e_bsdf: print(f"        {P_WARN} Failed to set BSDF input {bsdf_input_name} with value '{value_any}': {e_bsdf}")
        else: print(f"        {P_WARN} BSDF input '{bsdf_input_name}' not found on node.")
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
    original_requested_type = obj_type_normalized
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
                inline_material_data = None; final_mat_name = None; color_set_by_material_processing = False
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
                if not final_mat_name: final_mat_name = f"{obj_name}_FallbackMat"
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

                # Corrected Shading Block
                bpy.ops.object.select_all(action='DESELECT')
                created_bpy_obj.select_set(True)
                bpy.context.view_layer.objects.active = created_bpy_obj
                shade_str_raw = obj_attributes.get("SHADING", "Smooth")
                shade_str_processed = str(shade_str_raw).strip('"\' ').strip().title() if isinstance(shade_str_raw, str) else "Smooth"
                if shade_str_processed == "Smooth":
                    bpy.ops.object.shade_smooth()
                    print(f"        {P_INFO} Set shading to Smooth.")
                elif shade_str_processed == "Flat":
                    bpy.ops.object.shade_flat()
                    print(f"        {P_INFO} Set shading to Flat.")
        else: print(f"    {P_ERROR} Object creation did not result in an active object."); return None
    except Exception as e: print(f"    {P_ERROR} Error creating Blender object '{obj_name}': {e}"); return None
    return created_bpy_obj

def process_zw_structure(data_dict: dict, parent_bpy_obj=None, current_bpy_collection=None):
    if not bpy: return
    if current_bpy_collection is None: current_bpy_collection = bpy.context.scene.collection
    if not isinstance(data_dict, dict):
        print(f"{P_WARN} process_zw_structure expects a dictionary, got {type(data_dict)}. Skipping.")
        return

    for key, value in data_dict.items():
        key_upper = key.upper()
        key_clean_stripped = key.strip('"\' ').strip()

        obj_attributes_for_current_zw_object = None

        if key_upper.startswith("ZW-COLLECTION"):
            collection_name_raw = key.split(":", 1)[1].strip() if ":" in key else key.replace("ZW-COLLECTION", "", 1).strip()
            collection_name = collection_name_raw.strip('"\' ')
            if not collection_name: collection_name = "Unnamed_ZW_Collection"
            print(f"{P_INFO} Processing ZW-COLLECTION block: '{collection_name}' under '{current_bpy_collection.name}'")
            block_bpy_collection = get_or_create_collection(collection_name, parent_collection=current_bpy_collection)
            if isinstance(value, dict):
                 process_zw_structure(value, parent_bpy_obj=parent_bpy_obj, current_bpy_collection=block_bpy_collection)
            elif isinstance(value, list):
                for child_item in value:
                    if isinstance(child_item, dict):
                        process_zw_structure(child_item, parent_bpy_obj=parent_bpy_obj, current_bpy_collection=block_bpy_collection)
            continue
        elif key_upper == "ZW-OBJECT":
            if isinstance(value, dict): obj_attributes_for_current_zw_object = value
            elif isinstance(value, str): obj_attributes_for_current_zw_object = {"TYPE": value.strip('"\' ')}
        elif key_upper == "ZW-MESH":
            if isinstance(value, dict): handle_zw_mesh_block(value, current_bpy_collection)
            else: print(f"{P_WARN} ZW-MESH value is not a dictionary: {value}")
            continue
        elif key_upper == "ZW-COMPOSE-TEMPLATE":
             if isinstance(value, dict): handle_zw_compose_template_block(value)
             else: print(f"{P_WARN} ZW-COMPOSE-TEMPLATE value is not a dictionary: {value}")
             continue
        elif key_upper == "ZW-COMPOSE":
            if isinstance(value, dict): handle_zw_compose_block(value, current_bpy_collection)
            else: print(f"{P_WARN} ZW-COMPOSE value is not a dictionary: {value}")
            continue
        elif key_clean_stripped.title() in ["Sphere", "Cube", "Plane", "Cone", "Cylinder", "Torus", "Grid", "Monkey"] and isinstance(value, dict):
            obj_attributes_for_current_zw_object = value.copy()
            obj_attributes_for_current_zw_object["TYPE"] = key_clean_stripped

        if obj_attributes_for_current_zw_object:
            created_obj = handle_zw_object_creation(obj_attributes_for_current_zw_object, parent_bpy_obj)
            if created_obj:
                explicit_coll_name = obj_attributes_for_current_zw_object.get("COLLECTION")
                target_coll = current_bpy_collection
                if isinstance(explicit_coll_name, str) and explicit_coll_name.strip('"\' '):
                    target_coll = get_or_create_collection(explicit_coll_name.strip('"\' '), bpy.context.scene.collection)

                if target_coll and created_obj.name not in target_coll.objects: # Check if not already linked to target
                    # Unlink from all current collections before linking to the target one
                    for coll_user in created_obj.users_collection:
                        coll_user.objects.unlink(created_obj)
                    target_coll.objects.link(created_obj)
                    print(f"    {P_INFO} Linked '{created_obj.name}' to collection '{target_coll.name}'")
                elif not created_obj.users_collection and target_coll : # If it has no collections, link it.
                     target_coll.objects.link(created_obj)
                     print(f"    {P_INFO} Linked '{created_obj.name}' to collection '{target_coll.name}' (was in no collections).")


                children_list = obj_attributes_for_current_zw_object.get("CHILDREN")
                if isinstance(children_list, list):
                    print(f"{P_INFO} Processing CHILDREN for '{created_obj.name}' in collection '{target_coll.name if target_coll else 'None'}'")
                    for child_def in children_list:
                        if isinstance(child_def, dict):
                            process_zw_structure(child_def, parent_bpy_obj=created_obj, current_bpy_collection=target_coll)
                elif children_list is not None:
                     print(f"    {P_WARN} CHILDREN attribute for '{created_obj.name}' is not a list: {type(children_list)}")
            continue
        elif isinstance(value, dict):
            process_zw_structure(value, parent_bpy_obj=parent_bpy_obj, current_bpy_collection=current_bpy_collection)

def run_blender_adapter(input_filepath_str: str = None):
    print(f"{P_INFO} --- Starting ZW Blender Adapter ---")
    if not bpy:
        print(f"{P_ERROR} Blender Python environment (bpy) not detected. Cannot proceed.")
        print(f"{P_INFO} --- ZW Blender Adapter Finished (with errors) ---")
        return
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    current_zw_input_file = Path(input_filepath_str if input_filepath_str else ZW_INPUT_FILE_PATH)

    try:
        with open(current_zw_input_file, "r", encoding="utf-8") as f: zw_text_content = f.read()
        print(f"{P_INFO} Successfully read ZW file: {current_zw_input_file}")
    except FileNotFoundError:
        print(f"{P_ERROR} ZW input file not found at '{current_zw_input_file}'")
        print(f"{P_INFO} --- ZW Blender Adapter Finished (with errors) ---"); return
    except Exception as e:
        print(f"{P_ERROR} Error reading ZW file '{current_zw_input_file}': {e}")
        print(f"{P_INFO} --- ZW Blender Adapter Finished (with errors) ---"); return
    if not zw_text_content.strip():
        print(f"{P_ERROR} ZW input file is empty: '{current_zw_input_file}'.")
        print(f"{P_INFO} --- ZW Blender Adapter Finished (with errors) ---"); return

    try:
        print(f"{P_INFO} Parsing ZW text from '{current_zw_input_file}'..."); parsed_zw_data = parse_zw(zw_text_content)
        if not parsed_zw_data: print(f"{P_WARN} Parsed ZW data from '{current_zw_input_file}' is empty. No objects will be created.")
    except Exception as e:
        print(f"{P_ERROR} Error parsing ZW text from '{current_zw_input_file}': {e}")
        print(f"{P_INFO} --- ZW Blender Adapter Finished (with errors) ---"); return

    try:
        print(f"{P_INFO} Processing ZW structure for Blender object creation...")
        process_zw_structure(parsed_zw_data, current_bpy_collection=bpy.context.scene.collection)
        print(f"{P_INFO} Finished processing ZW structure from '{current_zw_input_file}'.")
    except Exception as e:
        print(f"{P_ERROR} Error during ZW structure processing for Blender from '{current_zw_input_file}': {e}")
        print(f"{P_INFO} --- ZW Blender Adapter Finished (with errors) ---"); return

    print(f"{P_SUCCESS} --- ZW Blender Adapter Finished Successfully ---")

if __name__ == "__main__":
    adapter_parser = argparse.ArgumentParser(description="ZW Blender Adapter Script")
    adapter_parser.add_argument(
        "--input",
        type=str,
        help="Path to the ZW input file to process.",
        default=None
    )
    argv = sys.argv
    try:
        idx = argv.index("--") + 1
        script_args = argv[idx:]
    except ValueError:
        script_args = []
    if bpy:
        args = adapter_parser.parse_args(args=script_args)
        run_blender_adapter(input_filepath_str=args.input if args.input else str(ZW_INPUT_FILE_PATH))
    else:
        print(f"{P_WARN} bpy module not available. Full Blender operations cannot be performed.")
        print(f"{P_INFO} To process a ZW file with this adapter, run it through Blender's Python environment.")
        # print("Example: blender --background --python zw_mcp/blender_adapter.py -- --input /path/to/your/file.zw")

[end of zw_mcp/blender_adapter.py]
