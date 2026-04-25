import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from components.workflow_corridor.python.productos_workflow_corridor.runtime import (
    build_corridor_publish_check,
    build_workflow_corridor_bundle,
    render_corridor_html,
)
from core.python.productos_runtime import build_visual_direction_plan

EXAMPLE_DIR = ROOT / "core" / "examples" / "artifacts"
SCHEMA_DIR = ROOT / "core" / "schemas" / "artifacts"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validator_for(schema_name: str) -> Draft202012Validator:
    return Draft202012Validator(load_json(SCHEMA_DIR / schema_name))


def source_bundle() -> dict:
    return {
        "workspace_id": "ws_corridor_demo",
        "title": "Configurable workflow corridor",
        "corridor_story": "One HTML corridor page should explain the workflow, trust posture, and overlay logic without presenter narration.",
        "source_artifact_ids": [
            "workflow_spec_corridor_demo",
            "persona_pack_corridor_demo",
            "segment_map_corridor_demo",
        ],
        "workflow": {
            "stages": [
                {
                    "stage_id": "stage_intake",
                    "label": "Intake",
                    "headline": "Normalize raw signal into one reviewable intake",
                    "summary": "ProductOS brings notes, support exports, and discovery inputs into one bounded starting point.",
                    "lane_ids": ["lane_signal", "lane_pm"],
                    "owner_role": "Research",
                    "status": "approved",
                    "claim_mode": "observed",
                    "proof_refs": ["proof_intake"],
                },
                {
                    "stage_id": "stage_design",
                    "label": "Design",
                    "headline": "Curate one corridor story with explicit proof posture",
                    "summary": "PM chooses the baseline and keeps claim posture explicit.",
                    "lane_ids": ["lane_pm"],
                    "owner_role": "PM",
                    "status": "approved",
                    "claim_mode": "observed",
                    "proof_refs": ["proof_publish"],
                },
                {
                    "stage_id": "stage_review",
                    "label": "Review",
                    "headline": "Show the handoff and keep watch states visible",
                    "summary": "Leadership and operations see where the workflow remains bounded.",
                    "lane_ids": ["lane_exec", "lane_ops"],
                    "owner_role": "Operations",
                    "status": "watch",
                    "claim_mode": "inferred",
                    "proof_refs": ["proof_handoff"],
                },
            ],
            "lanes": [
                {
                    "lane_id": "lane_signal",
                    "label": "Signal",
                    "summary": "Raw signal intake",
                    "owner_role": "Research",
                },
                {
                    "lane_id": "lane_pm",
                    "label": "PM",
                    "summary": "PM curation and approval",
                    "owner_role": "PM",
                },
                {
                    "lane_id": "lane_exec",
                    "label": "Executive",
                    "summary": "Decision trust review",
                    "owner_role": "Leadership",
                },
                {
                    "lane_id": "lane_ops",
                    "label": "Ops",
                    "summary": "Operational handoff and follow-through",
                    "owner_role": "Operations",
                },
            ],
            "owner_transitions": [
                {
                    "transition_id": "transition_intake_design",
                    "from_stage_id": "stage_intake",
                    "to_stage_id": "stage_design",
                    "from_owner_role": "Research",
                    "to_owner_role": "PM",
                    "status": "approved",
                    "claim_mode": "observed",
                    "proof_refs": ["proof_intake"],
                },
                {
                    "transition_id": "transition_design_review",
                    "from_stage_id": "stage_design",
                    "to_stage_id": "stage_review",
                    "from_owner_role": "PM",
                    "to_owner_role": "Operations",
                    "status": "watch",
                    "claim_mode": "inferred",
                    "proof_refs": ["proof_handoff"],
                },
            ],
        },
        "personas": [
            {
                "persona_id": "persona_buyer",
                "label": "Buyer",
                "summary": "Needs the corridor to explain itself.",
                "goal": "Trust the workflow and understand what the product actually proves.",
                "visible_stage_ids": ["stage_intake", "stage_design", "stage_review"],
                "priority_proof_refs": ["proof_publish"],
            },
            {
                "persona_id": "persona_operator",
                "label": "Operator",
                "summary": "Needs governance and owner transitions.",
                "goal": "See the handoff and any watch states without extra narration.",
                "visible_stage_ids": ["stage_design", "stage_review"],
                "priority_proof_refs": ["proof_handoff"],
            },
        ],
        "segment_overlays": [
            {
                "overlay_id": "segment_mid_market",
                "dimension": "segment",
                "label": "Mid-market",
                "summary": "Prefers one buyer-safe corridor story with clear package scope.",
                "impact_stage_ids": ["stage_intake", "stage_design"],
                "claim_mode": "observed",
                "proof_refs": ["proof_intake"],
            }
        ],
        "operating_models": [
            {
                "overlay_id": "operating_async",
                "dimension": "operating_model",
                "label": "Async review",
                "summary": "Keeps proof and governance visible for self-serve review.",
                "impact_stage_ids": ["stage_design", "stage_review"],
                "claim_mode": "observed",
                "proof_refs": ["proof_publish"],
            }
        ],
        "package_scope": [
            {
                "package_id": "package_public_corridor",
                "label": "Public Corridor",
                "summary": "Includes publishable workflow corridor pages and proof rails.",
                "included_stage_ids": ["stage_intake", "stage_design", "stage_review"],
            }
        ],
        "terminal_outcomes": [
            {
                "outcome_id": "outcome_confidence",
                "label": "Customer confidence",
                "summary": "The workflow can be shared externally without apology.",
                "status": "approved",
                "claim_mode": "observed",
                "kpi_refs": ["kpi_confidence"],
                "proof_refs": ["proof_publish"],
            }
        ],
        "kpi_mappings": [
            {
                "kpi_id": "kpi_confidence",
                "label": "Shareable confidence",
                "summary": "Publish checks stay excellent in public mode.",
                "stage_id": "stage_design",
                "target_outcome_id": "outcome_confidence",
                "claim_mode": "observed",
                "proof_refs": ["proof_publish"],
            }
        ],
        "proof_items": [
            {
                "proof_id": "proof_intake",
                "label": "Artifact-driven intake",
                "summary": "The corridor starts from structured ProductOS artifacts instead of manual-only page edits.",
                "claim_mode": "observed",
                "source_artifact_id": "workflow_spec_corridor_demo",
                "customer_safe": True,
            },
            {
                "proof_id": "proof_publish",
                "label": "Publish gate coverage",
                "summary": "Narrative clarity, proof visibility, and audience safety all have hard publish checks.",
                "claim_mode": "observed",
                "source_artifact_id": "corridor_publish_policy",
                "customer_safe": True,
            },
            {
                "proof_id": "proof_handoff",
                "label": "Visible watch state",
                "summary": "The PM to Ops handoff is visible but still intentionally bounded as inferred.",
                "claim_mode": "inferred",
                "source_artifact_id": "validation_lane_report_corridor",
                "customer_safe": True,
            },
        ],
        "workspace_input_refs": [
            {
                "ref_id": "workspace_manifest_ws_corridor_demo",
                "ref_type": "workspace_manifest",
                "label": "Workspace packaging context",
                "customer_safe": True,
            }
        ],
    }


