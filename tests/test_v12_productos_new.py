"""Tests for ProductOS V12 productos new command."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


def _run_cli(root_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/productos.py", *args],
        cwd=root_dir,
        capture_output=True,
        text=True,
        check=False,
    )


class TestProductosNew:
    """Test the V12 productos new command."""

    def test_new_creates_workspace_with_artifacts(self, root_dir: Path, tmp_path: Path):
        dest = tmp_path / "new-workspace"
        result = _run_cli(
            root_dir,
            "new",
            "AI-powered inventory forecasting for SMB retailers",
            "--dest", str(dest),
        )

        assert result.returncode == 0, result.stderr
        assert dest.exists()
        assert (dest / "artifacts" / "problem_brief.json").exists()
        assert (dest / "artifacts" / "concept_brief.json").exists()
        assert (dest / "artifacts" / "prd.json").exists()
        assert (dest / "artifacts" / "competitor_dossier.json").exists()
        assert (dest / "artifacts" / "persona_pack.json").exists()
        assert (dest / "artifacts" / "market_analysis_brief.json").exists()
        assert (dest / "outputs" / "cockpit" / "cockpit_bundle.json").exists()
        assert (dest / "outputs" / "cockpit" / "cockpit.html").exists()
        assert (dest / "outputs" / "cockpit" / "quality_snapshot.json").exists()
        assert (dest / "workspace_manifest.yaml").exists()

    def test_new_seeds_problem_statement(self, root_dir: Path, tmp_path: Path):
        dest = tmp_path / "new-workspace"
        result = _run_cli(
            root_dir,
            "new",
            "Remote team async standups need better tooling",
            "--dest", str(dest),
        )

        assert result.returncode == 0, result.stderr

        prd_path = dest / "artifacts" / "prd.json"
        with prd_path.open() as f:
            prd = json.load(f)

        assert "Remote team async standups need better tooling" in prd["problem_summary"]
        assert prd["schema_version"] == "1.1.0"
        assert len(prd["out_of_scope"]) >= 1

    def test_new_outputs_json_when_format_json(self, root_dir: Path, tmp_path: Path):
        dest = tmp_path / "new-workspace-json"
        result = _run_cli(
            root_dir,
            "--format", "json",
            "new",
            "Fast checkout for mobile shoppers",
            "--dest", str(dest),
        )

        assert result.returncode == 0, result.stderr
        payload = json.loads(result.stdout)
        assert payload["status"] == "ok"
        assert payload["returncode"] == 0
        assert "Created workspace" in payload["stdout"]

    def test_new_rejects_existing_directory(self, root_dir: Path, tmp_path: Path):
        dest = tmp_path / "existing"
        dest.mkdir()
        result = _run_cli(
            root_dir,
            "new",
            "Something new",
            "--dest", str(dest),
        )

        assert result.returncode != 0

    def test_new_creates_mission_brief(self, root_dir: Path, tmp_path: Path):
        dest = tmp_path / "new-workspace"
        result = _run_cli(
            root_dir,
            "new",
            "Decentralized identity for healthcare records",
            "--dest", str(dest),
        )

        assert result.returncode == 0, result.stderr

        mission_path = dest / "artifacts" / "mission_brief.json"
        assert mission_path.exists()
        with mission_path.open() as f:
            mission = json.load(f)

        assert mission["schema_version"] == "1.0.0"
        assert "healthcare records" in mission["customer_problem"]
        assert mission["operating_mode"] == "discover_to_align"

    def test_new_creates_cockpit_state(self, root_dir: Path, tmp_path: Path):
        dest = tmp_path / "new-workspace"
        result = _run_cli(
            root_dir,
            "new",
            "Carbon tracking for logistics fleets",
            "--dest", str(dest),
        )

        assert result.returncode == 0, result.stderr

        cockpit_path = dest / "outputs" / "cockpit" / "cockpit_bundle.json"
        with cockpit_path.open() as f:
            bundle = json.load(f)

        cockpit = bundle["cockpit_state"]
        assert cockpit["mode"] == "plan"
        assert cockpit["status"] == "active"
        assert len(cockpit["living_updates_queue"]) == 0
        assert cockpit["mission_control"]["active_stage"] == "discover"
