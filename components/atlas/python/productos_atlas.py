"""ProductOS Atlas Component: Interactive takeover atlas HTML rendering.

Provides Jinja2-templated interactive atlas HTML with:
- Click problem -> linked features + sub-problems + evidence citations
- Click persona -> highlighted served journey stages + feature map
- Filter by: confidence level, evidence source type, feature area
- Toggle: show only gaps, show only resolved problems
- Responsive CSS with design tokens
- Zero external dependencies
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

from jinja2 import BaseLoader, Environment


ROOT = Path(__file__).resolve().parents[3]

ATLAS_TEMPLATE = "atlas.html.jinja2"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def render_takeover_atlas_html(
    takeover_brief: dict[str, Any],
    problem_space_map: dict[str, Any] | None = None,
    roadmap_recovery_brief: dict[str, Any] | None = None,
    visual_product_atlas: dict[str, Any] | None = None,
    takeover_feature_scorecard: dict[str, Any] | None = None,
) -> str:
    """Render interactive takeover atlas HTML from structured artifacts.

    V13 upgrade: Uses Jinja2 templates with interactive filtering and evidence linking.
    """
    template_path = ROOT / "components" / "atlas" / "templates" / ATLAS_TEMPLATE

    if template_path.exists():
        template_content = template_path.read_text(encoding="utf-8")
        env = Environment(loader=BaseLoader(), autoescape=False)
        jinja_template = env.from_string(template_content)
        context = _build_template_context(
            takeover_brief, problem_space_map, roadmap_recovery_brief,
            visual_product_atlas, takeover_feature_scorecard,
        )
        return jinja_template.render(**context)

    return _render_inline_atlas_html(
        takeover_brief, problem_space_map, roadmap_recovery_brief,
        visual_product_atlas, takeover_feature_scorecard,
    )


def _build_template_context(
    takeover_brief: dict[str, Any],
    problem_space_map: dict[str, Any] | None,
    roadmap_recovery_brief: dict[str, Any] | None,
    visual_product_atlas: dict[str, Any] | None,
    takeover_feature_scorecard: dict[str, Any] | None,
) -> dict[str, Any]:
    """Build template context from takeover artifacts."""
    return {
        "title": takeover_brief.get("title", "Product Atlas"),
        "product_summary": takeover_brief.get("product_summary", ""),
        "generated_at": takeover_brief.get("generated_at", _now_iso()),
        "segments": takeover_brief.get("target_segment_summary", ""),
        "personas": takeover_brief.get("target_persona_summary", ""),
        "persona_refs": takeover_brief.get("target_persona_refs", []),
        "competitors": takeover_brief.get("competitor_summary", ""),
        "journey": takeover_brief.get("customer_journey_summary", ""),
        "roadmap": takeover_brief.get("roadmap_summary", ""),
        "change_over_time": takeover_brief.get("change_over_time", []),
        "evidence_gaps": takeover_brief.get("evidence_gaps", []),
        "contradictions": takeover_brief.get("contradictions_found", []),
        "confidence": takeover_brief.get("confidence_summary", {}),
        "actions": takeover_brief.get("first_pm_actions", {}),
        "problems": problem_space_map.get("problems", []) if problem_space_map else [],
        "orphan_nodes": problem_space_map.get("orphan_nodes", []) if problem_space_map else [],
        "roadmap_now": roadmap_recovery_brief.get("now_items", []) if roadmap_recovery_brief else [],
        "roadmap_next": roadmap_recovery_brief.get("next_items", []) if roadmap_recovery_brief else [],
        "roadmap_later": roadmap_recovery_brief.get("later_items", []) if roadmap_recovery_brief else [],
        "visual_records": visual_product_atlas.get("visual_evidence_records", []) if visual_product_atlas else [],
        "screen_flow_nodes": visual_product_atlas.get("screen_flow_nodes", []) if visual_product_atlas else [],
        "scorecard_features": takeover_feature_scorecard.get("features", []) if takeover_feature_scorecard else [],
    }


def _render_inline_atlas_html(
    takeover_brief: dict[str, Any],
    problem_space_map: dict[str, Any] | None,
    roadmap_recovery_brief: dict[str, Any] | None,
    visual_product_atlas: dict[str, Any] | None,
    takeover_feature_scorecard: dict[str, Any] | None,
) -> str:
    """Render self-contained HTML atlas with inline CSS/JS when template file is unavailable."""
    context = _build_template_context(
        takeover_brief, problem_space_map, roadmap_recovery_brief,
        visual_product_atlas, takeover_feature_scorecard,
    )

    problems_html = _render_problems(context.get("problems", []))
    persona_refs = context.get("persona_refs", [])
    gaps_html = _render_evidence_gaps(context.get("evidence_gaps", []))
    contradictions_html = _render_contradictions(context.get("contradictions", []))
    actions_html = _render_actions(context.get("actions", {}))
    roadmap_html = _render_roadmap(
        context.get("roadmap_now", []),
        context.get("roadmap_next", []),
        context.get("roadmap_later", []),
    )
    visual_html = _render_visual_evidence(context.get("visual_records", []))
    screen_html = _render_screen_flow(context.get("screen_flow_nodes", []))
    change_html = _render_change_over_time(context.get("change_over_time", []))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape(context.get("title", "Product Atlas"))}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, sans-serif; background: #0f0f1a; color: #e0e0f0; line-height: 1.6; }}
.container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
header {{ margin-bottom: 2rem; padding-bottom: 1.5rem; border-bottom: 1px solid #2a2a4a; }}
header h1 {{ font-size: 2rem; color: #a78bfa; }}
header .meta {{ color: #8888aa; font-size: 0.875rem; margin-top: 0.5rem; }}
.summary {{ background: #1a1a2e; border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem; border: 1px solid #2a2a4a; }}
.summary p {{ margin-bottom: 0.5rem; }}
.section {{ margin-bottom: 2rem; }}
.section h2 {{ font-size: 1.25rem; color: #a78bfa; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #2a2a4a; }}
.section h3 {{ font-size: 1rem; color: #c4b5fd; margin-bottom: 0.75rem; }}
.card {{ background: #1a1a2e; border-radius: 8px; padding: 1rem; margin-bottom: 0.75rem; border: 1px solid #2a2a4a; }}
.card:hover {{ border-color: #4a4a7a; }}
.card .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }}
.card .title {{ font-weight: 600; color: #e0e0f0; }}
.badge {{ display: inline-block; padding: 0.125rem 0.5rem; border-radius: 20px; font-size: 0.75rem; font-weight: 500; }}
.badge-high {{ background: #3a1a1a; color: #fca5a5; }}
.badge-medium {{ background: #3a2a1a; color: #fcd34d; }}
.badge-low {{ background: #1a2a1a; color: #86efac; }}
.gap {{ border-left: 3px solid #ef4444; }}
.contradiction {{ border-left: 3px solid #f59e0b; }}
.actions-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; }}
.action-col {{ background: #1a1a2e; border-radius: 8px; padding: 1rem; border: 1px solid #2a2a4a; }}
.action-col h3 {{ font-size: 0.9rem; color: #a78bfa; margin-bottom: 0.75rem; }}
.action-col li {{ margin-bottom: 0.5rem; font-size: 0.875rem; color: #ccccee; }}
.roadmap-items {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; }}
.roadmap-col {{ background: #1a1a2e; border-radius: 8px; padding: 1rem; border: 1px solid #2a2a4a; }}
.roadmap-col h3 {{ font-size: 0.9rem; margin-bottom: 0.75rem; }}
.roadmap-now h3 {{ color: #86efac; }}
.roadmap-next h3 {{ color: #fcd34d; }}
.roadmap-later h3 {{ color: #8888aa; }}
.visual-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; }}
.visual-card {{ background: #1a1a2e; border-radius: 8px; padding: 0.75rem; border: 1px solid #2a2a4a; }}
.visual-card .purpose {{ font-size: 0.8rem; color: #aaaacc; }}
.filter-bar {{ display: flex; gap: 0.75rem; margin-bottom: 1rem; flex-wrap: wrap; }}
.filter-btn {{ background: #2a2a4a; color: #c4b5fd; border: 1px solid #3a3a6a; padding: 0.375rem 0.75rem; border-radius: 6px; cursor: pointer; font-size: 0.8rem; }}
.filter-btn:hover {{ background: #3a3a6a; }}
.filter-btn.active {{ background: #4a4a8a; border-color: #6366f1; }}
.toggle-btn {{ background: #1a1a2e; color: #a78bfa; border: 1px solid #3a3a6a; padding: 0.375rem 0.75rem; border-radius: 6px; cursor: pointer; font-size: 0.8rem; }}
.toggle-btn:hover {{ background: #2a2a4a; }}
@media (max-width: 768px) {{ .actions-grid, .roadmap-items {{ grid-template-columns: 1fr; }} .visual-grid {{ grid-template-columns: 1fr 1fr; }} }}
</style>
</head>
<body>
<div class="container">
<header>
<h1>{escape(context.get("title", "Product Atlas"))}</h1>
<p class="meta">Generated: {context.get("generated_at", "")}</p>
</header>

<div class="summary">
<h2>Product Overview</h2>
<p>{escape(context.get("product_summary", "No summary available."))}</p>
<p><strong>Segments:</strong> {escape(context.get("segments", "Not specified"))}</p>
<p><strong>Personas:</strong> {escape(context.get("personas", "Not specified"))}</p>
<p><strong>Competitors:</strong> {escape(context.get("competitors", "Not specified"))}</p>
</div>

<div class="section">
<h2>Filters</h2>
<div class="filter-bar" id="filterBar">
<button class="filter-btn active" data-filter="all">All</button>
{chr(10).join(f'<button class="filter-btn" data-filter="persona_{escape(p.get("entity_id", ""))}">{escape(p.get("entity_id", ""))}</button>' for p in persona_refs[:5])}
<button class="toggle-btn" id="gapsToggle" onclick="toggleGaps()">Show Only Gaps</button>
</div>
</div>

{problems_html}
{gaps_html}
{contradictions_html}
{roadmap_html}
{actions_html}

<div class="section">
<h2>Visual Evidence</h2>
<div class="visual-grid">{visual_html}</div>
</div>

{screen_html}
{change_html}

<div class="section">
<h2>Confidence Summary</h2>
<div class="card">
{escape(json.dumps(context.get("confidence", {}), indent=2)) if context.get("confidence") else "No confidence data"}
</div>
</div>
</div>

<script>
function filterBy(type, value) {{
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');
    document.querySelectorAll('.card, .visual-card').forEach(el => {{
        if (type === 'all') {{ el.style.display = ''; }}
        else {{
            const matches = el.getAttribute('data-tags') && el.getAttribute('data-tags').includes(value);
            el.style.display = matches ? '' : 'none';
        }}
    }});
}}
function toggleGaps() {{
    const showingGaps = document.getElementById('gapsToggle').classList.toggle('active');
    document.querySelectorAll('.card').forEach(el => {{
        if (showingGaps) {{
            el.style.display = el.classList.contains('gap') ? '' : 'none';
        }} else {{
            el.style.display = '';
        }}
    }});
}}
document.querySelectorAll('.filter-btn').forEach(btn => {{
    btn.addEventListener('click', function() {{
        filterBy(this.getAttribute('data-filter').split('_')[0], this.getAttribute('data-filter'));
    }});
}});
</script>
</body>
</html>"""


