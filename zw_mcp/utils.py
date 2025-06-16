import ast


def safe_eval(str_val, default_val):
    """Safely evaluate a string to a Python literal."""
    if not isinstance(str_val, str):
        return default_val
    try:
        return ast.literal_eval(str_val)
    except (ValueError, SyntaxError):
        return default_val


def parse_color(color_val, default=(1.0, 1.0, 1.0, 1.0)):
    """Parse a color definition from hex or tuple string formats."""
    if not isinstance(color_val, str):
        return default

    val = color_val.strip()
    if val.startswith("#"):
        try:
            r = int(val[1:3], 16) / 255.0
            g = int(val[3:5], 16) / 255.0
            b = int(val[5:7], 16) / 255.0
            a = int(val[7:9], 16) / 255.0 if len(val) == 9 else 1.0
            return (r, g, b, a)
        except Exception:
            return default

    if val.startswith("(") and val.endswith(")"):
        try:
            tup = ast.literal_eval(val)
            if isinstance(tup, (list, tuple)):
                if len(tup) == 3:
                    return (float(tup[0]), float(tup[1]), float(tup[2]), 1.0)
                if len(tup) == 4:
                    return (float(tup[0]), float(tup[1]), float(tup[2]), float(tup[3]))
        except Exception:
            return default

    return default
