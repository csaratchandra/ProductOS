from pathlib import Path

from conftest import load_json, validator_for


SPECIAL_EXAMPLES = {
    "artifact_trace_map.schema.json": Path("core/examples/traces/status_mail.trace_map.example.json"),
    "release_metadata.schema.json": Path("core/examples/registry/release_metadata.example.json"),
    "suite_registration.schema.json": Path("core/examples/registry/suite_registration.example.json"),
    "workspace_registration.schema.json": Path("core/examples/registry/workspace_registration.example.json"),
    "workflow_state.schema.json": Path("core/examples/workflows/biweekly_status_mail.workflow_state.example.json"),
}


INVALID_FIXTURES = [
    ("status_mail.schema.json", "status_mail_missing_next_steps.json", "next_steps"),
    ("meeting_record.schema.json", "meeting_record_missing_action_owner.json", "action_items.0"),
    ("decision_log.schema.json", "decision_log_missing_sources.json", "decisions.0"),
    ("pm_superpower_benchmark.schema.json", "pm_superpower_benchmark_missing_success_thresholds.json", "golden_loop_scores.0"),
    ("persona_operating_profile.schema.json", "persona_operating_profile_missing_review_path.json", "profiles.0"),
    ("validation_lane_report.schema.json", "validation_lane_report_missing_checks_run.json", "ai_tester_lane"),
    (
        "research_feature_recommendation_brief.schema.json",
        "research_feature_recommendation_brief_missing_evidence_refs.json",
        "recommendations.0",
    ),
    (
        "ralph_loop_state.schema.json",
        "ralph_loop_state_invalid_stage_key.json",
        "stages.0.stage_key",
    ),
]


def example_path_for(schema_name: str, root_dir: Path, example_dir: Path) -> Path:
    if schema_name in SPECIAL_EXAMPLES:
        return root_dir / SPECIAL_EXAMPLES[schema_name]
    return example_dir / schema_name.replace(".schema.json", ".example.json")


def test_valid_examples_match_schemas(root_dir: Path, schema_dir: Path, example_dir: Path):
    for schema_path in sorted(schema_dir.glob("*.schema.json")):
        example_path = example_path_for(schema_path.name, root_dir, example_dir)
        assert example_path.exists(), f"Missing example for {schema_path.name}"

        validator = validator_for(schema_path.name)
        payload = load_json(example_path)
        errors = sorted(validator.iter_errors(payload), key=lambda item: list(item.path))
        assert not errors, f"{example_path.name} failed {schema_path.name}: {[error.message for error in errors]}"


def test_invalid_fixtures_fail_validation(root_dir: Path):
    invalid_dir = root_dir / "tests" / "fixtures" / "invalid"

    for schema_name, fixture_name, expected_path_prefix in INVALID_FIXTURES:
        validator = validator_for(schema_name)
        payload = load_json(invalid_dir / fixture_name)
        errors = sorted(validator.iter_errors(payload), key=lambda item: list(item.path))

        assert errors, f"{fixture_name} unexpectedly passed {schema_name}"

        error_paths = {".".join(str(part) for part in error.absolute_path) or "<root>" for error in errors}
        assert any(
            path.startswith(expected_path_prefix) or path == "<root>" for path in error_paths
        ), f"{fixture_name} failed for unexpected paths: {sorted(error_paths)}"
