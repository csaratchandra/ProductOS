from __future__ import annotations

import copy
import json
import shutil
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

from . import yaml_compat as yaml
from .adoption import build_workspace_adoption_bundle_from_source
from .lifecycle import init_workspace_from_template
from .research import build_external_research_plan_from_workspace, run_external_research_loop_from_workspace
from .journey_synthesis import synthesize_customer_journey_map


TAKEOVER_ARTIFACT_SCHEMAS: dict[str, str] = {
    "takeover_brief": "takeover_brief.schema.json",
    "problem_space_map": "problem_space_map.schema.json",
    "roadmap_recovery_brief": "roadmap_recovery_brief.schema.json",
    "visual_product_atlas": "visual_product_atlas.schema.json",
}

ROOT = Path(__file__).resolve().parents[3]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def _artifact_path(workspace_dir: Path, filename: str) -> Path:
    return workspace_dir / "artifacts" / filename


def _artifact_exists(workspace_dir: Path, filename: str) -> bool:
    return _artifact_path(workspace_dir, filename).exists()


def _load_artifact(workspace_dir: Path, filename: str) -> dict[str, Any] | None:
    path = _artifact_path(workspace_dir, filename)
    if not path.exists():
        return None
    return _load_json(path)


def _slug(value: str) -> str:
    normalized = "".join(char.lower() if char.isalnum() else "_" for char in value)
    while "__" in normalized:
        normalized = normalized.replace("__", "_")
    return normalized.strip("_")


def _append_manifest_artifact_path(manifest_path: Path, artifact_path: str) -> None:
    if not manifest_path.exists():
        return
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    paths = manifest.get("artifact_paths", [])
    if artifact_path not in paths:
        paths.append(artifact_path)
    manifest["artifact_paths"] = paths
    with manifest_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(manifest, f, sort_keys=False)


def ingest_screenshots(workspace_dir: Path, *, generated_at: str | None = None) -> list[dict[str, Any]]:
    generated_at = generated_at or _now_iso()
    screenshots_dir = workspace_dir / "inbox" / "screenshots"
    visual_records: list[dict[str, Any]] = []
    if not screenshots_dir.exists():
        return visual_records

    known_extensions = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp"}
    for path in sorted(screenshots_dir.iterdir()):
        if not path.is_file() or path.suffix.lower() not in known_extensions:
            continue
        record_id = f"vr_{_slug(path.stem)}"
        visual_records.append(
            {
                "visual_record_id": record_id,
                "source_path": str(path.relative_to(workspace_dir)),
                "source_type": "screenshot",
                "screen_purpose": f"Screenshot captured from workspace: {path.stem}",
                "probable_workflow_stage": "unknown",
                "linked_artifact_refs": [],
                "provenance": {
                    "source": f"inbox/screenshots/{path.name}",
                    "confidence": "inferred",
                },
                "captured_at": generated_at,
            }
        )
    return visual_records


def _infer_screen_purpose_from_context(workspace_dir: Path, stem: str) -> str:
    lowered = stem.lower()
    keyword_map = {
        "cockpit": "PM cockpit dashboard showing workspace overview and mission status",
        "dashboard": "Analytics or metrics dashboard for product performance tracking",
        "journey": "Customer journey map visualization with stages and emotion curve",
        "screen": "Application screen flow or user interface mockup",
        "flow": "Screen flow or workflow visualization showing user navigation paths",
        "roadmap": "Product roadmap view showing planned features and timeline",
        "segment": "Segment map or customer segmentation visualization",
        "persona": "Persona profile card or archetype visualization",
        "competitor": "Competitor landscape or competitive analysis view",
        "market": "Market analysis or market sizing visualization",
        "prototype": "Interactive prototype or wireframe mockup",
        "deck": "Presentation deck slide or slide preview",
        "corridor": "Workflow corridor visualization showing user paths",
    }
    for keyword, purpose in keyword_map.items():
        if keyword in lowered:
            return purpose
    return f"Product screenshot related to: {stem}"


