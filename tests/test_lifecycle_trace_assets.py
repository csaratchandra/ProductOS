from pathlib import Path

import yaml

from conftest import load_json, validator_for


def test_lifecycle_trace_core_examples_validate(root_dir: Path):
    cases = [
        ("item_lifecycle_state.schema.json", root_dir / "core" / "examples" / "artifacts" / "item_lifecycle_state.example.json"),
        ("lifecycle_stage_snapshot.schema.json", root_dir / "core" / "examples" / "artifacts" / "lifecycle_stage_snapshot.example.json"),
    ]
    for schema_name, example_path in cases:
        payload = load_json(example_path)
        errors = sorted(validator_for(schema_name).iter_errors(payload), key=lambda item: list(item.path))
        assert not errors, f"{example_path.name} failed {schema_name}: {[error.message for error in errors]}"


def test_workspace_lifecycle_trace_assets_validate(root_dir: Path):
    artifacts_dir = root_dir / "internal" / "ProductOS-Next" / "artifacts"
    cases = [
        ("research_notebook.schema.json", artifacts_dir / "research_notebook_pm_lifecycle_visibility.example.json"),
        ("segment_map.schema.json", artifacts_dir / "segment_map_pm_lifecycle_visibility.example.json"),
        ("persona_pack.schema.json", artifacts_dir / "persona_pack_pm_lifecycle_visibility.example.json"),
        ("competitor_dossier.schema.json", artifacts_dir / "competitor_dossier_pm_lifecycle_visibility.example.json"),
        ("market_analysis_brief.schema.json", artifacts_dir / "market_analysis_brief_pm_lifecycle_visibility.example.json"),
        ("market_strategy_brief.schema.json", artifacts_dir / "market_strategy_brief_pm_lifecycle_visibility.example.json"),
        ("idea_record.schema.json", artifacts_dir / "idea_record_pm_lifecycle_visibility.json"),
        ("problem_brief.schema.json", artifacts_dir / "problem_brief_pm_lifecycle_visibility.json"),
        ("concept_brief.schema.json", artifacts_dir / "concept_brief_pm_lifecycle_visibility.json"),
        ("prototype_record.schema.json", artifacts_dir / "prototype_record_pm_item_timeline.json"),
        ("ux_design_review.schema.json", artifacts_dir / "ux_design_review_pm_lifecycle_visibility.example.json"),
        ("visual_reasoning_state.schema.json", artifacts_dir / "visual_reasoning_state_pm_lifecycle_visibility.example.json"),
        ("prd.schema.json", artifacts_dir / "prd_pm_lifecycle_visibility.json"),
        ("story_pack.schema.json", artifacts_dir / "story_pack_pm_lifecycle_visibility.json"),
        ("acceptance_criteria_set.schema.json", artifacts_dir / "acceptance_criteria_set_pm_lifecycle_visibility.json"),
        ("validation_lane_report.schema.json", artifacts_dir / "validation_lane_report_pm_lifecycle_visibility.example.json"),
        ("manual_validation_record.schema.json", artifacts_dir / "manual_validation_record_pm_lifecycle_visibility.example.json"),
        ("item_lifecycle_state.schema.json", artifacts_dir / "item_lifecycle_state_pm_lifecycle_visibility.example.json"),
        ("lifecycle_stage_snapshot.schema.json", artifacts_dir / "lifecycle_stage_snapshot_discovery.example.json"),
        ("lifecycle_stage_snapshot.schema.json", artifacts_dir / "lifecycle_stage_snapshot_delivery.example.json"),
        ("lifecycle_stage_snapshot.schema.json", artifacts_dir / "lifecycle_stage_snapshot_full_lifecycle.example.json"),
    ]
    for schema_name, path in cases:
        payload = load_json(path)
        errors = sorted(validator_for(schema_name).iter_errors(payload), key=lambda item: list(item.path))
        assert not errors, f"{path.name} failed {schema_name}: {[error.message for error in errors]}"


def test_mixed_competitor_research_is_present(root_dir: Path):
    artifacts_dir = root_dir / "internal" / "ProductOS-Next" / "artifacts"
    dossier = load_json(artifacts_dir / "competitor_dossier_pm_lifecycle_visibility.example.json")
    snapshot = load_json(artifacts_dir / "lifecycle_stage_snapshot_discovery.example.json")
    full_lifecycle = load_json(artifacts_dir / "lifecycle_stage_snapshot_full_lifecycle.example.json")

    assert {
        "Productboard Spark",
        "Jira Product Discovery",
        "Linear",
        "Aha! Roadmaps",
        "Jira Software",
        "Asana",
        "monday dev",
        "ClickUp",
    } == {competitor["name"] for competitor in dossier["competitors"]}
    assert snapshot["focus_area"] == "discovery"
    assert snapshot["item_count"] == 1
    assert full_lifecycle["focus_area"] == "full_lifecycle"
    assert full_lifecycle["gate_counts"]["passed"] == 10


def test_starter_workspace_seeds_traceable_lifecycle_bundle(root_dir: Path):
    starter = root_dir / "templates"
    required = [
        starter / "docs" / "README.md",
        starter / "docs" / "product" / "product-overview.md",
        starter / "docs" / "discovery" / "discovery-review.md",
        starter / "docs" / "delivery" / "release-readiness-review.md",
        starter / "artifacts" / "research_notebook.json",
        starter / "artifacts" / "segment_map.json",
        starter / "artifacts" / "persona_pack.json",
        starter / "artifacts" / "competitor_dossier.json",
        starter / "artifacts" / "market_analysis_brief.json",
        starter / "artifacts" / "market_strategy_brief.json",
        starter / "artifacts" / "idea_record.json",
        starter / "artifacts" / "problem_brief.json",
        starter / "artifacts" / "concept_brief.json",
        starter / "artifacts" / "prototype_record.json",
        starter / "artifacts" / "prd.json",
        starter / "artifacts" / "story_pack.json",
        starter / "artifacts" / "acceptance_criteria_set.json",
        starter / "artifacts" / "release_readiness.json",
        starter / "artifacts" / "item_lifecycle_state.json",
        starter / "artifacts" / "lifecycle_stage_snapshot.json",
        starter / "artifacts" / "lifecycle_stage_snapshot_delivery.json",
        starter / "artifacts" / "lifecycle_stage_snapshot_full_lifecycle.json",
        starter / "artifacts" / "validation_lane_report.json",
        starter / "artifacts" / "manual_validation_record.json",
    ]
    missing = [path for path in required if not path.exists()]
    assert not missing, f"Missing starter lifecycle assets: {missing}"

    with (starter / "workspace_manifest.yaml").open("r", encoding="utf-8") as handle:
        manifest = yaml.safe_load(handle)

    assert "artifacts/item_lifecycle_state.json" in manifest["artifact_paths"]
    assert "artifacts/lifecycle_stage_snapshot.json" in manifest["artifact_paths"]
    assert "artifacts/story_pack.json" in manifest["artifact_paths"]
    assert "artifacts/release_readiness.json" in manifest["artifact_paths"]
    assert "../../core/workflows/mastery/item-lifecycle-trace-workflow.md" in manifest["workflow_paths"]
