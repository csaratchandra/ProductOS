"""Tests for V14 Healthcare Domain Pack."""

import json
from pathlib import Path

import pytest

from core.python.productos_runtime.intent_engine import IntentEngine


ROOT = Path(__file__).resolve().parents[1]
HEALTHCARE_DIR = ROOT / "core" / "domains" / "healthcare"


class TestHealthcareDomainPack:
    def test_pack_structure_exists(self):
        assert (HEALTHCARE_DIR / "README.md").exists()
        assert (HEALTHCARE_DIR / "base.schema.overlay.json").exists()
        assert (HEALTHCARE_DIR / "regions" / "us.schema.overlay.json").exists()
        assert (HEALTHCARE_DIR / "workflows" / "prior_authorization.workflow.json").exists()
        assert (HEALTHCARE_DIR / "sub-packs" / "provider.manifest.json").exists()
        assert (HEALTHCARE_DIR / "sub-packs" / "payer.manifest.json").exists()

    def test_base_overlay_has_fhir_resources(self):
        with (HEALTHCARE_DIR / "base.schema.overlay.json").open() as f:
            data = json.load(f)
        assert "FHIR R4" in data["base_refs"]
        assert len(data["core_resources"]) >= 5

    def test_us_overlay_has_hipaa_compliance(self):
        with (HEALTHCARE_DIR / "regions" / "us.schema.overlay.json").open() as f:
            data = json.load(f)
        assert "HIPAA" in data["regulations"]
        assert len(data["compliance_requirements"]) >= 5

    def test_prior_auth_workflow_has_cms_sla(self):
        with (HEALTHCARE_DIR / "workflows" / "prior_authorization.workflow.json").open() as f:
            data = json.load(f)
        assert data["sla_hours"] == 72
        assert data["regulation"] == "CMS"

    def test_sub_packs_have_refs(self):
        for sp in ["provider", "payer"]:
            path = HEALTHCARE_DIR / "sub-packs" / f"{sp}.manifest.json"
            with path.open() as f:
                data = json.load(f)
            assert len(data["refs"]) >= 1

    def test_intent_detects_healthcare(self):
        engine = IntentEngine()
        result = engine.decompose("HIPAA-compliant prior authorization for providers and payers")
        assert result["domain_match"]["domain"] == "healthcare"
        assert result["domain_match"]["confidence"] >= 0.5
