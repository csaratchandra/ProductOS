from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from core.python.productos_runtime.prd_scope_boundary import build_prd_boundary_report


def test_prd_scope_boundary_report_validates_against_schema(tmp_path: Path, root_dir: Path):
    workspace_dir = tmp_path / "workspace"
    artifacts_dir = workspace_dir / "artifacts"
    artifacts_dir.mkdir(parents=True)

    prd = {
        "schema_version": "1.1.0",
        "prd_id": "prd_demo",
        "workspace_id": "ws_demo",
        "title": "Demo PRD",
        "problem_summary": "Teams need a clearer weekly operating rhythm.",
        "outcome_summary": "Reduce coordination drag.",
        "scope_summary": "Weekly planning and review only.",
        "strategic_context_summary": "Start with a narrow PM wedge.",
        "value_hypothesis": "Structured review beats ad hoc notes.",
        "target_outcomes": ["Ship a reviewable workflow"],
        "target_segment_refs": [{"entity_type": "segment", "entity_id": "seg_pm"}],
        "target_persona_refs": [{"entity_type": "persona", "entity_id": "pers_pm"}],
        "linked_entity_refs": [{"entity_type": "feature", "entity_id": "feat_1"}],
        "upstream_artifact_ids": ["problem_brief_demo"],
        "canonical_persona_archetype_pack_id": "persona_pack_demo",
        "artifact_trace_map_id": "trace_demo",
        "ralph_status": "review_needed",
        "prioritization": {
            "lane": "must_now",
            "priority_score": 80,
            "confidence": "moderate",
            "agentic_delivery_burden": "medium",
            "priority_rationale": "Concrete workflow pain is visible.",
            "reviewer_handoff": "PM should confirm top exclusions."
        },
        "scope_boundaries": ["Web workflow only"],
        "out_of_scope": [
            "Native mobile apps in v1.",
            "Enterprise SSO in v1.",
            "Real-time multiplayer editing in v1.",
            "Marketplace integrations in v1.",
            "Admin analytics in v1.",
            "Billing workflows in v1.",
            "Internationalization in v1.",
            "Public API management in v1."
        ],
        "open_questions": ["Which review lane matters most?"],
        "handoff_risks": ["A broad wedge could create execution sprawl."],
        "generated_at": "2026-05-11T00:00:00Z"
    }
    problem_brief = {
        "problem_statement": "Teams need a clearer weekly operating rhythm."
    }

    (artifacts_dir / "prd.json").write_text(json.dumps(prd), encoding="utf-8")
    (artifacts_dir / "problem_brief.json").write_text(json.dumps(problem_brief), encoding="utf-8")

    report = build_prd_boundary_report(workspace_dir, generated_at="2026-05-11T00:00:00Z")
    schema = json.loads((root_dir / "core" / "schemas" / "artifacts" / "prd_boundary_report.schema.json").read_text(encoding="utf-8"))
    errors = list(Draft202012Validator(schema).iter_errors(report))
    assert not errors
    assert report["approval_status"] in {"approved", "needs_revision"}


def test_prd_scope_boundary_report_flags_vague_language(tmp_path: Path):
    workspace_dir = tmp_path / "workspace"
    artifacts_dir = workspace_dir / "artifacts"
    artifacts_dir.mkdir(parents=True)
    (artifacts_dir / "prd.json").write_text(
        json.dumps(
            {
                "prd_id": "prd_vague",
                "workspace_id": "ws_demo",
                "out_of_scope": ["Other features TBD"],
            }
        ),
        encoding="utf-8",
    )
    report = build_prd_boundary_report(workspace_dir, generated_at="2026-05-11T00:00:00Z")
    assert report["approval_status"] == "blocked"
    assert any(item["issue"] == "vague_language" for item in report["flagged_boundaries"])
