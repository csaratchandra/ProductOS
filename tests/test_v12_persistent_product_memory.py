from __future__ import annotations

import json
from pathlib import Path

from core.python.productos_runtime.memory_registers import (
    load_competitor_registry,
    load_problem_register,
    sync_memory_registers,
)
from core.python.productos_runtime.pm_note_ingestion import ingest_pm_note


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_sync_memory_registers_bootstraps_from_canonical_artifacts(root_dir: Path, tmp_path: Path):
    workspace_dir = tmp_path / "workspace"
    artifacts_dir = workspace_dir / "artifacts"
    artifacts_dir.mkdir(parents=True)
    (workspace_dir / "workspace_manifest.yaml").write_text("artifact_paths: []\n", encoding="utf-8")

    problem_brief = _load_json(root_dir / "templates" / "artifacts" / "problem_brief.json")
    competitor_dossier = _load_json(root_dir / "templates" / "artifacts" / "competitor_dossier.json")
    problem_brief["workspace_id"] = "ws_memory_test"
    competitor_dossier["workspace_id"] = "ws_memory_test"

    (artifacts_dir / "problem_brief.json").write_text(json.dumps(problem_brief), encoding="utf-8")
    (artifacts_dir / "competitor_dossier.json").write_text(json.dumps(competitor_dossier), encoding="utf-8")

    synced = sync_memory_registers(
        workspace_dir,
        generated_at="2026-05-12T10:00:00Z",
        problem_brief=problem_brief,
        competitor_dossier=competitor_dossier,
    )

    assert "problem_register.json" in synced
    assert "competitor_registry.json" in synced
    assert (artifacts_dir / "problem_register.json").exists()
    assert (artifacts_dir / "competitor_registry.json").exists()

    register = load_problem_register(workspace_dir, persist=False)
    competitor_registry = load_competitor_registry(workspace_dir, persist=False)
    assert register is not None
    assert competitor_registry is not None
    assert register["current_problem_entry_id"] == "problem_starter_trace_demo"
    assert len(competitor_registry["competitors"]) == 2


def test_ingest_pm_note_emits_problem_and_competitor_memory_candidates(root_dir: Path, tmp_path: Path):
    workspace_dir = tmp_path / "workspace"
    artifacts_dir = workspace_dir / "artifacts"
    inbox_dir = workspace_dir / "inbox" / "raw-notes"
    artifacts_dir.mkdir(parents=True)
    inbox_dir.mkdir(parents=True)

    problem_brief = _load_json(root_dir / "templates" / "artifacts" / "problem_brief.json")
    competitor_dossier = _load_json(root_dir / "templates" / "artifacts" / "competitor_dossier.json")
    problem_brief["workspace_id"] = workspace_dir.name
    competitor_dossier["workspace_id"] = workspace_dir.name

    (artifacts_dir / "problem_brief.json").write_text(json.dumps(problem_brief), encoding="utf-8")
    (artifacts_dir / "competitor_dossier.json").write_text(json.dumps(competitor_dossier), encoding="utf-8")
    sync_memory_registers(
        workspace_dir,
        generated_at="2026-05-12T10:00:00Z",
        problem_brief=problem_brief,
        competitor_dossier=competitor_dossier,
    )

    note_path = inbox_dir / "market-note.txt"
    note_path.write_text(
        "We have a competitor signal from Linear and a new problem around workflow friction that should update our current problem framing.",
        encoding="utf-8",
    )

    proposal = ingest_pm_note(workspace_dir, note_path, generated_at="2026-05-12T10:00:00Z")

    assert proposal["proposed_deltas"]
    assert proposal["memory_candidates"]
    candidate_types = {item["candidate_type"] for item in proposal["memory_candidates"]}
    assert candidate_types == {"problem", "competitor"}
