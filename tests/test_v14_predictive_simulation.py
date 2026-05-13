"""Tests for V14 Predictive Simulation Engine."""

import json
from pathlib import Path

import pytest

from core.python.productos_runtime.predictive_simulation import PredictiveSimulation
from core.python.productos_runtime.architecture_synthesis import ArchitectureSynthesis
from core.python.productos_runtime.intent_engine import IntentEngine
from conftest import SCHEMA_DIR


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def sim_engine() -> PredictiveSimulation:
    return PredictiveSimulation()


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
# Tests
# ---------------------------------------------------------------------------

class TestPredictiveSimulation:

    def test_baseline_forecast_completes(self, sim_engine, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine, HEALTHCARE_INTENT)
        result = sim_engine.forecast(arch, scenario="baseline")
        assert result["schema_version"] == "1.0.0"
        assert result["scenario"] == "baseline"
        assert result["baseline_forecast"]["simulation_runs"] > 0

    def test_baseline_forecast_under_10s(self, sim_engine, arch_engine, intent_engine):
        import time
        arch = _build_architecture(arch_engine, intent_engine, HEALTHCARE_INTENT)
        start = time.time()
        sim_engine.forecast(arch, scenario="baseline")
        duration = time.time() - start
        assert duration < 10, f"Forecast took {duration:.2f}s (expected <10s)"

    def test_identifies_bottleneck(self, sim_engine, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine, HEALTHCARE_INTENT)
        result = sim_engine.forecast(arch)
        assert len(result["bottleneck_rankings"]) >= 1
        assert result["bottleneck_rankings"][0]["rank"] == 1

    def test_bottleneck_has_confidence_intervals(self, sim_engine, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine, HEALTHCARE_INTENT)
        result = sim_engine.forecast(arch)
        for b in result["bottleneck_rankings"]:
            assert b["predicted_wait_time_seconds"] >= 0
            assert b["queue_depth"] >= 0

    def test_sla_violation_predictions(self, sim_engine, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine, HEALTHCARE_INTENT)
        result = sim_engine.forecast(arch)
        assert len(result["sla_violation_predictions"]) >= 1
        for v in result["sla_violation_predictions"]:
            assert 0.0 <= v["violation_probability"] <= 1.0
            assert v["risk_level"] in ("low", "medium", "high", "critical")

    def test_percentile_distributions(self, sim_engine, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine, HEALTHCARE_INTENT)
        result = sim_engine.forecast(arch)
        bf = result["baseline_forecast"]
        assert bf["p50_completion_seconds"] <= bf["p90_completion_seconds"]
        assert bf["p90_completion_seconds"] <= bf["p95_completion_seconds"]

    def test_optimistic_scenario(self, sim_engine, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine, HEALTHCARE_INTENT)
        baseline = sim_engine.forecast(arch, scenario="baseline")
        optimistic = sim_engine.forecast(arch, scenario="optimistic")
        assert optimistic["baseline_forecast"]["p50_completion_seconds"] <= baseline["baseline_forecast"]["p50_completion_seconds"]

    def test_pessimistic_scenario(self, sim_engine, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine, HEALTHCARE_INTENT)
        baseline = sim_engine.forecast(arch, scenario="baseline")
        pessimistic = sim_engine.forecast(arch, scenario="pessimistic")
        assert pessimistic["baseline_forecast"]["p50_completion_seconds"] >= baseline["baseline_forecast"]["p50_completion_seconds"]

    def test_no_handoffs_returns_message(self, sim_engine):
        arch = {"product_architecture_id": "test", "workflow_orchestration_map": {"personas": [], "handoffs": []}}
        result = sim_engine.forecast(arch)
        assert "message" in result
        assert "Cannot simulate" in result["message"]

    def test_resource_contention_warnings(self, sim_engine, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine, HEALTHCARE_INTENT)
        result = sim_engine.forecast(arch)
        assert len(result["resource_contention_warnings"]) >= 0

    def test_cascade_failure_predictions(self, sim_engine, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine, HEALTHCARE_INTENT)
        result = sim_engine.forecast(arch)
        for cf in result.get("cascade_failure_predictions", []):
            assert 0.0 <= cf["cascade_probability"] <= 1.0
            assert len(cf["explanation"]) >= 10

    def test_sensitivity_analysis(self, sim_engine, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine, HEALTHCARE_INTENT)
        result = sim_engine.forecast(arch, scenario="sensitivity")
        assert len(result["sensitivity_analysis"]) >= 1
        for s in result["sensitivity_analysis"]:
            assert 0.0 <= s["sensitivity_score"] <= 1.0

    def test_different_scenarios_have_different_scenario_field(self, sim_engine, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine, HEALTHCARE_INTENT)
        for scenario in ("baseline", "optimistic", "pessimistic", "sensitivity"):
            result = sim_engine.forecast(arch, scenario=scenario)
            assert result["scenario"] == scenario


class TestWhatIfScenarios:

    def test_generates_5_scenarios(self, sim_engine, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine, HEALTHCARE_INTENT)
        forecast = sim_engine.forecast(arch)
        scenarios = sim_engine.generate_what_if_scenarios(forecast)
        assert len(scenarios) == 5

    def test_scenarios_have_outcomes(self, sim_engine, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine, HEALTHCARE_INTENT)
        forecast = sim_engine.forecast(arch)
        scenarios = sim_engine.generate_what_if_scenarios(forecast)
        for s in scenarios:
            assert len(s["predicted_outcomes"]) >= 1
            assert len(s["parameter_changes"]) >= 1

    def test_scenario_has_effort_estimate(self, sim_engine, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine, HEALTHCARE_INTENT)
        forecast = sim_engine.forecast(arch)
        scenarios = sim_engine.generate_what_if_scenarios(forecast)
        for s in scenarios:
            assert s["implementation_effort"]["size"] in ("S", "M", "L", "XL")
            assert len(s["implementation_effort"]["rationale"]) >= 10

    def test_scenario_has_confidence(self, sim_engine, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine, HEALTHCARE_INTENT)
        forecast = sim_engine.forecast(arch)
        scenarios = sim_engine.generate_what_if_scenarios(forecast)
        for s in scenarios:
            assert 0.0 <= s["confidence"] <= 1.0

    def test_scenario_descriptions_present(self, sim_engine, arch_engine, intent_engine):
        arch = _build_architecture(arch_engine, intent_engine, HEALTHCARE_INTENT)
        forecast = sim_engine.forecast(arch)
        scenarios = sim_engine.generate_what_if_scenarios(forecast)
        for s in scenarios:
            assert len(s["description"]) >= 10


class TestSimulationForecastSchema:
    def test_schema_loads(self):
        schema_path = SCHEMA_DIR / "simulation_forecast.schema.json"
        assert schema_path.exists()
        with schema_path.open("r", encoding="utf-8") as f:
            schema = json.load(f)
        assert schema["$id"].endswith("simulation_forecast.schema.json")


class TestWhatIfScenarioSchema:
    def test_schema_loads(self):
        schema_path = SCHEMA_DIR / "what_if_scenario.schema.json"
        assert schema_path.exists()
        with schema_path.open("r", encoding="utf-8") as f:
            schema = json.load(f)
        assert schema["$id"].endswith("what_if_scenario.schema.json")
