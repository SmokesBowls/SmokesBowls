# ZWX Test Suite

This folder contains structured `.zwx` files used for testing `engain_orbit.py` and validating the intent routing system.

## Test Naming Convention

- Files starting with `valid_` are expected to be successfully processed.
- Files starting with `invalid_` are expected to fail validation or execution.
- Files are grouped by subfolder topic (e.g., `godot/`, `payload_variants/`, etc.).

## Test Runner

Run the test suite from the root:

```bash
python tools/test_orbit_routing.py

