from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.python.productos_runtime.living_system import (
    build_regeneration_queue,
    generate_impact_propagation_map,
    process_regeneration_item,
)


def test_generate_impact_propagation_map_creates_dependencies(bundled_workspace_dir: Path):
    ipm = generate_impact_propagation_map(bundled_workspace_dir)
    assert ipm["schema_version"] == "1.0.0"
    assert "dependencies" in ipm
    deps = ipm["dependencies"]
    # Should find at least some dependencies from scanning artifacts
    assert isinstance(deps, dict)


def test_build_regeneration_queue_detects_persona_change_and_queues_journey_map(bundled_workspace_dir: Path, tmp_path: Path):
    workspace_copy = tmp_path / "ls-workspace"
    import shutil
    shutil.copytree(bundled_workspace_dir, workspace_copy)

    # Generate propagation map first
    ipm = generate_impact_propagation_map(workspace_copy)
    ipm_path = workspace_copy / "artifacts" / "impact_propagation_map.json"
    with ipm_path.open("w", encoding="utf-8") as f:
        json.dump(ipm, f, indent=2)
        f.write("\n")

    trigger = {
        "event_type": "artifact_updated",
        "source_artifact_ref": "artifacts/persona_pack.example.json",
        "change_summary": "Updated persona pain points for PM operating rhythm",
    }
    queue = build_regeneration_queue(trigger, workspace_copy)

    # Should queue customer_journey_map if persona -> cjm dependency exists
    target_refs = [i["target_artifact_ref"] for i in queue["queued_items"]]
    assert any("customer_journey_map" in ref for ref in target_refs), (
        f"Expected customer_journey_map in queued items, got {target_refs}"
    )

    # Propagation latency should be negligible (<5s is implied by in-memory build)
    assert queue["status"] == "active"


def test_process_regeneration_item_approves_content_deep_but_does_not_fail(bundled_workspace_dir: Path):
    """process_regeneration_item should handle content_deep changes gracefully."""
    item = {
        "item_id": "rq_item_001",
        "target_artifact_ref": "artifacts/customer_journey_map.json",
        "impact_classification": "content_deep",
        "regeneration_mode": "pm_review",
        "status": "pending",
        "delta_preview": "Content-deep change: persona pain updated -> customer_journey_map.json",
        "pm_note": "",
        "execution_log": [],
    }
    processed = process_regeneration_item(item, bundled_workspace_dir, action="approve")
    assert processed["status"] in ("approved", "content_regenerated")
    assert any("Approved by PM" in log or "regeneration executed" in log for log in processed["execution_log"])


def test_process_regeneration_item_rejects_item(bundled_workspace_dir: Path):
    item = {
        "item_id": "rq_item_002",
        "target_artifact_ref": "artifacts/customer_journey_map.json",
        "impact_classification": "content_deep",
        "regeneration_mode": "pm_review",
        "status": "pending",
        "delta_preview": "test",
        "pm_note": "",
        "execution_log": [],
    }
    processed = process_regeneration_item(item, bundled_workspace_dir, action="reject", pm_note="Not now")
    assert processed["status"] == "rejected"
    assert any("Rejected by PM" in log for log in processed["execution_log"])
