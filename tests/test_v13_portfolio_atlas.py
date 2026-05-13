"""Tests for V13 portfolio atlas and gap analysis."""

import json
from pathlib import Path

import pytest

from core.python.productos_runtime.portfolio_atlas import (
    build_portfolio_atlas,
    build_portfolio_gap_analysis,
    _detect_shared_personas,
    _detect_feature_overlaps,
)
from core.python.productos_runtime.ecosystem_map import (
    build_ecosystem_map,
    render_ecosystem_html,
    render_portfolio_atlas_html,
)


@pytest.fixture
def persona_pack():
    return {
        "personas": [
            {"persona_id": "p_admin", "name": "Admin User"},
            {"persona_id": "p_end_user", "name": "End User"},
        ]
    }


class TestPortfolioAtlas:
    def test_build_portfolio_atlas_with_single_workspace(self, tmp_path):
        ws = tmp_path / "product_a"
        ws.mkdir(parents=True)
        (ws / "artifacts").mkdir()

        atlas = build_portfolio_atlas("suite_1", [ws])
        assert atlas["schema_version"] == "1.0.0"
        assert len(atlas["workspace_summaries"]) == 1
        assert "aggregate_metrics" in atlas

    def test_cross_product_persona_detection(self, tmp_path):
        ws1 = tmp_path / "product_a"
        ws2 = tmp_path / "product_b"
        for ws in [ws1, ws2]:
            ws.mkdir(parents=True)
            arts = ws / "artifacts"
            arts.mkdir()
            (arts / "persona_pack.json").write_text(
                json.dumps({"personas": [{"persona_id": "p_admin", "name": "Admin User"}]}), encoding="utf-8"
            )

        personas = _detect_shared_personas([ws1, ws2])
        assert len(personas) >= 1

    def test_feature_overlap_detection(self, tmp_path):
        ws1 = tmp_path / "product_a"
        ws2 = tmp_path / "product_b"
        for ws in [ws1, ws2]:
            ws.mkdir(parents=True)
            arts = ws / "artifacts"
            arts.mkdir()
            (arts / "feature_scorecard.json").write_text(
                json.dumps({"features": [{"feature_name": "Onboarding Wizard"}]}), encoding="utf-8"
            )

        overlaps = _detect_feature_overlaps([ws1, ws2])
        assert len(overlaps) >= 1


class TestPortfolioGapAnalysis:
    def test_gap_analysis_basic(self, tmp_path):
        ws = tmp_path / "product_a"
        ws.mkdir(parents=True)
        atlas = build_portfolio_atlas("suite_1", [ws])
        gaps = build_portfolio_gap_analysis(atlas, [ws])
        assert gaps["schema_version"] == "1.0.0"
        assert len(gaps["gaps"]) >= 0
        assert "heat_map" in gaps
        assert "portfolio_update" in gaps

    def test_heat_map_structure(self, tmp_path):
        ws = tmp_path / "product_a"
        ws.mkdir(parents=True)
        atlas = build_portfolio_atlas("suite_1", [ws])
        gaps = build_portfolio_gap_analysis(atlas, [ws])
        hm = gaps["heat_map"]
        assert "personas" in hm
        assert "journey_stages" in hm
        assert "cells" in hm
        assert len(hm["cells"]) > 0


class TestEcosystemMap:
    def test_build_ecosystem_map(self):
        eco = build_ecosystem_map(
            ["suite_a", "suite_b"],
            {"suite_a": {}, "suite_b": {}},
        )
        assert eco["schema_version"] == "1.0.0"
        assert len(eco["entities"]) >= 2
        assert "relationships" in eco

    def test_ecosystem_html_rendering(self, tmp_path):
        eco = build_ecosystem_map(
            ["suite_a", "suite_b"],
            {"suite_a": {}, "suite_b": {}},
        )
        html = render_ecosystem_html(eco)
        assert html.startswith("<!DOCTYPE html>")
        assert "Ecosystem Map" in html
        assert "<canvas" in html

    def test_portfolio_atlas_html_rendering(self, tmp_path):
        ws = tmp_path / "product_a"
        ws.mkdir(parents=True)
        atlas = build_portfolio_atlas("suite_1", [ws])
        html = render_portfolio_atlas_html(atlas)
        assert html.startswith("<!DOCTYPE html>")
        assert "Portfolio Atlas" in html
