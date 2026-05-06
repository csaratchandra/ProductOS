from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from . import yaml_compat as yaml

ROOT = Path(__file__).resolve().parents[3]
CORE_EXAMPLES_DIR = ROOT / "core" / "examples" / "artifacts"
PRESENTATION_EXAMPLES_DIR = ROOT / "components" / "presentation" / "examples" / "artifacts"
REFERENCE_WORKSPACE_ARTIFACTS_DIR = ROOT / "tests" / "fixtures" / "workspaces" / "productos-sample" / "artifacts"

_STARTER_SUPPORT_ARTIFACT_SOURCES = (
    ("increment_plan.json", CORE_EXAMPLES_DIR / "increment_plan.example.json"),
    ("program_increment_state.example.json", CORE_EXAMPLES_DIR / "program_increment_state.example.json"),
    ("release_readiness.example.json", CORE_EXAMPLES_DIR / "release_readiness.example.json"),
    ("release_gate_decision.example.json", CORE_EXAMPLES_DIR / "release_gate_decision.example.json"),
    ("runtime_adapter_registry.example.json", CORE_EXAMPLES_DIR / "runtime_adapter_registry.example.json"),
    ("execution_session_state.example.json", CORE_EXAMPLES_DIR / "execution_session_state.example.json"),
    ("productos_feedback_log.example.json", CORE_EXAMPLES_DIR / "productos_feedback_log.example.json"),
    ("presentation_brief.example.json", PRESENTATION_EXAMPLES_DIR / "presentation_brief.example.json"),
    ("presentation_sample_record.example.json", CORE_EXAMPLES_DIR / "presentation_sample_record.example.json"),
    ("presentation_pattern_review.example.json", CORE_EXAMPLES_DIR / "presentation_pattern_review.example.json"),
    ("feedback_cluster_state.example.json", CORE_EXAMPLES_DIR / "feedback_cluster_state.example.json"),
    ("gap_cluster_state.example.json", CORE_EXAMPLES_DIR / "gap_cluster_state.example.json"),
    ("improvement_loop_state.example.json", CORE_EXAMPLES_DIR / "improvement_loop_state.example.json"),
    ("pm_benchmark.example.json", CORE_EXAMPLES_DIR / "pm_benchmark.example.json"),
    ("superpower_benchmark.example.json", CORE_EXAMPLES_DIR / "superpower_benchmark.example.json"),
    ("decision_queue.example.json", CORE_EXAMPLES_DIR / "decision_queue.example.json"),
    ("decision_log.example.json", CORE_EXAMPLES_DIR / "decision_log.example.json"),
    ("follow_up_queue.example.json", CORE_EXAMPLES_DIR / "follow_up_queue.example.json"),
    ("status_mail.example.json", CORE_EXAMPLES_DIR / "status_mail.example.json"),
    ("issue_log.example.json", CORE_EXAMPLES_DIR / "issue_log.example.json"),
    (
        "runtime_scenario_report_adapter_parity.example.json",
        REFERENCE_WORKSPACE_ARTIFACTS_DIR / "runtime_scenario_report_adapter_parity.example.json",
    ),
    (
        "runtime_scenario_report_market_refresh.example.json",
        REFERENCE_WORKSPACE_ARTIFACTS_DIR / "runtime_scenario_report_market_refresh.example.json",
    ),
    (
        "runtime_scenario_report_market_distribution.example.json",
        REFERENCE_WORKSPACE_ARTIFACTS_DIR / "runtime_scenario_report_market_distribution.example.json",
    ),
    ("document_sync_state_live_docs.example.json", REFERENCE_WORKSPACE_ARTIFACTS_DIR / "document_sync_state_live_docs.example.json"),
    (
        "validation_lane_report_next_version_completion.example.json",
        REFERENCE_WORKSPACE_ARTIFACTS_DIR / "validation_lane_report_next_version_completion.example.json",
    ),
    (
        "manual_validation_record_next_version_completion.example.json",
        REFERENCE_WORKSPACE_ARTIFACTS_DIR / "manual_validation_record_next_version_completion.example.json",
    ),
    (
        "release_gate_decision_next_version_completion.example.json",
        REFERENCE_WORKSPACE_ARTIFACTS_DIR / "release_gate_decision_next_version_completion.example.json",
    ),
    (
        "research_notebook_agentic_market_intelligence.example.json",
        REFERENCE_WORKSPACE_ARTIFACTS_DIR / "research_notebook_agentic_market_intelligence.example.json",
    ),
    (
        "landscape_matrix_agentic_market_intelligence.example.json",
        REFERENCE_WORKSPACE_ARTIFACTS_DIR / "landscape_matrix_agentic_market_intelligence.example.json",
    ),
    (
        "competitor_dossier_agentic_market_intelligence.example.json",
        REFERENCE_WORKSPACE_ARTIFACTS_DIR / "competitor_dossier_agentic_market_intelligence.example.json",
    ),
    (
        "market_analysis_brief_agentic_market_intelligence.example.json",
        REFERENCE_WORKSPACE_ARTIFACTS_DIR / "market_analysis_brief_agentic_market_intelligence.example.json",
    ),
    (
        "research_feature_recommendation_brief.example.json",
        REFERENCE_WORKSPACE_ARTIFACTS_DIR / "research_feature_recommendation_brief.example.json",
    ),
    ("ralph_loop_state.example.json", REFERENCE_WORKSPACE_ARTIFACTS_DIR / "ralph_loop_state.example.json"),
    (
        "validation_lane_report_market_intelligence.example.json",
        REFERENCE_WORKSPACE_ARTIFACTS_DIR / "validation_lane_report_market_intelligence.example.json",
    ),
    (
        "manual_validation_record_market_intelligence.example.json",
        REFERENCE_WORKSPACE_ARTIFACTS_DIR / "manual_validation_record_market_intelligence.example.json",
    ),
    (
        "rejected_path_record_market_intelligence.example.json",
        REFERENCE_WORKSPACE_ARTIFACTS_DIR / "rejected_path_record_market_intelligence.example.json",
    ),
    (
        "leadership_review_market_intelligence_distribution.example.json",
        REFERENCE_WORKSPACE_ARTIFACTS_DIR / "leadership_review_market_intelligence_distribution.example.json",
    ),
    (
        "portfolio_update_market_intelligence_distribution.example.json",
        REFERENCE_WORKSPACE_ARTIFACTS_DIR / "portfolio_update_market_intelligence_distribution.example.json",
    ),
    (
        "source_note_card_productboard_spark_official_2026.example.json",
        REFERENCE_WORKSPACE_ARTIFACTS_DIR / "source_note_card_productboard_spark_official_2026.example.json",
    ),
    (
        "source_note_card_jpd_ai_official_2026.example.json",
        REFERENCE_WORKSPACE_ARTIFACTS_DIR / "source_note_card_jpd_ai_official_2026.example.json",
    ),
    (
        "source_note_card_aha_knowledge_ai_official_2026.example.json",
        REFERENCE_WORKSPACE_ARTIFACTS_DIR / "source_note_card_aha_knowledge_ai_official_2026.example.json",
    ),
    (
        "source_note_card_linear_asks_official_2026.example.json",
        REFERENCE_WORKSPACE_ARTIFACTS_DIR / "source_note_card_linear_asks_official_2026.example.json",
    ),
    (
        "source_note_card_notion_mcp_official_2026.example.json",
        REFERENCE_WORKSPACE_ARTIFACTS_DIR / "source_note_card_notion_mcp_official_2026.example.json",
    ),
    (
        "source_note_card_coda_ai_official_2026.example.json",
        REFERENCE_WORKSPACE_ARTIFACTS_DIR / "source_note_card_coda_ai_official_2026.example.json",
    ),
    (
        "source_note_card_asana_ai_teammates_official_2026.example.json",
        REFERENCE_WORKSPACE_ARTIFACTS_DIR / "source_note_card_asana_ai_teammates_official_2026.example.json",
    ),
    (
        "source_note_card_openai_deep_research_official_2026.example.json",
        REFERENCE_WORKSPACE_ARTIFACTS_DIR / "source_note_card_openai_deep_research_official_2026.example.json",
    ),
    (
        "source_note_card_gemini_deep_research_official_2026.example.json",
        REFERENCE_WORKSPACE_ARTIFACTS_DIR / "source_note_card_gemini_deep_research_official_2026.example.json",
    ),
    (
        "source_note_card_perplexity_deep_research_official_2026.example.json",
        REFERENCE_WORKSPACE_ARTIFACTS_DIR / "source_note_card_perplexity_deep_research_official_2026.example.json",
    ),
    (
        "source_note_card_glean_agentic_engine_official_2026.example.json",
        REFERENCE_WORKSPACE_ARTIFACTS_DIR / "source_note_card_glean_agentic_engine_official_2026.example.json",
    ),
    (
        "source_note_card_crayon_ci_official_2026.example.json",
        REFERENCE_WORKSPACE_ARTIFACTS_DIR / "source_note_card_crayon_ci_official_2026.example.json",
    ),
    (
        "source_note_card_klue_compete_agent_official_2026.example.json",
        REFERENCE_WORKSPACE_ARTIFACTS_DIR / "source_note_card_klue_compete_agent_official_2026.example.json",
    ),
    (
        "source_note_card_semrush_eyeon_official_2026.example.json",
        REFERENCE_WORKSPACE_ARTIFACTS_DIR / "source_note_card_semrush_eyeon_official_2026.example.json",
    ),
    (
        "source_note_card_app_review_jpd.example.json",
        CORE_EXAMPLES_DIR / "source_note_card_app_review_jpd.example.json",
    ),
    (
        "source_note_card_consultant_ai_pm.example.json",
        CORE_EXAMPLES_DIR / "source_note_card.example.json",
    ),
)


