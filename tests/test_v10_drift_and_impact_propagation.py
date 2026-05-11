from __future__ import annotations

import json
from pathlib import Path

from core.python.productos_runtime.living_system import (
    build_regeneration_queue,
    detect_circular_dependencies,
    generate_impact_propagation_map,
)


def test_competitor_dossier_update_queues_strategy_brief(tmp_path: Path):
    workspace_dir = tmp_path / "workspace"
    artifacts_dir = workspace_dir / "artifacts"
    artifacts_dir.mkdir(parents=True)
    (artifacts_dir / "competitor_dossier.json").write_text(
        json.dumps(
            {
                "schema_version": "1.1.0",
                "source_artifact_ids": ["artifacts/research_notebook.json"]
            }
        ),
        encoding="utf-8",
    )
    (artifacts_dir / "strategy_context_brief.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "source_artifact_ids": ["artifacts/competitor_dossier.json"]
            }
        ),
        encoding="utf-8",
    )
    ipm = generate_impact_propagation_map(workspace_dir)
    (artifacts_dir / "impact_propagation_map.json").write_text(json.dumps(ipm), encoding="utf-8")
    queue = build_regeneration_queue(
        {
            "event_type": "competitive_alert",
            "source_artifact_ref": "artifacts/competitor_dossier.json",
            "change_summary": "competitor pricing and positioning changed",
        },
        workspace_dir,
        generated_at="2026-05-11T00:00:00Z",
    )
    assert any("strategy_context_brief" in item["target_artifact_ref"] for item in queue["queued_items"])


def test_prd_scope_change_queues_prototype_record(tmp_path: Path):
    workspace_dir = tmp_path / "workspace"
    artifacts_dir = workspace_dir / "artifacts"
    artifacts_dir.mkdir(parents=True)
    (artifacts_dir / "prd.json").write_text(json.dumps({"schema_version": "1.1.0"}), encoding="utf-8")
    (artifacts_dir / "prototype_record.json").write_text(
        json.dumps({"schema_version": "1.0.0", "source_artifact_ids": ["artifacts/prd.json"]}),
        encoding="utf-8",
    )
    ipm = generate_impact_propagation_map(workspace_dir)
    (artifacts_dir / "impact_propagation_map.json").write_text(json.dumps(ipm), encoding="utf-8")
    queue = build_regeneration_queue(
        {
            "event_type": "artifact_updated",
            "source_artifact_ref": "artifacts/prd.json",
            "change_summary": "scope tightened for v1",
        },
        workspace_dir,
        generated_at="2026-05-11T00:00:00Z",
    )
    assert any("prototype_record" in item["target_artifact_ref"] for item in queue["queued_items"])


def test_circular_dependency_escalates(tmp_path: Path):
    workspace_dir = tmp_path / "workspace"
    artifacts_dir = workspace_dir / "artifacts"
    artifacts_dir.mkdir(parents=True)
    for filename, deps in {
        "a.json": ["artifacts/b.json"],
        "b.json": ["artifacts/c.json"],
        "c.json": ["artifacts/a.json"],
    }.items():
        (artifacts_dir / filename).write_text(json.dumps({"dependencies": deps}), encoding="utf-8")
    cycle = detect_circular_dependencies(
        ["artifacts/a.json", "artifacts/b.json", "artifacts/c.json"],
        workspace_dir,
    )
    assert cycle is not None
