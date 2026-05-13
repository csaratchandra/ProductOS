"""Tests for V14 Intent Engine — intent decomposition and master PRD generation."""

import json
from pathlib import Path

import pytest

from core.python.productos_runtime.intent_engine import IntentEngine
from conftest import validator_for, SCHEMA_DIR


# ---------------------------------------------------------------------------
# Fixtures — 10 intents of varying specificity
# ---------------------------------------------------------------------------

INTENT_FIXTURES = [
    ("vague", "a healthcare app", False, "general"),
    ("general_saas", "a project management tool with workflow automation for remote teams", True, "enterprise_saas"),
    ("healthcare_vague", "a platform for doctors to manage patient records", True, "healthcare"),
    ("prior_auth_full", "A HIPAA-compliant prior authorization platform for US providers and payers with AI-assisted review", True, "healthcare"),
    ("finance_trading", "A FIX-compliant trade execution platform for US and EU capital markets with real-time risk management", True, "finance"),
    ("fintech_payments", "A PCI-DSS compliant payment processing platform with AML/KYC for banking and lending", True, "finance"),
    ("healthcare_telehealth", "A telehealth platform connecting patients with providers for virtual consultations with EHR integration", True, "healthcare"),
    ("ecommerce_marketplace", "A multi-vendor marketplace connecting buyers and sellers with inventory management and fulfillment", True, "ecommerce"),
    ("enterprise_compliance", "Enterprise compliance automation platform for legal and risk teams with audit trail and reporting", True, "enterprise_saas"),
    ("empty", "", False, None),
]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestIntentEngineDecompose:
    """Intent decomposition tests."""

    @pytest.fixture
    def engine(self) -> IntentEngine:
        return IntentEngine()

    @pytest.mark.parametrize("name,intent,expect_valid,expected_domain", [
        (n, i, e, d) for n, i, e, d in INTENT_FIXTURES if n != "empty"
    ])
    def test_decompose_valid_intents(self, engine: IntentEngine, name: str, intent: str, expect_valid: bool, expected_domain: str):
        result = engine.decompose(intent)
        assert result["schema_version"] == "1.0.0"
        assert result["raw_text"] == intent.strip()
        assert len(result["extracted_problem"]) >= 10
        assert len(result["extracted_outcomes"]) >= 1
        assert len(result["inferred_personas"]) >= 1
        assert result["domain_match"]["domain"] == expected_domain or (expected_domain == "general" and result["domain_match"]["confidence"] < 0.5)

        if expect_valid:
            assert result["domain_match"]["confidence"] >= 0.2
        else:
            assert len(result["ambiguity_flags"]) > 0

    def test_empty_intent_raises(self, engine: IntentEngine):
        with pytest.raises(ValueError, match="at least 10 characters"):
            engine.decompose("")

    def test_short_intent_raises(self, engine: IntentEngine):
        with pytest.raises(ValueError, match="at least 10 characters"):
            engine.decompose("hi")

    def test_specific_prior_auth_personas(self, engine: IntentEngine):
        result = engine.decompose(INTENT_FIXTURES[3][1])
        persona_labels = [p["label"].lower() for p in result["inferred_personas"]]
        assert "provider" in " ".join(persona_labels) or "providers" in " ".join(persona_labels)
        assert "payer" in " ".join(persona_labels) or "payers" in " ".join(persona_labels)

    def test_healthcare_has_hipaa_constraint(self, engine: IntentEngine):
        result = engine.decompose(INTENT_FIXTURES[3][1])
        compliance_constraints = [c for c in result["implied_constraints"] if c["type"] == "compliance"]
        assert len(compliance_constraints) >= 1
        assert any("HIPAA" in c["description"].upper() for c in compliance_constraints)

    def test_finance_has_pci_constraint(self, engine: IntentEngine):
        result = engine.decompose(INTENT_FIXTURES[5][1])
        compliance_constraints = [c for c in result["implied_constraints"] if c["type"] == "compliance"]
        assert len(compliance_constraints) >= 1
        assert any("PCI" in c["description"].upper() for c in compliance_constraints)

    def test_vague_intent_has_ambiguity_flags(self, engine: IntentEngine):
        result = engine.decompose(INTENT_FIXTURES[0][1])
        assert len(result["ambiguity_flags"]) > 0
        assert len(result["suggested_clarifications"]) > 0

    def test_confidence_scores_present(self, engine: IntentEngine):
        result = engine.decompose(INTENT_FIXTURES[3][1])
        cs = result["confidence_scores"]
        assert cs["overall"] >= 0.0
        assert cs["overall"] <= 1.0
        assert cs["problem"] >= 0.0
        assert cs["domain"] >= 0.0

    def test_specific_intent_confidence(self, engine: IntentEngine):
        result = engine.decompose(INTENT_FIXTURES[3][1])
        assert result["domain_match"]["confidence"] >= 0.8

    def test_inferred_personas_have_confidence(self, engine: IntentEngine):
        result = engine.decompose(INTENT_FIXTURES[3][1])
        for p in result["inferred_personas"]:
            assert 0.0 <= p["confidence"] <= 1.0

    def test_ai_mention_triggers_ambiguity(self, engine: IntentEngine):
        result = engine.decompose("an AI-powered platform for team collaboration")
        ai_flags = [f for f in result["ambiguity_flags"] if "AI" in f["statement"] or "ai" in f["statement"].lower()]
        assert len(ai_flags) >= 1

    def test_outcomes_smart_formatted(self, engine: IntentEngine):
        result = engine.decompose(INTENT_FIXTURES[3][1])
        for o in result["extracted_outcomes"]:
            assert len(o["description"]) > 5
            assert len(o["measurement"]) > 3


