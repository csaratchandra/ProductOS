"""Master end-to-end test for V14 full pipeline from intent to export."""

import time

import pytest

from core.python.productos_runtime.intent_engine import IntentEngine
from core.python.productos_runtime.architecture_synthesis import ArchitectureSynthesis
from core.python.productos_runtime.gap_intelligence import GapIntelligence
from core.python.productos_runtime.predictive_simulation import PredictiveSimulation
from core.python.productos_runtime.domain_intelligence import DomainIntelligence
from core.python.productos_runtime.architecture_exporter import ArchitectureExporter
from core.python.productos_runtime.predictive_analytics import PredictiveAnalytics
from core.python.productos_runtime.outcome_intelligence import OutcomeIntelligence
from core.python.productos_runtime.ai_architecture import AIArchitecture
from core.python.productos_runtime.experience_intelligence import ExperienceIntelligence
from core.python.productos_runtime.market_simulation import MarketSimulation


MEDIUM_INTENT = "A HIPAA-compliant prior authorization platform for US providers and payers with AI-assisted review"


class TestMasterEndToEnd:
    """Complete V14 pipeline — all modules working together."""

    @pytest.fixture(scope="class")
    def pipeline_result(self):
        start = time.time()
        result = {}

        ie = IntentEngine()
        ae = ArchitectureSynthesis()
        ge = GapIntelligence()
        se = PredictiveSimulation()
        di = DomainIntelligence()
        ex = ArchitectureExporter()
        pa = PredictiveAnalytics()
        oi = OutcomeIntelligence()
        ai = AIArchitecture()
        ei = ExperienceIntelligence()
        ms = MarketSimulation()

        decomp = ie.decompose(MEDIUM_INTENT)
        prd = ie.generate_master_prd(decomp)
        arch = ae.synthesize(prd)
        gaps = ge.analyze(arch)
        forecast = se.forecast(arch)
        activation = di.auto_activate(decomp)
        bundle = ex.export_all(arch)
        analytics_plan = pa.auto_plan(arch)
        cascade = oi.generate_cascade(arch)
        ai_plan = ai.plan_ai_layer(arch)
        exp_plan = ei.plan_experience(arch)
        market_sim = ms.simulate_with_market(arch, {})

        elapsed = time.time() - start

        result["elapsed"] = elapsed
        result["decomp"] = decomp
        result["prd"] = prd
        result["arch"] = arch
        result["gaps"] = gaps
        result["forecast"] = forecast
        result["activation"] = activation
        result["bundle_size"] = len(bundle)
        result["analytics_plan"] = analytics_plan
        result["cascade"] = cascade
        result["ai_plan"] = ai_plan
        result["exp_plan"] = exp_plan
        result["market_sim"] = market_sim
        return result

    def test_pipeline_completes_under_30s(self, pipeline_result):
        assert pipeline_result["elapsed"] < 30

    def test_intent_decomposition(self, pipeline_result):
        assert pipeline_result["decomp"]["domain_match"]["domain"] == "healthcare"

    def test_master_prd(self, pipeline_result):
        assert "master_prd_id" in pipeline_result["prd"]

    def test_architecture(self, pipeline_result):
        assert len(pipeline_result["arch"]["artifacts"]) >= 5

    def test_gaps(self, pipeline_result):
        assert pipeline_result["gaps"]["summary"]["total_gaps"] >= 0

    def test_forecast(self, pipeline_result):
        assert pipeline_result["forecast"]["baseline_forecast"]["simulation_runs"] > 0

    def test_domain_activation(self, pipeline_result):
        assert pipeline_result["activation"]["domain"] == "healthcare"

    def test_12_format_export(self, pipeline_result):
        assert pipeline_result["bundle_size"] == 12

    def test_analytics_plan(self, pipeline_result):
        assert len(pipeline_result["analytics_plan"]["event_taxonomy"]) >= 2

    def test_outcome_cascade(self, pipeline_result):
        assert len(pipeline_result["cascade"]["cascade"]) >= 3

    def test_ai_plan(self, pipeline_result):
        assert len(pipeline_result["ai_plan"]["automation_candidates"]) >= 1

    def test_experience_plan(self, pipeline_result):
        assert len(pipeline_result["exp_plan"]["per_persona_device_context"]) >= 1

    def test_market_simulation(self, pipeline_result):
        assert len(pipeline_result["market_sim"]["competitive_response"]) >= 1
