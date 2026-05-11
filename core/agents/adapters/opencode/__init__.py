from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_opencode_adapter_definition(
    workspace_dir: Path,
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    generated_at = generated_at or _now_iso()
    return {
        "adapter_id": "opencode",
        "name": "OpenCode",
        "system_prompt": "Operate within the repo, keep claims bounded to repo proof, and prefer ProductOS CLI surfaces over ad hoc mutations.",
        "tools": [
            {"name": "productos_status", "command": "./productos --workspace-dir {workspace_dir} status"},
            {"name": "productos_run_discover", "command": "./productos --workspace-dir {workspace_dir} run discover"},
            {"name": "productos_queue_build", "command": "./productos --workspace-dir {workspace_dir} queue build --source-artifact {source_artifact} --change-summary {change_summary}"},
        ],
        "generated_at": generated_at,
        "workspace_dir": str(workspace_dir),
    }
