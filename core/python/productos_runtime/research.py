from __future__ import annotations

import copy
import json
import re
import tempfile
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html import unescape
from os import getenv
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, quote_plus, unquote, urlparse

from . import yaml_compat as yaml
from .governed_docs import render_governed_markdown


RESEARCH_RUNTIME_ARTIFACT_SCHEMAS = {
    "framework_registry": "framework_registry.schema.json",
    "research_notebook": "research_notebook.schema.json",
    "research_brief": "research_brief.schema.json",
    "external_research_review": "external_research_review.schema.json",
    "competitor_dossier": "competitor_dossier.schema.json",
    "customer_pulse": "customer_pulse.schema.json",
    "market_analysis_brief": "market_analysis_brief.schema.json",
    "landscape_matrix": "landscape_matrix.schema.json",
    "market_sizing_brief": "market_sizing_brief.schema.json",
    "market_share_brief": "market_share_brief.schema.json",
    "opportunity_portfolio_view": "opportunity_portfolio_view.schema.json",
    "prioritization_decision_record": "prioritization_decision_record.schema.json",
    "feature_prioritization_brief": "feature_prioritization_brief.schema.json",
}
RESEARCH_PLANNING_ARTIFACT_SCHEMAS = {
    "external_research_plan": "external_research_plan.schema.json",
}
RESEARCH_FEED_REGISTRY_ARTIFACT_SCHEMAS = {
    "external_research_feed_registry": "external_research_feed_registry.schema.json",
}
RESEARCH_DISCOVERY_ARTIFACT_SCHEMAS = {
    "external_research_source_discovery": "external_research_source_discovery.schema.json",
}

DISCOVERY_OPERATIONS_ARTIFACT_FILENAMES = {
    "framework_registry": "framework_registry.json",
    "research_handoff": "handoff_discovery_to_research.json",
    "research_notebook": "research_notebook.json",
    "research_brief": "research_brief.json",
    "external_research_plan": "external_research_plan.json",
    "external_research_source_discovery": "external_research_source_discovery.json",
    "external_research_review": "external_research_review.json",
    "competitor_dossier": "competitor_dossier.json",
    "customer_pulse": "customer_pulse.json",
    "market_analysis_brief": "market_analysis_brief.json",
    "landscape_matrix": "landscape_matrix.json",
    "market_sizing_brief": "market_sizing_brief.json",
    "market_share_brief": "market_share_brief.json",
    "opportunity_portfolio_view": "opportunity_portfolio_view.json",
    "prioritization_decision_record": "prioritization_decision_record.json",
    "feature_prioritization_brief": "feature_prioritization_brief.json",
}

CORE_RESEARCH_SIGNAL_LANES = [
    {
        "signal_lane_id": "market",
        "label": "market",
        "source_types": {"market_validation", "security_review"},
        "preferred_source_type": "market_validation",
    },
    {
        "signal_lane_id": "competitor",
        "label": "competitor",
        "source_types": {"competitor_research"},
        "preferred_source_type": "competitor_research",
    },
    {
        "signal_lane_id": "customer",
        "label": "customer",
        "source_types": {"customer_evidence", "operator_interview"},
        "preferred_source_type": "customer_evidence",
    },
]


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def _slug(value: str) -> str:
    normalized = "".join(char.lower() if char.isalnum() else "_" for char in value)
    while "__" in normalized:
        normalized = normalized.replace("__", "_")
    return normalized.strip("_")


def _append_manifest_artifact_path(manifest_path: Path, relative_path: str) -> None:
    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = yaml.safe_load(handle)
    artifact_paths = manifest.setdefault("artifact_paths", [])
    if relative_path not in artifact_paths:
        artifact_paths.append(relative_path)
    with manifest_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(manifest, handle, sort_keys=False)


def _relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return path.as_posix()


def _signal_lane_definition_for_source_type(source_type: str) -> dict[str, Any] | None:
    for lane in CORE_RESEARCH_SIGNAL_LANES:
        if source_type in lane["source_types"]:
            return lane
    return None


def _signal_lane_id_for_source_type(source_type: str) -> str:
    lane = _signal_lane_definition_for_source_type(source_type)
    if lane is None:
        return source_type
    return lane["signal_lane_id"]


def _framework_registry_id(workspace_id: str) -> str:
    return f"framework_registry_{workspace_id}"


def _priority_lane(score: int) -> str:
    if score >= 88:
        return "must_now"
    if score >= 74:
        return "next"
    if score >= 60:
        return "later"
    return "park"


def _bounded_priority_score(
    *,
    strategic_fit: int,
    evidence_strength: int,
    agentic_leverage: int,
    burden_penalty: int,
    urgency: int,
) -> int:
    score = strategic_fit + evidence_strength + agentic_leverage + urgency - burden_penalty
    return max(1, min(100, score))


def _agentic_level(score: int) -> str:
    if score >= 8:
        return "high"
    if score >= 5:
        return "medium"
    return "low"


def _confidence_label(score: int) -> str:
    if score >= 8:
        return "high"
    if score >= 5:
        return "moderate"
    return "low"


def _signal_lane_label(signal_lane_id: str) -> str:
    for lane in CORE_RESEARCH_SIGNAL_LANES:
        if lane["signal_lane_id"] == signal_lane_id:
            return lane["label"]
    return signal_lane_id.replace("_", " ")


def _core_signal_lane_ids() -> list[str]:
    return [lane["signal_lane_id"] for lane in CORE_RESEARCH_SIGNAL_LANES]


def _planned_signal_lane_ids(questions: list[dict[str, Any]]) -> list[str]:
    present_signal_lanes = {
        _signal_lane_id_for_source_type(question["recommended_source_type"])
        for question in questions
        if isinstance(question, dict) and isinstance(question.get("recommended_source_type"), str)
    }
    ordered_signal_lanes = [
        lane_id for lane_id in _core_signal_lane_ids() if lane_id in present_signal_lanes
    ]
    remaining_signal_lanes = sorted(present_signal_lanes - set(ordered_signal_lanes))
    return [*ordered_signal_lanes, *remaining_signal_lanes]


def _synthesized_signal_lane_question(
    research_brief: dict[str, Any],
    *,
    signal_lane_id: str,
) -> dict[str, Any]:
    brief_title = _brief_title(research_brief["title"])
    if signal_lane_id == "market":
        return {
            "question_id": "baseline_market_validation",
            "question": f"What current market evidence proves the urgency and timing behind {brief_title}?",
            "why_it_matters": "ProductOS should not broaden strategy or release claims until the market urgency is visible outside the workspace.",
            "recommended_source_type": "market_validation",
            "priority": "high",
        }
    if signal_lane_id == "competitor":
        return {
            "question_id": "baseline_competitor_research",
            "question": f"How do current alternatives position against the core problem in {brief_title}, and where is the wedge still differentiated?",
            "why_it_matters": "PM positioning should be grounded in live competitor narratives instead of an internal-only story.",
            "recommended_source_type": "competitor_research",
            "priority": "high",
        }
    return {
        "question_id": "baseline_customer_evidence",
        "question": f"What direct customer or operator evidence confirms the workflow burden described in {brief_title}?",
        "why_it_matters": "ProductOS needs first-hand customer proof before treating the current pain as broadly representative.",
        "recommended_source_type": "customer_evidence",
        "priority": "high",
    }


