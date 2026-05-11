from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from components.prototype.python.prototype_engine import write_prototype_bundle


def _run_cli(root_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/productos.py", *args],
        cwd=root_dir,
        capture_output=True,
        text=True,
        check=False,
    )


def test_write_prototype_bundle_outputs_html_and_quality_report(bundled_workspace_dir: Path, tmp_path: Path):
    workspace_copy = tmp_path / "workspace"
    import shutil
    shutil.copytree(bundled_workspace_dir, workspace_copy)
    bundle_paths = write_prototype_bundle(workspace_copy, generated_at="2026-05-11T00:00:00Z")
    assert bundle_paths["prototype_html"].exists()
    assert bundle_paths["story_map_html"].exists()
    quality = json.loads(bundle_paths["prototype_quality_report"].read_text(encoding="utf-8"))
    assert quality["schema_version"] == "1.0.0"
    assert quality["scores"]["interaction_depth"] >= 7


def test_render_docs_command_renders_available_documents(root_dir: Path, bundled_workspace_dir: Path):
    result = _run_cli(
        root_dir,
        "--workspace-dir", str(bundled_workspace_dir),
        "render", "docs",
    )
    assert result.returncode == 0, result.stderr
    assert "Rendered Documents" in result.stdout


def test_render_prototype_command_outputs_bundle(root_dir: Path, bundled_workspace_dir: Path):
    result = _run_cli(
        root_dir,
        "--workspace-dir", str(bundled_workspace_dir),
        "render", "prototype",
        "--workspace-dir", str(bundled_workspace_dir),
    )
    assert result.returncode == 0, result.stderr
    assert "Prototype HTML" in result.stdout
