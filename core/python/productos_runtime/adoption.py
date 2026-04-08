from __future__ import annotations

import copy
import json
import shutil
from collections import Counter
from pathlib import Path
from typing import Any

from . import yaml_compat as yaml

from .lifecycle import DISCOVERY_STAGE_ORDER, LIFECYCLE_STAGE_ORDER, init_workspace_from_template


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
    "lifecycle_stage_snapshot": "lifecycle_stage_snapshot.schema.json",
    "lifecycle_stage_snapshot_delivery": "lifecycle_stage_snapshot.schema.json",
    "lifecycle_stage_snapshot_launch": "lifecycle_stage_snapshot.schema.json",
    "lifecycle_stage_snapshot_outcomes": "lifecycle_stage_snapshot.schema.json",
    "lifecycle_stage_snapshot_full_lifecycle": "lifecycle_stage_snapshot.schema.json",
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


def _visible_files(source_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(source_dir.rglob("*")):
        if not path.is_file():
            continue
        if any(part.startswith(".") for part in path.relative_to(source_dir).parts):
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


def _write_adoption_docs(destination: Path, bundle: dict[str, dict[str, Any]], name: str, *, include_report: bool) -> None:
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
            "## Review Queue",
            "",
        ]
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
    _write_adoption_docs(destination, bundle, name, include_report=emit_report)

    return destination, bundle
