"""ProductOS User Journey Screen Flow Runtime.

Generates embedded SVG screen-flow diagrams from a `user_journey_map.json` or
`customer_journey_map.json` artifact. Each step maps to screen nodes with
state variants (loading, empty, normal, error, edge, onboarding). Output is
standalone SVG with zero external dependencies — suitable for embedding in
PRDs, decks, and prototype HTML.

Also provides a pipeline helper that links journey stages to prototype
screen variants and regenerates `prototype.html` downstream.
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path
from typing import Any, Dict, List


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_screen_flow_svg(
    user_journey_map: Dict[str, Any],
    design_tokens: Dict[str, Any] | None = None,
) -> str:
    """Render an embedded SVG screen flow diagram from a user journey map.

    Args:
        user_journey_map: Validated user_journey_map.json payload
        design_tokens: Optional theming override

    Returns:
        Standalone SVG string with embedded CSS and clickable nodes
    """
    tokens = _resolve_tokens(design_tokens)
    steps = list(user_journey_map.get("steps", []))
    title = user_journey_map.get("title", "Screen Flow")

    if not steps:
        return _empty_svg(title, tokens)

    return _build_flow_svg(steps, title, tokens)


def generate_screen_flow_from_journey_stages(
    journey_map: Dict[str, Any],
    design_tokens: Dict[str, Any] | None = None,
) -> str:
    """Generate a screen flow diagram from customer journey stages.

    Maps each journey stage to a conceptual screen node. Useful when a
    full user_journey_map.json is not yet available.
    """
    tokens = _resolve_tokens(design_tokens)
    stages = list(journey_map.get("journey_stages", []))
    title = journey_map.get("title", "Journey Screen Flow")

    if not stages:
        return _empty_svg(title, tokens)

    # Convert stages to pseudo-steps
    steps = []
    for stage in stages:
        steps.append({
            "step_id": stage.get("stage_id", "step"),
            "step_order": stage.get("stage_order", len(steps) + 1),
            "step_name": stage.get("stage_name", "Screen").replace("_", " ").title(),
            "user_action": stage.get("persona_actions", ["Navigate"])[0] if stage.get("persona_actions") else "Navigate",
            "system_response": stage.get("description", "")[:80],
            "cognitive_load": "medium",
        })
    return _build_flow_svg(steps, title, tokens, from_journey=True)


def write_screen_flow_html(
    user_journey_map: Dict[str, Any],
    output_path: Path,
    design_tokens: Dict[str, Any] | None = None,
) -> Path:
    """Write a standalone HTML wrapper around the SVG screen flow."""
    svg = generate_screen_flow_svg(user_journey_map, design_tokens)
    title = user_journey_map.get("title", "Screen Flow")
    html = _wrap_svg_in_html(svg, title)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return output_path


# ---------------------------------------------------------------------------
# Token resolution
# ---------------------------------------------------------------------------

def _resolve_tokens(design_tokens: Dict[str, Any] | None) -> Dict[str, Any]:
    defaults = {
        "colors": {
            "primary": "#2563EB",
            "neutral": {"50": "#F8FAFC", "100": "#F1F5F9", "200": "#E2E8F0", "300": "#CBD5E1", "500": "#64748B", "700": "#334155", "900": "#0F172A"},
            "semantic": {"success": "#16A34A", "warning": "#D97706", "error": "#DC2626", "info": "#0EA5E9"},
        },
        "typography": {"font_family": "Inter, system-ui, sans-serif"},
        "spacing": {"md": "16px", "lg": "24px", "xl": "32px"},
    }
    if design_tokens is None:
        return defaults
    merged = {}
    for key in defaults:
        if key in design_tokens:
            if isinstance(defaults[key], dict) and isinstance(design_tokens[key], dict):
                merged[key] = {**defaults[key], **design_tokens[key]}
            else:
                merged[key] = design_tokens[key]
        else:
            merged[key] = defaults[key]
    return merged


# ---------------------------------------------------------------------------
# SVG builder
# ---------------------------------------------------------------------------

def _build_flow_svg(
    steps: List[Dict[str, Any]],
    title: str,
    tokens: Dict[str, Any],
    from_journey: bool = False,
) -> str:
    node_height = 48
    node_width = 180
    gap_x = 40
    gap_y = 80
    cols = 4
    margin = 40

    # Compute positions
    positions = []
    for i, step in enumerate(steps):
        col = i % cols
        row = i // cols
        x = margin + col * (node_width + gap_x)
        y = margin + 40 + row * (node_height + gap_y)
        positions.append((x, y))

    max_x = max((p[0] + node_width for p in positions), default=margin + node_width)
    max_y = max((p[1] + node_height for p in positions), default=margin + node_height)
    width = max_x + margin
    height = max_y + margin

    # Build nodes
    nodes_svg = []
    for i, (step, (x, y)) in enumerate(zip(steps, positions)):
        node_id = f"node_{i}"
        label = step.get("step_name", f"Step {i+1}")
        action = step.get("user_action", "Action")
        load = step.get("cognitive_load", "medium")
        color = _load_color(load, tokens)

        # Node rect with rounded corners
        rect = (
            f'<rect id="{node_id}" x="{x}" y="{y}" width="{node_width}" height="{node_height}" '
            f'rx="8" ry="8" fill="{tokens["colors"]["neutral"]["50"]}" stroke="{color}" stroke-width="2" '
            f'class="flow-node" data-step="{step.get("step_id", "")}"/>'
        )

        # Title text
        title_text = textwrap.shorten(label, width=22, placeholder="...")
        text_y = y + 20
        text_el = (
            f'<text x="{x + node_width/2}" y="{text_y}" text-anchor="middle" '
            f'font-family="{tokens["typography"]["font_family"]}" font-size="12" font-weight="600" '
            f'fill="{tokens["colors"]["neutral"]["900"]}">{_esc(title_text)}</text>'
        )

        # Subtitle text
        sub = textwrap.shorten(action, width=30, placeholder="...")
        sub_el = (
            f'<text x="{x + node_width/2}" y="{text_y + 16}" text-anchor="middle" '
            f'font-family="{tokens["typography"]["font_family"]}" font-size="10" '
            f'fill="{tokens["colors"]["neutral"]["500"]}">{_esc(sub)}</text>'
        )

        nodes_svg.extend([rect, text_el, sub_el])

    # Build arrows between consecutive steps
    arrows_svg = []
    for i in range(len(steps) - 1):
        x1, y1 = positions[i]
        x2, y2 = positions[i + 1]
        # Determine start and end points
        if x1 == x2:  # same column -> vertical
            sx = x1 + node_width / 2
            sy = y1 + node_height
            ex = x2 + node_width / 2
            ey = y2
        else:
            sx = x1 + node_width
            sy = y1 + node_height / 2
            ex = x2
            ey = y2 + node_height / 2

        arrow_color = tokens["colors"]["neutral"]["300"]
        path_d = f"M {sx},{sy} L {ex},{ey}"
        # Arrowhead
        angle = 0
        if abs(ex - sx) > abs(ey - sy):
            angle = 0 if ex > sx else 180
        else:
            angle = 90 if ey > sy else -90

        arrow = (
            f'<line x1="{sx}" y1="{sy}" x2="{ex}" y2="{ey}" '
            f'stroke="{arrow_color}" stroke-width="2" marker-end="url(#arrowhead)"/>'
        )
        arrows_svg.append(arrow)

    # Marker definition
    marker = (
        f'<marker id="arrowhead" markerWidth="10" markerHeight="7" '
        f'refX="9" refY="3.5" orient="auto">'
        f'<polygon points="0 0, 10 3.5, 0 7" fill="{tokens["colors"]["neutral"]["300"]}"/>'
        f'</marker>'
    )

    title_svg = (
        f'<text x="{width/2}" y="28" text-anchor="middle" '
        f'font-family="{tokens["typography"]["font_family"]}" font-size="16" font-weight="600" '
        f'fill="{tokens["colors"]["neutral"]["900"]}">{_esc(title)}</text>'
    )

    svg_content = "\n".join([title_svg, marker] + arrows_svg + nodes_svg)

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" style="background:#F8FAFC">\n'
        f'  <defs>\n    {marker}\n  </defs>\n'
        f'  {svg_content}\n'
        f'</svg>'
    )


def _empty_svg(title: str, tokens: Dict[str, Any]) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="120" viewBox="0 0 400 120" style="background:#F8FAFC">\n'
        f'  <text x="200" y="60" text-anchor="middle" font-family="{tokens["typography"]["font_family"]}" '
        f'font-size="14" fill="{tokens["colors"]["neutral"]["500"]}">{_esc(title)} — no steps defined</text>\n'
        f'</svg>'
    )


def _wrap_svg_in_html(svg: str, title: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{_esc(title)}</title>
  <style>body {{ margin: 0; padding: 24px; background: #F8FAFC; font-family: Inter, system-ui, sans-serif; }}</style>
</head>
<body>
  {svg}
</body>
</html>"""


