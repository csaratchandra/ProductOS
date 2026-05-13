"""ProductOS V13 Document Ingestion: LLM-driven parsing of existing PRDs, strategy docs, and meeting notes."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .llm import LLMProvider, default_provider


MULTI_MODAL_INGESTION_SCHEMA = "multi_modal_ingestion_report.schema.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _slug(value: str) -> str:
    normalized = "".join(char.lower() if char.isalnum() else "_" for char in value)
    while "__" in normalized:
        normalized = normalized.replace("__", "_")
    return normalized.strip("_")


DOC_ENTITY_EXTRACTION_PROMPT = """You are analyzing a product document for a product takeover.
Extract the following structured entities from the document text:

1. Problems - what customer problems or pain points are described?
2. Personas - what user personas or roles are mentioned?  
3. Features - what product features or capabilities are discussed?
4. Decisions - what strategic or product decisions have been made?
5. Competitors - what competitors or alternatives are referenced?
6. Metrics - what KPIs, targets, or measurements are mentioned?

For each entity, provide a unique ID, name, brief description, and the confidence level.

Respond ONLY with valid JSON matching the schema.
Do not include markdown formatting, explanations, or code fences."""

CONTRADICTION_DETECTION_PROMPT = """You are analyzing multiple product documents for contradictions.
Compare the following documents and identify any contradictions between them.
A contradiction is when two documents make claims that cannot both be true.

For each contradiction found, provide:
1. A description of the contradiction
2. Which sources are involved
3. The severity (low/medium/high/critical)
4. A resolution recommendation

Respond ONLY with valid JSON matching the schema.
Do not include markdown formatting, explanations, or code fences."""


def ingest_document(
    doc_path: Path,
    workspace_dir: Path | None = None,
    *,
    llm: LLMProvider | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Parse a document and extract structured entities.

    Performs:
    - Content extraction (markdown, plain text)
    - Entity extraction via LLM (or heuristic fallback)
    - Source note card generation
    """
    provider = llm or default_provider()
    generated_at = generated_at or _now_iso()
    source_id = f"src_{_slug(doc_path.stem)}_{generated_at[:10]}"
    content = _extract_document_text(doc_path)

    doc_type = _classify_document_type(doc_path)

    entities = _extract_entities(content, provider)

    return {
        "source_id": source_id,
        "source_type": doc_type,
        "source_path": str(doc_path),
        "extraction_confidence": "inferred",
        "extracted_entities": entities,
        "ingested_at": generated_at,
    }


def _classify_document_type(doc_path: Path) -> str:
    """Classify document type based on filename and content heuristics."""
    name_lower = doc_path.stem.lower()
    suffix = doc_path.suffix.lower()

    type_map: list[tuple[str, str]] = [
        ("prd", "prd_document"),
        ("strategy", "strategy_doc"),
        ("roadmap", "strategy_doc"),
        ("competitor", "competitor_analysis"),
        ("transcript", "transcript"),
        ("meeting", "meeting_notes"),
        ("notes", "meeting_notes"),
        ("research", "research_report"),
        ("spec", "prd_document"),
        ("requirements", "prd_document"),
        ("brief", "strategy_doc"),
    ]

    for keyword, doc_type in type_map:
        if keyword in name_lower:
            return doc_type

    if suffix in {".txt", ".md"}:
        return "strategy_doc"
    if suffix in {".html", ".pdf"}:
        return "research_report"

    return "other"


def _extract_document_text(doc_path: Path) -> str:
    """Extract text content from a document file."""
    try:
        if doc_path.suffix.lower() in {".md", ".txt", ".html"}:
            return doc_path.read_text(encoding="utf-8", errors="ignore")
        return f"[Unsupported format: {doc_path.suffix}]"
    except Exception:
        return ""


