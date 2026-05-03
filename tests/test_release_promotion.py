import json
import subprocess
from pathlib import Path

import pytest

from core.python.productos_runtime.release import (
    promote_public_release,
    promote_release_from_ralph,
    run_public_release,
    verify_public_release_alignment,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _run_git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr or completed.stdout
    return completed.stdout.strip()


def _seed_public_release_repo(root: Path, *, version: str = "7.2.0") -> None:
    (root / "registry" / "releases").mkdir(parents=True)
    (root / "registry" / "workspaces").mkdir(parents=True)
    (root / "registry" / "suites").mkdir(parents=True)
    (root / "internal" / "ProductOS-Next" / "docs" / "product").mkdir(parents=True)
    (root / "docs").mkdir(parents=True)

    (root / ".gitignore").write_text(
        ".DS_Store\n.pytest_cache/\n__pycache__/\ninternal/*\n!internal/README.md\nworkspaces/*\n!workspaces/.gitkeep\n",
        encoding="utf-8",
    )
    (root / "README.md").write_text(
        "# ProductOS\n\n"
        f"ProductOS V{version} is the current stable ProductOS Core line.\n\n"
        f"ProductOS V{version} is organized around the PM lifecycle plus governed research and improvement loops:\n\n"
        "- latest stable release assets remain present\n",
        encoding="utf-8",
    )
    (root / "docs" / "public-note.md").write_text("Tracked public release note.\n", encoding="utf-8")
    (root / "internal" / "ProductOS-Next" / "docs" / "product" / "product-overview.md").write_text(
        f"The current stable line is ProductOS `V{version}`.\n",
        encoding="utf-8",
    )
    _write_json(
        root / "registry" / "releases" / f"release_{version.replace('.', '_')}.json",
        {
            "schema_version": "1.0.0",
            "release_id": f"release_{version.replace('.', '_')}",
            "core_version": version,
            "released_at": "2026-04-09T12:10:00Z",
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
        root / "registry" / "workspaces" / "ws_productos_v2.registration.json",
        {
            "schema_version": "1.0.0",
            "registration_id": "ws_reg_productos_v2",
            "workspace_id": "ws_productos_v2",
            "workspace_name": "ProductOS Self-Hosting Workspace",
            "current_core_version": version,
            "upgrade_history": [
                {
                    "core_version": version,
                    "adopted_at": "2026-04-09T12:10:00Z",
                    "approved_by": "ProductOS PM",
                    "change_note": "Previous stable release.",
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
            "current_core_version": version,
            "workspace_ids": ["ws_productos_v2"],
            "upgrade_history": [
                {
                    "core_version": version,
                    "adopted_at": "2026-04-09T12:10:00Z",
                    "approved_by": "ProductOS PM",
                    "change_note": "Previous stable release.",
                }
            ],
            "registered_at": "2026-03-19T18:30:00Z",
        },
    )


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


def test_promote_public_release_updates_only_tracked_public_surfaces(tmp_path: Path):
    root = tmp_path / "repo"
    _seed_public_release_repo(root)

    result = promote_public_release(
        root,
        slice_label="public release operator slice",
        released_at="2026-04-09T12:20:00Z",
    )

    release = json.loads((root / "registry" / "releases" / "release_7_3_0.json").read_text(encoding="utf-8"))
    workspace = json.loads((root / "registry" / "workspaces" / "ws_productos_v2.registration.json").read_text(encoding="utf-8"))
    suite = json.loads((root / "registry" / "suites" / "suite_productos.registration.json").read_text(encoding="utf-8"))
    readme = (root / "README.md").read_text(encoding="utf-8")
    overview = (root / "internal" / "ProductOS-Next" / "docs" / "product" / "product-overview.md").read_text(encoding="utf-8")

    assert result["target_version"] == "7.3.0"
    assert result["tag_name"] == "v7.3.0"
    assert release["core_version"] == "7.3.0"
    assert "public release operator slice" in release["summary"]
    assert workspace["current_core_version"] == "7.3.0"
    assert suite["current_core_version"] == "7.3.0"
    assert "ProductOS V7.3.0 is the current stable ProductOS Core line." in readme
    assert "ProductOS `V7.2.0`" in overview


def test_promote_public_release_can_promote_to_v9_after_manual_gate_clear(tmp_path: Path):
    root = tmp_path / "repo"
    _seed_public_release_repo(root, version="8.4.0")

    result = promote_public_release(
        root,
        slice_label="lifecycle enrichment program",
        released_at="2026-05-03T12:00:00Z",
        target_version="9.0.0",
    )

    release = json.loads((root / "registry" / "releases" / "release_9_0_0.json").read_text(encoding="utf-8"))
    workspace = json.loads((root / "registry" / "workspaces" / "ws_productos_v2.registration.json").read_text(encoding="utf-8"))
    suite = json.loads((root / "registry" / "suites" / "suite_productos.registration.json").read_text(encoding="utf-8"))
    readme = (root / "README.md").read_text(encoding="utf-8")

    assert result["target_version"] == "9.0.0"
    assert release["core_version"] == "9.0.0"
    assert workspace["current_core_version"] == "9.0.0"
    assert suite["current_core_version"] == "9.0.0"
    assert "ProductOS V9.0.0 is the current stable ProductOS Core line." in readme


def test_run_public_release_commits_tags_and_blocks_ignored_boundaries(tmp_path: Path):
    root = tmp_path / "repo"
    _seed_public_release_repo(root)
    _run_git(root, "init")
    _run_git(root, "config", "user.name", "ProductOS Test")
    _run_git(root, "config", "user.email", "test@example.com")
    _run_git(root, "add", ".")
    _run_git(root, "commit", "-m", "Initial state")

    (root / "docs" / "queued-feature.md").write_text("Release the queued public feature.\n", encoding="utf-8")
    (root / "internal" / "ProductOS-Next" / "artifacts").mkdir(parents=True, exist_ok=True)
    (root / "internal" / "ProductOS-Next" / "artifacts" / "ignored-proof.json").write_text(
        "{\"status\": \"local-only\"}\n",
        encoding="utf-8",
    )

    result = run_public_release(
        root,
        slice_label="public release operator slice",
        released_at="2026-04-09T12:20:00Z",
        push=False,
    )

    committed_paths = set(filter(None, _run_git(root, "show", "--name-only", "--format=", "HEAD").splitlines()))
    assert result["target_version"] == "7.3.0"
    assert _run_git(root, "describe", "--tags", "--exact-match") == "v7.3.0"
    assert "docs/queued-feature.md" in committed_paths
    assert "registry/releases/release_7_3_0.json" in committed_paths
    assert all(not path.startswith("internal/") for path in committed_paths)
    assert verify_public_release_alignment(root, target_version="7.3.0", tag_name="v7.3.0")["status"] == "aligned"


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


def test_promote_release_from_ralph_blocks_unresolved_external_research_review(tmp_path: Path):
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
            "manual_review_summary": "Loop is structurally complete but research evidence is still conflicted.",
            "next_action": "Resolve the external research review blockers before promotion.",
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
            "status": "passed",
            "run_scope": "Foundation-only V4.8 validation run.",
            "summary": "Promotion candidate passes the frozen eval suite.",
            "total_cases": 3,
            "passed_cases": 3,
            "warning_cases": 0,
            "failed_cases": 0,
            "regression_count": 0,
            "truthfulness_status": "healthy",
            "case_results": [],
            "recommended_next_action": "Proceed if all release gates are clear.",
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
            "truthfulness_status": "healthy",
            "eval_run_ref": "eval_run_report_ws_productos_v2_v4_8",
            "scorecard_refs": [],
            "feature_summaries": [
                {
                    "feature_id": "market_intelligence",
                    "feature_name": "Governed research and market refresh",
                    "loop_id": "signal_to_product_decision",
                    "overall_score": 5,
                    "adoption_recommendation": "promote_as_standard",
                    "gap_summary": "Promotion would be ready if the external research review were clear.",
                    "provenance_classification": "real",
                    "next_action": "Resolve the external research review blockers.",
                }
            ],
            "top_priority_feature_id": "market_intelligence",
            "promoted_feature_ids": ["market_intelligence"],
            "internal_use_feature_ids": [],
            "active_improvement_feature_ids": [],
            "blocked_feature_ids": [],
            "highlighted_risks": [],
            "next_action": "Proceed if all release gates are clear.",
            "generated_at": "2026-03-26T08:00:00Z",
        },
    )
    _write_json(
        root / "internal" / "ProductOS-Next" / "artifacts" / "external_research_review.json",
        {
            "schema_version": "1.0.0",
            "external_research_review_id": "external_research_review_ws_productos_v2",
            "workspace_id": "ws_productos_v2",
            "review_status": "review_required",
            "accepted_source_ids": ["src_proof", "src_competitor"],
            "contradiction_items": [
                {
                    "contradiction_id": "external_contradiction_proof_posture",
                    "topic": "proof_posture",
                    "severity": "moderate",
                    "statement": "External sources disagree on whether buyers already require measurable governance proof.",
                    "question_ids": ["research_q_adoption_workspace_outcomes_proof"],
                    "source_ids": ["src_proof", "src_competitor"],
                }
            ],
            "review_items": [
                "External sources disagree on whether buyers already require measurable governance proof."
            ],
            "recommendation": "pm_review_required",
            "created_at": "2026-03-26T08:00:00Z",
        },
    )

    with pytest.raises(ValueError, match="external research"):
        promote_release_from_ralph(
            root,
            root / "internal" / "ProductOS-Next" / "artifacts" / "ralph_loop_state_next_version_completion.example.json",
            released_at="2026-03-26T08:10:00Z",
            eval_run_report_path=root / "internal" / "ProductOS-Next" / "artifacts" / "eval_run_report.json",
            feature_portfolio_review_path=root / "internal" / "ProductOS-Next" / "artifacts" / "feature_portfolio_review.json",
            external_research_review_path=root / "internal" / "ProductOS-Next" / "artifacts" / "external_research_review.json",
        )


def test_promote_release_from_ralph_blocks_planned_research_without_discovery(tmp_path: Path):
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
            "manual_review_summary": "Loop is structurally complete but the research loop has not been completed.",
            "next_action": "Persist discovery and selected research sources before promotion.",
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
            "status": "passed",
            "run_scope": "Foundation-only V4.8 validation run.",
            "summary": "Promotion candidate passes the frozen eval suite.",
            "total_cases": 3,
            "passed_cases": 3,
            "warning_cases": 0,
            "failed_cases": 0,
            "regression_count": 0,
            "truthfulness_status": "healthy",
            "case_results": [],
            "recommended_next_action": "Proceed if all release gates are clear.",
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
            "truthfulness_status": "healthy",
            "eval_run_ref": "eval_run_report_ws_productos_v2_v4_8",
            "scorecard_refs": [],
            "feature_summaries": [
                {
                    "feature_id": "market_intelligence",
                    "feature_name": "Governed research and market refresh",
                    "loop_id": "signal_to_product_decision",
                    "overall_score": 5,
                    "adoption_recommendation": "promote_as_standard",
                    "gap_summary": "Promotion would be ready if the governed research loop were complete.",
                    "provenance_classification": "real",
                    "next_action": "Persist discovery and selected sources.",
                }
            ],
            "top_priority_feature_id": "market_intelligence",
            "promoted_feature_ids": ["market_intelligence"],
            "internal_use_feature_ids": [],
            "active_improvement_feature_ids": [],
            "blocked_feature_ids": [],
            "highlighted_risks": [],
            "next_action": "Proceed if all release gates are clear.",
            "generated_at": "2026-03-26T08:00:00Z",
        },
    )
    _write_json(
        root / "internal" / "ProductOS-Next" / "artifacts" / "research_brief.json",
        {
            "schema_version": "1.0.0",
            "research_brief_id": "research_brief_ws_productos_v2",
            "workspace_id": "ws_productos_v2",
            "title": "Research Brief: ProductOS proof posture",
            "summary": "Validate the external proof posture before promotion.",
            "target_segment_refs": [],
            "insights": [],
            "known_gaps": ["Need external validation on governance proof posture."],
            "external_research_questions": [
                {
                    "question_id": "research_q_productos_proof_posture",
                    "question": "Do buyers expect measurable governance proof before adopting ProductOS-like systems?",
                    "recommended_source_type": "market_validation",
                    "why_it_matters": "The release claim should not overstate validated proof posture.",
                }
            ],
            "created_at": "2026-03-26T08:00:00Z",
        },
    )
    _write_json(
        root / "internal" / "ProductOS-Next" / "artifacts" / "external_research_plan.json",
        {
            "schema_version": "1.0.0",
            "external_research_plan_id": "external_research_plan_ws_productos_v2",
            "workspace_id": "ws_productos_v2",
            "title": "External research plan",
            "generated_from_artifact_id": "research_brief_ws_productos_v2",
            "research_objective": "Validate the external proof posture before promotion.",
            "prioritized_questions": [
                {
                    "question_id": "research_q_productos_proof_posture",
                    "question": "Do buyers expect measurable governance proof before adopting ProductOS-like systems?",
                    "why_it_matters": "The release claim should not overstate validated proof posture.",
                    "recommended_source_type": "market_validation",
                    "priority": "high",
                    "search_queries": ["product operations governance proof measurable rollout"],
                    "source_requirements": ["Fresh operator or market validation evidence"],
                }
            ],
            "coverage_summary": {
                "known_gaps": ["Need external validation on governance proof posture."],
                "claims_needing_validation": ["Governance proof posture is customer-safe to claim."],
                "recommended_next_step": "Run source discovery and refresh research artifacts.",
            },
            "created_at": "2026-03-26T08:00:00Z",
        },
    )

    with pytest.raises(ValueError, match="source discovery has not been persisted"):
        promote_release_from_ralph(
            root,
            root / "internal" / "ProductOS-Next" / "artifacts" / "ralph_loop_state_next_version_completion.example.json",
            released_at="2026-03-26T08:10:00Z",
            eval_run_report_path=root / "internal" / "ProductOS-Next" / "artifacts" / "eval_run_report.json",
            feature_portfolio_review_path=root / "internal" / "ProductOS-Next" / "artifacts" / "feature_portfolio_review.json",
            research_brief_path=root / "internal" / "ProductOS-Next" / "artifacts" / "research_brief.json",
            external_research_plan_path=root / "internal" / "ProductOS-Next" / "artifacts" / "external_research_plan.json",
        )


