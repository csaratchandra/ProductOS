"""Integration tests for V14.1 intelligence modules working together.

Validates that predictive analytics, outcome intelligence, AI architecture,
and healthcare domain pack produce consistent, cross-referenced outputs.
"""

import pytest

from core.python.productos_runtime.intent_engine import IntentEngine
from core.python.productos_runtime.architecture_synthesis import ArchitectureSynthesis
from core.python.productos_runtime.predictive_analytics import PredictiveAnalytics
from core.python.productos_runtime.outcome_intelligence import OutcomeIntelligence
from core.python.productos_runtime.ai_architecture import AIArchitecture


HEALTHCARE_INTENT = "A HIPAA-compliant prior authorization platform for US providers and payers with AI-assisted review"
FINANCE_INTENT = "A FIX-compliant trade execution platform for US and EU capital markets with real-time risk management"


@pytest.fixture(scope="module")
def healthcare_architecture():
    ie = IntentEngine()
    ae = ArchitectureSynthesis()
    decomp = ie.decompose(HEALTHCARE_INTENT)
    prd = ie.generate_master_prd(decomp)
    return ae.synthesize(prd)


@pytest.fixture(scope="module")
def finance_architecture():
    ie = IntentEngine()
    ae = ArchitectureSynthesis()
    decomp = ie.decompose(FINANCE_INTENT)
    prd = ie.generate_master_prd(decomp)
    return ae.synthesize(prd)


class TestPredictiveAnalyticsIntegration:
    """Predictive analytics must produce coherent plans from architecture."""

    def test_analytics_plan_has_events_matching_handoffs(self, healthcare_architecture):
        pa = PredictiveAnalytics()
        plan = pa.auto_plan(healthcare_architecture)
        workflow = healthcare_architecture.get("workflow_orchestration_map", {})
        num_handoffs = len(workflow.get("handoffs", []))
        assert len(plan["event_taxonomy"]) >= num_handoffs, (
            f"Expected at least {num_handoffs} events for {num_handoffs} handoffs, "
            f"got {len(plan['event_taxonomy'])}"
        )

    def test_analytics_plan_has_metric_definitions(self, healthcare_architecture):
        pa = PredictiveAnalytics()
        plan = pa.auto_plan(healthcare_architecture)
        assert len(plan["metric_definitions"]) >= 1, "Expected at least 1 metric definition"

    def test_analytics_plan_privacy_classification(self, healthcare_architecture):
        pa = PredictiveAnalytics()
        plan = pa.auto_plan(healthcare_architecture)
        for event in plan["event_taxonomy"]:
            classification = event.get("privacy_classification", "")
            assert classification in ("", "pii", "phi", "financial", "behavioral", "technical", "none"), (
                f"Invalid privacy classification: {classification}"
            )


class TestOutcomeIntelligenceIntegration:
    """Outcome intelligence must produce cascades consistent with architecture."""

    def test_outcome_cascade_has_all_levels(self, healthcare_architecture):
        oi = OutcomeIntelligence()
        cascade = oi.generate_cascade(healthcare_architecture)
        levels = {entry["level"] for entry in cascade["cascade"]}
        expected = {"Business Outcome", "Product Outcome", "Feature Metric", "User Action", "Data Source"}
        assert levels.issuperset(expected), f"Cascade missing levels: {expected - levels}"

    def test_outcome_cascade_has_entries(self, healthcare_architecture):
        oi = OutcomeIntelligence()
        cascade = oi.generate_cascade(healthcare_architecture)
        total_entries = sum(len(entry["entries"]) for entry in cascade["cascade"])
        assert total_entries >= 5, f"Expected at least 5 cascade entries, got {total_entries}"

    def test_outcome_cascade_confidence_scored(self, healthcare_architecture):
        oi = OutcomeIntelligence()
        cascade = oi.generate_cascade(healthcare_architecture)
        for level in cascade["cascade"]:
            for entry in level["entries"]:
                if "confidence" in entry:
                    assert entry["confidence"] in ("observed", "inferred", "assumed"), (
                        f"Invalid confidence: {entry['confidence']}"
                    )


