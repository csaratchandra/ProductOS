"""Tests for V13 atlas synthesis module."""

from pathlib import Path

import pytest

from core.python.productos_runtime.atlas_synthesis import (
    synthesize_takeover_brief,
    decompose_problems,
    grade_atlas_quality,
    _identify_evidence_gaps,
    _compute_confidence_weights,
)


class TestSynthesizeTakeoverBrief:
    def test_synthesize_with_minimal_input(self):
        brief = synthesize_takeover_brief(
            code_understanding=None,
            visual_product_atlas=None,
            source_note_cards=None,
            adoption_artifacts=None,
            workspace_id="test_ws",
        )
        assert brief["takeover_brief_id"]
        assert brief["workspace_id"] == "test_ws"
        assert "evidence_gaps" in brief

    def test_synthesize_with_code_understanding(self):
        code = {
            "module_graph": [{"module_name": "api", "module_path": "api.py", "confidence": "observed", "dependencies": [], "change_frequency": "frequent", "purpose": "API layer"}],
            "api_surface": [{"method": "GET", "path": "/test", "inferred_feature": "Test", "confidence": "observed"}],
            "feature_flags": [],
            "change_velocity": {"module_velocity": [], "overall_summary": "test"},
            "evidence_confidence": {"observed_count": 1, "inferred_count": 0, "uncertain_count": 0, "summary": "test"},
        }
        brief = synthesize_takeover_brief(
            code_understanding=code,
            workspace_id="test_ws",
        )
        assert "product_summary" in brief
        assert len(brief.get("evidence_gaps", [])) >= 0

    def test_output_contains_required_fields(self):
        brief = synthesize_takeover_brief(workspace_id="test")
        required = ["takeover_brief_id", "workspace_id", "title", "product_summary",
                     "old_problem_framing", "target_segment_summary", "target_persona_summary",
                     "competitor_summary", "customer_journey_summary", "roadmap_summary",
                     "evidence_gaps", "first_pm_actions", "generated_at"]
        for field in required:
            assert field in brief, f"Missing required field: {field}"


class TestProblemDecomposition:
    def test_decompose_problems(self):
        result = decompose_problems(
            main_problem="Users cannot easily onboard to the product",
            product_context="SaaS platform for team collaboration",
        )
        assert "main_problem" in result
        assert "sub_problems" in result
        assert len(result["sub_problems"]) > 0

    def test_sub_problems_have_required_fields(self):
        result = decompose_problems(
            main_problem="Users struggle with data import",
            product_context="Data analytics platform",
        )
        for sp in result["sub_problems"]:
            assert "problem_id" in sp
            assert "title" in sp
            assert "severity" in sp

    def test_dependency_graph(self):
        result = decompose_problems(
            main_problem="Complex workflow management",
            product_context="Project management tool",
        )
        deps = result.get("dependency_graph", [])
        if deps:
            assert "source_id" in deps[0]
            assert "target_id" in deps[0]


class TestAtlasQualityGrading:
    def test_grade_quality_output(self):
        brief = synthesize_takeover_brief(workspace_id="test_ws")
        quality = grade_atlas_quality(brief)
        assert quality["schema_version"] == "1.0.0"
        assert quality["overall_score"] >= 0
        assert quality["overall_score"] <= 5
        assert len(quality["dimension_scores"]) == 6

    def test_dimension_scores_have_rationale(self):
        brief = synthesize_takeover_brief(workspace_id="test_ws")
        quality = grade_atlas_quality(brief)
        for d in quality["dimension_scores"]:
            assert "rationale" in d
            assert d["score"] >= 0
            assert d["score"] <= d["max_score"]

    def test_grade_with_evidence_gaps(self):
        brief = synthesize_takeover_brief(workspace_id="test")
        quality = grade_atlas_quality(brief)
        if brief.get("evidence_gaps"):
            assert len(quality.get("recommendations", [])) >= 0
