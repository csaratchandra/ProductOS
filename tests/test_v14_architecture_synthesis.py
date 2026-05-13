"""Tests for V14 Architecture Synthesis Engine."""

import json
from pathlib import Path

import pytest

from core.python.productos_runtime.architecture_synthesis import ArchitectureSynthesis
from core.python.productos_runtime.intent_engine import IntentEngine
from conftest import SCHEMA_DIR


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def engine() -> ArchitectureSynthesis:
    return ArchitectureSynthesis()


@pytest.fixture(scope="module")
def intent_engine() -> IntentEngine:
    return IntentEngine()


SIMPLE_INTENT = "A task management tool for small teams with assignees and reviewers"
MEDIUM_INTENT = "A HIPAA-compliant prior authorization platform for US providers and payers with AI-assisted review"
COMPLEX_INTENT = "A global multi-currency payment processing platform for merchants, consumers, and bank partners in US, EU, and APAC with PCI-DSS compliance and fraud detection"


def _get_master_prd(intent_engine: IntentEngine, intent: str) -> dict:
    decomp = intent_engine.decompose(intent)
    return intent_engine.generate_master_prd(decomp)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestArchitectureSynthesis:

    def test_simple_synthesis(self, engine: ArchitectureSynthesis, intent_engine: IntentEngine):
        prd = _get_master_prd(intent_engine, SIMPLE_INTENT)
        arch = engine.synthesize(prd)
        assert arch["schema_version"] == "1.0.0"
        assert len(arch["artifacts"]) >= 5
        assert "persona_archetype_pack" in arch
        assert "workflow_orchestration_map" in arch
        assert "component_prds" in arch
        assert "zoom_navigation_map" in arch

    def test_medium_synthesis_all_artifacts(self, engine: ArchitectureSynthesis, intent_engine: IntentEngine):
        prd = _get_master_prd(intent_engine, MEDIUM_INTENT)
        arch = engine.synthesize(prd)
        assert len(arch["persona_archetype_pack"]["archetypes"]) >= 2
        assert len(arch["workflow_orchestration_map"]["handoffs"]) >= 1
        assert len(arch["component_prds"]) >= 1
        assert len(arch["customer_journey_maps"]) >= 1
        assert len(arch["api_contract_hypotheses"]) >= 1
        assert len(arch["zoom_navigation_map"]["levels"]) >= 3

    def test_complex_synthesis_cross_links(self, engine: ArchitectureSynthesis, intent_engine: IntentEngine):
        prd = _get_master_prd(intent_engine, COMPLEX_INTENT)
        arch = engine.synthesize(prd)
        assert len(arch["cross_links"]) >= 5
        for link in arch["cross_links"]:
            assert "source_artifact_uuid" in link
            assert "target_artifact_uuid" in link
            assert link.get("confidence", 0) > 0

    def test_synthesis_duration_under_15s(self, engine: ArchitectureSynthesis, intent_engine: IntentEngine):
        import time
        prd = _get_master_prd(intent_engine, MEDIUM_INTENT)
        start = time.time()
        engine.synthesize(prd)
        duration = time.time() - start
        assert duration < 15, f"Synthesis took {duration:.2f}s (expected <15s)"

    def test_synthesis_includes_generation_metadata(self, engine: ArchitectureSynthesis, intent_engine: IntentEngine):
        prd = _get_master_prd(intent_engine, MEDIUM_INTENT)
        arch = engine.synthesize(prd)
        meta = arch["generation_metadata"]
        assert meta["mode"] in ("standard", "quick", "full")
        assert meta["duration_ms"] >= 0
        assert meta["decomposition_uuid"]

    def test_artifact_types_are_valid(self, engine: ArchitectureSynthesis, intent_engine: IntentEngine):
        prd = _get_master_prd(intent_engine, MEDIUM_INTENT)
        arch = engine.synthesize(prd)
        valid_types = {
            "master_prd", "persona_archetype_pack", "workflow_orchestration_map", "component_prd",
            "customer_journey_map", "api_contract_hypothesis", "zoom_navigation_map"
        }
        for art in arch["artifacts"]:
            assert art["type"] in valid_types

    def test_workflow_has_compliance_gates_for_regulated(self, engine: ArchitectureSynthesis, intent_engine: IntentEngine):
        prd = _get_master_prd(intent_engine, MEDIUM_INTENT)
        arch = engine.synthesize(prd)
        wom = arch["workflow_orchestration_map"]
        assert len(wom.get("compliance_gates", [])) >= 1

    def test_component_prds_at_handoff_boundaries(self, engine: ArchitectureSynthesis, intent_engine: IntentEngine):
        prd = _get_master_prd(intent_engine, COMPLEX_INTENT)
        arch = engine.synthesize(prd)
        wom = arch["workflow_orchestration_map"]
        components = arch["component_prds"]
        assert len(components) >= 1
        for c in components:
            assert "assigned_personas" in c
            assert "api_endpoints" in c

    def test_journey_maps_per_persona(self, engine: ArchitectureSynthesis, intent_engine: IntentEngine):
        prd = _get_master_prd(intent_engine, MEDIUM_INTENT)
        arch = engine.synthesize(prd)
        num_personas = len(arch["persona_archetype_pack"]["archetypes"])
        assert len(arch["customer_journey_maps"]) == num_personas

    def test_cross_link_types_are_valid(self, engine: ArchitectureSynthesis, intent_engine: IntentEngine):
        prd = _get_master_prd(intent_engine, MEDIUM_INTENT)
        arch = engine.synthesize(prd)
        valid_link_types = {"depends_on", "references", "implements", "traces_to", "validates", "handoff_pair"}
        for link in arch["cross_links"]:
            assert link["link_type"] in valid_link_types


