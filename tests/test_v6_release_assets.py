from pathlib import Path

from conftest import latest_release, load_json, validator_for


def test_v6_release_artifacts_validate(root_dir: Path):
    artifacts_dir = root_dir / "workspaces" / "productos-v2" / "artifacts"
    cases = [
        ("runtime_scenario_report.schema.json", artifacts_dir / "runtime_scenario_report_v6_lifecycle_traceability.json"),
        ("validation_lane_report.schema.json", artifacts_dir / "validation_lane_report_v6_lifecycle_traceability.json"),
        ("manual_validation_record.schema.json", artifacts_dir / "manual_validation_record_v6_lifecycle_traceability.json"),
        ("release_readiness.schema.json", artifacts_dir / "release_readiness_v6_lifecycle_traceability.json"),
        ("release_gate_decision.schema.json", artifacts_dir / "release_gate_decision_v6_lifecycle_traceability.json"),
        ("ralph_loop_state.schema.json", artifacts_dir / "ralph_loop_state_v6_lifecycle_traceability.json"),
    ]

    for schema_name, path in cases:
        payload = load_json(path)
        errors = sorted(validator_for(schema_name).iter_errors(payload), key=lambda item: list(item.path))
        assert not errors, f"{path.name} failed {schema_name}: {[error.message for error in errors]}"


def test_v6_release_surfaces_are_current(root_dir: Path):
    release = latest_release(root_dir)
    workspace_registration = load_json(root_dir / "registry" / "workspaces" / "ws_productos_v2.registration.json")
    suite_registration = load_json(root_dir / "registry" / "suites" / "suite_productos.registration.json")
    readme = (root_dir / "README.md").read_text(encoding="utf-8")
    overview = (root_dir / "workspaces" / "productos-v2" / "docs" / "product" / "product-overview.md").read_text(encoding="utf-8")

    assert release["core_version"] == "6.0.0"
    assert release["summary"] == "ProductOS V6.0.0 is the stable release for lifecycle-traceability through release_readiness slice."
    assert workspace_registration["current_core_version"] == "6.0.0"
    assert suite_registration["current_core_version"] == "6.0.0"
    assert "ProductOS V6.0.0 is the current stable ProductOS Core line." in readme
    assert "active core line is now `6.0.0`" in readme
    assert "ProductOS `V6.0.0`" in overview
    assert "lifecycle traceability through `release_readiness`" in overview
