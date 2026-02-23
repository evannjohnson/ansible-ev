#!/usr/bin/env python3
"""Validate an Ansible preset JSON file against the preset schema."""

import json
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("ERROR: jsonschema package not installed. Run: pip install jsonschema")
    sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print(f"usage: {Path(sys.argv[0]).name} <preset.json>")
        sys.exit(1)

    preset_path = Path(sys.argv[1])
    schema_path = Path(__file__).parent / "ansible-preset-schema.json"

    if not schema_path.exists():
        print(f"ERROR: schema not found: {schema_path}")
        sys.exit(1)

    try:
        with schema_path.open() as f:
            schema = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSON in schema: {e}")
        sys.exit(1)

    if not preset_path.exists():
        print(f"ERROR: file not found: {preset_path}")
        sys.exit(1)

    try:
        with preset_path.open() as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSON in preset file: {e}")
        sys.exit(1)

    validator = jsonschema.Draft7Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))

    if not errors:
        print("VALID")
        sys.exit(0)

    for error in errors:
        path_str = "".join(
            f"[{part}]" if isinstance(part, int) else f".{part}"
            for part in error.absolute_path
        ) or "."
        print(f"ERROR: {path_str}")
        print(f"  {error.message}")
        print()

    count = len(errors)
    print(f"{count} error(s) found.")
    sys.exit(1)


if __name__ == "__main__":
    main()