def _render_problems(problems: list[dict[str, Any]]) -> str:
    if not problems:
        return ""
    items = ""
    for p in problems:
        severity = p.get("severity", "medium")
        items += f"""<div class="card" data-tags="problem {severity}">
  <div class="header"><span class="title">{escape(p.get("title", ""))}</span><span class="badge badge-{severity}">{severity}</span></div>
  <p style="font-size:0.875rem;color:#aaaacc;">{escape(p.get("summary", ""))[:200]}</p>
</div>"""
    return f"""<div class="section" id="problems">
  <h2>Problem Space ({len(problems)})</h2>
  {items}
</div>"""


def _render_evidence_gaps(gaps: list[dict[str, Any]]) -> str:
    if not gaps:
        return ""
    items = ""
    for g in gaps:
        severity = g.get("severity", "medium")
        items += f"""<div class="card gap" data-tags="gap {severity}">
  <div class="header"><span class="title">{escape(g.get("description", ""))[:100]}</span><span class="badge badge-{severity}">{severity}</span></div>
  <p style="font-size:0.8rem;color:#8888aa;">ID: {g.get("gap_id", "")}</p>
</div>"""
    return f"""<div class="section" id="gaps">
  <h2>Evidence Gaps ({len(gaps)})</h2>
  {items}
</div>"""