LIFECYCLE_STAGE_ORDER = [
    "signal_intake",
    "research_synthesis",
    "segmentation_and_personas",
    "problem_framing",
    "concept_shaping",
    "prototype_validation",
    "prd_handoff",
    "story_planning",
    "acceptance_ready",
    "release_readiness",
    "launch_preparation",
    "outcome_review",
]

DISCOVERY_STAGE_ORDER = [
    "signal_intake",
    "research_synthesis",
    "segmentation_and_personas",
    "problem_framing",
    "concept_shaping",
    "prototype_validation",
    "prd_handoff",
]


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def _seed_starter_support_artifacts(destination: Path, manifest: dict[str, Any]) -> None:
    artifacts_dir = destination / "artifacts"
    artifact_paths = manifest.setdefault("artifact_paths", [])
    existing_paths = set(artifact_paths)
    for filename, source_path in _STARTER_SUPPORT_ARTIFACT_SOURCES:
        target_path = artifacts_dir / filename
        if not target_path.exists():
            shutil.copy2(source_path, target_path)
        relative_path = f"artifacts/{filename}"
        if relative_path not in existing_paths:
            artifact_paths.append(relative_path)
            existing_paths.add(relative_path)


def _workspace_artifacts_dir(workspace_dir: Path | str) -> Path:
    return Path(workspace_dir).resolve() / "artifacts"


