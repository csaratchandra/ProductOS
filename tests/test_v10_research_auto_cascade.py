"""Tests for ProductOS V11 Research Auto-Cascade."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.python.productos_runtime.living_system import (
    build_regeneration_queue,
    generate_impact_propagation_map,
)


class TestResearchAutoCascade:
    """Test that competitive research changes auto-cascade to downstream artifacts."""

    def test_competitor_dossier_change_queues_strategy_brief(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        artifacts_dir = workspace_dir / "artifacts"
        artifacts_dir.mkdir(parents=True)

        # Create competitor dossier (source)
        competitor_dossier = {
            "schema_version": "1.0.0",
            "competitor_id": "comp_001",
            "title": "CompetitorAlpha Dossier",
            "source_artifact_ids": ["artifacts/external_research_review.json"],
        }
        with (artifacts_dir / "competitor_dossier.json").open("w") as f:
            json.dump(competitor_dossier, f)

        # Create strategy brief (downstream)
        strategy_brief = {
            "schema_version": "1.0.0",
            "strategy_context_brief_id": "strat_001",
            "title": "Strategy Brief",
            "source_artifact_ids": ["artifacts/competitor_dossier.json"],
        }
        with (artifacts_dir / "strategy_context_brief.json").open("w") as f:
            json.dump(strategy_brief, f)

        # Auto-generate and save impact propagation map
        impact_map = generate_impact_propagation_map(workspace_dir)
        assert "artifacts/competitor_dossier.json" in impact_map["dependencies"]
        assert any("strategy_context_brief" in ref for ref in impact_map["dependencies"]["artifacts/competitor_dossier.json"])

        with (artifacts_dir / "impact_propagation_map.json").open("w") as f:
            json.dump(impact_map, f)

        # Trigger: competitor dossier updated
        trigger = {
            "event_type": "competitive_alert",
            "source_artifact_ref": "artifacts/competitor_dossier.json",
            "change_summary": "CompetitorAlpha launched new pricing strategy",
        }

        queue = build_regeneration_queue(trigger, workspace_dir, generated_at="2026-05-06T12:00:00Z")

        assert queue["status"] == "active"
        assert len(queue["queued_items"]) >= 1
        target_refs = [item["target_artifact_ref"] for item in queue["queued_items"]]
        assert any("strategy_context_brief" in ref for ref in target_refs)

    def test_customer_pulse_change_queues_persona(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        artifacts_dir = workspace_dir / "artifacts"
        artifacts_dir.mkdir(parents=True)

        # Create customer pulse
        customer_pulse = {
            "schema_version": "1.0.0",
            "pulse_id": "pulse_001",
            "title": "Customer Pulse Q2",
            "findings": ["Users want mobile checkout"],
        }
        with (artifacts_dir / "customer_pulse.json").open("w") as f:
            json.dump(customer_pulse, f)

        # Create persona narrative (downstream from pulse via evidence_refs)
        persona = {
            "schema_version": "1.0.0",
            "persona_pack_id": "pers_001",
            "title": "Mobile Shopper",
            "evidence_refs": ["artifacts/customer_pulse.json"],
        }
        with (artifacts_dir / "persona_narrative_card.json").open("w") as f:
            json.dump(persona, f)

        # Create journey map (downstream from persona)
        journey = {
            "schema_version": "1.0.0",
            "customer_journey_map_id": "cjm_001",
            "title": "Checkout Journey",
            "source_artifact_ids": ["artifacts/persona_narrative_card.json"],
        }
        with (artifacts_dir / "customer_journey_map.json").open("w") as f:
            json.dump(journey, f)

        # Save impact propagation map
        impact_map = generate_impact_propagation_map(workspace_dir)
        with (artifacts_dir / "impact_propagation_map.json").open("w") as f:
            json.dump(impact_map, f)

        trigger = {
            "event_type": "research_fresh",
            "source_artifact_ref": "artifacts/customer_pulse.json",
            "change_summary": "customer pulse updated with new mobile checkout pain point",
        }

        queue = build_regeneration_queue(trigger, workspace_dir, generated_at="2026-05-06T12:00:00Z")

        target_refs = [item["target_artifact_ref"] for item in queue["queued_items"]]
        # Persona should be queued as direct downstream from pulse
        assert any("persona_narrative_card" in ref for ref in target_refs)

    def test_high_severity_shift_always_pm_review(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        artifacts_dir = workspace_dir / "artifacts"
        artifacts_dir.mkdir(parents=True)

        # Create PRD (critical artifact)
        prd = {
            "schema_version": "1.0.0",
            "prd_id": "prd_001",
            "title": "Product Requirements",
            "dependencies": ["artifacts/competitor_dossier.json"],
        }
        with (artifacts_dir / "prd.json").open("w") as f:
            json.dump(prd, f)

        # Save impact propagation map
        impact_map = generate_impact_propagation_map(workspace_dir)
        with (artifacts_dir / "impact_propagation_map.json").open("w") as f:
            json.dump(impact_map, f)

        trigger = {
            "event_type": "competitive_alert",
            "source_artifact_ref": "artifacts/competitor_dossier.json",
            "change_summary": "competitor launched feature parity with our core differentiator",
        }

        queue = build_regeneration_queue(trigger, workspace_dir, generated_at="2026-05-06T12:00:00Z")

        for item in queue["queued_items"]:
            if "prd" in item["target_artifact_ref"]:
                assert item["regeneration_mode"] == "pm_review"

    def test_mechanical_change_auto_executes_without_pm(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        artifacts_dir = workspace_dir / "artifacts"
        artifacts_dir.mkdir(parents=True)

        artifact = {
            "schema_version": "1.0.0",
            "artifact_id": "art_001",
            "title": "Reference Doc",
            "version": 1,
            "updated_at": "old",
            "dependencies": [],
        }
        with (artifacts_dir / "reference.json").open("w") as f:
            json.dump(artifact, f)

        trigger = {
            "event_type": "artifact_updated",
            "source_artifact_ref": "artifacts/reference.json",
            "change_summary": "version bump and date stamp updated",
        }

        queue = build_regeneration_queue(trigger, workspace_dir, generated_at="2026-05-06T12:00:00Z")

        for item in queue["queued_items"]:
            assert item["impact_classification"] == "mechanical"
            assert item["regeneration_mode"] == "auto"

    def test_circular_dependency_detected_and_blocked(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        artifacts_dir = workspace_dir / "artifacts"
        artifacts_dir.mkdir(parents=True)

        a = {"schema_version": "1.0.0", "artifact_id": "a", "title": "A", "dependencies": ["artifacts/b.json"]}
        b = {"schema_version": "1.0.0", "artifact_id": "b", "title": "B", "dependencies": ["artifacts/c.json"]}
        c = {"schema_version": "1.0.0", "artifact_id": "c", "title": "C", "dependencies": ["artifacts/a.json"]}

        for name, data in [("a.json", a), ("b.json", b), ("c.json", c)]:
            with (artifacts_dir / name).open("w") as f:
                json.dump(data, f)

        deps = ["artifacts/a.json", "artifacts/b.json", "artifacts/c.json"]
        from core.python.productos_runtime.living_system import detect_circular_dependencies

        circular = detect_circular_dependencies(deps, workspace_dir)
        assert circular is not None
        assert len(circular) >= 2
