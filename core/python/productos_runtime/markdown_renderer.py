"""ProductOS V11 Living Markdown Renderer: Renders readable documents from structured artifacts."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jinja2 import BaseLoader, Environment


DOC_CONFIGS = {
    "prd": {
        "template": "prd.md.jinja2",
        "sources": [
            "artifacts/prd.json",
            "artifacts/problem_brief.json",
            "artifacts/research_notebook.json",
            "artifacts/acceptance_criteria_set.json",
        ],
    },
    "problem-brief": {
        "template": "problem-brief.md.jinja2",
        "sources": [
            "artifacts/problem_brief.json",
            "artifacts/customer_pulse.json",
            "artifacts/persona_narrative_card.json",
        ],
    },
    "strategy-brief": {
        "template": "strategy-brief.md.jinja2",
        "sources": [
            "artifacts/strategy_context_brief.json",
            "artifacts/competitor_dossier.json",
            "artifacts/landscape_matrix.json",
        ],
    },
    "user-journey": {
        "template": "user-journey.md.jinja2",
        "sources": [
            "artifacts/user_journey_map.json",
            "artifacts/persona_narrative_card.json",
            "artifacts/empathy_map.json",
        ],
    },
}


def _load_json_if_exists(path: Path) -> dict | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _default_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_template(template_name: str) -> str:
    """Load a Jinja2 template from the living_docs template directory."""
    template_path = Path(__file__).parents[2] / "templates" / "living_docs" / template_name
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    return template_path.read_text(encoding="utf-8")


def resolve_source_artifacts(
    source_refs: list[str],
    workspace_dir: Path,
) -> dict[str, Any]:
    """Load all source artifacts referenced by a document."""
    artifacts = {}
    for ref in source_refs:
        artifact_path = workspace_dir / ref
        if artifact_path.exists():
            data = _load_json_if_exists(artifact_path)
            if data:
                artifacts[ref] = data
        else:
            artifacts[ref] = None
    return artifacts


def preserve_annotations(
    existing_markdown: str,
    new_markdown: str,
) -> str:
    """Preserve PM manual annotations from existing markdown in the new rendered version."""
    annotation_pattern = r"<!-- PM NOTE: (.*?) -->"
    annotations = re.findall(annotation_pattern, existing_markdown)
    
    if not annotations:
        return new_markdown
    
    result = new_markdown
    for annotation in annotations:
        result += f"\n\n<!-- PM NOTE: {annotation} -->"
    
    return result


def render_living_document(
    doc_key: str,
    workspace_dir: Path,
    *,
    generated_at: str | None = None,
) -> str:
    """Render a living document from structured artifacts and templates.
    
    Args:
        doc_key: Document key (e.g., "prd", "problem-brief", "strategy-brief", "user-journey")
        workspace_dir: Path to the workspace
        generated_at: Optional timestamp
    
    Returns:
        Rendered markdown content
    """
    if generated_at is None:
        generated_at = _default_timestamp()
    
    if doc_key not in DOC_CONFIGS:
        raise ValueError(f"Unknown document key: {doc_key}. Available: {list(DOC_CONFIGS.keys())}")

    config = DOC_CONFIGS[doc_key]
    template_content = load_template(config["template"])
    sources = resolve_source_artifacts(config["sources"], workspace_dir)
    
    primary_source = config["sources"][0]
    if sources.get(primary_source) is None:
        raise ValueError(f"Missing source artifacts: ['{primary_source}']")
    
    rendered = _apply_template(template_content, sources, doc_key, generated_at)
    
    existing_path = workspace_dir / "docs" / f"{doc_key}.md"
    if existing_path.exists():
        existing_content = existing_path.read_text(encoding="utf-8")
        rendered = preserve_annotations(existing_content, rendered)
    
    return rendered


def render_all_living_documents(
    workspace_dir: Path,
    *,
    generated_at: str | None = None,
) -> dict[str, str]:
    generated_at = generated_at or _default_timestamp()
    rendered_docs: dict[str, str] = {}
    for doc_key in DOC_CONFIGS:
        try:
            rendered_docs[doc_key] = render_living_document(
                doc_key,
                workspace_dir,
                generated_at=generated_at,
            )
        except ValueError:
            continue
    return rendered_docs


def _apply_template(
    template: str,
    sources: dict[str, Any],
    doc_key: str,
    generated_at: str,
) -> str:
    """Apply a Jinja2 template with source data."""
    env = Environment(loader=BaseLoader(), autoescape=False)
    jinja_template = env.from_string(template)

    # Build context: primary artifact fields at top level, plus helpers
    context: dict[str, Any] = {
        "generated_at": generated_at,
        "doc_key": doc_key,
    }

    # Flatten primary source artifacts into context
    for ref, data in sources.items():
        if data is None:
            continue
        for key, value in data.items():
            if key not in context or key in ("schema_version",):
                # Prefer the first artifact that provides a given key
                if key not in context:
                    context[key] = value

    # Helper: bullet-list formatter for list fields
    def _bullet_list(items: list[str] | None) -> str:
        if not items:
            return ""
        return "\n".join(f"- {item}" for item in items)

    # Apply list-formatter aliases expected by templates
    for list_key in ("out_of_scope", "acceptance_criteria", "criteria", "findings", "quotes"):
        if list_key in context and isinstance(context[list_key], list):
            context[list_key] = _bullet_list(context[list_key])

    # Fallbacks for fields commonly referenced in templates but not always present
    fallbacks = {
        "title": context.get("title", "Untitled"),
        "problem_statement": context.get("problem_statement", context.get("summary", "")),
        "solution_approach": context.get("solution_approach", ""),
        "evidence_quotes": context.get("evidence_quotes", context.get("quotes", "")),
        "scope_summary": context.get("scope_summary", context.get("description", "")),
        "timing_rationale": context.get("timing_rationale", ""),
        "affected_segments": context.get("affected_segments", ""),
        "desired_outcomes": context.get("desired_outcomes", ""),
    }
    for key, value in fallbacks.items():
        if key not in context or not context[key]:
            context[key] = value

    return jinja_template.render(**context)
