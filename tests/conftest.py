import json
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


def parse_semver(version: str) -> tuple[int, int, int]:
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
