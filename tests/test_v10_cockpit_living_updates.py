"""Tests for ProductOS V11 Cockpit Living Updates (PM Delta Review Lane)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from jsonschema import Draft202012Validator

from core.python.productos_runtime.living_system import (
    build_regeneration_queue,
    process_regeneration_item,
)


class TestCockpitLivingUpdatesSchema:
    """Test that cockpit_state.schema.json supports living_updates_queue."""

    def test_living_update_item_validates(self, root_dir: Path):
        schema_path = root_dir / "core" / "schemas" / "artifacts" / "cockpit_state.schema.json"
        assert schema_path.exists()

        with schema_path.open() as f:
            schema = json.load(f)

        item_schema = schema["$defs"]["livingUpdateItem"]
        validator = Draft202012Validator(item_schema)

        valid_item = {
            "update_id": "lu_001",
            "regeneration_queue_item_ref": "rq_item_001",
            "source_change": "Competitor dossier updated",
            "target_artifact": "artifacts/strategy_context_brief.json",
            "delta_summary": "3 claims outdated: pricing advantage, feature parity, segment targeting",
            "impact_classification": "content_deep",
            "pm_action": "pending",
            "pm_note": "",
            "reviewed_at": "2026-05-06T12:00:00Z",
        }

        errors = list(validator.iter_errors(valid_item))
        assert len(errors) == 0, f"Schema validation failed: {[e.message for e in errors]}"

    def test_living_update_item_missing_required_fails(self, root_dir: Path):
        schema_path = root_dir / "core" / "schemas" / "artifacts" / "cockpit_state.schema.json"
        with schema_path.open() as f:
            schema = json.load(f)

        item_schema = schema["$defs"]["livingUpdateItem"]
        validator = Draft202012Validator(item_schema)

        invalid_item = {
            "update_id": "lu_001",
            "source_change": "Competitor dossier updated",
            "target_artifact": "artifacts/strategy_context_brief.json",
            "delta_summary": "3 claims outdated",
            "impact_classification": "content_deep",
            "pm_action": "pending",
        }

        errors = list(validator.iter_errors(invalid_item))
        assert len(errors) > 0, "Expected validation to fail for missing required field"

    def test_living_update_invalid_classification_fails(self, root_dir: Path):
        schema_path = root_dir / "core" / "schemas" / "artifacts" / "cockpit_state.schema.json"
        with schema_path.open() as f:
            schema = json.load(f)

        item_schema = schema["$defs"]["livingUpdateItem"]
        validator = Draft202012Validator(item_schema)

        invalid_item = {
            "update_id": "lu_002",
            "regeneration_queue_item_ref": "rq_item_002",
            "source_change": "Persona updated",
            "target_artifact": "artifacts/persona.json",
            "delta_summary": "Pain point changed",
            "impact_classification": "invalid_classification",
            "pm_action": "pending",
        }

        errors = list(validator.iter_errors(invalid_item))
        assert len(errors) > 0, "Expected validation to fail for invalid impact_classification"


class TestReviewDeltaCLI:
    """Test the review-delta CLI command behavior."""

    def test_review_delta_approve(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        cockpit_dir = workspace_dir / "outputs" / "cockpit"
        cockpit_dir.mkdir(parents=True)

        cockpit = {
            "cockpit_state": {
                "living_updates_queue": [
                    {
                        "update_id": "lu_001",
                        "regeneration_queue_item_ref": "rq_item_001",
                        "source_change": "Competitor dossier updated",
                        "target_artifact": "artifacts/strategy_context_brief.json",
                        "delta_summary": "3 claims outdated",
                        "impact_classification": "content_deep",
                        "pm_action": "pending",
                        "pm_note": "",
                    }
                ]
            }
        }

        with (cockpit_dir / "cockpit_bundle.json").open("w") as f:
            json.dump(cockpit, f)

        update = next((u for u in cockpit["cockpit_state"]["living_updates_queue"] if u["update_id"] == "lu_001"), None)
        assert update is not None
        update["pm_action"] = "approve"
        update["reviewed_at"] = "2026-05-06T12:00:00Z"

        assert update["pm_action"] == "approve"
        assert update["reviewed_at"] == "2026-05-06T12:00:00Z"

    def test_review_delta_reject_blocks_propagation(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        cockpit_dir = workspace_dir / "outputs" / "cockpit"
        cockpit_dir.mkdir(parents=True)

        cockpit = {
            "cockpit_state": {
                "living_updates_queue": [
                    {
                        "update_id": "lu_002",
                        "regeneration_queue_item_ref": "rq_item_002",
                        "source_change": "PRD scope tightened",
                        "target_artifact": "artifacts/prototype_plan.json",
                        "delta_summary": "2 new screens required",
                        "impact_classification": "content_deep",
                        "pm_action": "pending",
                        "pm_note": "",
                    }
                ]
            }
        }

        with (cockpit_dir / "cockpit_bundle.json").open("w") as f:
            json.dump(cockpit, f)

        update = next((u for u in cockpit["cockpit_state"]["living_updates_queue"] if u["update_id"] == "lu_002"), None)
        assert update is not None
        update["pm_action"] = "reject"
        update["pm_note"] = "Too risky for current sprint"
        update["reviewed_at"] = "2026-05-06T12:00:00Z"

        assert update["pm_action"] == "reject"
        assert "Too risky" in update["pm_note"]

    def test_review_delta_not_found(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        cockpit_dir = workspace_dir / "outputs" / "cockpit"
        cockpit_dir.mkdir(parents=True)

        cockpit = {"cockpit_state": {"living_updates_queue": []}}
        with (cockpit_dir / "cockpit_bundle.json").open("w") as f:
            json.dump(cockpit, f)

        update = next((u for u in cockpit["cockpit_state"]["living_updates_queue"] if u["update_id"] == "lu_missing"), None)
        assert update is None


class TestLivingSystemIntegration:
    """Test that living system produces cockpit-compatible queue items."""

    def test_build_regeneration_queue_populates_cockpit_fields(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        artifacts_dir = workspace_dir / "artifacts"
        artifacts_dir.mkdir(parents=True)

        # Create a source artifact and a downstream artifact
        source = {"schema_version": "1.0.0", "title": "Source", "version": 1}
        target = {"schema_version": "1.0.0", "title": "Target", "version": 1}

        with (artifacts_dir / "source.json").open("w") as f:
            json.dump(source, f)
        with (artifacts_dir / "target.json").open("w") as f:
            json.dump(target, f)

        # Create impact propagation map
        impact_map = {
            "schema_version": "1.0.0",
            "propagation_map_id": "ipm_test",
            "workspace_id": workspace_dir.name,
            "dependencies": {
                "artifacts/source.json": ["artifacts/target.json"],
            },
            "generated_at": "2026-05-06T12:00:00Z",
        }
        with (artifacts_dir / "impact_propagation_map.json").open("w") as f:
            json.dump(impact_map, f)

        trigger = {
            "event_type": "artifact_updated",
            "source_artifact_ref": "artifacts/source.json",
            "change_summary": "competitor pricing changed",
        }

        queue = build_regeneration_queue(trigger, workspace_dir, generated_at="2026-05-06T12:00:00Z")

        assert queue["status"] == "active"
        assert len(queue["queued_items"]) == 1

        item = queue["queued_items"][0]
        assert item["target_artifact_ref"] == "artifacts/target.json"
        assert item["impact_classification"] == "content_deep"
        assert item["regeneration_mode"] == "pm_review"
        assert "delta_preview" in item
        assert item["status"] == "pending"

    def test_process_regeneration_item_approval_flow(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        artifacts_dir = workspace_dir / "artifacts"
        artifacts_dir.mkdir(parents=True)

        target = {"schema_version": "1.0.0", "title": "Target", "version": 1}
        with (artifacts_dir / "target.json").open("w") as f:
            json.dump(target, f)

        item = {
            "item_id": "rq_item_001",
            "target_artifact_ref": "artifacts/target.json",
            "impact_classification": "content_deep",
            "regeneration_mode": "pm_review",
            "status": "pending",
            "delta_preview": "Strategy change",
            "pm_note": "",
            "execution_log": [],
        }

        result = process_regeneration_item(item, workspace_dir, action="approve", pm_note="Looks good", generated_at="2026-05-06T12:00:00Z")

        assert result["status"] == "approved"
        assert "Looks good" in result["execution_log"][0]
        assert result["executed_at"] == "2026-05-06T12:00:00Z"

    def test_process_regeneration_item_modify(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        artifacts_dir = workspace_dir / "artifacts"
        artifacts_dir.mkdir(parents=True)

        target = {"schema_version": "1.0.0", "title": "Target", "version": 1}
        with (artifacts_dir / "target.json").open("w") as f:
            json.dump(target, f)

        item = {
            "item_id": "rq_item_002",
            "target_artifact_ref": "artifacts/target.json",
            "impact_classification": "content_deep",
            "regeneration_mode": "pm_review",
            "status": "pending",
            "delta_preview": "Scope changed",
            "pm_note": "",
            "execution_log": [],
        }

        result = process_regeneration_item(item, workspace_dir, action="modify", pm_note="Adjust scope to MVP only", generated_at="2026-05-06T12:00:00Z")

        assert result["status"] == "approved"
        assert "Adjust scope" in result["execution_log"][0]
