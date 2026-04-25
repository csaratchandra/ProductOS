from __future__ import annotations

import re
from typing import Any


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _dedupe_strings(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if isinstance(value, str) and value))


def _corridor_status(status: str | None, gate_status: str | None = None) -> str:
    if status in {"blocked", "failed"} or gate_status in {"blocked", "failed"}:
        return "blocked"
    if status in {"completed", "approved", "ready"} and gate_status in {"passed", "ready", None}:
        return "approved"
    if status in {"in_progress", "active", "watch"}:
        return "watch"
    return "inferred"


def _claim_mode(status: str | None, gate_status: str | None = None) -> str:
    if status in {"completed", "approved", "ready"} and gate_status in {"passed", "ready", None}:
        return "observed"
    if status in {"blocked", "failed"} or gate_status in {"blocked", "failed"}:
        return "inferred"
    return "inferred"


def _lane_for_role(owner_role: str) -> str:
    lane_map = {
        "Research": "lane_signal",
        "PM": "lane_pm",
        "Design": "lane_design",
        "Engineering": "lane_delivery",
        "Operations": "lane_ops",
        "Leadership": "lane_review",
    }
    return lane_map.get(owner_role, "lane_pm")


def build_align_corridor_source_bundle(
    *,
    workspace_id: str,
    presentation_brief: dict[str, Any],
    presentation_publish_check: dict[str, Any],
    document_sync_state: dict[str, Any],
    mission_brief: dict[str, Any] | None = None,
    research_brief: dict[str, Any] | None = None,
    problem_brief: dict[str, Any] | None = None,
    generated_at: str,
) -> dict[str, Any]:
    source_artifact_ids = _dedupe_strings(
        [
            *(presentation_brief.get("source_artifact_ids") or []),
            document_sync_state.get("document_sync_state_id", ""),
            presentation_brief.get("presentation_brief_id", ""),
            presentation_publish_check.get("publish_check_id", ""),
            (mission_brief or {}).get("mission_brief_id", ""),
            (research_brief or {}).get("research_brief_id", ""),
            (problem_brief or {}).get("problem_brief_id", ""),
        ]
    )
    primary_source_id = (source_artifact_ids or [f"mission_brief_{workspace_id}"])[0]
    mission_title = (mission_brief or {}).get("title") or presentation_brief.get("title") or "ProductOS workflow corridor"
    publish_ready = bool(presentation_publish_check.get("publish_ready"))
    publish_status = "approved" if publish_ready else "watch"
    publish_claim_mode = "observed" if publish_ready else "inferred"
    objective = presentation_brief.get("objective") or "Package current ProductOS truth into one explainable workflow page."
    narrative_goal = presentation_brief.get("narrative_goal") or objective
    next_action = document_sync_state.get("next_action") or "Keep the public workflow explanation aligned with repo truth."

    return {
        "corridor_id": f"{workspace_id}_align",
        "workspace_id": workspace_id,
        "title": f"Workflow corridor: {mission_title}",
        "corridor_story": (
            "ProductOS can turn repo-backed PM truth into one customer-safe workflow page "
            "that explains the operating flow, proof posture, and publish decision without presenter narration."
        ),
        "source_artifact_ids": source_artifact_ids or [f"mission_brief_{workspace_id}"],
        "workflow": {
            "stages": [
                {
                    "stage_id": "stage_source_truth",
                    "label": "Source truth",
                    "headline": "Collect repo-backed PM truth before any visual packaging begins",
                    "summary": objective,
                    "lane_ids": ["lane_signal", "lane_pm"],
                    "owner_role": "Research",
                    "status": "approved",
                    "claim_mode": "observed",
                    "proof_refs": ["proof_sources"],
                },
                {
                    "stage_id": "stage_alignment",
                    "label": "Alignment",
                    "headline": "Package one canonical workflow story from the approved artifacts",
                    "summary": next_action,
                    "lane_ids": ["lane_pm", "lane_design"],
                    "owner_role": "PM",
                    "status": "approved",
                    "claim_mode": "observed",
                    "proof_refs": ["proof_alignment"],
                },
                {
                    "stage_id": "stage_publish_review",
                    "label": "Publish review",
                    "headline": "Check whether the workflow explanation is safe to publish externally",
                    "summary": narrative_goal,
                    "lane_ids": ["lane_review", "lane_ops"],
                    "owner_role": "Leadership",
                    "status": publish_status,
                    "claim_mode": publish_claim_mode,
                    "proof_refs": ["proof_publish"],
                },
            ],
            "lanes": [
                {"lane_id": "lane_signal", "label": "Signal", "summary": "Source material and evidence intake", "owner_role": "Research"},
                {"lane_id": "lane_pm", "label": "PM", "summary": "PM curation and workflow packaging", "owner_role": "PM"},
                {"lane_id": "lane_design", "label": "Design", "summary": "Visual shaping and reading-path quality", "owner_role": "Design"},
                {"lane_id": "lane_review", "label": "Review", "summary": "Publish and leadership review", "owner_role": "Leadership"},
                {"lane_id": "lane_ops", "label": "Ops", "summary": "Operational publish and follow-through", "owner_role": "Operations"},
            ],
            "owner_transitions": [
                {
                    "transition_id": "transition_truth_alignment",
                    "from_stage_id": "stage_source_truth",
                    "to_stage_id": "stage_alignment",
                    "from_owner_role": "Research",
                    "to_owner_role": "PM",
                    "status": "approved",
                    "claim_mode": "observed",
                    "proof_refs": ["proof_sources"],
                },
                {
                    "transition_id": "transition_alignment_publish",
                    "from_stage_id": "stage_alignment",
                    "to_stage_id": "stage_publish_review",
                    "from_owner_role": "PM",
                    "to_owner_role": "Leadership",
                    "status": publish_status,
                    "claim_mode": publish_claim_mode,
                    "proof_refs": ["proof_publish"],
                },
            ],
        },
        "personas": [
            {
                "persona_id": "persona_buyer",
                "label": "Buyer",
                "summary": "Needs the workflow page to explain itself clearly.",
                "goal": "Understand the workflow and trust what ProductOS can actually prove.",
                "visible_stage_ids": ["stage_source_truth", "stage_alignment", "stage_publish_review"],
                "priority_proof_refs": ["proof_publish"],
            },
            {
                "persona_id": "persona_operator",
                "label": "Operator",
                "summary": "Needs owner transitions and publish posture to stay explicit.",
                "goal": "See where the workflow is ready, watch, or still bounded.",
                "visible_stage_ids": ["stage_alignment", "stage_publish_review"],
                "priority_proof_refs": ["proof_alignment", "proof_publish"],
            },
        ],
        "segment_overlays": [
            {
                "overlay_id": "segment_exec_review",
                "dimension": "segment",
                "label": "Executive review",
                "summary": "Compress the workflow story without hiding proof or publish boundaries.",
                "impact_stage_ids": ["stage_alignment", "stage_publish_review"],
                "claim_mode": publish_claim_mode,
                "proof_refs": ["proof_publish"],
            }
        ],
        "operating_models": [
            {
                "overlay_id": "operating_async_review",
                "dimension": "operating_model",
                "label": "Async review",
                "summary": "Keep the workflow self-explanatory for async and customer-facing review.",
                "impact_stage_ids": ["stage_alignment", "stage_publish_review"],
                "claim_mode": "observed",
                "proof_refs": ["proof_alignment"],
            }
        ],
        "package_scope": [
            {
                "package_id": "package_visual_alignment",
                "label": "Visual Alignment Package",
                "summary": "Includes deck outputs and corridor outputs generated from the same repo-backed truth.",
                "included_stage_ids": ["stage_source_truth", "stage_alignment", "stage_publish_review"],
            }
        ],
        "terminal_outcomes": [
            {
                "outcome_id": "outcome_shareable_workflow",
                "label": "Shareable workflow explanation",
                "summary": "The workflow can be understood and reviewed from one customer-safe corridor page.",
                "status": publish_status,
                "claim_mode": publish_claim_mode,
                "kpi_refs": ["kpi_publish_confidence"],
                "proof_refs": ["proof_publish"],
            }
        ],
        "kpi_mappings": [
            {
                "kpi_id": "kpi_publish_confidence",
                "label": "Publish confidence",
                "summary": "Publish checks stay explicit and strong for the workflow corridor.",
                "stage_id": "stage_publish_review",
                "target_outcome_id": "outcome_shareable_workflow",
                "claim_mode": publish_claim_mode,
                "proof_refs": ["proof_publish"],
            }
        ],
        "proof_items": [
            {
                "proof_id": "proof_sources",
                "label": "Repo-backed source truth",
                "summary": "The corridor is derived from repo-backed artifacts rather than ad hoc page edits.",
                "claim_mode": "observed",
                "source_artifact_id": primary_source_id,
                "customer_safe": True,
            },
            {
                "proof_id": "proof_alignment",
                "label": "Aligned packaging path",
                "summary": "The deck and corridor are packaged from one aligned visual flow instead of diverging narratives.",
                "claim_mode": "observed",
                "source_artifact_id": presentation_brief.get("presentation_brief_id", primary_source_id),
                "customer_safe": True,
            },
            {
                "proof_id": "proof_publish",
                "label": "Publish gate coverage",
                "summary": "Publish review remains explicit before a workflow page is treated as externally shareable.",
                "claim_mode": publish_claim_mode,
                "source_artifact_id": presentation_publish_check.get("publish_check_id", primary_source_id),
                "customer_safe": True,
            },
        ],
        "workspace_input_refs": [
            {
                "ref_id": f"workspace_manifest_{workspace_id}",
                "ref_type": "workspace_manifest",
                "label": "Workspace manifest context",
                "customer_safe": True,
            }
        ],
        "created_at": generated_at,
    }