class TestCrossConsistency:

    def test_clean_architecture_passes(self, engine: ArchitectureSynthesis, intent_engine: IntentEngine):
        prd = _get_master_prd(intent_engine, MEDIUM_INTENT)
        arch = engine.synthesize(prd)
        report = engine.validate_cross_consistency(arch)
        assert report["overall_status"] in ("passed", "warning")
        assert len(report["checks_passed"]) >= 1

    def test_all_personas_in_orchestration(self, engine: ArchitectureSynthesis, intent_engine: IntentEngine):
        prd = _get_master_prd(intent_engine, MEDIUM_INTENT)
        arch = engine.synthesize(prd)
        report = engine.validate_cross_consistency(arch)
        for fail in report["checks_failed"]:
            assert fail["check_name"] != "persona_in_orchestration"

    def test_no_orphan_artifacts_in_healthy(self, engine: ArchitectureSynthesis, intent_engine: IntentEngine):
        prd = _get_master_prd(intent_engine, SIMPLE_INTENT)
        arch = engine.synthesize(prd)
        report = engine.validate_cross_consistency(arch)
        for fail in report["checks_failed"]:
            assert fail["check_name"] != "orphan_artifacts"

    def test_report_has_required_fields(self, engine: ArchitectureSynthesis, intent_engine: IntentEngine):
        prd = _get_master_prd(intent_engine, MEDIUM_INTENT)
        arch = engine.synthesize(prd)
        report = engine.validate_cross_consistency(arch)
        assert "consistency_report_id" in report
        assert "architecture_ref" in report
        assert "overall_status" in report
        assert "created_at" in report

    def test_schema_version_present(self, engine: ArchitectureSynthesis, intent_engine: IntentEngine):
        prd = _get_master_prd(intent_engine, MEDIUM_INTENT)
        arch = engine.synthesize(prd)
        report = engine.validate_cross_consistency(arch)
        assert report["schema_version"] == "1.0.0"


class TestProductArchitectureSchema:
    def test_schema_loads(self):
        schema_path = SCHEMA_DIR / "product_architecture.schema.json"
        assert schema_path.exists()
        with schema_path.open("r", encoding="utf-8") as f:
            schema = json.load(f)
        assert schema["$id"].endswith("product_architecture.schema.json")


class TestConsistencyReportSchema:
    def test_schema_loads(self):
        schema_path = SCHEMA_DIR / "consistency_report.schema.json"
        assert schema_path.exists()
        with schema_path.open("r", encoding="utf-8") as f:
            schema = json.load(f)
        assert schema["$id"].endswith("consistency_report.schema.json")