class TestIntentEngineMasterPRD:
    """Master PRD generation from decomposition."""

    @pytest.fixture
    def engine(self) -> IntentEngine:
        return IntentEngine()

    def test_generates_all_sections(self, engine: IntentEngine):
        decomposition = engine.decompose(INTENT_FIXTURES[3][1])
        prd = engine.generate_master_prd(decomposition)
        assert "master_prd_id" in prd
        assert "executive_summary" in prd
        assert "problem_statement" in prd
        assert "business_outcomes" in prd
        assert "success_metrics" in prd
        assert "scope_boundaries" in prd
        assert "persona_coverage_map" in prd
        assert "assumptions" in prd

    def test_assumptions_have_provenance(self, engine: IntentEngine):
        decomposition = engine.decompose(INTENT_FIXTURES[3][1])
        prd = engine.generate_master_prd(decomposition)
        for a in prd["assumptions"]:
            assert a["provenance"] in ("observed", "inferred", "assumed")

    def test_persona_coverage_from_decomposition(self, engine: IntentEngine):
        decomposition = engine.decompose(INTENT_FIXTURES[3][1])
        prd = engine.generate_master_prd(decomposition)
        assert len(prd["persona_coverage_map"]) >= 1
        for pc in prd["persona_coverage_map"]:
            assert pc["coverage_status"] in ("primary", "secondary")

    def test_scope_boundaries_from_constraints(self, engine: IntentEngine):
        decomposition = engine.decompose(INTENT_FIXTURES[3][1])
        prd = engine.generate_master_prd(decomposition)
        if decomposition["implied_constraints"]:
            assert len(prd["scope_boundaries"]) >= 1


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------

class TestIntentDecompositionSchema:
    """Validate intent decomposition schema itself."""

    def test_schema_loads(self):
        schema_path = SCHEMA_DIR / "intent_decomposition.schema.json"
        assert schema_path.exists()
        with schema_path.open("r", encoding="utf-8") as f:
            schema = json.load(f)
        assert schema["$id"].endswith("intent_decomposition.schema.json")
        assert schema["title"] == "ProductOS Intent Decomposition"
