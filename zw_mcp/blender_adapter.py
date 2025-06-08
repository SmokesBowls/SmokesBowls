# zw_mcp/blender_adapter.py
import sys
import json # For potential pretty printing if needed, not directly for to_zw
from pathlib import Path
import argparse
import math # Added for math.radians

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

def get_or_create_collection(name: str, parent_collection=None):
    """
    Gets an existing collection by name or creates it under the parent_collection.
    If parent_collection is None, uses the scene's master collection.
    """
    if not bpy:
        print("[!] bpy not available. Skipping collection get/create.")
        return None

    if parent_collection is None:
        parent_collection = bpy.context.scene.collection

    # Check if collection already exists as a child of the parent_collection
    existing_collection = parent_collection.children.get(name)
    if existing_collection:
        print(f"    Found existing collection: '{name}' in '{parent_collection.name}'")
        return existing_collection
    else:
        # Create new collection and link it to the parent_collection
        new_collection = bpy.data.collections.new(name=name)
        parent_collection.children.link(new_collection)
        print(f"    Created and linked new collection: '{name}' to '{parent_collection.name}'")
        return new_collection

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

# --- Geometry Node Function Handlers ---

def apply_array_gn(source_obj: bpy.types.Object, params: dict):
    if not bpy: return
    if source_obj is None:
        print("[!] ARRAY target object not found or provided. Skipping.")
        return

    print(f"[*] Applying ARRAY GN to create instances of '{source_obj.name}' with params: {params}")

    array_host_name = f"{source_obj.name}_ArrayResult"
    array_host_obj = bpy.data.objects.new(array_host_name, None) # Empty object for GN

    # Link to the same collection as the source object, or scene's master if source is not in one
    source_collection = source_obj.users_collection[0] if source_obj.users_collection else bpy.context.scene.collection
    source_collection.objects.link(array_host_obj)
    print(f"    Created ARRAY host object '{array_host_name}' in collection '{source_collection.name}'")

    mod = array_host_obj.modifiers.new(name="ZW_Array", type='NODES')
    gn_tree_name = f"ZW_Array_{source_obj.name}_GN"

    # Check if node group already exists, reuse if so, otherwise create
    if gn_tree_name in bpy.data.node_groups:
        node_group = bpy.data.node_groups[gn_tree_name]
        print(f"    Reusing existing Node Group: {gn_tree_name}")
    else:
        node_group = bpy.data.node_groups.new(name=gn_tree_name, type='GeometryNodeTree')
        print(f"    Created new Node Group: {gn_tree_name}")

        nodes = node_group.nodes
        links = node_group.links
        nodes.clear() # Clear default nodes

        group_input = nodes.new(type='NodeGroupInput')
        group_input.location = (-400, 0)
        group_output = nodes.new(type='NodeGroupOutput')
        group_output.location = (400, 0)

        # Define inputs/outputs for the group if needed (e.g. for dynamic params)
        # For now, params are set directly on nodes.

        obj_info = nodes.new('GeometryNodeObjectInfo')
        obj_info.location = (-200, 200)
        obj_info.inputs['Object'].default_value = source_obj

        mesh_line = nodes.new('NodeGeometryMeshLine')
        mesh_line.location = (-200, -100)
        count = int(params.get("COUNT", 5))
        offset_vec_str = params.get("OFFSET", "(0,0,1)") # Default offset changed to Z-axis for more visible pillar example
        offset_vec = safe_eval(offset_vec_str, (0,0,1))

        mesh_line.mode = 'END_POINTS' # Use start and end points for offset
        # For 'END_POINTS' mode with offset, we set 'Start Location' to (0,0,0) and 'End Location' to the total offset
        # For a count of N items, there are N-1 segments for the offset.
        # If offset is per item, total_offset = (count-1) * offset_vec IF offset is between items.
        # Or, if offset is total length, and count is number of points:
        # mesh_line.inputs['Start Location'].default_value = (0,0,0)
        # mesh_line.inputs['Offset'].default_value = offset_vec # This makes it use the 'Offset' mode implicitly if count changes
        # Let's use the direct 'Offset' mode which is simpler with count
        mesh_line.mode = 'OFFSET'
        mesh_line.inputs['Count'].default_value = count
        mesh_line.inputs['Offset'].default_value = offset_vec


        inst_on_pts = nodes.new('GeometryNodeInstanceOnPoints')
        inst_on_pts.location = (0, 0)

        links.new(mesh_line.outputs['Mesh'], inst_on_pts.inputs['Points'])
        links.new(obj_info.outputs['Geometry'], inst_on_pts.inputs['Instance'])

        if str(params.get("MODE", "INSTANCE")).upper() == "REALIZE":
            realize = nodes.new('GeometryNodeRealizeInstances')
            realize.location = (200, 0)
            links.new(inst_on_pts.outputs['Instances'], realize.inputs['Geometry'])
            links.new(realize.outputs['Geometry'], group_output.inputs.new('NodeSocketGeometry', 'Geometry'))
            print("    Array set to REALIZED instances.")
        else:
            links.new(inst_on_pts.outputs['Instances'], group_output.inputs.new('NodeSocketGeometry', 'Geometry'))
            print("    Array set to INSTANCED instances.")

    mod.node_group = node_group
    bpy.context.view_layer.objects.active = array_host_obj
    array_host_obj.select_set(True)
    print(f"    Applied ARRAY to '{array_host_name}' using source '{source_obj.name}'")