def test_corridor_examples_match_schemas():
    example_names = [
        "workflow_corridor_spec.example.json",
        "corridor_proof_pack.example.json",
        "corridor_narrative_plan.example.json",
        "corridor_render_model.example.json",
        "corridor_publish_check.example.json",
    ]
    for example_name in example_names:
        schema_name = example_name.replace(".example.json", ".schema.json")
        errors = sorted(
            validator_for(schema_name).iter_errors(load_json(EXAMPLE_DIR / example_name)),
            key=lambda item: list(item.path),
        )
        assert not errors, f"{example_name} failed {schema_name}: {[error.message for error in errors]}"


def test_workflow_corridor_bundle_supports_public_generation_from_artifacts():
    bundle = build_workflow_corridor_bundle(source_bundle())
    html = render_corridor_html(bundle["corridor_render_model"])

    assert "<html" in html.lower()
    assert "workflow-corridor" in html
    assert "Proof rail" in html
    assert "Persona visibility matrix" in html
    assert "Governance Rail" in html
    assert bundle["corridor_publish_check"]["publish_ready"] is True
    assert bundle["corridor_publish_check"]["review_grade"] == "excellent"

    validations = {
        "workflow_corridor_spec.schema.json": bundle["workflow_corridor_spec"],
        "corridor_proof_pack.schema.json": bundle["corridor_proof_pack"],
        "corridor_narrative_plan.schema.json": bundle["corridor_narrative_plan"],
        "corridor_render_model.schema.json": bundle["corridor_render_model"],
        "corridor_publish_check.schema.json": bundle["corridor_publish_check"],
    }
    for schema_name, payload in validations.items():
        errors = sorted(validator_for(schema_name).iter_errors(payload), key=lambda item: list(item.path))
        assert not errors, f"{schema_name} failed: {[error.message for error in errors]}"


