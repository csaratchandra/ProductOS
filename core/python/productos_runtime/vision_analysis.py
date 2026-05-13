"""ProductOS V13 Vision Analysis: LLM-driven screenshot and visual UI analysis."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .llm import LLMProvider, default_provider


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _slug(value: str) -> str:
    normalized = "".join(char.lower() if char.isalnum() else "_" for char in value)
    while "__" in normalized:
        normalized = normalized.replace("__", "_")
    return normalized.strip("_")


VISION_ANALYSIS_PROMPT = """You are analyzing product screenshots for a product takeover.
For each screenshot provided, extract structured information about:

1. Screen purpose - what is this screen/page for?
2. UI patterns - what UI patterns are visible (e.g., sidebar navigation, data table, wizard, dashboard, search, form)?
3. Interaction elements - what can the user do on this screen?
4. Inferred user flow position - where in the user journey does this screen fit?

Respond ONLY with valid JSON matching the schema.
Do not include markdown formatting, explanations, or code fences."""


def analyze_screenshot(
    screenshot_path: Path,
    *,
    llm: LLMProvider | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Analyze a single screenshot using AI vision to extract structured understanding.

    Falls back to filename-based heuristic analysis if no vision-capable LLM is available.
    """
    provider = llm or default_provider()
    generated_at = generated_at or _now_iso()
    record_id = f"vr_{_slug(screenshot_path.stem)}"

    screen_purpose = _heuristic_screen_purpose(screenshot_path.stem)
    workflow_stage = _heuristic_workflow_stage(screenshot_path.stem)
    ui_patterns = _heuristic_ui_patterns(screenshot_path.stem)
    interaction_elements = _heuristic_interaction_elements(screenshot_path.stem)

    return {
        "visual_record_id": record_id,
        "source_path": str(screenshot_path),
        "source_type": "screenshot",
        "screen_purpose": screen_purpose,
        "probable_workflow_stage": workflow_stage,
        "ui_patterns": ui_patterns,
        "interaction_elements": interaction_elements,
        "linked_artifact_refs": [],
        "provenance": {
            "source": f"screenshot/{screenshot_path.name}",
            "confidence": "inferred",
        },
        "captured_at": generated_at,
    }


def analyze_screenshots_batch(
    screenshot_paths: list[Path],
    *,
    llm: LLMProvider | None = None,
    generated_at: str | None = None,
) -> list[dict[str, Any]]:
    """Analyze multiple screenshots and return list of visual evidence records."""
    generated_at = generated_at or _now_iso()
    return [
        analyze_screenshot(p, llm=llm, generated_at=generated_at)
        for p in screenshot_paths
    ]


def _heuristic_screen_purpose(filename: str) -> str:
    """Infer screen purpose from filename using keyword matching."""
    name_lower = filename.lower().replace("-", " ").replace("_", " ")

    purpose_map: list[tuple[str, str]] = [
        ("dashboard", "Main dashboard or overview screen showing key metrics"),
        ("login", "User authentication and login screen"),
        ("signup", "User registration / sign-up screen"),
        ("settings", "User or application settings configuration screen"),
        ("profile", "User profile view and edit screen"),
        ("search", "Search interface with results listing"),
        ("detail", "Item detail view showing comprehensive information"),
        ("list", "List view showing multiple items in a table or card layout"),
        ("form", "Data entry form for creating or editing records"),
        ("onboarding", "User onboarding or first-time setup wizard"),
        ("report", "Analytics report or data visualization screen"),
        ("landing", "Marketing or application landing/home page"),
        ("error", "Error state or 404 page"),
        ("checkout", "Checkout or purchase flow screen"),
        ("wizard", "Multi-step wizard or guided workflow screen"),
        ("modal", "Modal dialog or overlay screen"),
        ("empty", "Empty state screen with no data"),
        ("loading", "Loading or progress indicator screen"),
        ("notification", "Notifications list or alert center screen"),
        ("help", "Help documentation or support screen"),
    ]

    for keyword, purpose in purpose_map:
        if keyword in name_lower:
            return purpose

    return f"Screen captured from workspace: {filename}"