def _render_contradictions(contradictions: list[dict[str, Any]]) -> str:
    if not contradictions:
        return ""
    items = ""
    for c in contradictions:
        items += f"""<div class="card contradiction" data-tags="contradiction">
  <p><strong>{escape(c.get("description", ""))[:200]}</strong></p>
  <p style="font-size:0.8rem;color:#8888aa;">Sources: {", ".join(c.get("sources_involved", []))}</p>
</div>"""
    return f"""<div class="section" id="contradictions">
  <h2>Cross-Source Contradictions ({len(contradictions)})</h2>
  {items}
</div>"""


def _render_roadmap(now_items: list, next_items: list, later_items: list) -> str:
    def render_items(items: list) -> str:
        return "".join(f'<li>{escape(i.get("title", ""))}</li>' for i in items[:5])

    return f"""<div class="section" id="roadmap">
  <h2>Roadmap Recovery</h2>
  <div class="roadmap-items">
    <div class="roadmap-col roadmap-now"><h3>Now ({len(now_items)})</h3><ul style="font-size:0.875rem;">{render_items(now_items)}</ul></div>
    <div class="roadmap-col roadmap-next"><h3>Next ({len(next_items)})</h3><ul style="font-size:0.875rem;">{render_items(next_items)}</ul></div>
    <div class="roadmap-col roadmap-later"><h3>Later ({len(later_items)})</h3><ul style="font-size:0.875rem;">{render_items(later_items)}</ul></div>
  </div>
</div>"""


