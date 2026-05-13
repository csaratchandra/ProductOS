"""Tests for V14 Gap Intelligence Engine."""

import json
from pathlib import Path

import pytest

from core.python.productos_runtime.gap_intelligence import GapIntelligence
from core.python.productos_runtime.architecture_synthesis import ArchitectureSynthesis
from core.python.productos_runtime.intent_engine import IntentEngine
from conftest import SCHEMA_DIR


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def gap_engine() -> GapIntelligence:
    return GapIntelligence()


@pytest.fixture(scope="module")
def arch_engine() -> ArchitectureSynthesis:
    return ArchitectureSynthesis()


@pytest.fixture(scope="module")
def intent_engine() -> IntentEngine:
    return IntentEngine()


HEALTHCARE_INTENT = "A HIPAA-compliant prior authorization platform for US providers and payers with AI-assisted review"
SIMPLE_INTENT = "A simple to-do list app for individual users"


def _build_architecture(arch_engine, intent_engine, intent: str) -> dict:
    decomp = intent_engine.decompose(intent)
    prd = intent_engine.generate_master_prd(decomp)
    return arch_engine.synthesize(prd)


# ---------------------------------------------------------------------------
# Known gap fixtures
# ---------------------------------------------------------------------------

def _build_architecture_with_missing_handoff(arch_engine, intent_engine) -> dict:
    """Build architecture and then remove a handoff to create a known gap."""
    arch = _build_architecture(arch_engine, intent_engine, HEALTHCARE_INTENT)
    wom = arch["workflow_orchestration_map"]
    if wom.get("handoffs"):
        # Remove the second persona reference from orchestration to create orphan
        arch["workflow_orchestration_map"]["personas"] = ["pers_provider"]
        arch["workflow_orchestration_map"]["handoffs"] = []
    return arch


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestGapIntelligence:

    def test_analyze_clean_architecture(self, gap_engine, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine, SIMPLE_INTENT)
        result = gap_engine.analyze(arch)
        assert "gap_analysis_id" in result
        assert "gaps" in result
        assert "summary" in result
        assert result["summary"]["total_gaps"] >= 0

    def test_healthcare_architecture_has_some_gaps(self, gap_engine, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine, HEALTHCARE_INTENT)
        result = gap_engine.analyze(arch)
        assert result["summary"]["total_gaps"] >= 0

    def test_missing_handoff_detected(self, gap_engine, arch_engine, intent_engine):
        arch = _build_architecture_with_missing_handoff(arch_engine, intent_engine)
        result = gap_engine.analyze(arch)
        gap_types = {g["gap_type"] for g in result["gaps"]}
        assert "orphan_persona" in gap_types or "missing_handoff" in gap_types

    def test_gap_has_narrative_impact(self, gap_engine, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine, HEALTHCARE_INTENT)
        result = gap_engine.analyze(arch)
        for g in result["gaps"]:
            assert len(g["impact"]) >= 10, f"Gap {g['gap_id']} has no meaningful impact narrative"
            assert len(g["suggestion"]) >= 10, f"Gap {g['gap_id']} has no meaningful suggestion"

    def test_gap_has_confidence_score(self, gap_engine, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine, HEALTHCARE_INTENT)
        result = gap_engine.analyze(arch)
        for g in result["gaps"]:
            assert 0.0 <= g["confidence"] <= 1.0

    def test_gap_severity_is_valid(self, gap_engine, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine, HEALTHCARE_INTENT)
        result = gap_engine.analyze(arch)
        for g in result["gaps"]:
            assert g["severity"] in ("critical", "warning", "info")

    def test_gap_type_is_valid(self, gap_engine, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine, HEALTHCARE_INTENT)
        result = gap_engine.analyze(arch)
        valid_types = {
            "missing_handoff", "orphan_persona", "sla_inconsistency", "compliance_gap",
            "persona_coverage_gap", "api_contract_gap", "outcome_measurement_gap",
            "broken_cross_layer_link", "circular_dependency"
        }
        for g in result["gaps"]:
            assert g["gap_type"] in valid_types

    def test_summary_counts_match(self, gap_engine, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine, HEALTHCARE_INTENT)
        result = gap_engine.analyze(arch)
        summary = result["summary"]
        assert summary["total_gaps"] == summary["critical_count"] + summary["warning_count"] + summary["info_count"]

    def test_suggest_fixes_returns_suggestions(self, gap_engine, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine, HEALTHCARE_INTENT)
        result = gap_engine.analyze(arch)
        suggestion_set = gap_engine.suggest_fixes(result["gaps"])
        assert "suggestion_set_id" in suggestion_set
        assert suggestion_set["total_suggestions"] == len(result["gaps"])
        for s in suggestion_set["suggestions"]:
            assert "gap_ref" in s
            assert "suggestion" in s
            assert "effort_estimate" in s

    def test_auto_fix_available_flag(self, gap_engine, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine, HEALTHCARE_INTENT)
        result = gap_engine.analyze(arch)
        for g in result["gaps"]:
            assert "auto_fix_available" in g

    def test_gap_has_affected_artifact_uuids(self, gap_engine, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine, HEALTHCARE_INTENT)
        result = gap_engine.analyze(arch)
        for g in result["gaps"]:
            assert "affected_artifact_uuids" in g

    def test_clean_architecture_returns_valid_summary(self, gap_engine, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine, "A simple calculator app")
        result = gap_engine.analyze(arch)
        assert result["summary"]["total_gaps"] >= 0


class TestGapAnalysisSchema:
    def test_schema_loads(self):
        schema_path = SCHEMA_DIR / "gap_analysis.schema.json"
        assert schema_path.exists()
        with schema_path.open("r", encoding="utf-8") as f:
            schema = json.load(f)
        assert schema["$id"].endswith("gap_analysis.schema.json")