def apply_displace_noise_gn(target_obj: bpy.types.Object, params: dict):
    if not bpy: return
    if target_obj is None or target_obj.type != 'MESH':
        print(f"[!] DISPLACE_NOISE target object '{target_obj.name if target_obj else 'None'}' is not a MESH. Skipping.")
        return

    print(f"[*] Applying DISPLACE_NOISE GN to '{target_obj.name}' with params: {params}")

    mod = target_obj.modifiers.new(name="ZW_DisplaceNoise", type='NODES')
    gn_tree_name = f"ZW_Displace_{target_obj.name}_GN"

    if gn_tree_name in bpy.data.node_groups:
        node_group = bpy.data.node_groups[gn_tree_name]
        print(f"    Reusing existing Node Group: {gn_tree_name}")
    else:
        node_group = bpy.data.node_groups.new(name=gn_tree_name, type='GeometryNodeTree')
        print(f"    Created new Node Group: {gn_tree_name}")

        nodes = node_group.nodes
        links = node_group.links
        nodes.clear()

        group_input = nodes.new(type='NodeGroupInput')
        group_input.location = (-600, 0)
        group_output = nodes.new(type='NodeGroupOutput')
        group_output.location = (400, 0)

        # Ensure input and output sockets are named 'Geometry'
        node_group.inputs.new('NodeSocketGeometry', 'Geometry')
        node_group.outputs.new('NodeSocketGeometry', 'Geometry')


        set_pos = nodes.new('GeometryNodeSetPosition')
        set_pos.location = (0, 0)

        noise_tex = nodes.new('ShaderNodeTexNoise')
        noise_tex.location = (-400, -200)
        noise_tex.noise_dimensions = '3D' # Default is 3D
        noise_tex.inputs['Scale'].default_value = float(params.get("SCALE", 5.0))
        # Use 'W' as a proxy for seed if noise is 3D, or a dedicated seed input if available/desired for 4D.
        noise_tex.inputs['W'].default_value = float(params.get("SEED", 0.0))

        # To make noise affect position, we need to convert its factor (0-1) or color (vector)
        # into a displacement vector. Usually, this involves Normal.
        normal_node = nodes.new('GeometryNodeInputNormal')
        normal_node.location = (-400, 0)

        # Scale the noise factor by strength
        strength_scale_node = nodes.new('ShaderNodeMath') # Using Math node for scalar strength
        strength_scale_node.operation = 'MULTIPLY'
        strength_scale_node.location = (-200, -200)
        strength_scale_node.inputs[1].default_value = float(params.get("STRENGTH", 0.5))
        links.new(noise_tex.outputs['Fac'], strength_scale_node.inputs[0])


        # Multiply scaled noise factor by normal vector to displace along normal
        vec_multiply_normal = nodes.new('ShaderNodeVectorMath')
        vec_multiply_normal.operation = 'MULTIPLY' # Or 'SCALE' if using the factor directly on normal
        vec_multiply_normal.location = (-200, 0)
        links.new(normal_node.outputs['Normal'], vec_multiply_normal.inputs[0])
        links.new(strength_scale_node.outputs['Value'], vec_multiply_normal.inputs[1]) # Use scaled noise factor

        # Handle displacement axis (simplified: Z or Normal)
        displace_axis = params.get("AXIS", "NORMAL").upper() # Default to NORMAL

        offset_vector_source_node = None
        if displace_axis == 'Z':
            combine_xyz = nodes.new('ShaderNodeCombineXYZ')
            combine_xyz.location = (-200, 200) # Position it if used
            links.new(strength_scale_node.outputs['Value'], combine_xyz.inputs['Z']) # Noise Fac directly to Z
            # X and Y inputs of CombineXYZ remain 0 by default.
            offset_vector_source_node = combine_xyz
        elif displace_axis == 'X':
            combine_xyz = nodes.new('ShaderNodeCombineXYZ')
            combine_xyz.location = (-200, 200)
            links.new(strength_scale_node.outputs['Value'], combine_xyz.inputs['X'])
            offset_vector_source_node = combine_xyz
        elif displace_axis == 'Y':
            combine_xyz = nodes.new('ShaderNodeCombineXYZ')
            combine_xyz.location = (-200, 200)
            links.new(strength_scale_node.outputs['Value'], combine_xyz.inputs['Y'])
            offset_vector_source_node = combine_xyz
        else: # Default to Normal
            offset_vector_source_node = vec_multiply_normal
            print("    Displacing along Normal.")


        links.new(offset_vector_source_node.outputs['Vector'], set_pos.inputs['Offset'])

        links.new(group_input.outputs['Geometry'], set_pos.inputs['Geometry'])
        links.new(set_pos.outputs['Geometry'], group_output.inputs['Geometry'])

    mod.node_group = node_group
    bpy.context.view_layer.objects.active = target_obj
    target_obj.select_set(True)
    print(f"    Applied DISPLACE_NOISE to '{target_obj.name}'")

