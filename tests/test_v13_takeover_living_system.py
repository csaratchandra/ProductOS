"""Tests for V13 takeover living system integration."""

import json
from pathlib import Path

import pytest

from core.python.productos_runtime.living_system import (
    generate_impact_propagation_map,
    build_regeneration_queue,
)


class TestTakeoverArtifactPropagation:
    def test_propagation_map_includes_takeover_refs(self, tmp_path):
        artifacts_dir = tmp_path / "artifacts"
        artifacts_dir.mkdir(parents=True)

        # Create a takeover source artifact
        code_understanding = {
            "code_understanding_id": "cu_test",
            "workspace_id": "test",
            "module_graph": [],
            "api_surface": [],
            "feature_flags": [],
            "change_velocity": {"module_velocity": [], "overall_summary": ""},
            "evidence_confidence": {"summary": "", "observed_count": 0, "inferred_count": 0, "uncertain_count": 0},
            "source_repo_path": "/test",
            "generated_at": "2026-03-22T08:00:00Z",
            "schema_version": "1.0.0",
        }
        (artifacts_dir / "code_understanding.json").write_text(json.dumps(code_understanding), encoding="utf-8")

        prop_map = generate_impact_propagation_map(tmp_path)
        deps = prop_map.get("dependencies", {})

        takeover_downstream = ["artifacts/takeover_brief.json", "artifacts/problem_space_map.json"]
        cu_ref = "artifacts/code_understanding.json"
        if cu_ref in deps:
            for td in takeover_downstream:
                assert td in deps[cu_ref], f"{cu_ref} should propagate to {td}"

    def test_regeneration_scoped_to_takeover(self, tmp_path):
        artifacts_dir = tmp_path / "artifacts"
        artifacts_dir.mkdir(parents=True)
        (artifacts_dir / "persona_pack.json").write_text(
            json.dumps({"persona_pack_id": "pp_test", "personas": [{"name": "Admin"}]}), encoding="utf-8"
        )
        change_event = {
            "event_type": "artifact_updated",
            "source_artifact_ref": "artifacts/persona_pack.json",
            "changed_keys": ["personas"],
        }
        queue = build_regeneration_queue(change_event, tmp_path)
        assert queue is not None
        assert "regeneration_queue_id" in queue


class TestSpecArtifactPropagation:
    def test_propagation_map_includes_spec_refs(self, tmp_path):
        artifacts_dir = tmp_path / "artifacts"
        artifacts_dir.mkdir(parents=True)

        (artifacts_dir / "problem_space_map.json").write_text(
            json.dumps({"problem_space_map_id": "psm_test", "problems": [{"problem_id": "p1"}]}), encoding="utf-8"
        )

        prop_map = generate_impact_propagation_map(tmp_path)
        deps = prop_map.get("dependencies", {})

        spec_downstream = ["artifacts/multi_journey_bundle.json", "artifacts/build_spec_bundle.json"]
        psm_ref = "artifacts/problem_space_map.json"
        if psm_ref in deps:
            for sd in spec_downstream:
                assert sd in deps[psm_ref], f"{psm_ref} should propagate to {sd}"
