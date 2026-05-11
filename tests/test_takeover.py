from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from core.python.productos_runtime.takeover import (
    build_takeover_brief,
    build_problem_space_map,
    build_roadmap_recovery_brief,
    build_visual_product_atlas,
    build_takeover_feature_scorecard,
    build_takeover_cockpit_section,
    build_takeover_bundle,
    ingest_screenshots,
    render_takeover_atlas_html,
    TAKEOVER_ARTIFACT_SCHEMAS,
)


def _run_cli(root_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/productos.py", *args],
        cwd=root_dir,
        capture_output=True,
        text=True,
        check=False,
    )


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _validator_for(schema_name: str, root_dir: Path) -> Draft202012Validator:
    schema = _load_json(root_dir / "core" / "schemas" / "artifacts" / schema_name)
    return Draft202012Validator(schema)


def _create_minimal_workspace(tmp_path: Path, workspace_id: str) -> Path:
    ws = tmp_path / workspace_id
    ws.mkdir(parents=True)
    (ws / "artifacts").mkdir(parents=True)
    (ws / "inbox").mkdir()
    (ws / "inbox" / "raw-notes").mkdir()
    (ws / "inbox" / "screenshots").mkdir()
    (ws / "docs").mkdir()
    (ws / "docs" / "planning").mkdir()
    (ws / "outputs").mkdir()

    manifest = {
        "schema_version": "1.0.0",
        "workspace_id": workspace_id,
        "name": "Test Workspace",
        "mode": "research",
        "artifact_paths": [],
        "workflow_paths": [],
    }
    with open(ws / "workspace_manifest.yaml", "w") as f:
        yaml.dump(manifest, f, default_flow_style=False)
    return ws


def _add_problem_brief(ws: Path, workspace_id: str) -> dict:
    pb = {
        "schema_version": "1.1.0",
        "problem_brief_id": f"problem_brief_{workspace_id}",
        "workspace_id": workspace_id,
        "title": f"Test Problem: {workspace_id}",
        "problem_summary": "PMs cannot quickly understand inherited products due to scattered evidence and opaque roadmap reasoning.",
        "strategic_fit_summary": "Takeover superpower fits challenger posture by making ProductOS the first thing a new PM runs.",
        "posture_alignment": "challenger",
        "why_this_problem_now": "New PMs waste weeks reconstructing context when inheriting products.",
        "why_this_problem_for_this_segment": "B2B product teams frequently rotate PMs across products.",
        "problem_severity": {"customer_pain": "high", "workflow_frequency": "high", "evidence_strength": "moderate", "severity_rationale": "Context reconstruction is a recurring pain for inheriting PMs."},
        "target_segment_refs": [{"entity_type": "segment", "entity_id": "segment_b2b_product_teams"}],
        "target_persona_refs": [{"entity_type": "persona", "entity_id": "persona_incoming_pm"}],
        "linked_entity_refs": [{"entity_type": "problem", "entity_id": "problem_context_reconstruction"}],
        "evidence_refs": [{"source_type": "other", "source_id": "inbox/raw-notes/pm-interview.md", "justification": "PM interviews confirm context reconstruction takes 2-4 weeks."}],
        "upstream_artifact_ids": ["mission_brief_test"],
        "canonical_persona_archetype_pack_id": "persona_archetype_pack_test",
        "artifact_trace_map_id": "trace_map_test",
        "ralph_status": "decision_ready",
        "prioritization": {"lane": "must_now", "priority_score": 90, "confidence": "high", "agentic_delivery_burden": "medium", "priority_rationale": "Takeover is the core superpower for this slice.", "reviewer_handoff": "PM should validate evidence gaps."},
        "handoff_readiness_summary": "Problem brief is ready for takeover orchestration.",
        "recommended_next_step": "prd",
        "created_at": "2026-05-12T08:00:00Z",
    }
    _load_json.__dict__["_cache"] = {}
    with open(ws / "artifacts" / "problem_brief.json", "w") as f:
        json.dump(pb, f, indent=2)
    return pb