def handle_zw_animation_block(anim_data: dict):
    if not bpy: return

    target_obj_name = anim_data.get("TARGET_OBJECT")
    prop_path = anim_data.get("PROPERTY_PATH")
    prop_idx_str = anim_data.get("INDEX")
    unit = anim_data.get("UNIT", "").lower()
    interpolation_str = anim_data.get("INTERPOLATION", "BEZIER").upper()
    keyframes_list = anim_data.get("KEYFRAMES")

    if not all([target_obj_name, prop_path, keyframes_list]):
        print(f"[!] ZW-ANIMATION '{anim_data.get('NAME', 'UnnamedAnimation')}' missing TARGET_OBJECT, PROPERTY_PATH, or KEYFRAMES. Skipping.")
        return

    target_obj = bpy.data.objects.get(target_obj_name)
    if not target_obj:
        print(f"[!] ZW-ANIMATION target object '{target_obj_name}' not found. Skipping.")
        return

    if not target_obj.animation_data:
        target_obj.animation_data_create()

    action_name = anim_data.get("NAME", f"{target_obj.name}_{prop_path}_AnimAction")
    # Use existing action if name matches, otherwise create new or use current if no name conflict
    if not target_obj.animation_data.action:
        print(f"    Creating new Action: {action_name} for {target_obj_name}")
        target_obj.animation_data.action = bpy.data.actions.new(name=action_name)
    elif target_obj.animation_data.action.name != action_name and anim_data.get("NAME"):
        print(f"    Creating new Action (name conflict/specified): {action_name} for {target_obj_name}")
        target_obj.animation_data.action = bpy.data.actions.new(name=action_name)
    else:
        print(f"    Using existing or current Action: {target_obj.animation_data.action.name} for {target_obj_name}")

    action = target_obj.animation_data.action

    prop_idx = None
    if prop_idx_str is not None:
        try:
            prop_idx = int(prop_idx_str)
        except ValueError:
            print(f"    [Warning] Invalid INDEX '{prop_idx_str}' for animation on {target_obj_name}. Ignoring index.")
            prop_idx = None

    print(f"  Animating '{target_obj.name}.{prop_path}' (Index: {prop_idx if prop_idx is not None else 'All'}) with {interpolation_str} interpolation.")

    for kf_data in keyframes_list:
        frame = kf_data.get("FRAME")
        value_input = kf_data.get("VALUE")

        if frame is None or value_input is None:
            print(f"    [Warning] Keyframe missing FRAME or VALUE for {target_obj_name}. Skipping keyframe: {kf_data}")
            continue

        frame = float(frame)

        if prop_idx is not None: # Animating a single component (e.g. rotation_euler[2])
            try:
                val = float(value_input)
                if unit == "degrees" and "rotation" in prop_path.lower(): # Check if it's a rotation property
                    val = math.radians(val)

                fcurve = action.fcurves.find(prop_path, index=prop_idx)
                if not fcurve:
                    fcurve = action.fcurves.new(prop_path, index=prop_idx, action_group=target_obj.name)

                keyframe_point = fcurve.keyframe_points.insert(frame, val)
                keyframe_point.interpolation = interpolation_str
                # print(f"      KF Inserted: Frame {frame}, Value {val:.3f}, Interpolation {interpolation_str}")
            except ValueError:
                print(f"    [Warning] Could not convert value '{value_input}' to float for {target_obj_name}.{prop_path}[{prop_idx}]. Skipping keyframe.")

        else: # Animating a vector (e.g. location, scale)
            parsed_tuple = safe_eval(str(value_input), None) # Ensure value_input is str for safe_eval
            if isinstance(parsed_tuple, tuple) and (len(parsed_tuple) == 3 or len(parsed_tuple) == 4) : # Typically 3 for loc/scale/rot_euler
                final_values = list(parsed_tuple)
                if unit == "degrees" and "rotation" in prop_path.lower():
                    final_values = [math.radians(c) for c in parsed_tuple]

                for i, comp_val in enumerate(final_values):
                    # For vectors like 'location', 'scale', 'rotation_euler', prop_idx is used as component index (0=X, 1=Y, 2=Z)
                    fcurve = action.fcurves.find(prop_path, index=i)
                    if not fcurve:
                        fcurve = action.fcurves.new(prop_path, index=i, action_group=target_obj.name)

                    keyframe_point = fcurve.keyframe_points.insert(frame, comp_val)
                    keyframe_point.interpolation = interpolation_str
                    # print(f"      KF Inserted (Vec Idx {i}): Frame {frame}, Value {comp_val:.3f}, Interpolation {interpolation_str}")
            else:
                print(f"    [Warning] Value '{value_input}' is not a valid tuple string for vector property {target_obj_name}.{prop_path}. Skipping keyframe.")
    print(f"    ✅ Finished animation setup for: {action_name}")