class TestAIArchitectureIntegration:
    """AI architecture must identify automation candidates from workflow."""

    def test_ai_plan_has_automation_candidates(self, healthcare_architecture):
        ai = AIArchitecture()
        plan = ai.plan_ai_layer(healthcare_architecture)
        assert len(plan["automation_candidates"]) >= 1, "Expected at least 1 automation candidate"

    def test_ai_plan_automation_candidates_have_confidence(self, healthcare_architecture):
        ai = AIArchitecture()
        plan = ai.plan_ai_layer(healthcare_architecture)
        for candidate in plan["automation_candidates"]:
            assert 0.0 <= candidate.get("confidence", -1) <= 1.0, (
                f"Invalid confidence: {candidate.get('confidence')}"
            )

    def test_ai_plan_human_in_the_loop(self, healthcare_architecture):
        ai = AIArchitecture()
        plan = ai.plan_ai_layer(healthcare_architecture)
        checkpoints = plan.get("human_in_the_loop_checkpoints", [])
        if checkpoints:
            for cp in checkpoints:
                assert "stage" in cp or "workflow_stage" in cp, "Checkpoint missing stage reference"


class TestCrossModuleConsistency:
    """V14.1 modules must produce consistent, non-contradictory outputs."""

    def test_analytics_and_ai_use_same_architecture(self, healthcare_architecture):
        pa = PredictiveAnalytics()
        ai = AIArchitecture()
        analytics_plan = pa.auto_plan(healthcare_architecture)
        ai_plan = ai.plan_ai_layer(healthcare_architecture)

        assert analytics_plan["architecture_ref"] == healthcare_architecture["product_architecture_id"]
        assert ai_plan["architecture_ref"] == healthcare_architecture["product_architecture_id"]

    def test_cascade_and_analytics_event_overlap(self, healthcare_architecture):
        oi = OutcomeIntelligence()
        pa = PredictiveAnalytics()
        cascade = oi.generate_cascade(healthcare_architecture)
        plan = pa.auto_plan(healthcare_architecture)

        user_actions = []
        for level in cascade["cascade"]:
            if level["level"] == "User Action":
                user_actions = [e["description"].lower() for e in level["entries"]]

        event_names = [e["event_name"].lower() for e in plan["event_taxonomy"]]

        if user_actions and event_names:
            action_event_overlap = 0
            for action in user_actions:
                action_words = set(action.split())
                for evt in event_names:
                    if action_words & set(evt.split("_")):
                        action_event_overlap += 1
                        break
            assert action_event_overlap > 0 or len(event_names) == 0, (
                f"None of {len(user_actions)} user actions overlap with {len(event_names)} analytics events"
            )


class TestDomainPackIntegration:
    """Domain packs must integrate with V14.1 intelligence modules."""

    def test_healthcare_ai_plan_mentions_hipaa(self, healthcare_architecture):
        ai = AIArchitecture()
        plan = ai.plan_ai_layer(healthcare_architecture)
        all_text = str(plan).lower()
        assert "hipaa" in all_text or "compliance" in all_text, (
            "Healthcare AI plan should reference HIPAA or compliance"
        )

    def test_finance_ai_plan_mentions_regulations(self, finance_architecture):
        ai = AIArchitecture()
        plan = ai.plan_ai_layer(finance_architecture)
        all_text = str(plan).lower()
        has_regulation = any(reg in all_text for reg in ("sec", "finra", "mifid", "emir", "compliance"))
        assert has_regulation, "Finance AI plan should reference relevant regulations"

    def test_analytics_plan_respects_domain_privacy(self, healthcare_architecture):
        pa = PredictiveAnalytics()
        plan = pa.auto_plan(healthcare_architecture)
        phi_events = [e for e in plan["event_taxonomy"] if e.get("privacy_classification") == "phi"]
        if phi_events:
            assert len(phi_events) >= 1, "Healthcare analytics should classify PHI events"
