import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml


def _run_cli(root_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/productos.py", *args],
        cwd=root_dir,
        capture_output=True,
        text=True,
        check=False,
    )


def test_productos_status_command(root_dir: Path):
    result = _run_cli(root_dir, "status")

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Mode: status" in result.stdout
    assert "Top Priority Feature: extend_lifecycle_beyond_release_readiness" in result.stdout
    assert "Truthfulness Status: healthy" in result.stdout
    assert "Eval Status: passed (0 regressions)" in result.stdout
    assert "Stable Promotion: ready" in result.stdout


def test_productos_doctor_command(root_dir: Path):
    result = _run_cli(root_dir, "doctor")

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Bundle Status: healthy" in result.stdout
    assert "Stable Promotion: ready" in result.stdout
    assert "Intake Items: 2" in result.stdout
    assert "Top Priority Feature: extend_lifecycle_beyond_release_readiness" in result.stdout


def test_productos_cutover_command(root_dir: Path, tmp_path: Path):
    output_path = tmp_path / "v6-cutover-plan.md"
    result = _run_cli(root_dir, "cutover", "--output-path", str(output_path))

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Target Version: 6.0.0" in result.stdout
    assert "Selection Status: stable_active" in result.stdout
    assert "Promotion Gate: ready" in result.stdout
    assert "Stable Release: V6.0.0" in result.stdout
    assert "Build Strategy: stabilize_then_extend" in result.stdout
    assert "Selected Bundle: Lifecycle traceability through release readiness" in result.stdout
    assert output_path.exists()
    markdown = output_path.read_text(encoding="utf-8")
    assert "# V6 Cutover Plan" in markdown
    assert "## Selected Bundle" in markdown
    assert "Lifecycle traceability through release readiness" in markdown
    assert "extend_lifecycle_beyond_release_readiness" in markdown
    assert "keep V6.0.0 as the stable line" in markdown
    assert "extend beyond release_readiness only through a later bounded release" in markdown


def test_productos_v5_command(root_dir: Path, tmp_path: Path):
    archived_v5_dir = root_dir / "internal" / "ProductOS-Next" / "archive" / "historical-artifacts" / "v5_lifecycle_traceability"
    release_5_path = root_dir / "registry" / "releases" / "release_5_0_0.json"
    if not archived_v5_dir.exists() or not release_5_path.exists():
        pytest.skip("Historical V5 validation surface is not included in this repo boundary.")

    result = _run_cli(root_dir, "v5", "--output-dir", str(tmp_path))

    assert result.returncode == 0, result.stderr or result.stdout
    assert "V5 Bundle: Lifecycle traceability through PRD handoff" in result.stdout
    assert "Target Release: 5.0.0" in result.stdout
    assert "Scenario Status: passed" in result.stdout
    assert "Release Decision: go" in result.stdout
    assert (tmp_path / "runtime_scenario_report_v5_lifecycle_traceability.json").exists()
    assert (tmp_path / "release_gate_decision_v5_lifecycle_traceability.json").exists()
    assert (tmp_path / "ralph_loop_state_v5_lifecycle_traceability.json").exists()


def test_productos_v6_command(root_dir: Path, tmp_path: Path):
    result = _run_cli(root_dir, "v6", "--output-dir", str(tmp_path))

    assert result.returncode == 0, result.stderr or result.stdout
    assert "V6 Bundle: Lifecycle traceability through release readiness" in result.stdout
    assert "Target Release: 6.0.0" in result.stdout
    assert "Scenario Status: passed" in result.stdout
    assert "Release Decision: go" in result.stdout
    assert (tmp_path / "runtime_scenario_report_v6_lifecycle_traceability.json").exists()
    assert (tmp_path / "release_gate_decision_v6_lifecycle_traceability.json").exists()
    assert (tmp_path / "ralph_loop_state_v6_lifecycle_traceability.json").exists()


def test_productos_run_discover_command_exports_phase_artifacts(root_dir: Path, tmp_path: Path):
    result = _run_cli(root_dir, "run", "discover", "--output-dir", str(tmp_path))

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Phase: discover" in result.stdout
    assert "Session Status: completed" in result.stdout
    assert "Context Pack: context_pack_ws_productos_v2_bounded_baseline" in result.stdout
    assert (tmp_path / "context_pack.json").exists()
    assert (tmp_path / "discover_problem_brief.json").exists()
    assert (tmp_path / "discover_concept_brief.json").exists()
    assert (tmp_path / "discover_prd.json").exists()
    assert (tmp_path / "discover_execution_session_state.json").exists()
    assert (tmp_path / "discover_feature_scorecard.json").exists()