def _extract_entities(content: str, provider: LLMProvider) -> dict[str, list[str]]:
    """Extract structured entities from document content."""
    if not content.strip():
        return {
            "problems": [],
            "personas": [],
            "features": [],
            "decisions": [],
            "competitors": [],
            "metrics": [],
        }

    try:
        schema = {
            "type": "object",
            "properties": {
                "problems": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Customer problems or pain points identified",
                },
                "personas": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "User personas or roles mentioned",
                },
                "features": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Product features or capabilities discussed",
                },
                "decisions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Strategic or product decisions made",
                },
                "competitors": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Competitors or alternatives referenced",
                },
                "metrics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "KPIs, targets, or measurements mentioned",
                },
            },
            "required": ["problems", "personas", "features", "decisions", "competitors", "metrics"],
        }
        result = provider.generate_structured(
            f"{DOC_ENTITY_EXTRACTION_PROMPT}\n\nDocument content:\n{content[:8000]}",
            schema,
        )
        return {
            "problems": result.get("problems", []),
            "personas": result.get("personas", []),
            "features": result.get("features", []),
            "decisions": result.get("decisions", []),
            "competitors": result.get("competitors", []),
            "metrics": result.get("metrics", []),
        }
    except Exception:
        return _heuristic_extract_entities(content)


def _heuristic_extract_entities(content: str) -> dict[str, list[str]]:
    """Fallback entity extraction using pattern matching."""
    entities: dict[str, list[str]] = {
        "problems": [],
        "personas": [],
        "features": [],
        "decisions": [],
        "competitors": [],
        "metrics": [],
    }

    lines = content.splitlines()
    for line in lines:
        lower = line.strip().lower()
        if not lower:
            continue

        if any(k in lower for k in ("problem", "pain point", "challenge", "frustration")):
            entities["problems"].append(line.strip()[:120])

        if any(k in lower for k in ("persona", "user role", "who will", "target user")):
            entities["personas"].append(line.strip()[:120])

        if any(k in lower for k in ("feature", "capability", "functionality", "ability to")):
            entities["features"].append(line.strip()[:120])

        if any(k in lower for k in ("decision", "decided", "chose", "selected", "opted")):
            entities["decisions"].append(line.strip()[:120])

        if any(k in lower for k in ("competitor", "alternative", "versus", "vs ")):
            entities["competitors"].append(line.strip()[:120])

        if any(k in lower for k in ("kpi", "metric", "target", "goal", "%", "increase")):
            entities["metrics"].append(line.strip()[:120])

    return entities


def detect_contradictions(
    source_entries: list[dict[str, Any]],
    *,
    llm: LLMProvider | None = None,
) -> list[dict[str, Any]]:
    """Detect contradictions across multiple ingested sources."""
    provider = llm or default_provider()

    if len(source_entries) < 2:
        return []

    contradictions: list[dict[str, Any]] = []

    for i in range(len(source_entries)):
        for j in range(i + 1, len(source_entries)):
            src_a = source_entries[i]
            src_b = source_entries[j]
            match = _find_contradiction(src_a, src_b)
            if match:
                contradictions.append(match)

    return contradictions


def _find_contradiction(
    src_a: dict[str, Any],
    src_b: dict[str, Any],
) -> dict[str, Any] | None:
    """Check a pair of sources for contradictions."""
    entities_a = src_a.get("extracted_entities", {})
    entities_b = src_b.get("extracted_entities", {})

    features_a = set(entities_a.get("features", []))
    features_b = set(entities_b.get("features", []))

    overlapping = features_a & features_b
    if overlapping:
        return {
            "contradiction_id": f"contra_{_slug(src_a['source_id'])}_{_slug(src_b['source_id'])}",
            "description": f"Both sources describe overlapping features: {', '.join(list(overlapping)[:3])}",
            "sources_involved": [src_a["source_id"], src_b["source_id"]],
            "severity": "medium",
        }

    segments_a = set(entities_a.get("segments", []))
    segments_b = set(entities_b.get("segments", []))
    shared_segments = segments_a & segments_b
    features_only_a = features_a - features_b
    features_only_b = features_b - features_a

    for segment in shared_segments:
        if features_only_a and features_only_b:
            return {
                "contradiction_id": f"contra_feature_gap_{_slug(src_a['source_id'])}_{_slug(src_b['source_id'])}",
                "description": (
                    f"Documents mention segment '{segment}' but describe different feature sets: "
                    f"Doc A mentions {list(features_only_a)[:2]}, Doc B mentions {list(features_only_b)[:2]}"
                ),
                "sources_involved": [src_a["source_id"], src_b["source_id"]],
                "severity": "low",
            }

    return None


