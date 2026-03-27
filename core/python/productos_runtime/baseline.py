from __future__ import annotations

from pathlib import Path
from typing import Any

from .v4 import (
    build_v4_foundation_bundle_from_workspace,
    build_v4_market_intelligence_bundle_from_workspace,
)


def build_foundation_bundle_from_workspace(
    workspace_dir: Path | str,
    *,
    generated_at: str,
) -> dict[str, dict[str, Any]]:
    """Active bounded-baseline wrapper over the historical V4 foundation builder."""
    return build_v4_foundation_bundle_from_workspace(
        workspace_dir,
        generated_at=generated_at,
    )


def build_market_intelligence_bundle_from_workspace(
    workspace_dir: Path | str,
    *,
    generated_at: str,
) -> dict[str, Any]:
    """Active bounded-baseline wrapper over the historical market-intelligence builder."""
    return build_v4_market_intelligence_bundle_from_workspace(
        workspace_dir,
        generated_at=generated_at,
    )