def test_productos_run_align_command_exports_phase_artifacts(root_dir: Path, tmp_path: Path):
    result = _run_cli(root_dir, "run", "align", "--output-dir", str(tmp_path))

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Phase: align" in result.stdout
    assert "Session Status: completed" in result.stdout
    assert (tmp_path / "context_pack.json").exists()
    assert (tmp_path / "align_execution_session_state.json").exists()
    assert (tmp_path / "align_document_sync_state.json").exists()
    assert (tmp_path / "market_distribution_report.json").exists()
    assert (tmp_path / "docs_alignment_feature_scorecard.json").exists()
    assert (tmp_path / "presentation_feature_scorecard.json").exists()


def test_productos_run_operate_command_exports_phase_artifacts(root_dir: Path, tmp_path: Path):
    result = _run_cli(root_dir, "run", "operate", "--output-dir", str(tmp_path))

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Phase: operate" in result.stdout
    assert "Session Status: completed" in result.stdout
    assert (tmp_path / "context_pack.json").exists()
    assert (tmp_path / "operate_execution_session_state.json").exists()
    assert (tmp_path / "operate_status_mail.json").exists()
    assert (tmp_path / "operate_issue_log.json").exists()
    assert (tmp_path / "weekly_pm_autopilot_feature_scorecard.json").exists()


def test_productos_run_improve_command_exports_phase_artifacts(root_dir: Path, tmp_path: Path):
    result = _run_cli(root_dir, "run", "improve", "--output-dir", str(tmp_path))

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Phase: improve" in result.stdout
    assert "Session Status: completed" in result.stdout
    assert (tmp_path / "context_pack.json").exists()
    assert (tmp_path / "eval_suite_manifest.json").exists()
    assert (tmp_path / "eval_run_report.json").exists()
    assert (tmp_path / "improve_execution_session_state.json").exists()
    assert (tmp_path / "improve_improvement_loop_state.json").exists()
    assert (tmp_path / "adapter_parity_report.json").exists()
    assert (tmp_path / "market_refresh_report.json").exists()
    assert (tmp_path / "self_improvement_feature_scorecard.json").exists()
    assert (tmp_path / "feature_portfolio_review.json").exists()


def test_productos_export_command_writes_bundle(root_dir: Path, tmp_path: Path):
    output_dir = tmp_path / "bundle"
    result = _run_cli(root_dir, "export", "--output-dir", str(output_dir))

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Exported 31 artifacts" in result.stdout

    portfolio_path = output_dir / "feature_portfolio_review.json"
    assert portfolio_path.exists()
    payload = json.loads(portfolio_path.read_text(encoding="utf-8"))
    assert payload["top_priority_feature_id"] == "v5_bundle_selection"


def test_productos_trace_item_command(root_dir: Path):
    result = _run_cli(root_dir, "trace", "--item-id", "opp_pm_lifecycle_traceability")

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Item: Lifecycle traceability and stage visibility for PM work" in result.stdout
    assert "Current Stage: release_readiness" in result.stdout
    assert "- problem_framing: completed" in result.stdout


def test_productos_trace_stage_command(root_dir: Path):
    result = _run_cli(root_dir, "trace", "--stage", "delivery")

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Focus Area: delivery" in result.stdout
    assert "Items: 1" in result.stdout
    assert "- story_planning: items=1, gate_passed=1" in result.stdout
    assert "- release_readiness: items=1, gate_passed=1" in result.stdout


def test_productos_init_workspace_command(root_dir: Path, tmp_path: Path):
    destination = tmp_path / "acme-workspace"
    result = _run_cli(
        root_dir,
        "init-workspace",
        "--dest",
        str(destination),
        "--workspace-id",
        "ws_acme",
        "--name",
        "Acme Product Workspace",
        "--mode",
        "enterprise",
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert destination.exists()
    assert "Initialized workspace from templates" in result.stdout

    with (destination / "workspace_manifest.yaml").open("r", encoding="utf-8") as handle:
        manifest = yaml.safe_load(handle)
    lifecycle_state = json.loads((destination / "artifacts" / "item_lifecycle_state.json").read_text(encoding="utf-8"))

    assert manifest["workspace_id"] == "ws_acme"
    assert manifest["name"] == "Acme Product Workspace"
    assert manifest["mode"] == "enterprise"
    assert manifest["active_increment_id"] == "pi_initial_01"
    assert lifecycle_state["workspace_id"] == "ws_acme"
    assert "artifacts/story_pack.json" in manifest["artifact_paths"]
    assert "artifacts/release_readiness.json" in manifest["artifact_paths"]