def handle_zw_driver_block(driver_data: dict):
    if not bpy: return

    source_object_name = driver_data.get("SOURCE_OBJECT")
    source_property_path = driver_data.get("SOURCE_PROPERTY")
    target_object_name = driver_data.get("TARGET_OBJECT")
    target_property_path = driver_data.get("TARGET_PROPERTY")
    expression = driver_data.get("EXPRESSION", "var") # Default to direct copy
    driver_name = driver_data.get("NAME", f"ZWDriver_{target_object_name}_{target_property_path}")

    if not all([source_object_name, source_property_path, target_object_name, target_property_path]):
        print(f"[!] Error in ZW-DRIVER '{driver_name}': Missing one or more required fields (SOURCE_OBJECT, SOURCE_PROPERTY, TARGET_OBJECT, TARGET_PROPERTY). Skipping.")
        return

    source_obj = bpy.data.objects.get(source_object_name)
    target_obj = bpy.data.objects.get(target_object_name)

    if not source_obj:
        print(f"[!] Error in ZW-DRIVER '{driver_name}': Source object '{source_object_name}' not found. Skipping.")
        return
    if not target_obj:
        print(f"[!] Error in ZW-DRIVER '{driver_name}': Target object '{target_object_name}' not found. Skipping.")
        return

    print(f"[*] Creating ZW-DRIVER '{driver_name}': {source_object_name}.{source_property_path} -> {target_object_name}.{target_property_path}")

    try:
        parsed_target_path = target_property_path
        parsed_target_index = -1
        if '[' in target_property_path and target_property_path.endswith(']'):
            path_parts = target_property_path.split('[')
            parsed_target_path = path_parts[0]
            try:
                parsed_target_index = int(path_parts[1].rstrip(']'))
            except ValueError:
                print(f"    [Error] Invalid index in TARGET_PROPERTY: {target_property_path} for driver '{driver_name}'. Skipping.")
                return

        # Add driver
        if parsed_target_index != -1:
            fcurve = target_obj.driver_add(parsed_target_path, parsed_target_index)
        else:
            # This handles paths like "location.x", "rotation_euler.z", custom properties etc.
            fcurve = target_obj.driver_add(parsed_target_path)

        driver = fcurve.driver
        driver.type = 'SCRIPTED'
        driver.expression = expression

        # Add variable
        var = driver.variables.new()
        var.name = "var" # Variable name used in the expression
        var.type = 'SINGLE_PROP'

        var_target = var.targets[0]
        var_target.id_type = 'OBJECT'
        var_target.id = source_obj
        var_target.data_path = source_property_path

        print(f"    ✅ Successfully created driver: '{driver_name}'")
        print(f"       Source: {source_obj.name} -> {source_property_path}")
        print(f"       Target: {target_obj.name} -> {target_property_path} (index: {parsed_target_index if parsed_target_index != -1 else 'N/A'})")
        print(f"       Expression: {expression}")

    except Exception as e:
        print(f"    [!] Error setting up driver '{driver_name}': {e}")


