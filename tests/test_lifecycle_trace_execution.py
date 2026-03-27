from pathlib import Path

from core.python.productos_runtime.lifecycle import (
    DISCOVERY_STAGE_ORDER,
    load_item_lifecycle_state_from_workspace,
    load_lifecycle_stage_snapshot_from_workspace,
)


def test_load_item_lifecycle_state_from_workspace(root_dir: Path):
    payload = load_item_lifecycle_state_from_workspace(
        root_dir / "workspaces" / "productos-v2",
        item_id="opp_pm_lifecycle_traceability",
    )

    assert payload["current_stage"] == "release_readiness"
    assert payload["overall_status"] == "completed"
    assert payload["item_ref"]["entity_id"] == "opp_pm_lifecycle_traceability"
    assert [stage["stage_key"] for stage in payload["lifecycle_stages"]] == [
        *DISCOVERY_STAGE_ORDER,
        "story_planning",
        "acceptance_ready",
        "release_readiness",
        "launch_preparation",
        "outcome_review",
    ]
    assert payload["lifecycle_stages"][0]["artifact_ids"] == [
        "intake_routing_state_ws_productos_v2_discovery_traceability",
    ]
    assert payload["lifecycle_stages"][-1]["status"] == "not_started"


def test_load_lifecycle_stage_snapshot_from_workspace(root_dir: Path):
    payload = load_lifecycle_stage_snapshot_from_workspace(
        root_dir / "workspaces" / "productos-v2",
        focus_area="discovery",
    )

    assert payload["focus_area"] == "discovery"
    assert payload["item_count"] == 1
    assert payload["segment_count"] == 3
    assert payload["persona_count"] == 3
    assert payload["gate_counts"]["passed"] == 7
    assert payload["active_item_ids"] == ["opp_pm_lifecycle_traceability"]
    assert payload["stage_summaries"][-1]["stage_key"] == "prd_handoff"


def test_load_delivery_and_full_lifecycle_snapshots_from_workspace(root_dir: Path):
    delivery = load_lifecycle_stage_snapshot_from_workspace(
        root_dir / "workspaces" / "productos-v2",
        focus_area="delivery",
    )
    full_lifecycle = load_lifecycle_stage_snapshot_from_workspace(
        root_dir / "workspaces" / "productos-v2",
        focus_area="full_lifecycle",
    )

    assert delivery["focus_area"] == "delivery"
    assert delivery["gate_counts"]["passed"] == 3
    assert delivery["stage_summaries"][0]["stage_key"] == "story_planning"
    assert full_lifecycle["focus_area"] == "full_lifecycle"
    assert full_lifecycle["gate_counts"]["passed"] == 10
    assert full_lifecycle["stage_summaries"][-1]["stage_key"] == "outcome_review"
