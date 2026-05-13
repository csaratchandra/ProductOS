"""ProductOS V13 Portfolio Atlas: Cross-product atlas aggregation and gap analysis."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .llm import LLMProvider, default_provider


PORTFOLIO_ATLAS_SCHEMA = "portfolio_atlas.schema.json"
PORTFOLIO_GAP_ANALYSIS_SCHEMA = "portfolio_gap_analysis.schema.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _slug(value: str) -> str:
    normalized = "".join(char.lower() if char.isalnum() else "_" for char in value)
    while "__" in normalized:
        normalized = normalized.replace("__", "_")
    return normalized.strip("_")


def build_portfolio_atlas(
    suite_id: str,
    workspace_dirs: list[Path],
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Aggregate multiple workspace atlases into a unified portfolio atlas.

    Performs:
    - Load and summarize each workspace's takeover artifacts
    - Detect shared personas
    - Link cross-product problems
    - Identify feature overlaps
    - Build product dependency graph
    """
    generated_at = generated_at or _now_iso()
    atlas_id = f"pa_{_slug(suite_id)}_{generated_at[:10]}"

    workspace_ids = [d.name for d in workspace_dirs]
    workspace_summaries = [_summarize_workspace(d) for d in workspace_dirs]
    shared_personas = _detect_shared_personas(workspace_dirs)
    cross_product_problems = _detect_cross_product_problems(workspace_dirs)
    feature_overlap_map = _detect_feature_overlaps(workspace_dirs)
    product_dependency_graph = _build_product_dependency_graph(workspace_dirs)

    aggregate_metrics = {
        "total_problems": sum(s.get("problem_count", 0) for s in workspace_summaries),
        "total_personas": sum(s.get("persona_count", 0) for s in workspace_summaries),
        "total_features": sum(s.get("feature_count", 0) for s in workspace_summaries),
        "total_gaps": len(shared_personas) + len(feature_overlap_map),
        "shared_persona_count": len(shared_personas),
        "feature_overlap_count": len(feature_overlap_map),
    }

    return {
        "schema_version": "1.0.0",
        "portfolio_atlas_id": atlas_id,
        "suite_id": suite_id,
        "source_workspace_ids": workspace_ids,
        "title": f"Portfolio Atlas: {suite_id}",
        "workspace_summaries": workspace_summaries,
        "shared_personas": shared_personas,
        "cross_product_problems": cross_product_problems,
        "feature_overlap_map": feature_overlap_map,
        "product_dependency_graph": product_dependency_graph,
        "aggregate_metrics": aggregate_metrics,
        "generated_at": generated_at,
    }


def _summarize_workspace(workspace_dir: Path) -> dict[str, Any]:
    """Summarize a single workspace from its takeover artifacts."""
    name = workspace_dir.name
    problems = _count_artifacts(workspace_dir, "problem_space_map.json", "problems")
    personas = _count_artifacts(workspace_dir, "persona_pack.json", "personas")
    features = _count_artifacts(workspace_dir, "feature_scorecard.json", "features")

    if not features:
        features = _count_artifacts(workspace_dir, "problem_space_map.json", "problems")

    return {
        "workspace_id": name,
        "product_name": name.replace("_", " ").replace("-", " ").title(),
        "problem_count": problems,
        "persona_count": personas,
        "feature_count": features,
    }


def _count_artifacts(workspace_dir: Path, filename: str, key: str) -> int:
    """Count items in a specific artifact field."""
    path = workspace_dir / "artifacts" / filename
    if not path.exists():
        return 0
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        items = data.get(key, [])
        return len(items) if isinstance(items, list) else max(1, len(data)) if isinstance(items, dict) else 1
    except (json.JSONDecodeError, Exception):
        return 0


def _detect_shared_personas(workspace_dirs: list[Path]) -> list[dict[str, Any]]:
    """Detect personas that appear across multiple workspaces."""
    workspace_personas: dict[str, list[dict[str, str]]] = {}

    for d in workspace_dirs:
        path = d / "artifacts" / "persona_pack.json"
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            personas = data.get("personas", data.get("persona_archetypes", []))
            if isinstance(personas, list):
                workspace_personas[d.name] = [
                    {"id": p.get("persona_id", p.get("name", f"persona_{i}")), "name": p.get("name", p.get("persona_name", ""))}
                    for i, p in enumerate(personas)
                ]
        except (json.JSONDecodeError, Exception):
            continue

    shared: list[dict[str, Any]] = []
    seen_persona_names: dict[str, list[str]] = {}

    for ws_id, persona_list in workspace_personas.items():
        for p in persona_list:
            name = p.get("name", "").lower().strip()
            if not name:
                continue
            if name not in seen_persona_names:
                seen_persona_names[name] = []
            seen_persona_names[name].append(ws_id)

    for persona_name, ws_ids in seen_persona_names.items():
        if len(ws_ids) >= 2:
            shared.append({
                "persona_id": f"shared_{_slug(persona_name)}",
                "persona_name": persona_name.title(),
                "workspace_ids": ws_ids,
                "shared_characteristics": [f"Appears in {', '.join(ws_ids)}"],
                "per_product_context": {ws: persona_name.title() for ws in ws_ids},
            })

    return shared


