from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.agents.adapters.codex import build_codex_adapter_definition
from core.agents.adapters.opencode import build_opencode_adapter_definition
from core.agents.adapters.shared import build_shared_agent_context


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_runtime_adapter_registry(
    workspace_dir: Path,
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    generated_at = generated_at or _now_iso()
    return {
        "schema_version": "1.0.0",
        "runtime_adapter_registry_id": f"runtime_adapter_registry_{workspace_dir.name}",
        "workspace_id": workspace_dir.name,
        "status": "healthy",
        "default_adapter_id": "codex",
        "adapters": [
            _registry_adapter("codex", "Codex", used_by_default=True),
            _registry_adapter("opencode", "OpenCode"),
        ],
        "evaluated_at": generated_at,
    }


def build_agent_context(
    workspace_dir: Path,
    *,
    target: str,
    generated_at: str | None = None,
) -> dict[str, Any]:
    generated_at = generated_at or _now_iso()
    shared = build_shared_agent_context(workspace_dir, generated_at=generated_at)
    adapter = {
        "codex": build_codex_adapter_definition,
        "opencode": build_opencode_adapter_definition,
    }[target](workspace_dir, generated_at=generated_at)
    return {
        "status": "ok",
        "target": target,
        "generated_at": generated_at,
        "shared_context": shared,
        "adapter": adapter,
        "runtime_adapter_registry": build_runtime_adapter_registry(workspace_dir, generated_at=generated_at),
    }


def _registry_adapter(adapter_id: str, name: str, *, used_by_default: bool = False) -> dict[str, Any]:
    return {
        "adapter_id": adapter_id,
        "name": name,
        "capability_type": "worker_session",
        "availability_status": "available",
        "supported_actions": [
            "status",
            "run_discover",
            "queue_build",
            "review_delta",
            "export_artifacts",
        ],
        "requires_host_support": True,
        "verification_status": "verified",
        "supported_mission_stages": ["discover", "align", "operate", "improve"],
        "prompt_pattern_capabilities": {
            "mission_routing": "repo_managed",
            "task_boundary_visibility": "repo_managed",
            "research_freshness": "limited",
            "validation_enforcement": "repo_managed",
            "delegation_support": "native",
            "approval_gating": "repo_managed",
            "memory_steering": "limited",
            "artifact_export": "repo_managed",
        },
        "used_by_default": used_by_default,
        "host_constraints": [
            "Relies on repo-local CLI and workspace state.",
            "Broad internet or GUI actions remain host-policy constrained.",
        ],
        "notes": f"{name} context pack generated from ProductOS workspace state.",
    }
