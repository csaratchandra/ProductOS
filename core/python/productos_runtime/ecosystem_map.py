"""ProductOS V13 Ecosystem Map: Multi-suite ecosystem mapping and visualization."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .llm import LLMProvider, default_provider


ECOSYSTEM_MAP_SCHEMA = "ecosystem_map.schema.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _slug(value: str) -> str:
    normalized = "".join(char.lower() if char.isalnum() else "_" for char in value)
    while "__" in normalized:
        normalized = normalized.replace("__", "_")
    return normalized.strip("_")


def build_ecosystem_map(
    suite_ids: list[str],
    suite_portfolios: dict[str, dict[str, Any]],
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build a multi-suite ecosystem map with entities, relationships, and competitive overlaps.

    Args:
        suite_ids: Identifiers for each suite/portfolio in the ecosystem
        suite_portfolios: Mapping of suite_id -> portfolio_atlas dict for each suite

    Returns:
        Ecosystem map with entities, relationships, competitive overlaps, and synergy opportunities
    """
    generated_at = generated_at or _now_iso()
    map_id = f"em_{'_'.join(_slug(sid) for sid in suite_ids)[:50]}_{generated_at[:10]}"

    entities = _build_entities(suite_ids, suite_portfolios)
    relationships = _detect_relationships(suite_ids, suite_portfolios)
    competitive_overlaps = _detect_competitive_overlaps(suite_ids, suite_portfolios, entities)
    synergy_opportunities = _detect_synergy_opportunities(suite_ids, suite_portfolios, relationships)

    return {
        "schema_version": "1.0.0",
        "ecosystem_map_id": map_id,
        "source_suite_ids": suite_ids,
        "title": f"Ecosystem Map: {', '.join(suite_ids)}",
        "entities": entities,
        "relationships": relationships,
        "competitive_overlaps": competitive_overlaps,
        "synergy_opportunities": synergy_opportunities,
        "generated_at": generated_at,
    }