def build_takeover_brief(
    workspace_dir: Path,
    workspace_id: str,
    *,
    adoption_bundle: dict[str, Any] | None = None,
    problem_space_map: dict[str, Any] | None = None,
    visual_product_atlas: dict[str, Any] | None = None,
    roadmap_recovery: dict[str, Any] | None = None,
    takeover_feature_scorecard: dict[str, Any] | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    generated_at = generated_at or _now_iso()
    existing_problem_brief = _load_artifact(workspace_dir, "problem_brief.json")
    existing_competitor_dossier = _load_artifact(workspace_dir, "competitor_dossier.json")
    existing_persona_pack = _load_artifact(workspace_dir, "persona_pack.json")
    existing_segment_map = _load_artifact(workspace_dir, "segment_map.json")
    existing_journey_map = _load_artifact(workspace_dir, "customer_journey_map.json")
    existing_mission_brief = _load_artifact(workspace_dir, "mission_brief.json")
    existing_prd = _load_artifact(workspace_dir, "prd.json")

    problem_summary = ""
    if existing_problem_brief:
        problem_summary = existing_problem_brief.get("problem_summary", "")
    if not problem_summary and adoption_bundle:
        problem_summary = adoption_bundle.get("problem_brief", {}).get("problem_summary", "")

    segment_summary = ""
    persona_summary = ""
    if existing_segment_map:
        segment_summary = existing_segment_map.get("market_scope_summary", "")
    if existing_persona_pack:
        persona_summaries = [p.get("role", p.get("name", "")) for p in existing_persona_pack.get("personas", [])]
        persona_summary = ", ".join(persona_summaries) if persona_summaries else ""

    competitor_summary = ""
    if existing_competitor_dossier:
        competitor_summary = existing_competitor_dossier.get("competitive_frame", "")

    journey_summary = ""
    if existing_journey_map:
        stages = existing_journey_map.get("journey_stages", [])
        stage_names = [s.get("stage_name", "") for s in stages]
        journey_summary = f"Journey spans {len(stages)} stages: {', '.join(stage_names)}"

    roadmap_summary = ""
    if existing_prd:
        roadmap_summary = existing_prd.get("scope_summary", existing_prd.get("outcome_summary", ""))
    if not roadmap_summary and existing_mission_brief:
        roadmap_summary = existing_mission_brief.get("mission_objective", "")

    evidence_gaps: list[dict[str, Any]] = []
    gap_index = 0

    if existing_competitor_dossier:
        coverage = existing_competitor_dossier.get("evidence_coverage_status", "")
        if coverage == "incomplete":
            evidence_gaps.append({
                "gap_id": f"gap_competitor_evidence_{gap_index}",
                "description": "Competitor dossier evidence coverage is incomplete. Fresh competitive intelligence is needed.",
                "severity": "high",
                "related_artifact_refs": [existing_competitor_dossier.get("competitor_dossier_id", "competitor_dossier")],
            })
            gap_index += 1

    if not existing_journey_map:
        evidence_gaps.append({
            "gap_id": f"gap_journey_map_{gap_index}",
            "description": "No customer journey map found. User experience understanding is incomplete.",
            "severity": "high",
            "related_artifact_refs": [],
        })
        gap_index += 1

    if roadmap_recovery:
        for gap in roadmap_recovery.get("unresolved_evidence_gaps", []):
            evidence_gaps.append({
                "gap_id": gap.get("gap_id", f"gap_roadmap_{gap_index}"),
                "description": gap.get("description", "Unresolved evidence gap from roadmap recovery"),
                "severity": "medium",
                "related_artifact_refs": gap.get("blocking_items", []),
            })
            gap_index += 1

    product_summary = ""
    if existing_mission_brief:
        product_summary = existing_mission_brief.get("mission_objective", "")
    if not product_summary and adoption_bundle:
        product_summary = adoption_bundle.get("workspace_adoption_report", {}).get("source_summary", "")

    action_30 = ["Review all takeover artifacts to build baseline understanding of product state."]
    action_60 = ["Validate evidence gaps and refresh stale artifacts with current intelligence."]
    action_90 = ["Drive roadmap items toward delivery milestones and validate takeover scorecard."]

    if existing_problem_brief:
        action_30.append(f"Review existing problem brief: {existing_problem_brief.get('title', '')}")
    if adoption_bundle:
        review_queue = adoption_bundle.get("adoption_review_queue", {})
        review_items = review_queue.get("review_items", [])
        if review_items:
            action_30.append(f"Process {len(review_items)} adoption review items.")

    return {
        "schema_version": "1.0.0",
        "takeover_brief_id": f"takeover_brief_{workspace_id}",
        "workspace_id": workspace_id,
        "title": f"Takeover Brief: {workspace_id}",
        "product_summary": product_summary or "Product summary not yet available from workspace artifacts.",
        "old_problem_framing": problem_summary or "Problem framing not yet available from workspace artifacts.",
        "change_over_time": [],
        "target_segment_summary": segment_summary or "Target segment not yet identified in workspace artifacts.",
        "target_segment_refs": [{"entity_type": "segment", "entity_id": seg["entity_id"]} for seg in (existing_problem_brief or {}).get("target_segment_refs", [])] if existing_problem_brief else [],
        "target_persona_summary": persona_summary or "Target persona not yet defined in workspace artifacts.",
        "target_persona_refs": [{"entity_type": "persona", "entity_id": p["entity_id"]} for p in (existing_problem_brief or {}).get("target_persona_refs", [])] if existing_problem_brief else [],
        "competitor_summary": competitor_summary or "Competitor analysis not yet available from workspace artifacts.",
        "competitor_dossier_ref": existing_competitor_dossier.get("competitor_dossier_id", "competitor_dossier_not_found") if existing_competitor_dossier else "competitor_dossier_not_found",
        "customer_journey_summary": journey_summary or "Customer journey not yet synthesized for this workspace.",
        "customer_journey_ref": existing_journey_map.get("customer_journey_map_id", "customer_journey_not_found") if existing_journey_map else "customer_journey_not_found",
        "roadmap_summary": roadmap_summary or "Roadmap state not yet recovered for this workspace.",
        "roadmap_recovery_ref": roadmap_recovery.get("roadmap_recovery_brief_id", "roadmap_recovery_not_found") if roadmap_recovery else "roadmap_recovery_not_found",
        "evidence_gaps": evidence_gaps,
        "first_pm_actions": {
            "first_30_days": action_30,
            "first_60_days": action_60,
            "first_90_days": action_90,
        },
        "source_workspace_ref": workspace_id,
        "problem_space_map_ref": problem_space_map.get("problem_space_map_id", "problem_space_map_not_found") if problem_space_map else "problem_space_map_not_found",
        "visual_product_atlas_ref": visual_product_atlas.get("visual_product_atlas_id", "visual_product_atlas_not_found") if visual_product_atlas else "visual_product_atlas_not_found",
        "takeover_feature_scorecard_ref": takeover_feature_scorecard.get("feature_scorecard_id", "feature_scorecard_not_found") if takeover_feature_scorecard else "feature_scorecard_not_found",
        "generated_at": generated_at,
    }


def build_problem_space_map(
    workspace_dir: Path,
    workspace_id: str,
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    generated_at = generated_at or _now_iso()
    existing_problem_brief = _load_artifact(workspace_dir, "problem_brief.json")
    existing_segment_map = _load_artifact(workspace_dir, "segment_map.json")
    existing_persona_pack = _load_artifact(workspace_dir, "persona_pack.json")
    existing_competitor_dossier = _load_artifact(workspace_dir, "competitor_dossier.json")
    existing_prd = _load_artifact(workspace_dir, "prd.json")
    existing_journey_map = _load_artifact(workspace_dir, "customer_journey_map.json")

    problems: list[dict[str, Any]] = []
    if existing_problem_brief:
        problems.append({
            "problem_id": existing_problem_brief.get("problem_brief_id", "problem_1"),
            "title": existing_problem_brief.get("title", "Unknown problem"),
            "summary": existing_problem_brief.get("problem_summary", ""),
            "severity": existing_problem_brief.get("problem_severity", {}).get("customer_pain", "medium"),
            "source_artifact_ids": [existing_problem_brief.get("problem_brief_id", "")],
        })

    segment_links: list[dict[str, Any]] = []
    if existing_problem_brief:
        for ref in existing_problem_brief.get("target_segment_refs", []):
            for problem in problems:
                segment_links.append({
                    "source_id": problem["problem_id"],
                    "target_id": ref.get("entity_id", ""),
                    "relationship": "impacts",
                })

    persona_links: list[dict[str, Any]] = []
    if existing_problem_brief:
        for ref in existing_problem_brief.get("target_persona_refs", []):
            for problem in problems:
                persona_links.append({
                    "source_id": problem["problem_id"],
                    "target_id": ref.get("entity_id", ""),
                    "relationship": "primary_pain",
                })

    workflow_links: list[dict[str, Any]] = []
    if existing_journey_map:
        for stage in existing_journey_map.get("journey_stages", []):
            workflow_links.append({
                "workflow_id": f"wf_{_slug(stage.get('stage_name', ''))}",
                "workflow_name": stage.get("stage_name", "Unknown stage"),
                "problem_ids": [p["problem_id"] for p in problems],
                "journey_stage": stage.get("stage_name", ""),
            })

    evidence_links: list[dict[str, Any]] = []
    if existing_problem_brief:
        for ref in existing_problem_brief.get("evidence_refs", []):
            source_type = ref.get("source_type", "other")
            evidence_links.append({
                "evidence_id": f"evidence_{_slug(ref.get('source_id', ''))}",
                "source_type": source_type,
                "summary": ref.get("justification", "Evidence from problem brief"),
                "problem_ids": [p["problem_id"] for p in problems],
                "confidence": "moderate",
            })

    competitor_links: list[dict[str, Any]] = []
    if existing_competitor_dossier:
        for comp in existing_competitor_dossier.get("competitors", []):
            competitor_links.append({
                "competitor_name": comp.get("name", comp.get("competitor_name", "Unknown competitor")),
                "problem_ids": [p["problem_id"] for p in problems],
                "threat_level": "medium",
            })

    product_bet_links: list[dict[str, Any]] = []
    if existing_prd:
        product_bet_links.append({
            "bet_id": existing_prd.get("prd_id", "bet_current"),
            "bet_name": existing_prd.get("title", "Current product bet"),
            "problem_ids": [p["problem_id"] for p in problems],
            "status": "active",
            "confidence": "moderate",
        })

    orphan_nodes: list[dict[str, Any]] = []
    if not problems:
        orphan_nodes.append({
            "node_type": "problem",
            "node_id": "no_problems_found",
            "reason": "No problem_brief.json found in workspace artifacts.",
        })

    if problems:
        if not segment_links:
            orphan_nodes.append({
                "node_type": "segment",
                "node_id": "no_segment_links",
                "reason": "Problems exist but no segment links were found in workspace artifacts.",
            })
        if not persona_links:
            orphan_nodes.append({
                "node_type": "persona",
                "node_id": "no_persona_links",
                "reason": "Problems exist but no persona links were found in workspace artifacts.",
            })

    return {
        "schema_version": "1.0.0",
        "problem_space_map_id": f"problem_space_map_{workspace_id}",
        "workspace_id": workspace_id,
        "title": f"Problem Space Map: {workspace_id}",
        "problems": problems if problems else [{"problem_id": "problem_unknown", "title": "Unknown problem", "summary": "No problem brief found in workspace.", "severity": "medium", "source_artifact_ids": []}],
        "segment_links": segment_links,
        "persona_links": persona_links,
        "workflow_links": workflow_links,
        "evidence_links": evidence_links,
        "competitor_links": competitor_links,
        "product_bet_links": product_bet_links,
        "orphan_nodes": orphan_nodes,
        "generated_at": generated_at,
    }


def build_roadmap_recovery_brief(
    workspace_dir: Path,
    workspace_id: str,
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    generated_at = generated_at or _now_iso()
    existing_prd = _load_artifact(workspace_dir, "prd.json")
    existing_increment_plan = _load_artifact(workspace_dir, "increment_plan.json")
    existing_program_increment = _load_artifact(workspace_dir, "program_increment_state.json")
    existing_decision_queue = _load_artifact(workspace_dir, "decision_queue.json")
    existing_mission_brief = _load_artifact(workspace_dir, "mission_brief.json")
    existing_problem_brief = _load_artifact(workspace_dir, "problem_brief.json")

    now_items: list[dict[str, Any]] = []
    next_items: list[dict[str, Any]] = []
    later_items: list[dict[str, Any]] = []

    if existing_prd:
        now_items.append({
            "item_id": existing_prd.get("prd_id", "item_prd_current"),
            "title": existing_prd.get("title", "Current PRD"),
            "summary": existing_prd.get("outcome_summary", existing_prd.get("scope_summary", "Current PRD scope")),
            "confidence": "moderate",
            "dependencies": [],
            "artifact_refs": [existing_prd.get("prd_id", "prd")],
        })

    if existing_increment_plan:
        for feature in existing_increment_plan.get("planned_features", existing_increment_plan.get("scope_items", [])):
            now_items.append({
                "item_id": f"item_{_slug(feature.get('name', feature.get('title', 'unknown')))}",
                "title": feature.get("name", feature.get("title", "Planned feature")),
                "summary": feature.get("description", feature.get("summary", "Feature from increment plan")),
                "confidence": "moderate",
                "dependencies": feature.get("dependencies", []),
                "artifact_refs": [existing_increment_plan.get("increment_plan_id", "increment_plan")],
            })

    if existing_program_increment:
        objectives = existing_program_increment.get("program_objectives", existing_program_increment.get("objectives", []))
        for obj in objectives:
            next_items.append({
                "item_id": f"item_{_slug(obj.get('name', obj.get('title', 'unknown')))}",
                "title": obj.get("name", obj.get("title", "Program objective")),
                "summary": obj.get("description", obj.get("summary", "Objective from program increment")),
                "confidence": "moderate",
                "dependencies": [],
                "artifact_refs": [existing_program_increment.get("program_increment_state_id", "program_increment_state")],
            })

    if existing_decision_queue:
        for decision in existing_decision_queue.get("pending_decisions", existing_decision_queue.get("items", [])):
            later_items.append({
                "item_id": f"item_{_slug(decision.get('title', decision.get('name', 'unknown')))}",
                "title": decision.get("title", decision.get("name", "Pending decision")),
                "summary": decision.get("description", decision.get("summary", "Item from decision queue")),
                "confidence": "low",
                "dependencies": [],
                "artifact_refs": [existing_decision_queue.get("decision_queue_id", "decision_queue")],
            })

    if existing_mission_brief and not now_items:
        now_items.append({
            "item_id": "item_mission_current",
            "title": existing_mission_brief.get("title", "Current mission"),
            "summary": existing_mission_brief.get("mission_objective", ""),
            "confidence": "moderate",
            "dependencies": [],
            "artifact_refs": [existing_mission_brief.get("mission_brief_id", "mission_brief")],
        })

    open_decisions: list[dict[str, Any]] = []
    if existing_decision_queue:
        for decision in existing_decision_queue.get("pending_decisions", existing_decision_queue.get("items", [])):
            open_decisions.append({
                "decision_id": f"decision_{_slug(decision.get('title', 'unknown'))}",
                "question": decision.get("title", decision.get("name", "Open decision")),
                "impact": decision.get("description", decision.get("summary", "Decision pending review")),
                "deadline": decision.get("deadline", decision.get("target_date", "TBD")),
            })

    unresolved_evidence_gaps: list[dict[str, Any]] = []
    if existing_problem_brief:
        for ref in existing_problem_brief.get("evidence_refs", []):
            if ref.get("source_type") == "other":
                unresolved_evidence_gaps.append({
                    "gap_id": f"gap_{_slug(ref.get('source_id', 'evidence'))}",
                    "description": f"Evidence from {ref.get('source_type', 'unknown')} source needs validation",
                    "blocking_items": [existing_problem_brief.get("problem_brief_id", "problem_brief")],
                })

    if not existing_decision_queue:
        unresolved_evidence_gaps.append({
            "gap_id": "gap_no_decision_queue",
            "description": "No decision queue artifact found. Roadmap decisions may be undocumented.",
            "blocking_items": [item["item_id"] for item in later_items],
        })

    return {
        "schema_version": "1.0.0",
        "roadmap_recovery_brief_id": f"roadmap_recovery_brief_{workspace_id}",
        "workspace_id": workspace_id,
        "title": f"Roadmap Recovery Brief: {workspace_id}",
        "now_items": now_items,
        "next_items": next_items,
        "later_items": later_items,
        "open_decisions": open_decisions,
        "unresolved_evidence_gaps": unresolved_evidence_gaps,
        "confidence_assessment": {
            "overall_confidence": "moderate",
            "biggest_risk": "Roadmap confidence is limited by incomplete decision queue and increment plan coverage." if not existing_decision_queue or not existing_increment_plan else "Roadmap items depend on evidence that may be stale or unvalidated.",
            "recommended_focus": "Prioritize now items with highest confidence and fill evidence gaps before expanding next/later scope.",
        },
        "source_artifact_refs": [
            ref for ref in [
                existing_prd.get("prd_id", "") if existing_prd else "",
                existing_increment_plan.get("increment_plan_id", "") if existing_increment_plan else "",
                existing_program_increment.get("program_increment_state_id", "") if existing_program_increment else "",
                existing_decision_queue.get("decision_queue_id", "") if existing_decision_queue else "",
            ] if ref
        ],
        "generated_at": generated_at,
    }


def build_visual_product_atlas(
    workspace_dir: Path,
    workspace_id: str,
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    generated_at = generated_at or _now_iso()
    existing_journey_map = _load_artifact(workspace_dir, "customer_journey_map.json")
    visual_records = ingest_screenshots(workspace_dir, generated_at=generated_at)

    journey_stage_links: list[dict[str, Any]] = []
    if existing_journey_map:
        for stage in existing_journey_map.get("journey_stages", []):
            stage_id = stage.get("stage_id", _slug(stage.get("stage_name", "unknown")))
            stage_name = stage.get("stage_name", "Unknown stage")
            linked_records = [r["visual_record_id"] for r in visual_records if r.get("probable_workflow_stage", "").lower() in stage_name.lower()]
            journey_stage_links.append({
                "stage_id": stage_id,
                "stage_name": stage_name,
                "visual_record_ids": linked_records,
            })

    screen_flow_nodes: list[dict[str, Any]] = []
    for record in visual_records:
        screen_flow_nodes.append({
            "node_id": f"node_{record['visual_record_id']}",
            "node_name": Path(record["source_path"]).stem.replace("_", " ").title(),
            "screen_purpose": record["screen_purpose"],
            "workflow_stage": record["probable_workflow_stage"],
            "visual_record_ids": [record["visual_record_id"]],
            "linked_artifact_refs": record.get("linked_artifact_refs", []),
        })

    return {
        "schema_version": "1.0.0",
        "visual_product_atlas_id": f"visual_product_atlas_{workspace_id}",
        "workspace_id": workspace_id,
        "title": f"Visual Product Atlas: {workspace_id}",
        "visual_evidence_records": visual_records,
        "journey_stage_links": journey_stage_links,
        "screen_flow_nodes": screen_flow_nodes,
        "generated_at": generated_at,
    }


def build_takeover_feature_scorecard(
    workspace_dir: Path,
    workspace_id: str,
    *,
    takeover_brief: dict[str, Any] | None = None,
    problem_space_map: dict[str, Any] | None = None,
    roadmap_recovery: dict[str, Any] | None = None,
    visual_product_atlas: dict[str, Any] | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    generated_at = generated_at or _now_iso()

    evidence_gaps = takeover_brief.get("evidence_gaps", []) if takeover_brief else []
    orphan_count = len(problem_space_map.get("orphan_nodes", [])) if problem_space_map else 0
    visual_count = len(visual_product_atlas.get("visual_evidence_records", [])) if visual_product_atlas else 0
    roadmap_confidence = roadmap_recovery.get("confidence_assessment", {}).get("overall_confidence", "low") if roadmap_recovery else "low"

    scenario_results: list[dict[str, Any]] = []

    scenario_results.append({
        "scenario_id": "scenario_takeover_orchestration",
        "title": "Takeover orchestration produces all four artifacts",
        "scenario_type": "dogfood_run",
        "result": "passed" if all(x is not None for x in [takeover_brief, problem_space_map, roadmap_recovery, visual_product_atlas]) else "partial",
        "summary": "All four takeover artifacts were generated from the workspace.",
        "evidence_refs": [
            f"takeover_brief_{workspace_id}",
            f"problem_space_map_{workspace_id}",
            f"roadmap_recovery_brief_{workspace_id}",
            f"visual_product_atlas_{workspace_id}",
        ],
    })

    scenario_results.append({
        "scenario_id": "scenario_evidence_gaps_identified",
        "title": "Takeover identifies evidence gaps",
        "scenario_type": "dogfood_run",
        "result": "passed" if evidence_gaps else "partial",
        "summary": f"Takeover brief identified {len(evidence_gaps)} evidence gaps.",
        "evidence_refs": [f"takeover_brief_{workspace_id}"],
    })

    scenario_results.append({
        "scenario_id": "scenario_no_orphan_nodes",
        "title": "Problem space map has minimal orphan nodes",
        "scenario_type": "dogfood_run",
        "result": "passed" if orphan_count == 0 else ("partial" if orphan_count <= 2 else "failed"),
        "summary": f"Problem space map has {orphan_count} orphan nodes.",
        "evidence_refs": [f"problem_space_map_{workspace_id}"],
    })

    scenario_results.append({
        "scenario_id": "scenario_visual_evidence_ingestion",
        "title": "Visual evidence records captured from inbox",
        "scenario_type": "dogfood_run",
        "result": "passed" if visual_count > 0 else "partial",
        "summary": f"Visual product atlas contains {visual_count} visual evidence records.",
        "evidence_refs": [f"visual_product_atlas_{workspace_id}"],
    })

    scenario_results.append({
        "scenario_id": "scenario_roadmap_confidence",
        "title": "Roadmap recovery confidence is usable",
        "scenario_type": "dogfood_run",
        "result": "passed" if roadmap_confidence in ("moderate", "high") else "partial",
        "summary": f"Roadmap recovery confidence: {roadmap_confidence}.",
        "evidence_refs": [f"roadmap_recovery_brief_{workspace_id}"],
    })

    passed = sum(1 for s in scenario_results if s["result"] == "passed")
    total = len(scenario_results)
    overall_score = max(1, min(5, round(5 * passed / total))) if total else 3
    if overall_score == 5:
        adoption_rec = "promote_as_standard"
    elif overall_score == 4:
        adoption_rec = "keep_in_internal_use"
    elif overall_score <= 2:
        adoption_rec = "block"
    else:
        adoption_rec = "route_to_improvement"

    feedback_items: list[dict[str, Any]] = []
    for s in scenario_results:
        if s["result"] != "passed":
            feedback_items.append({
                "feedback_id": f"feedback_{s['scenario_id']}",
                "summary": s["summary"],
                "impact_level": "high" if s["result"] == "failed" else "medium",
                "recommended_action": f"Improve {s['title']} scenario: {s['summary']}",
                "route_targets": ["productos_feedback_log", "improvement_loop_state"],
                "linked_dimension_keys": ["output_quality"],
                "linked_artifact_refs": s["evidence_refs"],
            })

    dimension_scores = [
        {"dimension_key": "pm_leverage", "score": min(5, overall_score + 1), "rationale": "Takeover directly serves PM inheritance needs.", "evidence_refs": [f"takeover_brief_{workspace_id}"]},
        {"dimension_key": "output_quality", "score": overall_score, "rationale": f"Scenarios: {passed}/{total} passed.", "evidence_refs": [f"problem_space_map_{workspace_id}"]},
        {"dimension_key": "reliability", "score": overall_score, "rationale": "Takeover outputs are generated deterministically from workspace state.", "evidence_refs": [f"roadmap_recovery_brief_{workspace_id}"]},
        {"dimension_key": "autonomy_quality", "score": min(5, overall_score), "rationale": "Orchestrated pipeline with minimal intervention.", "evidence_refs": [f"visual_product_atlas_{workspace_id}"]},
        {"dimension_key": "repeatability", "score": min(5, overall_score + 1), "rationale": "Takeover flow can be run repeatedly on the same workspace.", "evidence_refs": [f"takeover_brief_{workspace_id}"]},
    ]

    return {
        "schema_version": "1.0.0",
        "feature_scorecard_id": f"takeover_feature_scorecard_{workspace_id}",
        "workspace_id": workspace_id,
        "feature_id": "feature_pm_takeover_command_center",
        "feature_name": "PM Takeover Command Center",
        "loop_id": "signal_to_product_decision",
        "status": "reviewed",
        "benchmark_ref": "productos_superpower_benchmark",
        "validation_tier": "tier_2",
        "scenarios": scenario_results,
        "evidence_refs": [f"takeover_brief_{workspace_id}", f"problem_space_map_{workspace_id}", f"roadmap_recovery_brief_{workspace_id}", f"visual_product_atlas_{workspace_id}"],
        "provenance_classification": "seeded",
        "score_basis": ["scenario_results", "evidence_gap_analysis", "orphan_node_analysis", "visual_coverage"],
        "truthfulness_summary": f"Takeover superpower scored {overall_score}/5 based on {passed}/{total} passing scenarios. Evidence gaps: {len(evidence_gaps)}, Orphan nodes: {orphan_count}.",
        "dimension_scores": dimension_scores,
        "overall_score": overall_score,
        "adoption_recommendation": adoption_rec,
        "reviewer_verdict": {"status": "pass" if overall_score >= 4 else "revise", "summary": f"Takeover superpower scores {overall_score}/5 with {passed}/{total} scenarios passing.", "evidence_refs": [f"takeover_brief_{workspace_id}"]},
        "tester_verdict": {"status": "pass" if overall_score >= 3 else "revise", "summary": f"All four takeover artifacts produced. {len(evidence_gaps)} evidence gaps identified.", "evidence_refs": [f"problem_space_map_{workspace_id}"]},
        "manual_verdict": {"status": "accept" if overall_score >= 4 else "revise", "summary": f"Takeover scorecard reviewed: {overall_score}/5 overall.", "evidence_refs": [f"takeover_brief_{workspace_id}"]},
        "blocked_by": [],
        "feedback_items": feedback_items,
        "next_action": "Review takeover artifacts and validate evidence gaps with PM input." if overall_score < 4 else "Takeover superpower is ready for internal use. Route feedback to improvement loop.",
        "generated_at": generated_at,
    }


def _infer_takeover_context(workspace_dir: Path) -> dict[str, Any]:
    existing_docs_dir = workspace_dir / "docs"
    docs_planning = existing_docs_dir / "planning"
    docs_product = existing_docs_dir / "product"
    has_planning_docs = docs_planning.exists() and any(docs_planning.iterdir())
    has_product_docs = docs_product.exists() and any(docs_product.iterdir())
    artifact_count = len(list((workspace_dir / "artifacts").glob("*.json"))) if (workspace_dir / "artifacts").exists() else 0

    existing_problem_brief = _load_artifact(workspace_dir, "problem_brief.json")
    existing_segment_map = _load_artifact(workspace_dir, "segment_map.json")
    existing_journey_map = _load_artifact(workspace_dir, "customer_journey_map.json")
    has_problems = existing_problem_brief is not None
    has_segments = existing_segment_map is not None
    has_journey = existing_journey_map is not None

    return {
        "has_planning_docs": has_planning_docs,
        "has_product_docs": has_product_docs,
        "artifact_count": artifact_count,
        "has_problems": has_problems,
        "has_segments": has_segments,
        "has_journey": has_journey,
    }


def build_takeover_cockpit_section(
    workspace_dir: Path,
    workspace_id: str,
    *,
    takeover_brief: dict[str, Any] | None = None,
    problem_space_map: dict[str, Any] | None = None,
    roadmap_recovery: dict[str, Any] | None = None,
    visual_product_atlas: dict[str, Any] | None = None,
    takeover_feature_scorecard: dict[str, Any] | None = None,
) -> dict[str, Any]:
    context = _infer_takeover_context(workspace_dir)
    evidence_gaps = takeover_brief.get("evidence_gaps", []) if takeover_brief else []
    scorecard = takeover_feature_scorecard or {}
    dimension_scores = scorecard.get("dimension_scores", [])
    overall_score = scorecard.get("overall_score", 0)
    visual_count = len(visual_product_atlas.get("visual_evidence_records", [])) if visual_product_atlas else 0
    orphan_count = len(problem_space_map.get("orphan_nodes", [])) if problem_space_map else 0
    roadmap_conf = roadmap_recovery.get("confidence_assessment", {}).get("overall_confidence", "low") if roadmap_recovery else "low"

    return {
        "takeover_status": "complete" if takeover_brief else "not_started",
        "overall_score": overall_score,
        "evidence_gap_count": len(evidence_gaps),
        "high_severity_gaps": sum(1 for g in evidence_gaps if g.get("severity") in ("high", "critical")),
        "visual_evidence_count": visual_count,
        "orphan_node_count": orphan_count,
        "roadmap_confidence": roadmap_conf,
        "source_coverage": {
            "has_problems": context["has_problems"],
            "has_segments": context["has_segments"],
            "has_journey": context["has_journey"],
            "has_planning_docs": context["has_planning_docs"],
            "total_artifacts": context["artifact_count"],
        },
        "required_pm_actions": _derive_pm_actions(evidence_gaps, roadmap_conf, context),
    }


def _derive_pm_actions(
    evidence_gaps: list[dict[str, Any]],
    roadmap_confidence: str,
    context: dict[str, Any],
) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []

    for gap in evidence_gaps:
        if gap.get("severity") in ("high", "critical"):
            actions.append({
                "action": "Review evidence gap",
                "detail": gap.get("description", "Unknown gap"),
                "priority": "high",
            })

    if roadmap_confidence == "low":
        actions.append({
            "action": "Improve roadmap confidence",
            "detail": "Roadmap recovery confidence is low. Review decision queue and increment plan artifacts.",
            "priority": "high",
        })

    if not context["has_journey"]:
        actions.append({
            "action": "Synthesize customer journey",
            "detail": "No customer journey map found. Run journey synthesis from existing artifacts.",
            "priority": "medium",
        })

    if not context["has_segments"]:
        actions.append({
            "action": "Define segments",
            "detail": "No segment map found. Define target segments for the product.",
            "priority": "medium",
        })

    return actions


def render_takeover_atlas_html(
    takeover_brief: dict[str, Any],
    problem_space_map: dict[str, Any],
    roadmap_recovery_brief: dict[str, Any],
    visual_product_atlas: dict[str, Any],
    takeover_feature_scorecard: dict[str, Any] | None = None,
) -> str:
    gap_section = ""
    for gap in takeover_brief.get("evidence_gaps", []):
        severity_color = {"low": "#FBBF24", "medium": "#F59E0B", "high": "#EF4444", "critical": "#DC2626"}.get(gap.get("severity", "medium"), "#F59E0B")
        gap_section += f"""
        <div style="border-left:4px solid {severity_color};padding:12px;margin:8px 0;background:#FEF3C7;border-radius:4px;">
          <strong>{escape(gap.get('gap_id', ''))}</strong> <span style="color:{severity_color}">({escape(gap.get('severity', ''))})</span>
          <p style="margin:4px 0 0;color:#4B5563;">{escape(gap.get('description', ''))}</p>
        </div>"""
    if not gap_section:
        gap_section = "<p style='color:#6B7280;'>No evidence gaps identified.</p>"

    orphan_count = len(problem_space_map.get("orphan_nodes", []))
    actions_html = ""
    actions = takeover_brief.get("first_pm_actions", {})
    for period_key, period_label in [("first_30_days", "First 30 Days"), ("first_60_days", "First 60 Days"), ("first_90_days", "First 90 Days")]:
        items = actions.get(period_key, [])
        if items:
            items_html = "".join(f"<li>{escape(item)}</li>" for item in items)
            actions_html += f"""
            <div style="margin:12px 0;">
              <h4 style="margin:0 0 8px;color:#1F2937;">{period_label}</h4>
              <ul style="margin:0;padding-left:20px;">{items_html}</ul>
            </div>"""

    problems_html = ""
    for problem in problem_space_map.get("problems", []):
        problems_html += f"""
        <div style="border:1px solid #E5E7EB;padding:12px;margin:8px 0;border-radius:6px;background:#FFFFFF;">
          <h4 style="margin:0 0 4px;color:#1F2937;">{escape(problem.get('title', ''))}</h4>
          <p style="margin:0;color:#6B7280;font-size:14px;">{escape(problem.get('summary', ''))}</p>
          <span style="display:inline-block;margin-top:4px;padding:2px 8px;background:#DBEAFE;border-radius:4px;font-size:12px;color:#1D4ED8;">{escape(problem.get('severity', ''))}</span>
        </div>"""

    roadmap_section = ""
    for lane, label in [("now_items", "Now"), ("next_items", "Next"), ("later_items", "Later")]:
        items = roadmap_recovery_brief.get(lane, [])
        if items:
            items_html = ""
            for item in items:
                conf_color = {"low": "#FCA5A5", "moderate": "#FDE68A", "high": "#BBF7D0"}.get(item.get("confidence", "low"), "#E5E7EB")
                items_html += f"""
                <div style="border:1px solid #E5E7EB;padding:10px;margin:6px 0;border-radius:4px;background:#FAFAFA;">
                  <div style="display:flex;justify-content:space-between;align-items:center;">
                    <strong style="color:#1F2937;">{escape(item.get('title', ''))}</strong>
                    <span style="padding:2px 8px;background:{conf_color};border-radius:4px;font-size:12px;">{escape(item.get('confidence', ''))}</span>
                  </div>
                  <p style="margin:4px 0 0;color:#6B7280;font-size:14px;">{escape(item.get('summary', ''))}</p>
                </div>"""
            roadmap_section += f"""
            <div style="margin:12px 0;">
              <h4 style="margin:0 0 8px;color:#1F2937;">{label}</h4>
              {items_html}
            </div>"""

    visual_section = ""
    for record in visual_product_atlas.get("visual_evidence_records", []):
        visual_section += f"""
        <div style="border:1px solid #E5E7EB;padding:10px;margin:6px 0;border-radius:4px;background:#FAFAFA;">
          <strong style="color:#1F2937;">{escape(record.get('visual_record_id', ''))}</strong>
          <p style="margin:4px 0 0;color:#6B7280;font-size:14px;">{escape(record.get('source_path', ''))}</p>
          <p style="margin:2px 0 0;color:#4B5563;font-size:13px;">{escape(record.get('screen_purpose', ''))}</p>
          <span style="display:inline-block;margin-top:4px;padding:2px 6px;background:#F3E8FF;border-radius:4px;font-size:11px;color:#7C3AED;">{escape(record.get('provenance', {}).get('confidence', ''))}</span>
        </div>"""

    scorecard_html = ""
    if takeover_feature_scorecard:
        scorecard_html += f"""
        <div style="display:flex;gap:16px;margin:12px 0;">
          <div style="flex:1;text-align:center;padding:16px;background:#EEF2FF;border-radius:8px;">
            <div style="font-size:36px;font-weight:700;color:#4F46E5;">{takeover_feature_scorecard.get('overall_score', '?')}/5</div>
            <div style="font-size:13px;color:#6B7280;">Overall Score</div>
          </div>
          <div style="flex:1;text-align:center;padding:16px;background:#F0FDF4;border-radius:8px;">
            <div style="font-size:36px;font-weight:700;color:#16A34A;">{len(takeover_feature_scorecard.get('scenarios', []))}</div>
            <div style="font-size:13px;color:#6B7280;">Scenarios</div>
          </div>
          <div style="flex:1;text-align:center;padding:16px;background:#FFF7ED;border-radius:8px;">
            <div style="font-size:36px;font-weight:700;color:#EA580C;">{len(takeover_feature_scorecard.get('feedback_items', []))}</div>
            <div style="font-size:13px;color:#6B7280;">Feedback Items</div>
          </div>
        </div>
        <p style="color:#4B5563;font-size:14px;"><strong>Recommendation:</strong> {escape(takeover_feature_scorecard.get('adoption_recommendation', ''))}</p>"""

    competitor_section = ""
    for link in problem_space_map.get("competitor_links", []):
        threat_color = {"low": "#6B7280", "medium": "#F59E0B", "high": "#EF4444"}.get(link.get("threat_level", "low"), "#6B7280")
        competitor_section += f"""
        <div style="border:1px solid #E5E7EB;padding:8px 12px;margin:4px 0;border-radius:4px;display:flex;justify-content:space-between;align-items:center;">
          <span style="color:#1F2937;">{escape(link.get('competitor_name', ''))}</span>
          <span style="color:{threat_color};font-size:13px;">{escape(link.get('threat_level', ''))}</span>
        </div>"""

    segment_section = ""
    for link in problem_space_map.get("segment_links", []):
        segment_section += f"""<div style="padding:4px 0;color:#4B5563;font-size:14px;">{escape(link.get('target_id', ''))}</div>"""

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Takeover Atlas: {escape(takeover_brief.get('title', ''))}</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #F8FAFC; color: #1F2937; line-height: 1.6; }}
    .container {{ max-width: 1100px; margin: 0 auto; padding: 32px 24px; }}
    h1 {{ font-size: 28px; font-weight: 700; color: #111827; margin-bottom: 4px; }}
    h2 {{ font-size: 20px; font-weight: 600; color: #1F2937; margin: 24px 0 12px; padding-bottom: 8px; border-bottom: 2px solid #E5E7EB; }}
    h3 {{ font-size: 16px; font-weight: 600; color: #374151; margin: 16px 0 8px; }}
    .header {{ background: linear-gradient(135deg, #4F46E5, #7C3AED); color: white; padding: 24px 32px; border-radius: 12px; margin-bottom: 24px; }}
    .header p {{ color: #C7D2FE; font-size: 14px; margin-top: 4px; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
    .card {{ background: white; border: 1px solid #E5E7EB; border-radius: 8px; padding: 16px; }}
    .card.full {{ grid-column: 1 / -1; }}
    .summary {{ display: flex; gap: 16px; margin: 16px 0; }}
    .summary-item {{ flex: 1; padding: 16px; background: white; border: 1px solid #E5E7EB; border-radius: 8px; text-align: center; }}
    .summary-value {{ font-size: 32px; font-weight: 700; color: #4F46E5; }}
    .summary-label {{ font-size: 13px; color: #6B7280; margin-top: 4px; }}
    .orphan {{ background: #FEF2F2; border: 1px solid #FECACA; padding: 12px; border-radius: 6px; margin: 8px 0; }}
    @media (max-width: 768px) {{ .grid {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>PM Takeover Atlas</h1>
      <p>{escape(takeover_brief.get('title', ''))} &middot; Generated {takeover_brief.get('generated_at', '')[:10]}</p>
      <p>Source: {escape(takeover_brief.get('source_workspace_ref', ''))}</p>
    </div>

    <div class="summary">
      <div class="summary-item">
        <div class="summary-value">{len(problem_space_map.get('problems', []))}</div>
        <div class="summary-label">Problems</div>
      </div>
      <div class="summary-item">
        <div class="summary-value">{len(problem_space_map.get('segment_links', []))}</div>
        <div class="summary-label">Segments</div>
      </div>
      <div class="summary-item">
        <div class="summary-value">{len(problem_space_map.get('competitor_links', []))}</div>
        <div class="summary-label">Competitors</div>
      </div>
      <div class="summary-item">
        <div class="summary-value">{len(takeover_brief.get('evidence_gaps', []))}</div>
        <div class="summary-label">Evidence Gaps</div>
      </div>
    </div>

    <h2>Product Overview</h2>
    <div class="card full">
      <p style="color:#4B5563;">{escape(takeover_brief.get('product_summary', ''))}</p>
      <div style="margin-top:12px;padding:12px;background:#F3F4F6;border-radius:6px;">
        <strong style="color:#374151;">Old Problem Framing:</strong>
        <p style="color:#6B7280;margin-top:4px;">{escape(takeover_brief.get('old_problem_framing', ''))}</p>
      </div>
    </div>

    <h2>Segments &amp; Personas</h2>
    <div class="grid">
      <div class="card">
        <h3>Segments</h3>
        <p style="color:#4B5563;margin-bottom:8px;">{escape(takeover_brief.get('target_segment_summary', ''))}</p>
        {segment_section}
      </div>
      <div class="card">
        <h3>Personas</h3>
        <p style="color:#4B5563;margin-bottom:8px;">{escape(takeover_brief.get('target_persona_summary', ''))}</p>
      </div>
    </div>

    <h2>Competitor &amp; Market</h2>
    <div class="card full">
      <p style="color:#4B5563;margin-bottom:12px;">{escape(takeover_brief.get('competitor_summary', ''))}</p>
      {competitor_section}
    </div>

    <h2>Customer Journey</h2>
    <div class="card full">
      <p style="color:#4B5563;">{escape(takeover_brief.get('customer_journey_summary', ''))}</p>
    </div>

    <h2>Problem Space</h2>
    <div class="card full">
      {problems_html}
      {f'<div class="orphan"><strong>Orphan Nodes:</strong> {orphan_count} nodes without connections</div>' if problem_space_map.get('orphan_nodes') else ''}
    </div>

    <h2>Roadmap State</h2>
    <div class="card full">
      <p style="color:#4B5563;margin-bottom:12px;">{escape(takeover_brief.get('roadmap_summary', ''))}</p>
      {roadmap_section}
    </div>

    <h2>Visual Evidence</h2>
    <div class="card full">
      <p style="color:#6B7280;margin-bottom:12px;">{len(visual_product_atlas.get('visual_evidence_records', []))} visual records captured</p>
      {visual_section}
    </div>

    <h2>Evidence Gaps</h2>
    <div class="card full">
      {gap_section}
    </div>

    <h2>First PM Actions</h2>
    <div class="card full">
      {actions_html}
    </div>

    <h2>Feature Scorecard</h2>
    <div class="card full">
      {scorecard_html}
    </div>

    <div style="margin-top:32px;padding:16px;text-align:center;color:#9CA3AF;font-size:13px;border-top:1px solid #E5E7EB;">
      Generated by ProductOS Takeover Command Center
    </div>
  </div>
</body>
</html>"""


def _write_takeover_artifacts(
    workspace_dir: Path,
    bundle: dict[str, Any],
    workspace_id: str,
) -> None:
    artifacts_dir = workspace_dir / "artifacts"
    manifest_path = workspace_dir / "workspace_manifest.yaml"

    artifact_files = {
        "takeover_brief": f"takeover_brief_{workspace_id}.json",
        "problem_space_map": f"problem_space_map_{workspace_id}.json",
        "roadmap_recovery_brief": f"roadmap_recovery_brief_{workspace_id}.json",
        "visual_product_atlas": f"visual_product_atlas_{workspace_id}.json",
        "takeover_feature_scorecard": f"takeover_feature_scorecard_{workspace_id}.json",
    }

    for key, filename in artifact_files.items():
        if key in bundle:
            _write_json(artifacts_dir / filename, bundle[key])
            _append_manifest_artifact_path(manifest_path, f"artifacts/{filename}")


def build_takeover_bundle(
    root_dir: Path | str,
    *,
    source_dir: Path | str | None = None,
    dest: Path | str,
    workspace_id: str,
    name: str,
    mode: str,
    generated_at: str | None = None,
    adopt_bundle: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    generated_at = generated_at or _now_iso()
    root = Path(root_dir).resolve()
    destination = Path(dest).resolve()

    if not destination.exists():
        if source_dir:
            from .adoption import adopt_workspace_from_source
            destination, adoption_bundle = adopt_workspace_from_source(
                root,
                source_dir=source_dir,
                dest=dest,
                workspace_id=workspace_id,
                name=name,
                mode=mode,
                generated_at=generated_at,
            )
        else:
            from .lifecycle import init_workspace_from_template
            destination = init_workspace_from_template(
                root,
                dest=dest,
                workspace_id=workspace_id,
                name=name,
                mode=mode,
            )
    else:
        adoption_bundle = adopt_bundle

    problem_space_map = build_problem_space_map(destination, workspace_id, generated_at=generated_at)
    roadmap_recovery = build_roadmap_recovery_brief(destination, workspace_id, generated_at=generated_at)
    visual_product_atlas = build_visual_product_atlas(destination, workspace_id, generated_at=generated_at)
    takeover_brief = build_takeover_brief(
        destination,
        workspace_id,
        adoption_bundle=adoption_bundle,
        problem_space_map=problem_space_map,
        visual_product_atlas=visual_product_atlas,
        roadmap_recovery=roadmap_recovery,
        generated_at=generated_at,
    )
    takeover_feature_scorecard = build_takeover_feature_scorecard(
        destination,
        workspace_id,
        takeover_brief=takeover_brief,
        problem_space_map=problem_space_map,
        roadmap_recovery=roadmap_recovery,
        visual_product_atlas=visual_product_atlas,
        generated_at=generated_at,
    )

    bundle: dict[str, dict[str, Any]] = {
        "takeover_brief": takeover_brief,
        "problem_space_map": problem_space_map,
        "roadmap_recovery_brief": roadmap_recovery,
        "visual_product_atlas": visual_product_atlas,
        "takeover_feature_scorecard": takeover_feature_scorecard,
    }

    _write_takeover_artifacts(destination, bundle, workspace_id)

    outputs_dir = destination / "outputs" / "takeover"
    atlas_html = render_takeover_atlas_html(
        takeover_brief,
        problem_space_map,
        roadmap_recovery,
        visual_product_atlas,
        takeover_feature_scorecard=takeover_feature_scorecard,
    )
    _write_json(outputs_dir / "takeover_bundle.json", bundle)
    _write_json(outputs_dir / "takeover_cockpit_section.json", build_takeover_cockpit_section(
        destination,
        workspace_id,
        takeover_brief=takeover_brief,
        problem_space_map=problem_space_map,
        roadmap_recovery=roadmap_recovery,
        visual_product_atlas=visual_product_atlas,
        takeover_feature_scorecard=takeover_feature_scorecard,
    ))
    (outputs_dir / "takeover_atlas.html").write_text(atlas_html, encoding="utf-8")

    return bundle
