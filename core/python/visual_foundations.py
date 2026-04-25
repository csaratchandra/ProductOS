from __future__ import annotations

from copy import deepcopy


_VISUAL_THEME_PRESETS = {
    "signal": {
        "preset": "signal",
        "font_family": "'Sora', 'Avenir Next', sans-serif",
        "background": "linear-gradient(160deg, #081826 0%, #113b5c 55%, #ff6f3c 100%)",
        "accent": "#ff6f3c",
    },
    "atlas": {
        "preset": "atlas",
        "font_family": "'Space Grotesk', 'Avenir Next', sans-serif",
        "background": "linear-gradient(135deg, #f7f2e8 0%, #d7e6f5 100%)",
        "accent": "#1e5aa8",
    },
    "editorial": {
        "preset": "editorial",
        "font_family": "'Fraunces', 'Georgia', serif",
        "background": "linear-gradient(135deg, #faf7f2 0%, #efe3d1 100%)",
        "accent": "#7a2418",
    },
    "corridor_public": {
        "preset": "corridor_public",
        "display_font": "'Space Grotesk', 'Avenir Next', sans-serif",
        "body_font": "'Manrope', 'Avenir Next', sans-serif",
        "accent": "#f76432",
        "background": "linear-gradient(180deg, #f5eee5 0%, #fffaf4 100%)",
        "ink": "#182028",
        "muted": "#5f6c76",
    },
    "corridor_browse": {
        "preset": "corridor_browse",
        "display_font": "'Sora', 'Avenir Next', sans-serif",
        "body_font": "'IBM Plex Sans', 'Avenir Next', sans-serif",
        "accent": "#0b7d75",
        "background": "linear-gradient(180deg, #edf8f6 0%, #f8fcfb 100%)",
        "ink": "#132028",
        "muted": "#537078",
    },
}

MAP_COMPOSITIONS = frozenset(
    {
        "roadmap_view",
        "user_journey_map",
        "process_flow",
        "workflow_map",
        "capability_map",
        "product_map",
        "feature_map",
        "mind_map",
        "swot_matrix",
        "impact_effort_matrix",
    }
)
MATRIX_MAP_COMPOSITIONS = frozenset({"swot_matrix", "impact_effort_matrix"})
CANVAS_MAP_COMPOSITIONS = MAP_COMPOSITIONS - MATRIX_MAP_COMPOSITIONS
HTML_RICH_COMPOSITIONS = frozenset(
    {
        "comparison_table",
        "metric_strip",
        "roadmap_view",
        "user_journey_map",
        "process_flow",
        "workflow_map",
        "capability_map",
        "product_map",
        "feature_map",
        "mind_map",
        "swot_matrix",
        "impact_effort_matrix",
    }
)

_CORRIDOR_READING_PATHS = {
    "desktop": ["hero", "corridor", "personas", "overlays", "proof", "outcomes"],
    "mobile": ["hero", "corridor", "proof", "personas", "overlays", "outcomes"],
}


def visual_theme(preset: str) -> dict[str, str]:
    return deepcopy(_VISUAL_THEME_PRESETS[preset])


def presentation_theme(preset: str) -> dict[str, str]:
    theme = visual_theme(preset)
    return {
        "preset": theme["preset"],
        "font_family": theme["font_family"],
        "background": theme["background"],
        "accent": theme["accent"],
    }


def corridor_theme_tokens(preset: str) -> dict[str, str]:
    theme = visual_theme(preset)
    return {
        "preset": theme["preset"],
        "display_font": theme["display_font"],
        "body_font": theme["body_font"],
        "accent": theme["accent"],
        "background": theme["background"],
        "ink": theme["ink"],
        "muted": theme["muted"],
    }


def narrative_pattern_for_archetype(archetype: str) -> str:
    if archetype in {"decision_recommendation", "executive_status_update"}:
        return "answer_first"
    if archetype in {"portfolio_review", "roadmap_dependency_review"}:
        return "option_comparison"
    return "scq"


def composition_type_for_intent(intent: str) -> str:
    return {
        "cover": "hero_statement",
        "summary": "summary_cards",
        "status": "metric_strip",
        "timeline": "timeline_with_dependencies",
        "risks": "risk_matrix",
        "decision": "decision_frame",
        "portfolio": "comparison_table",
        "closing": "appendix_evidence",
    }.get(intent, "summary_cards")


