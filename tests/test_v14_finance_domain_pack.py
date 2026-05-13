"""Tests for V14 Finance Domain Pack."""

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FINANCE_DIR = ROOT / "core" / "domains" / "finance"


class TestFinanceDomainPack:
    def test_pack_structure_exists(self):
        assert (FINANCE_DIR / "README.md").exists()
        assert (FINANCE_DIR / "base.schema.overlay.json").exists()
        assert (FINANCE_DIR / "regions" / "us.schema.overlay.json").exists()
        assert (FINANCE_DIR / "regions" / "eu.schema.overlay.json").exists()

    def test_base_overlay_has_iso_refs(self):
        with (FINANCE_DIR / "base.schema.overlay.json").open() as f:
            data = json.load(f)
        assert "ISO 20022" in data["base_refs"]

    def test_us_overlay_has_sec_regulation(self):
        with (FINANCE_DIR / "regions" / "us.schema.overlay.json").open() as f:
            data = json.load(f)
        assert "SEC" in data["regulations"]

    def test_eu_overlay_has_mifid(self):
        with (FINANCE_DIR / "regions" / "eu.schema.overlay.json").open() as f:
            data = json.load(f)
        assert "MiFID II" in data["regulations"]

    def test_trade_execution_workflow_has_fix(self):
        with (FINANCE_DIR / "workflows" / "trade_execution.workflow.json").open() as f:
            data = json.load(f)
        assert data["protocol"].startswith("FIX")

    def test_sub_packs_have_refs(self):
        for sp in ["capital_markets", "banking"]:
            path = FINANCE_DIR / "sub-packs" / f"{sp}.manifest.json"
            with path.open() as f:
                data = json.load(f)
            assert len(data["refs"]) >= 1
