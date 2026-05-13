"""Tests for V14 Experience Intelligence."""

import pytest
from core.python.productos_runtime.experience_intelligence import ExperienceIntelligence
from core.python.productos_runtime.architecture_synthesis import ArchitectureSynthesis
from core.python.productos_runtime.intent_engine import IntentEngine


@pytest.fixture(scope="module")
def ei() -> ExperienceIntelligence:
    return ExperienceIntelligence()


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


class TestExperienceIntelligence:
    def test_device_context_per_persona(self, ei, arch_engine, intent_engine):
        plan = ei.plan_experience(_arch(arch_engine, intent_engine))
        assert len(plan["per_persona_device_context"]) >= 1

    def test_performance_targets(self, ei, arch_engine, intent_engine):
        plan = ei.plan_experience(_arch(arch_engine, intent_engine))
        assert len(plan["performance_targets"]) >= 1

    def test_cognitive_load_analysis(self, ei, arch_engine, intent_engine):
        plan = ei.plan_experience(_arch(arch_engine, intent_engine))
        assert len(plan["cognitive_load_analysis"]) >= 1
