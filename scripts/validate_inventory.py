#!/usr/bin/env python3
"""Validate the expanded Ansible inventory against the Kubernetes schema."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


def load_inventory(inventory_path: Path) -> dict:
    """Run ansible-inventory and return the parsed JSON data."""
    command = [
        "ansible-inventory",
        "-i",
        str(inventory_path),
        "--list",
    ]
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as error:
        raise RuntimeError(
            "ansible-inventory is not available. Install Ansible or activate the "
            "project virtual environment before running validation."
        ) from error
    except subprocess.CalledProcessError as error:
        raise RuntimeError(
            "ansible-inventory failed to render the inventory.\n"
            f"Command: {' '.join(command)}\n"
            f"stdout:\n{error.stdout}\n"
            f"stderr:\n{error.stderr}"
        ) from error

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            "ansible-inventory did not return valid JSON output."
        ) from error


def validate_inventory(data: dict, schema_path: Path) -> None:
    """Validate the inventory data against the JSON schema."""
    schema = json.loads(schema_path.read_text())
    validator = Draft202012Validator(schema)

    errors = sorted(validator.iter_errors(data), key=lambda error: error.path)
    if errors:
        messages = [
            f"Validation error at {'/'.join(map(str, error.path)) or '<root>'}: {error.message}"
            for error in errors
        ]
        raise RuntimeError("\n".join(messages))


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    inventory_path = repo_root / "inventories" / "hosts.yml"
    schema_path = repo_root / "schemas" / "inventory.schema.json"

    try:
        inventory = load_inventory(inventory_path)
        validate_inventory(inventory, schema_path)
    except RuntimeError as error:
        print(error, file=sys.stderr)
        return 1

    print("Inventory validation succeeded.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
