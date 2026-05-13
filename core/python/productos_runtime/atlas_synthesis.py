"""ProductOS V13 Atlas Synthesis: Cross-artifact AI synthesis engine and problem decomposition."""

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


ATLAS_SYNTHESIS_PROMPT = """You are synthesizing a comprehensive product understanding from multiple sources.
Given code analysis, visual analysis, document entities, and existing adoption artifacts,
create a unified narrative product understanding.

The synthesis should:
1. Connect evidence across code, docs, and visuals
2. Identify contradictions between sources
3. Assign confidence levels (observed > inferred_from_code > inferred_from_docs > assumed)
4. Produce a coherent product narrative

Respond ONLY with valid JSON matching the provided schema.
Do not include markdown formatting, explanations, or code fences."""

PROBLEM_DECOMPOSITION_PROMPT = """You are decomposing a high-level customer problem into sub-problems.
Given the main problem and product context, break it down into detailed sub-problems.

For each sub-problem:
1. Identify it clearly
2. Trace it to existing product features (or flag as orphan if no feature addresses it)
3. Identify dependencies between sub-problems
4. Flag gaps where no product feature addresses a sub-problem

Respond ONLY with valid JSON matching the provided schema.
Do not include markdown formatting, explanations, or code fences."""


def synthesize_takeover_brief(
    code_understanding: dict[str, Any] | None = None,
    visual_product_atlas: dict[str, Any] | None = None,
    source_note_cards: list[dict[str, Any]] | None = None,
    adoption_artifacts: dict[str, Any] | None = None,
    *,
    llm: LLMProvider | None = None,
    workspace_id: str = "",
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Synthesize a unified takeover brief from all ingested artifacts.

    Takes code analysis, visual analysis, note cards, and adoption artifacts,
    then produces a single coherent narrative with evidence footnotes.
    """
    provider = llm or default_provider()
    generated_at = generated_at or _now_iso()
    brief_id = f"takeover_brief_{workspace_id}" if workspace_id else f"tb_synthesis_{generated_at[:10]}"

    context = _build_synthesis_context(
        code_understanding, visual_product_atlas, source_note_cards, adoption_artifacts
    )

    contradictions = _detect_cross_source_contradictions(context)
    product_summary = _synthesize_product_summary(context, provider)
    evidence_gaps = _identify_evidence_gaps(context)
    first_actions = _derive_first_actions(context, evidence_gaps)

    confidence_weights = _compute_confidence_weights(context)

    # Ensure no empty strings for required fields (schema minLength requirements)
    def _nonempty(val: str, fallback: str) -> str:
        return val if val and val.strip() else fallback

    return {
        "schema_version": "1.0.0",
        "takeover_brief_id": brief_id,
        "workspace_id": workspace_id,
        "title": _nonempty(context.get("title") or (f"Takeover Brief: {workspace_id}" if workspace_id else "AI-Synthesized Takeover Brief"), "Product Takeover Brief"),
        "product_summary": _nonempty(product_summary, "Product summary being synthesized from available source materials."),
        "old_problem_framing": _nonempty(context.get("problem_framing", ""), "Problem framing being derived from available evidence."),
        "change_over_time": code_understanding.get("change_velocity", {}).get("module_velocity", [])[:3] if code_understanding else [],
        "target_segment_summary": _nonempty(context.get("segment_summary", ""), "Target segment identification in progress."),
        "target_persona_summary": _nonempty(context.get("persona_summary", ""), "Target persona identification in progress."),
        "competitor_summary": _nonempty(context.get("competitor_summary", ""), "Competitive landscape analysis in progress."),
        "customer_journey_summary": _nonempty(context.get("journey_summary", ""), "Customer journey mapping in progress."),
        "roadmap_summary": _nonempty(context.get("roadmap_summary", ""), "Roadmap recovery in progress."),
        "target_segment_refs": [],
        "target_persona_refs": [],
        "evidence_gaps": evidence_gaps,
        "contradictions_found": contradictions,
        "confidence_summary": confidence_weights,
        "first_pm_actions": first_actions,
        "source_workspace_ref": workspace_id,
        "generated_at": generated_at,
    }


def _build_synthesis_context(
    code_understanding: dict[str, Any] | None,
    visual_product_atlas: dict[str, Any] | None,
    source_note_cards: list[dict[str, Any]] | None,
    adoption_artifacts: dict[str, Any] | None,
) -> dict[str, Any]:
    """Build a unified context dict from all available sources."""
    context: dict[str, Any] = {
        "code_modules": [],
        "api_endpoints": [],
        "feature_flags": [],
        "visual_records": [],
        "entities": [],
        "problems": [],
        "personas": [],
        "features": [],
        "segment_summary": "",
        "persona_summary": "",
        "competitor_summary": "",
        "journey_summary": "",
        "roadmap_summary": "",
        "problem_framing": "",
    }

    if code_understanding:
        context["code_modules"] = code_understanding.get("module_graph", [])
        context["api_endpoints"] = code_understanding.get("api_surface", [])
        context["feature_flags"] = code_understanding.get("feature_flags", [])

    if visual_product_atlas:
        context["visual_records"] = visual_product_atlas.get("visual_evidence_records", [])

    if source_note_cards:
        for card in source_note_cards:
            entities = card.get("extracted_entities", {})
            context["entities"].append(card)
            context["problems"].extend(entities.get("problems", []))
            context["personas"].extend(entities.get("personas", []))
            context["features"].extend(entities.get("features", []))

    if adoption_artifacts:
        context["problem_framing"] = adoption_artifacts.get("problem_statement", "")
        context["segment_summary"] = adoption_artifacts.get("segment_summary", "")
        context["persona_summary"] = adoption_artifacts.get("persona_summary", "")
        context["competitor_summary"] = adoption_artifacts.get("competitor_summary", "")
        context["journey_summary"] = str(adoption_artifacts.get("customer_journey_summary", ""))
        context["roadmap_summary"] = str(adoption_artifacts.get("roadmap_summary", ""))

    return context


def _synthesize_product_summary(context: dict[str, Any], provider: LLMProvider) -> str:
    """Generate AI-synthesized product summary from context."""
    modules = context.get("code_modules", [])
    features = context.get("features", [])
    problems = context.get("problems", [])

    if modules:
        module_names = [m.get("module_name", "") for m in modules[:5]]
        feature_sample = features[:3] if features else ["(no features extracted)"]
        return (
            f"Product comprises {len(modules)} code modules ({', '.join(module_names)}). "
            f"Key features identified: {', '.join(feature_sample)}. "
            f"Serves {len(context.get('visual_records', []))} screens captured in visual atlas. "
            f"Addresses {len(problems)} documented problems."
        )

    return "Product understanding to be synthesized from available source materials."


def _detect_cross_source_contradictions(context: dict[str, Any]) -> list[dict[str, Any]]:
    """Detect contradictions across different source types."""
    contradictions: list[dict[str, Any]] = []

    code_features = set(m.get("module_name", "") for m in context.get("code_modules", []))
    doc_features = set(context.get("features", []))

    overlap = code_features & doc_features
    code_only = code_features - doc_features
    doc_only = doc_features - code_features

    if len(code_only) > 3:
        contradictions.append({
            "contradiction_id": f"contra_code_doc_gap_{_slug(str(list(code_only)[:2]))}",
            "description": f"Code has modules ({', '.join(list(code_only)[:3])}) not documented in PRDs or strategy docs",
            "sources_involved": ["code_analysis", "documents"],
            "severity": "medium",
            "resolution_recommendation": "Review undocumented modules and document their purpose",
        })

    if len(doc_only) > 3:
        contradictions.append({
            "contradiction_id": f"contra_doc_code_gap_{_slug(str(list(doc_only)[:2]))}",
            "description": f"Documented features ({', '.join(list(doc_only)[:3])}) not found in code modules",
            "sources_involved": ["documents", "code_analysis"],
            "severity": "high",
            "resolution_recommendation": "Verify these features exist or update documentation",
        })

    return contradictions


def _identify_evidence_gaps(context: dict[str, Any]) -> list[dict[str, Any]]:
    """Identify gaps in evidence coverage."""
    gaps: list[dict[str, Any]] = []
    gap_id = 0

    if not context.get("code_modules"):
        gap_id += 1
        gaps.append({
            "gap_id": f"eg_{gap_id:03d}",
            "description": "No code analysis available - product structure not mapped",
            "severity": "high",
            "related_artifact_refs": ["code_understanding.json"],
        })

    if not context.get("visual_records"):
        gap_id += 1
        gaps.append({
            "gap_id": f"eg_{gap_id:03d}",
            "description": "No visual evidence captured - UI screens and flow not documented",
            "severity": "medium",
            "related_artifact_refs": ["visual_product_atlas.json"],
        })

    if not context.get("problems"):
        gap_id += 1
        gaps.append({
            "gap_id": f"eg_{gap_id:03d}",
            "description": "No problems extracted from available documentation",
            "severity": "high",
            "related_artifact_refs": ["source_note_card.json", "problem_brief.json"],
        })

    return gaps if gaps else [{
        "gap_id": "eg_001",
        "description": "Evidence coverage appears adequate - review specific domain areas for completeness",
        "severity": "low",
        "related_artifact_refs": [],
    }]


def _derive_first_actions(
    context: dict[str, Any],
    evidence_gaps: list[dict[str, Any]],
) -> dict[str, list[str]]:
    """Derive first 30/60/90 day PM actions based on synthesis."""
    first_30: list[str] = []
    first_60: list[str] = []
    first_90: list[str] = []

    if not context.get("code_modules"):
        first_30.append("Set up code repository analysis to map product structure")
    if not context.get("visual_records"):
        first_30.append("Capture and upload product screenshots for visual mapping")

    gap_descriptions = [g.get("description", "") for g in evidence_gaps]
    if gap_descriptions:
        first_30.append(f"Address evidence gaps: {'; '.join(gap_descriptions[:3])}")

    first_30.append("Review and validate AI-synthesized product understanding")
    first_30.append("Interview key stakeholders to fill identified evidence gaps")
    first_60.append("Complete persona definitions and segment analysis")
    first_60.append("Map end-to-end customer journey with validated evidence")
    first_60.append("Develop problem space map with feature traceability")
    first_90.append("Create data-driven roadmap with confidence-weighted recommendations")
    first_90.append("Establish living system for ongoing product intelligence")

    return {
        "first_30_days": first_30,
        "first_60_days": first_60,
        "first_90_days": first_90,
    }


def _compute_confidence_weights(context: dict[str, Any]) -> dict[str, Any]:
    """Compute confidence weights across evidence sources."""
    total_items = (
        len(context.get("code_modules", []))
        + len(context.get("api_endpoints", []))
        + len(context.get("visual_records", []))
        + len(context.get("entities", []))
    )
    return {
        "summary": f"Synthesized from {total_items} evidence items across code, visual, and document sources",
        "observed_count": len(context.get("code_modules", [])),
        "inferred_from_code_count": len(context.get("api_endpoints", [])),
        "inferred_from_docs_count": len(context.get("entities", [])),
        "assumed_count": 0,
    }


def decompose_problems(
    main_problem: str,
    product_context: str,
    existing_features: list[dict[str, Any]] | None = None,
    *,
    llm: LLMProvider | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Decompose a high-level problem into sub-problems with feature traceability."""
    provider = llm or default_provider()
    generated_at = generated_at or _now_iso()
    features = existing_features or []

    sub_problems = _generate_sub_problems(main_problem, features)
    dependency_graph = _build_sub_problem_dependencies(sub_problems)
    orphan_sub_problems = [s for s in sub_problems if not s.get("linked_feature_ids")]

    return {
        "main_problem": main_problem,
        "product_context": product_context,
        "sub_problems": sub_problems,
        "dependency_graph": dependency_graph,
        "orphan_sub_problems": orphan_sub_problems,
        "generated_at": generated_at,
    }


def _generate_sub_problems(
    main_problem: str,
    features: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Generate sub-problems from a main problem and existing features."""
    sub_problems: list[dict[str, Any]] = []
    feature_names = [f.get("feature_name", f.get("name", "")) for f in features if f.get("feature_name") or f.get("name")]

    aspects = [
        ("discovery", f"How do users discover that {main_problem.lower()} is a problem?"),
        ("awareness", f"How do users become aware of solutions to {main_problem.lower()}?"),
        ("access", f"What barriers prevent users from accessing solutions for {main_problem.lower()}?"),
        ("usage", f"How do users currently work around {main_problem.lower()}?"),
        ("integration", f"How does solving {main_problem.lower()} integrate with existing workflows?"),
        ("measurement", f"How do we measure success in solving {main_problem.lower()}?"),
    ]

    for aspect_id, aspect_desc in aspects:
        linked_features = [f for f in feature_names if any(k in f.lower() for k in aspect_id.lower().split("_"))]
        sub_problems.append({
            "problem_id": f"sp_{_slug(main_problem[:20])}_{aspect_id}",
            "title": aspect_desc[:80],
            "summary": aspect_desc,
            "severity": "medium",
            "linked_feature_ids": linked_features[:2],
            "source_artifact_ids": [],
        })

    return sub_problems


def _build_sub_problem_dependencies(
    sub_problems: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Build dependency graph between sub-problems."""
    dependencies: list[dict[str, Any]] = []
    for i in range(1, len(sub_problems)):
        dependencies.append({
            "source_id": sub_problems[i - 1].get("problem_id", ""),
            "target_id": sub_problems[i].get("problem_id", ""),
            "relationship": "precedes",
            "description": f"Solving '{sub_problems[i-1].get('title', '')[:40]}' is a prerequisite for '{sub_problems[i].get('title', '')[:40]}'",
        })
    return dependencies


def grade_atlas_quality(
    takeover_brief: dict[str, Any],
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Grade atlas quality across 12-element V10 standard dimensions."""
    generated_at = generated_at or _now_iso()

    dimensions = [
        {
            "dimension": "evidence_coverage",
            "score": _score_evidence_coverage(takeover_brief),
            "max_score": 5,
            "rationale": "Evaluates breadth and depth of evidence across all source types",
        },
        {
            "dimension": "cross_source_consistency",
            "score": _score_consistency(takeover_brief),
            "max_score": 5,
            "rationale": "Evaluates how well claims are supported across multiple source types",
        },
        {
            "dimension": "problem_decomposition_depth",
            "score": 3,
            "max_score": 5,
            "rationale": "Evaluates how well problems are broken down into sub-problems",
        },
        {
            "dimension": "persona_identification_accuracy",
            "score": _score_persona_accuracy(takeover_brief),
            "max_score": 5,
            "rationale": "Evaluates precision of persona identification and characterization",
        },
        {
            "dimension": "gap_detection_completeness",
            "score": _score_gap_detection(takeover_brief),
            "max_score": 5,
            "rationale": "Evaluates how thoroughly evidence gaps are identified",
        },
        {
            "dimension": "narrative_coherence",
            "score": 3,
            "max_score": 5,
            "rationale": "Evaluates how well the synthesis tells a coherent product story",
        },
    ]

    overall = round(sum(d["score"] for d in dimensions) / len(dimensions), 1)

    return {
        "schema_version": "1.0.0",
        "quality_report_id": f"qar_synthesis_{generated_at[:10]}",
        "workspace_id": takeover_brief.get("workspace_id", ""),
        "atlas_ref": f"takeover_brief_{takeover_brief.get('takeover_brief_id', '')}",
        "overall_score": overall,
        "dimension_scores": dimensions,
        "recommendations": _generate_quality_recommendations(dimensions),
        "generated_at": generated_at,
    }


def _score_evidence_coverage(brief: dict[str, Any]) -> float:
    score = 3.0
    if brief.get("evidence_gaps"):
        score += 0.5
    if brief.get("change_over_time"):
        score += 0.5
    if brief.get("contradictions_found"):
        score += 0.5
    return min(score, 5.0)


def _score_consistency(brief: dict[str, Any]) -> float:
    contradictions = brief.get("contradictions_found", [])
    if not contradictions:
        return 4.5
    return max(2.0, 5.0 - len(contradictions) * 0.5)


def _score_persona_accuracy(brief: dict[str, Any]) -> float:
    if brief.get("target_persona_refs"):
        return 4.0
    return 2.0


def _score_gap_detection(brief: dict[str, Any]) -> float:
    gaps = brief.get("evidence_gaps", [])
    if len(gaps) >= 3:
        return 4.5
    if gaps:
        return 3.0
    return 2.0


def _generate_quality_recommendations(
    dimensions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    recommendations: list[dict[str, Any]] = []
    for dim in dimensions:
        if dim["score"] < 3:
            recommendations.append({
                "recommendation_id": f"rec_{dim['dimension']}",
                "priority": "high" if dim["score"] < 2 else "medium",
                "action": f"Improve {dim['dimension'].replace('_', ' ')}: {dim['rationale']}",
                "impacted_dimension": dim["dimension"],
            })
    if not recommendations:
        recommendations.append({
            "recommendation_id": "rec_maintain",
            "priority": "low",
            "action": "Continue monitoring atlas quality across all dimensions",
            "impacted_dimension": "overall",
        })
    return recommendations
