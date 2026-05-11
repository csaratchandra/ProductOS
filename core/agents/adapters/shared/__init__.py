from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_shared_agent_context(
    workspace_dir: Path,
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    generated_at = generated_at or _now_iso()
    mission = _load_json_if_exists(workspace_dir / "artifacts" / "mission_brief.json") or {}
    prd = _load_json_if_exists(workspace_dir / "artifacts" / "prd.json") or {}
    cockpit = _load_json_if_exists(workspace_dir / "outputs" / "cockpit" / "cockpit_bundle.json") or {}
    cockpit_state = cockpit.get("cockpit_state", {})

    return {
        "workspace_dir": str(workspace_dir),
        "workspace_id": mission.get("workspace_id", workspace_dir.name),
        "mission_title": mission.get("title", workspace_dir.name),
        "problem_statement": prd.get("problem_statement", ""),
        "current_focus": cockpit_state.get("current_focus", "Work from the current mission and validate changes through repo-backed artifacts."),
        "recommended_next_step": cockpit_state.get("recommended_next_step", ""),
        "cli_commands": [
            "./productos status",
            "./productos run discover",
            "./productos queue build --source-artifact artifacts/prd.json --change-summary \"Scope updated\"",
            "./productos render doc --doc-key prd",
            "./productos export artifact --artifact artifacts/prd.json --format agent_brief",
        ],
        "generated_at": generated_at,
    }
