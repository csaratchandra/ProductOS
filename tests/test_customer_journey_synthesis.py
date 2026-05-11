from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from core.python.productos_runtime.journey_synthesis import synthesize_customer_journey_map


def test_synthesizes_valid_customer_journey_map_from_workspace_fixture(bundled_workspace_dir: Path):
    """Synthesis runtime should produce a schema-valid customer_journey_map.json
    from the bundled workspace's persona_pack + problem_brief + source_note_cards."""
    cjm = synthesize_customer_journey_map(bundled_workspace_dir)

    # Basic structure
    assert cjm["schema_version"] == "1.0.0"
    assert "customer_journey_map_id" in cjm
    assert "workspace_id" in cjm
    assert cjm["title"]

    # 11 stages
    stages = cjm["journey_stages"]
    assert len(stages) == 11
    stage_names = {s["stage_name"] for s in stages}
    expected = {
        "unaware", "aware", "research", "consideration", "decision",
        "purchase", "onboarding", "adoption", "expansion", "advocacy",
        "renewal_or_churn",
    }
    assert stage_names == expected

    # Emotion scores in range
    for s in stages:
        assert 1 <= s["emotion_score"] <= 10
        assert s["emotion_label"] in ["frustrated", "confused", "neutral", "satisfied", "delighted"]

    # Overall emotion curve
    curve = cjm["overall_emotion_curve"]
    assert curve["peak_emotion_stage"] in stage_names
    assert curve["valley_emotion_stage"] in stage_names

    # Moments of truth >= 2
    assert len(cjm["moments_of_truth"]) >= 2

    # Gap analysis
    gaps = cjm["gap_analysis"]
    assert "current_vs_ideal_summary" in gaps
    assert len(gaps["critical_gaps"]) >= 1

    # Opportunities >= 1
    assert len(cjm["opportunities"]) >= 1

    # Schema validation
    schema_path = bundled_workspace_dir.parents[3] / "core" / "schemas" / "artifacts" / "customer_journey_map.schema.json"
    schema = json.loads(schema_path.read_text())
    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(cjm))
    assert not errors, "Synthesized CJM has schema errors: " + "; ".join(
        f"{e.json_path}: {e.message}" for e in errors
    )


def test_synthesis_idempotent_given_same_workspace(bundled_workspace_dir: Path):
    cjm1 = synthesize_customer_journey_map(bundled_workspace_dir)
    cjm2 = synthesize_customer_journey_map(bundled_workspace_dir)
    assert cjm1["journey_stages"][0]["stage_name"] == cjm2["journey_stages"][0]["stage_name"]


def test_synthesis_includes_evidence_refs_when_source_notes_present(bundled_workspace_dir: Path):
    cjm = synthesize_customer_journey_map(bundled_workspace_dir)
    assert len(cjm.get("source_evidence_refs", [])) > 0


def test_synthesis_completes_in_under_30_seconds(bundled_workspace_dir: Path):
    import time
    start = time.time()
    synthesize_customer_journey_map(bundled_workspace_dir)
    elapsed = time.time() - start
    assert elapsed < 30