def _add_competitor_dossier(ws: Path, workspace_id: str) -> dict:
    cd = {
        "schema_version": "1.1.0",
        "competitor_dossier_id": f"competitor_dossier_{workspace_id}",
        "workspace_id": workspace_id,
        "title": "Competitor Dossier",
        "competitive_frame": "PM operating systems for product inheritance and discovery.",
        "comparison_basis": "Compared on takeover readiness and evidence traceability.",
        "framework_registry_ref": "framework_registry_test",
        "selected_framework_ids": ["competitive_displacement_map"],
        "target_segment_refs": [{"entity_type": "segment", "entity_id": "segment_b2b_product_teams"}],
        "target_persona_refs": [{"entity_type": "persona", "entity_id": "persona_incoming_pm"}],
        "linked_entity_refs": [],
        "source_artifact_ids": [],
        "status_quo_alternatives": ["Manual context reconstruction", "Scattered docs and notes"],
        "internal_build_risk": "medium",
        "competitive_landscape_status": "named_competitor_set",
        "evidence_coverage_status": "triangulated_external",
        "dossier_quality": "decision_ready",
        "named_competitor_count": 2,
        "where_we_win": ["Structured artifact model", "Evidence traceability"],
        "where_we_lose": ["Brand recognition", "User base size"],
        "credible_wedge_for_posture": "PM-specific takeover flow with evidence traceability.",
        "required_proof_to_displace": "End-to-end takeover demo with real workspace import.",
        "prioritization_implications": "Focus on takeover orchestration before expanding features.",
        "competitors": [
            {"name": "Competitor A", "category": "indirect", "threat_level": "medium", "wedge_advantage": "Existing user base"},
            {"name": "Competitor B", "category": "direct", "threat_level": "low", "wedge_advantage": "None in takeover"},
        ],
        "created_at": "2026-05-12T08:00:00Z",
    }
    with open(ws / "artifacts" / "competitor_dossier.json", "w") as f:
        json.dump(cd, f, indent=2)
    return cd


def _add_journey_map(ws: Path, workspace_id: str) -> dict:
    jm = {
        "schema_version": "1.0.0",
        "customer_journey_map_id": f"customer_journey_map_{workspace_id}",
        "workspace_id": workspace_id,
        "title": "Customer Journey Map",
        "target_segment_ref": {"entity_type": "segment", "entity_id": "segment_b2b_product_teams"},
        "target_persona_refs": [{"entity_type": "persona", "entity_id": "persona_incoming_pm"}],
        "journey_stages": [
            {"stage_id": "stage_unaware", "stage_name": "Unaware", "description": "PM is unaware of structured takeover tools.", "emotion_score": 3},
            {"stage_id": "stage_research", "stage_name": "Research", "description": "PM researches options for product inheritance.", "emotion_score": 4},
            {"stage_id": "stage_evaluation", "stage_name": "Evaluation", "description": "PM evaluates ProductOS for takeover needs.", "emotion_score": 5},
        ],
        "overall_emotion_curve": [{"stage": "Unaware", "score": 3}, {"stage": "Research", "score": 4}, {"stage": "Evaluation", "score": 5}],
        "moments_of_truth": [{"stage": "Evaluation", "description": "First takeover atlas render convinces PM."}],
        "gap_analysis": "Journey coverage is partial; more stages needed.",
        "opportunities": [{"description": "Build end-to-end takeover demo flow."}],
        "generated_at": "2026-05-12T08:00:00Z",
    }
    with open(ws / "artifacts" / "customer_journey_map.json", "w") as f:
        json.dump(jm, f, indent=2)
    return jm


def _add_persona_pack(ws: Path, workspace_id: str) -> dict:
    pp = {
        "schema_version": "1.0.0",
        "persona_pack_id": f"persona_pack_{workspace_id}",
        "workspace_id": workspace_id,
        "title": "Persona Pack",
        "segment_refs": [{"entity_type": "segment", "entity_id": "segment_b2b_product_teams"}],
        "personas": [{"persona_id": "persona_incoming_pm", "name": "Incoming PM", "role": "Product Manager inheriting a product", "goals": ["Understand product quickly", "Identify evidence gaps"], "pains": ["Context reconstruction", "Scattered evidence"], "behavior_notes": "Will run takeover flow first thing."}],
        "created_at": "2026-05-12T08:00:00Z",
    }
    with open(ws / "artifacts" / "persona_pack.json", "w") as f:
        json.dump(pp, f, indent=2)
    return pp


def _add_mission_brief(ws: Path, workspace_id: str) -> dict:
    mb = {
        "schema_version": "1.0.0",
        "mission_brief_id": f"mission_brief_{workspace_id}",
        "workspace_id": workspace_id,
        "title": "PM Takeover Command Center",
        "mission_objective": "Build a takeover-first system that lets a new PM understand an existing product in one session.",
        "strategic_context": "ProductOS needs a compelling takeover wedge before expanding into broader PM autonomy.",
        "target_user": "Incoming product manager",
        "customer_problem": "New PMs waste weeks reconstructing context.",
        "business_goal": "Make ProductOS the default first tool for PM inheritance.",
        "success_metrics": ["Time to product understanding", "Evidence gap identification rate"],
        "created_at": "2026-05-12T08:00:00Z",
    }
    with open(ws / "artifacts" / "mission_brief.json", "w") as f:
        json.dump(mb, f, indent=2)
    return mb


