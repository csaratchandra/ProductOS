from __future__ import annotations

from typing import Any


def _format_version_label(version_number: int) -> str:
    return f"v{version_number}"


def default_modification_log(
    *,
    version_number: int,
    updated_at: str,
    updated_by: str,
    summary: str,
) -> list[dict[str, Any]]:
    return [
        {
            "version_number": version_number,
            "updated_at": updated_at,
            "updated_by": updated_by,
            "summary": summary,
        }
    ]


def render_governed_markdown(
    *,
    title: str,
    body_lines: list[str],
    version_number: int,
    status: str,
    updated_at: str,
    updated_by: str,
    change_summary: str,
    source_artifact_ids: list[str] | None = None,
    modification_log: list[dict[str, Any]] | None = None,
) -> str:
    log_entries = modification_log or default_modification_log(
        version_number=version_number,
        updated_at=updated_at,
        updated_by=updated_by,
        summary=change_summary,
    )
    lines = [
        f"# {title}",
        "",
        f"Version: `{_format_version_label(version_number)}`",
        f"Status: `{status}`",
        f"Updated At: `{updated_at}`",
        f"Updated By: `{updated_by}`",
    ]
    if source_artifact_ids:
        lines.append(
            "Source Artifacts: " + ", ".join(f"`{artifact_id}`" for artifact_id in source_artifact_ids)
        )
    lines.extend(["", "## Modification Log", ""])
    for entry in log_entries:
        lines.append(
            f"- `{_format_version_label(entry['version_number'])}` `{entry['updated_at']}` `{entry['updated_by']}` {entry['summary']}"
        )
    lines.extend(["", *body_lines])
    return "\n".join(lines).rstrip() + "\n"
