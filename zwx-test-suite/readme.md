

This directory contains `.zwx` files for testing the intent-routing pipeline,
including validation, execution via `engain_orbit.py`, and monitoring via `orbit_watchdog.py`.

## Categories

- **basic/**: Standard pass/fail tests
- **edge_cases/**: Unicode, indentation quirks, extra spacing
- **godot/**: Godot-specific intent tests (stub or failure expected)

## Test Naming Convention

- Files prefixed with `invalid_` are expected to fail validation or execution by `engain_orbit.py`. The test runner (`tools/test_orbit_routing.py`) considers a non-zero exit code from `engain_orbit.py` as a PASS for these test cases.
- All other `.zwx` files are expected to pass, meaning `engain_orbit.py` should exit with a zero status code.

### Example:
- `invalid_missing_target.zwx` → PASS if `engain_orbit.py` exits with non-zero.
- `valid_inline_payload.zwx` → PASS if `engain_orbit.py` exits with 0.

## Running the Suite

To execute all tests in this suite, run:
```bash
python3 tools/test_orbit_routing.py
```

You can also run individual tests directly with `engain_orbit.py`:
```bash
python3 tools/engain_orbit.py zwx-test-suite/basic/valid_inline_payload.zwx
```

Or test the `orbit_watchdog.py` by copying files into its watch folder:
```bash
# Ensure orbit_watchdog.py is running
cp zwx-test-suite/basic/valid_inline_payload.zwx zw_drop_folder/validated_patterns/
```
