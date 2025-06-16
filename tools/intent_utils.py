"""Utilities for handling ZW-INTENT blocks."""

from typing import Union


def get_indentation(line_text: str) -> int:
    """Calculates the leading whitespace indentation of a string."""
    return len(line_text) - len(line_text.lstrip())

def validate_zw_intent_block(intent_string: str) -> Union[dict, str]:
    """
    Parses and validates a ZW-INTENT block string.
    Checks for TARGET_SYSTEM and either ROUTE_FILE or an inline ZW-PAYLOAD.
    If ZW-PAYLOAD is present, its content (potentially multi-line) is captured.
    Payload content is typically more indented than the ZW-PAYLOAD directive line.
    A new directive at an indentation level less than or equal to the
    ZW-PAYLOAD directive will terminate payload capture.
    """
    lines = intent_string.strip().split('\n')
    intent_data = {}

    found_line_starting_with_zw_payload = any(line.strip().startswith("ZW-PAYLOAD:") for line in lines)

    i = 0
    while i < len(lines):
        current_line_text = lines[i]
        current_line_strip = current_line_text.strip()

        if not current_line_strip:
            i += 1
            continue

        if ':' in current_line_strip:
            key, value_on_line = current_line_strip.split(':', 1)
            key = key.strip()
            value_on_line = value_on_line.strip()

            current_directive_indent = get_indentation(current_line_text)

            if key == "ZW-PAYLOAD":
                payload_content_list = []
                if value_on_line:
                    payload_content_list.append(value_on_line)

                payload_line_idx = i + 1
                while payload_line_idx < len(lines):
                    next_line_text = lines[payload_line_idx]
                    next_line_strip = next_line_text.strip()
                    next_line_indent = get_indentation(next_line_text)

                    if not next_line_strip:
                        if next_line_indent > current_directive_indent:
                             payload_content_list.append(next_line_text)
                        else:
                            break
                    elif ':' in next_line_strip and next_line_indent <= current_directive_indent:
                        break
                    elif next_line_indent > current_directive_indent:
                        payload_content_list.append(next_line_text)
                    else:
                        break
                    payload_line_idx += 1

                intent_data[key] = "\n".join(payload_content_list).strip()
                i = payload_line_idx
                continue
            else: # Not a ZW-PAYLOAD key
                intent_data[key] = value_on_line
        i += 1

    if "TARGET_SYSTEM" not in intent_data:
        return f"Missing TARGET_SYSTEM in ZW-INTENT block."

    if "ROUTE_FILE" not in intent_data and not found_line_starting_with_zw_payload:
        return f"Missing ROUTE_FILE or inline ZW-PAYLOAD in ZW-INTENT block."

    return intent_data

if __name__ == "__main__":
    valid_intent_1 = """
    TARGET_SYSTEM: Blender
    ROUTE_FILE: scenes/my_scene.zw
    DESCRIPTION: A cool scene to render.
    """
    print(f"Valid intent 1: {validate_zw_intent_block(valid_intent_1)}")

    valid_intent_2_inline_payload = """
    TARGET_SYSTEM: Godot
    DESCRIPTION: Setup player in Godot.
    ZW-PAYLOAD:
      TYPE: Player_Setup
      PLAYER_MODEL: player.glb
    """
    print(f"Valid intent 2 (inline payload): {validate_zw_intent_block(valid_intent_2_inline_payload)}")

    missing_target_system = """
    ROUTE_FILE: some/path.zw
    DESCRIPTION: Missing target.
    """
    print(f"Missing TARGET_SYSTEM: {validate_zw_intent_block(missing_target_system)}")

    missing_route_or_payload = """
    TARGET_SYSTEM: SomeSystem
    DESCRIPTION: No route or payload.
    """
    print(f"Missing ROUTE_FILE or ZW-PAYLOAD: {validate_zw_intent_block(missing_route_or_payload)}")

    valid_intent_with_payload_directive_single_line = """
    TARGET_SYSTEM: Blender
    ZW-PAYLOAD: This is a simple string value for ZW-PAYLOAD directive.
    DESCRIPTION: Test payload as a simple directive.
    """
    print(f"Valid intent with ZW-PAYLOAD directive single line: {validate_zw_intent_block(valid_intent_with_payload_directive_single_line)}")

    # Reformatted problematic case to ensure indent 0 for ZW-PAYLOAD and TARGET_SYSTEM lines
    valid_intent_payload_first = """ZW-PAYLOAD:
  ACTION: ANIMATE
  TARGET: Cube
TARGET_SYSTEM: Blender
PRIORITY: HIGH
"""
    print(f"Valid intent (payload first - testing directive capture): {validate_zw_intent_block(valid_intent_payload_first)}")

    valid_intent_empty_payload_then_directive = """
    TARGET_SYSTEM: Godot
    ZW-PAYLOAD:
    DESCRIPTION: Setup with empty payload.
    """
    print(f"Valid intent (empty ZW-PAYLOAD then directive): {validate_zw_intent_block(valid_intent_empty_payload_then_directive)}")

    valid_intent_payload_last = """
    TARGET_SYSTEM: Blender
    DESCRIPTION: A scene.
    ZW-PAYLOAD:
      ENTITY: Cube
      ACTION: Rotate
    """
    print(f"Valid intent (ZW-PAYLOAD is last): {validate_zw_intent_block(valid_intent_payload_last)}")

    intent_zw_payload_complex = """ZW-PAYLOAD:
  TYPE: SCENE_SETUP
  OBJECTS:
    - NAME: Camera
      TYPE: CAMERA
      POSITION: [0, -10, 1]
      ROTATION: [90, 0, 0]
    - NAME: Light
      TYPE: LIGHT
      LIGHT_TYPE: SUN
      ENERGY: 2.0
    - NAME: GroundPlane
      TYPE: MESH
      MESH_TYPE: PLANE
      SIZE: 100
      MATERIAL: GroundMaterial
  MATERIALS:
    - NAME: GroundMaterial
      TYPE: PRINCIPLED_BSDF
      COLOR: [0.1, 0.1, 0.1]
TARGET_SYSTEM: Blender
EXTRA_INFO: This is some extra info.
"""
    print(f"Complex ZW-PAYLOAD with following directives: {validate_zw_intent_block(intent_zw_payload_complex)}")

    # Reformatted simplified problematic case
    valid_intent_payload_first_simplified = """ZW-PAYLOAD:
  DATA
TARGET_SYSTEM: Blender
"""
    print(f"Simplified payload first: {validate_zw_intent_block(valid_intent_payload_first_simplified)}")
