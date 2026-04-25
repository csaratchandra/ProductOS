from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from html import escape
import json
from pathlib import Path
import re
from typing import Any

from core.python.visual_foundations import (
    corridor_reading_paths,
    corridor_theme_preset_for_publication,
    corridor_theme_tokens,
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def corridor_theme(preset: str = "corridor_public") -> dict[str, str]:
    return corridor_theme_tokens(preset)


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def _copy_override_map(curated_overrides: dict[str, Any]) -> dict[str, str]:
    return {
        item["target_id"]: item["replacement"]
        for item in curated_overrides.get("manual_copy_overrides", [])
        if isinstance(item, dict) and isinstance(item.get("target_id"), str) and isinstance(item.get("replacement"), str)
    }


def _normalize_visibility(value: str | None, customer_safe: bool) -> str:
    if value in {"customer_safe", "internal"}:
        return value
    return "customer_safe" if customer_safe else "internal"


def _normalize_claim_mode(value: str | None) -> str:
    if value in {"observed", "inferred", "hypothesis"}:
        return value
    return "observed"


def _normalize_status(value: str | None, claim_mode: str) -> str:
    if value in {"approved", "watch", "blocked", "inferred"}:
        return value
    return "inferred" if claim_mode != "observed" else "approved"


def _normalize_ref_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(value) for value in values if isinstance(value, str) and value.strip()]


def _visible_for_customer(item: dict[str, Any], customer_safe: bool) -> bool:
    visibility = item.get("visibility", "customer_safe")
    if not customer_safe:
        return True
    if visibility != "customer_safe":
        return False
    if item.get("customer_safe") is False:
        return False
    return True


def _apply_copy_override(target_id: str, fallback: str, overrides: dict[str, str]) -> str:
    return overrides.get(target_id, fallback)


