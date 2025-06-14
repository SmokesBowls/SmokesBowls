# zw_mcp/blender_adapter.py
import sys
import json # For potential pretty printing if needed, not directly for to_zw
from pathlib import Path
import argparse
import math # Added for math.radians

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

# Try to import parse_zw from zw_mcp.zw_parser
try:
    from zw_parser import parse_zw
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

def safe_eval(str_val, default_val):
    if not isinstance(str_val, str): return default_val
    try: return eval(str_val)
    except (SyntaxError, NameError, TypeError, ValueError) as e:
        print(f"    {P_WARN} Could not evaluate string '{str_val}' for attribute: {e}. Using default: {default_val}")
        return default_val

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
                bpy.context.view_layer.objects.active = created_bpy_obj
                shade_str_raw = obj_attributes.get("SHADING", "Smooth")
                shade_str_processed = str(shade_str_raw).strip('"\' ').strip().title() if isinstance(shade_str_raw, str) else "Smooth"
                if shade_str_processed == "Smooth": bpy.ops.object.shade_smooth(); print(f"        {P_INFO} Set shading to Smooth.")
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
            if not collection_name: collection_name = "Unnamed_ZW_Collection"
            print(f"{P_INFO} Processing ZW-COLLECTION block: '{collection_name}' under '{current_bpy_collection.name}'")
            block_bpy_collection = get_or_create_collection(collection_name, parent_collection=current_bpy_collection)
            if isinstance(value, dict) and "CHILDREN" in value and isinstance(value["CHILDREN"], list):
                for child_def_item in value["CHILDREN"]:
                    if isinstance(child_def_item, dict):
                        process_zw_structure(child_def_item, parent_bpy_obj=parent_bpy_obj, current_bpy_collection=block_bpy_collection)
            elif isinstance(value, dict) :
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
            process_zw_structure(value, parent_bpy_obj=parent_bpy_obj, current_bpy_collection=current_bpy_collection)

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

if __name__ == "__main__":
    run_blender_adapter()
```
