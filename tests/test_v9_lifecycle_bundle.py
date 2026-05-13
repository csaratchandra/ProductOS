from pathlib import Path

from conftest import latest_release, parse_semver, validator_for
from core.python.productos_runtime import build_v9_lifecycle_bundle_from_workspace
from core.python.productos_runtime.v9 import V9_ARTIFACT_SCHEMAS


def test_build_v9_lifecycle_bundle_from_workspace_validates(bundled_workspace_dir: Path):
    bundle = build_v9_lifecycle_bundle_from_workspace(
        bundled_workspace_dir,
        generated_at="2026-05-03T08:00:00Z",
    )

    for artifact_name, schema_name in V9_ARTIFACT_SCHEMAS.items():
        validator = validator_for(schema_name)
        payload = bundle[artifact_name]
        errors = sorted(validator.iter_errors(payload), key=lambda item: list(item.path))
        assert not errors, f"{artifact_name} failed schema validation: {[error.message for error in errors]}"


def test_v9_lifecycle_bundle_cross_refs_and_gate_stay_blocked_before_promotion(bundled_workspace_dir: Path):
    bundle = build_v9_lifecycle_bundle_from_workspace(
        bundled_workspace_dir,
        generated_at="2026-05-03T08:00:00Z",
    )

    runtime_report = bundle["runtime_scenario_report_v9_lifecycle_enrichment"]
    validation_report = bundle["validation_lane_report_v9_lifecycle_enrichment"]
    manual_record = bundle["manual_validation_record_v9_lifecycle_enrichment"]
    release_readiness = bundle["release_readiness_v9_lifecycle_enrichment"]
    release_gate = bundle["release_gate_decision_v9_lifecycle_enrichment"]
    ralph = bundle["ralph_loop_state_v9_lifecycle_enrichment"]

    assert runtime_report["candidate_version"] == "10.0.0"
    assert runtime_report["baseline_version"] == "10.0.0"
    assert validation_report["artifact_ref"] == runtime_report["runtime_scenario_report_id"]
    assert manual_record["subject_ref"] == runtime_report["runtime_scenario_report_id"]
    assert manual_record["related_validation_report_ref"] == validation_report["validation_lane_report_id"]
    assert release_gate["runtime_scenario_report_ref"] == runtime_report["runtime_scenario_report_id"]
    assert release_gate["release_readiness_ref"] == release_readiness["release_readiness_id"]
    assert release_gate["decision"] == "no_go"
    assert release_readiness["status"] == "watch"
    assert ralph["target_release"] == "v10_0_0"
    assert ralph["overall_status"] == "in_progress"
    assert validation_report["overall_status"] == "ready_for_manual_validation"


def test_v9_bundle_does_not_move_public_stable_line_before_go_gate(root_dir: Path, bundled_workspace_dir: Path):
    bundle = build_v9_lifecycle_bundle_from_workspace(
        bundled_workspace_dir,
        generated_at="2026-05-03T08:00:00Z",
    )

    release = latest_release(root_dir)
    candidate_version = bundle["runtime_scenario_report_v9_lifecycle_enrichment"]["candidate_version"]
    assert bundle["release_gate_decision_v9_lifecycle_enrichment"]["decision"] == "no_go"
    assert parse_semver(release["core_version"]) >= parse_semver(candidate_version)