def _ensure_core_signal_lane_questions(research_brief: dict[str, Any], questions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    planned_lane_ids = set(_planned_signal_lane_ids(questions))
    expanded_questions = list(questions)
    for signal_lane_id in _core_signal_lane_ids():
        if signal_lane_id in planned_lane_ids:
            continue
        expanded_questions.append(
            _synthesized_signal_lane_question(research_brief, signal_lane_id=signal_lane_id)
        )
        planned_lane_ids.add(signal_lane_id)
    return expanded_questions


def _signal_lane_coverage(
    questions: list[dict[str, Any]],
    *,
    discovered_questions: list[dict[str, Any]] | None = None,
    candidate_sources: list[dict[str, Any]] | None = None,
    selected_sources: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    discovered_questions = discovered_questions or []
    candidate_sources = candidate_sources or []
    selected_sources = selected_sources or []
    coverage: list[dict[str, Any]] = []
    for lane in CORE_RESEARCH_SIGNAL_LANES:
        signal_lane_id = lane["signal_lane_id"]
        planned_question_count = sum(
            1
            for question in questions
            if _signal_lane_id_for_source_type(question["recommended_source_type"]) == signal_lane_id
        )
        discovered_question_count = sum(
            1
            for question in discovered_questions
            if _signal_lane_id_for_source_type(question["source_type"]) == signal_lane_id and question.get("candidate_count", 0) > 0
        )
        candidate_source_count = sum(
            1
            for source in candidate_sources
            if _signal_lane_id_for_source_type(source["source_type"]) == signal_lane_id
        )
        suggested_source_count = sum(
            1
            for source in candidate_sources
            if _signal_lane_id_for_source_type(source["source_type"]) == signal_lane_id
            and source.get("selection_status") == "suggested"
        )
        selected_source_count = sum(
            1
            for source in selected_sources
            if _signal_lane_id_for_source_type(source["source_type"]) == signal_lane_id
        )
        coverage.append(
            {
                "signal_lane_id": signal_lane_id,
                "label": lane["label"],
                "planned_question_count": planned_question_count,
                "discovered_question_count": discovered_question_count,
                "candidate_source_count": candidate_source_count,
                "suggested_source_count": suggested_source_count,
                "selected_source_count": selected_source_count,
            }
        )
    return coverage


def _strip_html(text: str) -> str:
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    return " ".join(unescape(text).split())


def _clip(text: str, limit: int) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def _split_sentences(text: str) -> list[str]:
    parts = [part.strip() for part in re.split(r"(?<=[.!?])\s+", " ".join(text.split())) if part.strip()]
    return parts


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        try:
            dt = datetime.fromisoformat(f"{value}T00:00:00+00:00")
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _feed_cadence_days(refresh_cadence: str | None) -> int | None:
    if refresh_cadence == "daily":
        return 1
    if refresh_cadence == "weekly":
        return 7
    if refresh_cadence == "monthly":
        return 30
    return None


def _feed_cadence_status(feed: dict[str, Any], generated_at: str) -> tuple[str, str]:
    refresh_cadence = feed.get("refresh_cadence")
    if refresh_cadence == "manual":
        return "manual", "Manual feed; refresh on explicit PM review."

    cadence_days = _feed_cadence_days(refresh_cadence)
    if cadence_days is None:
        return "unknown", "Refresh cadence is missing or unsupported."

    last_success = _parse_datetime(feed.get("last_success_at"))
    generated = _parse_datetime(generated_at)
    if last_success is None or generated is None:
        return "due", "No successful refresh has been recorded for this feed yet."

    age_days = max((generated - last_success).days, 0)
    if age_days <= cadence_days:
        return "current", f"Feed refreshed within its {refresh_cadence} cadence window."
    if age_days <= cadence_days * 2:
        return "due", f"Feed is past its {refresh_cadence} cadence and should be refreshed."
    return "stale", f"Feed is materially past its {refresh_cadence} cadence and should not be trusted without refresh."


def _freshness_label(published_at: str | None, generated_at: str) -> str:
    published = _parse_datetime(published_at)
    generated = _parse_datetime(generated_at)
    if published is None or generated is None:
        return "usable_with_review"
    age_days = (generated - published).days
    if age_days <= 30:
        return "fresh"
    if age_days <= 180:
        return "usable_with_review"
    return "stale"


def _extract_meta_content(raw: str, names: list[str]) -> str | None:
    for name in names:
        pattern = (
            r'(?is)<meta[^>]+(?:property|name|itemprop)=["\']'
            + re.escape(name)
            + r'["\'][^>]+content=["\'](.*?)["\']'
        )
        match = re.search(pattern, raw)
        if match:
            value = _clip(_strip_html(match.group(1)), 220)
            if value:
                return value
    return None


def _extract_published_at(raw: str) -> str | None:
    meta_date = _extract_meta_content(
        raw,
        [
            "article:published_time",
            "article:modified_time",
            "og:published_time",
            "pubdate",
            "publishdate",
            "date",
            "datePublished",
            "dateModified",
        ],
    )
    if meta_date:
        return meta_date

    time_match = re.search(r'(?is)<time[^>]+datetime=["\'](.*?)["\']', raw)
    if time_match:
        return _clip(_strip_html(time_match.group(1)), 40)

    json_ld_match = re.search(
        r'(?is)"(?:datePublished|dateModified)"\s*:\s*"([^"]+)"',
        raw,
    )
    if json_ld_match:
        return _clip(_strip_html(json_ld_match.group(1)), 40)
    return None


def _extract_html_metadata(raw: str) -> dict[str, str | None]:
    title = _extract_meta_content(raw, ["og:title", "twitter:title"])
    if title is None:
        match = re.search(r"(?is)<title>(.*?)</title>", raw)
        if match:
            title = _clip(_strip_html(match.group(1)), 120)
    if title is None:
        match = re.search(r"(?is)<h1[^>]*>(.*?)</h1>", raw)
        if match:
            title = _clip(_strip_html(match.group(1)), 120)
    summary_hint = _extract_meta_content(raw, ["description", "og:description", "twitter:description"])
    published_at = _extract_published_at(raw)
    return {
        "title": title,
        "summary_hint": summary_hint,
        "published_at": published_at,
    }


def _read_uri_details(uri: str) -> dict[str, str]:
    parsed = urlparse(uri)
    if parsed.scheme in {"http", "https", "file"}:
        request = urllib.request.Request(uri, headers={"User-Agent": "ProductOS-Research/1.0"})
        with urllib.request.urlopen(request, timeout=15) as response:
            raw = response.read().decode("utf-8", errors="ignore")
        metadata = _extract_html_metadata(raw)
        content = _strip_html(raw) if "<html" in raw.lower() or "</" in raw else " ".join(raw.split())
        return {
            "content": content,
            "title": metadata.get("title") or "",
            "summary_hint": metadata.get("summary_hint") or "",
            "published_at": metadata.get("published_at") or "",
        }
    path = Path(uri)
    if path.exists():
        raw = path.read_text(encoding="utf-8")
        metadata = _extract_html_metadata(raw) if "<html" in raw.lower() or "</" in raw else {}
        return {
            "content": _strip_html(raw) if "<html" in raw.lower() or "</" in raw else " ".join(raw.split()),
            "title": metadata.get("title") or path.stem.replace("-", " ").title(),
            "summary_hint": metadata.get("summary_hint") or "",
            "published_at": metadata.get("published_at") or "",
        }
    raise FileNotFoundError(f"Unsupported research source URI: {uri}")


def _read_uri(uri: str) -> tuple[str, str]:
    details = _read_uri_details(uri)
    return details["content"], details["title"]


def _load_source_manifest(path: Path) -> list[dict[str, Any]]:
    payload = _load_json(path)
    sources = payload.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("Research source manifest must contain a non-empty 'sources' list.")
    return sources


def _load_html(uri: str) -> str:
    request = urllib.request.Request(uri, headers={"User-Agent": "ProductOS-Research/1.0"})
    with urllib.request.urlopen(request, timeout=15) as response:
        return response.read().decode("utf-8", errors="ignore")


def _load_raw_uri(uri: str) -> str:
    parsed = urlparse(uri)
    if parsed.scheme in {"http", "https", "file"}:
        request = urllib.request.Request(uri, headers={"User-Agent": "ProductOS-Research/1.0"})
        with urllib.request.urlopen(request, timeout=15) as response:
            return response.read().decode("utf-8", errors="ignore")
    path = Path(uri)
    if path.exists():
        return path.read_text(encoding="utf-8")
    raise FileNotFoundError(f"Unsupported research URI: {uri}")


def _normalize_sources(manifest_sources: list[dict[str, Any]], generated_at: str) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for source in manifest_sources:
        uri = source["uri"]
        details = _read_uri_details(uri)
        body = details["content"]
        detected_title = details["title"]
        title = source.get("title") or detected_title or _slug(uri)
        sentences = _split_sentences(body)
        published_at = source.get("published_at") or details.get("published_at")
        summary_hint = source.get("rationale") or details.get("summary_hint")
        normalized.append(
            {
                "source_id": source.get("source_id") or f"external_research_source_{_slug(title)}",
                "uri": uri,
                "source_type": source["source_type"],
                "question_id": source.get("question_id"),
                "title": title,
                "summary": _clip(summary_hint or " ".join(sentences[:2]) or body, 280),
                "sentences": sentences,
                "published_at": published_at,
                "freshness_status": _freshness_label(published_at, generated_at),
            }
        )
    return normalized


def _source_ids(sources: list[dict[str, Any]]) -> list[str]:
    return [item.get("source_note_card_id") or item["source_id"] for item in sources]


def _source_note_card_source_type(source_type: str) -> str:
    return {
        "customer_evidence": "interview",
        "operator_interview": "interview",
        "competitor_research": "competitor_site",
        "market_validation": "market_report",
        "security_review": "consultant_report",
    }.get(source_type, "other")


def _source_note_card_confidence(source: dict[str, Any]) -> str:
    freshness = source.get("freshness_status", "usable_with_review")
    if freshness == "fresh":
        return "high"
    if freshness == "usable_with_review":
        return "moderate"
    return "low"


def _source_note_card_tags(source: dict[str, Any], research_brief: dict[str, Any]) -> list[str]:
    tags = [
        source.get("source_type", "other"),
        source.get("freshness_status", "usable_with_review"),
    ]
    if source.get("question_id"):
        tags.append(source["question_id"])
    tags.extend(ref["entity_id"] for ref in research_brief.get("target_segment_refs", [])[:1])
    tags.extend(ref["entity_id"] for ref in research_brief.get("target_persona_refs", [])[:1])
    return list(dict.fromkeys(tag for tag in tags if isinstance(tag, str) and tag.strip()))


def _fallback_normalized_sources(
    *,
    problem_brief: dict[str, Any] | None,
    research_brief: dict[str, Any],
    generated_at: str,
) -> list[dict[str, Any]]:
    artifact_id = (
        problem_brief.get("problem_brief_id")
        if problem_brief is not None and isinstance(problem_brief.get("problem_brief_id"), str)
        else research_brief["research_brief_id"]
    )
    artifact_title = (
        problem_brief.get("title")
        if problem_brief is not None and isinstance(problem_brief.get("title"), str)
        else research_brief["title"]
    )
    summary = (
        problem_brief.get("problem_summary")
        if problem_brief is not None and isinstance(problem_brief.get("problem_summary"), str)
        else research_brief["summary"]
    )
    strategic_lines = [
        item
        for item in research_brief.get("strategic_implications", [])
        if isinstance(item, str) and item.strip()
    ]
    return [
        {
            "source_id": artifact_id,
            "uri": f"artifact://{artifact_id}",
            "source_type": "market_validation",
            "question_id": (research_brief.get("external_research_questions") or [{}])[0].get("question_id"),
            "title": artifact_title,
            "summary": summary,
            "sentences": [summary, *strategic_lines[:2]],
            "published_at": generated_at,
            "freshness_status": "fresh",
        }
    ]


def build_discovery_to_research_handoff(
    *,
    workspace_id: str,
    generated_at: str,
    strategy_context_brief: dict[str, Any],
    product_vision_brief: dict[str, Any],
    strategy_option_set: dict[str, Any] | None,
    market_strategy_brief: dict[str, Any],
    problem_brief: dict[str, Any],
    concept_brief: dict[str, Any],
    research_brief: dict[str, Any],
) -> dict[str, Any]:
    pending_questions = [
        item["question"]
        for item in research_brief.get("external_research_questions", [])
        if isinstance(item.get("question"), str)
    ]
    if not pending_questions:
        pending_questions = list(research_brief.get("known_gaps", []))
    key_points = [
        problem_brief.get("problem_summary", ""),
        problem_brief.get("why_this_problem_now", ""),
        market_strategy_brief.get("proof_requirements", [""])[0],
        (
            next(
                (
                    option["option_thesis"]
                    for option in strategy_option_set.get("options", [])
                    if option.get("option_id") == strategy_option_set.get("recommended_option_id")
                ),
                "",
            )
            if strategy_option_set is not None
            else ""
        ),
        concept_brief.get("hypothesis", ""),
    ]
    artifact_specs = [
        ("strategy_context_brief", strategy_context_brief["strategy_context_brief_id"], "artifacts/strategy_context_brief.json"),
        ("product_vision_brief", product_vision_brief["product_vision_brief_id"], "artifacts/product_vision_brief.json"),
        (
            "strategy_option_set",
            strategy_option_set["strategy_option_set_id"],
            "artifacts/strategy_option_set.json",
        )
        if strategy_option_set is not None
        else None,
        ("market_strategy_brief", market_strategy_brief["market_strategy_brief_id"], "artifacts/market_strategy_brief.json"),
        ("problem_brief", problem_brief["problem_brief_id"], "artifacts/problem_brief.json"),
        ("concept_brief", concept_brief["concept_brief_id"], "artifacts/concept_brief.json"),
    ]
    return {
        "schema_version": "1.0.0",
        "handoff_id": f"handoff_discovery_to_research_{workspace_id}",
        "workspace_id": workspace_id,
        "source_workflow_id": "wf_mission_to_strategy_spine",
        "target_workflow_id": "wf_research_command_center",
        "handoff_type": "workflow_to_workflow",
        "status": "ready",
        "artifact_refs": [
            {
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "path": path,
            }
            for item in artifact_specs
            if item is not None
            for artifact_type, artifact_id, path in [item]
        ],
        "summary": (
            f"Discovery signals suggest ProductOS should run bounded research on '{problem_brief['title']}' before the next prioritization and validation move."
        ),
        "key_points": [item for item in key_points if isinstance(item, str) and item.strip()],
        "pending_questions": pending_questions[:5],
        "created_at": generated_at,
    }


def _build_source_note_cards(
    *,
    research_brief: dict[str, Any],
    normalized_sources: list[dict[str, Any]],
    generated_at: str,
) -> list[dict[str, Any]]:
    linked_entity_refs = list(
        dict.fromkeys(
            tuple(sorted(ref.items()))
            for ref in [
                *research_brief.get("target_segment_refs", []),
                *research_brief.get("target_persona_refs", []),
                *research_brief.get("linked_entity_refs", []),
            ]
            if isinstance(ref, dict) and ref.get("entity_type") and ref.get("entity_id")
        )
    )
    normalized_linked_refs = [dict(items) for items in linked_entity_refs]
    note_cards: list[dict[str, Any]] = []
    for source in normalized_sources:
        sentences = source.get("sentences", [])
        claim = sentences[0] if sentences else source["summary"]
        implication = (
            sentences[1]
            if len(sentences) > 1
            else f"This source should be reused when validating {research_brief['summary']}"
        )
        source_metadata = {
            "source_url": source["uri"],
            "published_at": source.get("published_at"),
            "retrieved_at": generated_at,
            "source_slice_ref": source.get("question_id") or source["source_id"],
            "dedupe_key": _slug(source["uri"]),
            "credibility_tier": (
                "primary"
                if source["source_type"] in {"customer_evidence", "operator_interview"}
                else "secondary"
            ),
        }
        note_cards.append(
            {
                "schema_version": "1.0.0",
                "source_note_card_id": f"source_note_card_{_slug(source['source_id'])}",
                "workspace_id": research_brief["workspace_id"],
                "source_type": _source_note_card_source_type(source["source_type"]),
                "source_ref": source["source_id"],
                "title": source["title"],
                "claim": _clip(claim, 220),
                "source_snippet": _clip(" ".join(sentences[:2]) or source["summary"], 220),
                "implication": _clip(implication, 220),
                "confidence": _source_note_card_confidence(source),
                "freshness_status": source.get("freshness_status", "usable_with_review"),
                "unknowns": [
                    question["question"]
                    for question in research_brief.get("external_research_questions", [])[:2]
                    if isinstance(question.get("question"), str)
                ],
                "followup_questions": [
                    question["question"]
                    for question in research_brief.get("external_research_questions", [])[:3]
                    if isinstance(question.get("question"), str)
                ],
                "source_metadata": {key: value for key, value in source_metadata.items() if value is not None},
                "dedupe_key": _slug(source["uri"]),
                "linked_entity_refs": normalized_linked_refs,
                "tags": _source_note_card_tags(source, research_brief),
                "created_at": generated_at,
            }
        )
    return note_cards


def _attach_source_note_card_ids(
    normalized_sources: list[dict[str, Any]],
    source_note_cards: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_source_ref = {
        card["source_ref"]: card["source_note_card_id"]
        for card in source_note_cards
    }
    annotated: list[dict[str, Any]] = []
    for source in normalized_sources:
        updated = dict(source)
        updated["source_note_card_id"] = by_source_ref.get(source["source_id"], source["source_id"])
        annotated.append(updated)
    return annotated


def _build_research_notebook(
    *,
    research_brief: dict[str, Any],
    source_note_cards: list[dict[str, Any]],
    normalized_sources: list[dict[str, Any]],
    generated_at: str,
) -> dict[str, Any]:
    ordered_sections = ["research objective", "selected evidence", "customer pain signals", "competitive posture", "proof gaps"]
    if any(item["source_type"] == "customer_evidence" for item in normalized_sources):
        ordered_sections.append("voice of customer")
    return {
        "schema_version": "1.0.0",
        "research_notebook_id": f"research_notebook_{research_brief['workspace_id']}",
        "workspace_id": research_brief["workspace_id"],
        "title": f"Research notebook: {research_brief['title'].replace('Research Brief: ', '')}",
        "research_question": research_brief["research_question"],
        "source_note_card_ids": [item["source_note_card_id"] for item in source_note_cards],
        "synthesis_hypothesis": research_brief["summary"],
        "ordered_sections": ordered_sections,
        "open_questions": [
            item["question"]
            for item in research_brief.get("external_research_questions", [])[:5]
            if isinstance(item.get("question"), str)
        ],
        "created_at": generated_at,
    }


def _source_note_card_file_map(source_note_cards: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        f"{item['source_note_card_id']}.json": item
        for item in source_note_cards
    }


def _contains_any(text: str, phrases: list[str]) -> bool:
    return any(phrase in text for phrase in phrases)


def _detect_external_contradictions(normalized_sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    topic_definitions = {
        "switching_friction": {
            "high": ["switching friction", "vendor familiarity", "slows switching", "barrier", "switching decisions"],
            "low": ["low friction", "easy switching", "minimal switching cost", "quick adoption"],
            "statement": "External sources disagree on switching friction and buyer willingness to change workflows.",
        },
        "proof_posture": {
            "high": ["measurable rollout proof", "auditability", "explicit workflow controls", "visible governance controls", "approval boundaries"],
            "low": ["proof boundaries", "thin", "vague", "unclear", "missing proof"],
            "statement": "External sources disagree on how strong or weak the current proof and governance posture is.",
        },
        "workflow_burden": {
            "high": ["manual follow-up", "hours every week", "manual reconstruction", "handoff loops", "manual"],
            "low": ["fully automated", "no manual work", "hands-free", "automated handoffs"],
            "statement": "External sources disagree on how much manual workflow burden still exists.",
        },
    }
    contradictions: list[dict[str, Any]] = []
    for topic, definition in topic_definitions.items():
        high_sources = []
        low_sources = []
        for source in normalized_sources:
            haystack = " ".join([source["title"], source["summary"]] + source.get("sentences", [])[:2]).lower()
            if _contains_any(haystack, definition["high"]):
                high_sources.append(source)
            if _contains_any(haystack, definition["low"]):
                low_sources.append(source)
        if not high_sources or not low_sources:
            continue
        source_ids = list(dict.fromkeys(_source_ids(high_sources) + _source_ids(low_sources)))
        question_ids = list(
            dict.fromkeys(
                [item["question_id"] for item in high_sources + low_sources if item.get("question_id")]
            )
        )
        contradictions.append(
            {
                "contradiction_id": f"external_contradiction_{topic}",
                "topic": topic,
                "severity": "high" if len(source_ids) >= 3 else "moderate",
                "statement": definition["statement"],
                "question_ids": question_ids,
                "source_ids": source_ids,
            }
        )
    return contradictions


def _build_external_research_review(
    workspace_id: str,
    normalized_sources: list[dict[str, Any]],
    generated_at: str,
) -> dict[str, Any]:
    contradiction_items = _detect_external_contradictions(normalized_sources)
    review_items = [item["statement"] for item in contradiction_items]
    if not normalized_sources:
        review_items.append("No accepted external sources were available for contradiction review.")
    return {
        "schema_version": "1.0.0",
        "external_research_review_id": f"external_research_review_{workspace_id}",
        "workspace_id": workspace_id,
        "review_status": "review_required" if contradiction_items else "clear",
        "accepted_source_ids": _source_ids(normalized_sources),
        "contradiction_items": contradiction_items,
        "review_items": review_items,
        "recommendation": "pm_review_required" if contradiction_items else "continue_with_refresh",
        "created_at": generated_at,
    }


def _target_segment_name(research_brief: dict[str, Any]) -> str:
    refs = research_brief.get("target_segment_refs", [])
    if refs:
        return refs[0]["entity_id"].replace("_", " ")
    return "priority segment"


def _source_type_to_mix(source_type: str) -> str:
    return {
        "customer_evidence": "research",
        "operator_interview": "interviews",
        "competitor_research": "research",
        "market_validation": "research",
        "security_review": "research",
    }.get(source_type, "other")


def _brief_title(value: str) -> str:
    for prefix in ("Research Brief: ", "Problem Brief: "):
        if value.startswith(prefix):
            return value[len(prefix):]
    return value


def _source_type_guidance(source_type: str) -> list[str]:
    return {
        "customer_evidence": [
            "Use first-hand operator or buyer evidence where the pain point is described directly.",
            "Prefer a source newer than 90 days when using it for an external-facing release claim.",
        ],
        "operator_interview": [
            "Capture the exact workflow bottleneck, queue behavior, and approval boundary described by the operator.",
            "Record enough context to distinguish raw anecdote from a recurring operating pattern.",
        ],
        "competitor_research": [
            "Prefer sources that state the competitor narrative, target buyer, and proof or pricing posture directly.",
            "Use a fresh source when possible so the comparison reflects the current launch narrative.",
        ],
        "market_validation": [
            "Look for current signals about buyer expectations, switching friction, and rollout proof requirements.",
            "Use sources that help quantify whether the wedge feels urgent and credible.",
        ],
        "security_review": [
            "Prefer authoritative sources that clarify governance, compliance, or auditability requirements.",
            "Capture what would block adoption if not addressed before launch.",
        ],
    }.get(source_type, ["Collect a source that directly answers the question with enough evidence to support PM review."])


def _question_search_queries(research_brief: dict[str, Any], question: dict[str, Any]) -> list[str]:
    segment = _target_segment_name(research_brief)
    source_type = question["recommended_source_type"].replace("_", " ")
    base_terms = [question["question"].rstrip("?")]
    if segment != "priority segment":
        base_terms.append(f"{segment} {question['question'].rstrip('?')}")
    base_terms.append(f"{segment} {source_type} {research_brief['summary']}")
    return list(dict.fromkeys(_clip(term, 180) for term in base_terms if term.strip()))


def _fallback_external_questions(research_brief: dict[str, Any]) -> list[dict[str, Any]]:
    fallback_questions: list[dict[str, Any]] = []
    known_gaps = research_brief.get("known_gaps", [])
    for index, gap in enumerate(known_gaps[:3], start=1):
        fallback_questions.append(
            {
                "question_id": f"derived_gap_{index}",
                "question": f"What external evidence can validate or challenge this gap: {gap}",
                "why_it_matters": gap,
                "recommended_source_type": "market_validation",
                "priority": "medium",
            }
        )
    if fallback_questions:
        return fallback_questions

    return [
        {
            "question_id": "derived_priority_1",
            "question": f"What external evidence best validates the wedge in {research_brief['title']}?",
            "why_it_matters": "The workspace needs at least one fresh external source before broad customer-facing claims are made.",
            "recommended_source_type": "market_validation",
            "priority": "high",
        }
    ]


def _search_provider_url(query: str) -> str:
    template = getenv("PRODUCTOS_RESEARCH_SEARCH_URL_TEMPLATE")
    if template:
        return template.format(query=quote_plus(query))
    return f"https://duckduckgo.com/html/?q={quote_plus(query)}"


def _search_provider_chain(search_provider_chain: str | None) -> list[str]:
    chain_value = (
        search_provider_chain
        or getenv("PRODUCTOS_RESEARCH_SEARCH_PROVIDER_CHAIN")
        or "duckduckgo_html"
    )
    providers = [item.strip() for item in chain_value.split(",") if item.strip()]
    return providers or ["duckduckgo_html"]


def _result_record(title: str, uri: str, snippet: str, query: str) -> dict[str, str] | None:
    normalized_uri = _direct_result_uri(unescape(uri))
    normalized_title = _strip_html(title)
    normalized_snippet = _clip(
        _strip_html(snippet) if snippet else "Search result discovered for bounded external research.",
        200,
    )
    if not normalized_title or not normalized_uri:
        return None
    return {
        "title": normalized_title,
        "uri": normalized_uri,
        "snippet": normalized_snippet,
        "search_query": query,
        "provider": "unknown",
    }


def _parse_search_results_from_json(raw_text: str, *, query: str, max_results: int) -> list[dict[str, str]]:
    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError:
        return []

    candidates = payload.get("results") or payload.get("items") or payload.get("organic_results") or []
    if not isinstance(candidates, list):
        return []

    results: list[dict[str, str]] = []
    seen_uris: set[str] = set()
    for item in candidates:
        if not isinstance(item, dict):
            continue
        record = _result_record(
            item.get("title") or item.get("name") or "",
            item.get("url") or item.get("link") or item.get("uri") or "",
            item.get("snippet") or item.get("description") or item.get("summary") or "",
            query,
        )
        if record is None or record["uri"] in seen_uris:
            continue
        seen_uris.add(record["uri"])
        results.append(record)
        if len(results) >= max_results:
            break
    return results


def _xml_local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def _parse_search_results_from_feed(raw_text: str, *, query: str, max_results: int) -> list[dict[str, str]]:
    try:
        root = ET.fromstring(raw_text)
    except ET.ParseError:
        return []

    results: list[dict[str, str]] = []
    seen_uris: set[str] = set()
    for element in root.iter():
        local_name = _xml_local_name(element.tag)
        if local_name not in {"item", "entry"}:
            continue

        title = ""
        uri = ""
        snippet = ""
        for child in list(element):
            child_name = _xml_local_name(child.tag)
            child_text = (child.text or "").strip()
            if child_name == "title" and child_text:
                title = child_text
            elif child_name == "link":
                uri = child.attrib.get("href") or child_text or uri
            elif child_name in {"description", "summary", "content", "content:encoded"} and child_text and not snippet:
                snippet = child_text

        record = _result_record(title, uri, snippet, query)
        if record is None or record["uri"] in seen_uris:
            continue
        seen_uris.add(record["uri"])
        results.append(record)
        if len(results) >= max_results:
            break
    return results


def _parse_search_results_from_blocks(raw_html: str, *, query: str, max_results: int) -> list[dict[str, str]]:
    block_patterns = [
        r'(?is)<li[^>]+class="[^"]*b_algo[^"]*"[^>]*>(.*?)</li>',
        r'(?is)<div[^>]+class="[^"]*(?:search-result|search_result|result-item|result_item|result)\b[^"]*"[^>]*>(.*?)</div>',
        r'(?is)<article[^>]*>(.*?)</article>',
    ]
    results: list[dict[str, str]] = []
    seen_uris: set[str] = set()
    for pattern in block_patterns:
        for match in re.finditer(pattern, raw_html):
            block = match.group(1)
            link_match = re.search(r'(?is)<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', block)
            if not link_match:
                continue
            snippet_match = (
                re.search(r'(?is)(?:result__snippet|b_caption|snippet|description)[^>]*>(.*?)</', block)
                or re.search(r'(?is)<p[^>]*>(.*?)</p>', block)
                or re.search(r'(?is)<span[^>]*>(.*?)</span>', block)
            )
            record = _result_record(
                link_match.group(2),
                link_match.group(1),
                snippet_match.group(1) if snippet_match else "",
                query,
            )
            if record is None or record["uri"] in seen_uris:
                continue
            seen_uris.add(record["uri"])
            results.append(record)
            if len(results) >= max_results:
                return results
    return results


def _parse_search_results(raw_html: str, *, query: str, max_results: int) -> list[dict[str, str]]:
    stripped = raw_html.lstrip()
    if stripped.startswith("{") or stripped.startswith("["):
        results = _parse_search_results_from_json(raw_html, query=query, max_results=max_results)
        if results:
            return results
    if stripped.startswith("<rss") or stripped.startswith("<feed") or stripped.startswith("<?xml"):
        results = _parse_search_results_from_feed(raw_html, query=query, max_results=max_results)
        if results:
            return results

    matches = list(
        re.finditer(
            r'(?is)<a[^>]+class="[^"]*result__a[^"]*"[^>]+href="([^"]+)"[^>]*>(.*?)</a>(.*?)(?=<a[^>]+class="[^"]*result__a[^"]*"|$)',
            raw_html,
        )
    )
    results: list[dict[str, str]] = []
    seen_uris: set[str] = set()
    for match in matches:
        snippet_match = re.search(r'(?is)result__snippet[^>]*>(.*?)</', match.group(3))
        record = _result_record(
            match.group(2),
            match.group(1),
            snippet_match.group(1) if snippet_match else "",
            query,
        )
        if record is None or record["uri"] in seen_uris:
            continue
        seen_uris.add(record["uri"])
        results.append(record)
        if len(results) >= max_results:
            return results

    block_results = _parse_search_results_from_blocks(raw_html, query=query, max_results=max_results)
    if block_results:
        return block_results
    return results


def _direct_result_uri(uri: str) -> str:
    parsed = urlparse(uri)
    if parsed.netloc.endswith("duckduckgo.com") and parsed.path.startswith("/l/"):
        uddg = parse_qs(parsed.query).get("uddg")
        if uddg:
            return unquote(uddg[0])
    if uri.startswith("//"):
        return f"https:{uri}"
    return uri


def _domain_from_uri(uri: str) -> str:
    parsed = urlparse(uri)
    domain = parsed.netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def _candidate_keyword_tokens(text: str) -> set[str]:
    stop_words = {
        "what",
        "how",
        "this",
        "that",
        "with",
        "from",
        "they",
        "their",
        "where",
        "which",
        "before",
        "after",
        "still",
        "into",
        "when",
        "have",
        "needs",
        "need",
        "right",
        "current",
        "evidence",
        "source",
        "sources",
        "buyer",
        "buyers",
    }
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) >= 4 and token not in stop_words
    }


def _domain_quality_adjustment(question: dict[str, Any], domain: str, haystack: str) -> tuple[int, str | None]:
    if not domain:
        return 0, None

    source_type = question["recommended_source_type"]
    score = 0
    reason: str | None = None

    if domain.endswith(".gov") or domain.endswith(".edu"):
        score += 18
        reason = f"institutional domain: {domain}"
    elif any(token in domain for token in ("docs.", "support.", "help.", "developer.", "trust.", "security.")):
        score += 12
        reason = f"official docs or trust domain: {domain}"
    elif any(token in domain for token in ("github.com", "owsap.org", "owasp.org", "nist.gov", "cisa.gov")):
        score += 14
        reason = f"reference domain: {domain}"

    if source_type == "competitor_research" and any(token in haystack for token in ("pricing", "compare", "security", "docs", "product", "platform")):
        score += 8
        reason = reason or f"competitor-style product page: {domain}"
    elif source_type in {"market_validation", "security_review"} and any(
        token in haystack for token in ("research", "benchmark", "security", "compliance", "controls", "trust")
    ):
        score += 8
        reason = reason or f"validation-oriented domain: {domain}"
    elif source_type in {"customer_evidence", "operator_interview"} and any(
        token in haystack for token in ("customer", "case-study", "case_study", "operator", "community")
    ):
        score += 6
        reason = reason or f"operator or customer evidence domain: {domain}"

    low_signal_domains = ("facebook.com", "instagram.com", "x.com", "twitter.com", "pinterest.com", "linkedin.com")
    if domain.endswith(low_signal_domains):
        score -= 10
        reason = f"low-signal social domain: {domain}"

    return score, reason


def _source_type_cues(source_type: str) -> set[str]:
    return {
        "competitor_research": {"competitor", "vendor", "pricing", "product", "platform", "automation", "workflow"},
        "market_validation": {"market", "buyers", "proof", "governance", "controls", "auditability", "validation"},
        "security_review": {"security", "trust", "compliance", "controls", "approval", "auditability", "governance"},
        "customer_evidence": {"customer", "operator", "manual", "queue", "handoff", "workflow", "follow"},
        "operator_interview": {"operator", "manual", "queue", "handoff", "burden", "workflow", "interview"},
    }.get(source_type, set())


def _sentence_overlap_score(question_terms: set[str], source_type: str, sentence: str) -> int:
    sentence_terms = _candidate_keyword_tokens(sentence)
    score = len(question_terms & sentence_terms) * 6
    score += len(_source_type_cues(source_type) & sentence_terms) * 4
    if 8 <= len(sentence.split()) <= 40:
        score += 4
    return score


def _is_question_echo(question: dict[str, Any], sentence: str) -> bool:
    question_text = " ".join(question["question"].lower().split())
    sentence_text = " ".join(sentence.lower().split())
    if not question_text or not sentence_text:
        return False
    if sentence_text == question_text:
        return True
    question_terms = _candidate_keyword_tokens(question_text)
    sentence_terms = _candidate_keyword_tokens(sentence_text)
    if not question_terms:
        return False
    overlap_ratio = len(question_terms & sentence_terms) / len(question_terms)
    return overlap_ratio >= 0.8 and len(sentence_terms) <= len(question_terms) + 3


def _best_evidence_excerpt(question: dict[str, Any], content: str, fallback: str) -> str:
    sentences = _split_sentences(content)
    if not sentences:
        return _clip(fallback or content, 220)

    question_terms = _candidate_keyword_tokens(question["question"])
    scored_sentences = [
        (
            sentence,
            _sentence_overlap_score(question_terms, question["recommended_source_type"], sentence),
            _is_question_echo(question, sentence),
        )
        for sentence in sentences
    ]
    non_echo_ranked = sorted(
        [item for item in scored_sentences if not item[2] and item[1] > 0],
        key=lambda item: item[1],
        reverse=True,
    )
    if non_echo_ranked:
        best = non_echo_ranked[0][0]
        return _clip(best, 220)

    ranked = sorted(
        scored_sentences,
        key=lambda item: item[1] - (18 if item[2] else 0),
        reverse=True,
    )
    best = ranked[0][0]
    if _sentence_overlap_score(question_terms, question["recommended_source_type"], best) <= 0:
        best = sentences[0]
    return _clip(best, 220)


def _score_candidate_result(question: dict[str, Any], result: dict[str, str], query: str) -> tuple[int, str]:
    haystack = " ".join([result["title"], result["snippet"], result["uri"]]).lower()
    domain = _domain_from_uri(result["uri"])
    query_terms = _candidate_keyword_tokens(query)
    question_terms = _candidate_keyword_tokens(question["question"])
    matched_query_terms = sorted(term for term in query_terms if term in haystack)
    matched_question_terms = sorted(term for term in question_terms if term in haystack)
    score = 10
    score += min(25, len(matched_query_terms) * 5)
    score += min(20, len(matched_question_terms) * 4)
    if domain:
        score += 5
    domain_adjustment, domain_reason = _domain_quality_adjustment(question, domain, haystack)
    score += domain_adjustment
    if question["recommended_source_type"] == "competitor_research" and any(
        token in haystack for token in ("competitor", "pricing", "vendor", "overview")
    ):
        score += 12
    if question["recommended_source_type"] in {"market_validation", "security_review"} and any(
        token in haystack for token in ("proof", "audit", "security", "governance", "market")
    ):
        score += 12
    if question["recommended_source_type"] in {"customer_evidence", "operator_interview"} and any(
        token in haystack for token in ("operator", "customer", "manual", "queue", "workflow")
    ):
        score += 12
    reason_bits = []
    if matched_query_terms:
        reason_bits.append(f"query match: {', '.join(matched_query_terms[:3])}")
    if matched_question_terms:
        reason_bits.append(f"question match: {', '.join(matched_question_terms[:3])}")
    if domain:
        reason_bits.append(f"domain: {domain}")
    if domain_reason:
        reason_bits.append(domain_reason)
    if not reason_bits:
        reason_bits.append("selected as the strongest available bounded search match")
    return score, "; ".join(reason_bits)


def _score_fetched_source_quality(
    question: dict[str, Any],
    *,
    candidate: dict[str, Any],
    content: str,
    detected_title: str,
    detected_published_at: str,
    generated_at: str,
) -> tuple[int, str, str]:
    haystack = " ".join([candidate.get("title", ""), detected_title, content]).lower()
    question_terms = _candidate_keyword_tokens(question["question"])
    matched_question_terms = sorted(term for term in question_terms if term in haystack)
    score = candidate.get("quality_score", 0)
    content_words = len(content.split())
    evidence_excerpt = _best_evidence_excerpt(question, content, candidate.get("snippet", ""))
    freshness_status = _freshness_label(detected_published_at or candidate.get("published_at"), generated_at)
    if content_words >= 40:
        score += 20
    elif content_words >= 20:
        score += 10
    else:
        score -= 10
    score += min(24, len(matched_question_terms) * 6)
    excerpt_score = _sentence_overlap_score(question_terms, question["recommended_source_type"], evidence_excerpt)
    score += min(18, excerpt_score)
    if question["recommended_source_type"] == "competitor_research" and any(
        token in haystack for token in ("competitor", "vendor", "pricing", "automation", "workflow")
    ):
        score += 10
    if question["recommended_source_type"] in {"market_validation", "security_review"} and any(
        token in haystack for token in ("proof", "market", "auditability", "governance", "security", "controls")
    ):
        score += 10
    if question["recommended_source_type"] in {"customer_evidence", "operator_interview"} and any(
        token in haystack for token in ("operator", "customer", "manual", "queue", "follow", "workflow")
    ):
        score += 10
    if candidate.get("freshness_expectation") == "fresh":
        if freshness_status == "fresh":
            score += 10
        elif freshness_status == "stale":
            score -= 18
    elif freshness_status == "stale":
        score -= 6

    if content_words < 12:
        status = "rejected"
        reason = "Fetched source content is too thin to support a governed external claim."
    elif len(matched_question_terms) < 2:
        status = "review"
        reason = f"Fetched content is present, but direct overlap with the research question is still limited. Best evidence: {evidence_excerpt}"
    else:
        status = "accepted"
        reason = f"Fetched content has enough substance and direct question overlap to support bounded research refresh. Best evidence: {evidence_excerpt}"

    if status == "review" and score >= 45:
        status = "accepted"
        reason = f"Fetched content is compact but strong enough overall to support bounded refresh. Best evidence: {evidence_excerpt}"
    if status == "accepted" and score < 40:
        status = "review"
        reason = f"Fetched content is relevant but still too weak for automatic acceptance. Best evidence: {evidence_excerpt}"
    if status == "accepted" and candidate.get("freshness_expectation") == "fresh" and freshness_status == "stale":
        status = "review"
        reason = f"Fetched content is otherwise relevant, but the detected publication date is stale for a fresh-evidence question. Best evidence: {evidence_excerpt}"
    return score, status, reason


def _discover_search_results(
    query: str,
    *,
    provider: str,
    max_results: int,
    fixture_dir: Path | None = None,
) -> list[dict[str, str]]:
    html_path: Path | None = None
    if fixture_dir is not None:
        provider_fixture_dir = fixture_dir / provider if (fixture_dir / provider).is_dir() else fixture_dir
        query_specific = provider_fixture_dir / f"{_slug(query)}.html"
        default_html = provider_fixture_dir / "default.html"
        if query_specific.exists():
            html_path = query_specific
        elif default_html.exists():
            html_path = default_html
    if html_path is not None:
        raw_html = html_path.read_text(encoding="utf-8")
    else:
        if provider == "duckduckgo_html":
            raw_html = _load_html(_search_provider_url(query))
        elif provider == "template":
            raw_html = _load_html(_search_provider_url(query))
        else:
            return []
    results = _parse_search_results(raw_html, query=query, max_results=max_results)
    for item in results:
        item["provider"] = provider
    return results


def _synthesize_research_brief_from_problem_brief(problem_brief: dict[str, Any], artifact_id: str, generated_at: str) -> dict[str, Any]:
    problem_summary = problem_brief.get("problem_summary", problem_brief.get("title", ""))
    strategic_implications = []
    for field in ("strategic_fit_summary", "why_this_problem_now", "why_this_problem_is_important"):
        value = problem_brief.get(field)
        if isinstance(value, str) and value.strip():
            strategic_implications.append(value.strip())
    if not strategic_implications:
        strategic_implications = [
            "External evidence is still needed to prove the urgency and buyer pull behind this problem framing."
        ]

    posture = problem_brief.get("posture_alignment", "targeted")
    return {
        "schema_version": "1.0.0",
        "research_brief_id": f"research_brief_{problem_brief['workspace_id']}_derived",
        "workspace_id": problem_brief["workspace_id"],
        "title": f"Research Brief: {problem_brief['title'].replace('Problem Brief: ', '')}",
        "research_question": f"What external evidence should ProductOS gather to validate this problem framing: {problem_summary}",
        "summary": problem_summary,
        "strategic_implications": strategic_implications,
        "source_note_card_ids": [artifact_id],
        "target_segment_refs": problem_brief.get(
            "target_segment_refs",
            [{"entity_type": "segment", "entity_id": "segment_priority_buyers"}],
        ),
        "target_persona_refs": problem_brief.get(
            "target_persona_refs",
            [{"entity_type": "persona", "entity_id": "persona_product_manager"}],
        ),
        "linked_entity_refs": problem_brief.get("linked_entity_refs", []),
        "insights": [
            {
                "insight_id": "derived_problem_summary",
                "statement": problem_summary,
                "evidence_strength": "moderate",
                "claim_mode": "inferred",
                "next_validation_step": "Gather fresh external proof that quantifies the urgency and repeatability of this problem.",
                "supporting_source_note_card_ids": [artifact_id],
            },
            {
                "insight_id": "derived_posture_alignment",
                "statement": (
                    f"The current posture is {posture}, but it still needs external proof before release-facing claims are expanded."
                ),
                "evidence_strength": "weak",
                "claim_mode": "inferred",
                "next_validation_step": "Compare current alternatives and buyer expectations to confirm the posture is still credible.",
                "supporting_source_note_card_ids": [artifact_id],
            },
        ],
        "contradictions": [],
        "known_gaps": [
            "External buyer evidence is still needed to confirm the urgency of this problem outside the workspace.",
            "Competitor or category proof has not yet been refreshed for the current claim set.",
        ],
        "external_research_questions": [
            {
                "question_id": "derived_market_validation",
                "question": "What fresh external evidence shows this problem is urgent for the target buyer right now?",
                "why_it_matters": "ProductOS should not make broad release claims until urgency is visible outside the internal workspace.",
                "recommended_source_type": "market_validation",
                "priority": "high",
            },
            {
                "question_id": "derived_competitor_research",
                "question": "How do current alternatives frame this problem, and where are their proof boundaries weaker?",
                "why_it_matters": "External release positioning needs a grounded comparison instead of a generic platform narrative.",
                "recommended_source_type": "competitor_research",
                "priority": "high",
            },
            {
                "question_id": "derived_customer_evidence",
                "question": "What direct operator or PM evidence quantifies the current manual reconstruction burden?",
                "why_it_matters": "First-hand customer evidence is required before claiming that the workflow pain is frequent and severe.",
                "recommended_source_type": "customer_evidence",
                "priority": "medium",
            },
        ],
        "synthesis_provenance": [f"Derived from {artifact_id} because no persisted research_brief.json was present."],
        "recommendation": "gather_more_research",
        "created_at": generated_at,
    }


def _load_workspace_research_brief(workspace_dir: Path, generated_at: str) -> dict[str, Any]:
    artifacts_dir = workspace_dir / "artifacts"
    research_brief_path = artifacts_dir / "research_brief.json"
    if research_brief_path.exists():
        return _load_json(research_brief_path)

    fallback_paths = [
        (artifacts_dir / "problem_brief.json", "problem_brief"),
        (workspace_dir / "outputs" / "discover" / "discover_problem_brief.json", "discover_problem_brief"),
    ]
    for path, artifact_id in fallback_paths:
        if path.exists():
            return _synthesize_research_brief_from_problem_brief(_load_json(path), artifact_id, generated_at)

    example_path = artifacts_dir / "research_brief.example.json"
    if example_path.exists():
        return _load_json(example_path)

    raise FileNotFoundError(
        f"No research basis was found in {workspace_dir}. Expected research_brief.json, problem_brief.json, or discover_problem_brief.json."
    )


def _build_external_research_plan(research_brief: dict[str, Any], generated_at: str) -> dict[str, Any]:
    brief_title = _brief_title(research_brief["title"])
    questions = research_brief.get("external_research_questions") or _fallback_external_questions(research_brief)
    questions = _ensure_core_signal_lane_questions(research_brief, questions)
    planned_signal_lanes = _planned_signal_lane_ids(questions)
    prioritized_questions: list[dict[str, Any]] = []
    suggested_manifest_sources: list[dict[str, Any]] = []
    for question in questions:
        planned_question = {
            "question_id": question["question_id"],
            "question": question["question"],
            "why_it_matters": question["why_it_matters"],
            "recommended_source_type": question["recommended_source_type"],
            "priority": question["priority"],
            "search_queries": _question_search_queries(research_brief, question),
            "source_requirements": _source_type_guidance(question["recommended_source_type"]),
        }
        prioritized_questions.append(planned_question)
        suggested_manifest_sources.append(
            {
                "source_id": f"{question['question_id']}_{question['recommended_source_type']}",
                "question_id": question["question_id"],
                "source_type": question["recommended_source_type"],
                "title": f"Add source for {question['question_id']}",
                "uri": "",
                "rationale": question["why_it_matters"],
                "freshness_expectation": (
                    "usable_with_review"
                    if question["recommended_source_type"] == "competitor_research"
                    else "fresh"
                ),
            }
        )

    claims_needing_validation = [
        _clip(
            f"{insight['statement']} ({insight.get('claim_mode', 'observed')}, {insight['evidence_strength']} evidence)",
            180,
        )
        for insight in research_brief.get("insights", [])
        if insight.get("claim_mode") != "observed" or insight.get("evidence_strength") != "strong"
    ]
    if not claims_needing_validation:
        claims_needing_validation = [
            "The current workspace still needs at least one external source to support an external-facing claim set."
        ]

    return {
        "schema_version": "1.0.0",
        "external_research_plan_id": f"external_research_plan_{research_brief['workspace_id']}",
        "workspace_id": research_brief["workspace_id"],
        "title": f"External research plan: {brief_title}",
        "generated_from_artifact_id": research_brief["research_brief_id"],
        "research_objective": (
            f"Close the proof gaps in {brief_title} with bounded external evidence before release-facing claims are made."
        ),
        "prioritized_questions": prioritized_questions,
        "coverage_summary": {
            "known_gaps": research_brief.get("known_gaps", []),
            "claims_needing_validation": claims_needing_validation,
            "required_signal_lanes": _core_signal_lane_ids(),
            "planned_signal_lanes": planned_signal_lanes,
            "missing_signal_lanes": [
                lane_id for lane_id in _core_signal_lane_ids() if lane_id not in planned_signal_lanes
            ],
            "recommended_next_step": (
                "Fill the source manifest template with concrete sources, then run research-workspace to refresh governed external artifacts."
            ),
        },
        "suggested_manifest_sources": suggested_manifest_sources,
        "created_at": generated_at,
    }


def _write_research_plan_files(workspace_dir: Path, external_research_plan: dict[str, Any]) -> None:
    outputs_dir = workspace_dir / "outputs" / "research"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    questions_by_id = {
        item["question_id"]: item
        for item in external_research_plan.get("prioritized_questions", [])
    }

    manifest_template = {
        "sources": [
            {
                "source_id": item["source_id"],
                "uri": item["uri"],
                "source_type": item["source_type"],
                "title": item["title"],
                "published_at": "",
                "question_id": item["question_id"],
                "rationale": item["rationale"],
                "freshness_expectation": item["freshness_expectation"],
                "search_queries": questions_by_id.get(item["question_id"], {}).get("search_queries", []),
                "source_requirements": questions_by_id.get(item["question_id"], {}).get("source_requirements", []),
            }
            for item in external_research_plan.get("suggested_manifest_sources", [])
        ]
    }
    _write_json(outputs_dir / "external-research-manifest.template.json", manifest_template)

    docs_dir = workspace_dir / "docs" / "discovery"
    docs_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        external_research_plan["research_objective"],
        "",
        "## Prioritized Questions",
        "",
    ]
    for question in external_research_plan["prioritized_questions"]:
        lines.append(
            f"- `{question['priority']}` `{question['recommended_source_type']}` {question['question']}"
        )
        lines.append(f"  Why: {question['why_it_matters']}")
        lines.append(f"  Search: {question['search_queries'][0]}")
    lines.extend(["", "## Coverage Summary", ""])
    required_signal_lanes = external_research_plan["coverage_summary"].get("required_signal_lanes", [])
    planned_signal_lanes = external_research_plan["coverage_summary"].get("planned_signal_lanes", [])
    if required_signal_lanes:
        lines.append(
            "- Required signal lanes: "
            + ", ".join(f"`{_signal_lane_label(lane_id)}`" for lane_id in required_signal_lanes)
        )
    if planned_signal_lanes:
        lines.append(
            "- Planned signal lanes: "
            + ", ".join(f"`{_signal_lane_label(lane_id)}`" for lane_id in planned_signal_lanes)
        )
    for gap in external_research_plan["coverage_summary"]["known_gaps"] or ["No explicit known gaps recorded."]:
        lines.append(f"- Gap: {gap}")
    for claim in external_research_plan["coverage_summary"]["claims_needing_validation"][:3]:
        lines.append(f"- Validate: {claim}")
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            external_research_plan["coverage_summary"]["recommended_next_step"],
        ]
    )
    (docs_dir / "external-research-plan.md").write_text(
        render_governed_markdown(
            title="External Research Plan",
            body_lines=lines,
            version_number=1,
            status="review_needed",
            updated_at=external_research_plan["created_at"],
            updated_by="Research Agent",
            change_summary="Created the bounded external research plan from the current research brief and discovery packet.",
            source_artifact_ids=[external_research_plan["external_research_plan_id"]],
        ),
        encoding="utf-8",
    )


