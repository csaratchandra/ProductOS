from __future__ import annotations

import copy
import json
import shutil
from collections import Counter
from html import escape
from pathlib import Path
from typing import Any

from . import yaml_compat as yaml

from .lifecycle import (
    DISCOVERY_STAGE_ORDER,
    LIFECYCLE_STAGE_ORDER,
    init_workspace_from_template,
    load_all_item_lifecycle_states_from_workspace,
    load_item_lifecycle_state_from_workspace,
)
from components.presentation.python.productos_presentation import (
    build_evidence_pack,
    build_presentation_story,
    build_publish_check,
    build_ppt_export_plan,
    build_render_spec,
    build_slide_spec,
    write_html_presentation,
)


ADOPTION_ARTIFACT_SCHEMAS = {
    "workspace_adoption_report": "workspace_adoption_report.schema.json",
    "adoption_review_queue": "adoption_review_queue.schema.json",
    "intake_routing_state": "intake_routing_state.schema.json",
    "source_note_card_executive_brief": "source_note_card.schema.json",
    "source_note_card_self_analysis": "source_note_card.schema.json",
    "source_note_card_segment_map": "source_note_card.schema.json",
    "source_note_card_persona_pack": "source_note_card.schema.json",
    "source_note_card_pilot_proposal": "source_note_card.schema.json",
    "research_notebook": "research_notebook.schema.json",
    "research_brief": "research_brief.schema.json",
    "idea_record": "idea_record.schema.json",
    "problem_brief": "problem_brief.schema.json",
    "concept_brief": "concept_brief.schema.json",
    "segment_map": "segment_map.schema.json",
    "persona_pack": "persona_pack.schema.json",
    "prd": "prd.schema.json",
    "item_lifecycle_state": "item_lifecycle_state.schema.json",
    "thread_review_bundle": "thread_review_bundle.schema.json",
    "lifecycle_stage_snapshot": "lifecycle_stage_snapshot.schema.json",
    "lifecycle_stage_snapshot_delivery": "lifecycle_stage_snapshot.schema.json",
    "lifecycle_stage_snapshot_launch": "lifecycle_stage_snapshot.schema.json",
    "lifecycle_stage_snapshot_outcomes": "lifecycle_stage_snapshot.schema.json",
    "lifecycle_stage_snapshot_full_lifecycle": "lifecycle_stage_snapshot.schema.json",
}
THREAD_REVIEW_RELEASE_ARTIFACT_SCHEMAS = {
    "runtime_scenario_report_thread_review_release": "runtime_scenario_report.schema.json",
    "validation_lane_report_thread_review_release": "validation_lane_report.schema.json",
    "manual_validation_record_thread_review_release": "manual_validation_record.schema.json",
    "release_readiness_thread_review_release": "release_readiness.schema.json",
    "release_gate_decision_thread_review_release": "release_gate_decision.schema.json",
}

_FOCUS_STAGE_KEYS = {
    "discovery": DISCOVERY_STAGE_ORDER,
    "delivery": ["story_planning", "acceptance_ready", "release_readiness"],
    "launch": ["launch_preparation"],
    "outcomes": ["outcome_review"],
    "full_lifecycle": LIFECYCLE_STAGE_ORDER,
}

_RUNTIME_SUPPORT_ARTIFACTS = [
    "increment_plan.json",
    "decision_queue.example.json",
    "decision_log.example.json",
    "follow_up_queue.example.json",
    "status_mail.example.json",
    "issue_log.example.json",
    "release_readiness.example.json",
    "release_gate_decision.example.json",
    "runtime_adapter_registry.example.json",
    "execution_session_state.example.json",
    "productos_feedback_log.example.json",
    "presentation_brief.example.json",
    "presentation_sample_record.example.json",
    "presentation_pattern_review.example.json",
    "feedback_cluster_state.example.json",
    "gap_cluster_state.example.json",
    "improvement_loop_state.example.json",
    "pm_benchmark.example.json",
    "superpower_benchmark.example.json",
    "research_notebook_agentic_market_intelligence.example.json",
    "landscape_matrix_agentic_market_intelligence.example.json",
    "competitor_dossier_agentic_market_intelligence.example.json",
    "market_analysis_brief_agentic_market_intelligence.example.json",
    "research_feature_recommendation_brief.example.json",
    "ralph_loop_state.example.json",
    "validation_lane_report_market_intelligence.example.json",
    "manual_validation_record_market_intelligence.example.json",
    "rejected_path_record_market_intelligence.example.json",
    "leadership_review_market_intelligence_distribution.example.json",
    "portfolio_update_market_intelligence_distribution.example.json",
    "runtime_scenario_report_market_distribution.example.json",
    "document_sync_state_live_docs.example.json",
    "runtime_scenario_report_adapter_parity.example.json",
    "runtime_scenario_report_market_refresh.example.json",
    "validation_lane_report_next_version_completion.example.json",
    "manual_validation_record_next_version_completion.example.json",
    "release_gate_decision_next_version_completion.example.json",
]


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def _rewrite_workspace_ids(payload: Any, workspace_id: str) -> Any:
    if isinstance(payload, dict):
        return {key: (workspace_id if key == "workspace_id" else _rewrite_workspace_ids(value, workspace_id)) for key, value in payload.items()}
    if isinstance(payload, list):
        return [_rewrite_workspace_ids(item, workspace_id) for item in payload]
    return payload


def _slug(value: str) -> str:
    normalized = "".join(char.lower() if char.isalnum() else "_" for char in value)
    while "__" in normalized:
        normalized = normalized.replace("__", "_")
    return normalized.strip("_")


def _relative_path(path: Path, base: Path) -> str:
    return path.resolve().relative_to(base.resolve()).as_posix()


def _nested_workspace_roots(source_dir: Path) -> list[Path]:
    roots: list[Path] = []
    for manifest_path in sorted(source_dir.rglob("workspace_manifest.yaml")):
        workspace_root = manifest_path.parent
        if workspace_root == source_dir:
            continue
        roots.append(workspace_root)
    return roots


def _visible_files(source_dir: Path) -> list[Path]:
    files: list[Path] = []
    nested_workspace_roots = _nested_workspace_roots(source_dir)
    for path in sorted(source_dir.rglob("*")):
        if not path.is_file():
            continue
        if any(part.startswith(".") for part in path.relative_to(source_dir).parts):
            continue
        if any(root in path.parents for root in nested_workspace_roots):
            continue
        files.append(path)
    return files


def _classify_file(source_dir: Path, path: Path) -> dict[str, Any]:
    relative = path.relative_to(source_dir)
    suffix = path.suffix.lower()
    name = path.name.lower()
    path_text = relative.as_posix().lower()

    classification = "workspace_note"
    input_type = "raw_note"
    inbox_lane = "raw-notes"
    recommended_workflow_ids = ["wf_inbox_to_normalized_evidence"]
    derived_artifact_ids = ["idea_record_codesync_workspace_adoption"]

    if "research" in path_text and suffix in {".md", ".html"}:
        classification = "research_note"
        input_type = "document" if suffix == ".html" else "raw_note"
        inbox_lane = "documents" if suffix == ".html" else "raw-notes"
        recommended_workflow_ids = [
            "wf_inbox_to_normalized_evidence",
            "wf_research_command_center",
            "wf_problem_brief_to_prd",
        ]
        derived_artifact_ids = [
            "research_notebook_codesync_workspace_adoption",
            "research_brief_codesync_workspace_adoption",
            "problem_brief_codesync_workspace_adoption",
        ]
    elif suffix in {".png", ".jpg", ".jpeg", ".gif", ".svg"}:
        classification = "visual_asset"
        input_type = "screenshot"
        inbox_lane = "screenshots"
        recommended_workflow_ids = ["wf_inbox_to_normalized_evidence", "wf_artifact_to_readable_doc"]
        derived_artifact_ids = ["concept_brief_codesync_workspace_adoption", "prd_codesync_workspace_adoption"]
    elif suffix in {".html", ".pdf"}:
        classification = "presentation_or_document"
        input_type = "document"
        inbox_lane = "documents"
        recommended_workflow_ids = ["wf_inbox_to_normalized_evidence", "wf_artifact_to_readable_doc"]
        derived_artifact_ids = ["concept_brief_codesync_workspace_adoption", "prd_codesync_workspace_adoption"]
    elif suffix in {".txt"} or "transcript" in name:
        classification = "transcript_or_session_note"
        input_type = "transcript"
        inbox_lane = "transcripts"
        recommended_workflow_ids = ["wf_inbox_to_normalized_evidence", "wf_problem_brief_to_prd"]
        derived_artifact_ids = ["problem_brief_codesync_workspace_adoption", "prd_codesync_workspace_adoption"]

    return {
        "path": path,
        "relative_path": relative.as_posix(),
        "classification": classification,
        "input_type": input_type,
        "inbox_lane": inbox_lane,
        "recommended_workflow_ids": recommended_workflow_ids,
        "derived_artifact_ids": derived_artifact_ids,
    }


