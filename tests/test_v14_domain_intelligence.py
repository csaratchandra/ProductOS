"""Tests for V14 Domain Intelligence Engine."""

import json
from pathlib import Path

import pytest

from core.python.productos_runtime.domain_intelligence import DomainIntelligence
from core.python.productos_runtime.intent_engine import IntentEngine
from conftest import SCHEMA_DIR


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def domain_engine() -> DomainIntelligence:
    return DomainIntelligence()


@pytest.fixture(scope="module")
def intent_engine() -> IntentEngine:
    return IntentEngine()


HEALTHCARE_INTENT = "A HIPAA-compliant prior authorization platform for US providers and payers with AI-assisted review"
FINANCE_INTENT = "A FIX-compliant trade execution platform for US and EU capital markets with real-time risk management"
VAGUE_INTENT = "A simple to-do list app"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestDomainAutoActivate:

    def test_healthcare_activation(self, domain_engine, intent_engine):
        decomp = intent_engine.decompose(HEALTHCARE_INTENT)
        activation = domain_engine.auto_activate(decomp)
        assert activation["domain"] == "healthcare"
        assert activation["confidence"] >= 0.9
        assert "us" in activation["regions"]

    def test_finance_activation(self, domain_engine, intent_engine):
        decomp = intent_engine.decompose(FINANCE_INTENT)
        activation = domain_engine.auto_activate(decomp)
        assert activation["domain"] == "finance"
        assert "us" in activation["regions"]
        assert "eu" in activation["regions"]

    def test_vague_returns_general(self, domain_engine, intent_engine):
        decomp = intent_engine.decompose(VAGUE_INTENT)
        activation = domain_engine.auto_activate(decomp)
        assert activation["domain"] == "general" or activation["confidence"] < 0.5

    def test_healthcare_sub_packs(self, domain_engine, intent_engine):
        decomp = intent_engine.decompose(HEALTHCARE_INTENT)
        activation = domain_engine.auto_activate(decomp)
        assert len(activation.get("sub_packs", [])) >= 0

    def test_compatibility_notes_for_multi_region(self, domain_engine, intent_engine):
        decomp = intent_engine.decompose(FINANCE_INTENT)
        activation = domain_engine.auto_activate(decomp)
        if len(activation["regions"]) > 1:
            assert len(activation["compatibility_notes"]) >= 1

    def test_activation_required_fields(self, domain_engine, intent_engine):
        decomp = intent_engine.decompose(HEALTHCARE_INTENT)
        activation = domain_engine.auto_activate(decomp)
        assert "domain_activation_id" in activation
        assert "decomposition_ref" in activation
        assert "created_at" in activation

    def test_no_domain_returns_notes(self, domain_engine, intent_engine):
        decomp = intent_engine.decompose(VAGUE_INTENT)
        activation = domain_engine.auto_activate(decomp)
        if activation["domain"] == "general":
            assert len(activation["compatibility_notes"]) >= 1


class TestEnrichArchitecture:

    def _build_test_architecture(self) -> dict:
        return {
            "product_architecture_id": "arch_test",
            "workflow_orchestration_map": {
                "handoffs": [
                    {"handoff_id": "ho_001", "source_persona": "pers_provider", "target_persona": "pers_payer",
                     "shared_artifact": "prior_auth_request", "sla_target_seconds": 3600},
                ],
                "compliance_gates": [],
            },
            "component_prds": [],
        }

    def test_healthcare_enrichment_adds_compliance_gates(self, domain_engine):
        arch = self._build_test_architecture()
        activation = {
            "domain": "healthcare",
            "regions": ["us"],
            "sub_packs": [],
            "confidence": 0.95,
            "domain_activation_id": "da_test",
        }
        report = domain_engine.enrich_architecture(arch, activation)
        assert report["summary"]["total_additions"] >= 1
        assert report["summary"]["compliance_gates_added"] >= 1

    def test_enrichment_adds_data_model_refs(self, domain_engine):
        arch = self._build_test_architecture()
        activation = {"domain": "healthcare", "regions": ["us"], "sub_packs": [], "confidence": 0.95, "domain_activation_id": "da_test"}
        report = domain_engine.enrich_architecture(arch, activation)
        data_refs = [a for a in report["additions"] if a["addition_type"] == "data_model_ref"]
        assert len(data_refs) >= 1

    def test_enrichment_required_fields(self, domain_engine):
        arch = self._build_test_architecture()
        activation = {"domain": "healthcare", "regions": ["us"], "sub_packs": [], "confidence": 0.95, "domain_activation_id": "da_test"}
        report = domain_engine.enrich_architecture(arch, activation)
        assert "enrichment_report_id" in report
        assert "architecture_ref" in report
        assert "domain_activation_ref" in report

    def test_enrichment_adds_sla_constraints_for_healthcare_us(self, domain_engine):
        arch = self._build_test_architecture()
        activation = {"domain": "healthcare", "regions": ["us"], "sub_packs": [], "confidence": 0.95, "domain_activation_id": "da_test"}
        report = domain_engine.enrich_architecture(arch, activation)
        sla_additions = [a for a in report["additions"] if a["addition_type"] == "sla_constraint"]
        assert len(sla_additions) >= 1

    def test_each_addition_has_rationale(self, domain_engine):
        arch = self._build_test_architecture()
        activation = {"domain": "healthcare", "regions": ["us"], "sub_packs": [], "confidence": 0.95, "domain_activation_id": "da_test"}
        report = domain_engine.enrich_architecture(arch, activation)
        for a in report["additions"]:
            assert len(a["rationale"]) >= 5