def density_mode_for_preference(density_preference: str) -> str:
    return {
        "light": "airy",
        "balanced": "balanced",
        "dense": "dense",
        "airy": "airy",
    }[density_preference]


def map_layout_variant_for_composition(composition_type: str) -> str:
    return "matrix_map" if composition_type in MATRIX_MAP_COMPOSITIONS else "map_canvas"


def layout_variant_for_composition(composition_type: str, presentation_mode: str) -> str:
    if composition_type == "hero_statement":
        return "hero_with_recommendation_strip"
    if composition_type == "risk_matrix":
        return "matrix_with_mitigation_panel"
    if composition_type == "timeline_with_dependencies":
        return "horizontal_timeline" if presentation_mode == "live" else "annotated_timeline"
    if composition_type == "decision_frame":
        return "recommendation_with_options"
    if composition_type in {"comparison_table", "evidence_grid"}:
        return "two_column_cards"
    if composition_type in MAP_COMPOSITIONS:
        return map_layout_variant_for_composition(composition_type)
    return "standard_story_panel"


def fallback_layout_for_composition(composition_type: str) -> str:
    if composition_type in {"comparison_table", "evidence_grid"}:
        return "stacked_panels"
    if composition_type in MAP_COMPOSITIONS:
        return map_layout_variant_for_composition(composition_type)
    return "standard"


def html_target_profile_for_format(presentation_format: str, composition_type: str) -> str:
    if presentation_format == "html" and composition_type in HTML_RICH_COMPOSITIONS:
        return "html_rich"
    return "dual_target"


def ppt_target_profile_for_format(
    presentation_format: str,
    composition_type: str,
    html_target_profile: str,
) -> str:
    if presentation_format == "html" and html_target_profile == "html_rich":
        return "ppt_safe"
    return "dual_target"


def output_targets_for_deck(presentation_format: str) -> list[str]:
    return ["html"] if presentation_format == "html" else ["html", "pptx"]


def fidelity_mode_for_deck(presentation_format: str) -> str:
    return "html_first" if presentation_format == "html" else "dual_target"


def presentation_mode_for_map_rendering_mode(rendering_mode: str) -> str:
    return {
        "slide": "async",
        "memo": "memo",
        "dashboard": "async",
        "workshop_board": "meeting_brief",
    }[rendering_mode]


def density_preference_for_map_rendering_mode(rendering_mode: str) -> str:
    return "dense" if rendering_mode == "dashboard" else "balanced"


def presentation_format_for_map_rendering_mode(rendering_mode: str) -> str:
    return "both" if rendering_mode in {"slide", "workshop_board"} else "html"


def output_targets_for_map(rendering_mode: str) -> list[str]:
    return output_targets_for_deck(presentation_format_for_map_rendering_mode(rendering_mode))


def fidelity_mode_for_map(rendering_mode: str) -> str:
    return fidelity_mode_for_deck(presentation_format_for_map_rendering_mode(rendering_mode))


def corridor_theme_preset_for_publication(publication_mode: str) -> str:
    return "corridor_public" if publication_mode == "publishable_external" else "corridor_browse"


def corridor_reading_paths() -> dict[str, list[str]]:
    return deepcopy(_CORRIDOR_READING_PATHS)


def deck_composition_strategy(presentation_brief: dict[str, str]) -> dict[str, str]:
    return {
        "primary_pattern": narrative_pattern_for_archetype(presentation_brief["presentation_archetype"]),
        "reading_path": "headline_to_evidence_to_risk",
        "motion_level": "restrained",
        "composition_family": "executive_deck",
    }


def corridor_composition_strategy() -> dict[str, str]:
    return {
        "primary_pattern": "workflow_narrative",
        "reading_path": "stage_to_handoff_to_proof",
        "motion_level": "minimal",
        "composition_family": "configurable_workflow_corridor",
    }


def map_composition_strategy(visual_map_spec: dict[str, str]) -> dict[str, str]:
    return {
        "primary_pattern": "decision_map",
        "reading_path": "primary_message_to_map_to_evidence",
        "motion_level": "minimal" if visual_map_spec["rendering_mode"] == "memo" else "restrained",
        "composition_family": visual_map_spec["map_type"],
    }
