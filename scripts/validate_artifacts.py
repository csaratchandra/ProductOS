#!/usr/bin/env python3

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_EXAMPLE_DIR = ROOT / "core" / "examples" / "registry"
WORKFLOW_EXAMPLE_DIR = ROOT / "core" / "examples" / "workflows"
TRACE_EXAMPLE_DIR = ROOT / "core" / "examples" / "traces"

SURFACES = [
    {
        "label": "core artifacts",
        "schema_dir": ROOT / "core" / "schemas" / "artifacts",
        "example_dir": ROOT / "core" / "examples" / "artifacts",
        "special_examples": {
            "artifact_trace_map.schema.json": TRACE_EXAMPLE_DIR / "status_mail.trace_map.example.json",
            "release_metadata.schema.json": REGISTRY_EXAMPLE_DIR / "release_metadata.example.json",
            "suite_registration.schema.json": REGISTRY_EXAMPLE_DIR / "suite_registration.example.json",
            "workspace_registration.schema.json": REGISTRY_EXAMPLE_DIR / "workspace_registration.example.json",
            "workflow_state.schema.json": WORKFLOW_EXAMPLE_DIR / "biweekly_status_mail.workflow_state.example.json",
        },
    },
    {
        "label": "presentation component artifacts",
        "schema_dir": ROOT / "components" / "presentation" / "schemas" / "artifacts",
        "example_dir": ROOT / "components" / "presentation" / "examples" / "artifacts",
        "special_examples": {},
    },
]


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def example_for_schema(schema_path: Path, example_dir: Path, special_examples: Dict[str, Path]) -> Optional[Path]:
    if schema_path.name in special_examples:
        return special_examples[schema_path.name]

    example_name = schema_path.name.replace(".schema.json", ".example.json")
    candidate = example_dir / example_name
    if candidate.exists():
        return candidate
    return None


def validate_surface(
    *,
    label: str,
    schema_dir: Path,
    example_dir: Path,
    special_examples: Dict[str, Path],
) -> Tuple[List[str], List[Tuple[str, str, list]]]:
    missing_examples = []
    failures = []

    for schema_path in sorted(schema_dir.glob("*.schema.json")):
        example_path = example_for_schema(schema_path, example_dir, special_examples)
        if example_path is None:
            missing_examples.append(f"{label}: {schema_path.name}")
            continue

        schema = load_json(schema_path)
        example = load_json(example_path)

        validator = Draft202012Validator(schema)
        errors = sorted(validator.iter_errors(example), key=lambda item: list(item.path))
        if errors:
            failures.append((f"{label}: {schema_path.name}", example_path.name, errors))

    return missing_examples, failures


def main() -> int:
    failures = []
    missing_examples = []

    for surface in SURFACES:
        surface_missing, surface_failures = validate_surface(**surface)
        missing_examples.extend(surface_missing)
        failures.extend(surface_failures)

    if missing_examples:
        print("Missing examples for schemas:")
        for schema_name in missing_examples:
            print(f"  - {schema_name}")
        return 1

    if failures:
        for schema_name, example_name, errors in failures:
            print(f"FAIL {example_name} against {schema_name}")
            for error in errors:
                path = ".".join(str(part) for part in error.absolute_path) or "<root>"
                print(f"  - {path}: {error.message}")
        return 1

    print("All core and component artifact examples validate against their schemas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