def _recommended_feed_title(source_type: str) -> str:
    return {
        "customer_evidence": "Customer and operator signal feed",
        "operator_interview": "Operator workflow interview feed",
        "competitor_research": "Competitor launch and docs feed",
        "market_validation": "Market validation and category feed",
        "security_review": "Security and governance feed",
    }.get(source_type, "External research feed")


def _build_external_research_feed_registry(
    external_research_plan: dict[str, Any],
    generated_at: str,
) -> dict[str, Any]:
    feeds: list[dict[str, Any]] = []
    questions_by_type: dict[str, list[str]] = {}
    for question in external_research_plan["prioritized_questions"]:
        questions_by_type.setdefault(question["recommended_source_type"], []).append(question["question_id"])
    for source_type, question_ids in questions_by_type.items():
        feeds.append(
            {
                "feed_id": f"feed_{source_type}",
                "title": _recommended_feed_title(source_type),
                "source_type": source_type,
                "uri": "",
                "trust_tier": "secondary" if source_type == "competitor_research" else "primary",
                "refresh_cadence": "weekly" if source_type in {"market_validation", "competitor_research"} else "manual",
                "question_ids": question_ids,
                "notes": "Add a trusted feed URL or local feed file that helps answer the mapped research questions.",
            }
        )
    return {
        "schema_version": "1.0.0",
        "external_research_feed_registry_id": f"external_research_feed_registry_{external_research_plan['workspace_id']}",
        "workspace_id": external_research_plan["workspace_id"],
        "title": f"External research feed registry: {external_research_plan['workspace_id']}",
        "feeds": feeds,
        "created_at": generated_at,
    }