def build_thread_review_corridor_source_bundle(
    thread_review_bundle: dict[str, Any],
) -> dict[str, Any]:
    item_id = thread_review_bundle["item_ref"]["entity_id"]
    workspace_id = thread_review_bundle["workspace_id"]
    stage_owner_map = {
        "problem_framing": "PM",
        "market_validation": "Research",
        "prototype_validation": "Design",
        "prd_handoff": "PM",
        "story_planning": "PM",
        "acceptance_ready": "Engineering",
        "release_readiness": "Operations",
        "launch_preparation": "Operations",
        "outcome_review": "PM",
    }

    canonical_stages: list[dict[str, Any]] = []
    proof_items: list[dict[str, Any]] = []
    owner_transitions: list[dict[str, Any]] = []
    source_artifact_ids = _dedupe_strings(
        [
            *thread_review_bundle["pinned_context"]["source_artifact_ids"],
            thread_review_bundle["thread_review_bundle_id"],
        ]
    )
    stage_rail = thread_review_bundle["stage_rail"]
    for index, stage in enumerate(stage_rail):
        owner_role = stage_owner_map.get(stage["stage_key"], "PM")
        lane_id = _lane_for_role(owner_role)
        claim_mode = _claim_mode(stage.get("status"), stage.get("gate_status"))
        status = _corridor_status(stage.get("status"), stage.get("gate_status"))
        proof_id = f"proof_{stage['stage_key']}"
        proof_items.append(
            {
                "proof_id": proof_id,
                "label": stage["title"],
                "summary": stage["summary"] or f"Thread review evidence for {stage['title']}.",
                "claim_mode": claim_mode,
                "source_artifact_id": (stage.get("artifact_ids") or source_artifact_ids or [thread_review_bundle["thread_review_bundle_id"]])[0],
                "customer_safe": False,
            }
        )
        canonical_stages.append(
            {
                "stage_id": f"stage_{stage['stage_key']}",
                "label": stage["title"],
                "headline": stage["summary"] or f"{stage['title']} is part of the canonical review path.",
                "summary": stage["summary"] or f"{stage['title']} remains part of the internal review path.",
                "lane_ids": [lane_id],
                "owner_role": owner_role,
                "status": status,
                "claim_mode": claim_mode,
                "proof_refs": [proof_id],
                "visibility": "internal",
            }
        )
        if index > 0:
            previous = stage_rail[index - 1]
            previous_owner = stage_owner_map.get(previous["stage_key"], "PM")
            owner_transitions.append(
                {
                    "transition_id": f"transition_{previous['stage_key']}_{stage['stage_key']}",
                    "from_stage_id": f"stage_{previous['stage_key']}",
                    "to_stage_id": f"stage_{stage['stage_key']}",
                    "from_owner_role": previous_owner,
                    "to_owner_role": owner_role,
                    "status": status,
                    "claim_mode": claim_mode,
                    "proof_refs": [proof_id],
                    "visibility": "internal",
                }
            )

    lanes = [
        {"lane_id": "lane_signal", "label": "Research", "summary": "Research and evidence review", "owner_role": "Research", "visibility": "internal"},
        {"lane_id": "lane_pm", "label": "PM", "summary": "PM curation and product decisions", "owner_role": "PM", "visibility": "internal"},
        {"lane_id": "lane_design", "label": "Design", "summary": "Prototype and usability review", "owner_role": "Design", "visibility": "internal"},
        {"lane_id": "lane_delivery", "label": "Engineering", "summary": "Delivery and acceptance readiness", "owner_role": "Engineering", "visibility": "internal"},
        {"lane_id": "lane_ops", "label": "Ops", "summary": "Release and launch operations", "owner_role": "Operations", "visibility": "internal"},
    ]

    personas = [
        {
            "persona_id": f"persona_{_slug(persona)}",
            "label": persona.replace("_", " ").title(),
            "summary": "Needs the lifecycle thread and current stage to be self-explanatory.",
            "goal": "Understand the current stage, next action, and review posture.",
            "visible_stage_ids": [stage["stage_id"] for stage in canonical_stages],
            "priority_proof_refs": [proof_items[0]["proof_id"]] if proof_items else [],
            "visibility": "internal",
        }
        for persona in (thread_review_bundle["pinned_context"]["target_personas"] or ["pm_reviewer"])
    ]

    segment_overlays = [
        {
            "overlay_id": f"segment_{_slug(segment)}",
            "dimension": "segment",
            "label": segment.replace("_", " ").title(),
            "summary": "Shows how the same lifecycle thread is interpreted for this target segment.",
            "impact_stage_ids": [stage["stage_id"] for stage in canonical_stages[:3]],
            "claim_mode": "inferred",
            "proof_refs": [proof_items[0]["proof_id"]] if proof_items else [],
            "visibility": "internal",
        }
        for segment in thread_review_bundle["pinned_context"]["target_segments"]
    ]

    return {
        "corridor_id": f"{item_id}_thread_review",
        "workspace_id": workspace_id,
        "title": f"Thread review corridor: {item_id}",
        "corridor_story": (
            "One internal corridor page should explain the lifecycle thread, current stage, "
            "review posture, and next action without relying on separate thread-review narration."
        ),
        "source_artifact_ids": source_artifact_ids or [thread_review_bundle["thread_review_bundle_id"]],
        "workflow": {
            "stages": canonical_stages,
            "lanes": lanes,
            "owner_transitions": owner_transitions or [
                {
                    "transition_id": "transition_placeholder",
                    "from_stage_id": canonical_stages[0]["stage_id"],
                    "to_stage_id": canonical_stages[min(1, len(canonical_stages) - 1)]["stage_id"],
                    "from_owner_role": canonical_stages[0]["owner_role"],
                    "to_owner_role": canonical_stages[min(1, len(canonical_stages) - 1)]["owner_role"],
                    "status": "watch",
                    "claim_mode": "inferred",
                    "proof_refs": [proof_items[0]["proof_id"]],
                    "visibility": "internal",
                }
            ],
        },
        "personas": personas,
        "segment_overlays": segment_overlays,
        "operating_models": [
            {
                "overlay_id": "operating_thread_review",
                "dimension": "operating_model",
                "label": "Thread review",
                "summary": "Keep the lifecycle thread self-explanatory for internal PM review.",
                "impact_stage_ids": [stage["stage_id"] for stage in canonical_stages[:3]],
                "claim_mode": "observed",
                "proof_refs": [proof_items[0]["proof_id"]] if proof_items else [],
                "visibility": "internal",
            }
        ],
        "package_scope": [
            {
                "package_id": "package_thread_review_corridor",
                "label": "Thread Review Corridor",
                "summary": "Adds an internal corridor view alongside the thread-review page, markdown, and deck package.",
                "included_stage_ids": [stage["stage_id"] for stage in canonical_stages],
                "visibility": "internal",
            }
        ],
        "terminal_outcomes": [
            {
                "outcome_id": "outcome_review_clarity",
                "label": "Review clarity",
                "summary": thread_review_bundle["review_status_summary"],
                "status": "approved" if thread_review_bundle["review_status"] == "stable_full_lifecycle" else "watch",
                "claim_mode": "observed" if thread_review_bundle["review_status"] == "stable_full_lifecycle" else "inferred",
                "kpi_refs": ["kpi_thread_review_clarity"],
                "proof_refs": [proof_items[-1]["proof_id"]] if proof_items else [],
                "visibility": "internal",
            }
        ],
        "kpi_mappings": [
            {
                "kpi_id": "kpi_thread_review_clarity",
                "label": "Thread review clarity",
                "summary": "The lifecycle thread stays explainable and reviewable without extra narration.",
                "stage_id": canonical_stages[min(1, len(canonical_stages) - 1)]["stage_id"],
                "target_outcome_id": "outcome_review_clarity",
                "claim_mode": "inferred",
                "proof_refs": [proof_items[0]["proof_id"]] if proof_items else [],
            }
        ],
        "proof_items": proof_items[: max(3, len(proof_items))],
        "workspace_input_refs": [
            {
                "ref_id": thread_review_bundle["thread_review_bundle_id"],
                "ref_type": "thread_review_bundle",
                "label": "Thread review bundle context",
                "customer_safe": False,
            }
        ],
        "created_at": thread_review_bundle["generated_at"],
    }
