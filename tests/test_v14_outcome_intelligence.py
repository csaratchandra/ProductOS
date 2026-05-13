"""Tests for V14 Outcome Intelligence."""

import pytest
from core.python.productos_runtime.outcome_intelligence import OutcomeIntelligence
from core.python.productos_runtime.architecture_synthesis import ArchitectureSynthesis
from core.python.productos_runtime.intent_engine import IntentEngine


@pytest.fixture(scope="module")
def oi() -> OutcomeIntelligence:
    return OutcomeIntelligence()


@pytest.fixture(scope="module")
def arch_engine() -> ArchitectureSynthesis:
    return ArchitectureSynthesis()


@pytest.fixture(scope="module")
def intent_engine() -> IntentEngine:
    return IntentEngine()


HEALTHCARE = "A HIPAA-compliant prior authorization platform for US providers and payers with AI-assisted review"


def _arch(arch_engine, intent_engine):
    d = intent_engine.decompose(HEALTHCARE)
    p = intent_engine.generate_master_prd(d)
    return arch_engine.synthesize(p)


class TestOutcomeIntelligence:
    def test_generates_cascade(self, oi, arch_engine, intent_engine):
        cascade = oi.generate_cascade(_arch(arch_engine, intent_engine))
        assert cascade["schema_version"] == "1.0.0"

    def test_cascade_has_5_levels(self, oi, arch_engine, intent_engine):
        cascade = oi.generate_cascade(_arch(arch_engine, intent_engine))
        assert len(cascade["cascade"]) == 5

    def test_has_measurement_gaps(self, oi, arch_engine, intent_engine):
        cascade = oi.generate_cascade(_arch(arch_engine, intent_engine))
        assert len(cascade["measurement_gaps"]) >= 1

    def test_suggest_updates_returns_empty(self, oi):
        result = oi.suggest_cascade_updates({})
        assert "suggested_new_outcomes" in result
