import json
from pathlib import Path

import pytest

from core.python.productos_runtime.release import promote_release_from_ralph


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def test_promote_release_from_ralph_updates_current_release_surfaces(tmp_path: Path):
    root = tmp_path / "repo"
    (root / "registry" / "releases").mkdir(parents=True)
    (root / "registry" / "workspaces").mkdir(parents=True)
    (root / "registry" / "suites").mkdir(parents=True)
    (root / "internal" / "ProductOS-Next" / "docs" / "product").mkdir(parents=True)

    (root / "README.md").write_text(
        "# ProductOS\n\n"
        "ProductOS V4.1.0 is the current stable ProductOS Core line.\n\n"
        "ProductOS V4.1.0 is organized around the PM lifecycle plus governed research and improvement loops:\n\n"
        "- latest stable release assets remain present\n",
        encoding="utf-8",
    )
    (root / "internal" / "ProductOS-Next" / "docs" / "product" / "product-overview.md").write_text(
        "The current stable line is ProductOS `V4.1.0`.\n",
        encoding="utf-8",
    )

    _write_json(
        root / "registry" / "releases" / "release_4_1_0.json",
        {
            "schema_version": "1.0.0",
            "release_id": "release_4_1_0",
            "core_version": "4.1.0",
            "released_at": "2026-03-21T22:45:00Z",
            "release_type": "major",
            "change_classification": "major_product_change",
            "customer_visible": True,
            "classification_rationale": "Existing stable release.",
            "summary": "Existing stable release.",
            "breaking_changes": [],
            "upgrade_actions": ["Keep using the stable release."],
        },
    )
    _write_json(
        root / "registry" / "workspaces" / "ws_productos_v2.registration.json",
        {
            "schema_version": "1.0.0",
            "registration_id": "ws_reg_productos_v2",
            "workspace_id": "ws_productos_v2",
            "workspace_name": "ProductOS Self-Hosting Workspace",
            "current_core_version": "4.1.0",
            "upgrade_history": [
                {
                    "core_version": "4.1.0",
                    "adopted_at": "2026-03-21T22:45:00Z",
                    "approved_by": "ProductOS PM",
                    "change_note": "Previous release.",
                }
            ],
            "registered_at": "2026-03-21T00:00:00Z",
        },
    )
    _write_json(
        root / "registry" / "suites" / "suite_productos.registration.json",
        {
            "schema_version": "1.0.0",
            "registration_id": "suite_reg_productos",
            "suite_id": "suite_productos",
            "suite_name": "ProductOS Portfolio Suite",
            "current_core_version": "4.1.0",
            "workspace_ids": ["ws_productos_v2"],
            "upgrade_history": [
                {
                    "core_version": "4.1.0",
                    "adopted_at": "2026-03-21T22:45:00Z",
                    "approved_by": "ProductOS PM",
                    "change_note": "Previous release.",
                }
            ],
            "registered_at": "2026-03-21T00:00:00Z",
        },
    )
    _write_json(
        root / "internal" / "ProductOS-Next" / "artifacts" / "ralph_loop_state_live_docs.example.json",
        {
            "schema_version": "1.0.0",
            "ralph_loop_state_id": "ralph_loop_state_ws_productos_v2_v4_2_live_docs",
            "workspace_id": "ws_productos_v2",
            "target_release": "v4_2_0",
            "loop_goal": "Inspect, review, implement, validate, fix, and revalidate the live-doc and messaging slice before next-version promotion.",
            "overall_status": "ready_for_release",
            "subject_refs": ["document_sync_state_ws_productos_v2_v4_2_live_docs"],
            "stages": [
                {"stage_key": "inspect", "status": "passed"},
                {"stage_key": "review", "status": "passed"},
                {"stage_key": "implement", "status": "passed"},
                {"stage_key": "validate", "status": "passed"},
                {"stage_key": "fix", "status": "passed"},
                {"stage_key": "revalidate", "status": "passed"},
            ],
            "validation_report_refs": ["validation_lane_report_ws_productos_v2_live_docs"],
            "manual_review_summary": "Ready to promote.",
            "next_action": "Promote ProductOS to V4.2.0 stable.",
            "generated_at": "2026-03-22T10:00:00Z",
        },
    )

    result = promote_release_from_ralph(
        root,
        root / "internal" / "ProductOS-Next" / "artifacts" / "ralph_loop_state_live_docs.example.json",
        released_at="2026-03-21T10:10:00Z",
    )

    assert result["target_version"] == "4.2.0"
    assert (root / "registry" / "releases" / "release_4_2_0.json").exists()

    workspace = json.loads((root / "registry" / "workspaces" / "ws_productos_v2.registration.json").read_text(encoding="utf-8"))
    suite = json.loads((root / "registry" / "suites" / "suite_productos.registration.json").read_text(encoding="utf-8"))
    readme = (root / "README.md").read_text(encoding="utf-8")
    overview = (root / "internal" / "ProductOS-Next" / "docs" / "product" / "product-overview.md").read_text(encoding="utf-8")

    assert workspace["current_core_version"] == "4.2.0"
    assert suite["current_core_version"] == "4.2.0"
    assert workspace["upgrade_history"][-1]["core_version"] == "4.2.0"
    assert suite["upgrade_history"][-1]["core_version"] == "4.2.0"
    assert workspace["upgrade_history"][-1]["adopted_at"] == "2026-03-21T22:45:01Z"
    assert suite["upgrade_history"][-1]["adopted_at"] == "2026-03-21T22:45:01Z"
    assert "ProductOS V4.2.0 is the current stable ProductOS Core line." in readme
    assert "ProductOS V4.2.0 is the current stable ProductOS Core line." in readme
    assert "latest stable release assets remain present" in readme
    assert "ProductOS `V4.2.0`" in overview

    promote_release_from_ralph(
        root,
        root / "internal" / "ProductOS-Next" / "artifacts" / "ralph_loop_state_live_docs.example.json",
        released_at="2026-03-21T10:10:00Z",
    )
    workspace_after_second_run = json.loads(
        (root / "registry" / "workspaces" / "ws_productos_v2.registration.json").read_text(encoding="utf-8")
    )
    assert len(workspace_after_second_run["upgrade_history"]) == 2


