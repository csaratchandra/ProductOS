"""Tests for V14 Predictive Analytics Engine."""

import pytest
from core.python.productos_runtime.predictive_analytics import PredictiveAnalytics
from core.python.productos_runtime.architecture_synthesis import ArchitectureSynthesis
from core.python.productos_runtime.intent_engine import IntentEngine


@pytest.fixture(scope="module")
def analytics() -> PredictiveAnalytics:
    return PredictiveAnalytics()


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


class TestPredictiveAnalytics:
    def test_auto_plan_generates_events(self, analytics, arch_engine, intent_engine):
        plan = analytics.auto_plan(_arch(arch_engine, intent_engine))
        assert len(plan["event_taxonomy"]) >= 2

    def test_has_metric_definitions(self, analytics, arch_engine, intent_engine):
        plan = analytics.auto_plan(_arch(arch_engine, intent_engine))
        assert len(plan["metric_definitions"]) >= 1

    def test_has_dashboard_specs(self, analytics, arch_engine, intent_engine):
        plan = analytics.auto_plan(_arch(arch_engine, intent_engine))
        assert len(plan["dashboard_specs"]) >= 1

    def test_privacy_assessment(self, analytics, arch_engine, intent_engine):
        plan = analytics.auto_plan(_arch(arch_engine, intent_engine))
        assert len(plan["privacy_risk_assessment"]) >= 1

    def test_events_have_privacy_classification(self, analytics, arch_engine, intent_engine):
        plan = analytics.auto_plan(_arch(arch_engine, intent_engine))
        for e in plan["event_taxonomy"]:
            assert e.get("privacy_classification") in ("pii", "phi", "financial", "behavioral", "technical", "none")