# --- Main Processing Logic ---

def process_zw_structure(data_dict: dict, parent_bpy_obj=None, current_bpy_collection=None):
    """
    Recursively processes the parsed ZW structure to find and create objects.
    Passes parent_bpy_obj for parenting and current_bpy_collection for collection assignment.
    """
    if not bpy:
        return

    if current_bpy_collection is None:
        current_bpy_collection = bpy.context.scene.collection

    if not isinstance(data_dict, dict):
        return

    for key, value in data_dict.items():
        created_bpy_object_for_current_zw_object = None
        obj_attributes_for_current_zw_object = None
        target_collection_for_this_object = current_bpy_collection

        if key.upper().startswith("ZW-COLLECTION"):
            collection_name = key.split(":", 1)[1].strip() if ":" in key else key.replace("ZW-COLLECTION", "").strip()
            if not collection_name: collection_name = "Unnamed_ZW_Collection"

            print(f"[*] Processing ZW-COLLECTION block: '{collection_name}' under '{current_bpy_collection.name}'")
            block_bpy_collection = get_or_create_collection(collection_name, parent_collection=current_bpy_collection)

            if isinstance(value, dict) and "CHILDREN" in value and isinstance(value["CHILDREN"], list):
                for child_def_item in value["CHILDREN"]:
                    if isinstance(child_def_item, dict):
                        process_zw_structure(child_def_item, parent_bpy_obj=parent_bpy_obj, current_bpy_collection=block_bpy_collection)
            elif isinstance(value, dict) :
                process_zw_structure(value, parent_bpy_obj=parent_bpy_obj, current_bpy_collection=block_bpy_collection)
            continue

        elif key.upper() == "ZW-FUNCTION":
            if isinstance(value, dict):
                print(f"[*] Processing ZW-FUNCTION block: {value.get('NAME', 'Unnamed Function')}")
                handle_zw_function_block(value) # Pass the dictionary value
            else:
                print(f"[!] Warning: ZW-FUNCTION value is not a dictionary: {value}")
            continue

        elif key.upper() == "ZW-DRIVER": # Handle ZW-DRIVER
            if isinstance(value, dict):
                print(f"[*] Processing ZW-DRIVER block: {value.get('NAME', 'Unnamed Driver')}")
                handle_zw_driver_block(value) # Pass the dictionary value
            else:
                print(f"[!] Warning: ZW-DRIVER value is not a dictionary: {value}")
            continue

        elif key.upper() == "ZW-ANIMATION": # Handle ZW-ANIMATION
            if isinstance(value, dict):
                print(f"  Processing ZW-ANIMATION block: {value.get('NAME', 'UnnamedAnimation')}")
                handle_zw_animation_block(value)
            else:
                print(f"    [Warning] Value for 'ZW-ANIMATION' key is not a dictionary. Value: {value}")
            continue


        if key.upper() == "ZW-OBJECT":
            if isinstance(value, dict):
                obj_attributes_for_current_zw_object = value
            elif isinstance(value, str):
                obj_attributes_for_current_zw_object = {"TYPE": value}
        elif key.lower() in ["sphere", "cube", "plane", "cone", "cylinder", "torus"] and isinstance(value, dict):
            obj_attributes_for_current_zw_object = value.copy()
            obj_attributes_for_current_zw_object["TYPE"] = key

        if obj_attributes_for_current_zw_object:
            created_bpy_object_for_current_zw_object = handle_zw_object_creation(obj_attributes_for_current_zw_object, parent_bpy_obj)

            if created_bpy_object_for_current_zw_object:
                explicit_collection_name = obj_attributes_for_current_zw_object.get("COLLECTION")
                if explicit_collection_name:
                    target_collection_for_this_object = get_or_create_collection(explicit_collection_name, parent_collection=bpy.context.scene.collection)

                if target_collection_for_this_object:
                    for coll in created_bpy_object_for_current_zw_object.users_collection:
                        coll.objects.unlink(created_bpy_object_for_current_zw_object)
                    target_collection_for_this_object.objects.link(created_bpy_object_for_current_zw_object)
                    print(f"    Linked '{created_bpy_object_for_current_zw_object.name}' to collection '{target_collection_for_this_object.name}'")

                children_list = obj_attributes_for_current_zw_object.get("CHILDREN")
                if children_list and isinstance(children_list, list):
                    print(f"[*] Processing CHILDREN for '{created_bpy_object_for_current_zw_object.name}' in collection '{target_collection_for_this_object.name}'")
                    for child_item_definition in children_list:
                        if isinstance(child_item_definition, dict):
                            process_zw_structure(child_item_definition,
                                                 parent_bpy_obj=created_bpy_object_for_current_zw_object,
                                                 current_bpy_collection=target_collection_for_this_object) # Children inherit parent's collection unless specified otherwise
                        else:
                            print(f"    [!] Warning: Item in CHILDREN list is not a dictionary: {child_item_definition}")
                elif children_list is not None:
                     print(f"    [!] Warning: CHILDREN attribute for an object is not a list: {type(children_list)}")
            continue # Finished processing this ZW-OBJECT key

        # Recursive call for other nested structures (like ZW-NESTED-DETAILS or general groups)
        # These do not create their own Blender objects to become parents, nor do they define a new collection context by themselves.
        elif isinstance(value, dict):
            if key.upper() == "ZW-NESTED-DETAILS": # ZW-NESTED-DETAILS doesn't form a collection by its key
                print(f"[*] Processing ZW-NESTED-DETAILS (semantic parent link: {value.get('PARENT')}). Using collection '{current_bpy_collection.name}'")

            process_zw_structure(value, parent_bpy_obj=parent_bpy_obj, current_bpy_collection=current_bpy_collection)


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
    except Exception as e:
        print(f"[X] Error parsing ZW text: {e}")
        print("--- ZW Blender Adapter Finished (with errors) ---")
        return

    try:
        print("[*] Processing ZW structure for Blender object creation...")
        # Initial call starts with scene's master collection
        process_zw_structure(parsed_zw_data, current_bpy_collection=bpy.context.scene.collection)
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