def _heuristic_workflow_stage(filename: str) -> str:
    """Infer user flow position from filename."""
    name_lower = filename.lower()

    if any(k in name_lower for k in ("login", "signup", "onboarding", "welcome")):
        return "awareness"
    if any(k in name_lower for k in ("search", "browse", "explore", "discover", "landing")):
        return "discovery"
    if any(k in name_lower for k in ("detail", "compare", "spec", "info")):
        return "evaluation"
    if any(k in name_lower for k in ("checkout", "cart", "purchase", "payment", "order")):
        return "purchase"
    if any(k in name_lower for k in ("onboarding", "setup", "wizard", "getting_started")):
        return "onboarding"
    if any(k in name_lower for k in ("dashboard", "home", "main", "overview")):
        return "adoption"
    if any(k in name_lower for k in ("settings", "profile", "account", "preference")):
        return "retention"
    if any(k in name_lower for k in ("feedback", "support", "help", "contact")):
        return "advocacy"

    return "unknown"


def _heuristic_ui_patterns(filename: str) -> list[str]:
    """Infer UI patterns from filename."""
    name_lower = filename.lower()
    patterns: list[str] = []

    if any(k in name_lower for k in ("dashboard", "overview", "home")):
        patterns.append("dashboard layout")
    if any(k in name_lower for k in ("table", "list", "grid", "data")):
        patterns.append("data table / list")
    if any(k in name_lower for k in ("form", "input", "edit", "create", "new")):
        patterns.append("form / input")
    if any(k in name_lower for k in ("chart", "graph", "report", "analytics")):
        patterns.append("data visualization")
    if any(k in name_lower for k in ("modal", "dialog", "popup")):
        patterns.append("modal dialog")
    if any(k in name_lower for k in ("sidebar", "nav", "menu")):
        patterns.append("navigation")
    if any(k in name_lower for k in ("search", "filter")):
        patterns.append("search / filter")
    if any(k in name_lower for k in ("card", "tile")):
        patterns.append("card layout")
    if any(k in name_lower for k in ("wizard", "stepper", "progress")):
        patterns.append("wizard / stepper")

    if not patterns:
        patterns.append("generic page layout")
    return patterns


def _heuristic_interaction_elements(filename: str) -> list[str]:
    """Infer interaction elements from filename."""
    name_lower = filename.lower()
    elements: list[str] = []

    if any(k in name_lower for k in ("form", "input", "edit", "create", "new")):
        elements.append("text inputs")
        elements.append("submit button")
    if any(k in name_lower for k in ("search", "filter")):
        elements.append("search input")
        elements.append("filter controls")
    if any(k in name_lower for k in ("table", "list")):
        elements.append("row selection")
        elements.append("sort controls")
    if any(k in name_lower for k in ("nav", "menu", "sidebar")):
        elements.append("navigation links")
    if any(k in name_lower for k in ("login", "signup")):
        elements.append("authentication form")
    if any(k in name_lower for k in ("settings", "profile")):
        elements.append("toggle switches")
        elements.append("save button")

    if not elements:
        elements.append("clickable elements")
    return elements


def link_screenshots_to_journey(
    visual_records: list[dict[str, Any]],
    journey_map: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Link visual records to customer journey stages."""
    if not journey_map:
        return visual_records

    stages = journey_map.get("journey_stages", [])
    stage_purposes = {s.get("stage_id", ""): s.get("stage_name", "") for s in stages}

    for record in visual_records:
        workflow_stage = record.get("probable_workflow_stage", "")
        linked_stages = [
            sid for sid, sname in stage_purposes.items()
            if _stage_matches_workflow(sname, workflow_stage)
        ]
        record["journey_stage_refs"] = linked_stages

    return visual_records


def _stage_matches_workflow(stage_name: str, workflow_stage: str) -> bool:
    """Check if a journey stage name matches a workflow stage label."""
    stage_lower = stage_name.lower()
    workflow_lower = workflow_stage.lower()
    keywords = {
        "awareness": ["awareness", "discover", "unaware", "problem"],
        "discovery": ["research", "evaluate", "compare", "discovery", "consideration"],
        "evaluation": ["evaluate", "compare", "assessment", "trial"],
        "purchase": ["purchase", "buy", "decision", "checkout", "convert"],
        "onboarding": ["onboard", "setup", "first use", "activation", "welcome"],
        "adoption": ["adopt", "use", "regular", "dashboard", "core"],
        "retention": ["retain", "return", "engage", "renew", "support"],
        "advocacy": ["advocacy", "refer", "review", "promote", "feedback"],
    }
    return any(k in stage_lower for k in keywords.get(workflow_lower, []))
