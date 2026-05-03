import json
import re
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SCHEMA_DIR = ROOT / "core" / "schemas" / "artifacts"
EXAMPLE_DIR = ROOT / "core" / "examples" / "artifacts"
ENTITY_SCHEMA_DIR = ROOT / "core" / "schemas" / "entities"
ENTITY_EXAMPLE_DIR = ROOT / "core" / "examples" / "entities"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


from typing import Tuple

def parse_semver(version: str) -> Tuple[int, int, int]:
    major, minor, patch = version.split(".")
    return int(major), int(minor), int(patch)


def latest_release_path(root_dir: Path) -> Path:
    releases = sorted((root_dir / "registry" / "releases").glob("release_*.json"))
    return max(releases, key=lambda path: parse_semver(load_json(path)["core_version"]))


def latest_release(root_dir: Path) -> dict:
    return load_json(latest_release_path(root_dir))


def validator_for(schema_name: str) -> Draft202012Validator:
    schema = load_json(SCHEMA_DIR / schema_name)
    return Draft202012Validator(schema)


STANDARD_SKILL_HEADERS_V10 = [
    "1. Purpose",
    "2. Trigger / When To Use",
    "3. Prerequisites",
    "4. Input Specification",
    "5. Execution Steps",
    "6. Output Specification",
    "7. Guardrails",
    "8. Gold Standard Checklist",
    "9. Examples",
    "10. Cross-References",
    "11. Maturity Band Variations",
    "12. Validation Criteria",
]


def assert_v10_skill_contract(root_dir: Path, skill_name: str, expected_test_file: str):
    skill_path = root_dir / "core" / "skills" / skill_name / "SKILL.md"
    assert skill_path.exists(), f"Missing V10 skill: {skill_path}"

    text = skill_path.read_text(encoding="utf-8")
    headers = re.findall(r"^##\s+(.+)$", text, re.MULTILINE)
    assert headers == STANDARD_SKILL_HEADERS_V10, (
        f"{skill_path} should follow the V10 12-section skill contract.\n"
        f"Expected: {STANDARD_SKILL_HEADERS_V10}\n"
        f"Got: {headers}"
    )

    test_refs = set(re.findall(r"`(tests/[^`]+\.py)`", text))
    assert expected_test_file in test_refs, (
        f"{skill_path} should reference {expected_test_file} in Validation Criteria."
    )
    for ref in sorted(test_refs):
        assert (root_dir / ref).exists(), f"Missing skill-linked test: {ref}"

    schema_refs = set(re.findall(r"\b([a-z0-9_]+\.schema\.json)\b", text))
    for schema_name in sorted(schema_refs):
        artifact_schema = root_dir / "core" / "schemas" / "artifacts" / schema_name
        entity_schema = root_dir / "core" / "schemas" / "entities" / schema_name
        assert artifact_schema.exists() or entity_schema.exists(), (
            f"Missing schema referenced by {skill_path.name}: {schema_name}"
        )

    example_refs = set(re.findall(r"\b([a-z0-9_]+\.example\.json)\b", text))
    for example_name in sorted(example_refs):
        artifact_example = root_dir / "core" / "examples" / "artifacts" / example_name
        entity_example = root_dir / "core" / "examples" / "entities" / example_name
        assert artifact_example.exists() or entity_example.exists(), (
            f"Missing example referenced by {skill_path.name}: {example_name}"
        )


@pytest.fixture
def root_dir() -> Path:
    return ROOT


@pytest.fixture
def self_hosting_workspace_dir(root_dir: Path) -> Path:
    workspace_dir = root_dir / "internal" / "ProductOS-Next"
    if not workspace_dir.exists():
        pytest.skip("Private self-hosting workspace is not included in this repo boundary.")
    return workspace_dir


@pytest.fixture
def adoption_workspace_dir(root_dir: Path) -> Path:
    workspaces_root = root_dir / "workspaces"
    if not workspaces_root.exists():
        pytest.skip("Private adoption benchmark workspace is not included in this repo boundary.")

    candidates = sorted(
        path
        for path in workspaces_root.iterdir()
        if path.is_dir() and not path.name.startswith(".") and (path / "Notes" / "research").exists()
    )
    if not candidates:
        pytest.skip("Private adoption benchmark workspace is not included in this repo boundary.")
    return candidates[0]


@pytest.fixture
def contract_intelligence_workspace_dir(root_dir: Path) -> Path:
    workspace_dir = root_dir / "workspaces" / "contract-intelligence-platform"
    if not workspace_dir.exists():
        pytest.skip("Private contract-intelligence benchmark workspace is not included in this repo boundary.")
    return workspace_dir


@pytest.fixture
def schema_dir() -> Path:
    return SCHEMA_DIR


@pytest.fixture
def example_dir() -> Path:
    return EXAMPLE_DIR


@pytest.fixture
def entity_schema_dir() -> Path:
    return ENTITY_SCHEMA_DIR


@pytest.fixture
def entity_example_dir() -> Path:
    return ENTITY_EXAMPLE_DIR