def _add_prd(ws: Path, workspace_id: str) -> dict:
    prd = {
        "schema_version": "1.1.0",
        "prd_id": f"prd_{workspace_id}",
        "workspace_id": workspace_id,
        "title": "PRD: Takeover Command Center",
        "problem_summary": "PMs cannot quickly understand inherited products.",
        "outcome_summary": "A new PM can understand product, problem space, and roadmap in one session.",
        "scope_summary": "Build takeover orchestration flow with four synthesis artifacts.",
        "strategic_context_summary": "Takeover is the wedge for ProductOS adoption.",
        "value_hypothesis": "Takeover flow reduces PM context reconstruction from weeks to hours.",
        "target_outcomes": [{"outcome_id": "outcome_1", "description": "PM understands product in one session."}],
        "target_segment_refs": [{"entity_type": "segment", "entity_id": "segment_b2b_product_teams"}],
        "target_persona_refs": [{"entity_type": "persona", "entity_id": "persona_incoming_pm"}],
        "linked_entity_refs": [],
        "upstream_artifact_ids": [],
        "canonical_persona_archetype_pack_id": "",
        "artifact_trace_map_id": "",
        "ralph_status": "decision_ready",
        "prioritization": {"lane": "must_now", "priority_score": 95, "confidence": "high", "agentic_delivery_burden": "medium", "priority_rationale": "Takeover is the core superpower.", "reviewer_handoff": "Validate with PM."},
        "scope_boundaries": [{"boundary": "In scope: takeover orchestration", "type": "in_scope"}],
        "out_of_scope": ["Live research refresh"],
        "open_questions": ["Which research provider for live refresh?"],
        "handoff_risks": [],
        "generated_at": "2026-05-12T08:00:00Z",
    }
    with open(ws / "artifacts" / "prd.json", "w") as f:
        json.dump(prd, f, indent=2)
    return prd


# === Tests ===

class TestIngestScreenshots:
    def test_ingest_empty_screenshots_dir(self, tmp_path: Path):
        ws = _create_minimal_workspace(tmp_path, "ws_test_empty")
        records = ingest_screenshots(ws, generated_at="2026-05-12T08:00:00Z")
        assert records == []

    def test_ingest_screenshots_creates_visual_records(self, tmp_path: Path):
        ws = _create_minimal_workspace(tmp_path, "ws_test_screenshots")
        (ws / "inbox" / "screenshots" / "cockpit-dashboard.png").write_text("fake-png-data")
        (ws / "inbox" / "screenshots" / "journey-map.png").write_text("fake-png-data")
        (ws / "inbox" / "screenshots" / "readme.txt").write_text("not an image")

        records = ingest_screenshots(ws, generated_at="2026-05-12T08:00:00Z")
        assert len(records) == 2
        assert records[0]["source_type"] == "screenshot"
        assert records[0]["provenance"]["confidence"] == "inferred"
        assert records[0]["visual_record_id"] == "vr_cockpit_dashboard"
        assert records[1]["visual_record_id"] == "vr_journey_map"


class TestBuildProblemSpaceMap:
    def test_problem_space_map_from_workspace(self, tmp_path: Path):
        ws = _create_minimal_workspace(tmp_path, "ws_test_psm")
        _add_problem_brief(ws, "ws_test_psm")
        _add_competitor_dossier(ws, "ws_test_psm")
        _add_journey_map(ws, "ws_test_psm")

        psm = build_problem_space_map(ws, "ws_test_psm", generated_at="2026-05-12T08:00:00Z")
        assert psm["problem_space_map_id"] == "problem_space_map_ws_test_psm"
        assert len(psm["problems"]) >= 1
        assert len(psm["segment_links"]) >= 1
        assert len(psm["competitor_links"]) >= 1
        assert len(psm["workflow_links"]) >= 1
        assert len(psm["orphan_nodes"]) == 0

    def test_problem_space_map_no_artifacts(self, tmp_path: Path):
        ws = _create_minimal_workspace(tmp_path, "ws_test_empty")
        psm = build_problem_space_map(ws, "ws_test_empty", generated_at="2026-05-12T08:00:00Z")
        assert len(psm["orphan_nodes"]) >= 1

    def test_problem_space_map_validates_against_schema(self, tmp_path: Path, root_dir: Path):
        ws = _create_minimal_workspace(tmp_path, "ws_test_psm_schema")
        _add_problem_brief(ws, "ws_test_psm_schema")
        psm = build_problem_space_map(ws, "ws_test_psm_schema", generated_at="2026-05-12T08:00:00Z")
        validator = _validator_for("problem_space_map.schema.json", root_dir)
        errors = list(validator.iter_errors(psm))
        assert not errors, f"Schema validation errors: {errors}"


