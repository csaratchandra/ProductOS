"""Tests for V13 spec export formats."""

import json
from pathlib import Path

import pytest

from core.python.productos_runtime.spec_export import (
    export_agent_native_json,
    export_agent_tools_json,
    export_github_issues,
    export_spec_bundle,
)


SAMPLE_BUNDLE = {
    "schema_version": "1.0.0",
    "build_spec_bundle_id": "bsb_test",
    "workspace_id": "test_ws",
    "features": [
        {
            "feature_id": "f1",
            "feature_name": "Onboarding Wizard",
            "agent_task_id": "task_f1",
            "prd": {
                "problem_summary": "Users struggle to onboard",
                "outcome_summary": "80% completion rate",
                "scope_boundaries": ["wizard UI", "progress tracking"],
                "out_of_scope": ["multi-language"],
                "success_metrics": [{"metric_name": "completion_rate", "target_value": "80%"}],
            },
            "user_stories": [
                {"story_id": "us_1", "title": "Story 1", "as_a": "user", "i_want": "to onboard", "so_that": "I can use the product", "priority": "P0", "acceptance_criteria_ids": ["ac_1"], "estimated_story_points": 3},
            ],
            "acceptance_criteria": [
                {"ac_id": "ac_1", "story_id": "us_1", "given": "user is authenticated", "when": "user starts onboarding", "then": "wizard appears", "edge_cases": []},
            ],
            "api_contracts": [
                {"endpoint": "/api/v1/onboarding", "method": "POST", "request_schema": {}, "response_schema": {}, "auth_required": True, "ac_source_ids": ["ac_1"]},
            ],
        }
    ],
    "execution_graph": {
        "nodes": [{"node_id": "node_f1", "feature_id": "f1", "task_type": "build_feature", "description": "Build wizard"}],
        "edges": [],
    },
    "validation_checks": [{"artifact_ref": "feature_f1", "schema_valid": True, "quality_score": 85, "warnings": []}],
    "evidence_trail": [{"claim": "Feature test", "source_artifact_ref": "psm.json", "confidence": "observed"}],
    "generated_at": "2026-03-22T08:00:00Z",
}


class TestAgentNativeJSON:
    def test_export_returns_summary(self):
        result = export_agent_native_json(SAMPLE_BUNDLE)
        assert "bundle" in result
        assert "execution_summary" in result
        assert "agent_instructions" in result

    def test_execution_summary_counts(self):
        result = export_agent_native_json(SAMPLE_BUNDLE)
        summary = result["execution_summary"]
        assert summary["total_features"] == 1
        assert summary["total_stories"] == 1
        assert summary["total_criteria"] == 1

    def test_export_writes_to_file(self, tmp_path):
        output = tmp_path / "export.json"
        result = export_agent_native_json(SAMPLE_BUNDLE, output_path=output)
        assert output.exists()
        data = json.loads(output.read_text(encoding="utf-8"))
        assert "build_spec_bundle_id" in data


class TestAgentToolsJSON:
    def test_export_tool_definitions(self):
        tools = export_agent_tools_json(SAMPLE_BUNDLE)
        assert len(tools) == 1
        tool = tools[0]
        assert "name" in tool
        assert "description" in tool
        assert "input_schema" in tool
        assert "validation_rules" in tool

    def test_tool_name_is_slug(self):
        tools = export_agent_tools_json(SAMPLE_BUNDLE)
        assert tools[0]["name"] == "build_onboarding_wizard"

    def test_validation_rules_populated(self):
        tools = export_agent_tools_json(SAMPLE_BUNDLE)
        assert len(tools[0]["validation_rules"]) == 1


class TestGitHubIssues:
    def test_dry_run_output(self):
        result = export_github_issues(SAMPLE_BUNDLE, dry_run=True)
        assert result["dry_run"] is True
        assert len(result["epics"]) == 1

    def test_epic_has_issues(self):
        result = export_github_issues(SAMPLE_BUNDLE)
        epic = result["epics"][0]
        assert len(epic["issues"]) == 1

    def test_issue_body_format(self):
        result = export_github_issues(SAMPLE_BUNDLE)
        issue = result["epics"][0]["issues"][0]
        assert "###" in issue["body"]
        assert "**As a**" in issue["body"]

    def test_acceptance_criteria_in_body(self):
        result = export_github_issues(SAMPLE_BUNDLE)
        issue = result["epics"][0]["issues"][0]
        assert "**Given**" in issue["body"]
        assert "**When**" in issue["body"]
        assert "**Then**" in issue["body"]


class TestExportDispatch:
    def test_format_json(self):
        result = export_spec_bundle(SAMPLE_BUNDLE, "json")
        assert "bundle" in result

    def test_format_agent_tools(self):
        result = export_spec_bundle(SAMPLE_BUNDLE, "agent_tools")
        assert isinstance(result, list)

    def test_format_github(self):
        result = export_spec_bundle(SAMPLE_BUNDLE, "github")
        assert "epics" in result

    def test_invalid_format(self):
        with pytest.raises(ValueError):
            export_spec_bundle(SAMPLE_BUNDLE, "invalid_format")
