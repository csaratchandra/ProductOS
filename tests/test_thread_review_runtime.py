import json
from pathlib import Path
import shutil

from core.python.productos_runtime import (
    build_thread_review_bundle_from_workspace,
    build_thread_review_release_bundle_from_workspace,
    write_thread_review_index_site,
    write_thread_review_package,
    build_workspace_adoption_bundle_from_source,
)


def _section(bundle: dict, section_id: str) -> dict:
    return next(section for section in bundle["sections"] if section["section_id"] == section_id)


def test_thread_review_bundle_uses_artifact_backing(bundled_workspace_dir: Path):
    bundle = build_thread_review_bundle_from_workspace(
        bundled_workspace_dir,
        item_id="opp_pm_lifecycle_traceability",
        generated_at="2026-04-09T10:00:00Z",
    )

    assert bundle["review_status"] == "stable_full_lifecycle"
    assert bundle["action_items"]
    assert _section(bundle, "market_context")["backing_mode"] == "artifact_backed"
    assert _section(bundle, "prototype")["backing_mode"] == "artifact_backed"
    assert _section(bundle, "delivery")["backing_mode"] == "artifact_backed"
    assert _section(bundle, "release_readiness")["backing_mode"] == "artifact_backed"
    assert _section(bundle, "launch")["backing_mode"] == "artifact_backed"
    assert _section(bundle, "outcome_review")["backing_mode"] == "artifact_backed"


def test_adoption_thread_review_bundle_marks_fallback_and_deferred_sections(root_dir: Path, adoption_workspace_dir: Path):
    bundle = build_workspace_adoption_bundle_from_source(
        root_dir,
        source_dir=adoption_workspace_dir,
        workspace_id="ws_adoption_workspace",
        name="Adoption Workspace",
        generated_at="2026-04-09T10:00:00Z",
    )["thread_review_bundle"]

    assert bundle["review_status"] == "pm_review_required"
    assert bundle["action_items"]
    assert bundle["recommended_next_step"] == bundle["action_items"][0]["title"]
    assert _section(bundle, "problem")["backing_mode"] == "artifact_backed"
    assert _section(bundle, "market_context")["backing_mode"] == "artifact_backed"
    assert _section(bundle, "prototype")["backing_mode"] == "lifecycle_fallback"
    assert _section(bundle, "delivery")["backing_mode"] == "deferred"
    assert _section(bundle, "release_readiness")["backing_mode"] == "deferred"
    assert _section(bundle, "launch")["backing_mode"] == "deferred"
    assert _section(bundle, "outcome_review")["backing_mode"] == "deferred"


def test_thread_review_package_writes_markdown_and_presentation_outputs(
    bundled_workspace_dir: Path,
    tmp_path: Path,
):
    bundle = build_thread_review_bundle_from_workspace(
        bundled_workspace_dir,
        item_id="opp_pm_lifecycle_traceability",
        generated_at="2026-04-09T10:00:00Z",
    )

    output_paths = write_thread_review_package(bundle, tmp_path / "thread-package")

    assert output_paths["thread_review_html"].exists()
    assert output_paths["thread_review_markdown"].exists()
    assert output_paths["presentation_brief"].exists()
    assert output_paths["presentation_story"].exists()
    assert output_paths["presentation_html"].exists()
    assert output_paths["workflow_corridor_spec"].exists()
    assert output_paths["corridor_publish_check"].exists()
    assert output_paths["corridor_html"].exists()
    assert "## Review Actions" in output_paths["thread_review_markdown"].read_text(encoding="utf-8")
    presentation_brief = json.loads(output_paths["presentation_brief"].read_text(encoding="utf-8"))
    workflow_corridor_spec = json.loads(output_paths["workflow_corridor_spec"].read_text(encoding="utf-8"))
    assert presentation_brief["presentation_brief_id"].endswith("_thread_review")
    assert presentation_brief["slide_outlines"][0]["title"] == "Decision Now"
    assert workflow_corridor_spec["publication_mode"] == "internal_review"
    assert workflow_corridor_spec["customer_safe"] is False


def test_thread_review_index_site_generates_item_pages(
    bundled_workspace_dir: Path,
    tmp_path: Path,
):
    workspace_copy = tmp_path / "workspace-copy"
    shutil.copytree(bundled_workspace_dir, workspace_copy)
    artifacts_dir = workspace_copy / "artifacts"
    source_path = artifacts_dir / "item_lifecycle_state_pm_lifecycle_visibility.example.json"
    payload = json.loads(source_path.read_text(encoding="utf-8"))
    payload["item_lifecycle_state_id"] = "item_lifecycle_state_pm_release_lane"
    payload["item_ref"]["entity_id"] = "opp_pm_release_lane"
    payload["title"] = "Release lane and launch alignment"
    payload["current_stage"] = "launch_preparation"
    payload["overall_status"] = "active_delivery"
    duplicated_path = artifacts_dir / "item_lifecycle_state_pm_release_lane.json"
    duplicated_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    site = write_thread_review_index_site(
        workspace_copy,
        tmp_path / "thread-index",
        generated_at="2026-04-09T10:00:00Z",
    )

    assert site["thread_count"] == 2
    index_html = site["index_path"].read_text(encoding="utf-8")
    assert "Lifecycle traceability and stage visibility for PM work" in index_html
    assert "Release lane and launch alignment" in index_html
    assert "threads/opp_pm_release_lane/thread-review.html" in index_html


def test_thread_review_release_bundle_stays_bounded_for_external_claim(
    bundled_workspace_dir: Path,
    tmp_path: Path,
):
    result = build_thread_review_release_bundle_from_workspace(
        bundled_workspace_dir,
        item_id="opp_pm_lifecycle_traceability",
        generated_at="2026-04-09T10:00:00Z",
        output_dir=tmp_path / "thread-release-check",
    )

    release_gate = result["release_bundle"]["release_gate_decision_thread_review_release"]
    validation = result["release_bundle"]["validation_lane_report_thread_review_release"]
    release_readiness = result["release_bundle"]["release_readiness_thread_review_release"]

    assert validation["overall_status"] == "ready_for_manual_validation"
    assert release_readiness["status"] == "watch"
    assert release_gate["decision"] == "conditional_go"
    assert (tmp_path / "thread-release-check" / "release" / "release_gate_decision_thread_review_release.json").exists()