class TestBuildRoadmapRecoveryBrief:
    def test_roadmap_recovery_from_prd(self, tmp_path: Path):
        ws = _create_minimal_workspace(tmp_path, "ws_test_rr")
        _add_prd(ws, "ws_test_rr")
        _add_mission_brief(ws, "ws_test_rr")

        rr = build_roadmap_recovery_brief(ws, "ws_test_rr", generated_at="2026-05-12T08:00:00Z")
        assert rr["roadmap_recovery_brief_id"] == "roadmap_recovery_brief_ws_test_rr"
        assert len(rr["now_items"]) >= 1
        assert rr["confidence_assessment"]["overall_confidence"] in ("low", "moderate", "high")
        assert len(rr["unresolved_evidence_gaps"]) >= 1

    def test_roadmap_recovery_open_decisions(self, tmp_path: Path):
        ws = _create_minimal_workspace(tmp_path, "ws_test_rr_decisions")
        _add_prd(ws, "ws_test_rr_decisions")
        rr = build_roadmap_recovery_brief(ws, "ws_test_rr_decisions", generated_at="2026-05-12T08:00:00Z")
        assert isinstance(rr["open_decisions"], list)

    def test_roadmap_recovery_validates_against_schema(self, tmp_path: Path, root_dir: Path):
        ws = _create_minimal_workspace(tmp_path, "ws_test_rr_schema")
        _add_prd(ws, "ws_test_rr_schema")
        rr = build_roadmap_recovery_brief(ws, "ws_test_rr_schema", generated_at="2026-05-12T08:00:00Z")
        validator = _validator_for("roadmap_recovery_brief.schema.json", root_dir)
        errors = list(validator.iter_errors(rr))
        assert not errors, f"Schema validation errors: {errors}"


class TestBuildVisualProductAtlas:
    def test_visual_atlas_with_screenshots(self, tmp_path: Path):
        ws = _create_minimal_workspace(tmp_path, "ws_test_va")
        _add_journey_map(ws, "ws_test_va")
        (ws / "inbox" / "screenshots" / "cockpit.png").write_text("fake-png")
        (ws / "inbox" / "screenshots" / "journey.png").write_text("fake-png")

        va = build_visual_product_atlas(ws, "ws_test_va", generated_at="2026-05-12T08:00:00Z")
        assert va["visual_product_atlas_id"] == "visual_product_atlas_ws_test_va"
        assert len(va["visual_evidence_records"]) == 2
        assert len(va["journey_stage_links"]) >= 1
        assert len(va["screen_flow_nodes"]) == 2

    def test_visual_atlas_no_screenshots(self, tmp_path: Path):
        ws = _create_minimal_workspace(tmp_path, "ws_test_va_empty")
        _add_journey_map(ws, "ws_test_va_empty")
        va = build_visual_product_atlas(ws, "ws_test_va_empty", generated_at="2026-05-12T08:00:00Z")
        assert len(va["visual_evidence_records"]) == 0
        assert len(va["screen_flow_nodes"]) == 0

    def test_visual_atlas_validates_against_schema(self, tmp_path: Path, root_dir: Path):
        ws = _create_minimal_workspace(tmp_path, "ws_test_va_schema")
        _add_journey_map(ws, "ws_test_va_schema")
        (ws / "inbox" / "screenshots" / "test.png").write_text("fake-png")
        va = build_visual_product_atlas(ws, "ws_test_va_schema", generated_at="2026-05-12T08:00:00Z")
        validator = _validator_for("visual_product_atlas.schema.json", root_dir)
        errors = list(validator.iter_errors(va))
        assert not errors, f"Schema validation errors: {errors}"