def _read_or_empty(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _clip_sentence(text: str, limit: int) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def _infer_codesync_context(source_dir: Path) -> dict[str, str]:
    executive_brief = _read_or_empty(source_dir / "Notes" / "research" / "01-executive-brief.md")
    self_analysis = _read_or_empty(source_dir / "Notes" / "research" / "02-codesync-self-analysis.md")
    segment_map = _read_or_empty(source_dir / "Notes" / "research" / "05-segment-map.md")
    persona_pack = _read_or_empty(source_dir / "Notes" / "research" / "06-persona-pack.md")
    pilot = _read_or_empty(source_dir / "Notes" / "research" / "16-customer-pilot-proposal.md")

    wedge = (
        "Governed workflow control for ambulatory patient access, billing execution, denial prevention, "
        "and value-based care coordination without replacing incumbent systems."
    )
    if "operating layer" in executive_brief.lower():
        wedge = (
            "Operating layer for physician-led IPAs and multi-site ambulatory groups that need to unify patient "
            "access, billing execution, denial prevention, post-acute transitions, and value-based workflows."
        )

    best_beachhead = (
        "Physician-led, multi-site primary care or internal medicine groups with central billing, "
        "meaningful Medicare Advantage exposure, and visible post-acute or chronic-care burden."
    )
    if "best beachhead" in segment_map.lower():
        best_beachhead = (
            "Physician-led multi-site primary care or internal medicine groups with central billing, fragmented "
            "workflows, meaningful Medicare Advantage exposure, and a visible post-acute or chronic-care burden."
        )

    launch_lane = "Eligibility verification and prior authorization control."
    if "primary pilot lane" in pilot.lower():
        launch_lane = "Eligibility verification and prior authorization control as the initial governed launch lane."

    proof_gap = (
        "Public positioning implies large outcomes, but external proof, quantified before-after evidence, "
        "and implementation evidence remain incomplete."
    )
    if "proof risk" in self_analysis.lower():
        proof_gap = (
            "The research pack is strategically coherent, but proof gaps remain around customer case studies, "
            "implementation proof, auditability, security posture, and quantified outcomes."
        )

    return {
        "wedge": wedge,
        "best_beachhead": best_beachhead,
        "launch_lane": launch_lane,
        "proof_gap": proof_gap,
        "persona_signal": "Executives want ROI and visibility, RCM leaders want queue control, and front-office teams want fewer handoff failures.",
        "source_summary": "CodeSync exists today as a strong research pack and pilot narrative, but not as first-class ProductOS operating state.",
        "pilot_summary": "The current proposal is a controlled 90-day pilot proving one workflow lane first, then one adjacent expansion lane after evidence.",
    }


def _build_source_note_cards(
    *,
    source_dir: Path,
    workspace_id: str,
    product_slug: str,
    generated_at: str,
    opportunity_id: str,
    feature_id: str,
) -> dict[str, dict[str, Any]]:
    note_specs = [
        {
            "bundle_key": "source_note_card_executive_brief",
            "artifact_id": f"source_note_card_{product_slug}_executive_brief",
            "path": source_dir / "Notes" / "research" / "01-executive-brief.md",
            "source_type": "market_report",
            "title": "CodeSync executive brief",
            "tags": ["codesync", "market", "wedge"],
            "implication": "The workspace should be adopted around one narrow launch lane and not a broad platform claim.",
        },
        {
            "bundle_key": "source_note_card_self_analysis",
            "artifact_id": f"source_note_card_{product_slug}_self_analysis",
            "path": source_dir / "Notes" / "research" / "02-codesync-self-analysis.md",
            "source_type": "competitor_site",
            "title": "CodeSync self analysis",
            "tags": ["codesync", "positioning", "inference"],
            "implication": "Observed and inferred product-surface claims should remain visibly separated in adopted artifacts.",
        },
        {
            "bundle_key": "source_note_card_segment_map",
            "artifact_id": f"source_note_card_{product_slug}_segment_map",
            "path": source_dir / "Notes" / "research" / "05-segment-map.md",
            "source_type": "other",
            "title": "CodeSync segment map",
            "tags": ["codesync", "segments", "beachhead"],
            "implication": "The adopted workspace should preserve one recommended beachhead and explicit expansion ladder.",
        },
        {
            "bundle_key": "source_note_card_persona_pack",
            "artifact_id": f"source_note_card_{product_slug}_persona_pack",
            "path": source_dir / "Notes" / "research" / "06-persona-pack.md",
            "source_type": "other",
            "title": "CodeSync persona pack",
            "tags": ["codesync", "personas", "buyers"],
            "implication": "The adopted workspace should retain buyer, operator, and workflow-user distinctions rather than flattening them.",
        },
        {
            "bundle_key": "source_note_card_pilot_proposal",
            "artifact_id": f"source_note_card_{product_slug}_pilot_proposal",
            "path": source_dir / "Notes" / "research" / "16-customer-pilot-proposal.md",
            "source_type": "other",
            "title": "CodeSync pilot proposal",
            "tags": ["codesync", "pilot", "launch-lane"],
            "implication": "The adopted PRD should inherit the controlled pilot shape and review-first rollout model.",
        },
    ]
    cards: dict[str, dict[str, Any]] = {}
    for spec in note_specs:
        text = _read_or_empty(spec["path"])
        if not text:
            continue
        lines = [line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#")]
        claim = _clip_sentence(lines[0] if lines else text, 240)
        snippet = _clip_sentence(" ".join(lines[:2]) if lines else text, 280)
        cards[spec["bundle_key"]] = {
            "schema_version": "1.0.0",
            "source_note_card_id": spec["artifact_id"],
            "workspace_id": workspace_id,
            "source_type": spec["source_type"],
            "source_ref": _relative_path(spec["path"], source_dir),
            "title": spec["title"],
            "claim": claim,
            "source_snippet": snippet,
            "implication": spec["implication"],
            "confidence": "moderate",
            "freshness_status": "usable_with_review",
            "unknowns": [
                "The source is a workspace note and still requires PM confirmation before external proof claims are made."
            ],
            "followup_questions": [
                "What part of this note is observed versus inferred versus hypothesis?"
            ],
            "source_metadata": {
                "source_slice_ref": spec["path"].name,
                "dedupe_key": _slug(spec["artifact_id"]),
                "credibility_tier": "unknown",
            },
            "dedupe_key": _slug(spec["artifact_id"]),
            "linked_entity_refs": [
                {"entity_type": "opportunity", "entity_id": opportunity_id},
                {"entity_type": "feature", "entity_id": feature_id},
            ],
            "tags": spec["tags"],
            "created_at": generated_at,
        }
    return cards


def _load_template_artifact(root_dir: Path, filename: str) -> dict[str, Any]:
    return _load_json(root_dir / "templates" / "artifacts" / filename)


def _build_review_items(product_slug: str, generated_at: str, review_threshold: str) -> list[dict[str, Any]]:
    items = [
        {
            "review_item_id": f"review_claims_{product_slug}",
            "title": "Validate commercial and performance claims before external reuse.",
            "uncertainty_type": "claim_evidence",
            "confidence": "low",
            "status": "open",
            "source_refs": [
                "Notes/research/01-executive-brief.md",
                "Notes/research/09-kpi-benchmark-guardrails.md",
            ],
            "recommended_reviewer_action": (
                "Confirm which outcome claims are observed, which remain inferred, and which must stay in hypothesis language."
            ),
        },
        {
            "review_item_id": f"review_security_{product_slug}",
            "title": "Confirm security and compliance posture before customer-facing packaging.",
            "uncertainty_type": "security_posture",
            "confidence": "low",
            "status": "open",
            "source_refs": [
                "Notes/research/20-security-compliance-appendix.md",
            ],
            "recommended_reviewer_action": (
                "Convert the current appendix into explicit control claims, named evidence, and blocked proof items."
            ),
        },
        {
            "review_item_id": f"review_packaging_{product_slug}",
            "title": "Validate pricing, packaging, and launch-lane packaging assumptions.",
            "uncertainty_type": "commercial_model",
            "confidence": "medium",
            "status": "open",
            "source_refs": [
                "Notes/research/21-reference-implementation-and-packaging.md",
                "Notes/research/16-customer-pilot-proposal.md",
            ],
            "recommended_reviewer_action": (
                "Review whether the proposed pilot, subscription, and enhancement packaging are ready for external use or still internal placeholders."
            ),
        },
        {
            "review_item_id": f"review_scope_{product_slug}",
            "title": "Lock the first workflow lane before broader product-surface claims.",
            "uncertainty_type": "workflow_scope",
            "confidence": "medium",
            "status": "open",
            "source_refs": [
                "Notes/research/05-segment-map.md",
                "Notes/research/16-customer-pilot-proposal.md",
            ],
            "recommended_reviewer_action": (
                "Confirm the launch lane and adjacent lane so the adopted PRD does not over-claim broad workflow coverage."
            ),
        },
    ]
    if review_threshold == "high":
        items.append(
            {
                "review_item_id": f"review_positioning_{product_slug}",
                "title": "Resolve category ambiguity in the external positioning story.",
                "uncertainty_type": "artifact_mapping",
                "confidence": "medium",
                "status": "open",
                "source_refs": [
                    "Notes/research/02-codesync-self-analysis.md",
                    "Notes/research/15-slide-ready-narrative.md",
                ],
                "recommended_reviewer_action": (
                    "Decide which positioning language is canonical so adopted artifacts do not mix PM suite, RCM platform, and orchestration narratives."
                ),
            }
        )
    return items


def _build_item_lifecycle_state(
    *,
    workspace_id: str,
    product_slug: str,
    best_beachhead: str,
    generated_at: str,
) -> dict[str, Any]:
    opportunity_id = f"opp_{product_slug}_workflow_control"
    feature_id = f"feature_{product_slug}_launch_lane"
    segment_id = "segment_physician_led_multisite_primary_care"
    persona_ids = [
        "persona_ipa_executive",
        "persona_rcm_director",
        "persona_practice_manager",
    ]
    artifact_ids_by_stage = {
        "signal_intake": [f"idea_record_{product_slug}"],
        "research_synthesis": [f"research_notebook_{product_slug}", f"research_brief_{product_slug}"],
        "segmentation_and_personas": [f"segment_map_{product_slug}", f"persona_pack_{product_slug}"],
        "problem_framing": [f"problem_brief_{product_slug}"],
        "concept_shaping": [f"concept_brief_{product_slug}"],
        "prototype_validation": [],
        "prd_handoff": [f"prd_{product_slug}"],
        "story_planning": [],
        "acceptance_ready": [],
        "release_readiness": [],
        "launch_preparation": [],
        "outcome_review": [],
    }
    statuses = {
        "signal_intake": ("completed", "passed", "Existing notes and research files were classified into an adoptable intake surface."),
        "research_synthesis": ("completed", "passed", "The research pack was condensed into a first-pass research notebook and research brief."),
        "segmentation_and_personas": ("completed", "passed", f"The beachhead segment and primary buyer personas were inferred from the research pack: {best_beachhead}"),
        "problem_framing": ("completed", "passed", "The adopted problem brief captures the workflow-fragmentation problem and launch-lane wedge."),
        "concept_shaping": ("completed", "passed", "The concept brief now frames CodeSync as a governed workflow control layer rather than a broad AI platform claim."),
        "prototype_validation": ("in_progress", "pending", "No explicit prototype validation artifact was found in the source workspace; prototype proof remains a required next step."),
        "prd_handoff": ("in_progress", "pending", "A first-pass PRD was generated from the adopted notes and research pack, but it still requires PM review before handoff is treated as strong."),
        "story_planning": ("not_started", "not_started", "Story planning should begin only after the adopted PRD and launch lane are confirmed."),
        "acceptance_ready": ("not_started", "not_started", "Acceptance criteria are deferred until the launch-lane PRD is validated."),
        "release_readiness": ("not_started", "not_started", "Release readiness is out of scope for the adoption bootstrap slice."),
        "launch_preparation": ("not_started", "not_started", "Launch preparation is intentionally deferred until the adopted product thesis is confirmed."),
        "outcome_review": ("not_started", "not_started", "Outcome review is deferred until a real pilot or launch lane is operating."),
    }
    lifecycle_stages = []
    for stage_key in LIFECYCLE_STAGE_ORDER:
        status, gate_status, summary = statuses[stage_key]
        lifecycle_stages.append(
            {
                "stage_key": stage_key,
                "status": status,
                "gate_status": gate_status,
                "artifact_ids": artifact_ids_by_stage[stage_key],
                "summary": summary,
            }
        )

    return {
        "schema_version": "1.0.0",
        "item_lifecycle_state_id": f"item_lifecycle_state_{product_slug}",
        "workspace_id": workspace_id,
        "title": "CodeSync workflow control adoption path",
        "item_ref": {
            "entity_type": "opportunity",
            "entity_id": opportunity_id,
        },
        "current_stage": "prd_handoff",
        "overall_status": "active_discovery",
        "target_segment_refs": [
            {
                "entity_type": "segment",
                "entity_id": segment_id,
            }
        ],
        "target_persona_refs": [
            {
                "entity_type": "persona",
                "entity_id": persona_id,
            }
            for persona_id in persona_ids
        ],
        "linked_entity_refs": [
            {
                "entity_type": "feature",
                "entity_id": feature_id,
            }
        ],
        "lifecycle_stages": lifecycle_stages,
        "pending_questions": [
            "Which claims are supported strongly enough for external customer reuse versus internal planning only?",
            "Should the first launch lane stay limited to eligibility and prior authorization before denial-prevention expansion is added?",
        ],
        "blocked_reasons": [],
        "audit_log": [
            {
                "timestamp": generated_at,
                "actor": "Workspace adoption",
                "event_type": "note",
                "summary": "The source workspace was classified as notes-first rather than ProductOS-native.",
            },
            {
                "timestamp": generated_at,
                "actor": "Workspace adoption",
                "event_type": "artifact_created",
                "summary": "First-pass discovery artifacts were generated from the CodeSync notes and research pack.",
            },
            {
                "timestamp": generated_at,
                "actor": "Workspace adoption",
                "event_type": "handoff_prepared",
                "summary": "Low-confidence claims, packaging assumptions, and proof gaps were routed into the adoption review queue.",
            },
        ],
        "created_at": generated_at,
        "updated_at": generated_at,
    }


def _artifact_kind(artifact_id: str) -> str:
    prefixes = [
        "workspace_adoption_report",
        "adoption_review_queue",
        "intake_routing_state",
        "research_notebook",
        "research_brief",
        "idea_record",
        "problem_brief",
        "concept_brief",
        "segment_map",
        "persona_pack",
        "prd",
        "item_lifecycle_state",
        "lifecycle_stage_snapshot",
        "prototype_record",
        "ux_design_review",
        "validation_lane_report",
        "manual_validation_record",
        "story_pack",
        "acceptance_criteria_set",
        "release_readiness",
        "release_note",
        "outcome_review",
        "competitor_dossier",
        "market_analysis_brief",
    ]
    for prefix in prefixes:
        if artifact_id.startswith(prefix):
            return prefix
    return artifact_id.split("_", 1)[0]


def _stage_map(item_state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {stage["stage_key"]: stage for stage in item_state["lifecycle_stages"]}


def _confidence_for_stage_states(stage_states: list[dict[str, Any]]) -> str:
    statuses = {stage["status"] for stage in stage_states}
    if "in_progress" in statuses:
        return "medium"
    if statuses == {"not_started"}:
        return "low"
    return "high"


def _backing_mode(*, has_artifact_payload: bool, stage_states: list[dict[str, Any]]) -> str:
    if has_artifact_payload:
        return "artifact_backed"
    if all(stage["status"] == "not_started" for stage in stage_states):
        return "deferred"
    return "lifecycle_fallback"


def _backing_mode_label(backing_mode: str) -> str:
    labels = {
        "artifact_backed": "artifact-backed",
        "lifecycle_fallback": "lifecycle fallback",
        "deferred": "deferred",
    }
    return labels[backing_mode]


def _build_thread_review_section(
    *,
    section_id: str,
    selector_key: str,
    title: str,
    headline: str,
    summary: str,
    key_points: list[str],
    stage_states: list[dict[str, Any]],
    artifact_ids: list[str],
    source_refs: list[str],
    backing_mode: str,
) -> dict[str, Any]:
    return {
        "section_id": section_id,
        "selector_key": selector_key,
        "title": title,
        "headline": headline,
        "summary": summary,
        "key_points": key_points,
        "stage_states": stage_states,
        "artifact_ids": artifact_ids,
        "source_refs": source_refs,
        "backing_mode": backing_mode,
        "confidence": _confidence_for_stage_states(stage_states),
    }


def _build_thread_review_bundle(
    *,
    workspace_id: str,
    product_slug: str,
    generated_at: str,
    research_notebook: dict[str, Any],
    research_brief: dict[str, Any],
    idea_record: dict[str, Any],
    problem_brief: dict[str, Any],
    concept_brief: dict[str, Any],
    segment_map: dict[str, Any],
    persona_pack: dict[str, Any],
    prd: dict[str, Any],
    item_lifecycle_state: dict[str, Any],
    workspace_adoption_report: dict[str, Any],
    adoption_review_queue: dict[str, Any],
) -> dict[str, Any]:
    stage_map = _stage_map(item_lifecycle_state)
    review_items = adoption_review_queue["review_items"]
    source_artifact_ids = [
        research_notebook["research_notebook_id"],
        research_brief["research_brief_id"],
        problem_brief["problem_brief_id"],
        concept_brief["concept_brief_id"],
        segment_map["segment_map_id"],
        persona_pack["persona_pack_id"],
        prd["prd_id"],
        item_lifecycle_state["item_lifecycle_state_id"],
    ]
    recommended_beachhead_id = segment_map.get("recommended_beachhead_segment_id")
    recommended_beachhead = next(
        (segment["name"] for segment in segment_map["segments"] if segment["segment_id"] == recommended_beachhead_id),
        recommended_beachhead_id or "No recommended beachhead recorded.",
    )
    primary_personas = [persona["role"] for persona in persona_pack.get("personas", [])[:3]]
    research_insights = [item["statement"] for item in research_brief.get("insights", [])[:3]]
    review_titles = [item["title"] for item in review_items[:4]]
    sections = [
        _build_thread_review_section(
            section_id="problem",
            selector_key="problem_brief",
            title="Problem framing",
            headline="Why the adopted workspace needs governed product state.",
            summary=problem_brief["problem_summary"],
            key_points=[
                problem_brief["strategic_fit_summary"],
                problem_brief["why_this_problem_now"],
                problem_brief["why_this_problem_for_this_segment"],
            ],
            stage_states=[stage_map["problem_framing"]],
            artifact_ids=[problem_brief["problem_brief_id"]],
            source_refs=[
                *problem_brief.get("upstream_artifact_ids", []),
                *[item["source_id"] for item in problem_brief.get("evidence_refs", [])],
            ],
            backing_mode="artifact_backed",
        ),
        _build_thread_review_section(
            section_id="segments_personas",
            selector_key="segment_and_persona_pack",
            title="Segments and personas",
            headline="Who the launch lane is for first.",
            summary=f"Recommended beachhead: {recommended_beachhead}.",
            key_points=[
                segment_map["market_scope_summary"],
                segment_map["segmentation_logic"],
                *primary_personas,
            ],
            stage_states=[stage_map["segmentation_and_personas"]],
            artifact_ids=[segment_map["segment_map_id"], persona_pack["persona_pack_id"]],
            source_refs=[*persona_pack.get("source_artifact_ids", []), segment_map["segment_map_id"]],
            backing_mode="artifact_backed",
        ),
        _build_thread_review_section(
            section_id="market_context",
            selector_key="research_context",
            title="Market and competitor context",
            headline="What the adopted research says about wedge strength and proof gaps.",
            summary=research_brief["summary"],
            key_points=[
                *research_brief.get("strategic_implications", [])[:2],
                *research_insights,
            ],
            stage_states=[stage_map["research_synthesis"]],
            artifact_ids=[research_notebook["research_notebook_id"], research_brief["research_brief_id"]],
            source_refs=[
                *research_brief.get("source_note_card_ids", []),
                *research_brief.get("research_notebook_ids", []),
            ],
            backing_mode="artifact_backed",
        ),
        _build_thread_review_section(
            section_id="concept",
            selector_key="concept_brief",
            title="Concept",
            headline="How ProductOS should frame the adopted product thesis.",
            summary=concept_brief["hypothesis"],
            key_points=[
                concept_brief["positioning_hypothesis"],
                concept_brief["offering_hypothesis"],
                concept_brief["wedge_hypothesis"],
            ],
            stage_states=[stage_map["concept_shaping"]],
            artifact_ids=[idea_record["idea_record_id"], concept_brief["concept_brief_id"]],
            source_refs=[*concept_brief.get("idea_record_ids", []), *concept_brief.get("strategy_artifact_ids", [])],
            backing_mode="artifact_backed",
        ),
        _build_thread_review_section(
            section_id="prototype",
            selector_key="prototype_record",
            title="Prototype",
            headline="Prototype proof is still an explicit gap.",
            summary=stage_map["prototype_validation"]["summary"],
            key_points=[
                "No prototype validation artifact was inferred safely from the source workspace.",
                "Prototype proof remains a required step before the adopted PRD should be treated as ready for downstream delivery planning.",
            ],
            stage_states=[stage_map["prototype_validation"]],
            artifact_ids=stage_map["prototype_validation"]["artifact_ids"],
            source_refs=[],
            backing_mode="lifecycle_fallback",
        ),
        _build_thread_review_section(
            section_id="prd",
            selector_key="prd",
            title="PRD",
            headline="The adopted PRD is present, but still provisional.",
            summary=prd["outcome_summary"],
            key_points=[
                prd["problem_summary"],
                prd["scope_summary"],
            ],
            stage_states=[stage_map["prd_handoff"]],
            artifact_ids=[prd["prd_id"]],
            source_refs=prd.get("upstream_artifact_ids", []),
            backing_mode="artifact_backed",
        ),
        _build_thread_review_section(
            section_id="delivery",
            selector_key="delivery_scope",
            title="Story pack and acceptance",
            headline="Delivery planning stays deferred until the launch lane and PRD are reviewed.",
            summary="No story pack or acceptance criteria should be generated until the provisional PRD and proof gaps are resolved.",
            key_points=[
                stage_map["story_planning"]["summary"],
                stage_map["acceptance_ready"]["summary"],
            ],
            stage_states=[stage_map["story_planning"], stage_map["acceptance_ready"]],
            artifact_ids=[
                *stage_map["story_planning"]["artifact_ids"],
                *stage_map["acceptance_ready"]["artifact_ids"],
            ],
            source_refs=[prd["prd_id"]],
            backing_mode="deferred",
        ),
        _build_thread_review_section(
            section_id="release_readiness",
            selector_key="release_readiness",
            title="Release readiness",
            headline="Release readiness is intentionally absent from the bootstrap slice.",
            summary=stage_map["release_readiness"]["summary"],
            key_points=[
                "The adopted workspace should not imply release readiness before a validated launch lane, delivery scope, and explicit review approvals exist.",
            ],
            stage_states=[stage_map["release_readiness"]],
            artifact_ids=stage_map["release_readiness"]["artifact_ids"],
            source_refs=[],
            backing_mode="deferred",
        ),
        _build_thread_review_section(
            section_id="launch",
            selector_key="release_note",
            title="Launch communication",
            headline="Launch messaging stays deferred until proof and packaging are reviewed.",
            summary=stage_map["launch_preparation"]["summary"],
            key_points=[
                "Launch communication should eventually connect to the same canonical lifecycle item instead of separate slide-only narratives.",
                *review_titles[:2],
            ],
            stage_states=[stage_map["launch_preparation"]],
            artifact_ids=stage_map["launch_preparation"]["artifact_ids"],
            source_refs=[],
            backing_mode="deferred",
        ),
        _build_thread_review_section(
            section_id="outcome_review",
            selector_key="outcome_review",
            title="Outcome review",
            headline="Outcome review remains closed until real pilot evidence exists.",
            summary=stage_map["outcome_review"]["summary"],
            key_points=[
                "The adopted workspace should keep post-launch claims out of scope until observed evidence exists.",
                *research_brief.get("known_gaps", [])[:1],
            ],
            stage_states=[stage_map["outcome_review"]],
            artifact_ids=stage_map["outcome_review"]["artifact_ids"],
            source_refs=[],
            backing_mode="deferred",
        ),
    ]
    stage_rail = [
        {
            "stage_key": stage["stage_key"],
            "title": stage["stage_key"].replace("_", " ").title(),
            "status": stage["status"],
            "gate_status": stage["gate_status"],
            "artifact_ids": stage["artifact_ids"],
            "summary": stage["summary"],
        }
        for stage in item_lifecycle_state["lifecycle_stages"]
    ]
    review_status, review_status_summary, action_items = _derive_review_actions_and_status(
        item_state=item_lifecycle_state,
        current_stage_map=stage_map,
        adoption_review_queue=adoption_review_queue,
        outcome_review=None,
        release_readiness=None,
        release_note=None,
    )
    return {
        "schema_version": "1.0.0",
        "thread_review_bundle_id": f"thread_review_bundle_{product_slug}",
        "workspace_id": workspace_id,
        "item_ref": item_lifecycle_state["item_ref"],
        "title": f"Thread Review: {item_lifecycle_state['title']}",
        "current_stage": item_lifecycle_state["current_stage"],
        "overall_status": item_lifecycle_state["overall_status"],
        "review_status": review_status,
        "review_status_summary": review_status_summary,
        "stage_rail": stage_rail,
        "sections": sections,
        "action_items": action_items,
        "pinned_context": {
            "target_segments": [ref["entity_id"] for ref in item_lifecycle_state["target_segment_refs"]],
            "target_personas": [ref["entity_id"] for ref in item_lifecycle_state["target_persona_refs"]],
            "pending_questions": list(
                dict.fromkeys(
                    [
                        *item_lifecycle_state.get("pending_questions", []),
                        *workspace_adoption_report.get("unresolved_questions", []),
                    ]
                )
            ),
            "key_risks": review_titles,
            "decisions": [
                f"Research recommendation: {research_brief['recommendation']}",
                "Treat the adopted PRD as provisional until PM review resolves proof, security, and packaging gaps.",
                "Keep later lifecycle stages explicit instead of inferring delivery or launch readiness too early.",
            ],
            "source_artifact_ids": source_artifact_ids,
            "confidence_summary": workspace_adoption_report["confidence_summary"],
        },
        "recommended_next_step": (
            action_items[0]["title"]
            if action_items
            else "Resolve the adoption review queue, confirm the first launch lane, and add prototype proof before story planning begins."
        ),
        "generated_at": generated_at,
    }


def render_thread_review_html(thread_review_bundle: dict[str, Any]) -> str:
    accent = "#165d4a"
    primary_question = next(iter(thread_review_bundle["pinned_context"]["pending_questions"]), "No pending question recorded.")
    primary_risk = next(iter(thread_review_bundle["pinned_context"]["key_risks"]), "No key risk recorded.")
    primary_decision = next(iter(thread_review_bundle["pinned_context"]["decisions"]), "No explicit decision recorded.")
    review_status_label = _review_status_label(thread_review_bundle["review_status"])
    stage_items = []
    for stage in thread_review_bundle["stage_rail"]:
        stage_items.append(
            "<li class='stage-pill {status}'>"
            "<span class='stage-name'>{name}</span>"
            "<span class='stage-meta'>{gate}</span>"
            "</li>".format(
                status=escape(stage["status"]),
                name=escape(stage["title"]),
                gate=escape(stage["gate_status"]),
            )
        )

    section_cards = []
    status_rank = {"in_progress": 2, "completed": 1, "not_started": 0}
    for section in thread_review_bundle["sections"]:
        section_state = max(
            (stage["status"] for stage in section["stage_states"]),
            key=lambda value: status_rank.get(value, 0),
        )
        points = "".join(f"<li>{escape(point)}</li>" for point in section["key_points"])
        stage_summary = "".join(
            (
                "<li><strong>{title}</strong> <span>{status}</span> <em>{gate}</em><p>{summary}</p></li>"
            ).format(
                title=escape(stage["stage_key"].replace("_", " ").title()),
                status=escape(stage["status"]),
                gate=escape(stage["gate_status"]),
                summary=escape(stage["summary"]),
            )
            for stage in section["stage_states"]
        )
        source_refs = "".join(
            f"<li>{escape(ref)}</li>" for ref in section["source_refs"] or ["No direct source refs recorded."]
        )
        artifact_refs = "".join(f"<li>{escape(ref)}</li>" for ref in section["artifact_ids"] or ["No artifact yet."])
        section_cards.append(
            """
            <section class="thread-section" data-section-state="{state}" id="{section_id}">
              <div class="section-header">
                <div>
                  <p class="eyebrow">{headline}</p>
                  <h2>{title}</h2>
                </div>
                <div class="section-badges">
                  <span class="backing backing-{backing_mode}">{backing_label}</span>
                  <span class="confidence confidence-{confidence}">{confidence}</span>
                </div>
              </div>
              <p class="summary">{summary}</p>
              <div class="section-grid">
                <details class="detail-key-points" open>
                  <summary>Key points</summary>
                  <ul>{points}</ul>
                </details>
                <details class="detail-stage-states" open>
                  <summary>Stage states</summary>
                  <ul>{stage_summary}</ul>
                </details>
                <details class="detail-artifacts">
                  <summary>Artifacts</summary>
                  <ul>{artifact_refs}</ul>
                </details>
                <details class="detail-sources">
                  <summary>Source refs</summary>
                  <ul>{source_refs}</ul>
                </details>
              </div>
            </section>
            """.format(
                state=escape(section_state),
                section_id=escape(section["section_id"]),
                headline=escape(section["headline"]),
                title=escape(section["title"]),
                backing_mode=escape(section["backing_mode"]),
                backing_label=escape(_backing_mode_label(section["backing_mode"])),
                confidence=escape(section["confidence"]),
                summary=escape(section["summary"]),
                points=points,
                stage_summary=stage_summary,
                artifact_refs=artifact_refs,
                source_refs=source_refs,
            )
        )

    action_cards = []
    for action in thread_review_bundle["action_items"]:
        action_sources = "".join(
            f"<li>{escape(ref)}</li>" for ref in action["source_refs"] or ["No source refs recorded."]
        )
        action_cards.append(
            """
            <article class="action-card priority-{priority}">
              <div class="action-header">
                <span class="priority-badge priority-{priority}">{priority}</span>
                <span class="action-type">{action_type}</span>
              </div>
              <h3>{title}</h3>
              <p>{rationale}</p>
              <details>
                <summary>Source refs</summary>
                <ul>{sources}</ul>
              </details>
            </article>
            """.format(
                priority=escape(action["priority"]),
                action_type=escape(action["action_type"].replace("_", " ")),
                title=escape(action["title"]),
                rationale=escape(action["rationale"]),
                sources=action_sources,
            )
        )

    pinned = thread_review_bundle["pinned_context"]
    pinned_lists = {
        "Target segments": pinned["target_segments"] or ["None recorded."],
        "Target personas": pinned["target_personas"] or ["None recorded."],
        "Pending questions": pinned["pending_questions"] or ["No pending questions recorded."],
        "Key risks": pinned["key_risks"] or ["No key risks recorded."],
        "Decisions": pinned["decisions"] or ["No explicit decisions recorded."],
        "Source artifacts": pinned["source_artifact_ids"] or ["No source artifacts recorded."],
    }
    pinned_markup = []
    for title, items in pinned_lists.items():
        pinned_markup.append(
            "<section><h3>{title}</h3><ul>{items}</ul></section>".format(
                title=escape(title),
                items="".join(f"<li>{escape(item)}</li>" for item in items),
            )
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(thread_review_bundle["title"])}</title>
  <style>
    :root {{
      --bg: #f4efe6;
      --panel: rgba(255, 255, 255, 0.88);
      --ink: #182126;
      --muted: #57626d;
      --accent: {accent};
      --accent-soft: #d7ebe4;
      --border: rgba(24, 33, 38, 0.12);
      --shadow: 0 18px 40px rgba(22, 37, 31, 0.08);
      --radius: 18px;
      --mono: "IBM Plex Mono", "SFMono-Regular", monospace;
      --sans: "IBM Plex Sans", "Avenir Next", "Segoe UI", sans-serif;
      --display: "Space Grotesk", "IBM Plex Sans", sans-serif;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: var(--sans);
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(22, 93, 74, 0.18), transparent 28%),
        radial-gradient(circle at top right, rgba(214, 122, 62, 0.14), transparent 24%),
        linear-gradient(180deg, #f7f2e8 0%, #eef3ef 100%);
    }}
    a {{ color: inherit; }}
    .shell {{
      max-width: 1440px;
      margin: 0 auto;
      padding: 28px;
    }}
    .hero {{
      display: grid;
      gap: 18px;
      grid-template-columns: 1.7fr 1fr;
      align-items: start;
      margin-bottom: 22px;
    }}
    .hero-card, .aside-card, .thread-section {{
      background: var(--panel);
      border: 1px solid var(--border);
      box-shadow: var(--shadow);
      backdrop-filter: blur(12px);
      border-radius: var(--radius);
    }}
    .hero-card {{
      padding: 28px;
    }}
    .hero h1 {{
      font-family: var(--display);
      font-size: clamp(2rem, 3vw, 3.4rem);
      line-height: 0.96;
      margin: 10px 0 18px;
      max-width: 16ch;
    }}
    .eyebrow {{
      margin: 0;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      color: var(--muted);
      font-size: 0.77rem;
    }}
    .hero-grid {{
      display: grid;
      gap: 12px;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      margin-top: 18px;
    }}
    .metric {{
      padding: 14px;
      border-radius: 14px;
      background: rgba(22, 93, 74, 0.07);
    }}
    .metric strong {{
      display: block;
      font-size: 0.78rem;
      color: var(--muted);
      margin-bottom: 8px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    .metric span {{
      font-size: 1.05rem;
      font-weight: 700;
    }}
    .metric .meta {{
      display: block;
      margin-top: 6px;
      font-size: 0.8rem;
      color: var(--muted);
      font-weight: 500;
    }}
    .aside-card {{
      padding: 22px;
      position: sticky;
      top: 20px;
    }}
    .aside-card h2 {{
      font-family: var(--display);
      margin: 0 0 8px;
    }}
    .aside-card p {{
      margin: 0 0 14px;
      color: var(--muted);
    }}
    .controls {{
      display: grid;
      gap: 12px;
      margin-bottom: 18px;
    }}
    .control-group {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      align-items: center;
    }}
    .control-label {{
      font-size: 0.78rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      min-width: 96px;
    }}
    .controls button {{
      border: 1px solid var(--border);
      background: white;
      border-radius: 999px;
      padding: 10px 14px;
      font: inherit;
      cursor: pointer;
    }}
    .controls button.active {{
      background: var(--accent);
      color: white;
      border-color: var(--accent);
    }}
    .decision-strip {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin: 18px 0 0;
    }}
    .decision-card {{
      border-radius: 16px;
      padding: 16px;
      border: 1px solid var(--border);
      background: rgba(255,255,255,0.72);
    }}
    .decision-card strong {{
      display: block;
      margin-bottom: 8px;
      font-size: 0.78rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    .decision-card span {{
      display: block;
      font-weight: 700;
      line-height: 1.4;
    }}
    .stage-rail {{
      list-style: none;
      padding: 0;
      margin: 18px 0 0;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
      gap: 10px;
    }}
    .stage-pill {{
      list-style: none;
      padding: 12px 14px;
      border-radius: 14px;
      border: 1px solid var(--border);
      background: white;
    }}
    .stage-pill.in_progress {{ background: #f7ead6; }}
    .stage-pill.completed {{ background: var(--accent-soft); }}
    .stage-pill.not_started {{ background: #f2f3f5; }}
    .stage-name {{
      display: block;
      font-weight: 700;
      margin-bottom: 4px;
    }}
    .stage-meta {{
      color: var(--muted);
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }}
    .layout {{
      display: grid;
      gap: 22px;
      grid-template-columns: minmax(0, 1.5fr) minmax(280px, 0.72fr);
    }}
    .action-panel {{
      display: grid;
      gap: 14px;
    }}
    .action-panel h2 {{
      margin: 0;
      font-family: var(--display);
    }}
    .action-panel > p {{
      margin: 0;
      color: var(--muted);
    }}
    .action-grid {{
      display: grid;
      gap: 12px;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    }}
    .action-card {{
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 16px;
      background: rgba(255,255,255,0.78);
    }}
    .action-card h3 {{
      margin: 10px 0 8px;
      font-size: 1rem;
      line-height: 1.35;
    }}
    .action-card p {{
      margin: 0 0 12px;
      color: var(--muted);
    }}
    .action-header {{
      display: flex;
      justify-content: space-between;
      gap: 10px;
      align-items: center;
      flex-wrap: wrap;
    }}
    .priority-badge, .action-type {{
      border-radius: 999px;
      padding: 7px 10px;
      font-size: 0.76rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    .priority-high {{ background: #f7ddcf; color: #8b2d06; }}
    .priority-medium {{ background: #f7ead6; color: #7d4a09; }}
    .priority-low {{ background: #eceef1; color: #56606b; }}
    .action-type {{ background: #edf3f0; color: #294e45; }}
    .main {{
      display: grid;
      gap: 18px;
    }}
    .thread-section {{
      padding: 24px;
    }}
    .section-header {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: start;
      margin-bottom: 10px;
    }}
    .section-badges {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }}
    .section-header h2 {{
      margin: 6px 0 0;
      font-family: var(--display);
    }}
    .summary {{
      font-size: 1.02rem;
      margin-bottom: 18px;
      max-width: 72ch;
    }}
    .section-grid {{
      display: grid;
      gap: 12px;
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }}
    body[data-density="summary"] .detail-artifacts,
    body[data-density="summary"] .detail-sources {{
      display: none;
    }}
    body[data-density="summary"] .detail-stage-states p {{
      display: none;
    }}
    body[data-density="summary"] .thread-section {{
      padding: 20px;
    }}
    body[data-density="detailed"] .thread-section {{
      padding: 28px;
    }}
    details {{
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 14px;
      background: rgba(255,255,255,0.72);
    }}
    summary {{
      cursor: pointer;
      font-weight: 700;
      list-style: none;
    }}
    details ul {{
      margin: 12px 0 0;
      padding-left: 18px;
    }}
    details li {{
      margin-bottom: 10px;
    }}
    details p {{
      margin: 6px 0 0;
      color: var(--muted);
    }}
    .confidence {{
      border-radius: 999px;
      padding: 8px 12px;
      font-size: 0.85rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      white-space: nowrap;
    }}
    .confidence-high {{ background: var(--accent-soft); color: #0d4638; }}
    .confidence-medium {{ background: #f7ead6; color: #7d4a09; }}
    .confidence-low {{ background: #efefef; color: #4c535a; }}
    .backing {{
      border-radius: 999px;
      padding: 8px 12px;
      font-size: 0.85rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      white-space: nowrap;
    }}
    .backing-artifact_backed {{ background: #dbeaf8; color: #194f80; }}
    .backing-lifecycle_fallback {{ background: #f1e1c6; color: #7b5114; }}
    .backing-deferred {{ background: #eceef1; color: #56606b; }}
    .sidebar {{
      display: grid;
      gap: 16px;
      align-content: start;
    }}
    .sidebar section {{
      padding-bottom: 12px;
      border-bottom: 1px solid var(--border);
    }}
    .sidebar section:last-child {{
      border-bottom: 0;
      padding-bottom: 0;
    }}
    .sidebar h3 {{
      margin: 0 0 10px;
      font-family: var(--display);
      font-size: 1rem;
    }}
    .sidebar ul {{
      margin: 0;
      padding-left: 18px;
    }}
    .sidebar li {{
      margin-bottom: 8px;
    }}
    .footer-note {{
      margin-top: 14px;
      font-family: var(--mono);
      font-size: 0.88rem;
      color: var(--muted);
    }}
    @media (max-width: 1080px) {{
      .hero, .layout, .section-grid {{
        grid-template-columns: 1fr;
      }}
      .decision-strip {{
        grid-template-columns: 1fr;
      }}
      .aside-card {{
        position: static;
      }}
    }}
  </style>
</head>
<body data-density="standard">
  <div class="shell">
    <header class="hero">
      <section class="hero-card">
        <p class="eyebrow">ProductOS Thread Review</p>
        <h1>{escape(thread_review_bundle["title"])}</h1>
        <p class="summary">{escape(thread_review_bundle["recommended_next_step"])}</p>
        <div class="controls">
          <div class="control-group">
            <span class="control-label">Filter</span>
            <button class="active" data-filter="all">All sections</button>
            <button data-filter="active">Active now</button>
            <button data-filter="deferred">Deferred</button>
          </div>
          <div class="control-group">
            <span class="control-label">Density</span>
            <button class="active" data-density="standard">Standard mode</button>
            <button data-density="summary">Summary mode</button>
            <button data-density="detailed">Detailed mode</button>
          </div>
        </div>
        <div class="hero-grid">
          <div class="metric"><strong>Current stage</strong><span>{escape(thread_review_bundle["current_stage"])}</span></div>
          <div class="metric"><strong>Review status</strong><span>{escape(review_status_label)}</span><span class="meta">{escape(thread_review_bundle["review_status_summary"])}</span></div>
          <div class="metric"><strong>Item ref</strong><span>{escape(thread_review_bundle["item_ref"]["entity_id"])}</span></div>
        </div>
        <div class="decision-strip">
          <div class="decision-card">
            <strong>Decision now</strong>
            <span>{escape(thread_review_bundle["recommended_next_step"])}</span>
          </div>
          <div class="decision-card">
            <strong>Top question</strong>
            <span>{escape(primary_question)}</span>
          </div>
          <div class="decision-card">
            <strong>Top risk</strong>
            <span>{escape(primary_risk)}</span>
          </div>
        </div>
        <ul class="stage-rail">
          {''.join(stage_items)}
        </ul>
      </section>
      <aside class="aside-card">
        <h2>Confidence</h2>
        <p>{escape(pinned["confidence_summary"])}</p>
        <p><strong>Decision signal:</strong> {escape(primary_decision)}</p>
        <p class="footer-note">Generated at {escape(thread_review_bundle["generated_at"])}</p>
      </aside>
    </header>
    <div class="layout">
      <main class="main">
        <section class="thread-section action-panel">
          <div>
            <p class="eyebrow">Review Actions</p>
            <h2>What the PM should do next</h2>
            <p>{escape(thread_review_bundle["review_status_summary"])}</p>
          </div>
          <div class="action-grid">
            {''.join(action_cards) or "<article class='action-card priority-low'><h3>No explicit action items recorded.</h3><p>Advance the thread through the next bounded lifecycle review step.</p></article>"}
          </div>
        </section>
        {''.join(section_cards)}
      </main>
      <aside class="aside-card sidebar">
        {''.join(pinned_markup)}
      </aside>
    </div>
  </div>
  <script>
    const filterButtons = document.querySelectorAll('[data-filter]');
    const densityButtons = document.querySelectorAll('[data-density]');
    const sections = document.querySelectorAll('.thread-section');
    const detailsBlocks = document.querySelectorAll('.thread-section details');
    const matches = {{
      all: () => true,
      active: state => state === 'completed' || state === 'in_progress',
      deferred: state => state === 'not_started'
    }};
    filterButtons.forEach(button => {{
      button.addEventListener('click', () => {{
        filterButtons.forEach(item => item.classList.remove('active'));
        button.classList.add('active');
        const filter = button.dataset.filter;
        sections.forEach(section => {{
          section.hidden = !matches[filter](section.dataset.sectionState);
        }});
      }});
    }});
    densityButtons.forEach(button => {{
      button.addEventListener('click', () => {{
        densityButtons.forEach(item => item.classList.remove('active'));
        button.classList.add('active');
        const density = button.dataset.density;
        document.body.dataset.density = density;
        detailsBlocks.forEach(detail => {{
          if (density === 'summary') {{
            if (detail.classList.contains('detail-key-points') || detail.classList.contains('detail-stage-states')) {{
              detail.open = true;
            }} else {{
              detail.open = false;
            }}
          }} else if (density === 'detailed') {{
            detail.open = true;
          }} else {{
            if (detail.classList.contains('detail-key-points') || detail.classList.contains('detail-stage-states')) {{
              detail.open = true;
            }} else {{
              detail.open = false;
            }}
          }}
        }});
      }});
    }});
  </script>
</body>
</html>"""


def write_thread_review_page(thread_review_bundle: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_thread_review_html(thread_review_bundle), encoding="utf-8")
    return path


def _dedupe_strings(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if isinstance(value, str) and value))


def _thread_review_mode_counts(thread_review_bundle: dict[str, Any]) -> Counter[str]:
    return Counter(section["backing_mode"] for section in thread_review_bundle["sections"])


def format_thread_review_markdown(thread_review_bundle: dict[str, Any]) -> str:
    primary_question = next(iter(thread_review_bundle["pinned_context"]["pending_questions"]), "No pending question recorded.")
    primary_risk = next(iter(thread_review_bundle["pinned_context"]["key_risks"]), "No key risk recorded.")
    primary_decision = next(iter(thread_review_bundle["pinned_context"]["decisions"]), "No explicit decision recorded.")
    mode_counts = _thread_review_mode_counts(thread_review_bundle)

    lines = [
        f"# {thread_review_bundle['title']}",
        "",
        f"- Item: `{thread_review_bundle['item_ref']['entity_id']}`",
        f"- Current stage: `{thread_review_bundle['current_stage']}`",
        f"- Overall status: `{thread_review_bundle['overall_status']}`",
        f"- Review status: `{_review_status_label(thread_review_bundle['review_status'])}`",
        f"- Generated at: `{thread_review_bundle['generated_at']}`",
        "",
        "## Decision Now",
        "",
        thread_review_bundle["recommended_next_step"],
        "",
        "## Review Summary",
        "",
        f"- Status summary: {thread_review_bundle['review_status_summary']}",
        f"- Top question: {primary_question}",
        f"- Top risk: {primary_risk}",
        f"- Decision signal: {primary_decision}",
        (
            "- Section backing: "
            f"{mode_counts.get('artifact_backed', 0)} artifact-backed, "
            f"{mode_counts.get('lifecycle_fallback', 0)} lifecycle fallback, "
            f"{mode_counts.get('deferred', 0)} deferred"
        ),
        "",
    ]

    if thread_review_bundle["action_items"]:
        lines.extend(["## Review Actions", ""])
        for action in thread_review_bundle["action_items"]:
            lines.append(
                f"- `{action['priority']}` {action['title']}: {action['rationale']}"
            )
        lines.append("")

    lines.extend(["## Stage Rail", ""])
    for stage in thread_review_bundle["stage_rail"]:
        artifact_summary = ", ".join(stage["artifact_ids"]) if stage["artifact_ids"] else "none"
        lines.append(
            f"- `{stage['stage_key']}`: {stage['status']} / {stage['gate_status']} (artifacts: {artifact_summary})"
        )
    lines.append("")

    for section in thread_review_bundle["sections"]:
        lines.extend(
            [
                f"## {section['title']}",
                "",
                f"- Backing mode: `{section['backing_mode']}`",
                f"- Confidence: `{section['confidence']}`",
                f"- Headline: {section['headline']}",
                f"- Summary: {section['summary']}",
            ]
        )
        if section["key_points"]:
            lines.append("- Key points:")
            for point in section["key_points"]:
                lines.append(f"  - {point}")
        if section["artifact_ids"]:
            lines.append(f"- Artifacts: {', '.join(section['artifact_ids'])}")
        if section["source_refs"]:
            lines.append(f"- Source refs: {', '.join(section['source_refs'])}")
        lines.append("")

    lines.extend(
        [
            "## Pinned Context",
            "",
            f"- Target segments: {', '.join(thread_review_bundle['pinned_context']['target_segments']) or 'none'}",
            f"- Target personas: {', '.join(thread_review_bundle['pinned_context']['target_personas']) or 'none'}",
            f"- Confidence summary: {thread_review_bundle['pinned_context']['confidence_summary']}",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def write_thread_review_markdown(thread_review_bundle: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(format_thread_review_markdown(thread_review_bundle), encoding="utf-8")
    return path


def build_thread_review_presentation_brief(thread_review_bundle: dict[str, Any]) -> dict[str, Any]:
    source_artifact_ids = _dedupe_strings(
        [
            *thread_review_bundle["pinned_context"]["source_artifact_ids"],
            *[ref for action in thread_review_bundle["action_items"] for ref in action["source_refs"]],
            *[artifact_id for section in thread_review_bundle["sections"] for artifact_id in section["artifact_ids"]],
        ]
    )
    primary_question = next(iter(thread_review_bundle["pinned_context"]["pending_questions"]), "No pending question recorded.")
    primary_risk = next(iter(thread_review_bundle["pinned_context"]["key_risks"]), "No key risk recorded.")
    primary_action = (
        thread_review_bundle["action_items"][0]["title"]
        if thread_review_bundle["action_items"]
        else thread_review_bundle["recommended_next_step"]
    )
    mode_counts = _thread_review_mode_counts(thread_review_bundle)
    deferred_sections = [section["title"] for section in thread_review_bundle["sections"] if section["backing_mode"] == "deferred"]
    artifact_backed_sections = [section["title"] for section in thread_review_bundle["sections"] if section["backing_mode"] == "artifact_backed"]
    lifecycle_artifact_id = next(
        (
            artifact_id
            for artifact_id in source_artifact_ids
            if _artifact_kind(artifact_id) == "item_lifecycle_state"
        ),
        thread_review_bundle["thread_review_bundle_id"],
    )
    review_artifact_id = next(
        (
            artifact_id
            for artifact_id in source_artifact_ids
            if _artifact_kind(artifact_id) in {"workspace_adoption_report", "adoption_review_queue", "thread_review_bundle"}
        ),
        thread_review_bundle["thread_review_bundle_id"],
    )
    decision_artifact_id = next(
        (
            artifact_id
            for artifact_id in source_artifact_ids
            if _artifact_kind(artifact_id) in {"prd", "release_readiness", "outcome_review", "release_note"}
        ),
        review_artifact_id,
    )

    return {
        "schema_version": "1.0.0",
        "presentation_brief_id": f"presentation_brief_{_slug(thread_review_bundle['item_ref']['entity_id'])}_thread_review",
        "workspace_id": thread_review_bundle["workspace_id"],
        "title": f"{thread_review_bundle['title']} deck",
        "presentation_archetype": "decision_recommendation",
        "audience": "PM Review",
        "objective": "Review one canonical lifecycle thread end to end and decide the next bounded PM action without losing provenance.",
        "presentation_mode": "async",
        "presenter_mode": "self_explanatory",
        "audience_type": "working_team",
        "audience_familiarity": "medium",
        "decision_required": primary_action,
        "decision_stakes": "high" if thread_review_bundle["review_status"] == "pm_review_required" else "medium",
        "delivery_context": "Thread-level PM review generated from the canonical ProductOS lifecycle trace.",
        "density_preference": "balanced",
        "narrative_goal": "Lead with the next action, preserve lifecycle provenance, and show which sections are backed versus deferred.",
        "deck_length_target": "tight",
        "appendix_mode": "evidence_trace",
        "redaction_policy": "internal_only",
        "tone_profile": "operational",
        "success_outcome": "The PM should understand the current stage, top gaps, and immediate action needed without re-opening scattered source artifacts.",
        "audience_constraints": [
            "Keep the review self-explanatory without a live narrator.",
            "Keep provenance, deferred sections, and uncertainty visible.",
        ],
        "required_objections": [
            "Which parts of this thread are artifact-backed versus still inferred or deferred?",
            "What should the PM do now rather than later?",
        ],
        "non_negotiables": [
            "Do not hide deferred lifecycle sections.",
            "Do not let the presentation surface replace the canonical artifacts.",
        ],
        "comparison_baseline": "Opening multiple ProductOS artifacts by hand to reconstruct the same thread.",
        "theme_preset": "atlas",
        "presentation_format": "html",
        "slide_outlines": [
            {
                "slide_id": "slide_cover",
                "title": "Decision Now",
                "intent": "cover",
                "audience_question": "What does this thread need from PM review right now?",
                "claim": thread_review_bundle["review_status_summary"],
                "proof_requirements": [
                    "State the immediate PM action clearly",
                    "Show the current lifecycle stage and review state",
                ],
                "core_message": primary_action,
                "key_points": [
                    thread_review_bundle["current_stage"].replace("_", " "),
                    _review_status_label(thread_review_bundle["review_status"]),
                ],
                "evidence_refs": [lifecycle_artifact_id, review_artifact_id],
                "cta": primary_action,
                "visual_direction": "Lead with the next bounded PM action and keep the review posture explicit.",
            },
            {
                "slide_id": "slide_summary",
                "title": "Thread Coverage",
                "intent": "summary",
                "audience_question": "How much of the thread is already grounded in explicit lifecycle evidence?",
                "claim": (
                    f"{mode_counts.get('artifact_backed', 0)} sections are artifact-backed while "
                    f"{mode_counts.get('deferred', 0)} remain deferred."
                ),
                "proof_requirements": [
                    "Show coverage across artifact-backed and deferred sections",
                    "Keep the major backed sections visible",
                ],
                "core_message": "The review surface is strongest where the lifecycle already has explicit artifacts and should stay honest about deferred areas.",
                "key_points": artifact_backed_sections[:4] or ["No artifact-backed sections recorded."],
                "evidence_refs": [lifecycle_artifact_id, *source_artifact_ids[:2]],
                "cta": "Use the thread as a review surface, not a replacement for the source artifacts.",
                "visual_direction": "Coverage cards with clear backed versus deferred emphasis.",
            },
            {
                "slide_id": "slide_risks",
                "title": "Risks And Open Questions",
                "intent": "risks",
                "audience_question": "What should block the PM from advancing this thread too quickly?",
                "claim": primary_risk,
                "proof_requirements": [
                    "Show the main risk and the open review question",
                    "Keep deferred sections visible as scope limits",
                ],
                "core_message": primary_question,
                "key_points": (deferred_sections[:3] or ["No deferred sections recorded."]),
                "evidence_refs": [review_artifact_id, *[ref for action in thread_review_bundle["action_items"][:2] for ref in action["source_refs"]]],
                "must_show_risk": True,
                "cta": "Close the explicit risk before widening the thread scope.",
                "visual_direction": "Risk-led slide with visible blockers and deferred boundaries.",
            },
            {
                "slide_id": "slide_decision",
                "title": "Recommended Actions",
                "intent": "decision",
                "audience_question": "What are the next bounded actions to move this thread forward?",
                "claim": primary_action,
                "proof_requirements": [
                    "List the highest-priority PM actions",
                    "Keep action rationale and source grounding visible",
                ],
                "core_message": thread_review_bundle["recommended_next_step"],
                "key_points": [action["title"] for action in thread_review_bundle["action_items"][:3]] or [thread_review_bundle["recommended_next_step"]],
                "evidence_refs": [decision_artifact_id, *[ref for action in thread_review_bundle["action_items"][:3] for ref in action["source_refs"]]],
                "cta": thread_review_bundle["recommended_next_step"],
                "visual_direction": "Decision frame with the top actions ordered by priority.",
            },
        ],
        "source_artifact_ids": source_artifact_ids or [thread_review_bundle["thread_review_bundle_id"]],
        "source_material_snapshots": [
            {
                "artifact_id": lifecycle_artifact_id,
                "artifact_type": _artifact_kind(lifecycle_artifact_id),
                "facts": [
                    {
                        "fact_id": f"fact_{_slug(thread_review_bundle['item_ref']['entity_id'])}_current_stage",
                        "fact_type": "status",
                        "statement": (
                            f"The canonical item is currently at {thread_review_bundle['current_stage']} with overall status "
                            f"{thread_review_bundle['overall_status']}."
                        ),
                        "relevance_tags": ["cover", "summary", "status"],
                    },
                    {
                        "fact_id": f"fact_{_slug(thread_review_bundle['item_ref']['entity_id'])}_coverage",
                        "fact_type": "constraint",
                        "statement": (
                            f"{mode_counts.get('artifact_backed', 0)} sections are artifact-backed and "
                            f"{mode_counts.get('deferred', 0)} remain deferred."
                        ),
                        "relevance_tags": ["summary", "coverage", "constraint"],
                    },
                ],
            },
            {
                "artifact_id": review_artifact_id,
                "artifact_type": _artifact_kind(review_artifact_id),
                "facts": [
                    {
                        "fact_id": f"fact_{_slug(thread_review_bundle['item_ref']['entity_id'])}_review_status",
                        "fact_type": "decision",
                        "statement": thread_review_bundle["review_status_summary"],
                        "relevance_tags": ["cover", "decision", "recommendation"],
                    },
                    {
                        "fact_id": f"fact_{_slug(thread_review_bundle['item_ref']['entity_id'])}_primary_risk",
                        "fact_type": "risk",
                        "statement": primary_risk,
                        "relevance_tags": ["risk", "governance", "review"],
                    },
                ],
            },
            {
                "artifact_id": decision_artifact_id,
                "artifact_type": _artifact_kind(decision_artifact_id),
                "facts": [
                    {
                        "fact_id": f"fact_{_slug(thread_review_bundle['item_ref']['entity_id'])}_next_action",
                        "fact_type": "decision",
                        "statement": thread_review_bundle["recommended_next_step"],
                        "relevance_tags": ["decision", "recommendation", "next_step"],
                    },
                    {
                        "fact_id": f"fact_{_slug(thread_review_bundle['item_ref']['entity_id'])}_open_question",
                        "fact_type": "constraint",
                        "statement": primary_question,
                        "relevance_tags": ["risk", "review", "constraint"],
                    },
                ],
            },
        ],
        "known_gaps": _dedupe_strings(
            [primary_question, *deferred_sections[:4], *thread_review_bundle["pinned_context"]["key_risks"][:2]]
        ),
        "external_research_questions": thread_review_bundle["pinned_context"]["pending_questions"][:3],
        "contradiction_summaries": [],
        "customer_safe": False,
        "created_at": thread_review_bundle["generated_at"],
    }


def build_thread_review_presentation_package(
    thread_review_bundle: dict[str, Any],
    *,
    aspect_ratio: str = "16:9",
) -> dict[str, dict[str, Any]]:
    presentation_brief = build_thread_review_presentation_brief(thread_review_bundle)
    evidence_pack = build_evidence_pack(presentation_brief)
    presentation_story = build_presentation_story(presentation_brief, evidence_pack)
    render_spec = build_render_spec(presentation_brief, presentation_story, aspect_ratio=aspect_ratio)
    slide_spec = build_slide_spec(presentation_brief, aspect_ratio=aspect_ratio)
    publish_check = build_publish_check(presentation_brief, render_spec, target_format="html")
    ppt_export_plan = build_ppt_export_plan(render_spec)
    return {
        "presentation_brief": presentation_brief,
        "presentation_evidence_pack": evidence_pack,
        "presentation_story": presentation_story,
        "presentation_render_spec": render_spec,
        "presentation_slide_spec": slide_spec,
        "presentation_publish_check": publish_check,
        "presentation_ppt_export_plan": ppt_export_plan,
    }


def write_thread_review_package(
    thread_review_bundle: dict[str, Any],
    output_dir: str | Path,
    *,
    aspect_ratio: str = "16:9",
) -> dict[str, Path]:
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    thread_review_html = write_thread_review_page(thread_review_bundle, output_root / "thread-review.html")
    thread_review_markdown = write_thread_review_markdown(thread_review_bundle, output_root / "thread-review.md")
    presentation_dir = output_root / "presentation"
    presentation_dir.mkdir(parents=True, exist_ok=True)

    package = build_thread_review_presentation_package(thread_review_bundle, aspect_ratio=aspect_ratio)
    output_paths = {
        "thread_review_html": thread_review_html,
        "thread_review_markdown": thread_review_markdown,
        "presentation_brief": presentation_dir / "presentation_brief.json",
        "presentation_evidence_pack": presentation_dir / "presentation_evidence_pack.json",
        "presentation_story": presentation_dir / "presentation_story.json",
        "presentation_render_spec": presentation_dir / "presentation_render_spec.json",
        "presentation_slide_spec": presentation_dir / "presentation_slide_spec.json",
        "presentation_publish_check": presentation_dir / "presentation_publish_check.json",
        "presentation_ppt_export_plan": presentation_dir / "presentation_ppt_export_plan.json",
        "presentation_html": presentation_dir / "thread-review-deck.html",
    }
    for key, payload in package.items():
        _write_json(output_paths[key], payload)
    write_html_presentation(package["presentation_render_spec"], output_paths["presentation_html"])
    return output_paths


def _thread_review_sort_key(thread_review_bundle: dict[str, Any]) -> tuple[int, int, str]:
    review_rank = {
        "pm_review_required": 0,
        "ready_for_launch_review": 1,
        "in_progress": 2,
        "stable_full_lifecycle": 3,
    }
    stage_rank = {stage: index for index, stage in enumerate(LIFECYCLE_STAGE_ORDER)}
    return (
        review_rank.get(thread_review_bundle["review_status"], 99),
        stage_rank.get(thread_review_bundle["current_stage"], 99),
        thread_review_bundle["title"],
    )


def render_thread_review_index_html(entries: list[dict[str, Any]], *, workspace_id: str, generated_at: str) -> str:
    accent = "#185b4b"
    bundles = [entry["bundle"] for entry in entries]
    review_counts = Counter(bundle["review_status"] for bundle in bundles)
    stage_counts = Counter(bundle["current_stage"] for bundle in bundles)
    cards = []
    for entry in entries:
        bundle = entry["bundle"]
        mode_counts = _thread_review_mode_counts(bundle)
        top_risk = next(iter(bundle["pinned_context"]["key_risks"]), "No key risk recorded.")
        top_action = bundle["action_items"][0]["title"] if bundle["action_items"] else bundle["recommended_next_step"]
        cards.append(
            """
            <article class="thread-card" data-review-status="{review_status}" data-stage="{stage}">
              <div class="card-top">
                <div>
                  <p class="eyebrow">{review_label}</p>
                  <h2>{title}</h2>
                </div>
                <span class="stage-pill">{stage_label}</span>
              </div>
              <p class="summary">{summary}</p>
              <div class="metric-row">
                <div><strong>Artifact-backed</strong><span>{artifact_backed}</span></div>
                <div><strong>Deferred</strong><span>{deferred}</span></div>
                <div><strong>Actions</strong><span>{action_count}</span></div>
              </div>
              <div class="callout">
                <strong>Next action</strong>
                <span>{top_action}</span>
              </div>
              <div class="callout muted">
                <strong>Top risk</strong>
                <span>{top_risk}</span>
              </div>
              <div class="link-row">
                <a href="{thread_href}">Open thread</a>
                <a href="{markdown_href}">Markdown</a>
                <a href="{presentation_href}">Deck</a>
              </div>
            </article>
            """.format(
                review_status=escape(bundle["review_status"]),
                stage=escape(bundle["current_stage"]),
                review_label=escape(_review_status_label(bundle["review_status"])),
                title=escape(bundle["title"]),
                stage_label=escape(bundle["current_stage"].replace("_", " ")),
                summary=escape(bundle["review_status_summary"]),
                artifact_backed=mode_counts.get("artifact_backed", 0),
                deferred=mode_counts.get("deferred", 0),
                action_count=len(bundle["action_items"]),
                top_action=escape(top_action),
                top_risk=escape(top_risk),
                thread_href=escape(entry["thread_href"]),
                markdown_href=escape(entry["markdown_href"]),
                presentation_href=escape(entry["presentation_href"]),
            )
        )

    review_filters = [
        ("all", "All threads"),
        ("pm_review_required", "PM review"),
        ("ready_for_launch_review", "Launch review"),
        ("stable_full_lifecycle", "Stable"),
    ]
    review_filter_markup = "".join(
        f"<button data-review-filter=\"{escape(value)}\" class=\"{'active' if value == 'all' else ''}\">{escape(label)}</button>"
        for value, label in review_filters
    )
    stage_summary = ", ".join(
        f"{stage.replace('_', ' ')}: {count}" for stage, count in sorted(stage_counts.items(), key=lambda item: item[0])
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Thread Review Index</title>
  <style>
    :root {{
      --bg: #f4efe6;
      --panel: rgba(255,255,255,0.9);
      --ink: #1b2329;
      --muted: #58636d;
      --accent: {accent};
      --border: rgba(27,35,41,0.12);
      --shadow: 0 18px 40px rgba(27,35,41,0.08);
      --radius: 18px;
      --display: "Space Grotesk", "IBM Plex Sans", sans-serif;
      --sans: "IBM Plex Sans", "Avenir Next", sans-serif;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: var(--sans);
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(24,91,75,0.16), transparent 28%),
        radial-gradient(circle at top right, rgba(30,90,168,0.14), transparent 24%),
        linear-gradient(180deg, #f7f2e8 0%, #eef3ef 100%);
    }}
    .shell {{ max-width: 1440px; margin: 0 auto; padding: 28px; }}
    .hero, .thread-card {{
      background: var(--panel);
      border: 1px solid var(--border);
      box-shadow: var(--shadow);
      border-radius: var(--radius);
    }}
    .hero {{ padding: 28px; margin-bottom: 22px; }}
    .eyebrow {{
      margin: 0;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      color: var(--muted);
      font-size: 0.77rem;
    }}
    h1, h2 {{
      font-family: var(--display);
      margin: 8px 0 10px;
    }}
    .hero p.summary {{ max-width: 70ch; margin: 0 0 16px; color: var(--muted); }}
    .metrics {{
      display: grid;
      gap: 12px;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      margin-bottom: 16px;
    }}
    .metric {{
      border-radius: 14px;
      padding: 14px;
      background: rgba(24,91,75,0.07);
    }}
    .metric strong {{
      display: block;
      font-size: 0.76rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 8px;
    }}
    .metric span {{ font-size: 1.05rem; font-weight: 700; }}
    .controls {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      align-items: center;
    }}
    .controls button {{
      border: 1px solid var(--border);
      background: white;
      border-radius: 999px;
      padding: 10px 14px;
      font: inherit;
      cursor: pointer;
    }}
    .controls button.active {{
      background: var(--accent);
      color: white;
      border-color: var(--accent);
    }}
    .grid {{
      display: grid;
      gap: 18px;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    }}
    .thread-card {{ padding: 22px; }}
    .card-top {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: start;
    }}
    .stage-pill {{
      border-radius: 999px;
      padding: 8px 12px;
      background: #e4ece8;
      color: var(--accent);
      font-size: 0.8rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      white-space: nowrap;
    }}
    .summary {{ color: var(--muted); line-height: 1.5; min-height: 3em; }}
    .metric-row {{
      display: grid;
      gap: 10px;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      margin: 16px 0;
    }}
    .metric-row div {{
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 12px;
      background: rgba(255,255,255,0.78);
    }}
    .metric-row strong {{
      display: block;
      font-size: 0.74rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 8px;
    }}
    .metric-row span {{ font-weight: 700; }}
    .callout {{
      border-radius: 14px;
      padding: 14px;
      background: rgba(24,91,75,0.08);
      margin-bottom: 10px;
    }}
    .callout.muted {{ background: rgba(27,35,41,0.05); }}
    .callout strong {{
      display: block;
      font-size: 0.76rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 8px;
    }}
    .link-row {{
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      margin-top: 14px;
    }}
    .link-row a {{
      text-decoration: none;
      font-weight: 700;
      color: var(--accent);
    }}
    .footer-note {{ margin-top: 16px; color: var(--muted); font-size: 0.9rem; }}
    @media (max-width: 900px) {{
      .metrics, .metric-row {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <section class="hero">
      <p class="eyebrow">ProductOS Thread Review Index</p>
      <h1>{escape(workspace_id)}</h1>
      <p class="summary">Use this index to triage many lifecycle threads quickly, then open one canonical thread, its readable doc, or its deck without reconstructing context manually.</p>
      <div class="metrics">
        <div class="metric"><strong>Threads</strong><span>{len(entries)}</span></div>
        <div class="metric"><strong>PM review</strong><span>{review_counts.get('pm_review_required', 0)}</span></div>
        <div class="metric"><strong>Launch review</strong><span>{review_counts.get('ready_for_launch_review', 0)}</span></div>
        <div class="metric"><strong>Stable</strong><span>{review_counts.get('stable_full_lifecycle', 0)}</span></div>
      </div>
      <div class="controls">
        {review_filter_markup}
      </div>
      <p class="footer-note">Stage coverage: {escape(stage_summary or 'No stages recorded.')}<br>Generated at {escape(generated_at)}</p>
    </section>
    <section class="grid">
      {''.join(cards)}
    </section>
  </div>
  <script>
    const cards = document.querySelectorAll('.thread-card');
    const buttons = document.querySelectorAll('[data-review-filter]');
    buttons.forEach(button => {{
      button.addEventListener('click', () => {{
        buttons.forEach(item => item.classList.remove('active'));
        button.classList.add('active');
        const selected = button.dataset.reviewFilter;
        cards.forEach(card => {{
          card.hidden = !(selected === 'all' || card.dataset.reviewStatus === selected);
        }});
      }});
    }});
  </script>
</body>
</html>"""


def write_thread_review_index_site(
    workspace_dir: str | Path,
    output_dir: str | Path,
    *,
    generated_at: str,
    aspect_ratio: str = "16:9",
) -> dict[str, Any]:
    workspace_path = Path(workspace_dir).resolve()
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    item_states = load_all_item_lifecycle_states_from_workspace(workspace_path)
    entries: list[dict[str, Any]] = []
    for item_state in sorted(item_states, key=lambda payload: payload["item_ref"]["entity_id"]):
        bundle = build_thread_review_bundle_from_workspace(
            workspace_path,
            item_id=item_state["item_ref"]["entity_id"],
            generated_at=generated_at,
        )
        thread_slug = _slug(item_state["item_ref"]["entity_id"])
        thread_dir = output_root / "threads" / thread_slug
        paths = write_thread_review_package(bundle, thread_dir, aspect_ratio=aspect_ratio)
        entries.append(
            {
                "bundle": bundle,
                "thread_href": paths["thread_review_html"].relative_to(output_root).as_posix(),
                "markdown_href": paths["thread_review_markdown"].relative_to(output_root).as_posix(),
                "presentation_href": paths["presentation_html"].relative_to(output_root).as_posix(),
            }
        )

    entries.sort(key=lambda entry: _thread_review_sort_key(entry["bundle"]))
    index_path = output_root / "index.html"
    workspace_id = entries[0]["bundle"]["workspace_id"] if entries else workspace_path.name
    index_path.write_text(render_thread_review_index_html(entries, workspace_id=workspace_id, generated_at=generated_at), encoding="utf-8")
    return {
        "index_path": index_path,
        "thread_count": len(entries),
        "thread_paths": [entry["thread_href"] for entry in entries],
    }


def build_thread_review_release_bundle_from_workspace(
    workspace_dir: str | Path,
    *,
    item_id: str | None = None,
    generated_at: str,
    output_dir: str | Path,
    target_release: str = "v8_0_0",
) -> dict[str, Any]:
    workspace_path = Path(workspace_dir).resolve()
    output_root = Path(output_dir)
    thread_bundle = build_thread_review_bundle_from_workspace(
        workspace_path,
        item_id=item_id,
        generated_at=generated_at,
    )
    thread_output_dir = output_root / "thread-review"
    index_output_dir = output_root / "thread-review-index"
    package_paths = write_thread_review_package(thread_bundle, thread_output_dir)
    presentation_package = build_thread_review_presentation_package(thread_bundle)
    index_site = write_thread_review_index_site(
        workspace_path,
        index_output_dir,
        generated_at=generated_at,
    )

    publish_check = presentation_package["presentation_publish_check"]
    mode_counts = _thread_review_mode_counts(thread_bundle)
    deferred_sections = [section["title"] for section in thread_bundle["sections"] if section["backing_mode"] == "deferred"]
    package_ready = all(
        path.exists()
        for path in [
            package_paths["thread_review_html"],
            package_paths["thread_review_markdown"],
            package_paths["presentation_html"],
            package_paths["presentation_brief"],
            package_paths["presentation_publish_check"],
        ]
    )
    index_ready = index_site["index_path"].exists() and index_site["thread_count"] >= 1
    bounded_external_claim = (
        presentation_package["presentation_brief"]["redaction_policy"] == "internal_only"
        or not presentation_package["presentation_brief"]["customer_safe"]
    )
    manual_review_gap = thread_bundle["review_status"] == "pm_review_required"

    scenario_specs = [
        {
            "scenario_id": "scenario_thread_review_package",
            "name": "Single-thread package generation",
            "status": "passed" if package_ready else "failed",
            "metric_deltas": [
                {
                    "metric_name": "review_outputs_generated",
                    "baseline_value": 0.0,
                    "candidate_value": 3.0 if package_ready else 0.0,
                    "unit": "outputs",
                    "trend": "improved" if package_ready else "flat",
                },
                {
                    "metric_name": "artifact_backed_sections_visible",
                    "baseline_value": 0.0,
                    "candidate_value": float(mode_counts.get("artifact_backed", 0)),
                    "unit": "sections",
                    "trend": "improved" if mode_counts.get("artifact_backed", 0) > 0 else "flat",
                },
            ],
            "evidence_refs": [
                thread_bundle["thread_review_bundle_id"],
                presentation_package["presentation_brief"]["presentation_brief_id"],
                presentation_package["presentation_story"]["presentation_story_id"],
            ],
            "gaps": [] if package_ready else ["The thread review package did not render all expected review outputs."],
        },
        {
            "scenario_id": "scenario_thread_review_publishability",
            "name": "Governed presentation packaging",
            "status": "passed" if publish_check["publish_ready"] else "failed",
            "metric_deltas": [
                {
                    "metric_name": "publish_ready_surface",
                    "baseline_value": 0.0,
                    "candidate_value": 1.0 if publish_check["publish_ready"] else 0.0,
                    "unit": "boolean",
                    "trend": "improved" if publish_check["publish_ready"] else "flat",
                },
                {
                    "metric_name": "narrative_quality_score",
                    "baseline_value": 0.0,
                    "candidate_value": float(publish_check["narrative_quality_score"]),
                    "unit": "score",
                    "trend": "improved" if publish_check["narrative_quality_score"] > 0 else "flat",
                },
            ],
            "evidence_refs": [
                presentation_package["presentation_render_spec"]["render_spec_id"],
                presentation_package["presentation_publish_check"]["publish_check_id"],
            ],
            "gaps": publish_check["blocking_issues"][:3],
        },
        {
            "scenario_id": "scenario_thread_review_index",
            "name": "Workspace-scale thread review index",
            "status": "passed" if index_ready else "failed",
            "metric_deltas": [
                {
                    "metric_name": "indexed_threads",
                    "baseline_value": 0.0,
                    "candidate_value": float(index_site["thread_count"]),
                    "unit": "threads",
                    "trend": "improved" if index_site["thread_count"] > 0 else "flat",
                },
                {
                    "metric_name": "thread_level_deck_links",
                    "baseline_value": 0.0,
                    "candidate_value": float(index_site["thread_count"]),
                    "unit": "linked_decks",
                    "trend": "improved" if index_site["thread_count"] > 0 else "flat",
                },
            ],
            "evidence_refs": [thread_bundle["thread_review_bundle_id"], str(index_site["index_path"])],
            "gaps": [] if index_ready else ["The workspace-level thread review index did not render correctly."],
        },
        {
            "scenario_id": "scenario_thread_review_release_boundary",
            "name": "Bounded external release posture",
            "status": "watch" if bounded_external_claim or manual_review_gap or deferred_sections else "passed",
            "metric_deltas": [
                {
                    "metric_name": "bounded_release_claim",
                    "baseline_value": 0.0,
                    "candidate_value": 1.0,
                    "unit": "boolean",
                    "trend": "improved",
                },
                {
                    "metric_name": "customer_safe_publication",
                    "baseline_value": 0.0,
                    "candidate_value": 0.0 if bounded_external_claim else 1.0,
                    "unit": "boolean",
                    "trend": "flat" if bounded_external_claim else "improved",
                },
            ],
            "evidence_refs": [
                thread_bundle["thread_review_bundle_id"],
                presentation_package["presentation_brief"]["presentation_brief_id"],
            ],
            "gaps": _dedupe_strings(
                [
                    *(
                        ["The generated thread-review deck is intentionally internal-only and should not yet be claimed as a broad external PM web app."]
                        if bounded_external_claim
                        else []
                    ),
                    *(
                        ["The selected thread still requires PM review before broader external claims should be made."]
                        if manual_review_gap
                        else []
                    ),
                    *(
                        [f"Deferred lifecycle sections remain visible: {', '.join(deferred_sections[:3])}."]
                        if deferred_sections
                        else []
                    ),
                ]
            ),
        },
    ]

    failed_scenarios = [scenario for scenario in scenario_specs if scenario["status"] == "failed"]
    watch_scenarios = [scenario for scenario in scenario_specs if scenario["status"] == "watch"]
    runtime_status = "failed" if failed_scenarios else ("watch" if watch_scenarios else "passed")
    validation_status = "blocked" if failed_scenarios else ("ready_for_manual_validation" if watch_scenarios else "passed")
    reviewer_status = "block" if failed_scenarios else ("proceed" if publish_check["publish_ready"] else "revise")
    tester_status = "failed" if failed_scenarios else "passed"
    manual_policy_status = "pending" if validation_status != "passed" else "passed"
    release_status = "blocked" if failed_scenarios else ("watch" if watch_scenarios else "ready")
    gate_decision = "no_go" if failed_scenarios else ("conditional_go" if watch_scenarios else "go")

    item_slug = _slug(thread_bundle["item_ref"]["entity_id"])
    runtime_scenario_report = {
        "schema_version": "1.0.0",
        "runtime_scenario_report_id": f"runtime_scenario_report_{item_slug}_thread_review_release",
        "workspace_id": thread_bundle["workspace_id"],
        "baseline_version": "v7.3.0",
        "candidate_version": target_release.replace("_", ".").lstrip("v"),
        "status": runtime_status,
        "summary": (
            "The V8 thread-review capability now proves one canonical thread across HTML review, readable doc, governed deck, and workspace index surfaces."
            if runtime_status == "passed"
            else "The V8 thread-review capability is technically working, but the release boundary still stays bounded until manual review approves the exact external claim."
            if runtime_status == "watch"
            else "The V8 thread-review capability still has unresolved package or validation failures and should not cross the release boundary."
        ),
        "scenarios": scenario_specs,
        "generated_at": generated_at,
    }

    validation_lane_report = {
        "schema_version": "1.0.0",
        "validation_lane_report_id": f"validation_lane_report_{item_slug}_thread_review_release",
        "workspace_id": thread_bundle["workspace_id"],
        "artifact_ref": runtime_scenario_report["runtime_scenario_report_id"],
        "artifact_type": "runtime_scenario_report",
        "stage_name": "v8_0_thread_review_release_boundary",
        "validation_tier": "tier_2",
        "overall_status": validation_status,
        "review_summary": (
            "The V8 thread-review feature is proved across package generation, governed presentation reuse, and workspace-scale indexing, but manual review still controls the exact release claim."
            if validation_status == "ready_for_manual_validation"
            else "The V8 thread-review feature is fully release-ready under the current bounded claim."
            if validation_status == "passed"
            else "The V8 thread-review feature still has unresolved failures in package generation, publishability, or index coverage."
        ),
        "ai_reviewer_lane": {
            "status": reviewer_status,
            "reviewer_role": "AI Reviewer",
            "blocking_findings": [
                *[gap for scenario in failed_scenarios for gap in scenario["gaps"][:2]]
            ],
            "non_blocking_findings": _dedupe_strings(
                [
                    "The same canonical thread now renders as HTML, Markdown, and a governed presentation package.",
                    "The workspace-level index gives PMs a scalable entry point for large products with many feature threads.",
                    *(
                        ["The current release boundary correctly keeps the external claim bounded instead of overstating a general PM web app."]
                        if watch_scenarios
                        else []
                    ),
                ]
            ),
            "unresolved_questions": _dedupe_strings(
                [
                    *(
                        ["What is the first external user promise for thread review beyond internal dogfood and bounded demos?"]
                        if watch_scenarios
                        else []
                    ),
                    *thread_bundle["pinned_context"]["pending_questions"][:2],
                ]
            ),
        },
        "ai_tester_lane": {
            "status": tester_status,
            "tester_role": "AI Tester",
            "checks_run": [
                "Validated thread-review package generation across HTML review, Markdown doc, and governed presentation outputs.",
                "Validated presentation publish-check generation for the thread-review deck.",
                "Validated workspace-level thread-review index generation and linked thread subpages.",
                "Validated the release-boundary artifact bundle for the V8 thread-review claim.",
            ],
            "blocking_findings": [gap for scenario in failed_scenarios for gap in scenario["gaps"][:2]],
            "non_blocking_findings": _dedupe_strings(
                [
                    f"Artifact-backed sections remain explicit: {mode_counts.get('artifact_backed', 0)}.",
                    f"Deferred sections remain explicit: {mode_counts.get('deferred', 0)}.",
                ]
            ),
            "automation_gaps": _dedupe_strings(
                [
                    "Future releases should add customer-safe publication checks for thread-review packages.",
                    "Future releases should add broader distribution and shareability proof beyond local generated surfaces.",
                ]
            ),
        },
        "manual_validation_policy": {
            "required": True,
            "scope": "targeted",
            "owner_role": "PM Operator",
            "status": manual_policy_status,
            "rationale": "Thread review changes the external communication surface for ProductOS, so targeted PM validation remains required even when automated package checks pass.",
        },
        "referee_trigger": {
            "required": False,
            "rationale": "Reviewer and tester lanes agree on the bounded V8 claim and do not currently conflict.",
            "conflicting_lanes": [],
        },
        "governance_layer_refs": _dedupe_strings(
            [
                thread_bundle["thread_review_bundle_id"],
                *thread_bundle["pinned_context"]["source_artifact_ids"][:4],
                presentation_package["presentation_brief"]["presentation_brief_id"],
                presentation_package["presentation_publish_check"]["publish_check_id"],
                runtime_scenario_report["runtime_scenario_report_id"],
            ]
        ),
        "next_action": (
            "Run targeted PM validation on the bounded V8 thread-review claim and keep broader external-user claims deferred."
            if validation_status != "passed"
            else "Promote the bounded V8 thread-review capability as the governed review surface for canonical lifecycle items."
        ),
        "generated_at": generated_at,
    }

    manual_validation_record = {
        "schema_version": "1.0.0",
        "manual_validation_record_id": f"manual_validation_record_{item_slug}_thread_review_release",
        "workspace_id": thread_bundle["workspace_id"],
        "subject_ref": runtime_scenario_report["runtime_scenario_report_id"],
        "subject_type": "runtime_scenario_report",
        "validation_tier": "tier_2",
        "validator_role": "PM Operator",
        "scope": "targeted",
        "decision": "accept" if validation_status == "passed" else ("defer" if validation_status == "ready_for_manual_validation" else "revise"),
        "fit_notes": [
            "The V8 thread-review feature now gives one canonical item a readable, inspectable path from problem framing through release and outcome surfaces.",
            "The release claim stays correctly tied to generated repo-backed artifacts instead of a parallel web-app data model.",
        ],
        "required_follow_ups": _dedupe_strings(
            [
                "Define the first explicit external-user claim for thread review and keep it narrower than a general PM portal.",
                "Add customer-safe publication and sharing proof before broad external launch.",
            ]
        ),
        "related_validation_report_ref": validation_lane_report["validation_lane_report_id"],
        "final_approval": validation_status == "passed",
        "recorded_at": generated_at,
    }

    release_readiness = {
        "schema_version": "1.1.0",
        "release_readiness_id": f"release_readiness_{item_slug}_thread_review_release",
        "workspace_id": thread_bundle["workspace_id"],
        "feature_id": f"feature_{item_slug}_thread_review_release",
        "status": release_status,
        "launch_roles": [
            {
                "role_name": "Release owner",
                "responsibility": "Approve the bounded V8 thread-review release claim.",
                "assignment_status": "assigned",
                "owner_name": "ProductOS PM",
                "owner_function": "Product management",
            },
            {
                "role_name": "Design owner",
                "responsibility": "Validate that the generated thread package is reviewable at realistic PM density.",
                "assignment_status": "assigned",
                "owner_name": "ProductOS PM",
                "owner_function": "Review experience",
            },
            {
                "role_name": "Governance owner",
                "responsibility": "Keep external release claims aligned with package proof and customer-safe boundaries.",
                "assignment_status": "assigned",
                "owner_name": "ProductOS PM",
                "owner_function": "Release governance",
            },
        ],
        "checks": [
            {
                "name": "Thread-review package generation",
                "status": "passed" if package_ready else "failed",
                "notes": "HTML review, Markdown review, and governed deck outputs were generated from the same canonical thread bundle.",
            },
            {
                "name": "Governed presentation publish check",
                "status": "passed" if publish_check["publish_ready"] else "failed",
                "notes": "The thread-review deck can be evaluated through the existing presentation publish-check pipeline.",
            },
            {
                "name": "Workspace-scale thread index generation",
                "status": "passed" if index_ready else "failed",
                "notes": "Large-product review now has a portfolio-like index that links into thread-level packages.",
            },
            {
                "name": "Bounded external release posture",
                "status": "watch" if bounded_external_claim or manual_review_gap or deferred_sections else "passed",
                "notes": "The current claim should remain bounded to internal dogfood and controlled demos until customer-safe publication and PM signoff are explicit.",
            },
        ],
        "generated_at": generated_at,
    }

    release_gate_decision = {
        "schema_version": "1.0.0",
        "release_gate_decision_id": f"release_gate_decision_{item_slug}_thread_review_release",
        "workspace_id": thread_bundle["workspace_id"],
        "target_release": target_release,
        "decision": gate_decision,
        "pm_benchmark_ref": "pm_superpower_benchmark_ws_productos_v2_v4_0",
        "runtime_scenario_report_ref": runtime_scenario_report["runtime_scenario_report_id"],
        "release_readiness_ref": release_readiness["release_readiness_id"],
        "rationale": (
            "The V8 thread-review feature now proves a repo-backed PM review package and a workspace-scale index, but the external claim still stays intentionally bounded."
            if gate_decision == "conditional_go"
            else "The V8 thread-review feature is fully proved across package, index, and release-boundary checks."
            if gate_decision == "go"
            else "The V8 thread-review feature still has unresolved failures in package, publish-check, or index coverage."
        ),
        "next_action": (
            "Keep the claim bounded, complete targeted PM validation, and avoid broad external-user positioning until customer-safe publication proof exists."
            if gate_decision == "conditional_go"
            else "Promote the bounded V8 thread-review capability as part of the stable ProductOS review surface."
            if gate_decision == "go"
            else "Resolve the failed thread-review release checks before moving the V8 feature across the release boundary."
        ),
        "known_gaps": _dedupe_strings(
            [
                *(
                    ["The generated thread-review outputs are internal-only and not yet positioned as a customer-safe external PM web product."]
                    if bounded_external_claim
                    else []
                ),
                *(
                    ["The current thread still requires PM review before broader claims should be made."]
                    if manual_review_gap
                    else []
                ),
                *(
                    [f"Deferred lifecycle sections remain visible in the selected thread: {', '.join(deferred_sections[:3])}."]
                    if deferred_sections
                    else []
                ),
                *publish_check["blocking_issues"][:2],
            ]
        )
        or ["Targeted PM validation remains required before broader release claims."],
        "deferred_items": [
            "Customer-safe publication and sharing of thread-review packages.",
            "Broader external-user positioning beyond internal dogfood and controlled demos.",
            "A richer multi-user PM application surface with permissions, collaboration, and hosted distribution.",
        ],
        "blocker_categories": {
            "other_blockers": _dedupe_strings(
                [
                    *[gap for scenario in failed_scenarios for gap in scenario["gaps"][:2]],
                    *(
                        ["Release claim remains intentionally bounded while manual review is pending."]
                        if watch_scenarios and not failed_scenarios
                        else []
                    ),
                ]
            )
        },
        "generated_at": generated_at,
    }

    release_dir = output_root / "release"
    release_dir.mkdir(parents=True, exist_ok=True)
    release_bundle = {
        "runtime_scenario_report_thread_review_release": runtime_scenario_report,
        "validation_lane_report_thread_review_release": validation_lane_report,
        "manual_validation_record_thread_review_release": manual_validation_record,
        "release_readiness_thread_review_release": release_readiness,
        "release_gate_decision_thread_review_release": release_gate_decision,
    }
    release_file_paths = {}
    for name, payload in release_bundle.items():
        path = release_dir / f"{name}.json"
        _write_json(path, payload)
        release_file_paths[name] = path

    return {
        "thread_review_bundle": thread_bundle,
        "package_paths": package_paths,
        "index_site": index_site,
        "release_bundle": release_bundle,
        "release_file_paths": release_file_paths,
    }


def _payload_id(payload: dict[str, Any]) -> str | None:
    for key, value in payload.items():
        if key.endswith("_id") and key != "workspace_id" and isinstance(value, str):
            return value
    return None


def _load_workspace_artifacts_by_id(workspace_dir: Path | str) -> dict[str, dict[str, Any]]:
    artifacts_dir = Path(workspace_dir).resolve() / "artifacts"
    payloads: dict[str, dict[str, Any]] = {}
    for path in sorted(artifacts_dir.glob("*.json")):
        payload = _load_json(path)
        payload_id = _payload_id(payload)
        if payload_id is not None:
            payloads[payload_id] = payload
    return payloads


def _first_payload_for_prefixes(
    *,
    artifact_map: dict[str, dict[str, Any]],
    stage_artifact_ids: list[str],
    prefixes: list[str],
) -> dict[str, Any] | None:
    for artifact_id in stage_artifact_ids:
        if any(artifact_id.startswith(prefix) for prefix in prefixes) and artifact_id in artifact_map:
            return artifact_map[artifact_id]
    for artifact_id, payload in artifact_map.items():
        if any(artifact_id.startswith(prefix) for prefix in prefixes):
            return payload
    return None


def _all_payloads_for_prefixes(
    *,
    artifact_map: dict[str, dict[str, Any]],
    stage_artifact_ids: list[str],
    prefixes: list[str],
) -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for artifact_id in [*stage_artifact_ids, *artifact_map.keys()]:
        if artifact_id in seen_ids:
            continue
        if not any(artifact_id.startswith(prefix) for prefix in prefixes):
            continue
        payload = artifact_map.get(artifact_id)
        if payload is None:
            continue
        payloads.append(payload)
        seen_ids.add(artifact_id)
    return payloads


def _listify_strings(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        items: list[str] = []
        for item in value:
            if isinstance(item, str):
                items.append(item)
            elif isinstance(item, dict):
                for key in (
                    "statement",
                    "question",
                    "summary",
                    "title",
                    "name",
                    "description",
                    "responsibility",
                    "observed_signal",
                    "next_action",
                ):
                    candidate = item.get(key)
                    if isinstance(candidate, str):
                        items.append(candidate)
                        break
        return items
    return []


def _refs_from_evidence_refs(evidence_refs: Any) -> list[str]:
    refs: list[str] = []
    for item in evidence_refs or []:
        if isinstance(item, str):
            refs.append(item)
        elif isinstance(item, dict):
            candidate = item.get("source_id") or item.get("artifact_id") or item.get("path")
            if isinstance(candidate, str):
                refs.append(candidate)
    return refs


def _generic_confidence_summary(item_state: dict[str, Any]) -> str:
    stages = item_state["lifecycle_stages"]
    if all(stage["gate_status"] == "passed" for stage in stages):
        return "This thread is backed by a completed lifecycle trace with explicit downstream artifacts and passed gates."
    if any(stage["status"] == "in_progress" for stage in stages):
        return "This thread mixes completed and in-progress lifecycle stages; later-stage readiness should stay explicit rather than assumed."
    return "This thread is available for review, but significant stages remain not started."


def _build_action_item(
    *,
    action_id: str,
    title: str,
    rationale: str,
    priority: str,
    action_type: str,
    source_refs: list[str],
) -> dict[str, Any]:
    return {
        "action_id": action_id,
        "title": title,
        "rationale": rationale,
        "priority": priority,
        "action_type": action_type,
        "source_refs": source_refs,
    }


def _review_status_label(review_status: str) -> str:
    labels = {
        "pm_review_required": "PM review required",
        "ready_for_launch_review": "Ready for launch review",
        "stable_full_lifecycle": "Stable full lifecycle",
        "in_progress": "In progress",
    }
    return labels.get(review_status, review_status.replace("_", " "))


def _derive_review_actions_and_status(
    *,
    item_state: dict[str, Any],
    current_stage_map: dict[str, dict[str, Any]],
    adoption_review_queue: dict[str, Any] | None,
    outcome_review: dict[str, Any] | None,
    release_readiness: dict[str, Any] | None,
    release_note: dict[str, Any] | None,
) -> tuple[str, str, list[dict[str, Any]]]:
    actions: list[dict[str, Any]] = []
    product_slug = _slug(item_state["item_ref"]["entity_id"])
    review_items = (adoption_review_queue or {}).get("review_items", [])
    open_review_items = [item for item in review_items if item.get("status") == "open"]
    prototype_stage = current_stage_map["prototype_validation"]
    prd_stage = current_stage_map["prd_handoff"]
    story_stage = current_stage_map["story_planning"]
    acceptance_stage = current_stage_map["acceptance_ready"]
    release_stage = current_stage_map["release_readiness"]
    launch_stage = current_stage_map["launch_preparation"]
    outcome_stage = current_stage_map["outcome_review"]

    for item in open_review_items[:3]:
        actions.append(
            _build_action_item(
                action_id=item["review_item_id"],
                title=item["title"],
                rationale=item["recommended_reviewer_action"],
                priority=item.get("confidence", "medium"),
                action_type="review_queue",
                source_refs=item.get("source_refs", []),
            )
        )

    if prototype_stage["status"] == "in_progress":
        actions.append(
            _build_action_item(
                action_id=f"action_{product_slug}_prototype_gap",
                title="Add prototype proof before treating the thread as handoff-ready.",
                rationale=prototype_stage["summary"],
                priority="high",
                action_type="prototype_gap",
                source_refs=prototype_stage["artifact_ids"],
            )
        )

    if prd_stage["gate_status"] == "pending":
        actions.append(
            _build_action_item(
                action_id=f"action_{product_slug}_prd_review",
                title="Resolve PM review on the current PRD handoff.",
                rationale=prd_stage["summary"],
                priority="high",
                action_type="prd_review",
                source_refs=prd_stage["artifact_ids"],
            )
        )

    if story_stage["status"] == "completed" and acceptance_stage["status"] == "completed" and release_stage["status"] == "completed":
        actions.append(
            _build_action_item(
                action_id=f"action_{product_slug}_launch_progression",
                title="Keep release, launch, and outcome artifacts aligned to the same canonical item.",
                rationale=release_stage["summary"],
                priority="medium",
                action_type="stage_progression",
                source_refs=[
                    *release_stage["artifact_ids"],
                    *launch_stage["artifact_ids"],
                    *outcome_stage["artifact_ids"],
                ],
            )
        )

    if release_readiness is not None and outcome_stage["status"] == "completed":
        actions.append(
            _build_action_item(
                action_id=f"action_{product_slug}_stable_trace",
                title="Keep the full-lifecycle trace stable and reuse it for future communication surfaces.",
                rationale=(outcome_review or {}).get("next_action", "The full-lifecycle trace is complete and should remain the canonical review path."),
                priority="medium",
                action_type="stability",
                source_refs=[
                    *release_stage["artifact_ids"],
                    *launch_stage["artifact_ids"],
                    *outcome_stage["artifact_ids"],
                ],
            )
        )

    if release_note is not None and launch_stage["status"] == "completed":
        actions.append(
            _build_action_item(
                action_id=f"action_{product_slug}_launch_communication",
                title="Reuse launch communication without breaking lifecycle provenance.",
                rationale=release_note.get("summary", launch_stage["summary"]),
                priority="medium",
                action_type="launch_communication",
                source_refs=launch_stage["artifact_ids"],
            )
        )

    deduped_actions: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for action in actions:
        if action["action_id"] in seen_ids:
            continue
        deduped_actions.append(action)
        seen_ids.add(action["action_id"])

    priority_rank = {"high": 0, "medium": 1, "low": 2}
    deduped_actions.sort(key=lambda item: (priority_rank.get(item["priority"], 3), item["title"]))

    if open_review_items or prototype_stage["status"] == "in_progress" or prd_stage["gate_status"] == "pending":
        review_status = "pm_review_required"
        review_status_summary = "The thread is usable, but PM review must close proof or handoff gaps before it should advance."
    elif release_stage["status"] == "completed" and launch_stage["status"] != "completed":
        review_status = "ready_for_launch_review"
        review_status_summary = "Delivery and release-readiness proof are complete; the next review focus is launch communication."
    elif outcome_stage["status"] == "completed":
        review_status = "stable_full_lifecycle"
        review_status_summary = "The thread has explicit launch and outcome evidence and should now be kept stable as the canonical lifecycle review path."
    else:
        review_status = "in_progress"
        review_status_summary = "The thread is active and should move forward through the next bounded lifecycle review step."

    return review_status, review_status_summary, deduped_actions[:5]


def build_thread_review_bundle_from_workspace(
    workspace_dir: Path | str,
    *,
    item_id: str | None = None,
    generated_at: str,
) -> dict[str, Any]:
    workspace_path = Path(workspace_dir).resolve()
    item_state = load_item_lifecycle_state_from_workspace(workspace_path, item_id=item_id)
    artifact_map = _load_workspace_artifacts_by_id(workspace_path)
    stage_map = _stage_map(item_state)

    research_payloads = _all_payloads_for_prefixes(
        artifact_map=artifact_map,
        stage_artifact_ids=stage_map["research_synthesis"]["artifact_ids"],
        prefixes=["research_notebook", "research_brief", "competitor_dossier", "market_analysis_brief"],
    )
    research_notebook = _first_payload_for_prefixes(
        artifact_map=artifact_map,
        stage_artifact_ids=stage_map["research_synthesis"]["artifact_ids"],
        prefixes=["research_notebook"],
    )
    research_brief = _first_payload_for_prefixes(
        artifact_map=artifact_map,
        stage_artifact_ids=stage_map["research_synthesis"]["artifact_ids"],
        prefixes=["research_brief"],
    )
    problem_brief = _first_payload_for_prefixes(
        artifact_map=artifact_map,
        stage_artifact_ids=stage_map["problem_framing"]["artifact_ids"],
        prefixes=["problem_brief"],
    )
    segment_map = _first_payload_for_prefixes(
        artifact_map=artifact_map,
        stage_artifact_ids=stage_map["segmentation_and_personas"]["artifact_ids"],
        prefixes=["segment_map"],
    )
    persona_pack = _first_payload_for_prefixes(
        artifact_map=artifact_map,
        stage_artifact_ids=stage_map["segmentation_and_personas"]["artifact_ids"],
        prefixes=["persona_pack"],
    )
    idea_record = _first_payload_for_prefixes(
        artifact_map=artifact_map,
        stage_artifact_ids=stage_map["concept_shaping"]["artifact_ids"],
        prefixes=["idea_record"],
    )
    concept_brief = _first_payload_for_prefixes(
        artifact_map=artifact_map,
        stage_artifact_ids=stage_map["concept_shaping"]["artifact_ids"],
        prefixes=["concept_brief"],
    )
    prototype_record = _first_payload_for_prefixes(
        artifact_map=artifact_map,
        stage_artifact_ids=stage_map["prototype_validation"]["artifact_ids"],
        prefixes=["prototype_record"],
    )
    ux_design_review = _first_payload_for_prefixes(
        artifact_map=artifact_map,
        stage_artifact_ids=stage_map["prototype_validation"]["artifact_ids"],
        prefixes=["ux_design_review"],
    )
    prd = _first_payload_for_prefixes(
        artifact_map=artifact_map,
        stage_artifact_ids=stage_map["prd_handoff"]["artifact_ids"],
        prefixes=["prd"],
    )
    story_pack = _first_payload_for_prefixes(
        artifact_map=artifact_map,
        stage_artifact_ids=stage_map["story_planning"]["artifact_ids"],
        prefixes=["story_pack"],
    )
    acceptance_criteria = _first_payload_for_prefixes(
        artifact_map=artifact_map,
        stage_artifact_ids=stage_map["acceptance_ready"]["artifact_ids"],
        prefixes=["acceptance_criteria_set"],
    )
    release_readiness = _first_payload_for_prefixes(
        artifact_map=artifact_map,
        stage_artifact_ids=stage_map["release_readiness"]["artifact_ids"],
        prefixes=["release_readiness"],
    )
    release_note = _first_payload_for_prefixes(
        artifact_map=artifact_map,
        stage_artifact_ids=stage_map["launch_preparation"]["artifact_ids"],
        prefixes=["release_note"],
    )
    outcome_review = _first_payload_for_prefixes(
        artifact_map=artifact_map,
        stage_artifact_ids=stage_map["outcome_review"]["artifact_ids"],
        prefixes=["outcome_review"],
    )
    adoption_report = _first_payload_for_prefixes(
        artifact_map=artifact_map,
        stage_artifact_ids=[],
        prefixes=["workspace_adoption_report"],
    )
    adoption_review_queue = _first_payload_for_prefixes(
        artifact_map=artifact_map,
        stage_artifact_ids=[],
        prefixes=["adoption_review_queue"],
    )

    recommended_beachhead = None
    if segment_map is not None:
        recommended_beachhead_id = segment_map.get("recommended_beachhead_segment_id")
        recommended_beachhead = next(
            (segment["name"] for segment in segment_map.get("segments", []) if segment.get("segment_id") == recommended_beachhead_id),
            None,
        )

    source_artifact_ids = list(
        dict.fromkeys(
            [
                artifact_id
                for stage in item_state["lifecycle_stages"]
                for artifact_id in stage["artifact_ids"]
                if artifact_id in artifact_map
            ]
        )
    )

    sections = [
        _build_thread_review_section(
            section_id="problem",
            selector_key="problem_brief",
            title="Problem framing",
            headline="What problem the canonical item is solving.",
            summary=(problem_brief or {}).get("problem_summary", stage_map["problem_framing"]["summary"]),
            key_points=[
                *(
                    [
                        value
                        for value in [
                            (problem_brief or {}).get("strategic_fit_summary"),
                            (problem_brief or {}).get("why_this_problem_now"),
                            (problem_brief or {}).get("why_this_problem_for_this_segment"),
                        ]
                        if isinstance(value, str) and value
                    ]
                ),
            ]
            or [stage_map["problem_framing"]["summary"]],
            stage_states=[stage_map["problem_framing"]],
            artifact_ids=stage_map["problem_framing"]["artifact_ids"],
            source_refs=[
                *((problem_brief or {}).get("upstream_artifact_ids", [])),
                *_refs_from_evidence_refs((problem_brief or {}).get("evidence_refs")),
            ],
            backing_mode=_backing_mode(has_artifact_payload=problem_brief is not None, stage_states=[stage_map["problem_framing"]]),
        ),
        _build_thread_review_section(
            section_id="segments_personas",
            selector_key="segment_and_persona_pack",
            title="Segments and personas",
            headline="Who this item serves first.",
            summary=(
                f"Recommended beachhead: {recommended_beachhead}."
                if recommended_beachhead
                else stage_map["segmentation_and_personas"]["summary"]
            ),
            key_points=[
                *[
                    value
                    for value in [
                        (segment_map or {}).get("market_scope_summary"),
                        (segment_map or {}).get("segmentation_logic"),
                    ]
                    if isinstance(value, str) and value
                ],
                *[
                    persona.get("role")
                    for persona in (persona_pack or {}).get("personas", [])[:3]
                    if isinstance(persona.get("role"), str)
                ],
            ]
            or [stage_map["segmentation_and_personas"]["summary"]],
            stage_states=[stage_map["segmentation_and_personas"]],
            artifact_ids=stage_map["segmentation_and_personas"]["artifact_ids"],
            source_refs=list(dict.fromkeys([*((persona_pack or {}).get("source_artifact_ids", [])), *((segment_map or {}).get("source_artifact_ids", []))])),
            backing_mode=_backing_mode(
                has_artifact_payload=segment_map is not None or persona_pack is not None,
                stage_states=[stage_map["segmentation_and_personas"]],
            ),
        ),
        _build_thread_review_section(
            section_id="market_context",
            selector_key="research_context",
            title="Market and competitor context",
            headline="Research context behind the current wedge and stage posture.",
            summary=(research_brief or {}).get("summary", stage_map["research_synthesis"]["summary"]),
            key_points=[
                *[
                    item
                    for item in (
                        _listify_strings((research_brief or {}).get("strategic_implications"))
                        + _listify_strings((research_brief or {}).get("insights"))
                        + _listify_strings((research_notebook or {}).get("open_questions"))
                        + _listify_strings((next((payload.get("trend_summary") for payload in research_payloads if "trend_summary" in payload), None)))
                    )
                    if item
                ][:5],
            ]
            or [stage_map["research_synthesis"]["summary"]],
            stage_states=[stage_map["research_synthesis"]],
            artifact_ids=[_payload_id(payload) for payload in research_payloads if _payload_id(payload)],
            source_refs=list(
                dict.fromkeys(
                    [
                        *[ref for payload in research_payloads for ref in payload.get("source_note_card_ids", []) if isinstance(ref, str)],
                        *[ref for payload in research_payloads for ref in payload.get("research_notebook_ids", []) if isinstance(ref, str)],
                    ]
                )
            ),
            backing_mode=_backing_mode(
                has_artifact_payload=bool(research_payloads),
                stage_states=[stage_map["research_synthesis"]],
            ),
        ),
        _build_thread_review_section(
            section_id="concept",
            selector_key="concept_brief",
            title="Concept",
            headline="How the item is framed as a product concept.",
            summary=(concept_brief or {}).get("hypothesis", stage_map["concept_shaping"]["summary"]),
            key_points=[
                *[
                    value
                    for value in [
                        (concept_brief or {}).get("positioning_hypothesis"),
                        (concept_brief or {}).get("offering_hypothesis"),
                        (concept_brief or {}).get("wedge_hypothesis"),
                        (concept_brief or {}).get("why_now"),
                        (idea_record or {}).get("summary"),
                    ]
                    if isinstance(value, str) and value
                ][:5],
            ]
            or [stage_map["concept_shaping"]["summary"]],
            stage_states=[stage_map["concept_shaping"]],
            artifact_ids=stage_map["concept_shaping"]["artifact_ids"],
            source_refs=list(dict.fromkeys([*((concept_brief or {}).get("idea_record_ids", [])), *((concept_brief or {}).get("strategy_artifact_ids", []))])),
            backing_mode=_backing_mode(
                has_artifact_payload=concept_brief is not None or idea_record is not None,
                stage_states=[stage_map["concept_shaping"]],
            ),
        ),
        _build_thread_review_section(
            section_id="prototype",
            selector_key="prototype_record",
            title="Prototype",
            headline="Whether the concept has interaction or design proof.",
            summary=(
                (prototype_record or {}).get("objective")
                or (ux_design_review or {}).get("request_summary")
                or stage_map["prototype_validation"]["summary"]
            ),
            key_points=[
                *[
                    value
                    for value in [
                        (prototype_record or {}).get("uncertainty_statement"),
                        (prototype_record or {}).get("primary_test_scenario"),
                        (prototype_record or {}).get("recommendation"),
                    ]
                    if isinstance(value, str) and value
                ],
                *_listify_strings((prototype_record or {}).get("learnings"))[:2],
            ]
            or [stage_map["prototype_validation"]["summary"]],
            stage_states=[stage_map["prototype_validation"]],
            artifact_ids=stage_map["prototype_validation"]["artifact_ids"],
            source_refs=list(dict.fromkeys([*((ux_design_review or {}).get("source_artifact_ids", []))])),
            backing_mode=_backing_mode(
                has_artifact_payload=prototype_record is not None or ux_design_review is not None,
                stage_states=[stage_map["prototype_validation"]],
            ),
        ),
        _build_thread_review_section(
            section_id="prd",
            selector_key="prd",
            title="PRD",
            headline="What is ready for handoff and what still needs review.",
            summary=(prd or {}).get("outcome_summary", stage_map["prd_handoff"]["summary"]),
            key_points=[
                *[
                    value
                    for value in [
                        (prd or {}).get("problem_summary"),
                        (prd or {}).get("scope_summary"),
                    ]
                    if isinstance(value, str) and value
                ]
            ]
            or [stage_map["prd_handoff"]["summary"]],
            stage_states=[stage_map["prd_handoff"]],
            artifact_ids=stage_map["prd_handoff"]["artifact_ids"],
            source_refs=(prd or {}).get("upstream_artifact_ids", []),
            backing_mode=_backing_mode(has_artifact_payload=prd is not None, stage_states=[stage_map["prd_handoff"]]),
        ),
        _build_thread_review_section(
            section_id="delivery",
            selector_key="delivery_scope",
            title="Story pack and acceptance",
            headline="How delivery scope is attached to the same item.",
            summary=(
                (story_pack or {}).get("stories", [{}])[0].get("narrative")
                or stage_map["story_planning"]["summary"]
            ),
            key_points=[
                *[
                    story.get("title")
                    for story in (story_pack or {}).get("stories", [])[:2]
                    if isinstance(story.get("title"), str)
                ],
                *_listify_strings((acceptance_criteria or {}).get("criteria"))[:3],
            ]
            or [stage_map["story_planning"]["summary"], stage_map["acceptance_ready"]["summary"]],
            stage_states=[stage_map["story_planning"], stage_map["acceptance_ready"]],
            artifact_ids=[*stage_map["story_planning"]["artifact_ids"], *stage_map["acceptance_ready"]["artifact_ids"]],
            source_refs=[ref.get("path") for story in (story_pack or {}).get("stories", []) for ref in story.get("implementation_context_refs", []) if isinstance(ref.get("path"), str)],
            backing_mode=_backing_mode(
                has_artifact_payload=story_pack is not None or acceptance_criteria is not None,
                stage_states=[stage_map["story_planning"], stage_map["acceptance_ready"]],
            ),
        ),
        _build_thread_review_section(
            section_id="release_readiness",
            selector_key="release_readiness",
            title="Release readiness",
            headline="Whether the item is ready for release movement.",
            summary=(
                (release_readiness or {}).get("decision_summary")
                or (release_readiness or {}).get("status")
                or stage_map["release_readiness"]["summary"]
            ),
            key_points=[
                *[
                    role.get("responsibility")
                    for role in (release_readiness or {}).get("launch_roles", [])[:3]
                    if isinstance(role.get("responsibility"), str)
                ],
                *[
                    check.get("notes")
                    for check in (release_readiness or {}).get("checks", [])[:2]
                    if isinstance(check.get("notes"), str)
                ],
            ]
            or [stage_map["release_readiness"]["summary"]],
            stage_states=[stage_map["release_readiness"]],
            artifact_ids=stage_map["release_readiness"]["artifact_ids"],
            source_refs=[],
            backing_mode=_backing_mode(
                has_artifact_payload=release_readiness is not None,
                stage_states=[stage_map["release_readiness"]],
            ),
        ),
        _build_thread_review_section(
            section_id="launch",
            selector_key="release_note",
            title="Launch communication",
            headline="How launch-facing communication stays attached to the canonical item.",
            summary=(release_note or {}).get("summary", stage_map["launch_preparation"]["summary"]),
            key_points=[
                *[
                    value
                    for value in [
                        (release_note or {}).get("classification_rationale"),
                        (release_note or {}).get("audience"),
                        (release_note or {}).get("change_classification"),
                    ]
                    if isinstance(value, str) and value
                ]
            ]
            or [stage_map["launch_preparation"]["summary"]],
            stage_states=[stage_map["launch_preparation"]],
            artifact_ids=stage_map["launch_preparation"]["artifact_ids"],
            source_refs=(release_note or {}).get("feature_ids", []),
            backing_mode=_backing_mode(
                has_artifact_payload=release_note is not None,
                stage_states=[stage_map["launch_preparation"]],
            ),
        ),
        _build_thread_review_section(
            section_id="outcome_review",
            selector_key="outcome_review",
            title="Outcome review",
            headline="What the post-release learning says about the item.",
            summary=(outcome_review or {}).get("review_scope", stage_map["outcome_review"]["summary"]),
            key_points=[
                *_listify_strings((outcome_review or {}).get("target_outcomes"))[:3],
                *_listify_strings((outcome_review or {}).get("adoption_notes"))[:2],
                *[
                    value
                    for value in [(outcome_review or {}).get("next_action")]
                    if isinstance(value, str) and value
                ],
            ]
            or [stage_map["outcome_review"]["summary"]],
            stage_states=[stage_map["outcome_review"]],
            artifact_ids=stage_map["outcome_review"]["artifact_ids"],
            source_refs=(outcome_review or {}).get("evidence_refs", []),
            backing_mode=_backing_mode(
                has_artifact_payload=outcome_review is not None,
                stage_states=[stage_map["outcome_review"]],
            ),
        ),
    ]

    pending_questions = list(
        dict.fromkeys(
            [
                *item_state.get("pending_questions", []),
                *((adoption_report or {}).get("unresolved_questions", [])),
                *[question.get("question") for question in (research_brief or {}).get("external_research_questions", []) if isinstance(question.get("question"), str)],
                *((outcome_review or {}).get("unresolved_pain_points", [])),
            ]
        )
    )
    key_risks = (
        [item.get("title") for item in (adoption_review_queue or {}).get("review_items", []) if isinstance(item.get("title"), str)]
        or _listify_strings((research_brief or {}).get("known_gaps"))
        or item_state.get("blocked_reasons", [])
    )
    decisions = list(
        dict.fromkeys(
            [
                *[
                    value
                    for value in [
                        (research_brief or {}).get("recommendation"),
                        (release_readiness or {}).get("status"),
                        (outcome_review or {}).get("next_action"),
                    ]
                    if isinstance(value, str) and value
                ],
                *[event.get("summary") for event in item_state.get("audit_log", [])[-3:] if isinstance(event.get("summary"), str)],
            ]
        )
    )
    review_status, review_status_summary, action_items = _derive_review_actions_and_status(
        item_state=item_state,
        current_stage_map=stage_map,
        adoption_review_queue=adoption_review_queue,
        outcome_review=outcome_review,
        release_readiness=release_readiness,
        release_note=release_note,
    )

    return {
        "schema_version": "1.0.0",
        "thread_review_bundle_id": f"thread_review_bundle_{_slug(item_state['item_ref']['entity_id'])}",
        "workspace_id": item_state["workspace_id"],
        "item_ref": item_state["item_ref"],
        "title": f"Thread Review: {item_state['title']}",
        "current_stage": item_state["current_stage"],
        "overall_status": item_state["overall_status"],
        "review_status": review_status,
        "review_status_summary": review_status_summary,
        "stage_rail": [
            {
                "stage_key": stage["stage_key"],
                "title": stage["stage_key"].replace("_", " ").title(),
                "status": stage["status"],
                "gate_status": stage["gate_status"],
                "artifact_ids": stage["artifact_ids"],
                "summary": stage["summary"],
            }
            for stage in item_state["lifecycle_stages"]
        ],
        "sections": sections,
        "action_items": action_items,
        "pinned_context": {
            "target_segments": [ref["entity_id"] for ref in item_state["target_segment_refs"]],
            "target_personas": [ref["entity_id"] for ref in item_state["target_persona_refs"]],
            "pending_questions": pending_questions,
            "key_risks": key_risks,
            "decisions": decisions,
            "source_artifact_ids": source_artifact_ids,
            "confidence_summary": (adoption_report or {}).get("confidence_summary", _generic_confidence_summary(item_state)),
        },
        "recommended_next_step": (
            action_items[0]["title"]
            if action_items
            else decisions[0]
            if decisions
            else "Review the current stage and resolve the highest-risk open question before moving the item forward."
        ),
        "generated_at": generated_at,
    }


def _build_snapshot(
    *,
    workspace_id: str,
    product_slug: str,
    item_state: dict[str, Any],
    focus_area: str,
    summary: str,
    created_at: str,
) -> dict[str, Any]:
    included_stage_keys = _FOCUS_STAGE_KEYS[focus_area]
    stage_map = {
        stage["stage_key"]: stage
        for stage in item_state["lifecycle_stages"]
        if stage["stage_key"] in included_stage_keys
    }
    stage_summaries = []
    artifact_counts: Counter[str] = Counter()
    gate_counts = {"passed": 0, "pending": 0, "blocked": 0, "not_started": 0}
    for stage_key in included_stage_keys:
        stage = stage_map[stage_key]
        gate_counts[stage["gate_status"]] += 1
        for artifact_id in stage["artifact_ids"]:
            artifact_counts[_artifact_kind(artifact_id)] += 1
        stage_summaries.append(
            {
                "stage_key": stage_key,
                "item_ids": [item_state["item_ref"]["entity_id"]],
                "artifact_ids": stage["artifact_ids"],
                "gate_status_counts": {
                    "passed": 1 if stage["gate_status"] == "passed" else 0,
                    "pending": 1 if stage["gate_status"] == "pending" else 0,
                    "blocked": 1 if stage["gate_status"] == "blocked" else 0,
                    "not_started": 1 if stage["gate_status"] == "not_started" else 0,
                },
                "summary": stage["summary"],
            }
        )

    return {
        "schema_version": "1.0.0",
        "lifecycle_stage_snapshot_id": f"lifecycle_stage_snapshot_{focus_area}_{product_slug}",
        "workspace_id": workspace_id,
        "focus_area": focus_area,
        "snapshot_summary": summary,
        "item_count": 1,
        "segment_count": len(item_state["target_segment_refs"]),
        "persona_count": len(item_state["target_persona_refs"]),
        "artifact_counts": dict(artifact_counts),
        "active_item_ids": [item_state["item_ref"]["entity_id"]],
        "gate_counts": gate_counts,
        "stage_summaries": stage_summaries,
        "created_at": created_at,
    }


def build_workspace_adoption_bundle_from_source(
    root_dir: Path | str,
    *,
    source_dir: Path | str,
    workspace_id: str,
    name: str,
    generated_at: str,
    review_threshold: str = "medium",
) -> dict[str, dict[str, Any]]:
    root = Path(root_dir).resolve()
    source = Path(source_dir).resolve()
    if not source.exists():
        raise FileNotFoundError(f"Source workspace does not exist: {source}")

    product_slug = _slug(name)
    source_files = [_classify_file(source, path) for path in _visible_files(source)]
    file_counts = Counter(item["classification"] for item in source_files)
    context = _infer_codesync_context(source)
    review_items = _build_review_items(product_slug, generated_at, review_threshold)

    opportunity_id = f"opp_{product_slug}_workflow_control"
    feature_id = f"feature_{product_slug}_launch_lane"
    segment_ids = [
        "segment_physician_led_multisite_primary_care",
        "segment_broader_ipa_networks",
        "segment_specialty_auth_heavy_groups",
    ]
    persona_ids = [
        "persona_ipa_executive",
        "persona_rcm_director",
        "persona_practice_manager",
    ]
    source_note_cards = _build_source_note_cards(
        source_dir=source,
        workspace_id=workspace_id,
        product_slug=product_slug,
        generated_at=generated_at,
        opportunity_id=opportunity_id,
        feature_id=feature_id,
    )
    source_note_card_ids = [payload["source_note_card_id"] for payload in source_note_cards.values()]

    research_notebook = _load_template_artifact(root, "research_notebook.json")
    research_notebook.update(
        {
            "research_notebook_id": f"research_notebook_{product_slug}",
            "workspace_id": workspace_id,
            "title": f"Research notebook: {name} workspace adoption",
            "research_question": f"How should ProductOS convert the existing {name} research pack into governed product artifacts and a bounded launch-lane plan?",
            "source_note_card_ids": source_note_card_ids,
            "synthesis_hypothesis": context["source_summary"],
            "ordered_sections": [
                "market timing and wedge",
                "segment and persona priority",
                "launch-lane pilot logic",
                "proof gaps and review requirements",
            ],
            "open_questions": [
                "Which customer-facing claims can move from inferred to observed after PM review?",
                "What explicit prototype or pilot evidence must exist before the PRD is treated as ready for handoff?",
            ],
            "created_at": generated_at,
        }
    )

    research_brief = copy.deepcopy(_load_json(root / "core" / "examples" / "artifacts" / "research_brief.example.json"))
    research_brief.update(
        {
            "research_brief_id": f"research_brief_{product_slug}",
            "workspace_id": workspace_id,
            "title": f"Research Brief: {name} workflow control wedge",
            "research_question": f"Where does {name} have the strongest initial wedge across ambulatory patient access, RCM, and coordination workflows?",
            "summary": context["wedge"],
            "strategic_implications": [
                "The first launch lane should stay narrow enough to prove control and ROI quickly.",
                "ProductOS must keep observed evidence separate from inferred product-surface claims during adoption.",
            ],
            "source_note_card_ids": [
                source_note_cards["source_note_card_executive_brief"]["source_note_card_id"],
                source_note_cards["source_note_card_self_analysis"]["source_note_card_id"],
            ],
            "research_notebook_ids": [research_notebook["research_notebook_id"]],
            "target_segment_refs": [
                {"entity_type": "segment", "entity_id": segment_ids[0]},
            ],
            "target_persona_refs": [
                {"entity_type": "persona", "entity_id": persona_ids[0]},
                {"entity_type": "persona", "entity_id": persona_ids[1]},
            ],
            "linked_entity_refs": [
                {"entity_type": "opportunity", "entity_id": opportunity_id},
                {"entity_type": "feature", "entity_id": feature_id},
            ],
            "insights": [
                {
                    "insight_id": f"insight_{product_slug}_operating_layer",
                    "statement": context["wedge"],
                    "evidence_strength": "moderate",
                    "claim_mode": "inferred",
                    "next_validation_step": "Validate the wedge against live customer language, competitor positioning, and one external proof source before using it as a public claim.",
                    "supporting_source_note_card_ids": [
                        source_note_cards["source_note_card_executive_brief"]["source_note_card_id"],
                    ],
                },
                {
                    "insight_id": f"insight_{product_slug}_beachhead",
                    "statement": f"The best initial buyer context is {context['best_beachhead']}",
                    "evidence_strength": "strong",
                    "claim_mode": "observed",
                    "next_validation_step": "Confirm the beachhead still matches real buying urgency and current budget ownership before broadening the segment claim.",
                    "supporting_source_note_card_ids": [
                        source_note_cards["source_note_card_segment_map"]["source_note_card_id"],
                    ],
                },
                {
                    "insight_id": f"insight_{product_slug}_launch_lane",
                    "statement": context["launch_lane"],
                    "evidence_strength": "strong",
                    "claim_mode": "observed",
                    "next_validation_step": "Pressure-test the initial launch lane with one customer workflow owner and one measurable pilot success metric.",
                    "supporting_source_note_card_ids": [
                        source_note_cards["source_note_card_pilot_proposal"]["source_note_card_id"],
                    ],
                },
            ],
            "contradictions": [
                {
                    "statement": "The current research supports a broad platform narrative, but launch success still depends on one narrow workflow lane first.",
                    "severity": "moderate",
                    "supporting_source_note_card_ids": [
                        source_note_cards["source_note_card_self_analysis"]["source_note_card_id"],
                        source_note_cards["source_note_card_pilot_proposal"]["source_note_card_id"],
                    ],
                }
            ],
            "known_gaps": [
                context["proof_gap"],
                "The current source pack still needs explicit external proof for quantified before-after outcomes and customer-reference quality evidence.",
                "Security, auditability, and implementation-risk claims should not be treated as externally validated until they are backed by named controls and review evidence.",
            ],
            "external_research_questions": [
                {
                    "question_id": f"research_q_{product_slug}_outcomes_proof",
                    "question": "What observed customer evidence can validate the strongest ROI and workflow outcome claims in the current wedge narrative?",
                    "why_it_matters": "External packaging should not overstate impact without specific proof.",
                    "recommended_source_type": "customer_evidence",
                    "priority": "high",
                },
                {
                    "question_id": f"research_q_{product_slug}_security_controls",
                    "question": "Which security, auditability, and compliance controls can be stated as observed product facts versus roadmap or implementation assumptions?",
                    "why_it_matters": "Customer-facing pilots need clear risk boundaries and proof language.",
                    "recommended_source_type": "security_review",
                    "priority": "high",
                },
                {
                    "question_id": f"research_q_{product_slug}_competitive_wedge",
                    "question": "How does the proposed workflow-control launch lane compare with current competitor positioning and incumbent alternatives in the same operating context?",
                    "why_it_matters": "The PM needs a sharper wedge than generic platform language before external release.",
                    "recommended_source_type": "competitor_research",
                    "priority": "medium",
                },
            ],
            "synthesis_provenance": [
                "Synthesized from the CodeSync executive brief, self-analysis, segment map, persona pack, and customer pilot proposal.",
                "Observed versus inferred claim modes are kept explicit so external research can refine the product definition rather than overwrite the source corpus.",
            ],
            "recommendation": "advance_to_problem_brief",
            "created_at": generated_at,
        }
    )

    idea_record = _load_template_artifact(root, "idea_record.json")
    idea_record.update(
        {
            "idea_record_id": f"idea_record_{product_slug}",
            "workspace_id": workspace_id,
            "title": f"{name} workspace adoption wedge",
            "summary": context["wedge"],
            "source_type": "other",
            "target_segment_refs": [{"entity_type": "segment", "entity_id": segment_ids[0]}],
            "target_persona_refs": [{"entity_type": "persona", "entity_id": persona_ids[0]}],
            "linked_entity_refs": [{"entity_type": "opportunity", "entity_id": opportunity_id}],
            "created_at": generated_at,
        }
    )

    problem_brief = _load_template_artifact(root, "problem_brief.json")
    problem_brief.update(
        {
            "problem_brief_id": f"problem_brief_{product_slug}",
            "workspace_id": workspace_id,
            "title": f"Problem brief: {name} workspace adoption",
            "problem_summary": "The current CodeSync work is strategically rich, but it is trapped in notes, research docs, and presentation material rather than governed product state.",
            "strategic_fit_summary": "ProductOS can unlock the value of the existing research by converting it into artifact-backed product definition and a bounded launch-lane plan.",
            "why_this_problem_now": context["proof_gap"],
            "why_this_problem_for_this_segment": f"The immediate segment is {context['best_beachhead']}",
            "target_segment_refs": [{"entity_type": "segment", "entity_id": segment_ids[0]}],
            "target_persona_refs": [
                {"entity_type": "persona", "entity_id": persona_ids[0]},
                {"entity_type": "persona", "entity_id": persona_ids[1]},
                {"entity_type": "persona", "entity_id": persona_ids[2]},
            ],
            "linked_entity_refs": [
                {"entity_type": "problem", "entity_id": f"problem_{product_slug}_fragmented_workflows"},
                {"entity_type": "opportunity", "entity_id": opportunity_id},
            ],
            "evidence_refs": [
                {
                    "source_type": "research",
                    "source_id": research_brief["research_brief_id"],
                    "justification": "The adopted research brief identifies the launch lane, proof gaps, and target buyer context.",
                }
            ],
            "upstream_artifact_ids": [
                research_notebook["research_notebook_id"],
                research_brief["research_brief_id"],
                f"segment_map_{product_slug}",
                f"persona_pack_{product_slug}",
            ],
            "created_at": generated_at,
        }
    )

    concept_brief = _load_template_artifact(root, "concept_brief.json")
    concept_brief.update(
        {
            "concept_brief_id": f"concept_brief_{product_slug}",
            "workspace_id": workspace_id,
            "title": f"Concept brief: {name} workflow control adoption",
            "hypothesis": f"If ProductOS converts the existing {name} notes and research into first-class artifacts, the team can move faster without losing inference discipline.",
            "positioning_hypothesis": f"{name} should be positioned as a governed workflow control layer above incumbent systems.",
            "offering_hypothesis": "The first offering should be a narrow launch lane proving workflow control, not a broad all-workflows promise.",
            "wedge_hypothesis": context["launch_lane"],
            "why_now": "The research pack is already mature enough to justify an adopted PRD path, but not mature enough to rely on notes alone.",
            "why_us": "ProductOS can preserve provenance, confidence, and lifecycle traceability while turning the notes-first workspace into governed state.",
            "advantage_hypothesis": "A workspace adoption path converts strong research into repeatable product state faster than manual reconstruction.",
            "idea_record_ids": [idea_record["idea_record_id"]],
            "strategy_artifact_ids": [research_brief["research_brief_id"]],
            "target_segment_refs": [{"entity_type": "segment", "entity_id": segment_ids[0]}],
            "target_persona_refs": [
                {"entity_type": "persona", "entity_id": persona_ids[0]},
                {"entity_type": "persona", "entity_id": persona_ids[1]},
            ],
            "linked_entity_refs": [{"entity_type": "feature", "entity_id": feature_id}],
            "must_be_true_assumptions": [
                "The launch lane can prove value without replacing the EHR or clearinghouse stack.",
                "Review queues can keep commercial and compliance uncertainty visible instead of hidden in slide language.",
            ],
            "created_at": generated_at,
        }
    )

    segment_map = _load_template_artifact(root, "segment_map.json")
    segment_map.update(
        {
            "segment_map_id": f"segment_map_{product_slug}",
            "workspace_id": workspace_id,
            "title": f"Segment map: {name} workspace adoption",
            "market_name": "Ambulatory workflow control software",
            "market_scope_summary": "Organizations needing workflow control across patient access, billing execution, denial prevention, and coordination without full-stack replacement.",
            "segmentation_lens": "workflow_maturity",
            "segmentation_logic": "Segments are separated by workflow fragmentation, payer complexity, multi-entity coordination, and ability to buy a narrow launch lane.",
            "segments": [
                {
                    "segment_id": segment_ids[0],
                    "name": "Physician-led multi-site primary care groups",
                    "definition": "Primary care or internal medicine groups operating with IPA-like complexity, central billing, and meaningful payer friction.",
                    "qualifying_traits": ["central billing", "multi-site coordination"],
                    "core_job": "Reduce handoff failure and improve workflow control across patient access and reimbursement operations.",
                    "struggle_moments": ["Prior authorization delays create downstream denials.", "No single workflow layer connects access, billing, and care follow-up."],
                    "primary_value_drivers": ["Reduced manual touches", "Better workflow visibility"],
                    "buying_context": "Executive and operations-led buying motion with strong ROI expectations.",
                    "adoption_constraints": ["The launch lane must be narrow.", "Proof must come before broad platform expansion."],
                    "posture_fit": [
                        {
                            "posture": "niche",
                            "fit": "strong",
                            "rationale": "The segment values a focused workflow-control wedge more than a broad generic AI story.",
                        }
                    ],
                    "best_fit_posture": "niche",
                    "solution_entry_points": ["Eligibility and prior authorization control", "Denial prevention expansion after proof"],
                    "confidence": "high",
                    "attractiveness": "high",
                    "urgency": "high",
                    "evidence_refs": ["codesync_segment_signal_1"],
                },
                {
                    "segment_id": segment_ids[1],
                    "name": "Broader physician-led IPA networks",
                    "definition": "Distributed ambulatory organizations coordinating across practices, contracts, and service lines.",
                    "qualifying_traits": ["cross-practice operations", "payer complexity"],
                    "core_job": "Create one operating view across locations, queues, and payer-sensitive workflows.",
                    "struggle_moments": ["Workflow ownership is fragmented across teams.", "Operational visibility does not map cleanly to financial outcomes."],
                    "primary_value_drivers": ["Cross-entity visibility", "Governed workflow routing"],
                    "buying_context": "Executive plus platform-operations sponsorship.",
                    "adoption_constraints": ["Broader scope raises implementation risk.", "The first lane must already be repeatable."],
                    "posture_fit": [
                        {
                            "posture": "niche",
                            "fit": "viable",
                            "rationale": "The segment is attractive after the first lane is proven.",
                        }
                    ],
                    "best_fit_posture": "niche",
                    "solution_entry_points": ["Launch-lane repetition", "Adjacent denial and appeal workflows"],
                    "confidence": "moderate",
                    "attractiveness": "high",
                    "urgency": "medium",
                    "evidence_refs": ["codesync_segment_signal_2"],
                },
                {
                    "segment_id": segment_ids[2],
                    "name": "Specialty groups with heavy auth and denial burden",
                    "definition": "Specialty practices with repeated payer friction and measurable administrative pain.",
                    "qualifying_traits": ["high auth burden", "specialty payer nuance"],
                    "core_job": "Reduce repeated high-friction administrative steps without destabilizing current operations.",
                    "struggle_moments": ["Payer-specific documentation and approval steps create rework.", "Specialty nuance increases proof demands."],
                    "primary_value_drivers": ["Faster queue handling", "Better denial prevention"],
                    "buying_context": "Specialty operations and revenue leadership.",
                    "adoption_constraints": ["Category fit must be clearer.", "Launch only after primary-care proof is credible."],
                    "posture_fit": [
                        {
                            "posture": "niche",
                            "fit": "viable",
                            "rationale": "The segment is promising, but specialty nuance should not be the first launch wedge.",
                        }
                    ],
                    "best_fit_posture": "niche",
                    "solution_entry_points": ["Payer workflow automation", "Appeal and denial workflows"],
                    "confidence": "moderate",
                    "attractiveness": "medium",
                    "urgency": "medium",
                    "evidence_refs": ["codesync_segment_signal_3"],
                },
            ],
            "recommended_beachhead_segment_id": segment_ids[0],
            "created_at": generated_at,
        }
    )

    persona_pack = _load_template_artifact(root, "persona_pack.json")
    persona_pack.update(
        {
            "persona_pack_id": f"persona_pack_{product_slug}",
            "workspace_id": workspace_id,
            "title": f"Persona pack: {name} workspace adoption",
            "segment_refs": [{"entity_type": "segment", "entity_id": segment_id} for segment_id in segment_ids],
            "personas": [
                {
                    "persona_ref": {"entity_type": "persona", "entity_id": persona_ids[0]},
                    "role": "IPA executive / platform buyer",
                    "goals": ["Gain executive visibility into workflow and financial impact.", "Prove ROI quickly with one launch lane."],
                    "pains": ["Too many disconnected tools.", "No clean line from operational chaos to financial impact."],
                },
                {
                    "persona_ref": {"entity_type": "persona", "entity_id": persona_ids[1]},
                    "role": "Central RCM director",
                    "goals": ["Reduce preventable denials.", "Improve queue control and payer-specific visibility."],
                    "pains": ["Manual payer portals.", "No single source of truth for operational performance."],
                },
                {
                    "persona_ref": {"entity_type": "persona", "entity_id": persona_ids[2]},
                    "role": "Practice manager / front office lead",
                    "goals": ["Reduce registration and authorization friction.", "Keep patient access smoother without adding staff burden."],
                    "pains": ["Incomplete intake.", "Eligibility surprises and weak handoffs into billing."],
                },
            ],
            "source_artifact_ids": [segment_map["segment_map_id"]],
            "created_at": generated_at,
        }
    )

    prd = _load_template_artifact(root, "prd.json")
    prd.update(
        {
            "prd_id": f"prd_{product_slug}",
            "workspace_id": workspace_id,
            "title": f"PRD: {name} workspace adoption launch lane",
            "problem_summary": "CodeSync has a strong notes-first research pack, but it lacks first-class ProductOS product definition artifacts and a bounded launch-lane PRD.",
            "outcome_summary": "The adopted workspace should make CodeSync reviewable as a governed workflow-control product with one explicit launch lane and a visible review queue for unresolved proof gaps.",
            "scope_summary": "Adopt the existing research pack into ProductOS, keep the first launch lane focused on eligibility and prior authorization control, and preserve explicit review gates for claims, security, and commercial packaging.",
            "target_segment_refs": [{"entity_type": "segment", "entity_id": segment_ids[0]}],
            "target_persona_refs": [{"entity_type": "persona", "entity_id": persona_ids[0]}],
            "linked_entity_refs": [{"entity_type": "feature", "entity_id": feature_id}],
            "upstream_artifact_ids": [
                research_notebook["research_notebook_id"],
                research_brief["research_brief_id"],
                problem_brief["problem_brief_id"],
                concept_brief["concept_brief_id"],
                segment_map["segment_map_id"],
                persona_pack["persona_pack_id"],
            ],
            "generated_at": generated_at,
        }
    )

    intake_items = []
    key_sources = [
        ("01-executive-brief.md", ["wf_inbox_to_normalized_evidence", "wf_research_command_center", "wf_problem_brief_to_prd"], [research_notebook["research_notebook_id"], research_brief["research_brief_id"], problem_brief["problem_brief_id"]]),
        ("02-codesync-self-analysis.md", ["wf_inbox_to_normalized_evidence", "wf_research_command_center"], [research_notebook["research_notebook_id"], concept_brief["concept_brief_id"]]),
        ("05-segment-map.md", ["wf_inbox_to_normalized_evidence", "wf_research_command_center"], [segment_map["segment_map_id"], persona_pack["persona_pack_id"]]),
        ("06-persona-pack.md", ["wf_inbox_to_normalized_evidence", "wf_research_command_center"], [persona_pack["persona_pack_id"]]),
        ("16-customer-pilot-proposal.md", ["wf_inbox_to_normalized_evidence", "wf_problem_brief_to_prd"], [prd["prd_id"]]),
    ]
    for filename, workflow_ids, artifact_ids in key_sources:
        source_path = source / "Notes" / "research" / filename
        if not source_path.exists():
            continue
        intake_items.append(
            {
                "item_id": f"inbox_raw_note_{_slug(source_path.stem)}",
                "inbox_path": _relative_path(source_path, source),
                "input_type": "raw_note",
                "captured_at": generated_at,
                "provenance_status": "complete",
                "normalization_status": "routed",
                "recommended_workflow_ids": workflow_ids,
                "derived_artifact_ids": artifact_ids,
                "notes": f"Adopted from {filename} during bounded workspace conversion.",
            }
        )

    intake_routing_state = {
        "schema_version": "1.0.0",
        "intake_routing_state_id": f"intake_routing_state_{product_slug}",
        "workspace_id": workspace_id,
        "ingestion_mode": "manual",
        "status": "completed",
        "routing_summary": f"The source workspace was classified as notes-first and routed into a bounded discovery artifact set for {name}.",
        "active_inbox_paths": [
            "inbox/raw-notes",
            "inbox/documents",
            "inbox/screenshots",
        ],
        "intake_items": intake_items,
        "blocked_item_ids": [],
        "created_at": generated_at,
        "updated_at": generated_at,
    }

    item_lifecycle_state = _build_item_lifecycle_state(
        workspace_id=workspace_id,
        product_slug=product_slug,
        best_beachhead=context["best_beachhead"],
        generated_at=generated_at,
    )

    snapshots = {
        "lifecycle_stage_snapshot": _build_snapshot(
            workspace_id=workspace_id,
            product_slug=product_slug,
            item_state=item_lifecycle_state,
            focus_area="discovery",
            summary="The adopted workspace now converts the original CodeSync research pack into a traceable discovery path through a provisional PRD handoff.",
            created_at=generated_at,
        ),
        "lifecycle_stage_snapshot_delivery": _build_snapshot(
            workspace_id=workspace_id,
            product_slug=product_slug,
            item_state=item_lifecycle_state,
            focus_area="delivery",
            summary="Delivery planning remains intentionally deferred until the launch-lane PRD and review queue are resolved.",
            created_at=generated_at,
        ),
        "lifecycle_stage_snapshot_launch": _build_snapshot(
            workspace_id=workspace_id,
            product_slug=product_slug,
            item_state=item_lifecycle_state,
            focus_area="launch",
            summary="Launch preparation is still blocked on proof, packaging, and security review rather than hidden behind broad platform claims.",
            created_at=generated_at,
        ),
        "lifecycle_stage_snapshot_outcomes": _build_snapshot(
            workspace_id=workspace_id,
            product_slug=product_slug,
            item_state=item_lifecycle_state,
            focus_area="outcomes",
            summary="No pilot or launch outcome evidence exists yet, so the adopted workspace keeps outcome review explicitly out of scope.",
            created_at=generated_at,
        ),
        "lifecycle_stage_snapshot_full_lifecycle": _build_snapshot(
            workspace_id=workspace_id,
            product_slug=product_slug,
            item_state=item_lifecycle_state,
            focus_area="full_lifecycle",
            summary="The adopted workspace exposes a first-pass full lifecycle trace with discovery completed through concept shaping, provisional PRD handoff, and explicit later-stage deferrals.",
            created_at=generated_at,
        ),
    }

    thread_review_bundle = _build_thread_review_bundle(
        workspace_id=workspace_id,
        product_slug=product_slug,
        generated_at=generated_at,
        research_notebook=research_notebook,
        research_brief=research_brief,
        idea_record=idea_record,
        problem_brief=problem_brief,
        concept_brief=concept_brief,
        segment_map=segment_map,
        persona_pack=persona_pack,
        prd=prd,
        item_lifecycle_state=item_lifecycle_state,
        workspace_adoption_report={
            "confidence_summary": "The adopted problem, concept, segment, persona, and PRD artifacts are usable as a first pass, but customer claims, security posture, and packaging still require explicit PM review.",
            "unresolved_questions": [
                "Which customer-facing claims can move from inferred to observed without further proof?",
                "What minimum security and audit evidence is required before external pilot packaging is reused?",
            ],
        },
        adoption_review_queue={
            "review_items": review_items,
        },
    )

    generated_artifact_ids = [
        *source_note_card_ids,
        research_notebook["research_notebook_id"],
        research_brief["research_brief_id"],
        idea_record["idea_record_id"],
        problem_brief["problem_brief_id"],
        concept_brief["concept_brief_id"],
        segment_map["segment_map_id"],
        persona_pack["persona_pack_id"],
        prd["prd_id"],
        item_lifecycle_state["item_lifecycle_state_id"],
        thread_review_bundle["thread_review_bundle_id"],
        snapshots["lifecycle_stage_snapshot"]["lifecycle_stage_snapshot_id"],
        f"workspace_adoption_report_{product_slug}",
        f"adoption_review_queue_{product_slug}",
        intake_routing_state["intake_routing_state_id"],
    ]
    workspace_adoption_report = {
        "schema_version": "1.0.0",
        "workspace_adoption_report_id": f"workspace_adoption_report_{product_slug}",
        "workspace_id": workspace_id,
        "source_workspace_path": source.as_posix(),
        "destination_workspace_path": "",
        "source_workspace_mode": "notes_first",
        "source_file_count": len(source_files),
        "classified_file_counts": dict(file_counts),
        "generated_artifact_ids": generated_artifact_ids,
        "review_item_count": len(review_items),
        "adoption_summary": f"ProductOS converted the source {name} notes and research pack into a bounded discovery artifact set and lifecycle trace.",
        "confidence_summary": "The adopted problem, concept, segment, persona, and PRD artifacts are usable as a first pass, but customer claims, security posture, and packaging still require explicit PM review.",
        "unresolved_questions": [
            "Which customer-facing claims can move from inferred to observed without further proof?",
            "What minimum security and audit evidence is required before external pilot packaging is reused?",
        ],
        "created_at": generated_at,
    }
    adoption_review_queue = {
        "schema_version": "1.0.0",
        "adoption_review_queue_id": f"adoption_review_queue_{product_slug}",
        "workspace_id": workspace_id,
        "source_workspace_path": source.as_posix(),
        "generated_artifact_ids": generated_artifact_ids,
        "review_items": review_items,
        "created_at": generated_at,
    }
    thread_review_bundle["pinned_context"]["confidence_summary"] = workspace_adoption_report["confidence_summary"]
    thread_review_bundle["pinned_context"]["pending_questions"] = list(
        dict.fromkeys(
            [
                *thread_review_bundle["pinned_context"]["pending_questions"],
                *workspace_adoption_report["unresolved_questions"],
            ]
        )
    )

    return {
        "workspace_adoption_report": workspace_adoption_report,
        "adoption_review_queue": adoption_review_queue,
        "intake_routing_state": intake_routing_state,
        **source_note_cards,
        "research_notebook": research_notebook,
        "research_brief": research_brief,
        "idea_record": idea_record,
        "problem_brief": problem_brief,
        "concept_brief": concept_brief,
        "segment_map": segment_map,
        "persona_pack": persona_pack,
        "prd": prd,
        "item_lifecycle_state": item_lifecycle_state,
        "thread_review_bundle": thread_review_bundle,
        **snapshots,
    }


def _append_manifest_artifact_path(manifest_path: Path, relative_path: str) -> None:
    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = yaml.safe_load(handle)
    artifact_paths = manifest.setdefault("artifact_paths", [])
    if relative_path not in artifact_paths:
        artifact_paths.append(relative_path)
    with manifest_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(manifest, handle, sort_keys=False)


def _support_artifacts_dir(root: Path) -> Path | None:
    internal_artifacts = root / "internal" / "ProductOS-Next" / "artifacts"
    if internal_artifacts.exists():
        return internal_artifacts
    return None


def _support_artifact_source(root: Path, filename: str) -> Path | None:
    internal_dir = _support_artifacts_dir(root)
    if internal_dir is not None:
        candidate = internal_dir / filename
        if candidate.exists():
            return candidate
    core_candidate = root / "core" / "examples" / "artifacts" / filename
    if core_candidate.exists():
        return core_candidate
    return None


def _seed_runtime_support_assets(root: Path, destination: Path, workspace_id: str) -> None:
    support_dir = _support_artifacts_dir(root)
    if support_dir is None:
        return

    artifacts_dir = destination / "artifacts"
    manifest_path = destination / "workspace_manifest.yaml"
    for filename in _RUNTIME_SUPPORT_ARTIFACTS:
        source_path = _support_artifact_source(root, filename)
        if source_path is None:
            continue
        payload = _rewrite_workspace_ids(_load_json(source_path), workspace_id)
        _write_json(artifacts_dir / filename, payload)
        _append_manifest_artifact_path(manifest_path, f"artifacts/{filename}")

    for source_path in sorted(support_dir.glob("source_note_card*.json")):
        payload = _rewrite_workspace_ids(_load_json(source_path), workspace_id)
        _write_json(artifacts_dir / source_path.name, payload)
        _append_manifest_artifact_path(manifest_path, f"artifacts/{source_path.name}")


def _copy_source_into_inbox(
    source_dir: Path,
    destination: Path,
    *,
    include_internal_dogfood_inputs: bool,
) -> None:
    inbox_root = destination / "inbox"
    visible_files = [_classify_file(source_dir, path) for path in _visible_files(source_dir)]
    for item in visible_files:
        target_dir = inbox_root / item["inbox_lane"]
        target_dir.mkdir(parents=True, exist_ok=True)
        filename = item["path"].name if item["path"].name not in {".DS_Store"} else f"{_slug(item['relative_path'])}{item['path'].suffix.lower()}"
        target_path = target_dir / filename
        if target_path.exists():
            target_path = target_dir / f"{_slug(item['relative_path'])}{item['path'].suffix.lower()}"
        shutil.copy2(item["path"], target_path)

    if not include_internal_dogfood_inputs:
        return

    executive_brief = source_dir / "Notes" / "research" / "01-executive-brief.md"
    if executive_brief.exists():
        (inbox_root / "raw-notes").mkdir(parents=True, exist_ok=True)
        shutil.copy2(executive_brief, inbox_root / "raw-notes" / "2026-03-22-next-version-superpowers.md")

    pilot = source_dir / "Notes" / "research" / "16-customer-pilot-proposal.md"
    if pilot.exists():
        (inbox_root / "transcripts").mkdir(parents=True, exist_ok=True)
        shutil.copy2(pilot, inbox_root / "transcripts" / "2026-03-22-dogfood-next-version-session.txt")


def _write_adoption_docs(
    destination: Path,
    bundle: dict[str, dict[str, Any]],
    name: str,
    *,
    include_report: bool,
    thread_page_path: Path | None = None,
) -> None:
    research_brief = bundle["research_brief"]
    problem_brief = bundle["problem_brief"]
    prd = bundle["prd"]
    report = bundle["workspace_adoption_report"]
    review_queue = bundle["adoption_review_queue"]

    product_dir = destination / "docs" / "product"
    discovery_dir = destination / "docs" / "discovery"
    planning_dir = destination / "docs" / "planning"
    product_dir.mkdir(parents=True, exist_ok=True)
    discovery_dir.mkdir(parents=True, exist_ok=True)
    planning_dir.mkdir(parents=True, exist_ok=True)

    insights = research_brief.get("insights", [])
    observed_insights = [item["statement"] for item in insights if item.get("claim_mode") == "observed"]
    inferred_insights = [item["statement"] for item in insights if item.get("claim_mode") == "inferred"]
    hypothesis_insights = [item["statement"] for item in insights if item.get("claim_mode") == "hypothesis"]

    product_lines = [
        "# Product Overview",
        "",
        f"{name} is currently being shaped as a governed workflow-control product rather than a broad platform claim.",
        "",
        "## Current Wedge",
        "",
        research_brief["summary"],
        "",
        "## Product Definition",
        "",
        f"- Problem framing: {problem_brief['problem_summary']}",
        f"- Outcome summary: {prd['outcome_summary']}",
        f"- Current recommendation: `{research_brief['recommendation']}`",
        "",
        "## Claim Discipline",
        "",
        "Observed insights:",
    ]
    for statement in observed_insights or ["No observed insights are currently tagged."]:
        product_lines.append(f"- {statement}")
    product_lines.extend(["", "Inferred insights:"])
    for statement in inferred_insights or ["No inferred insights are currently tagged."]:
        product_lines.append(f"- {statement}")
    if hypothesis_insights:
        product_lines.extend(["", "Hypothesis-only insights:"])
        for statement in hypothesis_insights:
            product_lines.append(f"- {statement}")
    product_lines.extend(["", "## Known Gaps", ""])
    for gap in research_brief.get("known_gaps", []) or ["No explicit known gaps recorded."]:
        product_lines.append(f"- {gap}")
    product_lines.extend(["", "## Conflicted Evidence", ""])
    for contradiction in research_brief.get("contradictions", []) or [{"statement": "No explicit evidence conflicts recorded."}]:
        product_lines.append(f"- {contradiction['statement']}")
    product_lines.extend(["", "## Next External Research", ""])
    for question in research_brief.get("external_research_questions", []):
        product_lines.append(
            f"- [{question['priority']}] {question['question']} "
            f"({question['recommended_source_type']}: {question['why_it_matters']})"
        )
    if not research_brief.get("external_research_questions"):
        product_lines.append("- No bounded external research questions recorded.")
    (product_dir / "product-overview.md").write_text("\n".join(product_lines) + "\n", encoding="utf-8")

    discovery_lines = [
        "# Discovery Review",
        "",
        f"This workspace now treats {name} discovery as an evidence-governed product definition flow rather than a starter demo.",
        "",
        "## Core Artifacts",
        "",
        "- `research_notebook.json`",
        "- `research_brief.json`",
        "- `problem_brief.json`",
        "- `concept_brief.json`",
        "- `segment_map.json`",
        "- `persona_pack.json`",
        "- `prd.json`",
        "- `adoption_review_queue.json`",
        "",
        "## Evidence Status",
        "",
    ]
    for insight in insights:
        discovery_lines.append(
            f"- `{insight.get('claim_mode', 'unspecified')}`: {insight['statement']} "
            f"Next validation: {insight.get('next_validation_step', 'n/a')}"
        )
    discovery_lines.extend(["", "## Conflicted External Evidence", ""])
    for contradiction in research_brief.get("contradictions", []) or [{"statement": "No explicit evidence conflicts recorded."}]:
        discovery_lines.append(f"- {contradiction['statement']}")
    discovery_lines.extend(["", "## Review Queue", ""])
    for item in review_queue["review_items"]:
        discovery_lines.append(f"- {item['title']}")
    discovery_lines.extend(["", "## Bounded External Research", ""])
    for question in research_brief.get("external_research_questions", []):
        discovery_lines.append(f"- {question['question']}")
    if not research_brief.get("external_research_questions"):
        discovery_lines.append("- No external research questions recorded.")
    (discovery_dir / "discovery-review.md").write_text("\n".join(discovery_lines) + "\n", encoding="utf-8")

    if include_report:
        lines = [
            f"# Workspace Adoption Report: {name}",
            "",
            f"- Source workspace: `{report['source_workspace_path']}`",
            f"- Source mode: `{report['source_workspace_mode']}`",
            f"- Generated artifacts: `{len(report['generated_artifact_ids'])}`",
            f"- Review items: `{report['review_item_count']}`",
            "",
            "## Summary",
            "",
            report["adoption_summary"],
            "",
            "## Confidence Summary",
            "",
            report["confidence_summary"],
            "",
        ]
        if thread_page_path is not None:
            lines.extend(
                [
                    "## Thread Review Surface",
                    "",
                    f"- Generated page: `{thread_page_path.relative_to(destination).as_posix()}`",
                    "",
                ]
            )
        lines.extend(["## Review Queue", ""])
        for item in review_queue["review_items"]:
            lines.append(f"- {item['title']}")
        lines.extend(["", "## Conflicted Evidence", ""])
        for contradiction in research_brief.get("contradictions", []) or [{"statement": "No explicit evidence conflicts recorded."}]:
            lines.append(f"- {contradiction['statement']}")
        lines.extend(["", "## External Research Next", ""])
        for question in research_brief.get("external_research_questions", []):
            lines.append(f"- {question['question']}")
        (planning_dir / "workspace-adoption-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def adopt_workspace_from_source(
    root_dir: Path | str,
    *,
    source_dir: Path | str,
    dest: Path | str,
    workspace_id: str,
    name: str,
    mode: str,
    generated_at: str,
    review_threshold: str = "medium",
    emit_report: bool = False,
    emit_thread_page: bool = False,
    include_runtime_support_assets: bool = False,
) -> tuple[Path, dict[str, dict[str, Any]]]:
    root = Path(root_dir).resolve()
    source = Path(source_dir).resolve()
    destination = init_workspace_from_template(
        root,
        dest=dest,
        workspace_id=workspace_id,
        name=name,
        mode=mode,
    )
    bundle = build_workspace_adoption_bundle_from_source(
        root,
        source_dir=source,
        workspace_id=workspace_id,
        name=name,
        generated_at=generated_at,
        review_threshold=review_threshold,
    )
    bundle["workspace_adoption_report"]["destination_workspace_path"] = destination.as_posix()

    artifacts_dir = destination / "artifacts"
    for name_key, payload in bundle.items():
        _write_json(artifacts_dir / f"{name_key}.json", payload)
        _append_manifest_artifact_path(destination / "workspace_manifest.yaml", f"artifacts/{name_key}.json")

    if include_runtime_support_assets:
        _seed_runtime_support_assets(root, destination, workspace_id)
    _copy_source_into_inbox(
        source,
        destination,
        include_internal_dogfood_inputs=include_runtime_support_assets,
    )
    thread_page_path: Path | None = None
    if emit_thread_page:
        thread_page_path = write_thread_review_page(
            bundle["thread_review_bundle"],
            destination / "docs" / "review" / "thread-review.html",
        )
    _write_adoption_docs(destination, bundle, name, include_report=emit_report, thread_page_path=thread_page_path)

    return destination, bundle