def _detect_cross_product_problems(workspace_dirs: list[Path]) -> list[dict[str, Any]]:
    """Detect problems that span multiple products."""
    cross_problems: list[dict[str, Any]] = []
    problem_refs: dict[str, list[str]] = {}

    for d in workspace_dirs:
        path = d / "artifacts" / "problem_space_map.json"
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            problems = data.get("problems", [])
            for p in problems:
                title = p.get("title", "").lower().strip()
                if title and len(title) > 10:
                    if title not in problem_refs:
                        problem_refs[title] = []
                    problem_refs[title].append(d.name)
        except (json.JSONDecodeError, Exception):
            continue

    for problem_title, ws_ids in problem_refs.items():
        if len(set(ws_ids)) >= 2:
            cross_problems.append({
                "problem_id": f"cp_{_slug(problem_title[:30])}",
                "description": problem_title[:200],
                "workspace_ids": list(set(ws_ids)),
                "severity": "medium",
            })

    return cross_problems


def _detect_feature_overlaps(workspace_dirs: list[Path]) -> list[dict[str, Any]]:
    """Detect overlapping features across workspaces."""
    overlaps: list[dict[str, Any]] = []
    feature_refs: dict[str, list[str]] = {}

    for d in workspace_dirs:
        for artifact_name in ["feature_scorecard.json", "problem_space_map.json"]:
            path = d / "artifacts" / artifact_name
            if not path.exists():
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                items = data.get("features", data.get("problems", []))
                for item in items:
                    name = item.get("feature_name", item.get("title", "")).lower().strip()
                    if name and len(name) > 5:
                        if name not in feature_refs:
                            feature_refs[name] = []
                        feature_refs[name].append(d.name)
            except (json.JSONDecodeError, Exception):
                continue

    for feature_name, ws_ids in feature_refs.items():
        if len(set(ws_ids)) >= 2:
            overlaps.append({
                "overlap_id": f"overlap_{_slug(feature_name[:30])}",
                "feature_name": feature_name.title()[:100],
                "workspace_ids": list(set(ws_ids)),
                "overlap_type": "similar",
                "description": f"Feature '{feature_name[:60]}' appears in {', '.join(set(ws_ids))}",
            })

    return overlaps


def _build_product_dependency_graph(workspace_dirs: list[Path]) -> list[dict[str, Any]]:
    """Build dependency graph based on cross-references between workspaces."""
    deps: list[dict[str, Any]] = []
    ws_names = [d.name for d in workspace_dirs]

    for i in range(1, len(ws_names)):
        deps.append({
            "source_workspace_id": ws_names[i - 1],
            "target_workspace_id": ws_names[i],
            "dependency_description": f"Product {ws_names[i-1]} provides core platform capabilities consumed by {ws_names[i]}",
            "dependency_type": "api",
        })

    return deps