class TestBuildTakeoverBrief:
    def test_takeover_brief_contains_all_sections(self, tmp_path: Path):
        ws = _create_minimal_workspace(tmp_path, "ws_test_tb")
        _add_problem_brief(ws, "ws_test_tb")
        _add_competitor_dossier(ws, "ws_test_tb")
        _add_persona_pack(ws, "ws_test_tb")
        _add_journey_map(ws, "ws_test_tb")
        _add_prd(ws, "ws_test_tb")

        psm = build_problem_space_map(ws, "ws_test_tb", generated_at="2026-05-12T08:00:00Z")
        rr = build_roadmap_recovery_brief(ws, "ws_test_tb", generated_at="2026-05-12T08:00:00Z")
        va = build_visual_product_atlas(ws, "ws_test_tb", generated_at="2026-05-12T08:00:00Z")

        tb = build_takeover_brief(
            ws, "ws_test_tb",
            problem_space_map=psm,
            visual_product_atlas=va,
            roadmap_recovery=rr,
            generated_at="2026-05-12T08:00:00Z",
        )
        assert tb["takeover_brief_id"] == "takeover_brief_ws_test_tb"
        assert tb["product_summary"]
        assert tb["old_problem_framing"]
        assert tb["target_segment_summary"]
        assert tb["target_persona_summary"]
        assert tb["competitor_summary"]
        assert tb["customer_journey_summary"]
        assert tb["roadmap_summary"]
        assert len(tb["evidence_gaps"]) >= 0
        assert "first_30_days" in tb["first_pm_actions"]
        assert "first_60_days" in tb["first_pm_actions"]
        assert "first_90_days" in tb["first_pm_actions"]

    def test_takeover_brief_evidence_gaps(self, tmp_path: Path):
        ws = _create_minimal_workspace(tmp_path, "ws_test_tb_gaps")
        rr = build_roadmap_recovery_brief(ws, "ws_test_tb_gaps", generated_at="2026-05-12T08:00:00Z")
        tb = build_takeover_brief(ws, "ws_test_tb_gaps", roadmap_recovery=rr, generated_at="2026-05-12T08:00:00Z")
        gaps = tb["evidence_gaps"]
        assert len(gaps) >= 1

    def test_takeover_brief_validates_against_schema(self, tmp_path: Path, root_dir: Path):
        ws = _create_minimal_workspace(tmp_path, "ws_test_tb_schema")
        _add_problem_brief(ws, "ws_test_tb_schema")
        _add_competitor_dossier(ws, "ws_test_tb_schema")
        _add_persona_pack(ws, "ws_test_tb_schema")
        _add_journey_map(ws, "ws_test_tb_schema")
        _add_prd(ws, "ws_test_tb_schema")
        _add_mission_brief(ws, "ws_test_tb_schema")

        psm = build_problem_space_map(ws, "ws_test_tb_schema", generated_at="2026-05-12T08:00:00Z")
        rr = build_roadmap_recovery_brief(ws, "ws_test_tb_schema", generated_at="2026-05-12T08:00:00Z")
        va = build_visual_product_atlas(ws, "ws_test_tb_schema", generated_at="2026-05-12T08:00:00Z")
        tb = build_takeover_brief(
            ws, "ws_test_tb_schema",
            problem_space_map=psm,
            visual_product_atlas=va,
            roadmap_recovery=rr,
            generated_at="2026-05-12T08:00:00Z",
        )
        validator = _validator_for("takeover_brief.schema.json", root_dir)
        errors = list(validator.iter_errors(tb))
        assert not errors, f"Schema validation errors: {errors}"


class TestBuildTakeoverFeatureScorecard:
    def test_scorecard_with_all_artifacts(self, tmp_path: Path):
        ws = _create_minimal_workspace(tmp_path, "ws_test_sc")
        _add_problem_brief(ws, "ws_test_sc")
        _add_competitor_dossier(ws, "ws_test_sc")

        psm = build_problem_space_map(ws, "ws_test_sc", generated_at="2026-05-12T08:00:00Z")
        rr = build_roadmap_recovery_brief(ws, "ws_test_sc", generated_at="2026-05-12T08:00:00Z")
        va = build_visual_product_atlas(ws, "ws_test_sc", generated_at="2026-05-12T08:00:00Z")
        tb = build_takeover_brief(ws, "ws_test_sc", generated_at="2026-05-12T08:00:00Z")

        sc = build_takeover_feature_scorecard(
            ws, "ws_test_sc",
            takeover_brief=tb,
            problem_space_map=psm,
            roadmap_recovery=rr,
            visual_product_atlas=va,
            generated_at="2026-05-12T08:00:00Z",
        )
        assert sc["feature_scorecard_id"] == "takeover_feature_scorecard_ws_test_sc"
        assert 1 <= sc["overall_score"] <= 5
        assert len(sc["scenarios"]) >= 4
        assert sc["adoption_recommendation"] in ("promote_as_standard", "keep_in_internal_use", "route_to_improvement", "block")

    def test_scorecard_validates_against_schema(self, tmp_path: Path, root_dir: Path):
        ws = _create_minimal_workspace(tmp_path, "ws_test_sc_schema")
        psm = build_problem_space_map(ws, "ws_test_sc_schema", generated_at="2026-05-12T08:00:00Z")
        rr = build_roadmap_recovery_brief(ws, "ws_test_sc_schema", generated_at="2026-05-12T08:00:00Z")
        va = build_visual_product_atlas(ws, "ws_test_sc_schema", generated_at="2026-05-12T08:00:00Z")
        tb = build_takeover_brief(ws, "ws_test_sc_schema", generated_at="2026-05-12T08:00:00Z")
        sc = build_takeover_feature_scorecard(
            ws, "ws_test_sc_schema",
            takeover_brief=tb,
            problem_space_map=psm,
            roadmap_recovery=rr,
            visual_product_atlas=va,
            generated_at="2026-05-12T08:00:00Z",
        )
        validator = _validator_for("feature_scorecard.schema.json", root_dir)
        errors = list(validator.iter_errors(sc))
        assert not errors, f"Schema validation errors: {errors}"