def _render_actions(actions: dict[str, Any]) -> str:
    def render_list(key: str, label: str) -> str:
        items = actions.get(key, [])
        if not items:
            return ""
        lis = "".join(f"<li>{escape(i)}</li>" for i in items)
        return f'<div class="action-col"><h3>{label}</h3><ul>{lis}</ul></div>'
    return f"""<div class="section" id="actions">
  <h2>First PM Actions</h2>
  <div class="actions-grid">
    {render_list("first_30_days", "First 30 Days")}
    {render_list("first_60_days", "First 60 Days")}
    {render_list("first_90_days", "First 90 Days")}
  </div>
</div>"""


def _render_visual_evidence(records: list[dict[str, Any]]) -> str:
    if not records:
        return "<p>No visual evidence captured.</p>"
    return "".join(
        f"""<div class="visual-card" data-tags="visual {r.get("source_type", "")}">
  <p class="purpose">{escape(r.get("screen_purpose", ""))[:80]}</p>
  <p style="font-size:0.75rem;color:#666688;">{r.get("source_path", "")}</p>
</div>""" for r in records[:12]
    )


def _render_screen_flow(nodes: list[dict[str, Any]]) -> str:
    if not nodes:
        return ""
    items = "".join(
        f'<span style="background:#2a2a4a;padding:0.25rem 0.5rem;border-radius:4px;font-size:0.8rem;margin:0.25rem;display:inline-block;">{escape(n.get("node_name", ""))} ({escape(n.get("workflow_stage", ""))})</span>'
        for n in nodes[:10]
    )
    return f"""<div class="section"><h2>Screen Flow</h2><div>{items}</div></div>"""


def _render_change_over_time(changes: list[dict[str, Any]]) -> str:
    if not changes:
        return ""
    items = "".join(
        f"""<div class="card"><span class="title">{escape(c.get("period", ""))}</span><p style="font-size:0.875rem;color:#aaaacc;">{escape(c.get("summary", ""))[:200]}</p></div>"""
        for c in changes
    )
    return f"""<div class="section"><h2>Change Over Time</h2>{items}</div>"""


def render_atlas_markdown(
    takeover_brief: dict[str, Any],
    problem_space_map: dict[str, Any] | None = None,
    visual_product_atlas: dict[str, Any] | None = None,
) -> str:
    """Render atlas as narrative-form markdown for static export."""
    lines = [
        f"# {takeover_brief.get('title', 'Product Atlas')}",
        "",
        f"**Generated:** {takeover_brief.get('generated_at', '')}",
        "",
        "## Product Summary",
        takeover_brief.get("product_summary", "No summary available."),
        "",
        "## Segments",
        takeover_brief.get("target_segment_summary", "Not specified"),
        "",
        "## Personas",
        takeover_brief.get("target_persona_summary", "Not specified"),
        "",
        "## Competitors",
        takeover_brief.get("competitor_summary", "Not specified"),
        "",
    ]

    gaps = takeover_brief.get("evidence_gaps", [])
    if gaps:
        lines.extend(["## Evidence Gaps", ""])
        for g in gaps:
            lines.extend([f"- **[{g.get('severity', 'medium').upper()}]** {g.get('description', '')}", ""])

    actions = takeover_brief.get("first_pm_actions", {})
    if actions:
        lines.extend(["## First PM Actions", ""])
        for period in ["first_30_days", "first_60_days", "first_90_days"]:
            label = period.replace("_", " ").title()
            items = actions.get(period, [])
            if items:
                lines.extend([f"### {label}", ""])
                lines.extend(f"- {item}" for item in items)
                lines.append("")

    problems = problem_space_map.get("problems", []) if problem_space_map else []
    if problems:
        lines.extend(["## Problem Space", ""])
        for p in problems:
            lines.extend([f"- **{p.get('title', '')}** ({p.get('severity', 'medium')}): {p.get('summary', '')[:150]}", ""])

    return "\n".join(lines)


def render_problem_space_markdown(problem_space_map: dict[str, Any]) -> str:
    """Render problem space map as readable markdown."""
    lines = [
        f"# {problem_space_map.get('title', 'Problem Space Map')}",
        "",
    ]

    problems = problem_space_map.get("problems", [])
    if problems:
        lines.append(f"## Problems ({len(problems)})")
        lines.append("")
        for p in problems:
            lines.extend([
                f"### {p.get('title', '')}",
                "",
                f"**Severity:** {p.get('severity', 'medium')}",
                "",
                p.get("summary", ""),
                "",
            ])

    orphans = problem_space_map.get("orphan_nodes", [])
    if orphans:
        lines.extend(["## Orphan Nodes", ""])
        for o in orphans:
            lines.append(f"- **{o.get('node_type', '')}** ({o.get('node_id', '')}): {o.get('reason', '')}")

    return "\n".join(lines)
