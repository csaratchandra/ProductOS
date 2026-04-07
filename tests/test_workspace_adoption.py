import json
import subprocess
import sys
from pathlib import Path

import yaml


def _run_cli(root_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/productos.py", *args],
        cwd=root_dir,
        capture_output=True,
        text=True,
        check=False,
    )


def test_adopt_workspace_dry_run_exports_codesync_bundle(root_dir: Path, codesync_workspace_dir: Path, tmp_path: Path):
    output_dir = tmp_path / "adoption-bundle"
    destination = tmp_path / "codesync-adopted"
    result = _run_cli(
        root_dir,
        "adopt-workspace",
        "--source",
        str(codesync_workspace_dir),
        "--dest",
        str(destination),
        "--workspace-id",
        "ws_codesync",
        "--name",
        "CodeSync",
        "--mode",
        "research",
        "--dry-run",
        "--output-dir",
        str(output_dir),
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Source Workspace Mode: notes_first" in result.stdout
    assert "Adoption Status: dry-run" in result.stdout
    assert "Dry Run: no workspace files were written." in result.stdout
    assert not destination.exists()

    report = json.loads((output_dir / "workspace_adoption_report.json").read_text(encoding="utf-8"))
    review_queue = json.loads((output_dir / "adoption_review_queue.json").read_text(encoding="utf-8"))
    lifecycle_state = json.loads((output_dir / "item_lifecycle_state.json").read_text(encoding="utf-8"))
    note_card = json.loads((output_dir / "source_note_card_executive_brief.json").read_text(encoding="utf-8"))

    assert report["source_workspace_mode"] == "notes_first"
    assert report["source_file_count"] > 0
    assert "prd_codesync" in " ".join(report["generated_artifact_ids"])
    assert len(review_queue["review_items"]) >= 4
    assert lifecycle_state["current_stage"] == "prd_handoff"
    assert lifecycle_state["overall_status"] == "active_discovery"
    assert note_card["source_ref"] == "Notes/research/01-executive-brief.md"


def test_adopt_workspace_persists_traceable_workspace(root_dir: Path, codesync_workspace_dir: Path, tmp_path: Path):
    destination = tmp_path / "codesync-adopted"
    result = _run_cli(
        root_dir,
        "adopt-workspace",
        "--source",
        str(codesync_workspace_dir),
        "--dest",
        str(destination),
        "--workspace-id",
        "ws_codesync",
        "--name",
        "CodeSync",
        "--mode",
        "research",
        "--emit-report",
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Adoption Status: completed" in result.stdout
    assert destination.exists()

    with (destination / "workspace_manifest.yaml").open("r", encoding="utf-8") as handle:
        manifest = yaml.safe_load(handle)

    assert "artifacts/research_brief.json" in manifest["artifact_paths"]
    assert "artifacts/workspace_adoption_report.json" in manifest["artifact_paths"]
    assert "artifacts/adoption_review_queue.json" in manifest["artifact_paths"]

    prd = json.loads((destination / "artifacts" / "prd.json").read_text(encoding="utf-8"))
    report = json.loads((destination / "artifacts" / "workspace_adoption_report.json").read_text(encoding="utf-8"))
    snapshot = json.loads((destination / "artifacts" / "lifecycle_stage_snapshot.json").read_text(encoding="utf-8"))

    assert prd["title"] == "PRD: CodeSync workspace adoption launch lane"
    assert report["destination_workspace_path"] == destination.as_posix()
    assert snapshot["focus_area"] == "discovery"
    assert snapshot["gate_counts"]["pending"] >= 1

    assert (destination / "docs" / "planning" / "workspace-adoption-report.md").exists()
    assert (destination / "inbox" / "raw-notes" / "2026-03-22-next-version-superpowers.md").exists()
    assert (destination / "inbox" / "transcripts" / "2026-03-22-dogfood-next-version-session.txt").exists()


def test_adopted_workspace_supports_trace_command(root_dir: Path, codesync_workspace_dir: Path, tmp_path: Path):
    destination = tmp_path / "codesync-adopted"
    adopt_result = _run_cli(
        root_dir,
        "adopt-workspace",
        "--source",
        str(codesync_workspace_dir),
        "--dest",
        str(destination),
        "--workspace-id",
        "ws_codesync",
        "--name",
        "CodeSync",
        "--mode",
        "research",
    )
    assert adopt_result.returncode == 0, adopt_result.stderr or adopt_result.stdout

    trace_result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "trace",
        "--stage",
        "discovery",
    )

    assert trace_result.returncode == 0, trace_result.stderr or trace_result.stdout
    assert "Focus Area: discovery" in trace_result.stdout
    assert "- prd_handoff: items=1, gate_passed=0, gate_pending=1" in trace_result.stdout


def test_adopted_workspace_supports_ingest_discover_and_validate(root_dir: Path, codesync_workspace_dir: Path, tmp_path: Path):
    destination = tmp_path / "codesync-adopted"
    adopt_result = _run_cli(
        root_dir,
        "adopt-workspace",
        "--source",
        str(codesync_workspace_dir),
        "--dest",
        str(destination),
        "--workspace-id",
        "ws_codesync",
        "--name",
        "CodeSync",
        "--mode",
        "research",
    )
    assert adopt_result.returncode == 0, adopt_result.stderr or adopt_result.stdout

    ingest_result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "ingest",
    )
    assert ingest_result.returncode == 0, ingest_result.stderr or ingest_result.stdout
    assert "Ingestion Mode: manual" in ingest_result.stdout
    assert "Intake Items:" in ingest_result.stdout

    discover_output = tmp_path / "discover-output"
    discover_result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "run",
        "discover",
        "--output-dir",
        str(discover_output),
    )
    assert discover_result.returncode == 0, discover_result.stderr or discover_result.stdout
    assert "Phase: discover" in discover_result.stdout
    assert "Context Pack: context_pack_ws_codesync_bounded_baseline" in discover_result.stdout
    assert (discover_output / "discover_problem_brief.json").exists()
    assert (discover_output / "discover_concept_brief.json").exists()
    assert (discover_output / "discover_prd.json").exists()

    validate_result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "validate-workspace",
    )
    assert validate_result.returncode == 0, validate_result.stderr or validate_result.stdout
    assert "Workspace validation passed:" in validate_result.stdout
    assert "source note cards indexed." in validate_result.stdout