class TestBuildTakeoverCockpitSection:
    def test_cockpit_section_has_all_fields(self, tmp_path: Path):
        ws = _create_minimal_workspace(tmp_path, "ws_test_cockpit")
        tb = build_takeover_brief(ws, "ws_test_cockpit", generated_at="2026-05-12T08:00:00Z")
        psm = build_problem_space_map(ws, "ws_test_cockpit", generated_at="2026-05-12T08:00:00Z")
        rr = build_roadmap_recovery_brief(ws, "ws_test_cockpit", generated_at="2026-05-12T08:00:00Z")
        va = build_visual_product_atlas(ws, "ws_test_cockpit", generated_at="2026-05-12T08:00:00Z")

        section = build_takeover_cockpit_section(
            ws, "ws_test_cockpit",
            takeover_brief=tb,
            problem_space_map=psm,
            roadmap_recovery=rr,
            visual_product_atlas=va,
        )
        assert "takeover_status" in section
        assert "evidence_gap_count" in section
        assert "required_pm_actions" in section
        assert isinstance(section["required_pm_actions"], list)


class TestRenderTakeoverAtlasHTML:
    def test_render_html_contains_key_sections(self, tmp_path: Path):
        ws = _create_minimal_workspace(tmp_path, "ws_test_html")
        _add_problem_brief(ws, "ws_test_html")
        _add_competitor_dossier(ws, "ws_test_html")
        _add_journey_map(ws, "ws_test_html")
        (ws / "inbox" / "screenshots" / "cockpit.png").write_text("fake-png")

        psm = build_problem_space_map(ws, "ws_test_html", generated_at="2026-05-12T08:00:00Z")
        rr = build_roadmap_recovery_brief(ws, "ws_test_html", generated_at="2026-05-12T08:00:00Z")
        va = build_visual_product_atlas(ws, "ws_test_html", generated_at="2026-05-12T08:00:00Z")
        tb = build_takeover_brief(ws, "ws_test_html", generated_at="2026-05-12T08:00:00Z")
        sc = build_takeover_feature_scorecard(ws, "ws_test_html", generated_at="2026-05-12T08:00:00Z")

        html = render_takeover_atlas_html(tb, psm, rr, va, takeover_feature_scorecard=sc)
        assert "<!doctype html>" in html
        assert "PM Takeover Atlas" in html
        assert "Product Overview" in html
        assert "Problem Space" in html
        assert "Roadmap State" in html
        assert "Visual Evidence" in html
        assert "Evidence Gaps" in html
        assert "First PM Actions" in html
        assert "Feature Scorecard" in html

    def test_render_html_without_gaps(self, tmp_path: Path):
        ws = _create_minimal_workspace(tmp_path, "ws_test_html_nogaps")
        _add_journey_map(ws, "ws_test_html_nogaps")
        _add_competitor_dossier(ws, "ws_test_html_nogaps")
        _add_mission_brief(ws, "ws_test_html_nogaps")
        tb = build_takeover_brief(ws, "ws_test_html_nogaps", generated_at="2026-05-12T08:00:00Z")
        psm = build_problem_space_map(ws, "ws_test_html_nogaps", generated_at="2026-05-12T08:00:00Z")
        rr = build_roadmap_recovery_brief(ws, "ws_test_html_nogaps", generated_at="2026-05-12T08:00:00Z")
        va = build_visual_product_atlas(ws, "ws_test_html_nogaps", generated_at="2026-05-12T08:00:00Z")
        html = render_takeover_atlas_html(tb, psm, rr, va)
        assert "Evidence Gaps" in html


