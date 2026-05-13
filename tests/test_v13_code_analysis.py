"""Tests for V13 code analysis module."""

import json
from pathlib import Path

import pytest

from core.python.productos_runtime.code_analysis import (
    analyze_code_repository,
    _extract_module_graph,
    _extract_api_surface,
    _extract_feature_flags,
)


ROOT = Path(__file__).resolve().parents[1]


class TestModuleDetection:
    def test_extract_modules_from_repo(self):
        modules = _extract_module_graph(ROOT)
        assert len(modules) > 0
        assert any("code_analysis" in m["module_name"] for m in modules)

    def test_module_has_required_fields(self):
        modules = _extract_module_graph(ROOT)
        for m in modules:
            assert "module_name" in m
            assert "module_path" in m
            assert "purpose" in m
            assert "confidence" in m


class TestApiEndpointExtraction:
    def test_detects_flask_routes(self):
        endpoints = _extract_api_surface(ROOT)
        for ep in endpoints:
            assert "method" in ep
            assert "path" in ep
            assert "inferred_feature" in ep

    def test_endpoint_confidence(self):
        endpoints = _extract_api_surface(ROOT)
        for ep in endpoints:
            assert ep["confidence"] in ("observed", "inferred", "uncertain")


class TestFeatureFlagDetection:
    def test_detects_feature_flags(self):
        flags = _extract_feature_flags(ROOT)
        for f in flags:
            assert "flag_name" in f
            assert "location" in f
            assert "confidence" in f


class TestFullAnalysis:
    def test_analyze_code_repository_output(self):
        result = analyze_code_repository(ROOT)
        assert result["schema_version"] == "1.0.0"
        assert len(result["module_graph"]) > 0
        assert "api_surface" in result
        assert "change_velocity" in result
        assert "evidence_confidence" in result

    def test_code_understanding_output_valid(self):
        result = analyze_code_repository(ROOT)
        assert result["schema_version"] == "1.0.0"
        assert isinstance(result["module_graph"], list)
