"""Cross-pack integration tests — healthcare + finance domain packs coexisting."""

from pathlib import Path

import pytest

from core.python.productos_runtime.intent_engine import IntentEngine
from core.python.productos_runtime.domain_intelligence import DomainIntelligence


class TestCrossPackIntegration:
    def test_healthcare_detection(self):
        engine = IntentEngine()
        result = engine.decompose("A HIPAA-compliant prior authorization platform for US providers and payers")
        assert result["domain_match"]["domain"] == "healthcare"

    def test_finance_detection(self):
        engine = IntentEngine()
        result = engine.decompose("A FIX-compliant trade execution platform for US capital markets")
        assert result["domain_match"]["domain"] == "finance"

    def test_domain_intelligence_healthcare(self):
        di = DomainIntelligence()
        engine = IntentEngine()
        decomp = engine.decompose("A HIPAA-compliant prior authorization platform")
        activation = di.auto_activate(decomp)
        assert activation["domain"] == "healthcare"

    def test_domain_intelligence_finance(self):
        di = DomainIntelligence()
        engine = IntentEngine()
        decomp = engine.decompose("A trade execution and risk management platform for capital markets with SEC compliance")
        activation = di.auto_activate(decomp)
        assert activation["domain"] == "finance"

    def test_both_pack_dirs_exist(self):
        root = Path(__file__).resolve().parents[1]
        assert (root / "core" / "domains" / "healthcare").exists()
        assert (root / "core" / "domains" / "finance").exists()