class TestBuildTakeoverBundle:
    def test_bundle_creates_all_artifacts_in_existing_workspace(self, tmp_path: Path):
        ws = _create_minimal_workspace(tmp_path, "ws_test_bundle")
        _add_problem_brief(ws, "ws_test_bundle")
        _add_competitor_dossier(ws, "ws_test_bundle")
        _add_journey_map(ws, "ws_test_bundle")
        _add_persona_pack(ws, "ws_test_bundle")
        _add_prd(ws, "ws_test_bundle")

        bundle = build_takeover_bundle(
            tmp_path,
            dest=str(ws),
            workspace_id="ws_test_bundle",
            name="Test Bundle",
            mode="research",
            generated_at="2026-05-12T08:00:00Z",
        )
        assert "takeover_brief" in bundle
        assert "problem_space_map" in bundle
        assert "roadmap_recovery_brief" in bundle
        assert "visual_product_atlas" in bundle
        assert "takeover_feature_scorecard" in bundle

        assert bundle["takeover_brief"]["workspace_id"] == "ws_test_bundle"
        assert bundle["problem_space_map"]["workspace_id"] == "ws_test_bundle"
        assert bundle["roadmap_recovery_brief"]["workspace_id"] == "ws_test_bundle"
        assert bundle["visual_product_atlas"]["workspace_id"] == "ws_test_bundle"
        assert bundle["takeover_feature_scorecard"]["workspace_id"] == "ws_test_bundle"

        assert (ws / "outputs" / "takeover" / "takeover_bundle.json").exists()
        assert (ws / "outputs" / "takeover" / "takeover_atlas.html").exists()
        assert (ws / "outputs" / "takeover" / "takeover_cockpit_section.json").exists()

    def test_bundle_artifact_files_written(self, tmp_path: Path):
        ws = _create_minimal_workspace(tmp_path, "ws_test_bundle_files")
        _add_problem_brief(ws, "ws_test_bundle_files")

        bundle = build_takeover_bundle(
            tmp_path,
            dest=str(ws),
            workspace_id="ws_test_bundle_files",
            name="Test Bundle Files",
            mode="research",
            generated_at="2026-05-12T08:00:00Z",
        )
        assert (ws / "artifacts" / "takeover_brief_ws_test_bundle_files.json").exists()
        assert (ws / "artifacts" / "problem_space_map_ws_test_bundle_files.json").exists()
        assert (ws / "artifacts" / "roadmap_recovery_brief_ws_test_bundle_files.json").exists()
        assert (ws / "artifacts" / "visual_product_atlas_ws_test_bundle_files.json").exists()
        assert (ws / "artifacts" / "takeover_feature_scorecard_ws_test_bundle_files.json").exists()

    def test_bundle_validates_all_against_schemas(self, tmp_path: Path, root_dir: Path):
        ws = _create_minimal_workspace(tmp_path, "ws_test_bundle_schema")
        _add_problem_brief(ws, "ws_test_bundle_schema")
        _add_competitor_dossier(ws, "ws_test_bundle_schema")
        _add_journey_map(ws, "ws_test_bundle_schema")
        _add_persona_pack(ws, "ws_test_bundle_schema")
        _add_prd(ws, "ws_test_bundle_schema")

        bundle = build_takeover_bundle(
            tmp_path,
            dest=str(ws),
            workspace_id="ws_test_bundle_schema",
            name="Test Bundle Schema",
            mode="research",
            generated_at="2026-05-12T08:00:00Z",
        )

        for schema_key, schema_file in TAKEOVER_ARTIFACT_SCHEMAS.items():
            validator = _validator_for(schema_file, root_dir)
            errors = list(validator.iter_errors(bundle[schema_key]))
            assert not errors, f"Schema validation errors for {schema_key}: {errors}"


