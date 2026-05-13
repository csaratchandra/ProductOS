"""Tests for V13 spec chain generation."""

from pathlib import Path

import pytest

from core.python.productos_runtime.spec_pipeline import (
    build_full_spec_chain,
    synthesize_multi_journey,
    _generate_prd,
    _generate_user_stories,
)


class TestMultiJourneySynthesis:
    def test_synthesize_multi_journey_builds_bundle(self, tmp_path):
        problem_space_map = {
            "problems": [
                {"problem_id": "p_onboarding", "title": "Users struggle to onboard"},
                {"problem_id": "p_search", "title": "Users cannot find content"},
            ]
        }

        bundle = synthesize_multi_journey(
            tmp_path,
            problem_space_map,
            generated_at="2026-05-13T08:00:00Z",
        )

        assert bundle["schema_version"] == "1.0.0"
        assert bundle["workspace_id"] == tmp_path.name
        assert len(bundle["target_features"]) == 2
        assert len(bundle["journeys"]) == 2
        assert len(bundle["cross_feature_dependencies"]) == 1
        assert len(bundle["shared_moments_of_truth"]) == 1
        assert bundle["shared_moments_of_truth"][0]["mot_id"] == "mot_shared_2026-05-13"
        for journey in bundle["journeys"]:
            journey_path = tmp_path / journey["customer_journey_map_ref"]
            assert journey_path.exists()

    def test_synthesize_multi_journey_filters_problem_ids(self, tmp_path):
        problem_space_map = {
            "problems": [
                {"problem_id": "p_onboarding", "title": "Users struggle to onboard"},
                {"problem_id": "p_search", "title": "Users cannot find content"},
                {"problem_id": "p_retention", "title": "Users do not return"},
            ]
        }

        bundle = synthesize_multi_journey(
            tmp_path,
            problem_space_map,
            problem_ids=["p_search"],
            generated_at="2026-05-13T08:00:00Z",
        )

        assert bundle["source_problem_ids"] == ["p_search"]
        assert len(bundle["target_features"]) == 1
        assert len(bundle["journeys"]) == 1
        assert bundle["cross_feature_dependencies"] == []
        assert bundle["shared_moments_of_truth"] == []
        journey_path = tmp_path / bundle["journeys"][0]["customer_journey_map_ref"]
        assert journey_path.exists()


class TestSpecChainGeneration:
    def test_build_full_spec_chain(self, tmp_path):
        features = [
            {"feature_id": "f_onboarding", "feature_name": "Onboarding Wizard", "problem_ref": "Users struggle to onboard"},
            {"feature_id": "f_search", "feature_name": "Advanced Search", "problem_ref": "Users cannot find content"},
        ]
        bundle = build_full_spec_chain(tmp_path, features)
        assert bundle["schema_version"] == "1.0.0"
        assert len(bundle["features"]) == 2
        assert "execution_graph" in bundle
        assert "validation_checks" in bundle

    def test_feature_specs_have_required_fields(self, tmp_path):
        features = [{"feature_id": "f_test", "feature_name": "Test Feature", "problem_ref": "test"}]
        bundle = build_full_spec_chain(tmp_path, features)
        f = bundle["features"][0]
        assert "prd" in f
        assert "user_stories" in f
        assert "acceptance_criteria" in f
        assert "api_contracts" in f
        assert "agent_task_id" in f


class TestPRDGeneration:
    def test_prd_has_required_fields(self):
        spec = {"feature_id": "f1", "feature_name": "Test Feature", "problem_ref": "test problem"}
        prd = _generate_prd(spec, None)
        assert "problem_summary" in prd
        assert "outcome_summary" in prd
        assert "scope_boundaries" in prd
        assert "out_of_scope" in prd
        assert "success_metrics" in prd


class TestUserStoryGeneration:
    def test_stories_have_invest_fields(self):
        prd = {"problem_summary": "test", "outcome_summary": "test", "scope_boundaries": [], "out_of_scope": [], "success_metrics": []}
        spec = {"feature_id": "f1", "feature_name": "Test Feature", "problem_ref": "test"}
        stories = _generate_user_stories(prd, spec, None)
        for s in stories:
            assert "story_id" in s
            assert "title" in s
            assert "as_a" in s
            assert "i_want" in s
            assert "so_that" in s
            assert "priority" in s
