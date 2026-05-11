from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from core.python.productos_runtime.decision_runtimes import (
    run_api_contract_generation,
    run_battle_card_generation,
    run_investor_content_generation,
    run_premortem_analysis,
    run_stakeholder_management,
    run_trade_off_analysis,
)
from jsonschema import Draft202012Validator


def _run_cli(root_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/productos.py", *args],
        cwd=root_dir,
        capture_output=True,
        text=True,
        check=False,
    )


def test_agent_context_command_outputs_context(root_dir: Path, bundled_workspace_dir: Path, tmp_path: Path):
    output_path = tmp_path / "agent-context.json"
    result = _run_cli(
        root_dir,
        "--workspace-dir", str(bundled_workspace_dir),
        "agent-context",
        "--target", "codex",
        "--output-path", str(output_path),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["target"] == "codex"
    assert payload["runtime_adapter_registry"]["status"] == "healthy"


def test_export_artifact_command_writes_single_artifact_export(root_dir: Path, bundled_workspace_dir: Path, tmp_path: Path):
    output_path = tmp_path / "agent-brief.json"
    result = _run_cli(
        root_dir,
        "--workspace-dir", str(bundled_workspace_dir),
        "export",
        "artifact",
        "--artifact", "artifacts/prd.json",
        "--format", "agent_brief",
        "--output-path", str(output_path),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["format"] == "agent_brief"


def test_demo_command_copies_workspace(root_dir: Path, tmp_path: Path):
    dest = tmp_path / "demo-workspace"
    result = _run_cli(root_dir, "demo", "--dest", str(dest))
    assert result.returncode == 0, result.stderr
    assert (dest / "workspace_manifest.yaml").exists()
    assert (dest / "outputs" / "cockpit" / "cockpit.html").exists()


def test_packaging_metadata_and_example_workspaces_present(root_dir: Path):
    assert (root_dir / "pyproject.toml").exists()
    workspace_dirs = [path for path in (root_dir / "examples" / "workspaces").iterdir() if path.is_dir()]
    assert len(workspace_dirs) == 10


def test_decision_runtime_smoke_outputs_validate(root_dir: Path, bundled_workspace_dir: Path):
    artifacts = [
        (run_trade_off_analysis(bundled_workspace_dir, generated_at="2026-05-11T00:00:00Z"), "decision_analysis.schema.json"),
        (run_premortem_analysis(bundled_workspace_dir, generated_at="2026-05-11T00:00:00Z"), "decision_premortem.schema.json"),
        (run_battle_card_generation(bundled_workspace_dir, generated_at="2026-05-11T00:00:00Z"), "battle_card.schema.json"),
        (run_investor_content_generation(bundled_workspace_dir, generated_at="2026-05-11T00:00:00Z"), "investor_memo.schema.json"),
        (run_api_contract_generation(bundled_workspace_dir, generated_at="2026-05-11T00:00:00Z"), "api_contract.schema.json"),
        (run_stakeholder_management(bundled_workspace_dir, generated_at="2026-05-11T00:00:00Z"), "stakeholder_map.schema.json"),
    ]
    for artifact, schema_name in artifacts:
        schema = json.loads((root_dir / "core" / "schemas" / "artifacts" / schema_name).read_text(encoding="utf-8"))
        errors = list(Draft202012Validator(schema).iter_errors(artifact))
        assert not errors, f"{schema_name} failed validation: {[error.message for error in errors[:3]]}"