def test_workflow_corridor_bundle_supports_workspace_context_and_browse_mode():
    bundle = build_workflow_corridor_bundle(
        source_bundle(),
        publication_mode="product_browse",
        audience_mode="product_browse",
        curated_overrides={
            "manual_copy_overrides": [
                {
                    "target_id": "stage_design",
                    "replacement": "Use internal browse mode to curate the corridor before public publish.",
                }
            ]
        },
    )

    assert bundle["workflow_corridor_spec"]["publication_mode"] == "product_browse"
    assert bundle["workflow_corridor_spec"]["customer_safe"] is False
    corridor_section = next(
        section for section in bundle["corridor_render_model"]["sections"] if section["section_id"] == "corridor"
    )
    assert any("curate the corridor" in card["headline"] for card in corridor_section["cards"])


def test_visual_direction_plan_matches_corridor_render_foundations():
    direction_plan = build_visual_direction_plan(
        "corridor",
        source_bundle(),
        input_ref="generated://tests/corridor-source.json",
        audience_mode="customer_safe_public",
        publication_mode="publishable_external",
    )
    bundle = build_workflow_corridor_bundle(source_bundle())

    assert direction_plan["theme_preset"] == bundle["corridor_render_model"]["theme"]["preset"]
    assert direction_plan["composition_strategy"]["composition_family"] == bundle["corridor_render_model"]["visual_form"]
    assert bundle["corridor_render_model"]["reading_path"] == {
        "desktop": bundle["corridor_narrative_plan"]["desktop_reading_path"],
        "mobile": bundle["corridor_narrative_plan"]["mobile_reading_path"],
    }
    assert direction_plan["output_targets"] == ["html"]
    assert direction_plan["fidelity_mode"] == "html_first"


def test_workflow_corridor_publish_check_fails_when_proof_modes_are_missing():
    bundle = build_workflow_corridor_bundle(source_bundle())
    broken_spec = json.loads(json.dumps(bundle["workflow_corridor_spec"]))
    broken_spec["message_claims"][0]["proof_refs"] = []
    broken_spec["message_claims"][0]["claim_mode"] = "unsupported"

    publish_check = build_corridor_publish_check(broken_spec, bundle["corridor_render_model"])

    assert publish_check["publish_ready"] is False
    assert any("Claim mode" in issue for issue in publish_check["blocking_issues"])
    assert any("Proof visibility" in issue for issue in publish_check["blocking_issues"])


def test_workflow_corridor_publish_check_fails_when_customer_safe_filtering_is_incomplete():
    bundle = build_workflow_corridor_bundle(source_bundle())
    broken_spec = json.loads(json.dumps(bundle["workflow_corridor_spec"]))
    broken_render = json.loads(json.dumps(bundle["corridor_render_model"]))

    broken_spec["canonical_stages"][0]["visibility"] = "internal"
    broken_render["layout_guardrails"]["customer_safe_filter_applied"] = False
    publish_check = build_corridor_publish_check(broken_spec, broken_render, bundle["corridor_proof_pack"])

    assert publish_check["publish_ready"] is False
    assert any("Customer-safe filtering" in issue for issue in publish_check["blocking_issues"])


def test_workflow_corridor_publish_check_fails_on_ambiguous_handoffs_and_mobile_collapse():
    bundle = build_workflow_corridor_bundle(source_bundle())
    broken_spec = json.loads(json.dumps(bundle["workflow_corridor_spec"]))
    broken_render = json.loads(json.dumps(bundle["corridor_render_model"]))

    broken_spec["owner_transitions"][0]["to_owner_role"] = ""
    broken_render["reading_path"]["mobile"] = ["hero", "outcomes"]
    broken_render["layout_guardrails"]["slide_like_repetition"] = True
    publish_check = build_corridor_publish_check(broken_spec, broken_render, bundle["corridor_proof_pack"])

    assert publish_check["publish_ready"] is False
    assert any("Ownership or handoff transitions are ambiguous." == issue for issue in publish_check["blocking_issues"])
    assert any("Mobile reading path" in issue for issue in publish_check["blocking_issues"])
    assert any("slide-like repetition" in issue for issue in publish_check["blocking_issues"])


def test_export_workflow_corridor_script_writes_outputs(tmp_path: Path):
    script_path = ROOT / "scripts" / "export_workflow_corridor.py"
    source_path = tmp_path / "source.json"
    source_path.write_text(json.dumps(source_bundle(), indent=2) + "\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(script_path),
            str(source_path),
            "--output-dir",
            str(tmp_path / "out"),
        ],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    out_dir = tmp_path / "out"
    assert (out_dir / "workflow_corridor_spec.json").exists()
    assert (out_dir / "corridor_proof_pack.json").exists()
    assert (out_dir / "corridor_narrative_plan.json").exists()
    assert (out_dir / "corridor_render_model.json").exists()
    assert (out_dir / "corridor_publish_check.json").exists()
    assert (out_dir / "workflow_corridor.html").exists()
