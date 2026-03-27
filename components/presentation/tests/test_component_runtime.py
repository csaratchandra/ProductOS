import json
from copy import deepcopy
from pathlib import Path
import subprocess
import sys

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from components.presentation.python.productos_presentation.runtime import (
    build_evidence_pack,
    build_presentation_story,
    build_publish_check,
    build_ppt_export_plan,
    build_render_spec,
    render_render_spec_html,
)

EXAMPLE_DIR = ROOT / "components" / "presentation" / "examples" / "artifacts"
SCHEMA_DIR = ROOT / "components" / "presentation" / "schemas" / "artifacts"
CORE_SCHEMA_DIR = ROOT / "core" / "schemas" / "artifacts"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validator_for(schema_name: str) -> Draft202012Validator:
    return Draft202012Validator(load_json(SCHEMA_DIR / schema_name))


def core_validator_for(schema_name: str) -> Draft202012Validator:
    return Draft202012Validator(load_json(CORE_SCHEMA_DIR / schema_name))


def test_component_pipeline_matches_public_schemas():
    presentation_brief = load_json(EXAMPLE_DIR / "presentation_brief.example.json")
    example_export_plan = load_json(EXAMPLE_DIR / "ppt_export_plan.example.json")

    evidence_pack = build_evidence_pack(presentation_brief)
    presentation_story = build_presentation_story(presentation_brief, evidence_pack)
    render_spec = build_render_spec(presentation_brief, presentation_story)
    publish_check = build_publish_check(presentation_brief, render_spec)
    html = render_render_spec_html(render_spec)
    export_plan = build_ppt_export_plan(render_spec)

    assert not sorted(
        validator_for("evidence_pack.schema.json").iter_errors(evidence_pack),
        key=lambda item: list(item.path),
    )
    assert not sorted(
        validator_for("presentation_story.schema.json").iter_errors(presentation_story),
        key=lambda item: list(item.path),
    )
    assert not sorted(
        validator_for("render_spec.schema.json").iter_errors(render_spec),
        key=lambda item: list(item.path),
    )
    assert not sorted(
        validator_for("publish_check.schema.json").iter_errors(publish_check),
        key=lambda item: list(item.path),
    )
    assert not sorted(
        validator_for("ppt_export_plan.schema.json").iter_errors(example_export_plan),
        key=lambda item: list(item.path),
    )
    assert not sorted(
        validator_for("ppt_export_plan.schema.json").iter_errors(export_plan),
        key=lambda item: list(item.path),
    )
    assert "<html" in html.lower()
    assert "primary-claim" in html
    assert "hero-strip" in html
    assert "risk-matrix" in html
    assert "slide-frame" in html
    assert "slide-notes" in html
    assert "hero-signal-rail" in html
    assert "risk-heatmap" in html
    assert "echarts.min.js" in html
    assert presentation_story["story_arc"][0].startswith("Start with the recommendation")
    assert evidence_pack["evidence_units"][0]["confidence_reason"].startswith("Confidence is derived")
    assert "composition_payload" in render_spec["slides"][0]
    assert export_plan["status"] == "composition-aware"
    assert export_plan["slide_count"] == len(render_spec["slides"])
    assert export_plan["slide_rendering_plan"]
    assert export_plan["native_shape_counts"]
    assert export_plan["render_spec_id"] == render_spec["render_spec_id"]
    assert len(render_spec["slides"][0]["composition_payload"]["evidence_items"]) <= 4


def test_publish_check_catches_missing_evidence():
    presentation_brief = load_json(EXAMPLE_DIR / "presentation_brief.example.json")

    evidence_pack = build_evidence_pack(presentation_brief)
    presentation_story = build_presentation_story(presentation_brief, evidence_pack)
    render_spec = build_render_spec(presentation_brief, presentation_story)
    weakened = deepcopy(render_spec)
    weakened["slides"][0]["composition_payload"]["evidence_items"] = []
    weakened["slides"][0]["source_refs"] = []

    publish_check = build_publish_check(presentation_brief, weakened)

    assert publish_check["publish_ready"] is False
    assert publish_check["claim_support_exceptions"]
    assert publish_check["evidence_quality_score"] < 3.5


def test_component_manifest_matches_public_surface():
    manifest = load_json(ROOT / "components" / "presentation" / "component.json")
    schema_artifacts = {
        path.name.replace(".schema.json", "")
        for path in SCHEMA_DIR.glob("*.schema.json")
    }
    example_artifacts = {
        path.name.replace(".example.json", "")
        for path in EXAMPLE_DIR.glob("*.example.json")
    }

    assert set(manifest["artifacts"]) == schema_artifacts == example_artifacts
    for entrypoint in manifest["entrypoints"].values():
        assert (ROOT / entrypoint).exists(), f"Missing manifest entrypoint: {entrypoint}"


def test_component_contracts_match_core_agent_contracts():
    for contract_name in [
        "editor",
        "presentation",
        "publisher",
        "storyteller",
        "visual-design",
    ]:
        component_contract = (ROOT / "components" / "presentation" / "contracts" / contract_name / "CONTRACT.md").read_text(
            encoding="utf-8"
        )
        core_contract = (ROOT / "core" / "agents" / contract_name / "CONTRACT.md").read_text(encoding="utf-8")
        assert component_contract == core_contract, f"Contract drift detected for {contract_name}"


def test_export_presentation_script_writes_consistent_outputs(tmp_path: Path):
    script_path = ROOT / "scripts" / "export_presentation.py"
    brief_path = EXAMPLE_DIR / "presentation_brief.example.json"

    result = subprocess.run(
        [
            sys.executable,
            str(script_path),
            str(brief_path),
            "--output-dir",
            str(tmp_path),
            "--skip-ppt",
        ],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    )

    assert result.returncode == 0, result.stderr

    brief = load_json(brief_path)
    brief_id = brief["presentation_brief_id"]
    render_spec_path = tmp_path / f"{brief_id}.render-spec.json"
    slide_spec_path = tmp_path / f"{brief_id}.slide-spec.json"
    evidence_pack = load_json(tmp_path / f"{brief_id}.evidence-pack.json")
    presentation_story = load_json(tmp_path / f"{brief_id}.presentation-story.json")
    render_spec = load_json(render_spec_path)
    publish_check = load_json(tmp_path / f"{brief_id}.publish-check.json")
    export_plan = load_json(tmp_path / f"{brief_id}.ppt-export-plan.json")

    assert render_spec_path.exists()
    assert slide_spec_path.exists()
    assert (tmp_path / f"{brief_id}.html").exists()

    assert not sorted(
        validator_for("evidence_pack.schema.json").iter_errors(evidence_pack),
        key=lambda item: list(item.path),
    )
    assert not sorted(
        validator_for("presentation_story.schema.json").iter_errors(presentation_story),
        key=lambda item: list(item.path),
    )
    assert not sorted(
        validator_for("render_spec.schema.json").iter_errors(render_spec),
        key=lambda item: list(item.path),
    )
    assert not sorted(
        validator_for("publish_check.schema.json").iter_errors(publish_check),
        key=lambda item: list(item.path),
    )
    assert not sorted(
        validator_for("ppt_export_plan.schema.json").iter_errors(export_plan),
        key=lambda item: list(item.path),
    )
    assert not sorted(
        core_validator_for("slide_spec.schema.json").iter_errors(load_json(slide_spec_path)),
        key=lambda item: list(item.path),
    )