def test_promote_release_from_ralph_blocks_watch_level_promotion_gate(tmp_path: Path):
    root = tmp_path / "repo"
    (root / "registry" / "releases").mkdir(parents=True)
    (root / "internal" / "ProductOS-Next" / "artifacts").mkdir(parents=True)

    _write_json(
        root / "registry" / "releases" / "release_4_7_0.json",
        {
            "schema_version": "1.0.0",
            "release_id": "release_4_7_0",
            "core_version": "4.7.0",
            "released_at": "2026-03-21T22:45:00Z",
            "release_type": "minor",
            "change_classification": "feature_enhancement",
            "customer_visible": True,
            "classification_rationale": "Existing stable release.",
            "summary": "Existing stable release.",
            "breaking_changes": [],
            "upgrade_actions": ["Keep using the stable release."],
        },
    )
    _write_json(
        root / "internal" / "ProductOS-Next" / "artifacts" / "ralph_loop_state_next_version_completion.example.json",
        {
            "schema_version": "1.0.0",
            "ralph_loop_state_id": "ralph_loop_state_ws_productos_v2_v4_8_foundation",
            "workspace_id": "ws_productos_v2",
            "target_release": "v4_8_0",
            "loop_goal": "Inspect, review, implement, validate, fix, and revalidate the truthful control-surface slice before stable release promotion.",
            "overall_status": "ready_for_release",
            "subject_refs": ["feature_portfolio_review_ws_productos_v2_next_version_baseline"],
            "stages": [
                {"stage_key": "inspect", "status": "passed"},
                {"stage_key": "review", "status": "passed"},
                {"stage_key": "implement", "status": "passed"},
                {"stage_key": "validate", "status": "passed"},
                {"stage_key": "fix", "status": "passed"},
                {"stage_key": "revalidate", "status": "passed"},
            ],
            "validation_report_refs": ["validation_lane_report_ws_productos_v2_next_version_completion"],
            "manual_review_summary": "Loop is structurally complete but still watch-level.",
            "next_action": "Keep hardening before stable promotion.",
            "generated_at": "2026-03-26T08:00:00Z",
        },
    )
    _write_json(
        root / "internal" / "ProductOS-Next" / "artifacts" / "eval_run_report.json",
        {
            "schema_version": "1.0.0",
            "eval_run_report_id": "eval_run_report_ws_productos_v2_v4_8",
            "workspace_id": "ws_productos_v2",
            "eval_suite_manifest_id": "eval_suite_manifest_ws_productos_v2_v4_8",
            "baseline_version": "4.7.0",
            "candidate_version": "4.8.0",
            "status": "warning",
            "run_scope": "Foundation-only V4.8 validation run.",
            "summary": "Still blocked by regressions.",
            "total_cases": 3,
            "passed_cases": 1,
            "warning_cases": 1,
            "failed_cases": 1,
            "regression_count": 2,
            "truthfulness_status": "watch",
            "case_results": [],
            "recommended_next_action": "Keep candidate in watch mode.",
            "generated_at": "2026-03-26T08:00:00Z",
        },
    )
    _write_json(
        root / "internal" / "ProductOS-Next" / "artifacts" / "feature_portfolio_review.json",
        {
            "schema_version": "1.0.0",
            "feature_portfolio_review_id": "feature_portfolio_review_ws_productos_v2_next_version_baseline",
            "workspace_id": "ws_productos_v2",
            "review_scope": "V4.8 foundation review.",
            "benchmark_ref": "pm_superpower_benchmark_ws_productos_v2_v4_0",
            "adapter_registry_ref": "runtime_adapter_registry_ws_productos_v2_next_version",
            "truthfulness_status": "watch",
            "eval_run_ref": "eval_run_report_ws_productos_v2_v4_8",
            "scorecard_refs": [],
            "feature_summaries": [],
            "top_priority_feature_id": "runtime_control_surface",
            "promoted_feature_ids": [],
            "internal_use_feature_ids": [],
            "active_improvement_feature_ids": ["runtime_control_surface", "self_improvement_loop"],
            "blocked_feature_ids": [],
            "highlighted_risks": [],
            "next_action": "Keep hardening.",
            "generated_at": "2026-03-26T08:00:00Z",
        },
    )

    with pytest.raises(ValueError, match="Promotion gate is blocked"):
        promote_release_from_ralph(
            root,
            root / "internal" / "ProductOS-Next" / "artifacts" / "ralph_loop_state_next_version_completion.example.json",
            released_at="2026-03-26T08:10:00Z",
            eval_run_report_path=root / "internal" / "ProductOS-Next" / "artifacts" / "eval_run_report.json",
            feature_portfolio_review_path=root / "internal" / "ProductOS-Next" / "artifacts" / "feature_portfolio_review.json",
        )
