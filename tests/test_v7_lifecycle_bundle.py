from pathlib import Path

from conftest import validator_for
from core.python.productos_runtime import build_v7_lifecycle_bundle_from_workspace
from core.python.productos_runtime.v7 import V7_ARTIFACT_SCHEMAS


def test_build_v7_lifecycle_bundle_from_workspace_validates(root_dir: Path):
    bundle = build_v7_lifecycle_bundle_from_workspace(
        root_dir / "internal" / "ProductOS-Next",
        generated_at="2026-04-07T07:20:00Z",
    )

    for artifact_name, schema_name in V7_ARTIFACT_SCHEMAS.items():
        validator = validator_for(schema_name)
        payload = bundle[artifact_name]
        errors = sorted(validator.iter_errors(payload), key=lambda item: list(item.path))
        assert not errors, f"{artifact_name} failed schema validation: {[error.message for error in errors]}"


def test_v7_lifecycle_bundle_cross_refs(root_dir: Path):
    bundle = build_v7_lifecycle_bundle_from_workspace(
        root_dir / "internal" / "ProductOS-Next",
        generated_at="2026-04-07T07:20:00Z",
    )

    runtime_report = bundle["runtime_scenario_report_v7_lifecycle_traceability"]
    validation_report = bundle["validation_lane_report_v7_lifecycle_traceability"]
    manual_record = bundle["manual_validation_record_v7_lifecycle_traceability"]
    release_readiness = bundle["release_readiness_v7_lifecycle_traceability"]
    release_gate = bundle["release_gate_decision_v7_lifecycle_traceability"]
    ralph = bundle["ralph_loop_state_v7_lifecycle_traceability"]

    assert runtime_report["candidate_version"] == "7.0.0"
    assert runtime_report["baseline_version"] == "6.0.0"
    assert runtime_report["status"] == "passed"
    assert all(scenario["status"] == "passed" for scenario in runtime_report["scenarios"])
    assert validation_report["artifact_ref"] == runtime_report["runtime_scenario_report_id"]
    assert validation_report["overall_status"] == "passed"
    assert manual_record["subject_ref"] == runtime_report["runtime_scenario_report_id"]
    assert manual_record["related_validation_report_ref"] == validation_report["validation_lane_report_id"]
    assert manual_record["final_approval"] is True
    assert release_readiness["status"] == "ready"
    assert all(check["status"] == "passed" for check in release_readiness["checks"])
    assert release_gate["runtime_scenario_report_ref"] == runtime_report["runtime_scenario_report_id"]
    assert release_gate["release_readiness_ref"] == release_readiness["release_readiness_id"]
    assert release_gate["decision"] == "go"
    assert ralph["target_release"] == "v7_0_0"
    assert ralph["overall_status"] == "ready_for_release"
    assert ralph["validation_report_refs"] == [validation_report["validation_lane_report_id"]]
    assert manual_record["manual_validation_record_id"] in ralph["subject_refs"]
