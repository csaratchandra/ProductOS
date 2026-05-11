"""Tests for ProductOS V11 Export Pipeline."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.python.productos_runtime.export_pipeline import export_artifact


class TestExportPipeline:
    """Test the export pipeline comprehensively."""

    def test_export_markdown(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        artifacts_dir = workspace_dir / "artifacts"
        artifacts_dir.mkdir(parents=True)

        artifact = {
            "schema_version": "1.0.0",
            "title": "Test Artifact",
            "description": "A test artifact for export.",
            "artifact_id": "art_001",
        }
        with (artifacts_dir / "test.json").open("w") as f:
            json.dump(artifact, f)

        result = export_artifact("artifacts/test.json", "markdown", workspace_dir, generated_at="2026-05-06T12:00:00Z")

        assert result["format"] == "markdown"
        assert "Test Artifact" in result["content"]
        assert "A test artifact for export." in result["content"]
        assert result["source_artifact"] == "art_001"

    def test_export_deck(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        artifacts_dir = workspace_dir / "artifacts"
        artifacts_dir.mkdir(parents=True)

        artifact = {
            "schema_version": "1.0.0",
            "title": "Strategy Brief",
            "description": "Our market strategy.",
            "key_points": ["Point A", "Point B"],
            "audience": ["leadership", "PM"],
            "artifact_id": "art_002",
        }
        with (artifacts_dir / "strategy.json").open("w") as f:
            json.dump(artifact, f)

        result = export_artifact("artifacts/strategy.json", "deck", workspace_dir, generated_at="2026-05-06T12:00:00Z")

        assert result["format"] == "deck"
        assert result["presentation_brief"]["title"] == "Strategy Brief"
        assert result["presentation_brief"]["key_points"] == ["Point A", "Point B"]
        assert result["source_artifact"] == "art_002"

    def test_export_battle_card(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        artifacts_dir = workspace_dir / "artifacts"
        artifacts_dir.mkdir(parents=True)

        artifact = {
            "schema_version": "1.0.0",
            "title": "CompetitorAlpha",
            "competitor_name": "CompetitorAlpha",
            "strengths": ["Fast", "Cheap"],
            "weaknesses": ["Buggy", "No support"],
            "positioning": "Budget option",
            "counter_messaging": ["We have better support"],
            "artifact_id": "art_003",
        }
        with (artifacts_dir / "competitor.json").open("w") as f:
            json.dump(artifact, f)

        result = export_artifact("artifacts/competitor.json", "battle_card", workspace_dir, generated_at="2026-05-06T12:00:00Z")

        assert result["format"] == "battle_card"
        assert result["competitor"] == "CompetitorAlpha"
        assert result["strengths"] == ["Fast", "Cheap"]
        assert result["weaknesses"] == ["Buggy", "No support"]

    def test_export_one_pager(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        artifacts_dir = workspace_dir / "artifacts"
        artifacts_dir.mkdir(parents=True)

        artifact = {
            "schema_version": "1.0.0",
            "title": "Product One-Pager",
            "problem_statement": "Users need X",
            "solution_approach": "We provide Y",
            "value_proposition": "Best Y ever",
            "target_market": "SMBs",
            "artifact_id": "art_004",
        }
        with (artifacts_dir / "product.json").open("w") as f:
            json.dump(artifact, f)

        result = export_artifact("artifacts/product.json", "one_pager", workspace_dir, generated_at="2026-05-06T12:00:00Z")

        assert result["format"] == "one_pager"
        assert result["title"] == "Product One-Pager"
        assert result["problem"] == "Users need X"
        assert result["solution"] == "We provide Y"
        assert result["value_proposition"] == "Best Y ever"
        assert result["target_market"] == "SMBs"

    def test_export_agent_brief_weak_boundaries(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        artifacts_dir = workspace_dir / "artifacts"
        artifacts_dir.mkdir(parents=True)

        artifact = {
            "schema_version": "1.0.0",
            "title": "Weak PRD",
            "problem_statement": "Users need something",
            "out_of_scope": [],
            "acceptance_criteria": [],
            "artifact_id": "art_005",
        }
        with (artifacts_dir / "weak_prd.json").open("w") as f:
            json.dump(artifact, f)

        result = export_artifact("artifacts/weak_prd.json", "agent_brief", workspace_dir, generated_at="2026-05-06T12:00:00Z")

        assert result["format"] == "agent_brief"
        assert result["boundaries_strong"] is False
        assert "None specified" in result["content"] or "EXPLICIT OUT_OF_SCOPE" in result["content"]

    def test_export_artifact_not_found(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        with pytest.raises(FileNotFoundError):
            export_artifact("artifacts/missing.json", "markdown", workspace_dir)

    def test_export_unsupported_format(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        artifacts_dir = workspace_dir / "artifacts"
        artifacts_dir.mkdir(parents=True)

        artifact = {"schema_version": "1.0.0", "title": "Test"}
        with (artifacts_dir / "test.json").open("w") as f:
            json.dump(artifact, f)

        with pytest.raises(ValueError) as exc_info:
            export_artifact("artifacts/test.json", "pdf", workspace_dir)

        assert "Unsupported export format" in str(exc_info.value)
        assert "markdown" in str(exc_info.value)
