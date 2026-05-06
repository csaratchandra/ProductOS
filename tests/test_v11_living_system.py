"""Tests for ProductOS V11 Living System components."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.python.productos_runtime.living_system import (
    build_regeneration_queue,
    classify_impact,
    detect_circular_dependencies,
    generate_delta_preview,
    process_regeneration_item,
)
from core.python.productos_runtime.markdown_renderer import (
    preserve_annotations,
    render_living_document,
    resolve_source_artifacts,
)
from core.python.productos_runtime.export_pipeline import export_artifact


class TestRegenerationQueue:
    """Test the regeneration queue builder and processor."""

    def test_classify_impact_mechanical(self):
        source = {"event_type": "artifact_updated", "change_summary": "version bump and date stamp updated"}
        target = {"schema_version": "1.0.0", "title": "Test Artifact"}
        result = classify_impact(source, target)
        assert result == "mechanical"

    def test_classify_impact_content_deep(self):
        source = {"event_type": "competitive_alert", "change_summary": "competitor launched new pricing strategy"}
        target = {"schema_version": "1.0.0", "title": "Strategy Brief"}
        result = classify_impact(source, target)
        assert result == "content_deep"

    def test_classify_impact_default(self):
        source = {"event_type": "artifact_updated", "change_summary": "unspecified change"}
        target = {"schema_version": "1.0.0", "title": "Test Artifact"}
        result = classify_impact(source, target)
        assert result == "content_deep"

    def test_generate_delta_preview(self):
        source = {"event_type": "artifact_updated", "change_summary": "version bump"}
        target = {"schema_version": "1.0.0", "title": "Test Artifact", "artifact_id": "test_001"}
        result = generate_delta_preview(source, target)
        assert "Mechanical update" in result
        assert "test_001" in result
        assert "auto-executable" in result

    def test_build_regeneration_queue_empty(self, tmp_path):
        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir()
        (workspace_dir / "artifacts").mkdir()
        
        trigger = {
            "event_type": "artifact_updated",
            "source_artifact_ref": "artifacts/prd.json",
            "change_summary": "version bump"
        }
        
        queue = build_regeneration_queue(trigger, workspace_dir, generated_at="2026-05-06T12:00:00Z")
        
        assert queue["schema_version"] == "1.0.0"
        assert queue["status"] == "completed"
        assert len(queue["queued_items"]) == 0
        assert queue["pm_review_required"] is False

    def test_process_regeneration_item_approve_mechanical(self, tmp_path):
        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir()
        artifacts_dir = workspace_dir / "artifacts"
        artifacts_dir.mkdir()
        
        artifact = {"schema_version": "1.0.0", "title": "Test", "version": 1, "updated_at": "old"}
        artifact_path = artifacts_dir / "test.json"
        with artifact_path.open("w") as f:
            json.dump(artifact, f)
        
        item = {
            "item_id": "rq_item_001",
            "target_artifact_ref": "artifacts/test.json",
            "impact_classification": "mechanical",
            "regeneration_mode": "auto",
            "status": "pending",
            "delta_preview": "Version bump",
            "pm_note": "",
            "execution_log": []
        }
        
        result = process_regeneration_item(item, workspace_dir, action="approve", generated_at="2026-05-06T12:00:00Z")
        
        assert result["status"] == "auto_executed"
        assert len(result["execution_log"]) == 1
        
        # Verify artifact was updated
        with artifact_path.open("r") as f:
            updated = json.load(f)
        assert updated["version"] == 2

    def test_process_regeneration_item_reject(self, tmp_path):
        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir()
        
        item = {
            "item_id": "rq_item_001",
            "target_artifact_ref": "artifacts/test.json",
            "impact_classification": "content_deep",
            "regeneration_mode": "pm_review",
            "status": "pending",
            "delta_preview": "Strategy change",
            "pm_note": "",
            "execution_log": []
        }
        
        result = process_regeneration_item(item, workspace_dir, action="reject", pm_note="Too risky")
        
        assert result["status"] == "rejected"
        assert "Too risky" in result["execution_log"][0]

    def test_detect_circular_dependencies_none(self, tmp_path):
        deps = ["a.json", "b.json", "c.json"]
        result = detect_circular_dependencies(deps, tmp_path)
        assert result is None

    def test_detect_circular_dependencies_found(self, tmp_path):
        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir()
        artifacts_dir = workspace_dir / "artifacts"
        artifacts_dir.mkdir()
        
        # Create artifacts with circular dependencies
        a = {"schema_version": "1.0.0", "dependencies": ["artifacts/b.json"]}
        b = {"schema_version": "1.0.0", "dependencies": ["artifacts/c.json"]}
        c = {"schema_version": "1.0.0", "dependencies": ["artifacts/a.json"]}
        
        for name, data in [("a.json", a), ("b.json", b), ("c.json", c)]:
            with (artifacts_dir / name).open("w") as f:
                json.dump(data, f)
        
        deps = ["artifacts/a.json", "artifacts/b.json", "artifacts/c.json"]
        result = detect_circular_dependencies(deps, workspace_dir)
        
        assert result is not None
        assert len(result) >= 2


class TestMarkdownRenderer:
    """Test the living document markdown renderer."""

    def test_preserve_annotations(self):
        existing = "# Title\n\nContent\n\n<!-- PM NOTE: Remember to update pricing before launch -->"
        new_md = "# Title\n\nUpdated content"
        
        result = preserve_annotations(existing, new_md)
        assert "Remember to update pricing before launch" in result

    def test_preserve_annotations_no_annotations(self):
        existing = "# Title\n\nContent"
        new_md = "# Title\n\nUpdated content"
        
        result = preserve_annotations(existing, new_md)
        assert result == new_md

    def test_resolve_source_artifacts(self, tmp_path):
        workspace_dir = tmp_path / "workspace"
        artifacts_dir = workspace_dir / "artifacts"
        artifacts_dir.mkdir(parents=True)
        
        artifact = {"schema_version": "1.0.0", "title": "Test PRD"}
        with (artifacts_dir / "prd.json").open("w") as f:
            json.dump(artifact, f)
        
        sources = resolve_source_artifacts(["artifacts/prd.json"], workspace_dir)
        
        assert "artifacts/prd.json" in sources
        assert sources["artifacts/prd.json"]["title"] == "Test PRD"

    def test_resolve_source_artifacts_missing(self, tmp_path):
        workspace_dir = tmp_path / "workspace"
        
        sources = resolve_source_artifacts(["artifacts/missing.json"], workspace_dir)
        
        assert "artifacts/missing.json" in sources
        assert sources["artifacts/missing.json"] is None


class TestExportPipeline:
    """Test the export pipeline."""

    def test_export_agent_brief(self, tmp_path):
        workspace_dir = tmp_path / "workspace"
        artifacts_dir = workspace_dir / "artifacts"
        artifacts_dir.mkdir(parents=True)
        
        artifact = {
            "schema_version": "1.0.0",
            "title": "Test PRD",
            "artifact_id": "prd_001",
            "problem_statement": "Users need faster checkout",
            "out_of_scope": ["iOS app", "Enterprise SSO", "Real-time collaboration"],
            "acceptance_criteria": ["Checkout completes in <3s", "Mobile responsive"]
        }
        with (artifacts_dir / "prd.json").open("w") as f:
            json.dump(artifact, f)
        
        result = export_artifact("artifacts/prd.json", "agent_brief", workspace_dir, generated_at="2026-05-06T12:00:00Z")
        
        assert result["format"] == "agent_brief"
        assert "EXPLICIT OUT_OF_SCOPE" in result["content"]
        assert "iOS app" in result["content"]
        assert result["boundaries_strong"] is True

    def test_export_stakeholder_update(self, tmp_path):
        workspace_dir = tmp_path / "workspace"
        artifacts_dir = workspace_dir / "artifacts"
        artifacts_dir.mkdir(parents=True)
        
        artifact = {
            "schema_version": "1.0.0",
            "title": "Strategy Update",
            "artifact_id": "strat_001",
            "summary": "We are pivoting to enterprise",
            "decisions": ["Focus on B2B"],
            "risks": ["Longer sales cycle"],
            "next_steps": ["Update pricing page"]
        }
        with (artifacts_dir / "strategy.json").open("w") as f:
            json.dump(artifact, f)
        
        result = export_artifact("artifacts/strategy.json", "stakeholder_update", workspace_dir, generated_at="2026-05-06T12:00:00Z")
        
        assert result["format"] == "stakeholder_update"
        assert "pivoting to enterprise" in result["executive_summary"]

    def test_export_unsupported_format(self, tmp_path):
        workspace_dir = tmp_path / "workspace"
        artifacts_dir = workspace_dir / "artifacts"
        artifacts_dir.mkdir(parents=True)
        
        artifact = {"schema_version": "1.0.0", "title": "Test"}
        with (artifacts_dir / "test.json").open("w") as f:
            json.dump(artifact, f)
        
        with pytest.raises(ValueError) as exc_info:
            export_artifact("artifacts/test.json", "invalid_format", workspace_dir)
        
        assert "Unsupported export format" in str(exc_info.value)
        assert "markdown" in str(exc_info.value)


class TestSchemas:
    """Test V11 schema conformance."""

    def test_regeneration_queue_schema(self):
        from jsonschema import Draft202012Validator
        
        schema_path = Path("core/schemas/artifacts/regeneration_queue.schema.json")
        assert schema_path.exists()
        
        with schema_path.open() as f:
            schema = json.load(f)
        
        validator = Draft202012Validator(schema)
        
        valid_queue = {
            "schema_version": "1.0.0",
            "regeneration_queue_id": "rq_test_001",
            "workspace_id": "ws_test",
            "trigger_event": {
                "event_type": "artifact_updated",
                "source_artifact_ref": "artifacts/prd.json",
                "change_summary": "Scope boundary tightened"
            },
            "queued_items": [
                {
                    "item_id": "rq_item_001",
                    "target_artifact_ref": "artifacts/prototype_plan.json",
                    "impact_classification": "content_deep",
                    "regeneration_mode": "pm_review",
                    "status": "pending",
                    "delta_preview": "Prototype plan needs 2 new screens",
                    "pm_note": "",
                    "execution_log": []
                }
            ],
            "dependency_sequence": ["artifacts/prototype_plan.json"],
            "status": "active",
            "pm_review_required": True,
            "auto_executed_count": 0,
            "pm_review_count": 1,
            "generated_at": "2026-05-06T12:00:00Z"
        }
        
        errors = list(validator.iter_errors(valid_queue))
        assert len(errors) == 0, f"Schema validation failed: {[e.message for e in errors]}"

    def test_pm_note_delta_proposal_schema(self):
        from jsonschema import Draft202012Validator
        
        schema_path = Path("core/schemas/artifacts/pm_note_delta_proposal.schema.json")
        assert schema_path.exists()
        
        with schema_path.open() as f:
            schema = json.load(f)
        
        validator = Draft202012Validator(schema)
        
        valid_proposal = {
            "schema_version": "1.0.0",
            "pm_note_delta_proposal_id": "pndp_001",
            "workspace_id": "ws_test",
            "source_note": {
                "note_path": "inbox/raw-notes/customer-call.txt",
                "note_type": "transcript",
                "summary": "Customer mentioned CompetitorAlpha's new AI feature"
            },
            "proposed_deltas": [
                {
                    "delta_id": "pd_001",
                    "target_artifact_ref": "artifacts/competitor_dossier.json",
                    "proposed_change": "Add CompetitorAlpha AI feature launch",
                    "confidence": "high",
                    "evidence_quote": "CompetitorAlpha just launched an AI PRD generator",
                    "regeneration_queue_item_id": "rq_item_001"
                }
            ],
            "generated_at": "2026-05-06T12:00:00Z"
        }
        
        errors = list(validator.iter_errors(valid_proposal))
        assert len(errors) == 0, f"Schema validation failed: {[e.message for e in errors]}"
