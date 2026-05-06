"""ProductOS V11 Export Pipeline: Renders living artifacts to multiple formats."""

from __future__ import annotations

import json
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


def export_artifact(
    artifact_ref: str,
    fmt: str,
    workspace_dir: Path,
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Export a structured artifact to the specified format.
    
    Args:
        artifact_ref: Path to the source artifact (e.g., "artifacts/prd.json")
        fmt: Export format (markdown, deck, agent_brief, stakeholder_update, battle_card, one_pager)
        workspace_dir: Path to the workspace
        generated_at: Optional timestamp
    
    Returns:
        Exported content as a dict with format-specific keys
    """
    if generated_at is None:
        generated_at = _default_timestamp()
    
    artifact_path = workspace_dir / artifact_ref
    if not artifact_path.exists():
        raise FileNotFoundError(f"Artifact not found: {artifact_path}")
    
    artifact = _load_json_if_exists(artifact_path)
    if artifact is None:
        raise ValueError(f"Failed to load artifact: {artifact_path}")
    
    exporters = {
        "markdown": _export_markdown,
        "deck": _export_deck,
        "agent_brief": _export_agent_brief,
        "stakeholder_update": _export_stakeholder_update,
        "battle_card": _export_battle_card,
        "one_pager": _export_one_pager,
    }
    
    if fmt not in exporters:
        raise ValueError(f"Unsupported export format: {fmt}. Available: {list(exporters.keys())}")
    
    return exporters[fmt](artifact, workspace_dir, generated_at)


def _export_markdown(artifact: dict, workspace_dir: Path, generated_at: str) -> dict:
    """Export artifact as markdown living document."""
    return {
        "format": "markdown",
        "content": f"# {artifact.get('title', 'Untitled')}\n\n{artifact.get('description', artifact.get('summary', 'No description available.'))}\n\n---\n\n*Generated at {generated_at}*",
        "generated_at": generated_at,
        "source_artifact": artifact.get("artifact_id", "unknown"),
    }


def _export_deck(artifact: dict, workspace_dir: Path, generated_at: str) -> dict:
    """Export artifact as presentation brief for deck generation."""
    return {
        "format": "deck",
        "presentation_brief": {
            "title": artifact.get("title", "Untitled"),
            "narrative": artifact.get("description", artifact.get("summary", "")),
            "key_points": artifact.get("key_points", []),
            "audience": artifact.get("audience", ["PM"]),
        },
        "generated_at": generated_at,
        "source_artifact": artifact.get("artifact_id", "unknown"),
    }


def _export_agent_brief(artifact: dict, workspace_dir: Path, generated_at: str) -> dict:
    """Export artifact as agent-optimized brief for AI agent consumption."""
    out_of_scope = artifact.get("out_of_scope", [])
    acceptance_criteria = artifact.get("acceptance_criteria", [])
    
    return {
        "format": "agent_brief",
        "content": f"""# Agent Brief: {artifact.get('title', 'Untitled')}

## 1. Intent & Boundaries
- Problem: {artifact.get('problem_statement', artifact.get('description', 'N/A'))}
- EXPLICIT OUT_OF_SCOPE:
{chr(10).join(f'  - {item}' for item in out_of_scope) if out_of_scope else '  - None specified'}

## 2. Acceptance Criteria
{chr(10).join(f'- {criterion}' for criterion in acceptance_criteria) if acceptance_criteria else '- No criteria specified'}

## 3. Context
- Generated: {generated_at}
- Source: {artifact.get('artifact_id', 'unknown')}
""",
        "generated_at": generated_at,
        "source_artifact": artifact.get("artifact_id", "unknown"),
        "boundaries_strong": len(out_of_scope) >= 3,
    }


def _export_stakeholder_update(artifact: dict, workspace_dir: Path, generated_at: str) -> dict:
    """Export artifact as executive summary for stakeholder communication."""
    return {
        "format": "stakeholder_update",
        "executive_summary": artifact.get("summary", artifact.get("description", "No summary available.")),
        "key_decisions": artifact.get("decisions", []),
        "risks": artifact.get("risks", artifact.get("risk_summary", [])),
        "next_steps": artifact.get("next_steps", artifact.get("next_action", [])),
        "generated_at": generated_at,
        "source_artifact": artifact.get("artifact_id", "unknown"),
    }


def _export_battle_card(artifact: dict, workspace_dir: Path, generated_at: str) -> dict:
    """Export artifact as competitive battle card."""
    return {
        "format": "battle_card",
        "competitor": artifact.get("competitor_name", artifact.get("title", "Unknown")),
        "strengths": artifact.get("strengths", []),
        "weaknesses": artifact.get("weaknesses", []),
        "positioning": artifact.get("positioning", ""),
        "counter_messaging": artifact.get("counter_messaging", []),
        "generated_at": generated_at,
        "source_artifact": artifact.get("artifact_id", "unknown"),
    }


def _export_one_pager(artifact: dict, workspace_dir: Path, generated_at: str) -> dict:
    """Export artifact as product one-pager overview."""
    return {
        "format": "one_pager",
        "title": artifact.get("title", "Untitled"),
        "problem": artifact.get("problem_statement", artifact.get("customer_problem", "")),
        "solution": artifact.get("solution_approach", artifact.get("description", "")),
        "value_proposition": artifact.get("value_proposition", artifact.get("summary", "")),
        "target_market": artifact.get("target_market", artifact.get("market", "")),
        "generated_at": generated_at,
        "source_artifact": artifact.get("artifact_id", "unknown"),
    }
