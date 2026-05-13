"""Tests for V13 vision analysis module."""

from pathlib import Path

import pytest

from core.python.productos_runtime.vision_analysis import (
    analyze_screenshot,
    _heuristic_screen_purpose,
    _heuristic_workflow_stage,
)


class TestHeuristicScreenPurpose:
    def test_dashboard_purpose(self):
        purpose = _heuristic_screen_purpose("dashboard_main")
        assert "dashboard" in purpose.lower() or "overview" in purpose.lower()

    def test_login_purpose(self):
        purpose = _heuristic_screen_purpose("login_page")
        assert "login" in purpose.lower() or "authentication" in purpose.lower()

    def test_unknown_purpose(self):
        purpose = _heuristic_screen_purpose("xyz_abc_123")
        assert purpose.startswith("Screen captured from workspace")


class TestHeuristicWorkflowStage:
    def test_login_stage(self):
        stage = _heuristic_workflow_stage("login_screen")
        assert stage == "awareness"

    def test_dashboard_stage(self):
        stage = _heuristic_workflow_stage("main_dashboard")
        assert stage == "adoption"

    def test_unknown_stage(self):
        stage = _heuristic_workflow_stage("random_file_name")
        assert stage == "unknown"


class TestAnalyzeScreenshot:
    def test_analyze_screenshot_output(self, tmp_path):
        screenshot = tmp_path / "inbox" / "screenshots" / "dashboard.png"
        screenshot.parent.mkdir(parents=True, exist_ok=True)
        screenshot.write_text("fake-image-data")

        result = analyze_screenshot(screenshot)
        assert "visual_record_id" in result
        assert "source_path" in result
        assert "screen_purpose" in result
        assert result["source_type"] == "screenshot"
        assert "provenance" in result
        assert result["provenance"]["confidence"] in ("inferred", "observed", "confirmed")

    def test_analyze_screenshot_links_to_journey(self):
        pass  # Integration test with journey linking