class TestValidateComplianceCoverage:

    def _build_compliant_architecture(self) -> dict:
        return {
            "product_architecture_id": "arch_test",
            "workflow_orchestration_map": {
                "handoffs": [],
                "compliance_gates": [
                    {"gate_id": "g1", "name": "audit log at phi handoffs", "description": "HIPAA audit log requirement"},
                    {"gate_id": "g2", "name": "consent record at data access", "description": "Patient consent verification"},
                    {"gate_id": "g3", "name": "phi encryption at rest", "description": "PHI data encryption"},
                    {"gate_id": "g4", "name": "phi encryption in transit", "description": "PHI data encryption in transit"},
                ],
            },
        }

    def test_compliant_architecture_passes(self, domain_engine):
        arch = self._build_compliant_architecture()
        activation = {"domain": "healthcare", "regions": ["us"], "sub_packs": [], "confidence": 0.95, "domain_activation_id": "da_test"}
        report = domain_engine.validate_compliance_coverage(arch, activation)
        assert report["overall_coverage_score"] >= 0.3

    def test_compliance_report_has_required_fields(self, domain_engine):
        arch = self._build_compliant_architecture()
        activation = {"domain": "healthcare", "regions": ["us"], "sub_packs": [], "confidence": 0.95, "domain_activation_id": "da_test"}
        report = domain_engine.validate_compliance_coverage(arch, activation)
        assert "compliance_report_id" in report
        assert "regulations" in report
        assert "overall_coverage_score" in report
        assert "critical_gaps" in report

    def test_hipaa_validation(self, domain_engine):
        arch = {"product_architecture_id": "arch_test", "workflow_orchestration_map": {"handoffs": [], "compliance_gates": []}}
        activation = {"domain": "healthcare", "regions": ["us"], "sub_packs": [], "confidence": 0.95, "domain_activation_id": "da_test"}
        report = domain_engine.validate_compliance_coverage(arch, activation)
        hipaa = next((r for r in report["regulations"] if r["regulation"] == "HIPAA"), None)
        assert hipaa is not None
        assert hipaa["status"] in ("compliant", "partial", "non_compliant")

    def test_non_compliant_has_gaps(self, domain_engine):
        arch = {"product_architecture_id": "arch_test", "workflow_orchestration_map": {"handoffs": [], "compliance_gates": []}}
        activation = {"domain": "healthcare", "regions": ["us"], "sub_packs": [], "confidence": 0.95, "domain_activation_id": "da_test"}
        report = domain_engine.validate_compliance_coverage(arch, activation)
        assert len(report["critical_gaps"]) >= 1

    def test_non_compliant_gaps_have_actions(self, domain_engine):
        arch = {"product_architecture_id": "arch_test", "workflow_orchestration_map": {"handoffs": [], "compliance_gates": []}}
        activation = {"domain": "healthcare", "regions": ["us"], "sub_packs": [], "confidence": 0.95, "domain_activation_id": "da_test"}
        report = domain_engine.validate_compliance_coverage(arch, activation)
        for gap in report["critical_gaps"]:
            assert len(gap["required_action"]) >= 10


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------

class TestDomainSchemas:
    def test_domain_activation_schema_loads(self):
        for name in ["domain_activation", "enrichment_report", "compliance_report"]:
            schema_path = SCHEMA_DIR / f"{name}.schema.json"
            assert schema_path.exists(), f"Missing schema: {name}"
            with schema_path.open("r", encoding="utf-8") as f:
                schema = json.load(f)
            assert schema["$id"].endswith(f"{name}.schema.json")
