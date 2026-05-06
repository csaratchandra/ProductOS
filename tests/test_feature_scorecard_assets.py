from pathlib import Path

import yaml

from conftest import load_json, validator_for
from core.python.productos_runtime import build_foundation_bundle_from_workspace


def test_feature_scoring_docs_exist(root_dir: Path):
    required = [
        root_dir / "core" / "docs" / "feature-scoring-model.md",
        root_dir / "core" / "workflows" / "mastery" / "feature-scoring-and-dogfood-review-workflow.md",
        root_dir / "core" / "rubrics" / "prototype_quality_rubric.md",
    ]
    missing = [path for path in required if not path.exists()]
    assert not missing, f"Missing feature-scoring docs/workflow: {missing}"


def test_feature_scorecard_examples_validate(root_dir: Path, bundled_workspace_dir: Path):
    validator = validator_for("feature_scorecard.schema.json")

    core_payload = load_json(root_dir / "core" / "examples" / "artifacts" / "feature_scorecard.example.json")
    workspace_payload = load_json(bundled_workspace_dir / "artifacts" / "feature_scorecard.example.json")

    for name, payload in {
        "core": core_payload,
        "workspace": workspace_payload,
    }.items():
        errors = sorted(validator.iter_errors(payload), key=lambda item: list(item.path))
        assert not errors, f"{name} feature scorecard failed validation: {[error.message for error in errors]}"


def test_feature_scorecard_invalid_fixture_fails(root_dir: Path):
    validator = validator_for("feature_scorecard.schema.json")
    payload = load_json(root_dir / "tests" / "fixtures" / "invalid" / "feature_scorecard_missing_feedback_items_for_score_4.json")
    errors = sorted(validator.iter_errors(payload), key=lambda item: list(item.path))

    assert errors, "feature scorecard invalid fixture unexpectedly passed"
    error_paths = {".".join(str(part) for part in error.absolute_path) or "<root>" for error in errors}
    assert "feedback_items" in error_paths or "<root>" in error_paths


def test_workspace_manifest_wires_feature_scoring(bundled_workspace_dir: Path):
    manifest_path = bundled_workspace_dir / "workspace_manifest.yaml"
    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = yaml.safe_load(handle)

    assert "artifacts/feature_scorecard.example.json" in manifest["artifact_paths"]
    assert "../../core/workflows/mastery/feature-scoring-and-dogfood-review-workflow.md" in manifest["workflow_paths"]


def test_improvement_loop_tracks_feature_scorecard(bundled_workspace_dir: Path):
    validator = validator_for("improvement_loop_state.schema.json")
    payload = load_json(bundled_workspace_dir / "artifacts" / "improvement_loop_state.example.json")
    errors = sorted(validator.iter_errors(payload), key=lambda item: list(item.path))

    assert not errors, f"workspace improvement loop failed validation: {[error.message for error in errors]}"
    assert payload["feature_scorecard_refs"] == [
        "feature_scorecard_ws_productos_v2_docs_alignment_superpower",
        "feature_scorecard_ws_productos_v2_weekly_pm_autopilot",
        "feature_scorecard_ws_productos_v2_market_intelligence_superpower",
    ]


def test_bounded_foundation_bundle_includes_feature_scorecard(bundled_workspace_dir: Path):
    bundle = build_foundation_bundle_from_workspace(
        bundled_workspace_dir,
        generated_at="2026-03-21T23:55:00Z",
    )

    validator = validator_for("feature_scorecard.schema.json")
    payload = bundle["feature_scorecard"]
    errors = sorted(validator.iter_errors(payload), key=lambda item: list(item.path))
    assert not errors, f"generated feature scorecard failed validation: {[error.message for error in errors]}"

    assert payload["benchmark_ref"] == bundle["pm_superpower_benchmark"]["pm_superpower_benchmark_id"]
    assert payload["overall_score"] == 4
    assert payload["adoption_recommendation"] == "keep_in_internal_use"
    assert "document_sync_state_ws_productos_v2_v4_readable_docs" in payload["evidence_refs"]
    assert payload["feedback_items"][0]["route_targets"] == [
        "productos_feedback_log",
        "improvement_loop_state",
    ]
