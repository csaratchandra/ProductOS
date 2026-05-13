"""Tests for V14 Architecture Exporter — all 12 output formats."""

import json
from pathlib import Path

import pytest

from core.python.productos_runtime.architecture_exporter import ArchitectureExporter
from core.python.productos_runtime.architecture_synthesis import ArchitectureSynthesis
from core.python.productos_runtime.intent_engine import IntentEngine
from conftest import SCHEMA_DIR


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def exporter() -> ArchitectureExporter:
    return ArchitectureExporter()


@pytest.fixture(scope="module")
def arch_engine() -> ArchitectureSynthesis:
    return ArchitectureSynthesis()


@pytest.fixture(scope="module")
def intent_engine() -> IntentEngine:
    return IntentEngine()


HEALTHCARE_INTENT = "A HIPAA-compliant prior authorization platform for US providers and payers with AI-assisted review"


def _build_architecture(arch_engine, intent_engine) -> dict:
    decomp = intent_engine.decompose(HEALTHCARE_INTENT)
    prd = intent_engine.generate_master_prd(decomp)
    return arch_engine.synthesize(prd)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestArchitectureExportAll:

    def test_export_all_returns_12_formats(self, exporter, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine)
        bundle = exporter.export_all(arch)
        assert len(bundle) == 12

    def test_json_export_valid(self, exporter, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine)
        bundle = exporter.export_all(arch)
        parsed = json.loads(bundle["json_artifacts"])
        assert "product_architecture" in parsed

    def test_markdown_prds_export(self, exporter, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine)
        bundle = exporter.export_all(arch)
        assert "Product Architecture — Markdown PRD Export" in bundle["markdown_prds"]
        assert "## Component PRDs" in bundle["markdown_prds"]

    def test_html_atlas_export(self, exporter, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine)
        bundle = exporter.export_all(arch)
        assert "<!DOCTYPE html>" in bundle["html_atlas"]
        assert "Product Atlas" in bundle["html_atlas"]

    def test_adaptive_prototype_export(self, exporter, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine)
        bundle = exporter.export_all(arch)
        assert "<!DOCTYPE html>" in bundle["html_prototype"]
        assert "persona-switcher" in bundle["html_prototype"]

    def test_simulation_dashboard_export(self, exporter, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine)
        bundle = exporter.export_all(arch)
        assert "<!DOCTYPE html>" in bundle["html_simulation"]
        assert "Simulation Dashboard" in bundle["html_simulation"]

    def test_executive_summary_export(self, exporter, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine)
        bundle = exporter.export_all(arch)
        assert "Executive Summary" in bundle["executive_summary_pdf"]

    def test_mermaid_diagram_export(self, exporter, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine)
        bundle = exporter.export_all(arch)
        assert "graph TD" in bundle["mermaid_diagram"]

    def test_analytics_spec_export(self, exporter, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine)
        bundle = exporter.export_all(arch)
        parsed = json.loads(bundle["analytics_spec"])
        assert "event_taxonomy" in parsed

    def test_outcome_cascade_export(self, exporter, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine)
        bundle = exporter.export_all(arch)
        parsed = json.loads(bundle["outcome_cascade"])
        assert "cascade" in parsed

    def test_ai_layer_plan_export(self, exporter, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine)
        bundle = exporter.export_all(arch)
        parsed = json.loads(bundle["ai_layer_plan"])
        assert "automation_candidates" in parsed

    def test_experience_plan_export(self, exporter, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine)
        bundle = exporter.export_all(arch)
        parsed = json.loads(bundle["experience_plan"])
        assert "per_persona_device_context" in parsed

    def test_pm_briefing_export(self, exporter, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine)
        bundle = exporter.export_all(arch)
        assert "PM Briefing" in bundle["pm_briefing"]
        assert "What You Asked For" in bundle["pm_briefing"]

    def test_pm_briefing_with_gaps(self, exporter, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine)
        gaps = [{"gap_id": "g1", "severity": "critical", "description": "Test gap for briefing",
                 "impact": "This is a test impact", "suggestion": "This is a test suggestion", "confidence": 0.9}]
        briefing = exporter.generate_pm_briefing(arch, gaps, {}, {"domain": "healthcare", "confidence": 0.95})
        assert "Test gap for briefing" in briefing
        assert "Top Gaps" in briefing


class TestPMBriefingSchema:
    def test_schema_loads(self):
        schema_path = SCHEMA_DIR / "pm_briefing.schema.json"
        assert schema_path.exists()
        with schema_path.open("r", encoding="utf-8") as f:
            schema = json.load(f)
        assert schema["$id"].endswith("pm_briefing.schema.json")