def build_workflow_corridor_spec(
    source_bundle: dict[str, Any],
    *,
    corridor_id: str | None = None,
    workspace_id: str | None = None,
    title: str | None = None,
    audience_mode: str = "customer_safe_public",
    publication_mode: str = "publishable_external",
    scenario_baseline: str | dict[str, str] = "core_baseline",
    overlay_dimensions: list[str] | None = None,
    curated_overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = deepcopy(source_bundle)
    workflow = deepcopy(source.get("workflow", {}))
    curated = deepcopy(source.get("curated_overrides", {}))
    if curated_overrides:
        curated.update(deepcopy(curated_overrides))
    overrides = _copy_override_map(curated)

    customer_safe = publication_mode == "publishable_external" or audience_mode == "customer_safe_public"
    corridor_id = corridor_id or source.get("corridor_id") or _slug(source.get("title", "workflow corridor"))
    workspace_id = workspace_id or source.get("workspace_id") or "ws_unknown"

    stages_source = workflow.get("stages") or source.get("canonical_stages") or []
    lanes_source = workflow.get("lanes") or source.get("lanes") or []
    transitions_source = workflow.get("owner_transitions") or source.get("owner_transitions") or []
    if not stages_source or not lanes_source or not transitions_source:
        raise ValueError("source_bundle must include workflow stages, lanes, and owner transitions")

    proof_source = deepcopy(source.get("proof_items", []))
    proof_ids = [str(item.get("proof_id")) for item in proof_source if isinstance(item, dict) and item.get("proof_id")]
    stage_ids: list[str] = []

    canonical_stages: list[dict[str, Any]] = []
    for index, stage in enumerate(stages_source):
        stage_id = str(stage.get("stage_id") or f"stage_{index + 1}")
        stage_ids.append(stage_id)
        claim_mode = _normalize_claim_mode(stage.get("claim_mode"))
        canonical_stages.append(
            {
                "stage_id": stage_id,
                "label": str(stage.get("label") or stage_id.replace("_", " ").title()),
                "headline": _apply_copy_override(
                    stage_id,
                    str(stage.get("headline") or stage.get("label") or stage_id.replace("_", " ").title()),
                    overrides,
                ),
                "summary": str(stage.get("summary") or stage.get("headline") or "Stage summary pending."),
                "lane_ids": _normalize_ref_list(stage.get("lane_ids") or stage.get("lanes") or [lane.get("lane_id") for lane in lanes_source[:1] if isinstance(lane, dict)]),
                "owner_role": str(stage.get("owner_role") or stage.get("owner") or "PM"),
                "status": _normalize_status(stage.get("status"), claim_mode),
                "claim_mode": claim_mode,
                "proof_refs": _normalize_ref_list(stage.get("proof_refs")) or proof_ids[:1],
                "terminal_outcome_ids": _normalize_ref_list(stage.get("terminal_outcome_ids")),
                "visibility": _normalize_visibility(stage.get("visibility"), customer_safe),
            }
        )

    lanes = [
        {
            "lane_id": str(lane.get("lane_id") or f"lane_{index + 1}"),
            "label": str(lane.get("label") or f"Lane {index + 1}"),
            "summary": str(lane.get("summary") or "Lane summary pending."),
            "owner_role": str(lane.get("owner_role") or lane.get("owner") or "PM"),
            "visibility": _normalize_visibility(lane.get("visibility"), customer_safe),
        }
        for index, lane in enumerate(lanes_source)
        if isinstance(lane, dict)
    ]

    def normalize_overlay(items: list[dict[str, Any]], dimension_name: str) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                continue
            overlay_id = str(item.get("overlay_id") or f"{dimension_name}_{index + 1}")
            normalized.append(
                {
                    "overlay_id": overlay_id,
                    "dimension": str(item.get("dimension") or dimension_name),
                    "label": str(item.get("label") or overlay_id.replace("_", " ").title()),
                    "summary": _apply_copy_override(
                        overlay_id,
                        str(item.get("summary") or f"{overlay_id.replace('_', ' ').title()} overlay."),
                        overrides,
                    ),
                    "impact_stage_ids": _normalize_ref_list(item.get("impact_stage_ids")) or stage_ids[:2],
                    "claim_mode": _normalize_claim_mode(item.get("claim_mode")),
                    "proof_refs": _normalize_ref_list(item.get("proof_refs")),
                    "visibility": _normalize_visibility(item.get("visibility"), customer_safe),
                }
            )
        return normalized

    operating_models = normalize_overlay(deepcopy(source.get("operating_models", [])), "operating_model")
    segment_overlays = normalize_overlay(deepcopy(source.get("segment_overlays", [])), "segment")

    persona_views = []
    for index, persona in enumerate(source.get("personas") or source.get("persona_views") or []):
        if not isinstance(persona, dict):
            continue
        persona_id = str(persona.get("persona_id") or f"persona_{index + 1}")
        persona_views.append(
            {
                "persona_id": persona_id,
                "label": str(persona.get("label") or persona_id.replace("_", " ").title()),
                "summary": str(persona.get("summary") or "Persona summary pending."),
                "goal": str(persona.get("goal") or "Clarify the workflow value."),
                "visible_stage_ids": _normalize_ref_list(persona.get("visible_stage_ids")) or stage_ids,
                "priority_proof_refs": _normalize_ref_list(persona.get("priority_proof_refs")),
                "visibility": _normalize_visibility(persona.get("visibility"), customer_safe),
            }
        )

    package_scope = []
    for index, package in enumerate(source.get("package_scope", [])):
        if not isinstance(package, dict):
            continue
        package_id = str(package.get("package_id") or f"package_{index + 1}")
        package_scope.append(
            {
                "package_id": package_id,
                "label": str(package.get("label") or package_id.replace("_", " ").title()),
                "summary": str(package.get("summary") or "Package scope pending."),
                "included_stage_ids": _normalize_ref_list(package.get("included_stage_ids")) or stage_ids,
                "visibility": _normalize_visibility(package.get("visibility"), customer_safe),
            }
        )

    owner_transitions = []
    for index, transition in enumerate(transitions_source):
        if not isinstance(transition, dict):
            continue
        transition_id = str(transition.get("transition_id") or f"transition_{index + 1}")
        claim_mode = _normalize_claim_mode(transition.get("claim_mode"))
        owner_transitions.append(
            {
                "transition_id": transition_id,
                "from_stage_id": str(transition.get("from_stage_id") or stage_ids[max(index - 1, 0)]),
                "to_stage_id": str(transition.get("to_stage_id") or stage_ids[min(index, len(stage_ids) - 1)]),
                "from_owner_role": str(transition.get("from_owner_role") or transition.get("from_owner") or "PM"),
                "to_owner_role": str(transition.get("to_owner_role") or transition.get("to_owner") or "Operations"),
                "status": _normalize_status(transition.get("status"), claim_mode),
                "claim_mode": claim_mode,
                "proof_refs": _normalize_ref_list(transition.get("proof_refs")),
                "visibility": _normalize_visibility(transition.get("visibility"), customer_safe),
            }
        )

    terminal_outcomes = []
    for index, outcome in enumerate(source.get("terminal_outcomes", [])):
        if not isinstance(outcome, dict):
            continue
        outcome_id = str(outcome.get("outcome_id") or f"outcome_{index + 1}")
        claim_mode = _normalize_claim_mode(outcome.get("claim_mode"))
        terminal_outcomes.append(
            {
                "outcome_id": outcome_id,
                "label": str(outcome.get("label") or outcome_id.replace("_", " ").title()),
                "summary": _apply_copy_override(
                    outcome_id,
                    str(outcome.get("summary") or "Terminal outcome pending."),
                    overrides,
                ),
                "status": _normalize_status(outcome.get("status"), claim_mode),
                "claim_mode": claim_mode,
                "kpi_refs": _normalize_ref_list(outcome.get("kpi_refs")) or ["kpi_publish_confidence"],
                "proof_refs": _normalize_ref_list(outcome.get("proof_refs")),
                "visibility": _normalize_visibility(outcome.get("visibility"), customer_safe),
            }
        )

    kpi_mappings = []
    for index, kpi in enumerate(source.get("kpi_mappings", [])):
        if not isinstance(kpi, dict):
            continue
        kpi_mappings.append(
            {
                "kpi_id": str(kpi.get("kpi_id") or f"kpi_{index + 1}"),
                "label": str(kpi.get("label") or "KPI"),
                "summary": str(kpi.get("summary") or "KPI mapping pending."),
                "stage_id": str(kpi.get("stage_id") or stage_ids[min(index, len(stage_ids) - 1)]),
                "target_outcome_id": str(
                    kpi.get("target_outcome_id")
                    or (terminal_outcomes[min(index, len(terminal_outcomes) - 1)]["outcome_id"] if terminal_outcomes else "outcome_1")
                ),
                "claim_mode": _normalize_claim_mode(kpi.get("claim_mode")),
                "proof_refs": _normalize_ref_list(kpi.get("proof_refs")),
            }
        )

    proof_items = []
    for index, proof in enumerate(proof_source):
        if not isinstance(proof, dict):
            continue
        proof_items.append(
            {
                "proof_id": str(proof.get("proof_id") or f"proof_{index + 1}"),
                "label": str(proof.get("label") or f"Proof {index + 1}"),
                "summary": str(proof.get("summary") or "Proof summary pending."),
                "claim_mode": _normalize_claim_mode(proof.get("claim_mode")),
                "source_artifact_id": str(
                    proof.get("source_artifact_id")
                    or (source.get("source_artifact_ids") or ["artifact_unknown"])[0]
                ),
                "metric_name": str(proof.get("metric_name") or "evidence"),
                "observed_value": str(proof.get("observed_value") or "available"),
                "customer_safe": bool(proof.get("customer_safe", customer_safe)),
                "visibility": _normalize_visibility(proof.get("visibility"), customer_safe),
            }
        )

    message_claims = deepcopy(source.get("message_claims", []))
    if not message_claims:
        hero_proofs = proof_ids[:2]
        message_claims = [
            {
                "message_id": "claim_hero",
                "surface": "hero",
                "message": source.get("corridor_story")
                or "The corridor keeps workflow, proof posture, and overlays visible on one customer-safe page.",
                "claim_mode": "observed" if hero_proofs else "hypothesis",
                "proof_refs": hero_proofs,
            }
        ]
        for stage in canonical_stages:
            message_claims.append(
                {
                    "message_id": f"claim_{stage['stage_id']}",
                    "surface": "corridor",
                    "message": stage["headline"],
                    "claim_mode": stage["claim_mode"],
                    "proof_refs": stage["proof_refs"],
                }
            )

    normalized_claims = [
        {
            "message_id": str(claim.get("message_id") or f"claim_{index + 1}"),
            "surface": str(claim.get("surface") or "corridor"),
            "message": str(claim.get("message") or "Claim pending."),
            "claim_mode": _normalize_claim_mode(claim.get("claim_mode")),
            "proof_refs": _normalize_ref_list(claim.get("proof_refs")),
        }
        for index, claim in enumerate(message_claims)
        if isinstance(claim, dict)
    ]

    if isinstance(scenario_baseline, dict):
        baseline = {
            "baseline_id": str(scenario_baseline.get("baseline_id") or "baseline"),
            "label": str(scenario_baseline.get("label") or "Baseline"),
            "summary": str(scenario_baseline.get("summary") or "Corridor baseline."),
        }
    else:
        baseline = {
            "baseline_id": str(scenario_baseline),
            "label": source.get("baseline_label", "Workflow baseline"),
            "summary": str(
                source.get("baseline_summary")
                or "The default customer-safe corridor baseline used for external publication."
            ),
        }

    overlay_dimensions = overlay_dimensions or list(
        dict.fromkeys(
            [item["dimension"] for item in segment_overlays + operating_models]
            + ["package"]
        )
    )

    title = title or source.get("title") or "Configurable workflow corridor"
    corridor_story = str(
        source.get("corridor_story")
        or "This corridor page shows one canonical workflow, what changes by audience overlay, and what the product can actually prove."
    )
    source_artifact_ids = _normalize_ref_list(source.get("source_artifact_ids")) or ["workflow_spec_unknown"]

    workspace_input_refs = []
    for index, ref in enumerate(source.get("workspace_input_refs", [])):
        if not isinstance(ref, dict):
            continue
        workspace_input_refs.append(
            {
                "ref_id": str(ref.get("ref_id") or f"workspace_ref_{index + 1}"),
                "ref_type": str(ref.get("ref_type") or "workspace_input"),
                "label": str(ref.get("label") or f"Workspace input {index + 1}"),
                "customer_safe": bool(ref.get("customer_safe", customer_safe)),
            }
        )
    if not workspace_input_refs:
        workspace_input_refs.append(
            {
                "ref_id": f"workspace_manifest_{workspace_id}",
                "ref_type": "workspace_manifest",
                "label": "Workspace baseline context",
                "customer_safe": customer_safe,
            }
        )

    default_scenario_order = [item["overlay_id"] for item in segment_overlays + operating_models]
    curated.setdefault("manual_copy_overrides", [])
    curated.setdefault("scenario_order", default_scenario_order)
    curated.setdefault("highlighted_baseline", baseline["baseline_id"])
    curated.setdefault(
        "highlighted_terminal_outcome_ids",
        [item["outcome_id"] for item in terminal_outcomes[:1]],
    )
    curated.setdefault("audience_simplifications", [])

    return {
        "schema_version": "1.0.0",
        "workflow_corridor_spec_id": f"workflow_corridor_spec_{corridor_id}",
        "workspace_id": workspace_id,
        "visual_form": "configurable_workflow_corridor",
        "title": title,
        "corridor_story": corridor_story,
        "audience_mode": audience_mode,
        "publication_mode": publication_mode,
        "scenario_baseline": baseline,
        "overlay_dimensions": overlay_dimensions,
        "source_artifact_ids": source_artifact_ids,
        "workspace_input_refs": workspace_input_refs,
        "canonical_stages": canonical_stages,
        "lanes": lanes,
        "operating_models": operating_models,
        "persona_views": persona_views,
        "segment_overlays": segment_overlays,
        "package_scope": package_scope,
        "ownership_rules": {
            "ambiguity_fails_publish": bool(source.get("ownership_rules", {}).get("ambiguity_fails_publish", True)),
            "must_show_blocked_handoffs": bool(source.get("ownership_rules", {}).get("must_show_blocked_handoffs", True)),
            "must_show_owner_labels": bool(source.get("ownership_rules", {}).get("must_show_owner_labels", True)),
            "hidden_by_default_rules": deepcopy(source.get("ownership_rules", {}).get("hidden_by_default_rules"))
            or [
                {
                    "rule_id": "hide_workspace_internal",
                    "label": "Hide workspace-internal detail",
                    "applies_to": "workspace_input_refs",
                    "reason": "Public corridor pages must remain customer-safe.",
                }
            ],
        },
        "owner_transitions": owner_transitions,
        "terminal_outcomes": terminal_outcomes,
        "kpi_mappings": kpi_mappings,
        "proof_items": proof_items,
        "message_claims": normalized_claims,
        "visibility_policy": {
            "default_visibility": "customer_safe" if customer_safe else "internal",
            "permitted_audiences": [audience_mode],
            "allowed_claim_modes": ["observed", "inferred", "hypothesis"],
            "customer_safe_filtering": {
                "hide_internal_labels": customer_safe,
                "hide_private_proof_items": customer_safe,
                "hide_workspace_sensitive_refs": customer_safe,
            },
            "redaction_notes": deepcopy(source.get("redaction_notes", []))
            or ["Internal workspace detail stays hidden in customer-safe publication mode."],
        },
        "curated_overrides": curated,
        "customer_safe": customer_safe,
        "created_at": source.get("created_at", now_iso()),
    }


def build_corridor_proof_pack(workflow_corridor_spec: dict[str, Any]) -> dict[str, Any]:
    proof_items = deepcopy(workflow_corridor_spec["proof_items"])
    customer_safe = bool(workflow_corridor_spec["customer_safe"])
    visible_proof_items = [
        {
            "proof_id": item["proof_id"],
            "label": item["label"],
            "summary": item["summary"],
            "claim_mode": item["claim_mode"],
            "source_artifact_id": item["source_artifact_id"],
            "customer_safe": item.get("customer_safe", True),
        }
        for item in proof_items
        if _visible_for_customer(item, customer_safe)
    ]
    proof_lookup = {item["proof_id"]: item for item in proof_items}

    claim_mode_counts = {"observed": 0, "inferred": 0, "hypothesis": 0}
    claim_register: list[dict[str, Any]] = []
    proof_gaps: list[str] = []
    for claim in workflow_corridor_spec["message_claims"]:
        claim_mode = claim["claim_mode"] if claim.get("claim_mode") in claim_mode_counts else "hypothesis"
        claim_mode_counts[claim_mode] += 1
        proof_refs = claim.get("proof_refs", [])
        referenced = [proof_lookup[proof_id] for proof_id in proof_refs if proof_id in proof_lookup]
        if not referenced:
            support_status = "gap"
            proof_gaps.append(f"{claim['message_id']} has no linked proof items.")
        elif claim_mode == "observed":
            support_status = "supported"
        else:
            support_status = "bounded"
        claim_register.append(
            {
                "message_id": claim["message_id"],
                "claim_mode": claim_mode,
                "support_status": support_status,
                "proof_refs": proof_refs,
                "customer_safe": all(item.get("customer_safe", True) for item in referenced) if referenced else False,
            }
        )

    visibility_exceptions = [
        f"{item['proof_id']} is hidden in customer-safe mode."
        for item in proof_items
        if customer_safe and not _visible_for_customer(item, customer_safe)
    ]

    return {
        "schema_version": "1.0.0",
        "corridor_proof_pack_id": workflow_corridor_spec["workflow_corridor_spec_id"].replace(
            "workflow_corridor_spec", "corridor_proof_pack"
        ),
        "workflow_corridor_spec_id": workflow_corridor_spec["workflow_corridor_spec_id"],
        "workspace_id": workflow_corridor_spec["workspace_id"],
        "proof_summary": (
            f"{claim_mode_counts['observed']} observed claims, "
            f"{claim_mode_counts['inferred']} inferred claims, and "
            f"{claim_mode_counts['hypothesis']} hypothesis-level claims were registered for the corridor."
        ),
        "claim_mode_counts": claim_mode_counts,
        "claim_register": claim_register,
        "proof_items": visible_proof_items if customer_safe else proof_items,
        "proof_gaps": proof_gaps,
        "visibility_exceptions": visibility_exceptions,
        "customer_safe": customer_safe,
        "created_at": now_iso(),
    }


def build_corridor_narrative_plan(
    workflow_corridor_spec: dict[str, Any],
    corridor_proof_pack: dict[str, Any],
) -> dict[str, Any]:
    primary_message = workflow_corridor_spec["corridor_story"]
    reading_paths = corridor_reading_paths()
    desktop_path = reading_paths["desktop"]
    mobile_path = reading_paths["mobile"]
    moves = [
        {
            "section_id": "hero",
            "section_label": "Decision story",
            "primary_message": primary_message,
            "claim_mode": workflow_corridor_spec["message_claims"][0]["claim_mode"],
            "proof_refs": workflow_corridor_spec["message_claims"][0]["proof_refs"],
        },
        {
            "section_id": "corridor",
            "section_label": "Canonical corridor",
            "primary_message": "Show canonical stages and ownership transitions before overlay detail.",
            "claim_mode": "observed",
            "proof_refs": [corridor_proof_pack["proof_items"][0]["proof_id"]] if corridor_proof_pack["proof_items"] else [],
        },
        {
            "section_id": "personas",
            "section_label": "Persona visibility",
            "primary_message": "Make persona-specific visibility explicit so the page explains itself.",
            "claim_mode": "observed",
            "proof_refs": workflow_corridor_spec["persona_views"][0]["priority_proof_refs"],
        },
        {
            "section_id": "overlays",
            "section_label": "Scenario deltas",
            "primary_message": "Keep overlays secondary to the main corridor but concrete enough to support package and segment decisions.",
            "claim_mode": "observed",
            "proof_refs": [item["proof_id"] for item in corridor_proof_pack["proof_items"][:1]],
        },
        {
            "section_id": "proof",
            "section_label": "Proof rail",
            "primary_message": "Observed proof and bounded inference must remain visibly distinct.",
            "claim_mode": "inferred" if corridor_proof_pack["claim_mode_counts"]["inferred"] else "observed",
            "proof_refs": [item["proof_id"] for item in corridor_proof_pack["proof_items"][:2]],
        },
        {
            "section_id": "outcomes",
            "section_label": "Terminal outcomes",
            "primary_message": "Close on the customer-facing outcome and the KPI it supports.",
            "claim_mode": workflow_corridor_spec["terminal_outcomes"][0]["claim_mode"],
            "proof_refs": workflow_corridor_spec["terminal_outcomes"][0]["proof_refs"],
        },
    ]

    return {
        "schema_version": "1.0.0",
        "corridor_narrative_plan_id": workflow_corridor_spec["workflow_corridor_spec_id"].replace(
            "workflow_corridor_spec", "corridor_narrative_plan"
        ),
        "workflow_corridor_spec_id": workflow_corridor_spec["workflow_corridor_spec_id"],
        "corridor_proof_pack_id": corridor_proof_pack["corridor_proof_pack_id"],
        "workspace_id": workflow_corridor_spec["workspace_id"],
        "primary_message": primary_message,
        "section_order": desktop_path,
        "narrative_moves": moves,
        "desktop_reading_path": desktop_path,
        "mobile_reading_path": mobile_path,
        "created_at": now_iso(),
    }


def build_corridor_render_model(
    workflow_corridor_spec: dict[str, Any],
    corridor_proof_pack: dict[str, Any],
    corridor_narrative_plan: dict[str, Any],
) -> dict[str, Any]:
    customer_safe = workflow_corridor_spec["customer_safe"]
    theme = corridor_theme(corridor_theme_preset_for_publication(workflow_corridor_spec["publication_mode"]))

    visible_stages = [item for item in workflow_corridor_spec["canonical_stages"] if _visible_for_customer(item, customer_safe)]
    visible_personas = [item for item in workflow_corridor_spec["persona_views"] if _visible_for_customer(item, customer_safe)]
    visible_segment_overlays = [item for item in workflow_corridor_spec["segment_overlays"] if _visible_for_customer(item, customer_safe)]
    visible_operating_models = [item for item in workflow_corridor_spec["operating_models"] if _visible_for_customer(item, customer_safe)]
    visible_packages = [item for item in workflow_corridor_spec["package_scope"] if _visible_for_customer(item, customer_safe)]
    visible_transitions = [item for item in workflow_corridor_spec["owner_transitions"] if _visible_for_customer(item, customer_safe)]
    visible_outcomes = [item for item in workflow_corridor_spec["terminal_outcomes"] if _visible_for_customer(item, customer_safe)]

    stage_lookup = {item["stage_id"]: item for item in visible_stages}
    proof_lookup = {item["proof_id"]: item for item in corridor_proof_pack["proof_items"]}
    kpi_lookup = {item["kpi_id"]: item for item in workflow_corridor_spec["kpi_mappings"]}

    corridor_cards = []
    for stage in visible_stages:
        lane_labels = [
            lane["label"]
            for lane in workflow_corridor_spec["lanes"]
            if lane["lane_id"] in stage["lane_ids"] and _visible_for_customer(lane, customer_safe)
        ]
        corridor_cards.append(
            {
                "card_id": stage["stage_id"],
                "label": stage["label"],
                "headline": stage["headline"],
                "summary": stage["summary"],
                "owner_role": stage["owner_role"],
                "status": stage["status"],
                "claim_mode": stage["claim_mode"],
                "lane_labels": lane_labels,
                "proof_refs": stage["proof_refs"],
            }
        )

    persona_cards = []
    for persona in visible_personas:
        persona_cards.append(
            {
                "card_id": persona["persona_id"],
                "label": persona["label"],
                "summary": persona["summary"],
                "goal": persona["goal"],
                "visible_stage_ids": persona["visible_stage_ids"],
                "priority_proof_refs": persona["priority_proof_refs"],
            }
        )

    overlay_cards = []
    ordered_overlay_ids = workflow_corridor_spec["curated_overrides"]["scenario_order"]
    combined_overlays = {item["overlay_id"]: item for item in visible_segment_overlays + visible_operating_models}
    for overlay_id in ordered_overlay_ids:
        overlay = combined_overlays.get(overlay_id)
        if overlay:
            overlay_cards.append(
                {
                    "card_id": overlay["overlay_id"],
                    "label": overlay["label"],
                    "summary": overlay["summary"],
                    "dimension": overlay["dimension"],
                    "impact_stage_ids": overlay["impact_stage_ids"],
                    "claim_mode": overlay["claim_mode"],
                }
            )
    for package in visible_packages:
        overlay_cards.append(
            {
                "card_id": package["package_id"],
                "label": package["label"],
                "summary": package["summary"],
                "dimension": "package",
                "impact_stage_ids": package["included_stage_ids"],
                "claim_mode": "observed",
            }
        )

    proof_rail = [
        {
            "proof_id": item["proof_id"],
            "label": item["label"],
            "claim_mode": item["claim_mode"],
            "summary": item["summary"],
        }
        for item in corridor_proof_pack["proof_items"]
    ]

    governance_signals = [
        {
            "signal_id": transition["transition_id"],
            "label": (
                f"{transition['from_owner_role']} -> {transition['to_owner_role']} "
                f"between {stage_lookup.get(transition['from_stage_id'], {'label': transition['from_stage_id']})['label']} "
                f"and {stage_lookup.get(transition['to_stage_id'], {'label': transition['to_stage_id']})['label']}"
            ),
            "status": transition["status"],
            "summary": (
                f"Handoff is {transition['status']} and tagged as {transition['claim_mode']}."
            ),
        }
        for transition in visible_transitions
    ]

    terminal_outcomes = []
    for outcome in visible_outcomes:
        kpis = [kpi_lookup[kpi_id] for kpi_id in outcome["kpi_refs"] if kpi_id in kpi_lookup]
        terminal_outcomes.append(
            {
                "outcome_id": outcome["outcome_id"],
                "label": outcome["label"],
                "status": outcome["status"],
                "summary": outcome["summary"],
                "kpi_labels": [item["label"] for item in kpis],
                "claim_mode": outcome["claim_mode"],
            }
        )

    sections = [
        {
            "section_id": "hero",
            "heading": workflow_corridor_spec["title"],
            "primary_message": corridor_narrative_plan["primary_message"],
            "layout": "hero",
            "cards": [
                {
                    "card_id": workflow_corridor_spec["scenario_baseline"]["baseline_id"],
                    "label": workflow_corridor_spec["scenario_baseline"]["label"],
                    "summary": workflow_corridor_spec["scenario_baseline"]["summary"],
                }
            ],
        },
        {
            "section_id": "corridor",
            "heading": "Canonical corridor",
            "primary_message": corridor_narrative_plan["narrative_moves"][1]["primary_message"],
            "layout": "corridor_band",
            "cards": corridor_cards,
        },
        {
            "section_id": "personas",
            "heading": "Persona visibility matrix",
            "primary_message": corridor_narrative_plan["narrative_moves"][2]["primary_message"],
            "layout": "matrix",
            "cards": persona_cards,
        },
        {
            "section_id": "overlays",
            "heading": "Scenario overlays",
            "primary_message": corridor_narrative_plan["narrative_moves"][3]["primary_message"],
            "layout": "delta_panels",
            "cards": overlay_cards,
        },
        {
            "section_id": "proof",
            "heading": "Proof rail",
            "primary_message": corridor_narrative_plan["narrative_moves"][4]["primary_message"],
            "layout": "proof_rail",
            "cards": proof_rail,
        },
        {
            "section_id": "outcomes",
            "heading": "Terminal outcomes",
            "primary_message": corridor_narrative_plan["narrative_moves"][5]["primary_message"],
            "layout": "outcome_cards",
            "cards": terminal_outcomes,
        },
    ]

    layout_guardrails = {
        "one_primary_message_per_screen": all(section.get("primary_message") for section in sections),
        "proof_vs_inference_visible": True,
        "customer_safe_filter_applied": customer_safe,
        "slide_like_repetition": False,
        "generic_dashboard_pattern": False,
    }

    return {
        "schema_version": "1.0.0",
        "corridor_render_model_id": workflow_corridor_spec["workflow_corridor_spec_id"].replace(
            "workflow_corridor_spec", "corridor_render_model"
        ),
        "workflow_corridor_spec_id": workflow_corridor_spec["workflow_corridor_spec_id"],
        "corridor_proof_pack_id": corridor_proof_pack["corridor_proof_pack_id"],
        "corridor_narrative_plan_id": corridor_narrative_plan["corridor_narrative_plan_id"],
        "workspace_id": workflow_corridor_spec["workspace_id"],
        "visual_form": "configurable_workflow_corridor",
        "audience_mode": workflow_corridor_spec["audience_mode"],
        "publication_mode": workflow_corridor_spec["publication_mode"],
        "customer_safe": customer_safe,
        "theme": {
            "preset": theme["preset"],
            "display_font": theme["display_font"],
            "body_font": theme["body_font"],
            "accent": theme["accent"],
            "background": theme["background"],
        },
        "reading_path": {
            "desktop": corridor_narrative_plan["desktop_reading_path"],
            "mobile": corridor_narrative_plan["mobile_reading_path"],
        },
        "sections": sections,
        "proof_rail": proof_rail,
        "governance_signals": governance_signals,
        "terminal_outcomes": terminal_outcomes,
        "layout_guardrails": layout_guardrails,
        "created_at": now_iso(),
    }


def _score(base: float, penalties: list[bool], step: float = 0.6) -> float:
    score = base - sum(step for penalty in penalties if penalty)
    return max(0.0, min(5.0, round(score, 1)))


def build_corridor_publish_check(
    workflow_corridor_spec: dict[str, Any],
    corridor_render_model: dict[str, Any],
    corridor_proof_pack: dict[str, Any] | None = None,
) -> dict[str, Any]:
    proof_pack = corridor_proof_pack or build_corridor_proof_pack(workflow_corridor_spec)
    blocking_issues: list[str] = []
    warnings: list[str] = []

    missing_claim_modes = [
        claim["message_id"]
        for claim in workflow_corridor_spec["message_claims"]
        if claim.get("claim_mode") not in {"observed", "inferred", "hypothesis"}
    ]
    if missing_claim_modes:
        blocking_issues.append("Claim mode distinction is missing for one or more corridor messages.")

    if any(item.get("support_status") == "gap" for item in proof_pack["claim_register"]):
        blocking_issues.append("Proof visibility is incomplete because some corridor claims have no linked proof.")

    if workflow_corridor_spec["customer_safe"]:
        if not corridor_render_model["layout_guardrails"]["customer_safe_filter_applied"]:
            blocking_issues.append("Customer-safe filtering was not applied inside render logic.")
        if any(item.get("visibility") == "internal" for item in workflow_corridor_spec["canonical_stages"]):
            blocking_issues.append("Customer-safe filtering is incomplete because an internal stage is still present in the spec.")
        if any(not ref.get("customer_safe", True) for ref in workflow_corridor_spec["workspace_input_refs"]):
            warnings.append("Some workspace inputs were kept out of the published page by customer-safe filtering.")

    ambiguous_transitions = [
        transition["transition_id"]
        for transition in workflow_corridor_spec["owner_transitions"]
        if not transition.get("from_owner_role") or not transition.get("to_owner_role")
    ]
    if ambiguous_transitions or not workflow_corridor_spec["owner_transitions"]:
        blocking_issues.append("Ownership or handoff transitions are ambiguous.")

    if corridor_render_model["layout_guardrails"]["slide_like_repetition"]:
        blocking_issues.append("The corridor page degraded into slide-like repetition.")
    if corridor_render_model["layout_guardrails"]["generic_dashboard_pattern"]:
        blocking_issues.append("The corridor page degraded into a generic dashboard structure.")

    required_paths = corridor_reading_paths()
    required_desktop = required_paths["desktop"]
    required_mobile = required_paths["mobile"]
    if corridor_render_model["reading_path"]["desktop"] != required_desktop:
        blocking_issues.append("Desktop reading path no longer matches corridor narrative order.")
    if corridor_render_model["reading_path"]["mobile"] != required_mobile:
        blocking_issues.append("Mobile reading path collapses the intended corridor sequence.")

    if any(signal["status"] == "blocked" for signal in corridor_render_model["governance_signals"]):
        warnings.append("A blocked handoff remains visible in the governance rail.")
    if proof_pack["claim_mode_counts"]["inferred"] or proof_pack["claim_mode_counts"]["hypothesis"]:
        warnings.append("Some claims remain bounded as inferred or hypothesis-level.")

    narrative_clarity_score = _score(
        5.0,
        [
            not corridor_render_model["layout_guardrails"]["one_primary_message_per_screen"],
            not workflow_corridor_spec["corridor_story"],
        ],
    )
    proof_visibility_score = _score(
        5.0,
        [
            bool(proof_pack["proof_gaps"]),
            not corridor_render_model["layout_guardrails"]["proof_vs_inference_visible"],
        ],
    )
    workflow_credibility_score = _score(
        4.8,
        [
            bool(ambiguous_transitions),
            not workflow_corridor_spec["ownership_rules"]["must_show_blocked_handoffs"],
        ],
    )
    visual_hierarchy_score = _score(
        4.8,
        [
            corridor_render_model["layout_guardrails"]["slide_like_repetition"],
            corridor_render_model["layout_guardrails"]["generic_dashboard_pattern"],
        ],
    )
    audience_safety_score = _score(
        5.0,
        [
            workflow_corridor_spec["customer_safe"] and not corridor_render_model["layout_guardrails"]["customer_safe_filter_applied"],
            any(not item.get("customer_safe", True) for item in proof_pack["proof_items"]),
        ],
    )
    composition_fit_score = _score(
        4.9,
        [
            corridor_render_model["visual_form"] != "configurable_workflow_corridor",
            corridor_render_model["layout_guardrails"]["generic_dashboard_pattern"],
        ],
    )
    desktop_reading_path_score = _score(4.8, [corridor_render_model["reading_path"]["desktop"] != required_desktop])
    mobile_reading_path_score = _score(4.8, [corridor_render_model["reading_path"]["mobile"] != required_mobile])

    publish_ready = not blocking_issues and audience_safety_score >= 4.5 and proof_visibility_score >= 4.0
    minimum_score = min(
        narrative_clarity_score,
        proof_visibility_score,
        workflow_credibility_score,
        visual_hierarchy_score,
        audience_safety_score,
        composition_fit_score,
        desktop_reading_path_score,
        mobile_reading_path_score,
    )
    review_grade = "excellent" if publish_ready and minimum_score >= 4.5 else "good" if publish_ready else "blocked" if blocking_issues else "revise"

    return {
        "schema_version": "1.0.0",
        "corridor_publish_check_id": workflow_corridor_spec["workflow_corridor_spec_id"].replace(
            "workflow_corridor_spec", "corridor_publish_check"
        ),
        "workflow_corridor_spec_id": workflow_corridor_spec["workflow_corridor_spec_id"],
        "corridor_render_model_id": corridor_render_model["corridor_render_model_id"],
        "workspace_id": workflow_corridor_spec["workspace_id"],
        "publish_ready": publish_ready,
        "review_grade": review_grade,
        "world_class_claim_allowed": review_grade == "excellent",
        "publication_allowed": publish_ready and (not workflow_corridor_spec["customer_safe"] or audience_safety_score >= 4.5),
        "narrative_clarity_score": narrative_clarity_score,
        "proof_visibility_score": proof_visibility_score,
        "workflow_credibility_score": workflow_credibility_score,
        "visual_hierarchy_score": visual_hierarchy_score,
        "audience_safety_score": audience_safety_score,
        "composition_fit_score": composition_fit_score,
        "desktop_reading_path_score": desktop_reading_path_score,
        "mobile_reading_path_score": mobile_reading_path_score,
        "blocking_issues": blocking_issues,
        "warnings": warnings,
        "created_at": now_iso(),
    }


def build_workflow_corridor_bundle(
    source_bundle: dict[str, Any],
    *,
    corridor_id: str | None = None,
    workspace_id: str | None = None,
    title: str | None = None,
    audience_mode: str = "customer_safe_public",
    publication_mode: str = "publishable_external",
    scenario_baseline: str | dict[str, str] = "core_baseline",
    overlay_dimensions: list[str] | None = None,
    curated_overrides: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    spec = build_workflow_corridor_spec(
        source_bundle,
        corridor_id=corridor_id,
        workspace_id=workspace_id,
        title=title,
        audience_mode=audience_mode,
        publication_mode=publication_mode,
        scenario_baseline=scenario_baseline,
        overlay_dimensions=overlay_dimensions,
        curated_overrides=curated_overrides,
    )
    proof_pack = build_corridor_proof_pack(spec)
    narrative_plan = build_corridor_narrative_plan(spec, proof_pack)
    render_model = build_corridor_render_model(spec, proof_pack, narrative_plan)
    publish_check = build_corridor_publish_check(spec, render_model, proof_pack)
    return {
        "workflow_corridor_spec": spec,
        "corridor_proof_pack": proof_pack,
        "corridor_narrative_plan": narrative_plan,
        "corridor_render_model": render_model,
        "corridor_publish_check": publish_check,
    }


def _render_claim_badge(claim_mode: str) -> str:
    return f'<span class="claim-badge claim-{escape(claim_mode)}">{escape(claim_mode)}</span>'


def render_corridor_html(corridor_render_model: dict[str, Any]) -> str:
    theme = corridor_render_model["theme"]
    sections_by_id = {section["section_id"]: section for section in corridor_render_model["sections"]}
    hero = sections_by_id["hero"]
    corridor = sections_by_id["corridor"]
    personas = sections_by_id["personas"]
    overlays = sections_by_id["overlays"]
    proof = sections_by_id["proof"]
    outcomes = sections_by_id["outcomes"]

    corridor_cards = "".join(
        (
            '<article class="stage-card state-{status}">'
            "<div class=\"stage-meta\">"
            "<span class=\"stage-label\">{label}</span>"
            "<span class=\"stage-owner\">{owner}</span>"
            "{claim_badge}"
            "</div>"
            "<h3>{headline}</h3>"
            "<p>{summary}</p>"
            "<div class=\"stage-lanes\">{lanes}</div>"
            "</article>"
        ).format(
            status=escape(card["status"]),
            label=escape(card["label"]),
            owner=escape(card["owner_role"]),
            claim_badge=_render_claim_badge(card["claim_mode"]),
            headline=escape(card["headline"]),
            summary=escape(card["summary"]),
            lanes="".join(f"<span>{escape(lane)}</span>" for lane in card["lane_labels"]),
        )
        for card in corridor["cards"]
    )
    governance_cards = "".join(
        (
            '<article class="governance-card state-{status}">'
            "<h4>{label}</h4>"
            "<p>{summary}</p>"
            "</article>"
        ).format(
            status=escape(item["status"]),
            label=escape(item["label"]),
            summary=escape(item["summary"]),
        )
        for item in corridor_render_model["governance_signals"]
    )
    persona_rows = "".join(
        (
            "<tr>"
            "<th>{label}</th>"
            "<td>{goal}</td>"
            "<td>{stages}</td>"
            "<td>{proofs}</td>"
            "</tr>"
        ).format(
            label=escape(card["label"]),
            goal=escape(card["goal"]),
            stages=", ".join(escape(stage_id.replace("stage_", "").replace("_", " ").title()) for stage_id in card["visible_stage_ids"]),
            proofs=", ".join(escape(proof_id.replace("proof_", "").replace("_", " ").title()) for proof_id in card["priority_proof_refs"]) or "Baseline proof rail",
        )
        for card in personas["cards"]
    )
    overlay_cards = "".join(
        (
            '<article class="overlay-card">'
            "<div class=\"overlay-top\">"
            "<span class=\"overlay-dimension\">{dimension}</span>"
            "{claim_badge}"
            "</div>"
            "<h4>{label}</h4>"
            "<p>{summary}</p>"
            "<div class=\"impact-row\">Impacts: {impacts}</div>"
            "</article>"
        ).format(
            dimension=escape(card["dimension"].replace("_", " ")),
            claim_badge=_render_claim_badge(card["claim_mode"]),
            label=escape(card["label"]),
            summary=escape(card["summary"]),
            impacts=", ".join(escape(stage_id.replace("stage_", "").replace("_", " ").title()) for stage_id in card["impact_stage_ids"]),
        )
        for card in overlays["cards"]
    )
    proof_cards = "".join(
        (
            '<article class="proof-card">'
            "<div class=\"proof-top\">{claim_badge}<span>{label}</span></div>"
            "<p>{summary}</p>"
            "</article>"
        ).format(
            claim_badge=_render_claim_badge(card["claim_mode"]),
            label=escape(card["label"]),
            summary=escape(card["summary"]),
        )
        for card in proof["cards"]
    )
    outcome_cards = "".join(
        (
            '<article class="outcome-card state-{status}">'
            "<div class=\"outcome-top\">{claim_badge}<span>{label}</span></div>"
            "<p>{summary}</p>"
            "<div class=\"outcome-kpis\">{kpis}</div>"
            "</article>"
        ).format(
            status=escape(card["status"]),
            claim_badge=_render_claim_badge(card["claim_mode"]),
            label=escape(card["label"]),
            summary=escape(card["summary"]),
            kpis=", ".join(escape(label) for label in card.get("kpi_labels", [])) or "Outcome KPI",
        )
        for card in outcomes["cards"]
    )
    reading_path = "".join(
        f"<li>{escape(item.replace('_', ' ').title())}</li>"
        for item in corridor_render_model["reading_path"]["mobile"]
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(hero["heading"])}</title>
  <style>
    :root {{
      --bg: {theme["background"]};
      --ink: #182028;
      --muted: #5f6c76;
      --panel: rgba(255, 255, 255, 0.86);
      --line: rgba(24, 32, 40, 0.12);
      --accent: {theme["accent"]};
      --watch: #d88b1f;
      --blocked: #b53f2e;
      --ok: #1d7c58;
      --shadow: 0 28px 80px rgba(24, 32, 40, 0.12);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: {theme["body_font"]};
      color: var(--ink);
      background: var(--bg);
      line-height: 1.45;
    }}
    h1, h2, h3, h4 {{
      font-family: {theme["display_font"]};
      margin: 0;
      letter-spacing: -0.03em;
    }}
    p {{ margin: 0; color: var(--muted); }}
    .workflow-corridor {{
      max-width: 1440px;
      margin: 0 auto;
      padding: 32px 20px 72px;
    }}
    .hero-shell {{
      position: relative;
      overflow: hidden;
      background: rgba(255,255,255,0.74);
      border: 1px solid rgba(24,32,40,0.08);
      border-radius: 32px;
      box-shadow: var(--shadow);
      padding: 32px;
      display: grid;
      gap: 24px;
    }}
    .hero-shell::after {{
      content: "";
      position: absolute;
      inset: auto -10% -30% auto;
      width: 360px;
      height: 360px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(247,100,50,0.18), rgba(247,100,50,0));
      pointer-events: none;
    }}
    .eyebrow {{
      display: inline-flex;
      align-items: center;
      gap: 10px;
      text-transform: uppercase;
      font-size: 12px;
      letter-spacing: 0.14em;
      color: var(--muted);
    }}
    .eyebrow strong {{
      color: var(--accent);
    }}
    .hero-grid {{
      display: grid;
      grid-template-columns: minmax(0, 1.7fr) minmax(280px, 0.9fr);
      gap: 24px;
      align-items: start;
    }}
    .hero-copy h1 {{
      font-size: clamp(2.4rem, 4vw, 4.6rem);
      line-height: 0.95;
      max-width: 14ch;
    }}
    .hero-copy p {{
      margin-top: 18px;
      font-size: 1.05rem;
      max-width: 64ch;
    }}
    .baseline-card, .section-shell, .proof-rail, .outcome-strip {{
      background: var(--panel);
      border: 1px solid rgba(24,32,40,0.08);
      border-radius: 28px;
      box-shadow: var(--shadow);
    }}
    .baseline-card {{
      padding: 20px;
    }}
    .section-shell {{
      margin-top: 24px;
      padding: 24px;
    }}
    .section-head {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 12px;
      align-items: end;
      margin-bottom: 18px;
    }}
    .section-head h2 {{
      font-size: clamp(1.5rem, 2vw, 2.3rem);
    }}
    .section-head p {{
      max-width: 56ch;
    }}
    .reading-path {{
      list-style: none;
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      padding: 0;
      margin: 0;
    }}
    .reading-path li,
    .claim-badge,
    .stage-lanes span,
    .outcome-kpis,
    .overlay-dimension {{
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 6px 10px;
      font-size: 12px;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      background: rgba(255,255,255,0.72);
    }}
    .claim-badge {{
      font-weight: 700;
      color: var(--ink);
    }}
    .claim-observed {{ border-color: rgba(29,124,88,0.28); color: var(--ok); }}
    .claim-inferred {{ border-color: rgba(216,139,31,0.32); color: var(--watch); }}
    .claim-hypothesis {{ border-color: rgba(181,63,46,0.32); color: var(--blocked); }}
    .corridor-band {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
      position: relative;
    }}
    .corridor-band::before {{
      content: "";
      position: absolute;
      top: 38px;
      left: 6%;
      right: 6%;
      height: 3px;
      background: linear-gradient(90deg, rgba(247,100,50,0.2), rgba(24,32,40,0.12));
      z-index: 0;
    }}
    .stage-card, .overlay-card, .proof-card, .governance-card, .outcome-card {{
      position: relative;
      z-index: 1;
      background: rgba(255,255,255,0.85);
      border: 1px solid var(--line);
      border-radius: 22px;
      padding: 18px;
      display: grid;
      gap: 12px;
    }}
    .stage-card.state-blocked,
    .governance-card.state-blocked,
    .outcome-card.state-blocked {{
      border-color: rgba(181,63,46,0.35);
      box-shadow: inset 0 0 0 1px rgba(181,63,46,0.15);
    }}
    .stage-card.state-watch,
    .governance-card.state-watch,
    .outcome-card.state-watch {{
      border-color: rgba(216,139,31,0.35);
      box-shadow: inset 0 0 0 1px rgba(216,139,31,0.12);
    }}
    .stage-meta, .proof-top, .outcome-top, .overlay-top {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      justify-content: space-between;
      align-items: center;
    }}
    .stage-label {{
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
    }}
    .stage-owner {{
      font-size: 0.85rem;
      color: var(--accent);
    }}
    .persona-matrix {{
      width: 100%;
      border-collapse: collapse;
      overflow: hidden;
      border-radius: 22px;
      border: 1px solid var(--line);
    }}
    .persona-matrix th,
    .persona-matrix td {{
      text-align: left;
      padding: 16px;
      border-bottom: 1px solid var(--line);
      vertical-align: top;
    }}
    .persona-matrix th {{
      font-family: {theme["display_font"]};
      width: 16%;
      background: rgba(255,255,255,0.78);
    }}
    .overlay-grid,
    .proof-grid,
    .outcome-grid,
    .governance-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
    }}
    @media (max-width: 980px) {{
      .hero-grid,
      .corridor-band,
      .overlay-grid,
      .proof-grid,
      .outcome-grid,
      .governance-grid {{
        grid-template-columns: 1fr;
      }}
      .corridor-band::before {{
        display: none;
      }}
      .workflow-corridor {{
        padding: 16px 14px 56px;
      }}
      .hero-shell,
      .section-shell {{
        border-radius: 24px;
        padding: 18px;
      }}
      .persona-matrix,
      .persona-matrix tbody,
      .persona-matrix tr,
      .persona-matrix th,
      .persona-matrix td {{
        display: block;
        width: 100%;
      }}
      .persona-matrix tr {{
        border-bottom: 1px solid var(--line);
      }}
    }}
  </style>