def test_promote_release_from_ralph_blocks_degraded_external_research_feed_registry(tmp_path: Path):
    root = tmp_path / "repo"
    (root / "registry" / "releases").mkdir(parents=True)
    (root / "internal" / "ProductOS-Next" / "artifacts").mkdir(parents=True)
    (root / "internal" / "ProductOS-Next" / "outputs" / "research").mkdir(parents=True)

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
            "manual_review_summary": "Loop is structurally complete but governed feed health is degraded.",
            "next_action": "Repair degraded governed research feeds before promotion.",
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
            "status": "passed",
            "run_scope": "Foundation-only V4.8 validation run.",
            "summary": "Promotion candidate passes the frozen eval suite.",
            "total_cases": 3,
            "passed_cases": 3,
            "warning_cases": 0,
            "failed_cases": 0,
            "regression_count": 0,
            "truthfulness_status": "healthy",
            "case_results": [],
            "recommended_next_action": "Proceed if all release gates are clear.",
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
            "truthfulness_status": "healthy",
            "eval_run_ref": "eval_run_report_ws_productos_v2_v4_8",
            "scorecard_refs": [],
            "feature_summaries": [],
            "top_priority_feature_id": "market_intelligence",
            "promoted_feature_ids": ["market_intelligence"],
            "internal_use_feature_ids": [],
            "active_improvement_feature_ids": [],
            "blocked_feature_ids": [],
            "highlighted_risks": [],
            "next_action": "Proceed if all release gates are clear.",
            "generated_at": "2026-03-26T08:00:00Z",
        },
    )
    _write_json(
        root / "internal" / "ProductOS-Next" / "artifacts" / "research_brief.json",
        {
            "schema_version": "1.0.0",
            "research_brief_id": "research_brief_ws_productos_v2",
            "workspace_id": "ws_productos_v2",
            "title": "Research Brief",
            "summary": "Validate release posture.",
            "target_segment_refs": [],
            "insights": [],
            "known_gaps": ["Need governed market validation."],
            "external_research_questions": [
                {
                    "question_id": "research_q_productos_proof_posture",
                    "question": "Do buyers expect proof before adoption?",
                    "recommended_source_type": "market_validation",
                    "why_it_matters": "Release claims need evidence.",
                }
            ],
            "created_at": "2026-03-26T08:00:00Z",
        },
    )
    _write_json(
        root / "internal" / "ProductOS-Next" / "artifacts" / "external_research_plan.json",
        {
            "schema_version": "1.0.0",
            "external_research_plan_id": "external_research_plan_ws_productos_v2",
            "workspace_id": "ws_productos_v2",
            "prioritized_questions": [
                {
                    "question_id": "research_q_productos_proof_posture",
                    "question": "Do buyers expect proof before adoption?",
                }
            ],
            "created_at": "2026-03-26T08:00:00Z",
        },
    )
    _write_json(
        root / "internal" / "ProductOS-Next" / "artifacts" / "external_research_source_discovery.json",
        {
            "schema_version": "1.0.0",
            "external_research_source_discovery_id": "external_research_source_discovery_ws_productos_v2",
            "workspace_id": "ws_productos_v2",
            "search_status": "completed",
            "candidate_sources": [{"source_id": "src_market"}],
            "discovered_questions": [{"question_id": "research_q_productos_proof_posture", "candidate_count": 1}],
            "created_at": "2026-03-26T08:00:00Z",
        },
    )
    _write_json(
        root / "internal" / "ProductOS-Next" / "artifacts" / "external_research_feed_registry.json",
        {
            "schema_version": "1.0.0",
            "external_research_feed_registry_id": "external_research_feed_registry_ws_productos_v2",
            "workspace_id": "ws_productos_v2",
            "title": "External research feed registry",
            "feeds": [
                {
                    "feed_id": "feed_market_validation",
                    "title": "Market validation feed",
                    "source_type": "market_validation",
                    "uri": "https://example.com/feed.xml",
                    "trust_tier": "primary",
                    "refresh_cadence": "weekly",
                    "health_status": "healthy",
                    "cadence_status": "stale",
                    "cadence_reason": "Feed is materially past its weekly cadence and should not be trusted without refresh.",
                }
            ],
            "created_at": "2026-03-26T08:00:00Z",
        },
    )
    _write_json(
        root / "internal" / "ProductOS-Next" / "outputs" / "research" / "external-research-manifest.selected.json",
        {
            "sources": [
                {
                    "source_id": "src_market",
                    "question_id": "research_q_productos_proof_posture",
                }
            ]
        },
    )
    _write_json(
        root / "internal" / "ProductOS-Next" / "artifacts" / "external_research_review.json",
        {
            "schema_version": "1.0.0",
            "external_research_review_id": "external_research_review_ws_productos_v2",
            "workspace_id": "ws_productos_v2",
            "review_status": "clear",
            "accepted_source_ids": ["src_market"],
            "contradiction_items": [],
            "review_items": [],
            "recommendation": "continue_with_refresh",
            "created_at": "2026-03-26T08:00:00Z",
        },
    )

    with pytest.raises(ValueError, match="feed registry"):
        promote_release_from_ralph(
            root,
            root / "internal" / "ProductOS-Next" / "artifacts" / "ralph_loop_state_next_version_completion.example.json",
            released_at="2026-03-26T08:10:00Z",
            eval_run_report_path=root / "internal" / "ProductOS-Next" / "artifacts" / "eval_run_report.json",
            feature_portfolio_review_path=root / "internal" / "ProductOS-Next" / "artifacts" / "feature_portfolio_review.json",
            research_brief_path=root / "internal" / "ProductOS-Next" / "artifacts" / "research_brief.json",
            external_research_plan_path=root / "internal" / "ProductOS-Next" / "artifacts" / "external_research_plan.json",
            external_research_source_discovery_path=root / "internal" / "ProductOS-Next" / "artifacts" / "external_research_source_discovery.json",
            external_research_feed_registry_path=root / "internal" / "ProductOS-Next" / "artifacts" / "external_research_feed_registry.json",
            selected_manifest_path=root / "internal" / "ProductOS-Next" / "outputs" / "research" / "external-research-manifest.selected.json",
            external_research_review_path=root / "internal" / "ProductOS-Next" / "artifacts" / "external_research_review.json",
        )
