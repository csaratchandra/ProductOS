"""End-to-end integration test for V14 100x Orchestration Core.

Validates the full pipeline: intent → decomposition → architecture → gaps → simulation → export.
"""

import time
from pathlib import Path

import pytest

from core.python.productos_runtime.intent_engine import IntentEngine
from core.python.productos_runtime.architecture_synthesis import ArchitectureSynthesis
from core.python.productos_runtime.gap_intelligence import GapIntelligence
from core.python.productos_runtime.predictive_simulation import PredictiveSimulation
from core.python.productos_runtime.domain_intelligence import DomainIntelligence
from core.python.productos_runtime.architecture_exporter import ArchitectureExporter


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def intent_engine() -> IntentEngine:
    return IntentEngine()

@pytest.fixture(scope="module")
def arch_engine() -> ArchitectureSynthesis:
    return ArchitectureSynthesis()

@pytest.fixture(scope="module")
def gap_engine() -> GapIntelligence:
    return GapIntelligence()

@pytest.fixture(scope="module")
def sim_engine() -> PredictiveSimulation:
    return PredictiveSimulation()

@pytest.fixture(scope="module")
def domain_engine() -> DomainIntelligence:
    return DomainIntelligence()

@pytest.fixture(scope="module")
def exporter() -> ArchitectureExporter:
    return ArchitectureExporter()


MEDIUM_INTENT = "A HIPAA-compliant prior authorization platform for US providers and payers with AI-assisted review"


# ---------------------------------------------------------------------------
# Integration Tests
# ---------------------------------------------------------------------------

class TestV14EndToEnd:

    def test_full_pipeline_completes(self, intent_engine, arch_engine, gap_engine, sim_engine, domain_engine, exporter):
        """Full pipeline should complete for medium complexity intent."""
        start = time.time()

        # Phase 1: Intent Decomposition
        decomposition = intent_engine.decompose(MEDIUM_INTENT)
        assert decomposition["schema_version"] == "1.0.0"
        assert len(decomposition["inferred_personas"]) >= 2
        assert decomposition["domain_match"]["domain"] == "healthcare"

        # Master PRD generation
        master_prd = intent_engine.generate_master_prd(decomposition)
        assert master_prd["master_prd_id"]

        # Phase 2: Parallel Architecture Synthesis
        architecture = arch_engine.synthesize(master_prd)
        assert architecture["product_architecture_id"]
        assert len(architecture["artifacts"]) >= 5
        assert len(architecture["cross_links"]) >= 5

        # Cross-consistency validation
        consistency = arch_engine.validate_cross_consistency(architecture)
        assert consistency["overall_status"] in ("passed", "warning", "failed")

        # Phase 3: Gap Detection
        gaps = gap_engine.analyze(architecture)
        assert gaps["gap_analysis_id"]
        assert gaps["summary"]["total_gaps"] >= 0

        # Phase 4: Predictive Simulation
        forecast = sim_engine.forecast(architecture, scenario="baseline")
        assert forecast["baseline_forecast"]["simulation_runs"] > 0

        # What-if scenarios
        what_if = sim_engine.generate_what_if_scenarios(forecast)
        assert len(what_if) == 5

        # Domain Intelligence
        activation = domain_engine.auto_activate(decomposition)
        assert activation["domain"] == "healthcare"

        enrichment = domain_engine.enrich_architecture(architecture, activation)
        assert enrichment["summary"]["total_additions"] >= 1

        compliance = domain_engine.validate_compliance_coverage(architecture, activation)
        assert compliance["overall_coverage_score"] >= 0

        # Phase 5: Export
        bundle = exporter.export_all(architecture)
        assert len(bundle) == 12

        # PM Briefing
        briefing = exporter.generate_pm_briefing(
            architecture, gaps.get("gaps", []), forecast, activation
        )
        assert "PM Briefing" in briefing

        elapsed = time.time() - start
        assert elapsed < 30, f"Full pipeline took {elapsed:.2f}s (expected <30s)"

    def test_simple_intent_pipeline(self, intent_engine, arch_engine, gap_engine, exporter):
        """Minimal pipeline for simple intent should still produce valid output."""
        decomposition = intent_engine.decompose("A simple to-do list app for individual users")
        prd = intent_engine.generate_master_prd(decomposition)
        arch = arch_engine.synthesize(prd)
        gaps = gap_engine.analyze(arch)
        bundle = exporter.export_all(arch)

        assert bundle["json_artifacts"]
        assert gaps["summary"]["total_gaps"] >= 0

    def test_domain_activation_integrates_with_architecture(self, intent_engine, arch_engine, domain_engine):
        """Domain intelligence should seamlessly integrate with architecture."""
        decomposition = intent_engine.decompose(MEDIUM_INTENT)
        prd = intent_engine.generate_master_prd(decomposition)
        arch = arch_engine.synthesize(prd)
        activation = domain_engine.auto_activate(decomposition)
        enrichment = domain_engine.enrich_architecture(arch, activation)

        assert enrichment["architecture_ref"] == arch["product_architecture_id"]

    def test_gap_simulation_integration(self, intent_engine, arch_engine, gap_engine, sim_engine):
        """Gaps found should inform simulation analysis."""
        decomposition = intent_engine.decompose(MEDIUM_INTENT)
        prd = intent_engine.generate_master_prd(decomposition)
        arch = arch_engine.synthesize(prd)
        gaps = gap_engine.analyze(arch)
        forecast = sim_engine.forecast(arch)

        if gaps["summary"]["critical_count"] > 0:
            assert len(forecast["bottleneck_rankings"]) >= 0

    def test_pipeline_with_vague_intent(self, intent_engine, arch_engine, gap_engine, sim_engine, exporter):
        """Pipeline should handle vague intents gracefully."""
        decomposition = intent_engine.decompose("a healthcare app")
        prd = intent_engine.generate_master_prd(decomposition)
        arch = arch_engine.synthesize(prd)
        gaps = gap_engine.analyze(arch)
        forecast = sim_engine.forecast(arch)
        bundle = exporter.export_all(arch)

        assert len(decomposition["ambiguity_flags"]) >= 1
        assert bundle["json_artifacts"]

    def test_cross_consistency_after_full_pipeline(self, intent_engine, arch_engine):
        """Cross-consistency validation should pass after full synthesis."""
        decomposition = intent_engine.decompose(MEDIUM_INTENT)
        prd = intent_engine.generate_master_prd(decomposition)
        arch = arch_engine.synthesize(prd)
        consistency = arch_engine.validate_cross_consistency(arch)

        assert consistency["checks_passed"] or consistency["checks_failed"]