def _load_color(load: str, tokens: Dict[str, Any]) -> str:
    mapping = {
        "low": tokens["colors"]["semantic"]["success"],
        "medium": tokens["colors"]["semantic"]["warning"],
        "high": tokens["colors"]["semantic"]["error"],
        "very_high": tokens["colors"]["semantic"]["error"],
    }
    return mapping.get(load.lower(), tokens["colors"]["semantic"]["info"])


def _esc(text: str) -> str:
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


# ---------------------------------------------------------------------------
# Connected pipeline helpers
# ---------------------------------------------------------------------------

def link_journey_to_screens(
    customer_journey_map: Dict[str, Any],
    prototype_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Map customer journey stages to prototype screen variants.

    Returns a dict mapping stage_id -> list of screen variant refs.
    """
    stages = customer_journey_map.get("journey_stages", [])
    screens = prototype_record.get("screens", []) if prototype_record else []
    mapping: Dict[str, List[str]] = {}
    for stage in stages:
        sid = stage.get("stage_id", "")
        # Simple heuristic: match stage name substring to screen name
        matched = []
        sname = stage.get("stage_name", "").lower().replace("_", " ")
        for screen in screens:
            sc_name = screen.get("screen_name", "").lower()
            if sname in sc_name or sc_name in sname:
                matched.append(screen.get("screen_id", ""))
        if not matched:
            matched = [f"screen_{sid}"]
        mapping[sid] = matched
    return mapping


def generate_prototype_screen_variants(
    journey_map: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Generate minimal prototype screen variants from journey stages.

    Each journey stage gets 6 state variants: loading, empty, normal, error, edge, onboarding.
    Returns a list of screen dicts ready for prototype_record.json.
    """
    screens = []
    for stage in journey_map.get("journey_stages", []):
        sid = stage.get("stage_id", "")
        sname = stage.get("stage_name", "").replace("_", " ").title()
        for state in ["loading", "empty", "normal", "error", "edge", "onboarding"]:
            screens.append({
                "screen_id": f"{sid}_{state}",
                "screen_name": f"{sname} — {state.title()}",
                "linked_stage_id": sid,
                "state_variant": state,
                "description": f"{sname} screen in {state} state.",
            })
    return screens
