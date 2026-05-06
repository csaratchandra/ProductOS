"""ProductOS V11 Living Markdown Renderer: Renders readable documents from structured artifacts."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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
    
    template_map = {
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
    
    if doc_key not in template_map:
        raise ValueError(f"Unknown document key: {doc_key}. Available: {list(template_map.keys())}")
    
    config = template_map[doc_key]
    template_content = load_template(config["template"])
    sources = resolve_source_artifacts(config["sources"], workspace_dir)
    
    missing_sources = [ref for ref, data in sources.items() if data is None]
    if missing_sources:
        raise ValueError(f"Missing source artifacts: {missing_sources}")
    
    rendered = _apply_template(template_content, sources, doc_key, generated_at)
    
    existing_path = workspace_dir / "docs" / f"{doc_key}.md"
    if existing_path.exists():
        existing_content = existing_path.read_text(encoding="utf-8")
        rendered = preserve_annotations(existing_content, rendered)
    
    return rendered


def _apply_template(
    template: str,
    sources: dict[str, Any],
    doc_key: str,
    generated_at: str,
) -> str:
    """Apply a template with source data (simplified Jinja2-like rendering)."""
    result = template
    
    for ref, data in sources.items():
        if data is None:
            continue
        
        artifact_id = data.get(f"{doc_key.replace('-', '_')}_id", ref)
        title = data.get("title", data.get("name", ref))
        
        result = result.replace(f"{{{{ {ref}.title }}}}", title)
        result = result.replace(f"{{{{ {ref}.id }}}}", artifact_id)
        
        if "description" in data:
            result = result.replace(f"{{{{ {ref}.description }}}}", data["description"])
        if "summary" in data:
            result = result.replace(f"{{{{ {ref}.summary }}}}", data["summary"])
        if "problem_statement" in data:
            result = result.replace(f"{{{{ {ref}.problem_statement }}}}", data["problem_statement"])
        if "solution_approach" in data:
            result = result.replace(f"{{{{ {ref}.solution_approach }}}}", data["solution_approach"])
        if "out_of_scope" in data:
            out_of_scope = "\n".join(f"- {item}" for item in data["out_of_scope"])
            result = result.replace(f"{{{{ {ref}.out_of_scope }}}}", out_of_scope)
        if "acceptance_criteria" in data:
            criteria = "\n".join(f"- {item}" for item in data["acceptance_criteria"])
            result = result.replace(f"{{{{ {ref}.acceptance_criteria }}}}", criteria)
    
    result = result.replace("{{ generated_at }}", generated_at)
    result = result.replace("{{ doc_key }}", doc_key)
    
    return result
