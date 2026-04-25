from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.python.visual_foundations import (
    corridor_composition_strategy,
    corridor_theme_preset_for_publication,
    deck_composition_strategy,
    density_mode_for_preference,
    fidelity_mode_for_deck,
    fidelity_mode_for_map,
    map_composition_strategy,
    output_targets_for_deck,
    output_targets_for_map,
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _score(value: float) -> float:
    return max(0.0, min(5.0, round(float(value), 1)))


def _review_status(blockers: list[str], warnings: list[str]) -> str:
    if blockers:
        return "block"
    return "pass"


def _next_action(blockers: list[str], warnings: list[str]) -> str:
    if blockers:
        return "block"
    return "proceed"


def build_visual_direction_plan(
    visual_surface: str,
    payload: dict[str, Any],
    *,
    input_ref: str,
    aspect_ratio: str = "16:9",
    audience_mode: str | None = None,
    publication_mode: str | None = None,
    theme_name: str | None = None,
) -> dict[str, Any]:
    if visual_surface == "deck":
        presentation_format = payload.get("presentation_format", "both")
        return {
            "schema_version": "1.0.0",
            "visual_direction_plan_id": f"visual_direction_plan_{payload['presentation_brief_id']}",
            "workspace_id": payload["workspace_id"],
            "visual_surface": "deck",
            "source_artifact_type": "presentation_brief",
            "source_artifact_id": payload["presentation_brief_id"],
            "input_ref": input_ref,
            "audience": payload["audience"],
            "primary_message": payload["narrative_goal"],
            "design_tier": "world_class" if payload["audience_type"] == "leadership" else "premium",
            "theme_preset": payload["theme_preset"],
            "composition_strategy": deck_composition_strategy(payload),
            "density_mode": density_mode_for_preference(payload["density_preference"]),
            "output_targets": output_targets_for_deck(presentation_format),
            "fidelity_mode": fidelity_mode_for_deck(presentation_format),
            "customer_safe": payload["customer_safe"],
            "quality_gates": [
                "message_hierarchy",
                "publish_safety",
                "dual_target_fidelity",
                "evidence_visibility",
            ],
            "aspect_ratio": aspect_ratio,
            "notes": [
                payload["objective"],
                payload["success_outcome"],
            ],
            "generated_at": _now_iso(),
        }

    if visual_surface == "corridor":
        source_artifact_type = (
            "workflow_corridor_spec" if "workflow_corridor_spec_id" in payload else "workflow_corridor_source_bundle"
        )
        source_artifact_id = (
            payload.get("workflow_corridor_spec_id")
            or payload.get("corridor_id")
            or payload.get("title")
            or payload["workspace_id"]
        )
        audience = audience_mode or payload.get("audience_mode") or "customer_safe_public"
        return {
            "schema_version": "1.0.0",
            "visual_direction_plan_id": f"visual_direction_plan_{source_artifact_id}",
            "workspace_id": payload["workspace_id"],
            "visual_surface": "corridor",
            "source_artifact_type": source_artifact_type,
            "source_artifact_id": source_artifact_id,
            "input_ref": input_ref,
            "audience": audience,
            "primary_message": payload.get("corridor_story") or payload.get("title") or "Workflow corridor",
            "design_tier": "premium",
            "theme_preset": theme_name or corridor_theme_preset_for_publication(publication_mode or "publishable_external"),
            "composition_strategy": corridor_composition_strategy(),
            "density_mode": "balanced",
            "output_targets": ["html"],
            "fidelity_mode": "html_first",
            "customer_safe": publication_mode != "internal_review",
            "quality_gates": [
                "message_hierarchy",
                "publish_safety",
                "workflow_credibility",
                "reading_path",
            ],
            "aspect_ratio": aspect_ratio,
            "notes": [
                payload.get("title", "Workflow corridor"),
                publication_mode or "publishable_external",
            ],
            "generated_at": _now_iso(),
        }

    if visual_surface == "map":
        theme = theme_name or "atlas"
        return {
            "schema_version": "1.0.0",
            "visual_direction_plan_id": f"visual_direction_plan_{payload['visual_map_spec_id']}",
            "workspace_id": payload["workspace_id"],
            "visual_surface": "map",
            "source_artifact_type": "visual_map_spec",
            "source_artifact_id": payload["visual_map_spec_id"],
            "input_ref": input_ref,
            "audience": payload["audience"],
            "primary_message": payload["primary_message"],
            "design_tier": "premium",
            "theme_preset": theme,
            "composition_strategy": map_composition_strategy(payload),
            "density_mode": density_mode_for_preference(
                "dense" if payload["rendering_mode"] == "dashboard" else "balanced"
            ),
            "output_targets": output_targets_for_map(payload["rendering_mode"]),
            "fidelity_mode": fidelity_mode_for_map(payload["rendering_mode"]),
            "customer_safe": False,
            "quality_gates": [
                "message_hierarchy",
                "evidence_visibility",
                "reading_path",
                "map_semantics",
            ],
            "aspect_ratio": aspect_ratio,
            "notes": [
                payload["decision_use_case"],
                payload["map_type"],
            ],
            "generated_at": _now_iso(),
        }

    raise ValueError(f"Unsupported visual surface: {visual_surface}")


def visual_map_spec_targets_ppt(visual_map_spec: dict[str, Any]) -> bool:
    return "pptx" in output_targets_for_map(visual_map_spec["rendering_mode"])


def build_visual_quality_review_for_deck(
    visual_direction_plan: dict[str, Any],
    render_spec: dict[str, Any],
    publish_check: dict[str, Any],
) -> dict[str, Any]:
    warnings = [
        *publish_check.get("claim_support_exceptions", []),
        *publish_check.get("density_exceptions", []),
        *publish_check.get("fidelity_exceptions", []),
    ]
    blockers = list(publish_check.get("blocking_issues", []))
    strengths = [
        "Opening narrative is evaluated against an explicit publish bar.",
        "Source-linked evidence is preserved in the generated deck.",
        f"HTML fidelity status is {publish_check['html_fidelity_status']}.",
        f"PPT fidelity status is {publish_check['ppt_fidelity_status']}.",
    ]
    fidelity_score = 5.0
    if publish_check["html_fidelity_status"] != "aligned":
        fidelity_score -= 0.6
    if publish_check["ppt_fidelity_status"] != "aligned":
        fidelity_score -= 0.8

    return {
        "schema_version": "1.0.0",
        "visual_quality_review_id": f"visual_quality_review_{visual_direction_plan['source_artifact_id']}",
        "workspace_id": visual_direction_plan["workspace_id"],
        "visual_surface": "deck",
        "source_artifact_id": visual_direction_plan["source_artifact_id"],
        "visual_direction_plan_ref": visual_direction_plan["visual_direction_plan_id"],
        "output_ref": render_spec["render_spec_id"],
        "review_status": _review_status(blockers, warnings),
        "publish_ready": publish_check["publish_ready"],
        "narrative_clarity_score": _score(publish_check["narrative_quality_score"]),
        "visual_hierarchy_score": _score(publish_check["visual_clarity_score"]),
        "evidence_visibility_score": _score(publish_check["evidence_quality_score"]),
        "audience_fit_score": _score(publish_check["audience_fit_score"]),
        "fidelity_score": _score(fidelity_score),
        "strengths": strengths,
        "warnings": warnings,
        "blockers": blockers,
        "recommended_next_action": _next_action(blockers, warnings),
        "generated_at": _now_iso(),
    }


def build_visual_quality_review_for_corridor(
    visual_direction_plan: dict[str, Any],
    corridor_bundle: dict[str, Any],
) -> dict[str, Any]:
    publish_check = corridor_bundle["corridor_publish_check"]
    warnings = list(publish_check.get("warnings", []))
    blockers = list(publish_check.get("blocking_issues", []))
    strengths = [
        f"Corridor review grade is {publish_check['review_grade']}.",
        "Workflow proof posture is kept explicit in the corridor lane.",
        "Desktop and mobile reading paths are both scored explicitly.",
    ]
    fidelity_score = (publish_check["desktop_reading_path_score"] + publish_check["mobile_reading_path_score"]) / 2
    return {
        "schema_version": "1.0.0",
        "visual_quality_review_id": f"visual_quality_review_{visual_direction_plan['source_artifact_id']}",
        "workspace_id": visual_direction_plan["workspace_id"],
        "visual_surface": "corridor",
        "source_artifact_id": visual_direction_plan["source_artifact_id"],
        "visual_direction_plan_ref": visual_direction_plan["visual_direction_plan_id"],
        "output_ref": corridor_bundle["corridor_render_model"]["corridor_render_model_id"],
        "review_status": _review_status(blockers, warnings),
        "publish_ready": publish_check["publish_ready"],
        "narrative_clarity_score": _score(publish_check["narrative_clarity_score"]),
        "visual_hierarchy_score": _score(publish_check["visual_hierarchy_score"]),
        "evidence_visibility_score": _score(publish_check["proof_visibility_score"]),
        "audience_fit_score": _score(publish_check["audience_safety_score"]),
        "fidelity_score": _score(fidelity_score),
        "strengths": strengths,
        "warnings": warnings,
        "blockers": blockers,
        "recommended_next_action": _next_action(blockers, warnings),
        "generated_at": _now_iso(),
    }


def build_visual_quality_review_for_map(
    visual_direction_plan: dict[str, Any],
    render_spec: dict[str, Any],
) -> dict[str, Any]:
    slide = render_spec["slides"][0]
    map_payload = slide["composition_payload"].get("map_payload") or {}
    blockers: list[str] = []
    warnings: list[str] = []
    if not slide["source_refs"]:
        blockers.append("Map output is missing source references.")
    if not (map_payload.get("items") or map_payload.get("nodes")):
        warnings.append("Map output is relying on stages/lanes only without richer item or node content.")
    if "pptx" in visual_direction_plan["output_targets"] and slide["ppt_render_hints"].get("target_profile") == "ppt_safe":
        warnings.append("PPT-safe fallback is active for this map surface.")

    strengths = [
        "Map output keeps one primary message and explicit source labels.",
        "Map semantics are preserved through the normalized render spec.",
        f"Map composition uses {slide['composition_type']}.",
    ]
    evidence_visibility = 4.6 if slide["source_refs"] else 2.0
    if "pptx" in visual_direction_plan["output_targets"]:
        fidelity = 5.0 if slide["ppt_render_hints"].get("target_profile") == "dual_target" else 4.1
    else:
        fidelity = 5.0 if slide["html_render_hints"].get("target_profile") in {"dual_target", "html_rich"} else 4.1
    hierarchy = 4.7 if slide["headline"] and slide["core_message"] else 3.0
    return {
        "schema_version": "1.0.0",
        "visual_quality_review_id": f"visual_quality_review_{visual_direction_plan['source_artifact_id']}",
        "workspace_id": visual_direction_plan["workspace_id"],
        "visual_surface": "map",
        "source_artifact_id": visual_direction_plan["source_artifact_id"],
        "visual_direction_plan_ref": visual_direction_plan["visual_direction_plan_id"],
        "output_ref": render_spec["render_spec_id"],
        "review_status": _review_status(blockers, warnings),
        "publish_ready": not blockers,
        "narrative_clarity_score": _score(4.5),
        "visual_hierarchy_score": _score(hierarchy),
        "evidence_visibility_score": _score(evidence_visibility),
        "audience_fit_score": _score(4.4),
        "fidelity_score": _score(fidelity),
        "strengths": strengths,
        "warnings": warnings,
        "blockers": blockers,
        "recommended_next_action": _next_action(blockers, warnings),
        "generated_at": _now_iso(),
    }


def infer_visual_review_target(target: Path) -> Path:
    return target if target.is_dir() else target.parent