</head>
<body>
  <main class="workflow-corridor" data-publication-mode="{escape(corridor_render_model['publication_mode'])}">
    <section class="hero-shell">
      <div class="eyebrow">
        <strong>Workflow Corridor</strong>
        <span>{escape(corridor_render_model["audience_mode"].replace("_", " "))}</span>
      </div>
      <div class="hero-grid">
        <div class="hero-copy">
          <h1>{escape(hero["heading"])}</h1>
          <p>{escape(hero["primary_message"])}</p>
        </div>
        <aside class="baseline-card">
          <div class="eyebrow"><strong>Baseline</strong><span>{escape(hero["cards"][0]["label"])}</span></div>
          <p>{escape(hero["cards"][0]["summary"])}</p>
          <ul class="reading-path" aria-label="Mobile reading path">
            {reading_path}
          </ul>
        </aside>
      </div>
    </section>

    <section class="section-shell">
      <div class="section-head">
        <div>
          <h2>{escape(corridor["heading"])}</h2>
          <p>{escape(corridor["primary_message"])}</p>
        </div>
      </div>
      <div class="corridor-band">
        {corridor_cards}
      </div>
    </section>

    <section class="section-shell">
      <div class="section-head">
        <div>
          <h2>Governance Rail</h2>
          <p>Blocked, watch, inferred, and approved handoffs stay visible inside the corridor instead of hiding in notes.</p>
        </div>
      </div>
      <div class="governance-grid">
        {governance_cards}
      </div>
    </section>

    <section class="section-shell">
      <div class="section-head">
        <div>
          <h2>{escape(personas["heading"])}</h2>
          <p>{escape(personas["primary_message"])}</p>
        </div>
      </div>
      <table class="persona-matrix">
        <thead>
          <tr>
            <th>Persona</th>
            <th>Goal</th>
            <th>Visible stages</th>
            <th>Priority proof</th>
          </tr>
        </thead>
        <tbody>
          {persona_rows}
        </tbody>
      </table>
    </section>

    <section class="section-shell">
      <div class="section-head">
        <div>
          <h2>{escape(overlays["heading"])}</h2>
          <p>{escape(overlays["primary_message"])}</p>
        </div>
      </div>
      <div class="overlay-grid">
        {overlay_cards}
      </div>
    </section>

    <section class="section-shell proof-rail">
      <div class="section-head">
        <div>
          <h2>{escape(proof["heading"])}</h2>
          <p>{escape(proof["primary_message"])}</p>
        </div>
      </div>
      <div class="proof-grid">
        {proof_cards}
      </div>
    </section>

    <section class="section-shell outcome-strip">
      <div class="section-head">
        <div>
          <h2>{escape(outcomes["heading"])}</h2>
          <p>{escape(outcomes["primary_message"])}</p>
        </div>
      </div>
      <div class="outcome-grid">
        {outcome_cards}
      </div>
    </section>
  </main>
</body>
</html>
"""


def write_corridor_payload(payload: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def write_corridor_html(corridor_render_model: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_corridor_html(corridor_render_model), encoding="utf-8")
    return path
