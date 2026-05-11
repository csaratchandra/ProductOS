from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_codex_adapter_definition(
    workspace_dir: Path,
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    generated_at = generated_at or _now_iso()
    return {
        "adapter_id": "codex",
        "name": "Codex",
        "system_prompt": "Use ProductOS as the repo-native source of truth, keep PM approval explicit at release boundaries, and return machine-readable output when asked.",
        "tools": [
            {"name": "productos_status", "command": "./productos --workspace-dir {workspace_dir} --format json status"},
            {"name": "productos_render_prd", "command": "./productos --workspace-dir {workspace_dir} render doc --doc-key prd"},
            {"name": "productos_export_agent_brief", "command": "./productos --workspace-dir {workspace_dir} export artifact --artifact artifacts/prd.json --format agent_brief"},
        ],
        "generated_at": generated_at,
        "workspace_dir": str(workspace_dir),
    }
