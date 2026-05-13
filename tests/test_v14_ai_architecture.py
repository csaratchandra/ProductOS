"""Tests for V14 AI Architecture Planning."""

import pytest
from core.python.productos_runtime.ai_architecture import AIArchitecture
from core.python.productos_runtime.architecture_synthesis import ArchitectureSynthesis
from core.python.productos_runtime.intent_engine import IntentEngine


@pytest.fixture(scope="module")
def ai() -> AIArchitecture:
    return AIArchitecture()


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


class TestAIArchitecture:
    def test_plan_has_automation_candidates(self, ai, arch_engine, intent_engine):
        plan = ai.plan_ai_layer(_arch(arch_engine, intent_engine))
        assert len(plan["automation_candidates"]) >= 1

    def test_has_human_in_loop(self, ai, arch_engine, intent_engine):
        plan = ai.plan_ai_layer(_arch(arch_engine, intent_engine))
        assert len(plan["human_in_the_loop_checkpoints"]) >= 1

    def test_has_failure_modes(self, ai, arch_engine, intent_engine):
        plan = ai.plan_ai_layer(_arch(arch_engine, intent_engine))
        assert len(plan["failure_modes"]) >= 1

    def test_has_regulatory_alignment(self, ai, arch_engine, intent_engine):
        plan = ai.plan_ai_layer(_arch(arch_engine, intent_engine))
        assert len(plan["regulatory_alignment"]) >= 1

    def test_required_fields(self, ai, arch_engine, intent_engine):
        plan = ai.plan_ai_layer(_arch(arch_engine, intent_engine))
        assert plan["schema_version"] == "1.0.0"
        assert "ai_layer_plan_id" in plan