def _find_matching_artifacts(artifacts_dir: Path, prefix: str) -> list[Path]:
    return sorted(
        {
            *artifacts_dir.glob(f"{prefix}*.json"),
            *artifacts_dir.glob(f"{prefix}*.example.json"),
        }
    )


def load_item_lifecycle_state_from_workspace(
    workspace_dir: Path | str,
    *,
    item_id: str | None = None,
) -> dict[str, Any]:
    artifacts_dir = _workspace_artifacts_dir(workspace_dir)
    candidates = _find_matching_artifacts(artifacts_dir, "item_lifecycle_state")
    if not candidates:
        raise FileNotFoundError(f"No item lifecycle state artifacts found under {artifacts_dir}")

    payloads = [_load_json(path) for path in candidates]
    if item_id is None:
        if len(payloads) == 1:
            return payloads[0]
        raise ValueError("Multiple item lifecycle state artifacts found; provide --item-id.")

    for payload in payloads:
        item_ref = payload.get("item_ref", {})
        if item_id in {
            payload.get("item_lifecycle_state_id"),
            payload.get("title"),
            item_ref.get("entity_id"),
        }:
            return payload

    raise KeyError(f"No item lifecycle state found for item id {item_id}")


def load_all_item_lifecycle_states_from_workspace(workspace_dir: Path | str) -> list[dict[str, Any]]:
    artifacts_dir = _workspace_artifacts_dir(workspace_dir)
    candidates = _find_matching_artifacts(artifacts_dir, "item_lifecycle_state")
    if not candidates:
        raise FileNotFoundError(f"No item lifecycle state artifacts found under {artifacts_dir}")

    payloads = [_load_json(path) for path in candidates]
    return sorted(payloads, key=lambda payload: (payload.get("current_stage", ""), payload.get("title", ""), payload["item_ref"]["entity_id"]))


