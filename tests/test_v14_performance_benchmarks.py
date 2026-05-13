"""Performance benchmarks for V14 100x pipeline.

Validates that pipeline phases complete within expected time windows
for medium complexity architectures.
"""

import time

import pytest

from core.python.productos_runtime.intent_engine import IntentEngine
from core.python.productos_runtime.architecture_synthesis import ArchitectureSynthesis
from core.python.productos_runtime.gap_intelligence import GapIntelligence
from core.python.productos_runtime.predictive_simulation import PredictiveSimulation
from core.python.productos_runtime.domain_intelligence import DomainIntelligence
from core.python.productos_runtime.architecture_exporter import ArchitectureExporter


MEDIUM_INTENT = "A HIPAA-compliant prior authorization platform for US providers and payers with AI-assisted review"
COMPLEX_INTENT = (
    "A cross-border payment platform for EU and US businesses with real-time FX conversion, "
    "AML/KYC compliance, multi-currency wallets, and automated reconciliation for enterprise customers"
)


class TestV14PhaseBenchmarks:
    """Individual phase timing benchmarks."""

    @pytest.fixture(scope="class")
    def engines(self):
        return {
            "intent": IntentEngine(),
            "arch": ArchitectureSynthesis(),
            "gap": GapIntelligence(),
            "sim": PredictiveSimulation(),
            "domain": DomainIntelligence(),
            "exporter": ArchitectureExporter(),
        }

    def test_intent_decomposition_under_3s(self, engines):
        start = time.perf_counter()
        decomp = engines["intent"].decompose(MEDIUM_INTENT)
        elapsed = time.perf_counter() - start
        assert elapsed < 3.0, f"Intent decomposition took {elapsed:.2f}s (expected <3s)"
        assert decomp["schema_version"] == "1.0.0"

    def test_master_prd_generation_under_1s(self, engines):
        decomp = engines["intent"].decompose(MEDIUM_INTENT)
        start = time.perf_counter()
        prd = engines["intent"].generate_master_prd(decomp)
        elapsed = time.perf_counter() - start
        assert elapsed < 1.0, f"Master PRD generation took {elapsed:.2f}s (expected <1s)"
        assert prd["master_prd_id"]

    def test_architecture_synthesis_under_15s(self, engines):
        decomp = engines["intent"].decompose(MEDIUM_INTENT)
        prd = engines["intent"].generate_master_prd(decomp)
        start = time.perf_counter()
        arch = engines["arch"].synthesize(prd)
        elapsed = time.perf_counter() - start
        assert elapsed < 15.0, f"Architecture synthesis took {elapsed:.2f}s (expected <15s)"
        assert len(arch["artifacts"]) >= 5

    def test_cross_consistency_validation_under_3s(self, engines):
        decomp = engines["intent"].decompose(MEDIUM_INTENT)
        prd = engines["intent"].generate_master_prd(decomp)
        arch = engines["arch"].synthesize(prd)
        start = time.perf_counter()
        engines["arch"].validate_cross_consistency(arch)
        elapsed = time.perf_counter() - start
        assert elapsed < 3.0, f"Cross-consistency took {elapsed:.2f}s (expected <3s)"

    def test_gap_analysis_under_3s(self, engines):
        decomp = engines["intent"].decompose(MEDIUM_INTENT)
        prd = engines["intent"].generate_master_prd(decomp)
        arch = engines["arch"].synthesize(prd)
        start = time.perf_counter()
        engines["gap"].analyze(arch)
        elapsed = time.perf_counter() - start
        assert elapsed < 3.0, f"Gap analysis took {elapsed:.2f}s (expected <3s)"

    def test_predictive_simulation_under_10s(self, engines):
        decomp = engines["intent"].decompose(MEDIUM_INTENT)
        prd = engines["intent"].generate_master_prd(decomp)
        arch = engines["arch"].synthesize(prd)
        start = time.perf_counter()
        forecast = engines["sim"].forecast(arch, scenario="baseline")
        elapsed = time.perf_counter() - start
        assert elapsed < 10.0, f"Predictive simulation took {elapsed:.2f}s (expected <10s)"
        assert forecast["baseline_forecast"]["simulation_runs"] > 0

    def test_full_pipeline_medium_complexity_under_30s(self, engines):
        start = time.perf_counter()

        decomp = engines["intent"].decompose(MEDIUM_INTENT)
        prd = engines["intent"].generate_master_prd(decomp)
        arch = engines["arch"].synthesize(prd)
        engines["arch"].validate_cross_consistency(arch)
        engines["gap"].analyze(arch)
        forecast = engines["sim"].forecast(arch, scenario="baseline")
        engines["sim"].generate_what_if_scenarios(forecast)
        activation = engines["domain"].auto_activate(decomp)
        engines["domain"].enrich_architecture(arch, activation)
        engines["domain"].validate_compliance_coverage(arch, activation)
        bundle = engines["exporter"].export_all(arch)

        elapsed = time.perf_counter() - start
        assert elapsed < 30.0, f"Full pipeline took {elapsed:.2f}s (expected <30s)"
        assert len(bundle) == 12

    def test_complex_intent_pipeline_under_45s(self, engines):
        start = time.perf_counter()

        decomp = engines["intent"].decompose(COMPLEX_INTENT)
        prd = engines["intent"].generate_master_prd(decomp)
        arch = engines["arch"].synthesize(prd)
        engines["arch"].validate_cross_consistency(arch)
        engines["gap"].analyze(arch)
        bundle = engines["exporter"].export_all(arch)

        elapsed = time.perf_counter() - start
        assert elapsed < 45.0, f"Complex pipeline took {elapsed:.2f}s (expected <45s)"
        assert len(bundle) == 12

    def test_export_12_formats_under_5s(self, engines):
        decomp = engines["intent"].decompose(MEDIUM_INTENT)
        prd = engines["intent"].generate_master_prd(decomp)
        arch = engines["arch"].synthesize(prd)
        start = time.perf_counter()
        bundle = engines["exporter"].export_all(arch)
        elapsed = time.perf_counter() - start
        assert elapsed < 5.0, f"Export took {elapsed:.2f}s (expected <5s)"
        assert len(bundle) == 12
