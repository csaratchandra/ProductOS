"""Tests for V14 Market Simulation."""

import pytest
from core.python.productos_runtime.market_simulation import MarketSimulation
from core.python.productos_runtime.architecture_synthesis import ArchitectureSynthesis
from core.python.productos_runtime.intent_engine import IntentEngine


@pytest.fixture(scope="module")
def ms() -> MarketSimulation:
    return MarketSimulation()


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


class TestMarketSimulation:
    def test_competitive_response(self, ms, arch_engine, intent_engine):
        result = ms.simulate_with_market(_arch(arch_engine, intent_engine), {})
        assert len(result["competitive_response"]) >= 1
        assert "adoption_impact" in result["competitive_response"][0]

    def test_regulatory_timing(self, ms, arch_engine, intent_engine):
        result = ms.simulate_with_market(_arch(arch_engine, intent_engine), {})
        assert len(result["regulatory_timing"]) >= 1

    def test_risk_adjusted_roadmap(self, ms, arch_engine, intent_engine):
        result = ms.simulate_with_market(_arch(arch_engine, intent_engine), {})
        assert len(result["risk_adjusted_roadmap"]) >= 1
