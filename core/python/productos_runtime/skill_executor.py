from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .pm_note_ingestion import ingest_pm_note
from .prd_scope_boundary import build_prd_boundary_report


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_skill_contract(skill_path: Path) -> dict[str, str]:
    content = skill_path.read_text(encoding="utf-8")
    sections: dict[str, str] = {}
    current: str | None = None
    lines: list[str] = []
    for raw_line in content.splitlines():
        header = re.match(r"^##\s+\d+\.\s+(.*)$", raw_line)
        if header:
            if current is not None:
                sections[current] = "\n".join(lines).strip()
            current = header.group(1).strip()
            lines = []
            continue
        if current is not None:
            lines.append(raw_line)
    if current is not None:
        sections[current] = "\n".join(lines).strip()
    return sections


def execute_skill(
    skill_path: Path,
    workspace_dir: Path,
    *,
    generated_at: str | None = None,
    extra_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    generated_at = generated_at or _now_iso()
    skill_name = skill_path.parent.name
    contract = parse_skill_contract(skill_path)

    if skill_name == "prd_scope_boundary_check":
        artifact = build_prd_boundary_report(workspace_dir, generated_at=generated_at)
        return _execution_result(skill_name, contract, artifact, generated_at)

    if skill_name == "pm_note_ingestion":
        note_path = _latest_note_path(workspace_dir)
        artifact = ingest_pm_note(workspace_dir, note_path, generated_at=generated_at) if note_path else {
            "schema_version": "1.0.0",
            "pm_note_delta_proposal_id": f"pndp_{workspace_dir.name}_empty",
            "workspace_id": workspace_dir.name,
            "source_note": {
                "note_path": "",
                "note_type": "meeting_notes",
                "summary": "No note available.",
            },
            "proposed_deltas": [],
            "generated_at": generated_at,
        }
        return _execution_result(skill_name, contract, artifact, generated_at)

    artifact = {
        "skill_name": skill_name,
        "workspace_id": workspace_dir.name,
        "purpose": contract.get("Purpose", ""),
        "status": "planned",
        "generated_at": generated_at,
        "extra_context": extra_context or {},
    }
    return _execution_result(skill_name, contract, artifact, generated_at)


def _execution_result(
    skill_name: str,
    contract: dict[str, str],
    artifact: dict[str, Any],
    generated_at: str,
) -> dict[str, Any]:
    return {
        "status": "ok",
        "skill_name": skill_name,
        "generated_at": generated_at,
        "contract_sections": sorted(contract.keys()),
        "artifact": artifact,
    }


def _latest_note_path(workspace_dir: Path) -> Path | None:
    candidates = sorted((workspace_dir / "inbox").glob("**/*.*"))
    return candidates[-1] if candidates else None
