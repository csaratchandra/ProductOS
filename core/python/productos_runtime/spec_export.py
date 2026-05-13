"""ProductOS V13 Spec Export: Multi-format agent-native export pipeline.

Supports:
- Structured JSON bundle (agent_native)
- OpenCode/Codex tool definitions (agent_tools)
- GitHub issues/epics/tasks (github)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _slug(value: str) -> str:
    normalized = "".join(char.lower() if char.isalnum() else "_" for char in value)
    while "__" in normalized:
        normalized = normalized.replace("__", "_")
    return normalized.strip("_")


def export_agent_native_json(
    build_spec_bundle: dict[str, Any],
    *,
    output_path: Path | None = None,
) -> dict[str, Any]:
    """Export spec bundle as structured agent-native JSON.

    Returns the bundle itself (it is already in agent-native format).
    Optionally writes to a file.
    """
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(build_spec_bundle, indent=2) + "\n",
            encoding="utf-8",
        )

    # Add execution summary for agent consumption
    features = build_spec_bundle.get("features", [])
    execution_graph = build_spec_bundle.get("execution_graph", {})
    nodes = execution_graph.get("nodes", [])

    return {
        "bundle": build_spec_bundle,
        "execution_summary": {
            "total_features": len(features),
            "total_stories": sum(len(f.get("user_stories", [])) for f in features),
            "total_criteria": sum(len(f.get("acceptance_criteria", [])) for f in features),
            "total_apis": sum(len(f.get("api_contracts", [])) for f in features),
            "execution_steps": [
                {
                    "step": n.get("node_id"),
                    "feature": n.get("feature_id"),
                    "task_type": n.get("task_type"),
                    "description": n.get("description"),
                }
                for n in nodes
            ],
        },
        "agent_instructions": (
            "This bundle contains everything needed to build the specified features. "
            "Follow the execution_graph for build order. Each feature includes PRD, "
            "user stories, acceptance criteria, and API contracts. Validate against "
            "schemas before implementation."
        ),
    }


def export_agent_tools_json(
    build_spec_bundle: dict[str, Any],
    *,
    output_path: Path | None = None,
) -> list[dict[str, Any]]:
    """Export spec bundle as OpenCode/Codex tool definitions.

    Each feature becomes one agent tool definition.
    Each user story becomes a tool parameter.
    Acceptance criteria become validation rules.
    """
    features = build_spec_bundle.get("features", [])
    tools: list[dict[str, Any]] = []

    for feature in features:
        stories = feature.get("user_stories", [])
        criteria = feature.get("acceptance_criteria", [])
        api_contracts = feature.get("api_contracts", [])

        tool_def = {
            "name": f"build_{_slug(feature.get('feature_name', 'feature'))}",
            "description": f"Build the {feature.get('feature_name', 'feature')} feature",
            "agent_task_id": feature.get("agent_task_id", ""),
            "input_schema": {
                "type": "object",
                "properties": {
                    "feature_id": {
                        "type": "string",
                        "description": "Unique feature identifier",
                    },
                    "stories": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "story_id": {"type": "string"},
                                "title": {"type": "string"},
                                "as_a": {"type": "string"},
                                "i_want": {"type": "string"},
                                "so_that": {"type": "string"},
                                "priority": {
                                    "type": "string",
                                    "enum": ["P0", "P1", "P2", "P3"],
                                },
                            },
                        },
                        "description": "User stories for this feature",
                    },
                },
                "required": ["feature_id"],
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["completed", "in_progress", "failed"],
                    },
                    "validation_results": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "criterion_id": {"type": "string"},
                                "passed": {"type": "boolean"},
                            },
                        },
                    },
                    "api_endpoints_created": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
            },
            "validation_rules": [
                {
                    "rule_id": c.get("ac_id"),
                    "story_id": c.get("story_id"),
                    "given": c.get("given"),
                    "when": c.get("when"),
                    "then": c.get("then"),
                }
                for c in criteria
            ],
            "api_contracts": [
                {
                    "endpoint": c.get("endpoint"),
                    "method": c.get("method"),
                    "auth_required": c.get("auth_required", False),
                }
                for c in api_contracts
            ],
        }

        tools.append(tool_def)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(tools, indent=2) + "\n",
            encoding="utf-8",
        )

    return tools


def export_github_issues(
    build_spec_bundle: dict[str, Any],
    *,
    dry_run: bool = True,
    repo: str | None = None,
    output_path: Path | None = None,
) -> dict[str, Any]:
    """Export spec bundle as GitHub issues.

    In dry-run mode, previews issues without creating them.
    Epics -> Features, Issues -> User Stories, Tasks -> Acceptance Criteria.
    """
    features = build_spec_bundle.get("features", [])
    generated_at = _now_iso()

    issues: dict[str, Any] = {
        "schema_version": "1.0.0",
        "dry_run": dry_run,
        "repo": repo,
        "generated_at": generated_at,
        "epics": [],
    }

    for i, feature in enumerate(features):
        feature_name = feature.get("feature_name", f"Feature {i+1}")
        epic_number = i + 1

        epic = {
            "title": f"[Epic] {feature_name}",
            "body": _format_epic_body(feature),
            "labels": ["epic", f"feature-{_slug(feature_name[:15])}", "v13"],
            "issues": [],
        }

        stories = feature.get("user_stories", [])
        criteria = feature.get("acceptance_criteria", [])

        for j, story in enumerate(stories):
            story_criteria = [c for c in criteria if c.get("story_id") == story.get("story_id")]
            issue = {
                "title": story.get("title", f"Story {j+1}"),
                "body": _format_issue_body(story, story_criteria),
                "labels": [
                    "user-story",
                    story.get("priority", "P2"),
                    f"feature-{_slug(feature_name[:15])}",
                ],
                "epic": f"Epic {epic_number}: {feature_name}",
            }
            epic["issues"].append(issue)

        issues["epics"].append(epic)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(issues, indent=2) + "\n",
            encoding="utf-8",
        )

    return issues


def _format_epic_body(feature: dict[str, Any]) -> str:
    prd = feature.get("prd", {})
    lines = [
        f"## {feature.get('feature_name', 'Feature')}",
        "",
        "### Problem Summary",
        prd.get("problem_summary", "TBD"),
        "",
        "### Outcome Summary",
        prd.get("outcome_summary", "TBD"),
        "",
        "### Success Metrics",
    ]
    for metric in prd.get("success_metrics", []):
        lines.append(f"- **{metric.get('metric_name', '')}**: {metric.get('target_value', '')}")
    lines.append("")
    lines.append("### Scope")
    for s in prd.get("scope_boundaries", []):
        lines.append(f"- {s}")
    lines.append("")
    lines.append("### Out of Scope")
    for s in prd.get("out_of_scope", []):
        lines.append(f"- {s}")
    return "\n".join(lines)


def _format_issue_body(story: dict[str, Any], criteria: list[dict[str, Any]]) -> str:
    lines = [
        f"### {story.get('title', 'User Story')}",
        "",
        f"**As a** {story.get('as_a', 'user')}",
        "",
        f"**I want** {story.get('i_want', 'to perform an action')}",
        "",
        f"**So that** {story.get('so_that', 'I can accomplish my goal')}",
        "",
        f"**Priority**: {story.get('priority', 'P2')}",
        "",
        f"**Story Points**: {story.get('estimated_story_points', 3)}",
        "",
        "### Acceptance Criteria",
    ]
    for c in criteria:
        lines.extend([
            "",
            f"#### {c.get('ac_id', 'AC')}",
            f"- [ ] **Given** {c.get('given', '')}",
            f"- [ ] **When** {c.get('when', '')}",
            f"- [ ] **Then** {c.get('then', '')}",
        ])
        edge_cases = c.get("edge_cases", [])
        if edge_cases:
            lines.append("  - Edge cases:")
            for ec in edge_cases:
                lines.append(f"    - [ ] {ec}")
    return "\n".join(lines)


def export_spec_bundle(
    build_spec_bundle: dict[str, Any],
    output_format: str,
    *,
    output_path: Path | None = None,
    dry_run: bool = True,
    repo: str | None = None,
) -> Any:
    """Export a spec bundle to any supported format.

    Formats: json (agent_native), agent_tools, github
    """
    format_map = {
        "json": export_agent_native_json,
        "agent_native": export_agent_native_json,
        "agent_tools": export_agent_tools_json,
        "github": export_github_issues,
    }

    exporter = format_map.get(output_format)
    if not exporter:
        valid = list(format_map.keys())
        raise ValueError(f"Unknown format: {output_format}. Valid: {valid}")

    kwargs: dict[str, Any] = {"build_spec_bundle": build_spec_bundle, "output_path": output_path}
    if output_format == "github":
        kwargs["dry_run"] = dry_run
        kwargs["repo"] = repo

    return exporter(**kwargs)
