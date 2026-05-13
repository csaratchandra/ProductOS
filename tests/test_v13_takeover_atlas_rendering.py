"""Tests for V13 takeover atlas HTML rendering."""

from pathlib import Path

import pytest

from core.python.productos_runtime.takeover import build_takeover_brief
from components.atlas.python.productos_atlas import (
    render_takeover_atlas_html,
    render_atlas_markdown,
    render_problem_space_markdown,
    _build_template_context,
)


@pytest.fixture
def sample_brief():
    return {
        "takeover_brief_id": "tb_test",
        "workspace_id": "test_ws",
        "title": "Test Atlas",
        "product_summary": "A test product",
        "old_problem_framing": "Test problem",
        "target_segment_summary": "SMB segment",
        "target_persona_summary": "Power users",
        "competitor_summary": "Competitor X",
        "customer_journey_summary": "5 stages",
        "roadmap_summary": "Q1 roadmap",
        "evidence_gaps": [
            {"gap_id": "eg_001", "description": "Missing competitive data", "severity": "high", "related_artifact_refs": []}
        ],
        "first_pm_actions": {
            "first_30_days": ["Review artifacts"],
            "first_60_days": ["Validate gaps"],
            "first_90_days": ["Drive roadmap"],
        },
        "source_workspace_ref": "test_ws",
        "generated_at": "2026-03-22T08:00:00Z",
    }


class TestHTMLRendering:
    def test_render_contains_title(self, sample_brief):
        html = render_takeover_atlas_html(sample_brief)
        assert "Test Atlas" in html

    def test_render_contains_gaps(self, sample_brief):
        html = render_takeover_atlas_html(sample_brief)
        assert "Evidence Gaps" in html

    def test_render_contains_actions(self, sample_brief):
        html = render_takeover_atlas_html(sample_brief)
        assert "PM Actions" in html or "First 30 Days" in html

    def test_render_is_standalone_html(self, sample_brief):
        html = render_takeover_atlas_html(sample_brief)
        assert html.startswith("<!DOCTYPE html>")
        assert "</html>" in html
        assert "<style>" in html

    def test_render_with_problem_space(self, sample_brief):
        psm = {"problems": [{"problem_id": "p1", "title": "Test Problem", "summary": "A test", "severity": "high", "source_artifact_ids": []}]}
        html = render_takeover_atlas_html(sample_brief, problem_space_map=psm)
        assert "Test Problem" in html

    def test_render_empty_gaps(self):
        brief = {
            "takeover_brief_id": "tb_empty",
            "workspace_id": "test",
            "title": "Empty Atlas",
            "product_summary": "test",
            "old_problem_framing": "test",
            "target_segment_summary": "test",
            "target_persona_summary": "test",
            "competitor_summary": "test",
            "customer_journey_summary": "test",
            "roadmap_summary": "test",
            "evidence_gaps": [],
            "first_pm_actions": {"first_30_days": [], "first_60_days": [], "first_90_days": []},
            "source_workspace_ref": "test",
            "generated_at": "2026-03-22T08:00:00Z",
        }
        html = render_takeover_atlas_html(brief)
        assert "Empty Atlas" in html

    def test_interactive_filters_present(self, sample_brief):
        html = render_takeover_atlas_html(sample_brief)
        assert "filterBar" in html or "filter-bar" in html

    def test_evidence_footnotes(self, sample_brief):
        html = render_takeover_atlas_html(sample_brief)
        assert "gap_id" in html or "eg_001" in html


class TestMarkdownRendering:
    def test_render_atlas_markdown(self, sample_brief):
        md = render_atlas_markdown(sample_brief)
        assert md.startswith("#")
        assert "Product Summary" in md

    def test_render_problem_space_markdown(self):
        psm = {"title": "Problem Space", "problems": [{"problem_id": "p1", "title": "P1", "summary": "desc", "severity": "high", "source_artifact_ids": []}]}
        md = render_problem_space_markdown(psm)
        assert "# Problem Space" in md
        assert "P1" in md


class TestTemplateContext:
    def test_build_context(self, sample_brief):
        ctx = _build_template_context(sample_brief, None, None, None, None)
        assert ctx["title"] == "Test Atlas"
        assert len(ctx["evidence_gaps"]) == 1