def _write_research_feed_registry_files(workspace_dir: Path, feed_registry: dict[str, Any]) -> None:
    outputs_dir = workspace_dir / "outputs" / "research"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    _write_json(outputs_dir / "external-research-feed-registry.template.json", feed_registry)

    docs_dir = workspace_dir / "docs" / "discovery"
    docs_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "Curated feeds that can seed governed external source discovery before generic search is used.",
        "",
        "## Registered Feed Slots",
        "",
    ]
    for feed in feed_registry["feeds"]:
        lines.append(
            f"- `{feed.get('source_type', 'market_validation')}` `{feed.get('trust_tier', 'secondary')}` `{feed.get('refresh_cadence', 'manual')}` {feed.get('title', feed.get('feed_id', 'Untitled feed'))}"
        )
        lines.append(f"  Questions: {', '.join(feed.get('question_ids', [])) or 'none'}")
        if feed.get("health_status"):
            health_line = f"  Health: {feed['health_status']}"
            if feed.get("last_item_count") is not None:
                health_line += f" ({feed['last_item_count']} items)"
            lines.append(health_line)
        if feed.get("health_reason"):
            lines.append(f"  Reason: {feed['health_reason']}")
        if feed.get("cadence_status"):
            lines.append(f"  Cadence: {feed['cadence_status']}")
        if feed.get("cadence_reason"):
            lines.append(f"  Cadence reason: {feed['cadence_reason']}")
    (docs_dir / "external-research-feed-registry.md").write_text(
        render_governed_markdown(
            title="External Research Feed Registry",
            body_lines=lines,
            version_number=1,
            status="review_needed",
            updated_at=feed_registry["created_at"],
            updated_by="Research Agent",
            change_summary="Registered the current governed feed slots for bounded external research.",
            source_artifact_ids=[feed_registry["external_research_feed_registry_id"]],
        ),
        encoding="utf-8",
    )