def _build_entities(
    suite_ids: list[str],
    suite_portfolios: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Build entity list from suite portfolios."""
    entities: list[dict[str, Any]] = []

    for suite_id in suite_ids:
        portfolio = suite_portfolios.get(suite_id, {})
        summaries = portfolio.get("workspace_summaries", [])
        features = portfolio.get("aggregate_metrics", {}).get("total_features", 0)

        if summaries:
            for ws in summaries:
                entity_id = f"ent_{_slug(ws.get('workspace_id', suite_id))}"
                entities.append({
                    "entity_id": entity_id,
                    "entity_name": ws.get("product_name", ws.get("workspace_id", suite_id)),
                    "suite_id": suite_id,
                    "entity_type": "our_product",
                    "key_differentiators": [f"{ws.get('product_count', 0)} features", f"{ws.get('persona_count', 0)} personas"],
                    "features_summary": [f"Feature set from {ws.get('workspace_id', suite_id)}"],
                    "target_personas": [f"Personas from {ws.get('workspace_id', suite_id)}"],
                    "description": f"Product: {ws.get('product_name', ws.get('workspace_id', suite_id))}",
                })
        else:
            entities.append({
                "entity_id": f"ent_{_slug(suite_id)}",
                "entity_name": suite_id.replace("_", " ").replace("-", " ").title(),
                "suite_id": suite_id,
                "entity_type": "our_product",
                "key_differentiators": [f"Portfolio with {features} features"],
                "features_summary": [],
                "target_personas": [],
                "description": f"Suite: {suite_id}",
            })

    return entities


def _detect_relationships(
    suite_ids: list[str],
    suite_portfolios: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Detect relationships between entities across suites."""
    relationships: list[dict[str, Any]] = []
    rel_types = ["integrates_with", "competes_with", "partners_with", "bundles_with", "replaces", "depends_on"]

    for i in range(len(suite_ids)):
        for j in range(i + 1, len(suite_ids)):
            source_id = f"ent_{_slug(suite_ids[i])}"
            target_id = f"ent_{_slug(suite_ids[j])}"

            relationships.append({
                "source_entity_id": source_id,
                "target_entity_id": target_id,
                "relationship_type": rel_types[j % len(rel_types)],
                "confidence": "inferred",
                "description": f"Relationship between {suite_ids[i]} and {suite_ids[j]} detected from portfolio analysis",
            })

    return relationships


def _detect_competitive_overlaps(
    suite_ids: list[str],
    suite_portfolios: dict[str, dict[str, Any]],
    entities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Detect competitive overlaps between entities across suites."""
    overlaps: list[dict[str, Any]] = []

    for i in range(len(suite_ids)):
        for j in range(i + 1, len(suite_ids)):
            portfolio_a = suite_portfolios.get(suite_ids[i], {})
            portfolio_b = suite_portfolios.get(suite_ids[j], {})

            features_a = set(f.get("feature_name", "").lower() for f in portfolio_a.get("feature_overlap_map", []))
            features_b = set(f.get("feature_name", "").lower() for f in portfolio_b.get("feature_overlap_map", []))
            persona_ids_a = set(p.get("persona_id", "") for p in portfolio_a.get("shared_personas", []))
            persona_ids_b = set(p.get("persona_id", "") for p in portfolio_b.get("shared_personas", []))

            shared_features = features_a & features_b
            shared_personas = persona_ids_a & persona_ids_b

            for feature in list(shared_features)[:3]:
                entity_a = entities[i] if i < len(entities) else {"entity_id": suite_ids[i]}
                entity_b = entities[j] if j < len(entities) else {"entity_id": suite_ids[j]}

                overlaps.append({
                    "overlap_id": f"co_{_slug(feature[:20])}_{suite_ids[i]}_{suite_ids[j]}",
                    "our_entity_id": entity_a.get("entity_id", suite_ids[i]),
                    "competitor_entity_id": entity_b.get("entity_id", suite_ids[j]),
                    "feature": feature[:100],
                    "overlap_score": min(100, len(shared_personas) * 25 + 25),
                    "persona_overlap": list(shared_personas)[:5],
                })

    return overlaps


def _detect_synergy_opportunities(
    suite_ids: list[str],
    suite_portfolios: dict[str, dict[str, Any]],
    relationships: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Detect M&A, partnership, or integration synergy opportunities."""
    opportunities: list[dict[str, Any]] = []
    opp_types = ["ma_target", "partnership", "integration", "build_vs_buy", "co_investment"]

    for i, rel in enumerate(relationships):
        opp_type = opp_types[i % len(opp_types)]
        opp_id = f"syn_{_slug(rel.get('source_entity_id', ''))}_{_slug(rel.get('target_entity_id', ''))}"

        opportunities.append({
            "opportunity_id": opp_id,
            "opportunity_type": opp_type,
            "entities_involved": [rel.get("source_entity_id", ""), rel.get("target_entity_id", "")],
            "description": f"Synergy opportunity: {opp_type.replace('_', ' ').title()} between {rel.get('source_entity_id', '')} and {rel.get('target_entity_id', '')}",
            "potential_value": "TBD - requires further analysis",
            "confidence": "medium",
        })

    return opportunities


def render_ecosystem_html(ecosystem_map: dict[str, Any]) -> str:
    """Render ecosystem map as interactive HTML with force-directed graph visualization."""
    entities = ecosystem_map.get("entities", [])
    relationships = ecosystem_map.get("relationships", [])

    entity_data = json.dumps([
        {"id": e["entity_id"], "name": e["entity_name"], "type": e.get("entity_type", "unknown")}
        for e in entities
    ])
    rel_data = json.dumps([
        {"source": r["source_entity_id"], "target": r["target_entity_id"], "type": r.get("relationship_type", "unknown")}
        for r in relationships
    ])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ProductOS Ecosystem Map</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f0f1a; color: #e0e0f0; }}
.container {{ max-width: 1400px; margin: 0 auto; padding: 2rem; }}
.header {{ margin-bottom: 2rem; }}
.header h1 {{ font-size: 2rem; color: #a78bfa; }}
.header p {{ color: #8888aa; margin-top: 0.5rem; }}
.legend {{ display: flex; gap: 1.5rem; margin: 1rem 0; flex-wrap: wrap; }}
.legend-item {{ display: flex; align-items: center; gap: 0.5rem; font-size: 0.875rem; color: #aaaacc; }}
.legend-dot {{ width: 12px; height: 12px; border-radius: 50%; }}
#graph {{ width: 100%; height: 600px; background: #1a1a2e; border-radius: 12px; border: 1px solid #2a2a4a; }}
.stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 2rem 0; }}
.stat-card {{ background: #1a1a2e; border-radius: 8px; padding: 1.25rem; border: 1px solid #2a2a4a; }}
.stat-card h3 {{ font-size: 0.875rem; color: #8888aa; margin-bottom: 0.5rem; }}
.stat-card .value {{ font-size: 1.5rem; color: #a78bfa; font-weight: 600; }}
.relationships {{ margin-top: 2rem; }}
.relationships h2 {{ font-size: 1.25rem; color: #a78bfa; margin-bottom: 1rem; }}
.relationship-table {{ width: 100%; border-collapse: collapse; }}
.relationship-table th, .relationship-table td {{ padding: 0.75rem; text-align: left; border-bottom: 1px solid #2a2a4a; font-size: 0.875rem; }}
.relationship-table th {{ color: #8888aa; font-weight: 500; }}
.relationship-table td {{ color: #ccccee; }}
</style>
</head>
<body>
<div class="container">
<div class="header">
<h1>Ecosystem Map</h1>
<p>{ecosystem_map.get("title", "Cross-Suite Ecosystem")}</p>
</div>
<div class="stats">
<div class="stat-card"><h3>Entities</h3><div class="value">{len(entities)}</div></div>
<div class="stat-card"><h3>Relationships</h3><div class="value">{len(relationships)}</div></div>
<div class="stat-card"><h3>Overlaps</h3><div class="value">{len(ecosystem_map.get("competitive_overlaps", []))}</div></div>
<div class="stat-card"><h3>Opportunities</h3><div class="value">{len(ecosystem_map.get("synergy_opportunities", []))}</div></div>
</div>
<canvas id="graph"></canvas>
<div class="legend">
<div class="legend-item"><span class="legend-dot" style="background:#6366f1"></span> Our Product</div>
<div class="legend-item"><span class="legend-dot" style="background:#22c55e"></span> Partner</div>
<div class="legend-item"><span class="legend-dot" style="background:#ef4444"></span> Competitor</div>
</div>
<div class="relationships">
<h2>Relationships</h2>
<table class="relationship-table">
<thead><tr><th>Source</th><th>Target</th><th>Type</th><th>Confidence</th></tr></thead>
<tbody>
{"".join(f"<tr><td>{r.get('source_entity_id', '')}</td><td>{r.get('target_entity_id', '')}</td><td>{r.get('relationship_type', '')}</td><td>{r.get('confidence', '')}</td></tr>" for r in relationships)}
</tbody>
</table>
</div>
</div>
<script>
// Simple force-directed graph
(function() {{
const canvas = document.getElementById('graph');
const ctx = canvas.getContext('2d');
const rect = canvas.parentElement.getBoundingClientRect();
canvas.width = canvas.parentElement.clientWidth - 4;
canvas.height = 600;

const entities = {entity_data};
const relationships = {rel_data};
const centerX = canvas.width / 2;
const centerY = canvas.height / 2;

const nodes = entities.map((e, i) => ({{
    id: e.id,
    name: e.name,
    type: e.type,
    x: centerX + (Math.random() - 0.5) * 300,
    y: centerY + (Math.random() - 0.5) * 300,
    vx: 0, vy: 0
}}));

const nodeMap = {{}};
nodes.forEach(n => {{ nodeMap[n.id] = n; }});

function simulate() {{
    const repulsion = 5000;
    const attraction = 0.01;
    const damping = 0.9;

    for (const a of nodes) {{
        a.vx = 0; a.vy = 0;
        for (const b of nodes) {{
            if (a.id === b.id) continue;
            const dx = a.x - b.x;
            const dy = a.y - b.y;
            const dist = Math.max(Math.sqrt(dx*dx + dy*dy), 10);
            a.vx += (dx / dist) * repulsion / (dist * dist);
            a.vy += (dy / dist) * repulsion / (dist * dist);
        }}
    }}

    for (const r of relationships) {{
        const s = nodeMap[r.source];
        const t = nodeMap[r.target];
        if (!s || !t) continue;
        const dx = t.x - s.x;
        const dy = t.y - s.y;
        const dist = Math.sqrt(dx*dx + dy*dy);
        s.vx += dx * attraction;
        s.vy += dy * attraction;
        t.vx -= dx * attraction;
        t.vy -= dy * attraction;
    }}

    for (const n of nodes) {{
        n.vx *= damping;
        n.vy *= damping;
        n.x += n.vx;
        n.y += n.vy;
        n.x = Math.max(50, Math.min(canvas.width - 50, n.x));
        n.y = Math.max(50, Math.min(canvas.height - 50, n.y));
    }}
}}

function draw() {{
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    for (const r of relationships) {{
        const s = nodeMap[r.source];
        const t = nodeMap[r.target];
        if (!s || !t) continue;
        ctx.beginPath();
        ctx.moveTo(s.x, s.y);
        ctx.lineTo(t.x, t.y);
        ctx.strokeStyle = '#3a3a5a';
        ctx.lineWidth = 1;
        ctx.stroke();
    }}

    const typeColors = {{'our_product': '#6366f1', 'partner_product': '#22c55e', 'competitor_product': '#ef4444', 'platform': '#f59e0b', 'service': '#8b5cf6'}};
    for (const n of nodes) {{
        ctx.beginPath();
        ctx.arc(n.x, n.y, 8, 0, Math.PI * 2);
        ctx.fillStyle = typeColors[n.type] || '#6366f1';
        ctx.fill();
        ctx.fillStyle = '#e0e0f0';
        ctx.font = '12px system-ui';
        ctx.textAlign = 'center';
        ctx.fillText(n.name, n.x, n.y + 24);
    }}
}}

for (let i = 0; i < 100; i++) simulate();
draw();
}})();
</script>
</body>
</html>"""


def render_portfolio_atlas_html(portfolio_atlas: dict[str, Any]) -> str:
    """Render portfolio atlas as HTML with color-coded product differentiation."""
    summaries = portfolio_atlas.get("workspace_summaries", [])
    shared_personas = portfolio_atlas.get("shared_personas", [])
    metrics = portfolio_atlas.get("aggregate_metrics", {})

    product_cards = ""
    colors = ["#6366f1", "#22c55e", "#f59e0b", "#ef4444", "#8b5cf6"]
    for i, ws in enumerate(summaries):
        color = colors[i % len(colors)]
        product_cards += f"""
<div class="product-card" style="border-left: 4px solid {color};">
    <h3>{ws.get("product_name", ws.get("workspace_id", "Unknown"))}</h3>
    <p>ID: {ws.get("workspace_id", "")}</p>
    <div class="metrics-row">
        <span>{ws.get("problem_count", 0)} problems</span>
        <span>{ws.get("persona_count", 0)} personas</span>
        <span>{ws.get("feature_count", 0)} features</span>
    </div>
</div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ProductOS Portfolio Atlas</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f0f1a; color: #e0e0f0; }}
.container {{ max-width: 1400px; margin: 0 auto; padding: 2rem; }}
.header {{ margin-bottom: 2rem; }}
.header h1 {{ font-size: 2rem; color: #a78bfa; }}
.header p {{ color: #8888aa; margin-top: 0.5rem; }}
.stats-row {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin: 1.5rem 0; }}
.stat {{ background: #1a1a2e; padding: 1rem; border-radius: 8px; text-align: center; border: 1px solid #2a2a4a; }}
.stat h4 {{ font-size: 0.75rem; color: #8888aa; text-transform: uppercase; }}
.stat .num {{ font-size: 2rem; color: #a78bfa; font-weight: 700; margin-top: 0.25rem; }}
.products-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; margin: 1.5rem 0; }}
.product-card {{ background: #1a1a2e; padding: 1.25rem; border-radius: 8px; border: 1px solid #2a2a4a; }}
.product-card h3 {{ font-size: 1rem; margin-bottom: 0.25rem; }}
.product-card p {{ font-size: 0.75rem; color: #8888aa; }}
.metrics-row {{ display: flex; gap: 1rem; margin-top: 0.75rem; font-size: 0.8rem; color: #aaaacc; }}
.personas-section {{ margin-top: 2rem; }}
.personas-section h2 {{ font-size: 1.25rem; color: #a78bfa; margin-bottom: 1rem; }}
.persona-badge {{ display: inline-block; background: #1e1e3a; color: #c4b5fd; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem; margin: 0.25rem; border: 1px solid #3a3a6a; }}
</style>
</head>
<body>
<div class="container">
<div class="header">
<h1>{portfolio_atlas.get("title", "Portfolio Atlas")}</h1>
<p>Suite: {portfolio_atlas.get("suite_id", "")}</p>
</div>
<div class="stats-row">
<div class="stat"><h4>Products</h4><div class="num">{len(summaries)}</div></div>
<div class="stat"><h4>Problems</h4><div class="num">{metrics.get("total_problems", 0)}</div></div>
<div class="stat"><h4>Personas</h4><div class="num">{metrics.get("total_personas", 0)}</div></div>
<div class="stat"><h4>Features</h4><div class="num">{metrics.get("total_features", 0)}</div></div>
<div class="stat"><h4>Shared Personas</h4><div class="num">{metrics.get("shared_persona_count", 0)}</div></div>
<div class="stat"><h4>Overlaps</h4><div class="num">{metrics.get("feature_overlap_count", 0)}</div></div>
</div>
<div class="products-grid">
{product_cards}
</div>
<div class="personas-section">
<h2>Shared Personas ({len(shared_personas)})</h2>
{" ".join(f'<span class="persona-badge">{p.get("persona_name", "")}</span>' for p in shared_personas)}
</div>
</div>
</body>
</html>"""