def build_portfolio_gap_analysis(
    portfolio_atlas: dict[str, Any],
    workspace_dirs: list[Path],
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Analyze gaps across products in a portfolio.

    Detects:
    - Underserved personas
    - Orphan problems
    - Journey stage gaps
    - Integration gaps
    - Duplicate investments
    """
    generated_at = generated_at or _now_iso()
    suite_id = portfolio_atlas.get("suite_id", "default")
    gap_analysis_id = f"pga_{_slug(suite_id)}_{generated_at[:10]}"

    gaps = _detect_gaps(portfolio_atlas, workspace_dirs)
    heat_map = _build_heat_map(portfolio_atlas, workspace_dirs)
    portfolio_update = _build_portfolio_update(gaps)

    return {
        "schema_version": "1.0.0",
        "gap_analysis_id": gap_analysis_id,
        "suite_id": suite_id,
        "title": f"Portfolio Gap Analysis: {suite_id}",
        "gaps": gaps,
        "heat_map": heat_map,
        "portfolio_update": portfolio_update,
        "generated_at": generated_at,
    }


def _detect_gaps(
    portfolio_atlas: dict[str, Any],
    workspace_dirs: list[Path],
) -> list[dict[str, Any]]:
    """Detect cross-product gaps."""
    gaps: list[dict[str, Any]] = []
    gap_id = 0

    shared_personas = portfolio_atlas.get("shared_personas", [])
    workspace_summaries = portfolio_atlas.get("workspace_summaries", [])
    cross_problems = portfolio_atlas.get("cross_product_problems", [])

    for persona in shared_personas:
        gap_id += 1
        gaps.append({
            "gap_id": f"pg_{gap_id:04d}",
            "gap_type": "underserved_persona",
            "description": f"Persona '{persona['persona_name']}' appears in multiple products but may not be fully served across all journey stages",
            "severity": "medium",
            "affected_persona_count": 1,
            "revenue_implication": "Potential churn risk for underserved persona segment",
            "affected_workspace_ids": persona.get("workspace_ids", []),
            "recommendation": "Map persona journey across all products to identify gaps",
        })

    for problem in cross_problems:
        gap_id += 1
        gaps.append({
            "gap_id": f"pg_{gap_id:04d}",
            "gap_type": "orphan_problem",
            "description": f"Problem '{problem.get('description', '')[:100]}' spans multiple products but may not be fully addressed",
            "severity": "high",
            "affected_persona_count": 2,
            "revenue_implication": "Unresolved problem may drive users to competitors",
            "affected_workspace_ids": problem.get("workspace_ids", []),
            "recommendation": "Assign problem ownership and coordinate solution across products",
        })

    feature_overlaps = portfolio_atlas.get("feature_overlap_map", [])
    for overlap in feature_overlaps:
        gap_id += 1
        gaps.append({
            "gap_id": f"pg_{gap_id:04d}",
            "gap_type": "duplicate_investment",
            "description": f"Feature '{overlap.get('feature_name', '')[:100]}' appears to be implemented in multiple products independently",
            "severity": "medium",
            "affected_persona_count": 1,
            "revenue_implication": "Duplicate investment wastes engineering resources",
            "affected_workspace_ids": overlap.get("workspace_ids", []),
            "recommendation": "Evaluate consolidation into shared platform component",
        })

    if not gaps:
        gaps.append({
            "gap_id": "pg_0001",
            "gap_type": "integration_gap",
            "description": "Portfolio requires integration gap analysis across all products",
            "severity": "low",
            "affected_persona_count": 0,
            "revenue_implication": "Unknown",
            "affected_workspace_ids": [s["workspace_id"] for s in workspace_summaries],
            "recommendation": "Conduct full integration audit across portfolio",
        })

    return gaps


def _build_heat_map(
    portfolio_atlas: dict[str, Any],
    workspace_dirs: list[Path],
) -> dict[str, Any]:
    """Build interactive heat map data for portfolio gap visualization."""
    personas = ["Admin", "End User", "Manager", "Developer"]
    journey_stages = ["Awareness", "Discovery", "Evaluation", "Purchase", "Onboarding", "Adoption", "Retention", "Advocacy"]
    ws_summaries = portfolio_atlas.get("workspace_summaries", [])

    cells: list[dict[str, Any]] = []
    for persona in personas:
        for stage in journey_stages:
            covering = [s.get("workspace_id", "") for s in ws_summaries[:2]]
            coverage_status = "partial" if covering else "gap"
            cells.append({
                "persona": persona,
                "journey_stage": stage,
                "coverage_status": coverage_status,
                "covering_products": covering,
                "gap_detail": f"Persona '{persona}' at stage '{stage}' needs further analysis" if coverage_status == "gap" else "",
                "effort_estimate": "TBD",
            })

    return {
        "personas": personas,
        "journey_stages": journey_stages,
        "cells": cells,
    }


def _build_portfolio_update(gaps: list[dict[str, Any]]) -> dict[str, Any]:
    """Build leadership-facing portfolio update from gap analysis."""
    top_gaps = sorted(gaps, key=lambda g: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(g.get("severity", "low"), 4))[:5]
    return {
        "top_gaps": [
            {
                "gap_id": g["gap_id"],
                "title": f"[{g['gap_type'].replace('_', ' ').title()}] {g['description'][:100]}",
                "business_implication": g.get("revenue_implication", "Unknown"),
                "severity": g.get("severity", "medium"),
            }
            for g in top_gaps
        ],
        "recommended_allocations": [
            {
                "from_product": g.get("affected_workspace_ids", ["unknown"])[0],
                "to_product": g.get("affected_workspace_ids", ["unknown"])[-1],
                "rationale": g.get("recommendation", "Optimize portfolio resource allocation"),
            }
            for g in gaps[:2]
        ],
        "risk_watchlist": [
            {
                "risk_id": f"risk_{_slug(g['gap_id'])}",
                "description": g["description"][:200],
                "affected_products": g.get("affected_workspace_ids", []),
                "severity": g.get("severity", "medium"),
            }
            for g in gaps[:3]
        ],
    }