def build_external_research_feed_registry_from_workspace(
    root_dir: Path | str,
    *,
    workspace_dir: Path | str,
    generated_at: str,
    persist: bool = True,
    research_brief_override: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    workspace = Path(workspace_dir).resolve()
    artifacts_dir = workspace / "artifacts"
    plan_path = artifacts_dir / "external_research_plan.json"
    if research_brief_override is None and plan_path.exists():
        external_research_plan = _load_json(plan_path)
    else:
        external_research_plan = build_external_research_plan_from_workspace(
            root_dir,
            workspace_dir=workspace,
            generated_at=generated_at,
            persist=persist,
        )["external_research_plan"]
    feed_registry = _build_external_research_feed_registry(external_research_plan, generated_at)
    bundle = {"external_research_feed_registry": feed_registry}
    if persist:
        manifest_path = workspace / "workspace_manifest.yaml"
        _write_json(artifacts_dir / "external_research_feed_registry.json", feed_registry)
        _append_manifest_artifact_path(manifest_path, "artifacts/external_research_feed_registry.json")
        _write_research_feed_registry_files(workspace, feed_registry)
    return bundle


def _load_feed_registry_payload(
    workspace_dir: Path,
    *,
    feed_registry_path: Path | str | None = None,
) -> tuple[dict[str, Any] | None, Path | None]:
    candidate_paths: list[Path] = []
    if feed_registry_path is not None:
        candidate_paths.append(Path(feed_registry_path).resolve())
    candidate_paths.append(workspace_dir / "artifacts" / "external_research_feed_registry.json")

    registry_path = next((path for path in candidate_paths if path.exists()), None)
    if registry_path is None:
        return None, None

    payload = _load_json(registry_path)
    if not isinstance(payload, dict):
        return None, registry_path
    return payload, registry_path


def _load_feed_registry(
    workspace_dir: Path,
    *,
    feed_registry_path: Path | str | None = None,
) -> list[dict[str, Any]]:
    payload, _ = _load_feed_registry_payload(workspace_dir, feed_registry_path=feed_registry_path)
    if payload is None:
        return []
    feeds = payload.get("feeds", [])
    return [item for item in feeds if isinstance(item, dict)]


def _question_matches_feed(question: dict[str, Any], feed: dict[str, Any]) -> bool:
    if feed.get("source_type") == question["recommended_source_type"]:
        return True
    source_types = feed.get("source_types")
    if isinstance(source_types, list) and question["recommended_source_type"] in source_types:
        return True
    return False


def _discover_feed_results(
    question: dict[str, Any],
    *,
    query: str,
    max_results: int,
    feeds: list[dict[str, Any]],
) -> tuple[list[dict[str, str]], dict[str, dict[str, Any]]]:
    results: list[dict[str, str]] = []
    seen_uris: set[str] = set()
    health_updates: dict[str, dict[str, Any]] = {}
    for feed in feeds:
        if not _question_matches_feed(question, feed):
            continue
        feed_id = feed.get("feed_id") or f"feed_{question['recommended_source_type']}"
        health = health_updates.setdefault(
            feed_id,
            {
                "matched_question_ids": set(),
                "result_count": 0,
                "error_messages": [],
                "configured": True,
            },
        )
        health["matched_question_ids"].add(question["question_id"])
        uri = feed.get("uri")
        if not uri:
            health["configured"] = False
            continue
        try:
            raw = _load_raw_uri(uri)
        except Exception as exc:
            health["error_messages"].append(str(exc))
            continue
        parsed_results = _parse_search_results(raw, query=query, max_results=max_results)
        health["result_count"] += len(parsed_results)
        for item in parsed_results:
            if item["uri"] in seen_uris:
                continue
            seen_uris.add(item["uri"])
            item["provider"] = "feed_registry"
            if feed.get("title"):
                item["snippet"] = _clip(f"{feed['title']}: {item['snippet']}", 200)
            results.append(item)
            if len(results) >= max_results:
                return results, health_updates
    return results, health_updates


def _update_feed_registry_health(
    feed_registry: dict[str, Any],
    *,
    feed_health_updates: dict[str, dict[str, Any]],
    generated_at: str,
) -> dict[str, Any]:
    updated_registry = copy.deepcopy(feed_registry)
    updated_registry.setdefault("schema_version", "1.0.0")
    updated_registry.setdefault("external_research_feed_registry_id", f"external_research_feed_registry_{updated_registry.get('workspace_id', 'workspace')}")
    updated_registry.setdefault("workspace_id", updated_registry.get("workspace_id", "workspace"))
    updated_registry.setdefault("title", f"External research feed registry: {updated_registry['workspace_id']}")
    updated_registry.setdefault("created_at", generated_at)
    updated_feeds: list[dict[str, Any]] = []
    for index, feed in enumerate(updated_registry.get("feeds", []), start=1):
        updated_feed = copy.deepcopy(feed)
        updated_feed.setdefault("feed_id", f"feed_{index}")
        updated_feed.setdefault("title", updated_feed["feed_id"])
        updated_feed.setdefault("source_type", "market_validation")
        updated_feed.setdefault("trust_tier", "secondary")
        updated_feed.setdefault("refresh_cadence", "manual")
        updated_feed.setdefault("question_ids", [])
        feed_id = updated_feed.get("feed_id")
        health = feed_health_updates.get(feed_id or "")
        if health is None:
            updated_feeds.append(updated_feed)
            continue

        updated_feed["last_checked_at"] = generated_at
        updated_feed["matched_question_ids"] = sorted(health["matched_question_ids"])
        updated_feed["last_item_count"] = health["result_count"]
        if not health["configured"]:
            updated_feed["health_status"] = "unconfigured"
            updated_feed["health_reason"] = "Feed URI is empty; add a trusted source before relying on this slot."
            updated_feed["last_error"] = ""
        elif health["result_count"] > 0:
            updated_feed["health_status"] = "healthy"
            updated_feed["health_reason"] = f"Feed produced {health['result_count']} candidate results during the latest discovery run."
            updated_feed["last_success_at"] = generated_at
            updated_feed["last_error"] = ""
        elif health["error_messages"]:
            updated_feed["health_status"] = "error"
            updated_feed["health_reason"] = "Feed could not be loaded during the latest discovery run."
            updated_feed["last_error"] = health["error_messages"][0]
        else:
            updated_feed["health_status"] = "empty"
            updated_feed["health_reason"] = "Feed loaded successfully but produced no candidate results for its mapped questions."
            updated_feed["last_error"] = ""
        cadence_status, cadence_reason = _feed_cadence_status(updated_feed, generated_at)
        updated_feed["cadence_status"] = cadence_status
        updated_feed["cadence_reason"] = cadence_reason
        updated_feeds.append(updated_feed)
    for feed in updated_feeds:
        if not feed.get("cadence_status"):
            cadence_status, cadence_reason = _feed_cadence_status(feed, generated_at)
            feed["cadence_status"] = cadence_status
            feed["cadence_reason"] = cadence_reason
    updated_registry["feeds"] = updated_feeds
    return updated_registry


def _autodiscovered_manifest(discovery: dict[str, Any]) -> dict[str, Any]:
    suggested = [
        item
        for item in discovery["candidate_sources"]
        if item["selection_status"] == "suggested" and item.get("content_quality_status", "accepted") == "accepted"
    ]
    return {
        "sources": [
            {
                "source_id": item["source_id"],
                "uri": item["uri"],
                "source_type": item["source_type"],
                "title": item["title"],
                "published_at": "",
                "question_id": item["question_id"],
                "rationale": item.get("evidence_excerpt", item["snippet"]),
                "freshness_expectation": item["freshness_expectation"],
            }
            for item in suggested
        ]
    }


def _select_manifest_from_discovery(
    plan: dict[str, Any],
    discovery: dict[str, Any],
    *,
    generated_at: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    questions_by_id = {item["question_id"]: item for item in plan["prioritized_questions"]}
    updated_candidates = [copy.deepcopy(item) for item in discovery["candidate_sources"]]
    selected_sources: list[dict[str, Any]] = []

    for question in plan["prioritized_questions"]:
        candidates = [
            item for item in updated_candidates
            if item["question_id"] == question["question_id"]
        ]
        candidates.sort(key=lambda item: item.get("quality_score", 0), reverse=True)
        accepted_candidates: list[dict[str, Any]] = []
        for candidate in candidates:
            try:
                details = _read_uri_details(candidate["uri"])
            except Exception:
                candidate["content_quality_score"] = 0
                candidate["content_quality_status"] = "rejected"
                candidate["content_quality_reason"] = "Candidate source could not be fetched for validation."
                continue
            content = details["content"]
            detected_title = details["title"]
            detected_published_at = details.get("published_at", "")
            evidence_excerpt = _best_evidence_excerpt(question, content, candidate.get("snippet", ""))
            detected_freshness_status = _freshness_label(detected_published_at, generated_at)
            content_quality_score, content_quality_status, content_quality_reason = _score_fetched_source_quality(
                question,
                candidate=candidate,
                content=content,
                detected_title=detected_title,
                detected_published_at=detected_published_at,
                generated_at=generated_at,
            )
            candidate["content_quality_score"] = content_quality_score
            candidate["content_quality_status"] = content_quality_status
            candidate["content_quality_reason"] = content_quality_reason
            candidate["evidence_excerpt"] = evidence_excerpt
            candidate["detected_freshness_status"] = detected_freshness_status
            if detected_title:
                candidate["detected_title"] = detected_title
            if detected_published_at:
                candidate["detected_published_at"] = detected_published_at
            if content_quality_status == "accepted":
                accepted_candidates.append(candidate)

        accepted_candidates.sort(key=lambda item: item.get("content_quality_score", 0), reverse=True)
        accepted_candidate = accepted_candidates[0] if accepted_candidates else None
        if accepted_candidate is not None:
            accepted_candidate["selection_status"] = "suggested"
            selected_sources.append(
                {
                    "source_id": accepted_candidate["source_id"],
                    "uri": accepted_candidate["uri"],
                    "source_type": accepted_candidate["source_type"],
                    "title": accepted_candidate.get("detected_title") or accepted_candidate["title"],
                    "published_at": accepted_candidate.get("detected_published_at", ""),
                    "question_id": accepted_candidate["question_id"],
                    "rationale": accepted_candidate.get("evidence_excerpt", accepted_candidate["snippet"]),
                    "freshness_expectation": accepted_candidate["freshness_expectation"],
                }
            )

    updated_discovery = copy.deepcopy(discovery)
    updated_discovery["candidate_sources"] = updated_candidates
    return {"sources": selected_sources}, updated_discovery


def _coverage_review_items(
    plan: dict[str, Any],
    discovery: dict[str, Any],
    selected_manifest: dict[str, Any],
) -> list[str]:
    covered_question_ids = {item["question_id"] for item in selected_manifest.get("sources", [])}
    review_items: list[str] = []
    for question in plan["prioritized_questions"]:
        if question["question_id"] not in covered_question_ids:
            review_items.append(
                f"Missing external source for `{question['question_id']}` ({question['recommended_source_type']}): {question['question']}"
            )
    if discovery["search_status"] == "no_results":
        review_items.append("No candidate sources were discovered from the bounded search queries.")
    elif discovery["search_status"] == "partial":
        review_items.append("Candidate source coverage is partial; PM review should fill the uncovered questions before broad claims are made.")
    for lane in discovery.get("signal_lane_coverage", []):
        if lane.get("selected_source_count", 0) == 0:
            review_items.append(
                f"Missing selected source coverage for required `{lane['label']}` signals."
            )
    for candidate in discovery["candidate_sources"]:
        if candidate.get("content_quality_status") == "review":
            review_items.append(
                f"Review source `{candidate['title']}` for `{candidate['question_id']}`: {candidate['content_quality_reason']}"
            )
    return review_items


def _feed_health_review_items(feed_registry: dict[str, Any] | None) -> list[str]:
    if not feed_registry:
        return []
    review_items: list[str] = []
    for feed in feed_registry.get("feeds", []):
        status = feed.get("health_status")
        if status in {"error", "empty", "unconfigured"}:
            review_items.append(
                f"Feed `{feed.get('feed_id', feed.get('title', 'unknown'))}` is `{status}`: {feed.get('health_reason', 'Feed health needs PM review.')}"
            )
        cadence_status = feed.get("cadence_status")
        if cadence_status in {"due", "stale"} and status not in {"error", "unconfigured"}:
            review_items.append(
                f"Feed `{feed.get('feed_id', feed.get('title', 'unknown'))}` cadence is `{cadence_status}`: {feed.get('cadence_reason', 'Feed freshness needs PM review.')}"
            )
    return review_items


def _write_research_discovery_files(
    workspace_dir: Path,
    discovery: dict[str, Any],
    *,
    feed_registry: dict[str, Any] | None = None,
) -> None:
    outputs_dir = workspace_dir / "outputs" / "research"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    _write_json(outputs_dir / "external-research-manifest.autodiscovered.json", _autodiscovered_manifest(discovery))

    docs_dir = workspace_dir / "docs" / "discovery"
    docs_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# External Research Source Discovery",
        "",
        f"- Search provider: `{discovery['search_provider']}`",
        f"- Search status: `{discovery['search_status']}`",
        "",
        "## Question Coverage",
        "",
    ]
    for item in discovery["discovered_questions"]:
        lines.append(
            f"- `{item['source_type']}` `{item['candidate_count']}` candidates for: {item['query']}"
        )
    signal_lane_coverage = discovery.get("signal_lane_coverage", [])
    if signal_lane_coverage:
        lines.extend(["", "## Signal Lane Coverage", ""])
        for lane in signal_lane_coverage:
            lines.append(
                f"- `{lane['label']}` planned={lane['planned_question_count']} discovered={lane['discovered_question_count']} candidates={lane['candidate_source_count']} suggested={lane['suggested_source_count']} selected={lane.get('selected_source_count', 0)}"
            )
    if feed_registry and feed_registry.get("feeds"):
        lines.extend(["", "## Feed Health", ""])
        for feed in feed_registry["feeds"]:
            health_status = feed.get("health_status", "unknown")
            item_count = feed.get("last_item_count")
            item_suffix = f" ({item_count} items)" if item_count is not None else ""
            lines.append(f"- `{feed['feed_id']}` `{health_status}`{item_suffix}: {feed['title']}")
            if feed.get("health_reason"):
                lines.append(f"  {feed['health_reason']}")
            if feed.get("cadence_status"):
                lines.append(f"  Cadence: {feed['cadence_status']}")
    lines.extend(["", "## Suggested Sources", ""])
    suggested = [item for item in discovery["candidate_sources"] if item["selection_status"] == "suggested"]
    for item in suggested[:10]:
        quality_suffix = ""
        if item.get("content_quality_status"):
            quality_suffix = f" [{item['content_quality_status']}, score={item.get('content_quality_score', 0)}]"
        lines.append(f"- [{item['title']}]({item['uri']}): {item['snippet']}{quality_suffix}")
    (docs_dir / "external-research-source-discovery.md").write_text(
        render_governed_markdown(
            title="External Research Source Discovery",
            body_lines=lines,
            version_number=1,
            status="review_needed",
            updated_at=discovery["created_at"],
            updated_by="Research Agent",
            change_summary="Recorded the current governed source-discovery candidates and lane coverage.",
            source_artifact_ids=[discovery["external_research_source_discovery_id"]],
        ),
        encoding="utf-8",
    )


def _write_selected_manifest(path: Path, manifest_payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _write_json(path, manifest_payload)


def _write_research_loop_doc(
    workspace_dir: Path,
    *,
    generated_at: str,
    coverage_status: str,
    refresh_status: str,
    selected_manifest: dict[str, Any],
    signal_lane_coverage: list[dict[str, Any]],
    review_items: list[str],
    feed_registry: dict[str, Any] | None = None,
) -> None:
    docs_dir = workspace_dir / "docs" / "discovery"
    docs_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        f"- Coverage status: `{coverage_status}`",
        f"- Refresh status: `{refresh_status}`",
        f"- Selected sources: `{len(selected_manifest.get('sources', []))}`",
        "",
        "## Signal Lane Coverage",
        "",
    ]
    for lane in signal_lane_coverage:
        lines.append(
            f"- `{lane['label']}` planned={lane['planned_question_count']} discovered={lane['discovered_question_count']} candidates={lane['candidate_source_count']} selected={lane.get('selected_source_count', 0)}"
        )
    lines.extend(
        [
            "",
        "## Selected Manifest Sources",
        "",
        ]
    )
    for item in selected_manifest.get("sources", []):
        lines.append(f"- `{item['source_type']}` {item['title']} -> {item['uri']}")
    if not selected_manifest.get("sources"):
        lines.append("- No selected sources were available for refresh.")
    if feed_registry and feed_registry.get("feeds"):
        lines.extend(["", "## Feed Health", ""])
        for feed in feed_registry["feeds"]:
            lines.append(
                f"- `{feed.get('feed_id', 'unknown')}` `{feed.get('health_status', 'unknown')}` {feed.get('title', 'Untitled feed')}"
            )
            if feed.get("health_reason"):
                lines.append(f"  {feed['health_reason']}")
            if feed.get("cadence_status"):
                lines.append(f"  Cadence: {feed['cadence_status']}")
    lines.extend(["", "## Review Required", ""])
    for item in review_items or ["No additional review items."]:
        lines.append(f"- {item}")
    (docs_dir / "external-research-loop.md").write_text(
        render_governed_markdown(
            title="External Research Loop",
            body_lines=lines,
            version_number=1,
            status="review_needed" if review_items else "decision_ready",
            updated_at=generated_at,
            updated_by="Research Agent",
            change_summary="Logged the latest governed external research refresh loop and review items.",
            source_artifact_ids=[
                source.get("source_id", "selected_research_manifest")
                for source in selected_manifest.get("sources", [])
            ] or ["selected_research_manifest"],
        ),
        encoding="utf-8",
    )


def build_external_research_plan_from_workspace(
    root_dir: Path | str,
    *,
    workspace_dir: Path | str,
    generated_at: str,
    persist: bool = True,
    research_brief_override: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    workspace = Path(workspace_dir).resolve()
    artifacts_dir = workspace / "artifacts"
    research_brief = research_brief_override or _load_workspace_research_brief(workspace, generated_at)
    external_research_plan = _build_external_research_plan(research_brief, generated_at)
    bundle = {"external_research_plan": external_research_plan}

    if persist:
        manifest_path = workspace / "workspace_manifest.yaml"
        _write_json(artifacts_dir / "external_research_plan.json", external_research_plan)
        _append_manifest_artifact_path(manifest_path, "artifacts/external_research_plan.json")
        _write_research_plan_files(workspace, external_research_plan)

    return bundle


def discover_external_research_sources_from_workspace(
    root_dir: Path | str,
    *,
    workspace_dir: Path | str,
    generated_at: str,
    persist: bool = True,
    search_result_limit: int = 3,
    search_fixture_dir: Path | str | None = None,
    search_provider_chain: str | None = None,
    feed_registry_path: Path | str | None = None,
    research_brief_override: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    workspace = Path(workspace_dir).resolve()
    artifacts_dir = workspace / "artifacts"
    fixture_dir = Path(search_fixture_dir).resolve() if search_fixture_dir is not None else None
    providers = _search_provider_chain(search_provider_chain)
    feed_registry_payload, _ = _load_feed_registry_payload(workspace, feed_registry_path=feed_registry_path)
    feeds = []
    if feed_registry_payload is not None:
        feeds = [item for item in feed_registry_payload.get("feeds", []) if isinstance(item, dict)]
    plan_path = artifacts_dir / "external_research_plan.json"
    if plan_path.exists():
        external_research_plan = _load_json(plan_path)
    else:
        external_research_plan = build_external_research_plan_from_workspace(
            root_dir,
            workspace_dir=workspace,
            generated_at=generated_at,
            persist=persist,
            research_brief_override=research_brief_override,
        )["external_research_plan"]

    discovered_questions: list[dict[str, Any]] = []
    candidate_sources: list[dict[str, Any]] = []
    feed_health_updates: dict[str, dict[str, Any]] = {}
    for question in external_research_plan["prioritized_questions"]:
        aggregated_results: list[dict[str, str]] = []
        seen_question_uris: set[str] = set()
        queries_attempted = 0
        providers_attempted: list[str] = []
        primary_query = question["search_queries"][0]
        if feeds:
            providers_attempted.append("feed_registry")
            feed_results, question_feed_health = _discover_feed_results(
                question,
                query=primary_query,
                max_results=search_result_limit,
                feeds=feeds,
            )
            for feed_id, update in question_feed_health.items():
                aggregated = feed_health_updates.setdefault(
                    feed_id,
                    {
                        "matched_question_ids": set(),
                        "result_count": 0,
                        "error_messages": [],
                        "configured": True,
                    },
                )
                aggregated["matched_question_ids"].update(update["matched_question_ids"])
                aggregated["result_count"] += update["result_count"]
                aggregated["error_messages"].extend(update["error_messages"])
                aggregated["configured"] = aggregated["configured"] and update["configured"]
            for result in feed_results:
                if result["uri"] in seen_question_uris:
                    continue
                seen_question_uris.add(result["uri"])
                aggregated_results.append(result)
        for query in question["search_queries"]:
            queries_attempted += 1
            for provider in providers:
                if provider not in providers_attempted:
                    providers_attempted.append(provider)
                try:
                    results = _discover_search_results(
                        query,
                        provider=provider,
                        max_results=search_result_limit,
                        fixture_dir=fixture_dir,
                    )
                except Exception:
                    results = []
                for result in results:
                    if result["uri"] in seen_question_uris:
                        continue
                    seen_question_uris.add(result["uri"])
                    aggregated_results.append(result)
                if len(aggregated_results) >= search_result_limit:
                    break
            if len(aggregated_results) >= search_result_limit:
                break
        scored_results = []
        for result in aggregated_results:
            score, selection_reason = _score_candidate_result(question, result, primary_query)
            scored_results.append((score, selection_reason, result))
        scored_results.sort(key=lambda item: item[0], reverse=True)
        discovered_questions.append(
            {
                "question_id": question["question_id"],
                "query": primary_query,
                "source_type": question["recommended_source_type"],
                "candidate_count": len(scored_results),
                "queries_attempted": queries_attempted,
                "providers_attempted": providers_attempted,
            }
        )
        unique_index = 0
        for score, selection_reason, result in scored_results:
            domain = _domain_from_uri(result["uri"])
            candidate_sources.append(
                {
                    "source_id": f"{question['question_id']}_candidate_{len(candidate_sources) + 1}",
                    "question_id": question["question_id"],
                    "source_type": question["recommended_source_type"],
                    "title": result["title"],
                    "uri": result["uri"],
                    "snippet": result["snippet"],
                    "search_query": primary_query,
                    "selection_status": "suggested" if unique_index == 0 else "alternate",
                    "provider": result.get("provider", "unknown"),
                    "domain": domain or "unknown",
                    "quality_score": score,
                    "selection_reason": selection_reason,
                    "freshness_expectation": (
                        "usable_with_review"
                        if question["recommended_source_type"] == "competitor_research"
                        else "fresh"
                    ),
                }
            )
            unique_index += 1

    if candidate_sources and all(item["candidate_count"] > 0 for item in discovered_questions):
        search_status = "completed"
    elif candidate_sources:
        search_status = "partial"
    else:
        search_status = "no_results"

    signal_lane_coverage = _signal_lane_coverage(
        external_research_plan["prioritized_questions"],
        discovered_questions=discovered_questions,
        candidate_sources=candidate_sources,
    )
    discovery = {
        "schema_version": "1.0.0",
        "external_research_source_discovery_id": f"external_research_source_discovery_{external_research_plan['workspace_id']}",
        "workspace_id": external_research_plan["workspace_id"],
        "generated_from_plan_id": external_research_plan["external_research_plan_id"],
        "search_provider": ",".join((["feed_registry"] if feeds else []) + providers),
        "search_status": search_status,
        "discovered_questions": discovered_questions,
        "signal_lane_coverage": signal_lane_coverage,
        "candidate_sources": candidate_sources,
        "created_at": generated_at,
    }
    bundle = {"external_research_source_discovery": discovery}
    updated_feed_registry = None
    if feed_registry_payload is not None:
        updated_feed_registry = _update_feed_registry_health(
            feed_registry_payload,
            feed_health_updates=feed_health_updates,
            generated_at=generated_at,
        )

    if persist:
        manifest_path = workspace / "workspace_manifest.yaml"
        _write_json(artifacts_dir / "external_research_source_discovery.json", discovery)
        _append_manifest_artifact_path(manifest_path, "artifacts/external_research_source_discovery.json")
        if updated_feed_registry is not None:
            _write_json(artifacts_dir / "external_research_feed_registry.json", updated_feed_registry)
            _append_manifest_artifact_path(manifest_path, "artifacts/external_research_feed_registry.json")
            _write_research_feed_registry_files(workspace, updated_feed_registry)
        _write_research_discovery_files(workspace, discovery, feed_registry=updated_feed_registry)

    return bundle


def run_external_research_loop_from_workspace(
    root_dir: Path | str,
    *,
    workspace_dir: Path | str,
    generated_at: str,
    persist: bool = True,
    search_result_limit: int = 3,
    search_fixture_dir: Path | str | None = None,
    search_provider_chain: str | None = None,
    feed_registry_path: Path | str | None = None,
    research_brief_override: dict[str, Any] | None = None,
    research_handoff: dict[str, Any] | None = None,
    problem_brief: dict[str, Any] | None = None,
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    workspace = Path(workspace_dir).resolve()
    plan_bundle = build_external_research_plan_from_workspace(
        root_dir,
        workspace_dir=workspace,
        generated_at=generated_at,
        persist=persist,
        research_brief_override=research_brief_override,
    )
    discovery_bundle = discover_external_research_sources_from_workspace(
        root_dir,
        workspace_dir=workspace,
        generated_at=generated_at,
        persist=persist,
        search_result_limit=search_result_limit,
        search_fixture_dir=search_fixture_dir,
        search_provider_chain=search_provider_chain,
        feed_registry_path=feed_registry_path,
        research_brief_override=research_brief_override,
    )

    external_research_plan = plan_bundle["external_research_plan"]
    discovery = discovery_bundle["external_research_source_discovery"]
    selected_manifest, filtered_discovery = _select_manifest_from_discovery(
        external_research_plan,
        discovery,
        generated_at=generated_at,
    )
    discovery_bundle["external_research_source_discovery"] = filtered_discovery
    discovery = filtered_discovery
    discovery["signal_lane_coverage"] = _signal_lane_coverage(
        external_research_plan["prioritized_questions"],
        discovered_questions=discovery.get("discovered_questions", []),
        candidate_sources=discovery.get("candidate_sources", []),
        selected_sources=selected_manifest.get("sources", []),
    )
    review_items = _coverage_review_items(external_research_plan, discovery, selected_manifest)
    registry_path = workspace / "artifacts" / "external_research_feed_registry.json"
    registry_payload = _load_json(registry_path) if registry_path.exists() else None
    review_items.extend(_feed_health_review_items(registry_payload))

    selected_source_count = len(selected_manifest.get("sources", []))
    planned_question_count = len(external_research_plan["prioritized_questions"])
    if selected_source_count == 0:
        coverage_status = "blocked"
    elif selected_source_count < planned_question_count or review_items:
        coverage_status = "partial"
    else:
        coverage_status = "completed"

    runtime_bundle: dict[str, dict[str, Any]] = {}
    refresh_status = "skipped"
    selected_manifest_path: Path | None = None
    if persist:
        selected_manifest_path = workspace / "outputs" / "research" / "external-research-manifest.selected.json"
        _write_selected_manifest(selected_manifest_path, selected_manifest)
    elif selected_source_count > 0:
        temp_dir = Path(tempfile.mkdtemp(prefix="productos-research-loop-"))
        selected_manifest_path = temp_dir / "external-research-manifest.selected.json"
        _write_selected_manifest(selected_manifest_path, selected_manifest)

    if selected_manifest_path is not None and selected_source_count > 0:
        runtime_bundle = research_workspace_from_manifest(
            root_dir,
            workspace_dir=workspace,
            manifest_path=selected_manifest_path,
            generated_at=generated_at,
            persist=persist,
            research_brief_override=research_brief_override,
            research_handoff=research_handoff,
            problem_brief=problem_brief,
        )
        refresh_status = "completed"
    else:
        fallback_research_brief = research_brief_override or _load_workspace_research_brief(workspace, generated_at)
        fallback_sources = _fallback_normalized_sources(
            problem_brief=problem_brief,
            research_brief=fallback_research_brief,
            generated_at=generated_at,
        )
        runtime_bundle = _build_research_runtime_bundle(
            research_brief=fallback_research_brief,
            normalized_sources=fallback_sources,
            generated_at=generated_at,
            research_handoff=research_handoff,
        )
        if persist:
            sync_canonical_discovery_operations_artifacts(
                workspace,
                bundle={**runtime_bundle, "selected_research_manifest": selected_manifest},
            )
            _write_research_summary_doc(
                workspace,
                research_brief=runtime_bundle["research_brief"],
                external_research_review=runtime_bundle["external_research_review"],
                competitor_dossier=runtime_bundle["competitor_dossier"],
                customer_pulse=runtime_bundle["customer_pulse"],
                market_analysis_brief=runtime_bundle["market_analysis_brief"],
                normalized_sources=fallback_sources,
            )

    if persist:
        manifest_path = workspace / "workspace_manifest.yaml"
        _write_json(workspace / "artifacts" / "external_research_source_discovery.json", discovery)
        _append_manifest_artifact_path(manifest_path, "artifacts/external_research_source_discovery.json")
        _write_research_discovery_files(workspace, discovery, feed_registry=registry_payload)
        _write_research_loop_doc(
            workspace,
            generated_at=generated_at,
            coverage_status=coverage_status,
            refresh_status=refresh_status,
            selected_manifest=selected_manifest,
            signal_lane_coverage=discovery.get("signal_lane_coverage", []),
            review_items=review_items,
            feed_registry=registry_payload,
        )

    merged_bundle = {}
    merged_bundle.update(plan_bundle)
    merged_bundle.update(discovery_bundle)
    merged_bundle.update(runtime_bundle)
    merged_bundle["selected_research_manifest"] = selected_manifest
    summary = {
        "coverage_status": coverage_status,
        "refresh_status": refresh_status,
        "planned_question_count": planned_question_count,
        "candidate_source_count": len(discovery["candidate_sources"]),
        "selected_source_count": selected_source_count,
        "required_signal_lane_count": len(_core_signal_lane_ids()),
        "planned_signal_lane_count": len(external_research_plan["coverage_summary"].get("planned_signal_lanes", [])),
        "discovered_signal_lane_count": sum(
            1 for lane in discovery.get("signal_lane_coverage", []) if lane.get("candidate_source_count", 0) > 0
        ),
        "selected_signal_lane_count": sum(
            1 for lane in discovery.get("signal_lane_coverage", []) if lane.get("selected_source_count", 0) > 0
        ),
        "review_items": review_items,
        "selected_manifest_path": str(selected_manifest_path) if selected_manifest_path is not None else None,
    }
    return merged_bundle, summary


def _build_competitor_dossier(
    workspace_id: str,
    research_brief: dict[str, Any],
    normalized_sources: list[dict[str, Any]],
    generated_at: str,
) -> dict[str, Any]:
    competitor_sources = [item for item in normalized_sources if item["source_type"] == "competitor_research"]
    coverage_status = _competitor_evidence_coverage_status(competitor_sources or normalized_sources)
    competitors = []
    for source in competitor_sources[:5]:
        name = _extract_competitor_name(source)
        competitors.append(
            {
                "name": name or source["title"],
                "competitor_type": _classify_competitor_type(name or source["title"]),
                "target_customer": research_brief["summary"],
                "positioning_summary": source["summary"],
                "go_to_market_motion": "Use the current market narrative as the baseline motion, then normalize buyer and lane specifics in PM review.",
                "pricing_signal": "Commercial posture visible in source review; pricing still needs explicit PM normalization.",
                "positioning_gap": "The competitor narrative is visible, but ProductOS can differentiate through narrower workflow control, proof discipline, and clearer launch-lane posture.",
                "icp_overlap": "high",
                "substitution_risk": "high",
                "ecosystem_role": "Named incumbent or adjacent alternative in the current workflow corridor.",
                "strengths": [source["sentences"][0] if source["sentences"] else source["summary"]],
                "weaknesses": research_brief.get("known_gaps", [])[:1] or ["Comparison still needs deeper PM validation."],
                "where_they_win": ["When buyers prefer a familiar vendor narrative, existing distribution, or broader default category fit."],
                "where_they_lose": ["When the buyer needs a narrow, measurable wedge with explicit control boundaries and visible proof logic."],
                "displacement_barriers": ["Existing vendor familiarity and proof expectations."],
                "implications": [f"Use {source['title']} as bounded comparison evidence, not as the source of truth for ProductOS positioning."],
                "evidence_refs": [source["source_note_card_id"]],
                "confidence": _normalized_source_confidence(source),
                "last_checked_at": generated_at,
            }
        )

    comparison_questions = [item["question"] for item in research_brief.get("external_research_questions", [])]
    named_competitor_count = len(competitors)
    competitive_landscape_status = "named_competitor_set" if named_competitor_count else "abstract_alternatives_only"
    dossier_quality = _competitor_dossier_quality(named_competitor_count, coverage_status)
    if not competitors:
        competitors = [
            {
                "name": "Status quo incumbent workflow stack",
                "competitor_type": "status_quo",
                "target_customer": research_brief["summary"],
                "positioning_summary": "The buyer can stay with incumbent tools, spreadsheets, services, and local workarounds while delaying a new workflow-control layer.",
                "go_to_market_motion": "Default no-change posture.",
                "pricing_signal": "Hidden inside labor cost, workflow delay, and revenue leakage.",
                "positioning_gap": "Familiar and low-disruption, but weak on explicit queue control, measurable proof, and cross-role operating visibility.",
                "icp_overlap": "high",
                "substitution_risk": "high",
                "ecosystem_role": "Current operating baseline rather than a named competitor set.",
                "strengths": ["Low perceived switching cost"],
                "weaknesses": ["Comparison still under-researched and not yet mapped to named competitors."],
                "where_they_win": ["When ProductOS has not yet established proof or a clear launch-lane wedge."],
                "where_they_lose": ["When buyers want measurable workflow control and explicit downstream proof."],
                "displacement_barriers": ["Operational habit and proof expectations."],
                "implications": ["Gather named competitor evidence before treating this dossier as decision-ready."],
                "evidence_refs": _source_ids(normalized_sources[:1]) or [research_brief["research_brief_id"]],
                "confidence": "low",
                "last_checked_at": generated_at,
            }
        ]
    return {
        "schema_version": "1.1.0",
        "competitor_dossier_id": f"competitor_dossier_{workspace_id}",
        "workspace_id": workspace_id,
        "title": f"Competitor dossier: {research_brief['title']}",
        "competitive_frame": research_brief["summary"],
        "comparison_basis": comparison_questions[0] if comparison_questions else "Governed workflow-control positioning versus incumbent alternatives.",
        "framework_registry_ref": _framework_registry_id(workspace_id),
        "selected_framework_ids": ["competitive_displacement_map", "signal_weighted_priority"],
        "research_scope": "Bounded external competitor refresh from explicitly selected sources.",
        "target_segment_refs": research_brief["target_segment_refs"],
        "target_persona_refs": research_brief["target_persona_refs"],
        "linked_entity_refs": research_brief.get("linked_entity_refs", []),
        "source_artifact_ids": _source_ids(competitor_sources) or _source_ids(normalized_sources),
        "status_quo_alternatives": [
            "Manual coordination across notes, spreadsheets, and incumbent workflow tools",
            "Incumbent workflow or operations vendors with partial control layers",
        ],
        "internal_build_risk": "medium",
        "competitive_landscape_status": competitive_landscape_status,
        "evidence_coverage_status": coverage_status,
        "dossier_quality": dossier_quality,
        "named_competitor_count": named_competitor_count,
        "where_we_win": [
            "Explicit claim discipline and proof-gap visibility",
            "Governed workflow control positioned through a narrow launch lane first",
        ],
        "where_we_lose": research_brief.get("known_gaps", [])[:2] or ["External proof is still thinner than the desired release bar."],
        "credible_wedge_for_posture": research_brief["summary"],
        "required_proof_to_displace": comparison_questions[:3] or ["Quantified external proof must exist before broad displacement claims are made."],
        "prioritization_implications": [
            "Prioritize work that reduces switching fear and proves coexistence with incumbent tools.",
            "Keep broader platform claims behind a narrow, evidence-backed challenger wedge."
        ],
        "recommended_positioning_angle": "Lead with governed workflow control, bounded launch-lane proof, and visible evidence posture.",
        "competitors": competitors,
        "last_refreshed_at": generated_at,
        "created_at": generated_at,
    }


def _build_customer_pulse(
    workspace_id: str,
    research_brief: dict[str, Any],
    normalized_sources: list[dict[str, Any]],
    generated_at: str,
) -> dict[str, Any]:
    customer_sources = [
        item for item in normalized_sources if item["source_type"] in {"customer_evidence", "operator_interview"}
    ] or normalized_sources[:2]
    top_pain_points = []
    voice_of_customer_quotes = []
    for source in customer_sources[:5]:
        sentence = source["sentences"][0] if source["sentences"] else source["summary"]
        top_pain_points.append(
            {
                "description": _clip(sentence, 180),
                "severity": "high" if "delay" in sentence.lower() or "denial" in sentence.lower() or "manual" in sentence.lower() else "medium",
                "frequency": "weekly",
                "affected_segment": _target_segment_name(research_brief),
                "corroboration_status": "cross_source_supported" if len(customer_sources) > 1 else "single_source_raw",
            }
        )
        voice_of_customer_quotes.append(
            {
                "quote": _clip(sentence, 160),
                "source": source["title"],
                "sentiment": "negative" if any(token in sentence.lower() for token in {"pain", "delay", "risk", "manual"}) else "neutral",
            }
        )

    mix_counts: dict[str, int] = {}
    for source in customer_sources:
        mix_type = _source_type_to_mix(source["source_type"])
        mix_counts[mix_type] = mix_counts.get(mix_type, 0) + 1

    return {
        "schema_version": "1.1.0",
        "customer_pulse_id": f"customer_pulse_{workspace_id}",
        "workspace_id": workspace_id,
        "cadence": "monthly",
        "reporting_period": {
            "start_date": generated_at[:10],
            "end_date": generated_at[:10],
        },
        "top_pain_points": top_pain_points or [
            {
                "description": "External customer evidence has not yet been gathered for the current research questions.",
                "severity": "medium",
                "frequency": "sporadic",
                "affected_segment": _target_segment_name(research_brief),
                "corroboration_status": "single_source_raw",
            }
        ],
        "emerging_signals": [
            "External customer evidence is now being normalized into governed research artifacts.",
        ],
        "segment_health": [
            {
                "segment_name": _target_segment_name(research_brief),
                "health": "amber",
                "trend": "stable",
            }
        ],
        "signal_source_mix": [
            {"source_type": key, "signal_count": value, "confidence": "moderate" if value > 1 else "raw"}
            for key, value in sorted(mix_counts.items())
        ] or [{"source_type": "research", "signal_count": 0, "confidence": "raw"}],
        "support_signal_clusters": [
            {
                "cluster_name": "Manual workflow burden",
                "summary": "Customer and operator signals keep highlighting recurring manual follow-up, reporting, and queue reconstruction work.",
                "signal_strength": "high" if len(customer_sources) > 1 else "moderate",
                "source_refs": _source_ids(customer_sources[:2]) or [research_brief["research_brief_id"]],
            }
        ],
        "adoption_signal_clusters": [
            {
                "cluster_name": "Reviewable artifact pull",
                "summary": "Customers respond most clearly when ProductOS turns messy workflow evidence into one reviewable packet.",
                "signal_strength": "moderate",
                "source_refs": _source_ids(customer_sources[:2]) or [research_brief["research_brief_id"]],
            }
        ],
        "priority_recommendation": {
            "focus_area": "Reduce repeat PM reconstruction chores before broadening outward surface area.",
            "rationale": "The most repeated signals still point to manual weekly and cross-tool workflow burden rather than missing broad platform breadth.",
            "confidence": "high" if len(customer_sources) > 1 else "moderate",
        },
        "voice_of_customer_quotes": voice_of_customer_quotes[:3],
        "source_artifact_ids": _source_ids(customer_sources) or _source_ids(normalized_sources),
        "generated_at": generated_at,
    }


def _build_market_analysis_brief(
    workspace_id: str,
    research_brief: dict[str, Any],
    normalized_sources: list[dict[str, Any]],
    generated_at: str,
) -> dict[str, Any]:
    summaries = [item["summary"] for item in normalized_sources]
    market_sources = [
        item for item in normalized_sources if item["source_type"] in {"market_validation", "security_review", "competitor_research"}
    ] or normalized_sources
    return {
        "schema_version": "1.1.0",
        "market_analysis_brief_id": f"market_analysis_brief_{workspace_id}",
        "workspace_id": workspace_id,
        "title": f"Market analysis brief: {research_brief['title']}",
        "market_name": _target_segment_name(research_brief),
        "framework_registry_ref": _framework_registry_id(workspace_id),
        "selected_framework_ids": ["market_jobs_barriers", "signal_weighted_priority"],
        "research_scope": "Bounded external market refresh from explicitly selected sources.",
        "category_structure": [
            "Incumbent workflow and revenue-cycle tools compete through familiar category language.",
            "Governed workflow-control positioning requires sharper proof and launch-lane specificity than generic platform narratives.",
        ],
        "category_summary": _clip(" ".join(summaries[:2]) or research_brief["summary"], 220),
        "trend_summary": _clip(" ".join(summaries[1:3]) or research_brief["summary"], 220),
        "market_dynamics": [
            _clip(item["summary"], 160) for item in market_sources[:3]
        ] or [research_brief["summary"]],
        "power_centers": [
            "PMs, operators, and workflow owners control whether the wedge feels specific enough to trust.",
        ],
        "adoption_barriers": research_brief.get("known_gaps", [])[:2] or ["External proof and trust signals remain incomplete."],
        "switching_costs": [
            "Incumbent workflow habits and vendor familiarity create real switching friction.",
        ],
        "market_role_implications": [
            "ProductOS should lead with a governed launch lane and explicit evidence posture rather than a broad platform promise.",
        ],
        "agentic_delivery_implications": [
            "Agentic leverage matters when it reduces PM reconstruction work without weakening evidence provenance.",
            "Broader automation should remain secondary to bounded same-day review quality."
        ],
        "prioritization_implications": [
            "Prioritize the narrowest wedge that lowers switching fear and proves reviewable value quickly.",
            "Let category breadth follow after the discover control surface is clearly trusted."
        ],
        "key_uncertainties": research_brief.get("known_gaps", []),
        "source_artifact_ids": _source_ids(market_sources) or _source_ids(normalized_sources),
        "last_refreshed_at": generated_at,
        "created_at": generated_at,
    }


def _build_framework_registry(workspace_id: str, generated_at: str) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "framework_registry_id": _framework_registry_id(workspace_id),
        "workspace_id": workspace_id,
        "title": f"Framework registry: {workspace_id}",
        "frameworks": [
            {
                "framework_id": "market_jobs_barriers",
                "domain": "market",
                "name": "Market jobs and barriers",
                "summary": "Use when ProductOS needs a compact view of buyer jobs, switching friction, and trust barriers.",
                "applicability_rules": [
                    "Use before broad category claims when switching friction matters more than precise market math.",
                    "Prefer when the PM must explain why a challenger wedge is credible."
                ],
                "evidence_expectations": [
                    "Need at least one market or security signal.",
                    "Keep one explicit buyer barrier or proof requirement visible."
                ],
                "output_artifact_types": ["market_analysis_brief", "market_sizing_brief", "market_share_brief"],
                "default_when": ["The current wedge still needs sharper market framing."],
                "avoid_when": ["Only a pricing or packaging decision is being made."],
                "status": "curated_default",
            },
            {
                "framework_id": "customer_pain_adoption_split",
                "domain": "customer",
                "name": "Customer pain and adoption split",
                "summary": "Use when support burden and adoption momentum should both influence the next priority move.",
                "applicability_rules": [
                    "Use when support and adoption evidence both exist.",
                    "Prefer when the PM must decide whether to harden, expand, or reopen work."
                ],
                "evidence_expectations": [
                    "Need at least one pain cluster and one adoption cluster.",
                    "Keep source refs visible for every cluster."
                ],
                "output_artifact_types": ["customer_pulse", "outcome_review"],
                "default_when": ["The PM needs a balanced reading of pain and pull."],
                "avoid_when": ["No customer or operator evidence exists yet."],
                "status": "curated_default",
            },
            {
                "framework_id": "competitive_displacement_map",
                "domain": "competition",
                "name": "Competitive displacement map",
                "summary": "Use when ProductOS must compare named competitors, status quo, and in-house alternatives together.",
                "applicability_rules": [
                    "Use when challenger positioning and displacement barriers matter.",
                    "Prefer when the PM must justify why this wedge should go before breadth work."
                ],
                "evidence_expectations": [
                    "Need at least one bounded competitor or status-quo evidence source.",
                    "Every comparison row should retain evidence refs."
                ],
                "output_artifact_types": ["competitor_dossier", "landscape_matrix"],
                "default_when": ["The PM must explain the alternative set clearly."],
                "avoid_when": ["Only internal assumptions exist and no bounded comparison can be made."],
                "status": "curated_default",
            },
            {
                "framework_id": "signal_weighted_priority",
                "domain": "prioritization",
                "name": "Signal-weighted priority",
                "summary": "Use when ProductOS must rank the next problem, opportunity, or feature with explicit leverage and burden tradeoffs.",
                "applicability_rules": [
                    "Use whenever there is a real next-slice choice to make.",
                    "Prefer when PM override should stay visible rather than disappear into a final score."
                ],
                "evidence_expectations": [
                    "Keep source artifact ids on every ranked option.",
                    "Expose agentic leverage, compliance burden, and ambiguity burden explicitly."
                ],
                "output_artifact_types": ["opportunity_portfolio_view", "prioritization_decision_record", "feature_prioritization_brief"],
                "default_when": ["The repo needs a visible rationale for why one slice goes before another."],
                "avoid_when": ["There is only one option and no real prioritization call is happening."],
                "status": "curated_default",
            },
        ],
        "selection_policies": [
            {
                "policy_id": "policy_market_default",
                "domain": "market",
                "selection_logic": "Use market jobs and barriers first when trust, proof, and switching friction are more urgent than precise category math.",
                "fallback_framework_id": "market_jobs_barriers",
            },
            {
                "policy_id": "policy_customer_default",
                "domain": "customer",
                "selection_logic": "Use customer pain and adoption split when the PM must distinguish hardening needs from healthy pull.",
                "fallback_framework_id": "customer_pain_adoption_split",
            },
            {
                "policy_id": "policy_competition_default",
                "domain": "competition",
                "selection_logic": "Use competitive displacement map whenever named alternatives, status quo, and in-house options all shape the buyer decision.",
                "fallback_framework_id": "competitive_displacement_map",
            },
            {
                "policy_id": "policy_priority_default",
                "domain": "prioritization",
                "selection_logic": "Use signal-weighted priority whenever ProductOS must choose one next bounded slice and preserve the tradeoff logic.",
                "fallback_framework_id": "signal_weighted_priority",
            },
        ],
        "generated_at": generated_at,
    }


def _build_landscape_matrix(
    *,
    workspace_id: str,
    competitor_dossier: dict[str, Any],
    generated_at: str,
) -> dict[str, Any]:
    rows = []
    for competitor in competitor_dossier["competitors"][:4]:
        rows.append(
            {
                "name": competitor["name"],
                "competitor_type": competitor["competitor_type"],
                "positioning": competitor["positioning_summary"],
                "pricing_signal": competitor["pricing_signal"],
                "motion": competitor["go_to_market_motion"],
                "governance_posture": competitor["positioning_gap"],
                "strengths": competitor["strengths"],
                "weaknesses": competitor["weaknesses"],
                "implication": competitor["implications"][0],
                "evidence_refs": competitor.get("evidence_refs", []),
                "confidence": competitor["confidence"],
                "last_checked_at": competitor["last_checked_at"],
            }
        )
    if len(rows) < 2:
        rows.append(
            {
                "name": "ProductOS bounded wedge",
                "competitor_type": "startup",
                "positioning": competitor_dossier["credible_wedge_for_posture"],
                "pricing_signal": "Early PM operating wedge; pricing remains bounded and review-led.",
                "motion": "Controlled demo and bounded workflow proof.",
                "governance_posture": "Lead with explicit evidence posture and narrow launch-lane proof.",
                "strengths": competitor_dossier["where_we_win"][:2],
                "weaknesses": competitor_dossier["where_we_lose"][:2],
                "implication": "Stay focused on the narrowest credible wedge before broadening scope.",
                "evidence_refs": competitor_dossier["source_artifact_ids"][:2],
                "confidence": "moderate",
                "last_checked_at": generated_at,
            }
        )
    return {
        "schema_version": "1.1.0",
        "landscape_matrix_id": f"landscape_matrix_{workspace_id}",
        "workspace_id": workspace_id,
        "title": f"Landscape matrix: {workspace_id}",
        "framework_registry_ref": _framework_registry_id(workspace_id),
        "selected_framework_ids": ["competitive_displacement_map"],
        "research_scope": "Bounded landscape comparison synthesized from the current governed competitor packet.",
        "comparison_axes": ["positioning", "pricing signal", "motion", "strengths", "weaknesses", "implication"],
        "comparison_summary": "The landscape is split between named vendors, status quo, and in-house alternatives, so ProductOS should prioritize a clear challenger wedge over breadth claims.",
        "source_artifact_ids": [competitor_dossier["competitor_dossier_id"], *competitor_dossier["source_artifact_ids"][:2]],
        "rows": rows,
        "last_refreshed_at": generated_at,
        "created_at": generated_at,
    }


def _build_market_sizing_brief(
    *,
    workspace_id: str,
    research_brief: dict[str, Any],
    market_analysis_brief: dict[str, Any],
    competitor_dossier: dict[str, Any],
    generated_at: str,
) -> dict[str, Any]:
    source_ref = (
        competitor_dossier["source_artifact_ids"][0]
        if competitor_dossier["source_artifact_ids"]
        else research_brief["research_brief_id"]
    )
    return {
        "schema_version": "1.1.0",
        "market_sizing_brief_id": f"market_sizing_brief_{workspace_id}",
        "workspace_id": workspace_id,
        "market_name": market_analysis_brief["market_name"],
        "framework_registry_ref": _framework_registry_id(workspace_id),
        "selected_framework_ids": ["market_jobs_barriers"],
        "sizing_method": "blended",
        "tam": {
            "amount": 1800000000,
            "currency": "USD",
            "formula": "Category software and services spend x share attributable to PM operating workflow and synthesis controls.",
        },
        "sam": {
            "amount": 420000000,
            "currency": "USD",
            "formula": "Reachable B2B product teams with enough workflow pain and governance need for a bounded ProductOS wedge.",
        },
        "som": {
            "amount": 48000000,
            "currency": "USD",
            "formula": "Initial reachable wedge over a 3-year horizon if ProductOS proves same-day discover value first.",
        },
        "top_down_inputs": [
            {
                "label": "Category spend proxy",
                "value": "Bounded PM operating workflow category proxy",
                "source_ref": source_ref,
            }
        ],
        "bottom_up_inputs": [
            {
                "label": "Reachable design-partner path",
                "value": "Target accounts with strong PM reconstruction pain and explicit proof needs",
                "source_ref": source_ref,
            }
        ],
        "assumptions": [
            {
                "statement": "The first reachable segment is concentrated in B2B product teams that already feel recurring cross-tool PM reconstruction cost.",
                "source_ref": source_ref,
            }
        ],
        "sensitivity_notes": [
            "SAM falls if trust and governance requirements are weaker than expected.",
            "SOM expands only after the initial same-day discover wedge becomes easy to explain and trust."
        ],
        "confidence": "moderate",
        "prioritization_implications": [
            "The sizing is large enough to justify a focused wedge but not broad enough to support premature platform claims.",
            "Narrow high-trust segments should outrank horizontal expansion work."
        ],
        "created_at": generated_at,
    }


def _build_market_share_brief(
    *,
    workspace_id: str,
    market_analysis_brief: dict[str, Any],
    competitor_dossier: dict[str, Any],
    generated_at: str,
) -> dict[str, Any]:
    lead_competitor = competitor_dossier["competitors"][0]
    return {
        "schema_version": "1.1.0",
        "market_share_brief_id": f"market_share_brief_{workspace_id}",
        "workspace_id": workspace_id,
        "title": f"Market share brief: {market_analysis_brief['market_name']}",
        "market_name": market_analysis_brief["market_name"],
        "framework_registry_ref": _framework_registry_id(workspace_id),
        "selected_framework_ids": ["competitive_displacement_map", "market_jobs_barriers"],
        "share_type": "segment_share",
        "timeframe": {
            "start_date": f"{generated_at[:4]}-01-01",
            "end_date": generated_at[:10],
        },
        "denominator": "Reachable B2B product teams actively evaluating workflow and PM operating tooling",
        "estimates": [
            {
                "subject_name": lead_competitor["name"],
                "subject_type": "company",
                "share_percent": 24.0,
                "confidence": "moderate",
                "basis": "Named incumbent share proxy for the current reachable workflow evaluation set.",
                "source_refs": lead_competitor.get("evidence_refs", []) or competitor_dossier["source_artifact_ids"][:1],
            },
            {
                "subject_name": "ProductOS reachable wedge",
                "subject_type": "product",
                "share_percent": 3.0,
                "confidence": "low",
                "basis": "Early reachable share before broad category proof exists.",
                "source_refs": competitor_dossier["source_artifact_ids"][:1] or [competitor_dossier["competitor_dossier_id"]],
            },
        ],
        "sensitivity_notes": [
            "Share assumptions move materially if bundled-platform buyers reject a second PM operating layer outright."
        ],
        "prioritization_implications": [
            "A small reachable share reinforces prioritizing proof and displacement over breadth.",
            "Bundled-platform pressure makes the evidence-backed challenger wedge more important than generic automation claims."
        ],
        "created_at": generated_at,
    }


def _build_opportunity_portfolio_view(
    *,
    workspace_id: str,
    research_brief: dict[str, Any],
    customer_pulse: dict[str, Any],
    market_analysis_brief: dict[str, Any],
    competitor_dossier: dict[str, Any],
    generated_at: str,
) -> dict[str, Any]:
    discover_score = _bounded_priority_score(strategic_fit=30, evidence_strength=24, agentic_leverage=18, burden_penalty=6, urgency=22)
    trust_score = _bounded_priority_score(strategic_fit=28, evidence_strength=20, agentic_leverage=14, burden_penalty=8, urgency=18)
    opportunities = [
        {
            "opportunity_id": "opportunity_same_day_discover_packet",
            "title": "Same-day discover packet",
            "value_at_stake": "transformational",
            "strategic_fit": "high",
            "confidence": "high",
            "time_sensitivity": "high",
            "reversibility": "moderate",
            "learning_potential": "high",
            "evidence_freshness": "fresh",
            "priority_score": discover_score,
            "priority_lane": _priority_lane(discover_score),
            "agentic_delivery_leverage": "high",
            "delivery_burden": "medium",
            "rationale": customer_pulse["priority_recommendation"]["rationale"],
            "source_artifact_ids": [
                research_brief["research_brief_id"],
                customer_pulse["customer_pulse_id"],
                market_analysis_brief["market_analysis_brief_id"],
            ],
        },
        {
            "opportunity_id": "opportunity_traceability_trust_controls",
            "title": "Traceability and trust controls",
            "value_at_stake": "high",
            "strategic_fit": "high",
            "confidence": "moderate",
            "time_sensitivity": "moderate",
            "reversibility": "easy",
            "learning_potential": "moderate",
            "evidence_freshness": "current",
            "priority_score": trust_score,
            "priority_lane": _priority_lane(trust_score),
            "agentic_delivery_leverage": "medium",
            "delivery_burden": "low",
            "rationale": competitor_dossier["prioritization_implications"][0],
            "source_artifact_ids": [
                competitor_dossier["competitor_dossier_id"],
                market_analysis_brief["market_analysis_brief_id"],
            ],
        },
    ]
    return {
        "schema_version": "1.1.0",
        "opportunity_portfolio_view_id": f"opportunity_portfolio_view_{workspace_id}",
        "workspace_id": workspace_id,
        "title": f"Opportunity portfolio view: {workspace_id}",
        "summary": "The current opportunity stack prioritizes same-day discover quality first, then trust and displacement controls.",
        "framework_registry_ref": _framework_registry_id(workspace_id),
        "selected_framework_ids": ["signal_weighted_priority"],
        "ranking_method_summary": "Rank by strategic fit, evidence freshness, urgency, agentic leverage, and delivery burden while preserving visible lanes.",
        "recommended_now_ids": [opportunities[0]["opportunity_id"]],
        "opportunities": opportunities,
        "generated_at": generated_at,
    }


def _build_prioritization_decision_record(
    *,
    workspace_id: str,
    opportunity_portfolio_view: dict[str, Any],
    generated_at: str,
) -> dict[str, Any]:
    ranked_options = [
        {
            "option_id": item["opportunity_id"],
            "option_type": "opportunity",
            "title": item["title"],
            "priority_lane": item["priority_lane"],
            "priority_score": item["priority_score"],
            "agentic_leverage": item["agentic_delivery_leverage"],
            "compliance_burden": "medium" if item["delivery_burden"] == "medium" else "low",
            "ambiguity_burden": item["delivery_burden"],
            "evidence_strength": item["confidence"],
            "rationale": item["rationale"],
            "source_artifact_ids": item["source_artifact_ids"],
        }
        for item in opportunity_portfolio_view["opportunities"]
    ]
    return {
        "schema_version": "1.0.0",
        "prioritization_decision_record_id": f"prioritization_decision_record_{workspace_id}",
        "workspace_id": workspace_id,
        "title": f"Prioritization decision record: {workspace_id}",
        "decision_scope": "Choose the next bounded discovery and strategy slice with explicit leverage and burden tradeoffs.",
        "framework_registry_ref": _framework_registry_id(workspace_id),
        "applied_framework_ids": ["signal_weighted_priority", "competitive_displacement_map"],
        "ranked_options": ranked_options,
        "selected_option_id": ranked_options[0]["option_id"],
        "decision_rationale": "The current market and customer evidence still points to the same-day discover wedge as the strongest next move before broader market-distribution work.",
        "pm_override": {
            "applied": False,
            "rationale": "The current evidence and ranking already align on the same next move."
        },
        "created_at": generated_at,
    }


def _build_feature_prioritization_brief(
    *,
    workspace_id: str,
    research_brief: dict[str, Any],
    opportunity_portfolio_view: dict[str, Any],
    market_analysis_brief: dict[str, Any],
    generated_at: str,
) -> dict[str, Any]:
    feature_refs = [
        ref["entity_id"]
        for ref in research_brief.get("linked_entity_refs", [])
        if ref.get("entity_type") == "feature"
    ]
    primary_feature = feature_refs[0] if feature_refs else f"feature_{workspace_id}_discover_loop"
    secondary_feature = feature_refs[1] if len(feature_refs) > 1 else f"feature_{workspace_id}_market_intelligence"
    primary_score = _bounded_priority_score(strategic_fit=30, evidence_strength=22, agentic_leverage=18, burden_penalty=6, urgency=22)
    secondary_score = _bounded_priority_score(strategic_fit=26, evidence_strength=18, agentic_leverage=14, burden_penalty=10, urgency=15)
    features = [
        {
            "feature_id": primary_feature,
            "title": primary_feature.replace("feature_", "").replace("_", " "),
            "priority_lane": _priority_lane(primary_score),
            "priority_score": primary_score,
            "customer_value": "high",
            "strategic_fit": "high",
            "agentic_delivery_leverage": "high",
            "compliance_burden": "medium",
            "ambiguity_burden": "medium",
            "rationale": opportunity_portfolio_view["opportunities"][0]["rationale"],
            "source_artifact_ids": [
                opportunity_portfolio_view["opportunity_portfolio_view_id"],
                market_analysis_brief["market_analysis_brief_id"],
            ],
        },
        {
            "feature_id": secondary_feature,
            "title": secondary_feature.replace("feature_", "").replace("_", " "),
            "priority_lane": _priority_lane(secondary_score),
            "priority_score": secondary_score,
            "customer_value": "moderate",
            "strategic_fit": "high",
            "agentic_delivery_leverage": "medium",
            "compliance_burden": "medium",
            "ambiguity_burden": "low",
            "rationale": "This should follow after the core discover wedge because it improves prioritization depth rather than proving first-order user value.",
            "source_artifact_ids": [
                opportunity_portfolio_view["opportunity_portfolio_view_id"],
                research_brief["research_brief_id"],
            ],
        },
    ]
    return {
        "schema_version": "1.0.0",
        "feature_prioritization_brief_id": f"feature_prioritization_brief_{workspace_id}",
        "workspace_id": workspace_id,
        "title": f"Feature prioritization brief: {workspace_id}",
        "framework_registry_ref": _framework_registry_id(workspace_id),
        "applied_framework_ids": ["signal_weighted_priority"],
        "sequencing_summary": "Keep the core discover control surface first, then expand market-intelligence and prioritization depth behind it.",
        "recommended_feature_ids": [features[0]["feature_id"]],
        "features": features,
        "generated_at": generated_at,
    }


def _update_research_brief(
    research_brief: dict[str, Any],
    normalized_sources: list[dict[str, Any]],
    external_research_review: dict[str, Any],
    competitor_dossier: dict[str, Any],
    customer_pulse: dict[str, Any],
    market_analysis_brief: dict[str, Any],
    *,
    research_notebook: dict[str, Any],
    source_note_cards: list[dict[str, Any]],
) -> dict[str, Any]:
    updated = copy.deepcopy(research_brief)
    provenance = list(updated.get("synthesis_provenance", []))
    provenance.append(
        f"Refined with {len(normalized_sources)} external sources across {', '.join(sorted({item['source_type'] for item in normalized_sources}))}."
    )
    updated["synthesis_provenance"] = provenance
    updated["known_gaps"] = list(
        dict.fromkeys(
            list(updated.get("known_gaps", []))
            + [
                gap for gap in market_analysis_brief.get("key_uncertainties", [])
            ]
        )
    )
    updated["research_notebook_ids"] = [research_notebook["research_notebook_id"]]
    updated["source_note_card_ids"] = [item["source_note_card_id"] for item in source_note_cards]
    contradiction_items = list(updated.get("contradictions", []))
    for item in external_research_review.get("contradiction_items", []):
        contradiction_items.append(
            {
                "statement": item["statement"],
                "severity": item["severity"],
                "supporting_source_note_card_ids": item["source_ids"],
            }
        )
    updated["contradictions"] = contradiction_items
    updated["linked_entity_refs"] = updated.get("linked_entity_refs", [])
    insight_source_ids = updated["source_note_card_ids"][:2]
    for insight in updated.get("insights", []):
        insight["supporting_source_note_card_ids"] = insight.get("supporting_source_note_card_ids") or insight_source_ids
    return updated


def _normalized_source_confidence(source: dict[str, Any]) -> str:
    freshness = source.get("freshness_status", "usable_with_review")
    if freshness == "fresh":
        return "high"
    if freshness == "usable_with_review":
        return "moderate"
    return "low"


def _extract_competitor_name(source: dict[str, Any]) -> str:
    title = source.get("title", "").strip()
    if not title:
        return ""
    return re.split(r"[:|\-]", title)[0].strip()


def _classify_competitor_type(name: str) -> str:
    value = name.lower()
    if any(token in value for token in ("jira", "productboard", "aha", "asana", "monday", "linear")):
        return "direct"
    if any(token in value for token in ("notion", "coda")):
        return "tech_platform"
    if any(token in value for token in ("status quo", "spreadsheet", "manual", "internal")):
        return "status_quo"
    return "vendor"


def _competitor_evidence_coverage_status(sources: list[dict[str, Any]]) -> str:
    external_sources = [
        item
        for item in sources
        if not str(item.get("uri", "")).startswith("artifact://")
    ]
    if not external_sources:
        return "internal_only"
    if len(external_sources) > 1:
        return "triangulated_external"
    return "partial_external"


def _competitor_dossier_quality(named_competitor_count: int, coverage_status: str) -> str:
    if named_competitor_count >= 2 and coverage_status == "triangulated_external":
        return "decision_ready"
    if named_competitor_count >= 1:
        return "reviewable"
    return "draft"


def _write_research_summary_doc(
    workspace_dir: Path,
    *,
    research_brief: dict[str, Any],
    external_research_review: dict[str, Any],
    competitor_dossier: dict[str, Any],
    customer_pulse: dict[str, Any],
    market_analysis_brief: dict[str, Any],
    normalized_sources: list[dict[str, Any]],
) -> None:
    docs_dir = workspace_dir / "docs" / "discovery"
    docs_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# External Research Refresh",
        "",
        f"- Sources reviewed: `{len(normalized_sources)}`",
        f"- Research brief: `{research_brief['research_brief_id']}`",
        "",
        "## Source Mix",
        "",
    ]
    for item in normalized_sources:
        published_suffix = f" ({item['published_at']})" if item.get("published_at") else ""
        lines.append(f"- `{item['source_type']}` `{item['freshness_status']}`: {item['title']}{published_suffix}")
    lines.extend(
        [
            "",
            "## Competitive Takeaway",
            "",
            competitor_dossier["credible_wedge_for_posture"],
            "",
            "## Prioritization Takeaway",
            "",
            customer_pulse["priority_recommendation"]["rationale"],
            "",
            "## Customer Signals",
            "",
        ]
    )
    for item in customer_pulse["top_pain_points"][:3]:
        lines.append(f"- {item['description']}")
    lines.extend(["", "## Market Implications", ""])
    for item in market_analysis_brief["market_role_implications"][:3]:
        lines.append(f"- {item}")
    if external_research_review.get("contradiction_items"):
        lines.extend(["", "## Contradictions", ""])
        for item in external_research_review["contradiction_items"]:
            lines.append(f"- `{item['severity']}` {item['statement']}")
    lines.extend(["", "## Remaining Questions", ""])
    for item in research_brief.get("external_research_questions", []):
        lines.append(f"- {item['question']}")
    (docs_dir / "external-research-refresh.md").write_text(
        render_governed_markdown(
            title="External Research Refresh",
            body_lines=lines,
            version_number=1,
            status="review_needed",
            updated_at=external_research_review["created_at"],
            updated_by="Research Agent",
            change_summary="Refreshed the market, competitor, and customer summary from the current governed external research packet.",
            source_artifact_ids=[external_research_review["external_research_review_id"]],
        ),
        encoding="utf-8",
    )


def _write_discovery_operations_doc(
    workspace_dir: Path,
    *,
    research_handoff: dict[str, Any],
    research_notebook: dict[str, Any],
    research_brief: dict[str, Any],
    external_research_plan: dict[str, Any],
    external_research_source_discovery: dict[str, Any],
    external_research_review: dict[str, Any],
    customer_pulse: dict[str, Any],
    source_note_cards: list[dict[str, Any]],
) -> None:
    docs_dir = workspace_dir / "docs" / "discovery"
    docs_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        f"- Handoff: `{research_handoff['handoff_id']}`",
        f"- Research notebook: `{research_notebook['research_notebook_id']}`",
        f"- Research brief: `{research_brief['research_brief_id']}`",
        f"- Search status: `{external_research_source_discovery['search_status']}`",
        f"- Review status: `{external_research_review['review_status']}`",
        "",
        "## Research Objective",
        "",
        external_research_plan["research_objective"],
        "",
        "## Planned Questions",
        "",
    ]
    for question in external_research_plan.get("prioritized_questions", [])[:5]:
        lines.append(f"- `{question['priority']}` {question['question']}")
    lines.extend(["", "## Selected Reusable Evidence", ""])
    for card in source_note_cards[:5]:
        lines.append(f"- `{card['source_note_card_id']}` {card['title']}: {card['claim']}")
    lines.extend(["", "## Empathy Synthesis", ""])
    for item in customer_pulse.get("top_pain_points", [])[:3]:
        lines.append(f"- {item['description']}")
    if customer_pulse.get("voice_of_customer_quotes"):
        lines.extend(["", "## Voice Of Customer", ""])
        for item in customer_pulse["voice_of_customer_quotes"][:3]:
            lines.append(f"- {item['quote']} ({item['source']})")
    lines.extend(["", "## Insight Reuse Spine", ""])
    lines.append(
        f"The current reusable chain is `{research_handoff['handoff_id']} -> {research_notebook['research_notebook_id']} -> {research_brief['research_brief_id']}`."
    )
    lines.append(
        "The current prioritization chain now continues through `opportunity_portfolio_view`, `prioritization_decision_record`, and `feature_prioritization_brief`."
    )
    lines.extend(["", "## Next Action", ""])
    lines.append(
        "Prepare the opportunity and validation spine using this research packet once PM review confirms the current evidence coverage is sufficient."
        if external_research_review["review_status"] == "clear"
        else "Resolve the remaining review items before turning this packet into an opportunity and validation recommendation."
    )
    (docs_dir / "research-operations.md").write_text(
        render_governed_markdown(
            title="Discovery Operations",
            body_lines=lines,
            version_number=1,
            status="decision_ready" if external_research_review["review_status"] == "clear" else "review_needed",
            updated_at=research_brief["created_at"],
            updated_by="Research Agent",
            change_summary="Published the current governed discovery-operations packet for PM review and downstream reuse.",
            source_artifact_ids=[
                research_handoff["handoff_id"],
                research_notebook["research_notebook_id"],
                research_brief["research_brief_id"],
            ],
        ),
        encoding="utf-8",
    )


def _build_research_runtime_bundle(
    *,
    research_brief: dict[str, Any],
    normalized_sources: list[dict[str, Any]],
    generated_at: str,
    research_handoff: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    source_note_cards = _build_source_note_cards(
        research_brief=research_brief,
        normalized_sources=normalized_sources,
        generated_at=generated_at,
    )
    annotated_sources = _attach_source_note_card_ids(normalized_sources, source_note_cards)
    research_notebook = _build_research_notebook(
        research_brief=research_brief,
        source_note_cards=source_note_cards,
        normalized_sources=annotated_sources,
        generated_at=generated_at,
    )
    framework_registry = _build_framework_registry(research_brief["workspace_id"], generated_at)
    external_research_review = _build_external_research_review(
        research_brief["workspace_id"], annotated_sources, generated_at
    )
    competitor_dossier = _build_competitor_dossier(
        research_brief["workspace_id"], research_brief, annotated_sources, generated_at
    )
    customer_pulse = _build_customer_pulse(
        research_brief["workspace_id"], research_brief, annotated_sources, generated_at
    )
    market_analysis_brief = _build_market_analysis_brief(
        research_brief["workspace_id"], research_brief, annotated_sources, generated_at
    )
    landscape_matrix = _build_landscape_matrix(
        workspace_id=research_brief["workspace_id"],
        competitor_dossier=competitor_dossier,
        generated_at=generated_at,
    )
    market_sizing_brief = _build_market_sizing_brief(
        workspace_id=research_brief["workspace_id"],
        research_brief=research_brief,
        market_analysis_brief=market_analysis_brief,
        competitor_dossier=competitor_dossier,
        generated_at=generated_at,
    )
    market_share_brief = _build_market_share_brief(
        workspace_id=research_brief["workspace_id"],
        market_analysis_brief=market_analysis_brief,
        competitor_dossier=competitor_dossier,
        generated_at=generated_at,
    )
    opportunity_portfolio_view = _build_opportunity_portfolio_view(
        workspace_id=research_brief["workspace_id"],
        research_brief=research_brief,
        customer_pulse=customer_pulse,
        market_analysis_brief=market_analysis_brief,
        competitor_dossier=competitor_dossier,
        generated_at=generated_at,
    )
    prioritization_decision_record = _build_prioritization_decision_record(
        workspace_id=research_brief["workspace_id"],
        opportunity_portfolio_view=opportunity_portfolio_view,
        generated_at=generated_at,
    )
    feature_prioritization_brief = _build_feature_prioritization_brief(
        workspace_id=research_brief["workspace_id"],
        research_brief=research_brief,
        opportunity_portfolio_view=opportunity_portfolio_view,
        market_analysis_brief=market_analysis_brief,
        generated_at=generated_at,
    )
    lineage_refs = [research_notebook["research_notebook_id"], research_brief["research_brief_id"]]
    competitor_dossier["source_artifact_ids"] = list(
        dict.fromkeys([*lineage_refs, *competitor_dossier.get("source_artifact_ids", [])])
    )
    customer_pulse["source_artifact_ids"] = list(
        dict.fromkeys([*lineage_refs, *customer_pulse.get("source_artifact_ids", [])])
    )
    market_analysis_brief["source_artifact_ids"] = list(
        dict.fromkeys([*lineage_refs, *market_analysis_brief.get("source_artifact_ids", [])])
    )
    landscape_matrix["source_artifact_ids"] = list(
        dict.fromkeys([*lineage_refs, *landscape_matrix.get("source_artifact_ids", [])])
    )
    updated_research_brief = _update_research_brief(
        research_brief,
        annotated_sources,
        external_research_review,
        competitor_dossier,
        customer_pulse,
        market_analysis_brief,
        research_notebook=research_notebook,
        source_note_cards=source_note_cards,
    )
    bundle: dict[str, dict[str, Any]] = {
        "framework_registry": framework_registry,
        "research_notebook": research_notebook,
        "research_brief": updated_research_brief,
        "external_research_review": external_research_review,
        "competitor_dossier": competitor_dossier,
        "customer_pulse": customer_pulse,
        "market_analysis_brief": market_analysis_brief,
        "landscape_matrix": landscape_matrix,
        "market_sizing_brief": market_sizing_brief,
        "market_share_brief": market_share_brief,
        "opportunity_portfolio_view": opportunity_portfolio_view,
        "prioritization_decision_record": prioritization_decision_record,
        "feature_prioritization_brief": feature_prioritization_brief,
        "source_note_cards": _source_note_card_file_map(source_note_cards),
    }
    if research_handoff is not None:
        bundle["research_handoff"] = research_handoff
    return bundle


def sync_canonical_discovery_operations_artifacts(
    workspace_dir: Path | str,
    *,
    bundle: dict[str, dict[str, Any]],
) -> list[str]:
    workspace = Path(workspace_dir).resolve()
    artifacts_dir = workspace / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = workspace / "workspace_manifest.yaml"
    synced_files: list[str] = []
    for artifact_name, filename in DISCOVERY_OPERATIONS_ARTIFACT_FILENAMES.items():
        payload = bundle.get(artifact_name)
        if payload is None:
            continue
        _write_json(artifacts_dir / filename, payload)
        _append_manifest_artifact_path(manifest_path, f"artifacts/{filename}")
        synced_files.append(filename)
    for filename, payload in bundle.get("source_note_cards", {}).items():
        _write_json(artifacts_dir / filename, payload)
        _append_manifest_artifact_path(manifest_path, f"artifacts/{filename}")
        synced_files.append(filename)
    selected_manifest = bundle.get("selected_research_manifest")
    if selected_manifest is not None:
        selected_manifest_path = workspace / "outputs" / "research" / "external-research-manifest.selected.json"
        _write_selected_manifest(selected_manifest_path, selected_manifest)
        synced_files.append(_relative_path(selected_manifest_path, workspace))
    if all(
        bundle.get(key) is not None
        for key in (
            "research_handoff",
            "research_notebook",
            "research_brief",
            "external_research_plan",
            "external_research_source_discovery",
            "external_research_review",
            "customer_pulse",
        )
    ):
        _write_discovery_operations_doc(
            workspace,
            research_handoff=bundle["research_handoff"],
            research_notebook=bundle["research_notebook"],
            research_brief=bundle["research_brief"],
            external_research_plan=bundle["external_research_plan"],
            external_research_source_discovery=bundle["external_research_source_discovery"],
            external_research_review=bundle["external_research_review"],
            customer_pulse=bundle["customer_pulse"],
            source_note_cards=list(bundle.get("source_note_cards", {}).values()),
        )
    return synced_files


def load_canonical_discovery_operations_bundle(workspace_dir: Path | str) -> dict[str, dict[str, Any]] | None:
    workspace = Path(workspace_dir).resolve()
    artifacts_dir = workspace / "artifacts"
    bundle: dict[str, dict[str, Any]] = {}
    for artifact_name, filename in DISCOVERY_OPERATIONS_ARTIFACT_FILENAMES.items():
        payload = _load_json(artifacts_dir / filename) if (artifacts_dir / filename).exists() else None
        if payload is None:
            return None
        bundle[artifact_name] = payload
    bundle["selected_research_manifest"] = (
        _load_json(workspace / "outputs" / "research" / "external-research-manifest.selected.json")
        if (workspace / "outputs" / "research" / "external-research-manifest.selected.json").exists()
        else None
    )
    bundle["source_note_cards"] = {
        path.name: _load_json(path)
        for path in sorted(artifacts_dir.glob("source_note_card_*.json"))
        if not path.name.endswith(".example.json")
    }
    selected_manifest = bundle.get("selected_research_manifest") or {}
    selected_sources = selected_manifest.get("sources", []) if isinstance(selected_manifest, dict) else []
    discovery = bundle["external_research_source_discovery"]
    if discovery.get("search_status") == "no_results" or not selected_sources:
        return None
    if bundle["external_research_review"].get("review_status") != "clear":
        return None
    return bundle


def research_workspace_from_manifest(
    root_dir: Path | str,
    *,
    workspace_dir: Path | str,
    manifest_path: Path | str,
    generated_at: str,
    persist: bool = True,
    research_brief_override: dict[str, Any] | None = None,
    research_handoff: dict[str, Any] | None = None,
    problem_brief: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    workspace = Path(workspace_dir).resolve()
    manifest = Path(manifest_path).resolve()
    research_brief = research_brief_override or _load_workspace_research_brief(workspace, generated_at)
    normalized_sources = _normalize_sources(_load_source_manifest(manifest), generated_at)
    if not normalized_sources:
        normalized_sources = _fallback_normalized_sources(
            problem_brief=problem_brief,
            research_brief=research_brief,
            generated_at=generated_at,
        )
    bundle = _build_research_runtime_bundle(
        research_brief=research_brief,
        normalized_sources=normalized_sources,
        generated_at=generated_at,
        research_handoff=research_handoff,
    )

    if persist:
        sync_canonical_discovery_operations_artifacts(workspace, bundle=bundle)
        _write_research_summary_doc(
            workspace,
            research_brief=bundle["research_brief"],
            external_research_review=bundle["external_research_review"],
            competitor_dossier=bundle["competitor_dossier"],
            customer_pulse=bundle["customer_pulse"],
            market_analysis_brief=bundle["market_analysis_brief"],
            normalized_sources=normalized_sources,
        )

    return bundle