def build_ingestion_report(
    workspace_dir: Path,
    source_entries: list[dict[str, Any]],
    contradictions: list[dict[str, Any]],
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build the multi_modal_ingestion_report artifact."""
    generated_at = generated_at or _now_iso()
    report_id = f"ingest_{workspace_dir.name}_{generated_at[:10]}"

    domain_counters: dict[str, int] = {}
    for entry in source_entries:
        dtype = entry.get("source_type", "other")
        domain_counters[dtype] = domain_counters.get(dtype, 0) + 1

    total = len(source_entries)
    domain_areas = []
    for domain, count in sorted(domain_counters.items()):
        coverage_pct = round(count / max(total, 1) * 100, 1)
        if coverage_pct >= 50:
            status = "well_covered"
        elif coverage_pct >= 20:
            status = "partial"
        else:
            status = "gap_heavy"
        domain_areas.append({
            "domain": domain,
            "coverage_pct": coverage_pct,
            "status": status,
        })

    return {
        "schema_version": "1.0.0",
        "ingestion_report_id": report_id,
        "workspace_id": workspace_dir.name,
        "title": f"Ingestion Report: {workspace_dir.name}",
        "ingested_sources": source_entries,
        "contradictions_found": contradictions,
        "ingestion_coverage": {
            "domain_areas": domain_areas,
            "overall_coverage_pct": round(total / max(total, 10) * 100, 1),
            "gap_areas": [d["domain"] for d in domain_areas if d["status"] == "gap_heavy"],
        },
        "generated_at": generated_at,
    }


def classify_file_content_aware(
    file_path: Path,
    source_dir: Path,
    *,
    llm: LLMProvider | None = None,
) -> dict[str, Any]:
    """Content-aware file classification (replaces pure suffix/name matching).

    Uses LLM to classify based on actual content, falls back to heuristic.
    """
    provider = llm or default_provider()

    content_preview = ""
    try:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        content_preview = text[:500]
    except Exception:
        pass

    suffix = file_path.suffix.lower()
    name = file_path.name.lower()
    path_text = file_path.relative_to(source_dir).as_posix().lower() if source_dir else file_path.name

    if not content_preview.strip():
        return _heuristic_classify(suffix, name, path_text)

    try:
        schema = {
            "type": "object",
            "properties": {
                "classification": {
                    "type": "string",
                    "enum": [
                        "research_note", "visual_asset", "presentation_or_document",
                        "transcript_or_session_note", "workspace_note",
                        "prd_document", "strategy_document", "meeting_notes",
                        "technical_documentation", "design_spec",
                    ],
                },
                "input_type": {
                    "type": "string",
                    "enum": ["raw_note", "screenshot", "document", "transcript"],
                },
                "inbox_lane": {
                    "type": "string",
                    "enum": ["raw-notes", "screenshots", "documents", "transcripts"],
                },
                "confidence": {
                    "type": "string",
                    "enum": ["observed", "inferred", "uncertain"],
                },
                "purpose_summary": {"type": "string"},
            },
            "required": ["classification", "input_type", "inbox_lane", "confidence"],
        }

        result = provider.generate_structured(
            f"Classify this file based on its content:\n"
            f"Filename: {file_path.name}\n"
            f"Content preview:\n{content_preview}",
            schema,
        )

        classification = result.get("classification", "workspace_note")
        input_type = result.get("input_type", "raw_note")
        inbox_lane = result.get("inbox_lane", "raw-notes")
        confidence = result.get("confidence", "inferred")

        if confidence == "uncertain":
            base = _heuristic_classify(suffix, name, path_text)
            classification = base["classification"]
            input_type = base["input_type"]
            inbox_lane = base["inbox_lane"]
            confidence = "uncertain"

        recommended_workflow_ids = _workflows_for_classification(classification)
        derived_artifact_ids = _artifacts_for_classification(classification)

        return {
            "path": file_path,
            "relative_path": str(file_path.relative_to(source_dir)) if source_dir else file_path.name,
            "classification": classification,
            "input_type": input_type,
            "inbox_lane": inbox_lane,
            "confidence": confidence,
            "recommended_workflow_ids": recommended_workflow_ids,
            "derived_artifact_ids": derived_artifact_ids,
        }
    except Exception:
        return _heuristic_classify(suffix, name, path_text)


def _heuristic_classify(suffix: str, name: str, path_text: str) -> dict[str, Any]:
    """Pure heuristic file classification (backup when no LLM available)."""
    classification = "workspace_note"
    input_type = "raw_note"
    inbox_lane = "raw-notes"

    if suffix in {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp"}:
        classification = "visual_asset"
        input_type = "screenshot"
        inbox_lane = "screenshots"
    elif suffix in {".html", ".pdf"}:
        classification = "presentation_or_document"
        input_type = "document"
        inbox_lane = "documents"
    elif suffix in {".txt"} or "transcript" in name.lower():
        classification = "transcript_or_session_note"
        input_type = "transcript"
        inbox_lane = "transcripts"
    elif "research" in path_text and suffix in {".md", ".html"}:
        classification = "research_note"
        input_type = "document" if suffix == ".html" else "raw_note"
        inbox_lane = "documents" if suffix == ".html" else "raw-notes"

    recommended_workflow_ids = _workflows_for_classification(classification)
    derived_artifact_ids = _artifacts_for_classification(classification)

    return {
        "path": None,
        "relative_path": path_text,
        "classification": classification,
        "input_type": input_type,
        "inbox_lane": inbox_lane,
        "confidence": "inferred",
        "recommended_workflow_ids": recommended_workflow_ids,
        "derived_artifact_ids": derived_artifact_ids,
    }


def _workflows_for_classification(classification: str) -> list[str]:
    workflows: dict[str, list[str]] = {
        "research_note": ["wf_inbox_to_normalized_evidence", "wf_research_command_center", "wf_problem_brief_to_prd"],
        "visual_asset": ["wf_inbox_to_normalized_evidence", "wf_artifact_to_readable_doc"],
        "presentation_or_document": ["wf_inbox_to_normalized_evidence", "wf_artifact_to_readable_doc"],
        "transcript_or_session_note": ["wf_inbox_to_normalized_evidence", "wf_problem_brief_to_prd"],
        "prd_document": ["wf_inbox_to_normalized_evidence", "wf_problem_brief_to_prd"],
        "strategy_document": ["wf_inbox_to_normalized_evidence", "wf_research_command_center"],
        "meeting_notes": ["wf_inbox_to_normalized_evidence"],
        "technical_documentation": ["wf_inbox_to_normalized_evidence", "wf_artifact_to_readable_doc"],
        "design_spec": ["wf_inbox_to_normalized_evidence", "wf_artifact_to_readable_doc"],
    }
    return workflows.get(classification, ["wf_inbox_to_normalized_evidence"])


def _artifacts_for_classification(classification: str) -> list[str]:
    artifacts: dict[str, list[str]] = {
        "research_note": ["research_notebook_workspace_adoption", "research_brief_workspace_adoption", "problem_brief_workspace_adoption"],
        "visual_asset": ["concept_brief_workspace_adoption", "prd_workspace_adoption"],
        "presentation_or_document": ["concept_brief_workspace_adoption", "prd_workspace_adoption"],
        "transcript_or_session_note": ["problem_brief_workspace_adoption", "prd_workspace_adoption"],
        "prd_document": ["problem_brief_workspace_adoption", "prd_workspace_adoption"],
        "strategy_document": ["research_brief_workspace_adoption"],
        "meeting_notes": ["idea_record_workspace_adoption"],
        "technical_documentation": ["prd_workspace_adoption"],
        "design_spec": ["prd_workspace_adoption"],
    }
    return artifacts.get(classification, ["idea_record_workspace_adoption"])