def load_lifecycle_stage_snapshot_from_workspace(
    workspace_dir: Path | str,
    *,
    focus_area: str = "discovery",
) -> dict[str, Any]:
    artifacts_dir = _workspace_artifacts_dir(workspace_dir)
    candidates = _find_matching_artifacts(artifacts_dir, "lifecycle_stage_snapshot")
    if not candidates:
        raise FileNotFoundError(f"No lifecycle stage snapshot artifacts found under {artifacts_dir}")

    for path in candidates:
        payload = _load_json(path)
        if payload.get("focus_area") == focus_area:
            return payload

    raise KeyError(f"No lifecycle stage snapshot found for focus area {focus_area}")


def format_item_lifecycle_state(payload: dict[str, Any]) -> str:
    item_ref = payload["item_ref"]
    segments = ", ".join(ref["entity_id"] for ref in payload["target_segment_refs"])
    personas = ", ".join(ref["entity_id"] for ref in payload["target_persona_refs"])
    lines = [
        f"Item: {payload['title']}",
        f"Trace Unit: {item_ref['entity_type']}:{item_ref['entity_id']}",
        f"Current Stage: {payload['current_stage']}",
        f"Overall Status: {payload['overall_status']}",
        f"Segments: {segments}",
        f"Personas: {personas}",
        "Timeline:",
    ]
    for stage in payload["lifecycle_stages"]:
        artifact_summary = ", ".join(stage["artifact_ids"]) if stage["artifact_ids"] else "none"
        lines.append(
            f"- {stage['stage_key']}: {stage['status']} "
            f"(gate: {stage['gate_status']}, artifacts: {artifact_summary})"
        )
    if payload["pending_questions"]:
        lines.append("Pending Questions:")
        for question in payload["pending_questions"]:
            lines.append(f"- {question}")
    if payload["blocked_reasons"]:
        lines.append("Blocked Reasons:")
        for reason in payload["blocked_reasons"]:
            lines.append(f"- {reason}")
    return "\n".join(lines)


def format_lifecycle_stage_snapshot(payload: dict[str, Any]) -> str:
    lines = [
        f"Focus Area: {payload['focus_area']}",
        f"Summary: {payload['snapshot_summary']}",
        f"Items: {payload['item_count']}",
        f"Segments: {payload['segment_count']}",
        f"Personas: {payload['persona_count']}",
        (
            "Gate Counts: "
            f"passed={payload['gate_counts']['passed']}, "
            f"pending={payload['gate_counts']['pending']}, "
            f"blocked={payload['gate_counts']['blocked']}, "
            f"not_started={payload['gate_counts']['not_started']}"
        ),
        "Stage Details:",
    ]
    for summary in payload["stage_summaries"]:
        lines.append(
            f"- {summary['stage_key']}: items={len(summary['item_ids'])}, "
            f"gate_passed={summary['gate_status_counts']['passed']}, "
            f"gate_pending={summary['gate_status_counts']['pending']}, "
            f"gate_blocked={summary['gate_status_counts']['blocked']}"
        )
    return "\n".join(lines)


def init_workspace_from_template(
    root_dir: Path | str,
    *,
    template_name: str | None = None,
    dest: Path | str,
    workspace_id: str,
    name: str,
    mode: str,
) -> Path:
    root = Path(root_dir).resolve()
    if template_name not in (None, "templates"):
        raise ValueError(f"Unsupported workspace template: {template_name}")

    template_dir = root / "templates"
    destination = Path(dest).resolve()

    if not template_dir.exists():
        raise FileNotFoundError(f"Workspace template does not exist: {template_dir}")
    if destination.exists():
        raise FileExistsError(f"Destination already exists: {destination}")

    shutil.copytree(template_dir, destination, ignore=shutil.ignore_patterns(".DS_Store"))

    manifest_path = destination / "workspace_manifest.yaml"
    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = yaml.safe_load(handle)
    manifest["workspace_id"] = workspace_id
    manifest["name"] = name
    manifest["mode"] = mode
    if manifest.get("active_increment_id") == "pi_YYYY_qX_01":
        manifest["active_increment_id"] = "pi_initial_01"
    _seed_starter_support_artifacts(destination, manifest)
    with manifest_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(manifest, handle, sort_keys=False)

    for path in destination.rglob("*.json"):
        payload = _load_json(path)
        if "workspace_id" in payload:
            payload["workspace_id"] = workspace_id
        _write_json(path, payload)

    replacements = {
        "ProductOS Starter Workspace": name,
        "ws_product_starter": workspace_id,
    }
    for path in destination.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for source, target in replacements.items():
            text = text.replace(source, target)
        path.write_text(text, encoding="utf-8")

    return destination
