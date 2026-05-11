"""Tests for ProductOS V12 --format json CLI support."""

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


class TestFormatJson:
    """Test --format json produces valid machine-readable output."""

    def test_status_json_schema(self, root_dir: Path, bundled_workspace_dir: Path):
        result = _run_cli(
            root_dir,
            "--workspace-dir", str(bundled_workspace_dir),
            "--format", "json",
            "status",
        )

        assert result.returncode == 0, result.stderr
        payload = json.loads(result.stdout)
        assert payload["status"] == "ok"
        assert payload["returncode"] == 0
        assert "stdout" in payload
        assert "Mode:" in payload["stdout"]

    def test_json_error_on_missing_workspace(self, root_dir: Path):
        result = _run_cli(root_dir, "--format", "json", "status")

        assert result.returncode != 0
        payload = json.loads(result.stdout)
        assert payload["status"] == "error"
        assert payload["returncode"] != 0

    def test_help_includes_format_flag(self, root_dir: Path):
        result = _run_cli(root_dir, "--help")

        assert result.returncode == 0
        assert "--format" in result.stdout
        assert "json" in result.stdout
        assert "text" in result.stdout

    def test_queue_build_json_output(self, root_dir: Path, bundled_workspace_dir: Path):
        result = _run_cli(
            root_dir,
            "--workspace-dir", str(bundled_workspace_dir),
            "--format", "json",
            "queue", "build",
            "--source-artifact", "artifacts/prd.json",
            "--change-summary", "test change",
        )

        assert result.returncode == 0, result.stderr or result.stdout
        payload = json.loads(result.stdout)
        assert payload["status"] == "ok"
        assert payload["returncode"] == 0

    def test_review_delta_json_output(self, root_dir: Path, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        cockpit_dir = workspace_dir / "outputs" / "cockpit"
        cockpit_dir.mkdir(parents=True)

        cockpit = {
            "cockpit_state": {
                "living_updates_queue": [
                    {
                        "update_id": "lu_test_json",
                        "regeneration_queue_item_ref": "rq_item_001",
                        "source_change": "Test",
                        "target_artifact": "artifacts/test.json",
                        "delta_summary": "Test delta",
                        "impact_classification": "mechanical",
                        "pm_action": "pending",
                        "pm_note": "",
                    }
                ]
            }
        }
        with (cockpit_dir / "cockpit_bundle.json").open("w") as f:
            json.dump(cockpit, f)

        result = _run_cli(
            root_dir,
            "--workspace-dir", str(workspace_dir),
            "--format", "json",
            "review-delta",
            "--update-id", "lu_test_json",
            "--action", "approve",
        )

        assert result.returncode == 0, result.stderr or result.stdout
        payload = json.loads(result.stdout)
        assert payload["status"] == "ok"
        assert "Approved" in payload["stdout"]

    def test_doctor_json_output(self, root_dir: Path, bundled_workspace_dir: Path):
        result = _run_cli(
            root_dir,
            "--workspace-dir", str(bundled_workspace_dir),
            "--format", "json",
            "doctor",
        )

        assert result.returncode == 0, result.stderr or result.stdout
        payload = json.loads(result.stdout)
        assert payload["status"] == "ok"
        assert payload["returncode"] == 0
        assert "Bundle Status" in payload["stdout"]