class TestTakeoverCLI:
    def test_takeover_cli_help(self, root_dir: Path):
        result = _run_cli(root_dir, "takeover", "--help")
        assert result.returncode == 0
        assert "--source" in result.stdout
        assert "--dest" in result.stdout
        assert "--workspace-id" in result.stdout

    def test_takeover_cli_with_minimal_source(self, root_dir: Path, tmp_path: Path):
        source_dir = tmp_path / "source-product"
        source_dir.mkdir()
        (source_dir / "README.md").write_text("# Test Product\n\nA product for testing takeover.\n", encoding="utf-8")
        (source_dir / "roadmap.md").write_text("# Roadmap\n\nNow: Build takeover flow\nNext: Live research\n", encoding="utf-8")

        dest = tmp_path / "takeover-output"
        result = _run_cli(
            root_dir,
            "takeover",
            "--source", str(source_dir),
            "--dest", str(dest),
            "--workspace-id", "ws_cli_takeover_test",
            "--name", "CLI Takeover Test",
            "--mode", "research",
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        assert "Takeover Brief" in result.stdout
        assert "Problems" in result.stdout
        assert "Evidence Gaps" in result.stdout
        assert "Scorecard" in result.stdout

    def test_render_takeover_atlas_cli_help(self, root_dir: Path):
        result = _run_cli(root_dir, "render", "takeover-atlas", "--help")
        assert result.returncode == 0
        assert "--workspace-dir" in result.stdout

    def test_takeover_cli_outputs_artifacts(self, root_dir: Path, tmp_path: Path):
        source_dir = tmp_path / "source-artifacts"
        source_dir.mkdir()
        (source_dir / "README.md").write_text("# Artifact Test\n\nTesting artifact output.\n", encoding="utf-8")

        dest = tmp_path / "takeover-artifacts"
        result = _run_cli(
            root_dir,
            "takeover",
            "--source", str(source_dir),
            "--dest", str(dest),
            "--workspace-id", "ws_cli_artifact_test",
            "--name", "CLI Artifact Test",
            "--mode", "research",
        )
        assert result.returncode == 0

        takeover_output = dest / "outputs" / "takeover"
        assert (takeover_output / "takeover_bundle.json").exists()
        assert (takeover_output / "takeover_atlas.html").exists()
        assert (takeover_output / "takeover_cockpit_section.json").exists()

        bundle = _load_json(takeover_output / "takeover_bundle.json")
        for key in ("takeover_brief", "problem_space_map", "roadmap_recovery_brief", "visual_product_atlas", "takeover_feature_scorecard"):
            assert key in bundle, f"Missing {key} in bundle"


class TestTakeoverLivingSystemPropagation:
    def test_takeover_artifacts_participate_in_regeneration_queue(self, root_dir: Path, tmp_path: Path):
        from core.python.productos_runtime.living_system import build_regeneration_queue

        ws = _create_minimal_workspace(tmp_path, "ws_test_living")
        _add_problem_brief(ws, "ws_test_living")
        _add_competitor_dossier(ws, "ws_test_living")

        bundle = build_takeover_bundle(
            tmp_path,
            dest=str(ws),
            workspace_id="ws_test_living",
            name="Living Test",
            mode="research",
            generated_at="2026-05-12T08:00:00Z",
        )

        queue = build_regeneration_queue(
            trigger_event={"trigger_type": "artifact_updated", "source_artifact_ref": "problem_brief_ws_test_living", "change_summary": "Problem brief updated."},
            workspace_dir=ws,
            generated_at="2026-05-12T08:00:00Z",
        )
        assert "queued_items" in queue
        assert isinstance(queue["queued_items"], list)


class TestSchemaExamples:
    def test_takeover_brief_example_validates(self, root_dir: Path):
        example = _load_json(root_dir / "core" / "examples" / "artifacts" / "takeover_brief.example.json")
        validator = _validator_for("takeover_brief.schema.json", root_dir)
        errors = list(validator.iter_errors(example))
        assert not errors, f"Example validation errors: {errors}"

    def test_problem_space_map_example_validates(self, root_dir: Path):
        example = _load_json(root_dir / "core" / "examples" / "artifacts" / "problem_space_map.example.json")
        validator = _validator_for("problem_space_map.schema.json", root_dir)
        errors = list(validator.iter_errors(example))
        assert not errors, f"Example validation errors: {errors}"

    def test_roadmap_recovery_brief_example_validates(self, root_dir: Path):
        example = _load_json(root_dir / "core" / "examples" / "artifacts" / "roadmap_recovery_brief.example.json")
        validator = _validator_for("roadmap_recovery_brief.schema.json", root_dir)
        errors = list(validator.iter_errors(example))
        assert not errors, f"Example validation errors: {errors}"

    def test_visual_product_atlas_example_validates(self, root_dir: Path):
        example = _load_json(root_dir / "core" / "examples" / "artifacts" / "visual_product_atlas.example.json")
        validator = _validator_for("visual_product_atlas.schema.json", root_dir)
        errors = list(validator.iter_errors(example))
        assert not errors, f"Example validation errors: {errors}"
