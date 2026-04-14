from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

from components.presentation.python.productos_presentation import (
    build_evidence_pack,
    build_ppt_export_plan,
    build_presentation_story,
    build_publish_check,
    build_render_spec,
)
from .mission import build_discover_artifacts_from_mission
from .baseline import (
    build_foundation_bundle_from_workspace,
    build_market_intelligence_bundle_from_workspace,
)
from .release import evaluate_promotion_gate, external_research_gate_blockers


ROOT = Path(__file__).resolve().parents[3]
BASELINE_VERSION = "4.7.0"
CANDIDATE_VERSION = "4.8.0"
NEXT_VERSION_ARTIFACT_SCHEMAS: dict[str, str] = {
    "cockpit_state": "cockpit_state.schema.json",
    "orchestration_state": "orchestration_state.schema.json",
    "intake_routing_state": "intake_routing_state.schema.json",
    "memory_retrieval_state": "memory_retrieval_state.schema.json",
    "context_pack": "context_pack.schema.json",
    "autonomous_pm_swarm_plan": "autonomous_pm_swarm_plan.schema.json",
    "eval_suite_manifest": "eval_suite_manifest.schema.json",
    "eval_run_report": "eval_run_report.schema.json",
    "runtime_adapter_registry": "runtime_adapter_registry.schema.json",
    "adapter_parity_report": "runtime_scenario_report.schema.json",
    "market_refresh_report": "runtime_scenario_report.schema.json",
    "market_distribution_report": "runtime_scenario_report.schema.json",
    "next_version_release_gate_decision": "release_gate_decision.schema.json",
    "discover_problem_brief": "problem_brief.schema.json",
    "discover_concept_brief": "concept_brief.schema.json",
    "discover_prd": "prd.schema.json",
    "discover_execution_session_state": "execution_session_state.schema.json",
    "align_execution_session_state": "execution_session_state.schema.json",
    "align_document_sync_state": "document_sync_state.schema.json",
    "operate_execution_session_state": "execution_session_state.schema.json",
    "operate_status_mail": "status_mail.schema.json",
    "operate_issue_log": "issue_log.schema.json",
    "improve_execution_session_state": "execution_session_state.schema.json",
    "improve_improvement_loop_state": "improvement_loop_state.schema.json",
    "discover_feature_scorecard": "feature_scorecard.schema.json",
    "docs_alignment_feature_scorecard": "feature_scorecard.schema.json",
    "presentation_feature_scorecard": "feature_scorecard.schema.json",
    "weekly_pm_autopilot_feature_scorecard": "feature_scorecard.schema.json",
    "market_intelligence_feature_scorecard": "feature_scorecard.schema.json",
    "runtime_control_surface_feature_scorecard": "feature_scorecard.schema.json",
    "agent_adapter_feature_scorecard": "feature_scorecard.schema.json",
    "self_improvement_feature_scorecard": "feature_scorecard.schema.json",
    "autonomous_pm_swarm_feature_scorecard": "feature_scorecard.schema.json",
    "feature_portfolio_review": "feature_portfolio_review.schema.json",
}


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_persisted_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return _load_json(path)


def _artifact_path_with_archive_fallback(artifacts_dir: Path, filename: str) -> Path:
    return artifacts_dir / filename


def _relative_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return path.as_posix()


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _feedback_item(
    *,
    feedback_id: str,
    summary: str,
    impact_level: str,
    recommended_action: str,
    route_targets: list[str],
    linked_dimension_keys: list[str],
    linked_artifact_refs: list[str],
) -> dict[str, Any]:
    return {
        "feedback_id": feedback_id,
        "summary": summary,
        "impact_level": impact_level,
        "recommended_action": recommended_action,
        "route_targets": route_targets,
        "linked_dimension_keys": linked_dimension_keys,
        "linked_artifact_refs": linked_artifact_refs,
    }


def _quality_contract(
    *,
    audience: list[str],
    decision_needed: str,
    evidence: list[str],
    alternatives: list[str],
    recommendation: str,
    metrics: list[str],
    risks: list[str],
    owner: str,
    next_action: str,
) -> dict[str, Any]:
    return {
        "audience": audience,
        "decision_needed": decision_needed,
        "evidence": evidence,
        "alternatives": alternatives,
        "recommendation": recommendation,
        "metrics": metrics,
        "risks": risks,
        "owner": owner,
        "next_action": next_action,
    }


def _adapter_capability_profile(
    *,
    mission_routing: str,
    task_boundary_visibility: str,
    research_freshness: str,
    validation_enforcement: str,
    delegation_support: str,
    approval_gating: str,
    memory_steering: str,
    artifact_export: str,
) -> dict[str, str]:
    return {
        "mission_routing": mission_routing,
        "task_boundary_visibility": task_boundary_visibility,
        "research_freshness": research_freshness,
        "validation_enforcement": validation_enforcement,
        "delegation_support": delegation_support,
        "approval_gating": approval_gating,
        "memory_steering": memory_steering,
        "artifact_export": artifact_export,
    }


def _mission_control_boundary(
    *,
    mission_ref: str,
    mission_title: str,
    active_stage: str,
    current_route_ref: str,
    next_route_ref: str,
    current_task_name: str,
    current_task_summary: str,
    current_task_status: str,
    reviewer_lane: str,
) -> dict[str, str]:
    return {
        "mission_ref": mission_ref,
        "mission_title": mission_title,
        "active_stage": active_stage,
        "current_route_ref": current_route_ref,
        "next_route_ref": next_route_ref,
        "current_task_name": current_task_name,
        "current_task_summary": current_task_summary,
        "current_task_status": current_task_status,
        "reviewer_lane": reviewer_lane,
    }


def _default_mission_router() -> dict[str, Any]:
    return {
        "entry_phase": "discover",
        "phase_sequence": ["discover", "align", "operate", "improve"],
        "primary_reviewer_lane": "pm_builder",
        "routing_rationale": "Start every next-version mission in discover, then expand only when the prior phase stays reviewable and evidence-backed.",
        "stop_conditions": [
            "Stop if evidence freshness or provenance becomes unclear.",
            "Stop if the current phase output is not PM-reviewable.",
            "Stop before downstream release movement unless PM approval is explicit.",
        ],
    }


def _default_steering_context(workspace_path: Path) -> dict[str, Any]:
    return {
        "steering_refs": [
            _relative_path(workspace_path / "docs" / "planning" / "steering-context.md"),
            "core/docs/vendor-neutral-agent-harness-standard.md",
            "core/docs/ralph-loop-model.md",
        ],
        "operating_norms": [
            "Treat the repository as the system of record.",
            "Keep PM approval explicit for decision-driving scope and release movement.",
            "Preserve observed versus inferred claims when evidence is incomplete.",
            "Prefer the smallest coherent slice that can be validated end to end.",
        ],
        "memory_priority_order": [
            "decisions",
            "evidence",
            "prior_artifacts",
            "repeated_issues",
            "strategic_memory",
        ],
        "default_artifact_focus": [
            "mission_brief",
            "problem_brief",
            "concept_brief",
            "prd",
            "document_sync_state",
            "status_mail",
            "feature_portfolio_review",
        ],
    }


def _route_budget(
    *,
    max_parallel_routes: int,
    active_route_count: int,
    awaiting_review_count: int,
    blocked_route_count: int,
) -> dict[str, int]:
    return {
        "max_parallel_routes": max_parallel_routes,
        "active_route_count": active_route_count,
        "awaiting_review_count": awaiting_review_count,
        "blocked_route_count": blocked_route_count,
    }


def _build_eval_suite_manifest(
    *,
    workspace_id: str,
    generated_at: str,
) -> dict[str, Any]:
    case_templates = [
        (
            "signal_to_product_decision",
            "Discover truthfulness",
            "Check whether live discover outputs stay traceable and explicit about confidence.",
            ["traceable claims", "visible uncertainty", "fresh evidence"],
            ["problem_brief", "concept_brief", "prd"],
            5,
        ),
        (
            "decision_to_stakeholder_alignment",
            "Alignment traceability",
            "Check whether docs and presentation outputs preserve source truth and risk framing.",
            ["source-linked claims", "audience fit", "risk visibility"],
            ["document_sync_state", "presentation_brief"],
            4,
        ),
        (
            "feedback_to_accepted_improvement",
            "Improvement honesty",
            "Check whether the scoring loop exposes real gaps instead of auto-promoting the baseline.",
            ["sub-5 visibility", "bounded next action", "regression accounting"],
            ["feature_scorecard", "feature_portfolio_review"],
            5,
        ),
        (
            "cross_cutting",
            "Control-surface truth",
            "Check whether CLI summaries reflect provenance and eval risk instead of only green status.",
            ["truthfulness status", "eval visibility", "mixed provenance warning"],
            ["cockpit_state", "orchestration_state"],
            5,
        ),
        (
            "cross_cutting",
            "Decision memory retrieval",
            "Check whether rejected paths, tradeoffs, and follow-up reviews are recoverable.",
            ["decision recall", "tradeoff visibility", "follow-up dates"],
            ["decision_log", "strategic_memory_record", "outcome_review"],
            4,
        ),
    ]
    eval_cases = []
    for index, (loop_id, title, prompt_summary, success_signals, artifact_types, weight) in enumerate(case_templates, start=1):
        eval_cases.append(
            {
                "case_id": f"eval_case_{index:02d}",
                "title": title,
                "loop_id": loop_id,
                "prompt_summary": prompt_summary,
                "success_signals": success_signals,
                "required_artifact_types": artifact_types,
                "weight": weight,
            }
        )
    return {
        "schema_version": "1.0.0",
        "eval_suite_manifest_id": f"eval_suite_manifest_{workspace_id}_bounded_baseline",
        "workspace_id": workspace_id,
        "suite_name": "ProductOS frozen bounded-release eval suite",
        "baseline_version": BASELINE_VERSION,
        "candidate_version": CANDIDATE_VERSION,
        "locked_on": generated_at[:10],
        "owner": "ProductOS PM",
        "task_count": len(eval_cases),
        "eval_cases": eval_cases,
    }


def _build_eval_run_report(
    *,
    workspace_id: str,
    eval_suite_manifest: dict[str, Any],
    discover_scorecard: dict[str, Any],
    docs_alignment_scorecard: dict[str, Any],
    presentation_scorecard: dict[str, Any],
    runtime_control_surface_scorecard: dict[str, Any],
    self_improvement_scorecard: dict[str, Any],
    decision_log: dict[str, Any],
    strategic_memory: dict[str, Any],
    generated_at: str,
) -> dict[str, Any]:
    decision_entry = decision_log.get("decisions", [{}])[0] if decision_log.get("decisions") else {}
    decision_memory_fields = [
        "reversibility",
        "rejected_options",
        "key_tradeoffs",
        "kill_criteria",
        "followup_review_by",
    ]
    has_enriched_decision_memory = all(decision_entry.get(field) for field in decision_memory_fields)

    case_results = []
    for case in eval_suite_manifest["eval_cases"]:
        if case["loop_id"] == "signal_to_product_decision":
            outcome = "pass" if discover_scorecard["overall_score"] >= 4 else "warning"
            regression = False
            provenance = discover_scorecard["provenance_classification"]
            notes = (
                "Discover outputs stay strong, traceable, and explicitly bounded enough to clear the frozen internal-use truthfulness bar."
                if outcome == "pass"
                else "Discover outputs still need stronger traceability before they can clear the frozen truthfulness bar."
            )
            evidence_refs = [discover_scorecard["feature_scorecard_id"]]
        elif case["loop_id"] == "decision_to_stakeholder_alignment":
            alignment_is_healthy = (
                docs_alignment_scorecard["overall_score"] >= 4
                and presentation_scorecard["overall_score"] >= 4
            )
            outcome = "pass" if alignment_is_healthy else "warning"
            regression = False
            provenance = (
                "mixed"
                if "mixed"
                in {
                    docs_alignment_scorecard["provenance_classification"],
                    presentation_scorecard["provenance_classification"],
                }
                else "real"
            )
            notes = (
                "Docs and presentation preserve stakeholder-ready traceability, though the package still carries some mixed release provenance."
                if outcome == "pass"
                else "Alignment remains usable, but traceability or packaging quality is not yet consistently strong enough."
            )
            evidence_refs = [
                docs_alignment_scorecard["feature_scorecard_id"],
                presentation_scorecard["feature_scorecard_id"],
            ]
        elif case["title"] == "Improvement honesty":
            outcome = "pass" if self_improvement_scorecard["overall_score"] >= 4 else ("fail" if self_improvement_scorecard["overall_score"] <= 2 else "warning")
            regression = outcome == "fail"
            provenance = self_improvement_scorecard["provenance_classification"]
            notes = (
                "The scoring loop now stays grounded in frozen eval, decision-memory, validation, and release-gate evidence strongly enough to clear the internal-use honesty bar."
                if outcome == "pass"
                else (
                    "The scoring loop still cannot call the baseline healthy independently of the runtime that narrates it."
                    if outcome == "fail"
                    else "The scoring loop is improving and now consumes stronger release-gate inputs, but it still needs stronger eval independence before promotion."
                )
            )
            evidence_refs = [self_improvement_scorecard["feature_scorecard_id"]]
        elif case["title"] == "Control-surface truth":
            outcome = "pass" if runtime_control_surface_scorecard["overall_score"] >= 4 else ("fail" if runtime_control_surface_scorecard["overall_score"] <= 2 else "warning")
            regression = outcome == "fail"
            provenance = runtime_control_surface_scorecard["provenance_classification"]
            notes = (
                "The CLI now surfaces blocked promotion, eval pressure, and watch boundaries honestly enough to clear the frozen internal-use truth bar."
                if outcome == "pass"
                else (
                    "The CLI now surfaces blocked promotion honestly, but the control surface still carries mixed-provenance watch debt."
                    if outcome == "fail"
                    else "The control surface is no longer a hard fail, but it still has watch-level truthfulness debt."
                )
            )
            evidence_refs = [runtime_control_surface_scorecard["feature_scorecard_id"]]
        else:
            outcome = "pass" if has_enriched_decision_memory else "warning"
            regression = False
            provenance = "real"
            notes = (
                "Decision memory covers reversibility, rejected paths, tradeoffs, kill criteria, and follow-up dates."
                if outcome == "pass"
                else "Decision memory is reusable, but the richer release-memory fields are still not consistently present in the current decision log."
            )
            evidence_refs = [
                decision_log["decision_log_id"],
                strategic_memory["strategic_memory_record_id"],
            ]
        case_results.append(
            {
                "case_id": case["case_id"],
                "title": case["title"],
                "outcome": outcome,
                "regression": regression,
                "provenance_classification": provenance,
                "notes": notes,
                "evidence_refs": evidence_refs,
            }
        )

    failed_cases = sum(1 for item in case_results if item["outcome"] == "fail")
    warning_cases = sum(1 for item in case_results if item["outcome"] == "warning")
    passed_cases = sum(1 for item in case_results if item["outcome"] == "pass")
    regression_count = sum(1 for item in case_results if item["regression"])
    truthfulness_status = "watch" if regression_count else "healthy"
    status = "warning" if failed_cases or warning_cases else "passed"
    summary = (
        "The bounded baseline now reports the right blocked state, but control-surface and improvement-loop regressions still block stable promotion."
        if status != "passed"
        else "The bounded baseline clears the frozen eval suite and can promote its claims."
    )
    recommended_next_action = (
        "Keep the bundle in watch mode, fix self_improvement_loop first, and keep the truthful blocked-state control surface in place while rerunning the frozen eval suite."
        if status != "passed"
        else "Use the cleared bounded baseline to build the selected V5 lifecycle-traceability bundle and prepare the next stable extension."
    )
    return {
        "schema_version": "1.0.0",
        "eval_run_report_id": f"eval_run_report_{workspace_id}_bounded_baseline",
        "workspace_id": workspace_id,
        "eval_suite_manifest_id": eval_suite_manifest["eval_suite_manifest_id"],
        "baseline_version": BASELINE_VERSION,
        "candidate_version": CANDIDATE_VERSION,
        "status": status,
        "run_scope": "Bounded validation run for truthful control-surface, context, traceability, and decision-memory changes.",
        "summary": summary,
        "total_cases": len(case_results),
        "passed_cases": passed_cases,
        "warning_cases": warning_cases,
        "failed_cases": failed_cases,
        "regression_count": regression_count,
        "truthfulness_status": truthfulness_status,
        "case_results": case_results,
        "recommended_next_action": recommended_next_action,
        "generated_at": generated_at,
    }


def _scorecard(
    *,
    workspace_id: str,
    feature_id: str,
    feature_name: str,
    loop_id: str,
    benchmark_ref: str,
    validation_tier: str,
    overall_score: int,
    scenarios: list[dict[str, Any]],
    evidence_refs: list[str],
    provenance_classification: str,
    score_basis: list[str],
    truthfulness_summary: str,
    context_pack_ref: str,
    eval_run_ref: str,
    dimension_scores: list[dict[str, Any]],
    reviewer_status: str,
    reviewer_summary: str,
    tester_status: str,
    tester_summary: str,
    manual_status: str,
    manual_summary: str,
    blocked_by: list[str],
    feedback_items: list[dict[str, Any]],
    next_action: str,
    generated_at: str,
) -> dict[str, Any]:
    if overall_score == 5:
        adoption_recommendation = "promote_as_standard"
    elif overall_score == 4:
        adoption_recommendation = "keep_in_internal_use"
    elif overall_score <= 2 and blocked_by:
        adoption_recommendation = "block"
    else:
        adoption_recommendation = "route_to_improvement"

    return {
        "schema_version": "1.0.0",
        "feature_scorecard_id": f"feature_scorecard_{workspace_id}_{feature_id}",
        "workspace_id": workspace_id,
        "feature_id": feature_id,
        "feature_name": feature_name,
        "loop_id": loop_id,
        "status": "reviewed",
        "benchmark_ref": benchmark_ref,
        "validation_tier": validation_tier,
        "scenarios": scenarios,
        "evidence_refs": evidence_refs,
        "provenance_classification": provenance_classification,
        "score_basis": score_basis,
        "truthfulness_summary": truthfulness_summary,
        "context_pack_ref": context_pack_ref,
        "eval_run_ref": eval_run_ref,
        "dimension_scores": dimension_scores,
        "overall_score": overall_score,
        "adoption_recommendation": adoption_recommendation,
        "reviewer_verdict": {
            "status": reviewer_status,
            "summary": reviewer_summary,
            "evidence_refs": evidence_refs[:2] or evidence_refs,
        },
        "tester_verdict": {
            "status": tester_status,
            "summary": tester_summary,
            "evidence_refs": evidence_refs[:2] or evidence_refs,
        },
        "manual_verdict": {
            "status": manual_status,
            "summary": manual_summary,
            "evidence_refs": evidence_refs[-2:] or evidence_refs,
        },
        "blocked_by": blocked_by,
        "feedback_items": feedback_items,
        "next_action": next_action,
        "generated_at": generated_at,
    }


def _session_state(
    *,
    session_id: str,
    workspace_id: str,
    session_name: str,
    status: str,
    objective: str,
    owner_agent: str,
    capability_adapter_id: str,
    parent_orchestration_state_id: str,
    input_refs: list[str],
    output_refs: list[str],
    review_required: bool,
    verification_status: str,
    created_at: str,
    event_messages: list[tuple[str, str]],
) -> dict[str, Any]:
    session_state = {
        "schema_version": "1.0.0",
        "execution_session_state_id": session_id,
        "workspace_id": workspace_id,
        "session_name": session_name,
        "session_type": "analysis_session",
        "status": status,
        "objective": objective,
        "owner_agent": owner_agent,
        "capability_adapter_id": capability_adapter_id,
        "host_session_ref": f"{session_id}_host",
        "parent_orchestration_state_id": parent_orchestration_state_id,
        "source_workflow_state_id": "wf_next_version_superpower_ops",
        "review_required": review_required,
        "verification_status": verification_status,
        "input_refs": input_refs,
        "output_refs": output_refs,
        "blocking_reasons": [],
        "event_log": [
            {
                "timestamp": created_at,
                "event_type": event_type,
                "message": message,
            }
            for event_type, message in event_messages
        ],
        "created_at": created_at,
        "updated_at": created_at,
    }
    if status == "completed":
        session_state["completed_at"] = created_at
    return session_state


def _collect_inbox_items(workspace_path: Path, generated_at: str) -> list[dict[str, Any]]:
    workflow_map = {
        "raw-notes": (
            "raw_note",
            ["wf_inbox_to_normalized_evidence", "wf_research_command_center", "wf_problem_brief_to_prd"],
            [
                "problem_brief_productos_next_version_discover",
                "concept_brief_productos_next_version_discover",
            ],
        ),
        "transcripts": (
            "transcript",
            ["wf_transcript_to_notes", "wf_research_command_center", "wf_problem_brief_to_prd"],
            [
                "concept_brief_productos_next_version_discover",
                "prd_productos_next_version_discover",
            ],
        ),
        "documents": (
            "document",
            ["wf_inbox_to_normalized_evidence", "wf_artifact_to_readable_doc"],
            ["document_sync_state_ws_productos_v2_v4_readable_docs"],
        ),
        "support-exports": (
            "support_export",
            ["wf_productos_feedback_triage", "wf_bounded_improvement"],
            ["feedback_cluster_state_ws_productos_v2_runtime"],
        ),
    }

    intake_items: list[dict[str, Any]] = []
    for folder_name, (input_type, workflow_ids, derived_ids) in workflow_map.items():
        folder = workspace_path / "inbox" / folder_name
        if not folder.exists():
            continue
        for path in sorted(folder.iterdir()):
            if not path.is_file() or path.name == "README.md":
                continue
            item_id = f"inbox_{folder_name.replace('-', '_')}_{_slug(path.stem)}"
            excerpt = path.read_text(encoding="utf-8").strip().splitlines()[0][:120]
            intake_items.append(
                {
                    "item_id": item_id,
                    "inbox_path": _relative_path(path),
                    "input_type": input_type,
                    "captured_at": generated_at,
                    "provenance_status": "complete",
                    "normalization_status": "routed",
                    "recommended_workflow_ids": workflow_ids,
                    "derived_artifact_ids": derived_ids,
                    "notes": f"Captured for next-version dogfood routing: {excerpt}",
                }
            )
    return intake_items


def _build_live_discover_artifacts(
    workspace_path: Path,
    *,
    workspace_id: str,
    generated_at: str,
    mission_brief: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    raw_note_path = workspace_path / "inbox" / "raw-notes" / "2026-03-22-next-version-superpowers.md"
    transcript_path = workspace_path / "inbox" / "transcripts" / "2026-03-22-dogfood-next-version-session.txt"

    if (not raw_note_path.exists() or not transcript_path.exists()) and mission_brief is not None:
        return _build_mission_discover_artifacts(
            workspace_id=workspace_id,
            generated_at=generated_at,
            mission_brief=mission_brief,
        )
    if not raw_note_path.exists() or not transcript_path.exists():
        raise FileNotFoundError(
            "Discover fallback inputs are missing. Provide the self-hosting discover inputs or a mission_brief artifact."
        )

    raw_note_headline = raw_note_path.read_text(encoding="utf-8").strip().splitlines()[0]
    transcript_excerpt = transcript_path.read_text(encoding="utf-8").strip().splitlines()[1]

    problem_brief = {
        "schema_version": "1.0.0",
        "problem_brief_id": "problem_brief_productos_next_version_discover",
        "workspace_id": workspace_id,
        "title": "Problem Brief: ProductOS next-version discover proof",
        "problem_summary": (
            "ProductOS cannot credibly claim the next version until the repo turns messy notes and transcripts "
            "into a same-day, decision-ready PRD package with minimal PM reconstruction."
        ),
        "strategic_fit_summary": (
            "This problem fits a challenger posture because ProductOS can win by proving repo-first discover quality "
            "and PM trust faster than broader PM workflow systems."
        ),
        "posture_alignment": "challenger",
        "why_this_problem_now": (
            "The next version must prove a concrete discover wedge inside the self-hosting workspace before broader "
            "strategy claims are credible."
        ),
        "why_this_problem_for_this_segment": (
            "B2B product teams feel the cost of reconstructing context across messy notes, transcripts, and recurring "
            "PM workflows often enough to value a tighter discover control surface."
        ),
        "target_segment_refs": [
            {"entity_type": "segment", "entity_id": "segment_b2b_product_teams"}
        ],
        "target_persona_refs": [
            {"entity_type": "persona", "entity_id": "persona_product_manager"}
        ],
        "linked_entity_refs": [
            {"entity_type": "problem", "entity_id": "problem_productos_next_version_proof_gap"},
            {"entity_type": "outcome", "entity_id": "outcome_productos_same_day_prd_package"},
            {"entity_type": "opportunity", "entity_id": "opportunity_productos_discover_superpower"},
            {"entity_type": "feature", "entity_id": "feature_productos_repo_first_discover_cli"},
        ],
        "evidence_refs": [
            {
                "source_type": "other",
                "source_id": _relative_path(raw_note_path),
                "justification": f"The raw notes lock the must-win discover wedge and repo-first constraint: {raw_note_headline}",
            },
            {
                "source_type": "transcript",
                "source_id": _relative_path(transcript_path),
                "justification": (
                    "The transcript makes the release bar explicit: "
                    f"{transcript_excerpt}"
                ),
            },
        ],
        "upstream_artifact_ids": [
            "idea_record_pm_status_automation",
            "market_strategy_brief_pm_ops_challenger",
        ],
        "recommended_next_step": "prd",
        "created_at": generated_at,
    }

    concept_brief = {
        "schema_version": "1.0.0",
        "concept_brief_id": "concept_brief_productos_next_version_discover",
        "workspace_id": workspace_id,
        "title": "ProductOS next-version discover superpower",
        "hypothesis": (
            "If ProductOS routes live notes and transcripts through one repo-native CLI path, one PM can move "
            "from messy input to a reviewable PRD package in the same working day with no more than one material rewrite."
        ),
        "positioning_hypothesis": (
            "ProductOS will win as a trusted repo-first discover operating layer rather than a generic drafting wrapper."
        ),
        "offering_hypothesis": (
            "The offering should behave like a discover control surface that turns raw notes into validated PM artifacts."
        ),
        "wedge_hypothesis": (
            "Same-day messy-input-to-PRD conversion is the sharpest believable challenger wedge for the next-version discover path."
        ),
        "why_now": (
            "The next version is only believable if ProductOS proves its strongest loop inside the current self-hosting workspace."
        ),
        "why_us": (
            "ProductOS already has structured artifacts, validation lanes, readable docs, and a thin adapter contract inside the repo."
        ),
        "advantage_hypothesis": (
            "A repo-first control surface plus governed scoring can make discover automation trustworthy enough to promote as the current standard."
        ),
        "status": "validated",
        "idea_record_ids": ["idea_record_pm_status_automation"],
        "strategy_artifact_ids": ["market_strategy_brief_pm_ops_challenger"],
        "target_segment_refs": [
            {"entity_type": "segment", "entity_id": "segment_b2b_product_teams"}
        ],
        "target_persona_refs": [
            {"entity_type": "persona", "entity_id": "persona_product_manager"}
        ],
        "linked_entity_refs": [
            {"entity_type": "problem", "entity_id": "problem_productos_next_version_proof_gap"},
            {"entity_type": "outcome", "entity_id": "outcome_productos_same_day_prd_package"},
            {"entity_type": "opportunity", "entity_id": "opportunity_productos_discover_superpower"},
            {"entity_type": "feature", "entity_id": "feature_productos_repo_first_discover_cli"},
        ],
        "must_be_true_assumptions": [
            "One PM can review the generated bundle with no more than one material rewrite",
            "Repo-native validation and structured artifacts are enough to make the discover output trustworthy"
        ],
        "open_questions": [
            "How much of the weekly operating loop can reuse this discover control surface without adding review noise?"
        ],
        "uncertainty_map_refs": [
            "uncertainty_map_pm_strategy"
        ],
        "created_at": generated_at,
    }

    prd = {
        "schema_version": "1.0.0",
        "prd_id": "prd_productos_next_version_discover",
        "workspace_id": workspace_id,
        "title": "PRD: ProductOS next-version discover superpower",
        "problem_summary": problem_brief["problem_summary"],
        "outcome_summary": (
            "Enable one PM to move from messy notes and transcripts to a same-day, reviewable PRD package with at most one material rewrite."
        ),
        "scope_summary": (
            "Ingest live notes and transcripts, generate the next-version problem brief, concept brief, and PRD through the `productos` CLI, "
            "then score the slice and route the next priority into the improvement loop."
        ),
        "target_segment_refs": problem_brief["target_segment_refs"],
        "target_persona_refs": problem_brief["target_persona_refs"],
        "linked_entity_refs": concept_brief["linked_entity_refs"],
        "upstream_artifact_ids": [
            problem_brief["problem_brief_id"],
            concept_brief["concept_brief_id"],
        ],
        "generated_at": generated_at,
    }

    return problem_brief, concept_brief, prd


def _build_mission_discover_artifacts(
    *,
    workspace_id: str,
    generated_at: str,
    mission_brief: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    return build_discover_artifacts_from_mission(
        workspace_id=workspace_id,
        generated_at=generated_at,
        mission_brief=mission_brief,
    )


def _load_or_build_workspace_discover_artifacts(
    workspace_path: Path,
    *,
    workspace_id: str,
    generated_at: str,
    mission_brief: dict[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    artifacts_dir = workspace_path / "artifacts"
    problem_brief = _load_persisted_json(artifacts_dir / "problem_brief.json")
    concept_brief = _load_persisted_json(artifacts_dir / "concept_brief.json")
    prd = _load_persisted_json(artifacts_dir / "prd.json")
    if problem_brief and concept_brief and prd:
        return problem_brief, concept_brief, prd
    if mission_brief is not None:
        return _build_mission_discover_artifacts(
            workspace_id=workspace_id,
            generated_at=generated_at,
            mission_brief=mission_brief,
        )
    missing = [
        filename
        for filename, payload in {
            "problem_brief.json": problem_brief,
            "concept_brief.json": concept_brief,
            "prd.json": prd,
        }.items()
        if payload is None
    ]
    raise FileNotFoundError(
        f"Workspace is missing required discover artifacts: {', '.join(missing)}"
    )


def _load_persisted_discover_artifacts(workspace_path: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]] | None:
    output_dir = workspace_path / "outputs" / "discover"
    problem_brief = _load_persisted_json(output_dir / "discover_problem_brief.json")
    concept_brief = _load_persisted_json(output_dir / "discover_concept_brief.json")
    prd = _load_persisted_json(output_dir / "discover_prd.json")
    if not (problem_brief and concept_brief and prd):
        return None
    return problem_brief, concept_brief, prd


def _load_persisted_operate_artifacts(workspace_path: Path) -> tuple[dict[str, Any], dict[str, Any]] | None:
    output_dir = workspace_path / "outputs" / "operate"
    status_mail = _load_persisted_json(output_dir / "operate_status_mail.json")
    issue_log = _load_persisted_json(output_dir / "operate_issue_log.json")
    if not (status_mail and issue_log):
        return None
    return status_mail, issue_log


def _load_persisted_improve_artifacts(workspace_path: Path) -> dict[str, dict[str, Any]] | None:
    output_dir = workspace_path / "outputs" / "improve"
    improvement_loop_state = _load_persisted_json(output_dir / "improve_improvement_loop_state.json")
    eval_run_report = _load_persisted_json(output_dir / "eval_run_report.json")
    feature_portfolio_review = _load_persisted_json(output_dir / "feature_portfolio_review.json")
    release_gate_decision = _load_persisted_json(output_dir / "next_version_release_gate_decision.json")
    if not (improvement_loop_state and eval_run_report and feature_portfolio_review and release_gate_decision):
        return None
    return {
        "improvement_loop_state": improvement_loop_state,
        "eval_run_report": eval_run_report,
        "feature_portfolio_review": feature_portfolio_review,
        "release_gate_decision": release_gate_decision,
    }


def _load_persisted_presentation_artifacts(workspace_path: Path) -> dict[str, dict[str, Any]] | None:
    output_dir = workspace_path / "outputs" / "align"
    presentation_brief = _load_persisted_json(output_dir / "presentation_brief.json")
    presentation_evidence_pack = _load_persisted_json(output_dir / "presentation_evidence_pack.json")
    presentation_story = _load_persisted_json(output_dir / "presentation_story.json")
    presentation_render_spec = _load_persisted_json(output_dir / "presentation_render_spec.json")
    presentation_publish_check = _load_persisted_json(output_dir / "presentation_publish_check.json")
    presentation_ppt_export_plan = _load_persisted_json(output_dir / "presentation_ppt_export_plan.json")
    if not (
        presentation_brief
        and presentation_evidence_pack
        and presentation_story
        and presentation_render_spec
        and presentation_publish_check
        and presentation_ppt_export_plan
    ):
        return None
    return {
        "presentation_brief": presentation_brief,
        "presentation_evidence_pack": presentation_evidence_pack,
        "presentation_story": presentation_story,
        "presentation_render_spec": presentation_render_spec,
        "presentation_publish_check": presentation_publish_check,
        "presentation_ppt_export_plan": presentation_ppt_export_plan,
    }


def _augment_presentation_brief_with_workspace_research(
    presentation_brief: dict[str, Any],
    *,
    research_brief: dict[str, Any] | None,
    problem_brief: dict[str, Any] | None,
) -> dict[str, Any]:
    if research_brief is None and problem_brief is None:
        return presentation_brief

    enriched = copy.deepcopy(presentation_brief)
    known_gaps = list(enriched.get("known_gaps", []))
    external_research_questions = list(enriched.get("external_research_questions", []))
    contradiction_summaries = list(enriched.get("contradiction_summaries", []))
    source_material_snapshots = list(enriched.get("source_material_snapshots", []))

    if research_brief is not None:
        known_gaps.extend(research_brief.get("known_gaps", []))
        external_research_questions.extend(
            item["question"] for item in research_brief.get("external_research_questions", [])
        )
        research_facts = []
        for insight in research_brief.get("insights", []):
            research_facts.append(
                {
                    "fact_id": insight["insight_id"],
                    "fact_type": "observation",
                    "statement": insight["statement"],
                    "claim_mode": insight.get("claim_mode", "observed"),
                    "validation_note": insight.get("next_validation_step", ""),
                    "relevance_tags": ["summary", "evidence", "research"],
                }
            )
        for index, contradiction in enumerate(research_brief.get("contradictions", []), start=1):
            contradiction_summaries.append(contradiction["statement"])
            research_facts.append(
                {
                    "fact_id": f"{research_brief['research_brief_id']}_contradiction_{index}",
                    "fact_type": "risk",
                    "statement": contradiction["statement"],
                    "claim_mode": "observed",
                    "validation_note": "Keep this contradiction visible in stakeholder communication until PM review resolves the posture.",
                    "relevance_tags": ["risk", "governance", "research"],
                }
            )
        if research_facts:
            source_material_snapshots.append(
                {
                    "artifact_id": research_brief["research_brief_id"],
                    "artifact_type": "research_brief",
                    "facts": research_facts,
                }
            )

    if problem_brief is not None:
        source_material_snapshots.append(
            {
                "artifact_id": problem_brief["problem_brief_id"],
                "artifact_type": "problem_brief",
                "facts": [
                    {
                        "fact_id": f"{problem_brief['problem_brief_id']}_problem_summary",
                        "fact_type": "observation",
                        "statement": problem_brief["problem_summary"],
                        "claim_mode": "observed",
                        "validation_note": "Keep this problem framing aligned with the current research brief and PM review state.",
                        "relevance_tags": ["summary", "recommendation", "problem"],
                    },
                    {
                        "fact_id": f"{problem_brief['problem_brief_id']}_why_now",
                        "fact_type": "constraint",
                        "statement": problem_brief["why_this_problem_now"],
                        "claim_mode": "observed",
                        "validation_note": "Use this as the timing rationale, but keep proof gaps visible when presenting urgency.",
                        "relevance_tags": ["risk", "timeline", "problem"],
                    },
                ],
            }
        )

    enriched["known_gaps"] = list(dict.fromkeys(known_gaps))
    enriched["external_research_questions"] = list(dict.fromkeys(external_research_questions))
    enriched["contradiction_summaries"] = list(dict.fromkeys(contradiction_summaries))
    enriched["source_material_snapshots"] = source_material_snapshots
    return enriched


def _augment_presentation_brief_with_mission(
    presentation_brief: dict[str, Any],
    *,
    mission_brief: dict[str, Any] | None,
) -> dict[str, Any]:
    if mission_brief is None:
        return presentation_brief

    enriched = copy.deepcopy(presentation_brief)
    mission_title = mission_brief["title"]
    mission_problem = mission_brief["customer_problem"]
    mission_goal = mission_brief["business_goal"]
    mission_id = mission_brief["mission_brief_id"]
    source_artifact_ids = list(enriched.get("source_artifact_ids", []))
    source_material_snapshots = list(enriched.get("source_material_snapshots", []))
    known_gaps = list(enriched.get("known_gaps", []))
    non_negotiables = list(enriched.get("non_negotiables", []))
    required_objections = list(enriched.get("required_objections", []))

    enriched["objective"] = (
        f"{enriched['objective']} Keep the mission '{mission_title}' explicit while packaging the aligned recommendation."
    )
    enriched["narrative_goal"] = (
        f"{enriched['narrative_goal']} Show how the mission '{mission_title}' ties customer pain to the current aligned recommendation."
    )
    enriched["success_outcome"] = (
        f"{enriched['success_outcome']} The audience should also understand how this package advances the mission '{mission_title}'."
    )
    source_artifact_ids.append(mission_id)
    known_gaps.append(
        f"Keep the mission '{mission_title}' visible across docs and deck so PM intent does not get flattened into generic release narration."
    )
    required_objections.append(
        f"How does this aligned package specifically advance the mission '{mission_title}'?"
    )
    non_negotiables.append(
        f"Do not let presentation polish obscure the mission-specific customer problem: {mission_problem}"
    )
    source_material_snapshots.append(
        {
            "artifact_id": mission_id,
            "artifact_type": "mission_brief",
            "facts": [
                {
                    "fact_id": f"fact_{_slug(mission_title)}_mission_problem",
                    "fact_type": "constraint",
                    "statement": mission_problem,
                    "claim_mode": "observed",
                    "validation_note": "Taken directly from the canonical mission brief.",
                    "relevance_tags": ["cover", "recommendation", "mission"],
                },
                {
                    "fact_id": f"fact_{_slug(mission_title)}_business_goal",
                    "fact_type": "decision",
                    "statement": mission_goal,
                    "claim_mode": "observed",
                    "validation_note": "Taken directly from the canonical mission brief.",
                    "relevance_tags": ["summary", "decision", "mission"],
                },
            ],
        }
    )
    enriched["source_artifact_ids"] = list(dict.fromkeys(source_artifact_ids))
    enriched["known_gaps"] = list(dict.fromkeys(known_gaps))
    enriched["required_objections"] = list(dict.fromkeys(required_objections))
    enriched["non_negotiables"] = list(dict.fromkeys(non_negotiables))
    enriched["source_material_snapshots"] = source_material_snapshots
    return enriched


def _augment_document_sync_state_with_mission(
    document_sync_state: dict[str, Any],
    *,
    mission_brief: dict[str, Any] | None,
) -> dict[str, Any]:
    if mission_brief is None:
        return document_sync_state

    enriched = copy.deepcopy(document_sync_state)
    mission_id = mission_brief["mission_brief_id"]
    mission_title = mission_brief["title"]
    mission_problem = mission_brief["customer_problem"]
    mission_goal = mission_brief["business_goal"]
    enriched["source_artifact_refs"] = list(dict.fromkeys([*enriched["source_artifact_refs"], mission_id]))
    enriched["drift_summary"] = (
        f"{enriched['drift_summary']} The sync bundle must also preserve the mission '{mission_title}' across product and messaging docs."
    )
    enriched["review_requirements"] = list(
        dict.fromkeys(
            [
                *enriched["review_requirements"],
                f"Confirm the docs still reflect the mission '{mission_title}' and its customer problem without flattening it into generic positioning.",
            ]
        )
    )
    enriched["next_action"] = (
        f"{enriched['next_action']} Keep the mission '{mission_title}' explicit in the synced docs and messaging bundle."
    )
    updated_documents: list[dict[str, Any]] = []
    for document in enriched["documents"]:
        updated_document = copy.deepcopy(document)
        if mission_id not in updated_document["source_artifact_refs"]:
            updated_document["source_artifact_refs"].append(mission_id)
        if updated_document["doc_key"] in {"product_overview", "getting_started", "positioning", "messaging_house"}:
            updated_document["last_sync_status"] = (
                f"{updated_document['last_sync_status']} The current sync also preserves the mission '{mission_title}' "
                f"and its business goal: {mission_goal}"
            )
        updated_documents.append(updated_document)
    enriched["documents"] = updated_documents
    return enriched


def _augment_status_mail_with_mission(
    status_mail: dict[str, Any],
    *,
    mission_brief: dict[str, Any] | None,
) -> dict[str, Any]:
    if mission_brief is None:
        return status_mail

    enriched = copy.deepcopy(status_mail)
    mission_id = mission_brief["mission_brief_id"]
    mission_title = mission_brief["title"]
    mission_problem = mission_brief["customer_problem"]
    mission_goal = mission_brief["business_goal"]
    enriched["summary"] = (
        f"{enriched.get('summary', '')} The current operator cycle also stays anchored to the mission '{mission_title}'."
    ).strip()
    enriched["what_happened"] = list(
        dict.fromkeys(
            [
                *enriched["what_happened"],
                f"Kept the mission '{mission_title}' visible while routing aligned execution and review work.",
            ]
        )
    )
    enriched["next_steps"] = list(enriched["next_steps"])
    enriched["next_steps"].append(
        {
            "description": f"Confirm the next aligned and operating outputs still advance the mission '{mission_title}'.",
            "owner": "ProductOS PM",
            "target_date": enriched["reporting_period"]["end_date"],
        }
    )
    enriched["pm_context_requested"] = list(
        dict.fromkeys(
            [
                *enriched.get("pm_context_requested", []),
                f"Are the current outputs still directly addressing the mission problem: {mission_problem}?",
                f"What is the next highest-leverage move to achieve this business goal: {mission_goal}?",
            ]
        )
    )
    enriched["generated_from_artifact_ids"] = list(
        dict.fromkeys([*enriched.get("generated_from_artifact_ids", []), mission_id])
    )
    return enriched


def _augment_issue_log_with_mission(
    issue_log: dict[str, Any],
    *,
    mission_brief: dict[str, Any] | None,
) -> dict[str, Any]:
    if mission_brief is None:
        return issue_log

    enriched = copy.deepcopy(issue_log)
    mission_slug = _slug(mission_brief["title"])
    mission_title = mission_brief["title"]
    enriched["period_label"] = f"{enriched['period_label']} for {mission_title}"
    existing_issue_ids = {issue["issue_id"] for issue in enriched["issues"]}
    mission_issue_id = f"issue_{mission_slug}_mission_traceability"
    if mission_issue_id not in existing_issue_ids:
        enriched["issues"].append(
            {
                "issue_id": mission_issue_id,
                "title": f"Mission traceability for '{mission_title}' must stay explicit across aligned docs and operating outputs",
                "category": "product",
                "severity": "medium",
                "owner": "ProductOS PM",
                "status": "watch",
                "mitigation": "Keep the mission brief in the source chain for docs, deck, status, and issue routing until downstream traceability is routine.",
                "due_date": issue_log["updated_at"][:10],
            }
        )
    return enriched


def build_next_version_bundle_from_workspace(
    workspace_dir: Path | str,
    *,
    generated_at: str,
    adapter_name: str = "codex",
) -> dict[str, Any]:
    workspace_path = Path(workspace_dir).resolve()
    artifacts_dir = workspace_path / "artifacts"

    foundation_bundle = build_foundation_bundle_from_workspace(
        workspace_path,
        generated_at=generated_at,
    )
    market_bundle = build_market_intelligence_bundle_from_workspace(
        workspace_path,
        generated_at=generated_at,
    )

    workspace_mission_brief = _load_persisted_json(artifacts_dir / "mission_brief.json")
    seeded_problem_brief = _load_persisted_json(artifacts_dir / "problem_brief.json")
    workspace_id = (
        workspace_mission_brief.get("workspace_id")
        if workspace_mission_brief is not None
        else seeded_problem_brief.get("workspace_id") if seeded_problem_brief is not None else ""
    )
    problem_brief, concept_brief, prd = _load_or_build_workspace_discover_artifacts(
        workspace_path,
        workspace_id=workspace_id,
        generated_at=generated_at,
        mission_brief=workspace_mission_brief,
    )
    decision_queue = _load_json(artifacts_dir / "decision_queue.example.json")
    decision_log = _load_json(artifacts_dir / "decision_log.example.json")
    follow_up_queue = _load_json(artifacts_dir / "follow_up_queue.example.json")
    status_mail = _load_json(artifacts_dir / "status_mail.example.json")
    issue_log = _load_json(artifacts_dir / "issue_log.example.json")
    feedback_log = _load_json(artifacts_dir / "productos_feedback_log.example.json")
    improvement_loop_state = _load_json(artifacts_dir / "improvement_loop_state.example.json")
    adapter_parity_report = _load_json(artifacts_dir / "runtime_scenario_report_adapter_parity.example.json")
    market_refresh_report = _load_json(artifacts_dir / "runtime_scenario_report_market_refresh.example.json")
    live_doc_sync_state = _load_json(artifacts_dir / "document_sync_state_live_docs.example.json")
    completion_validation_report = _load_json(
        _artifact_path_with_archive_fallback(artifacts_dir, "validation_lane_report_next_version_completion.example.json")
    )
    completion_manual_record = _load_json(
        _artifact_path_with_archive_fallback(artifacts_dir, "manual_validation_record_next_version_completion.example.json")
    )
    completion_release_gate_decision = _load_json(
        _artifact_path_with_archive_fallback(artifacts_dir, "release_gate_decision_next_version_completion.example.json")
    )
    workspace_research_brief = _load_persisted_json(artifacts_dir / "research_brief.json")
    workspace_external_research_plan = _load_persisted_json(artifacts_dir / "external_research_plan.json")
    workspace_external_research_source_discovery = _load_persisted_json(
        artifacts_dir / "external_research_source_discovery.json"
    )
    workspace_external_research_feed_registry = _load_persisted_json(
        artifacts_dir / "external_research_feed_registry.json"
    )
    workspace_selected_research_manifest = _load_persisted_json(
        workspace_path / "outputs" / "research" / "external-research-manifest.selected.json"
    )
    workspace_external_research_review = _load_persisted_json(artifacts_dir / "external_research_review.json")
    workspace_problem_brief = _load_persisted_json(artifacts_dir / "problem_brief.json") or problem_brief
    strategic_memory = _load_json(ROOT / "core" / "examples" / "artifacts" / "strategic_memory_record.example.json")
    workspace_id = problem_brief["workspace_id"]

    intake_items = _collect_inbox_items(workspace_path, generated_at)
    persisted_discover_artifacts = _load_persisted_discover_artifacts(workspace_path)
    persisted_operate_artifacts = _load_persisted_operate_artifacts(workspace_path)
    persisted_improve_artifacts = _load_persisted_improve_artifacts(workspace_path)
    persisted_presentation_artifacts = _load_persisted_presentation_artifacts(workspace_path)
    if persisted_discover_artifacts is None:
        discover_problem_brief, discover_concept_brief, discover_prd = _build_live_discover_artifacts(
            workspace_path,
            workspace_id=workspace_id,
            generated_at=generated_at,
            mission_brief=workspace_mission_brief,
        )
    else:
        discover_problem_brief, discover_concept_brief, discover_prd = persisted_discover_artifacts
    if persisted_operate_artifacts is not None:
        status_mail, issue_log = persisted_operate_artifacts
    if persisted_improve_artifacts is not None:
        improvement_loop_state = persisted_improve_artifacts["improvement_loop_state"]
    presentation_brief = foundation_bundle["presentation_brief"]
    presentation_evidence_pack = foundation_bundle["presentation_evidence_pack"]
    presentation_story = foundation_bundle["presentation_story"]
    presentation_render_spec = foundation_bundle["presentation_render_spec"]
    presentation_publish_check = foundation_bundle["presentation_publish_check"]
    presentation_ppt_export_plan = foundation_bundle["presentation_ppt_export_plan"]
    if persisted_presentation_artifacts is not None:
        presentation_brief = persisted_presentation_artifacts["presentation_brief"]
        presentation_evidence_pack = persisted_presentation_artifacts["presentation_evidence_pack"]
        presentation_story = persisted_presentation_artifacts["presentation_story"]
        presentation_render_spec = persisted_presentation_artifacts["presentation_render_spec"]
        presentation_publish_check = persisted_presentation_artifacts["presentation_publish_check"]
        presentation_ppt_export_plan = persisted_presentation_artifacts["presentation_ppt_export_plan"]
    else:
        presentation_brief = _augment_presentation_brief_with_workspace_research(
            presentation_brief,
            research_brief=workspace_research_brief,
            problem_brief=workspace_problem_brief,
        )
        presentation_brief = _augment_presentation_brief_with_mission(
            presentation_brief,
            mission_brief=workspace_mission_brief,
        )
        presentation_evidence_pack = build_evidence_pack(presentation_brief)
        presentation_story = build_presentation_story(presentation_brief, presentation_evidence_pack)
        presentation_render_spec = build_render_spec(presentation_brief, presentation_story)
        presentation_publish_check = build_publish_check(presentation_brief, presentation_render_spec, target_format="html")
        presentation_ppt_export_plan = build_ppt_export_plan(presentation_render_spec)
    if persisted_presentation_artifacts is not None:
        presentation_brief = _augment_presentation_brief_with_mission(
            presentation_brief,
            mission_brief=workspace_mission_brief,
        )
        presentation_evidence_pack = build_evidence_pack(presentation_brief)
        presentation_story = build_presentation_story(presentation_brief, presentation_evidence_pack)
        presentation_render_spec = build_render_spec(presentation_brief, presentation_story)
        presentation_publish_check = build_publish_check(presentation_brief, presentation_render_spec, target_format="html")
        presentation_ppt_export_plan = build_ppt_export_plan(presentation_render_spec)
    live_doc_sync_state = _augment_document_sync_state_with_mission(
        live_doc_sync_state,
        mission_brief=workspace_mission_brief,
    )
    status_mail = _augment_status_mail_with_mission(
        status_mail,
        mission_brief=workspace_mission_brief,
    )
    issue_log = _augment_issue_log_with_mission(
        issue_log,
        mission_brief=workspace_mission_brief,
    )
    eval_suite_manifest = _build_eval_suite_manifest(
        workspace_id=workspace_id,
        generated_at=generated_at,
    )
    eval_run_report = {"eval_run_report_id": f"eval_run_report_{workspace_id}_bounded_baseline"}
    context_pack = {"context_pack_id": f"context_pack_{workspace_id}_bounded_baseline"}
    context_pack_request_summary = "Assemble the evidence, memory, and decision context needed to review the current bounded baseline."
    context_pack_decision_to_be_made = "Should ProductOS treat the current next-version runtime as trustworthy enough to score and promote release claims?"
    context_pack_audience = ["PM", "engineering", "leadership"]
    context_pack_evidence_bundle = [
        {
            "source_id": decision_log["decision_log_id"],
            "source_type": "decision_log",
            "summary": "The decision log records the baseline release decisions with reversibility, tradeoffs, rejected options, kill criteria, and follow-up review timing.",
            "confidence": 0.9,
            "freshness_status": "usable_with_review",
            "claim_mode": "direct_evidence",
        },
        {
            "source_id": strategic_memory["strategic_memory_record_id"],
            "source_type": "strategic_memory",
            "summary": "Strategic memory captures the prior thesis, later outcome, and lesson for reusable recall.",
            "confidence": 0.84,
            "freshness_status": "usable_with_review",
            "claim_mode": "direct_evidence",
        },
        {
            "source_id": eval_run_report["eval_run_report_id"],
            "source_type": "eval_run_report",
            "summary": "The frozen eval suite remains a first-class release input for the bounded baseline.",
            "confidence": 0.95,
            "freshness_status": "fresh",
            "claim_mode": "direct_evidence",
        },
        {
            "source_id": discover_prd["prd_id"],
            "source_type": "prd",
            "summary": "The live discover route can still produce a decision-ready PRD package from the inbox.",
            "confidence": 0.92,
            "freshness_status": "fresh",
            "claim_mode": "direct_evidence",
        },
    ]
    context_pack_open_questions = [
        "Which remaining mixed-provenance feature should be forced through the next bounded hardening cycle first?"
    ]
    context_pack_source_artifact_ids = [
        decision_log["decision_log_id"],
        strategic_memory["strategic_memory_record_id"],
        eval_run_report["eval_run_report_id"],
        discover_prd["prd_id"],
    ]
    context_pack_recommended_next_action = "Use the bounded baseline to make truthfulness, frozen evals, and decision memory visible in every promotion decision."
    if workspace_mission_brief is not None:
        context_pack_request_summary = (
            f"Assemble the evidence, memory, and execution context needed to run the mission '{workspace_mission_brief['title']}'."
        )
        context_pack_decision_to_be_made = (
            f"How should ProductOS execute the mission '{workspace_mission_brief['title']}' without dropping truthfulness, review gates, or PM approval?"
        )
        context_pack_audience = list(dict.fromkeys([*context_pack_audience, *workspace_mission_brief.get("audience", [])]))
        context_pack_evidence_bundle.insert(
            0,
            {
                "source_id": workspace_mission_brief["mission_brief_id"],
                "source_type": "mission_brief",
                "summary": workspace_mission_brief["mission_summary"],
                "confidence": 0.97,
                "freshness_status": "fresh",
                "claim_mode": "direct_evidence",
            },
        )
        context_pack_open_questions.append(workspace_mission_brief["customer_problem"])
        context_pack_source_artifact_ids.insert(0, workspace_mission_brief["mission_brief_id"])
        context_pack_recommended_next_action = workspace_mission_brief.get("next_action", context_pack_recommended_next_action)

    mission_router = (
        copy.deepcopy(workspace_mission_brief.get("mission_router"))
        if workspace_mission_brief is not None and workspace_mission_brief.get("mission_router") is not None
        else _default_mission_router()
    )
    steering_context = (
        copy.deepcopy(workspace_mission_brief.get("steering_context"))
        if workspace_mission_brief is not None and workspace_mission_brief.get("steering_context") is not None
        else _default_steering_context(workspace_path)
    )

    selected_adapter_id = {
        "codex": "adapter_codex_thin",
        "claude": "adapter_claude_style_thin",
        "windsurf": "adapter_windsurf_thin",
        "antigravity": "adapter_antigravity_thin",
    }.get(adapter_name, "adapter_codex_thin")

    runtime_adapter_registry = {
        "schema_version": "1.0.0",
        "runtime_adapter_registry_id": f"runtime_adapter_registry_{workspace_id}_next_version",
        "workspace_id": workspace_id,
        "status": "healthy",
        "default_adapter_id": selected_adapter_id,
        "adapters": [
            {
                "adapter_id": "adapter_codex_thin",
                "name": "Codex Thin Adapter",
                "capability_type": "custom",
                "availability_status": "available",
                "supported_actions": [
                    "inspect_repo",
                    "run_superpower_loop",
                    "capture_review_findings",
                    "run_validation",
                    "export_artifacts",
                ],
                "requires_host_support": True,
                "verification_status": "verified",
                "used_by_default": adapter_name == "codex",
                "supported_mission_stages": ["discover", "align", "operate", "improve"],
                "prompt_pattern_capabilities": _adapter_capability_profile(
                    mission_routing="repo_managed",
                    task_boundary_visibility="repo_managed",
                    research_freshness="repo_managed",
                    validation_enforcement="repo_managed",
                    delegation_support="limited",
                    approval_gating="native",
                    memory_steering="repo_managed",
                    artifact_export="repo_managed",
                ),
                "host_constraints": [
                    "Uses the repo contract and local validation commands."
                ],
                "notes": "Reference thin adapter for the current ProductOS workspace.",
            },
            {
                "adapter_id": "adapter_claude_style_thin",
                "name": "Claude-Style Thin Adapter",
                "capability_type": "custom",
                "availability_status": "available",
                "supported_actions": [
                    "inspect_repo",
                    "run_superpower_loop",
                    "capture_review_findings",
                    "run_validation",
                    "export_artifacts",
                ],
                "requires_host_support": True,
                "verification_status": "verified",
                "used_by_default": adapter_name == "claude",
                "supported_mission_stages": ["discover", "align", "operate", "improve"],
                "prompt_pattern_capabilities": _adapter_capability_profile(
                    mission_routing="repo_managed",
                    task_boundary_visibility="repo_managed",
                    research_freshness="repo_managed",
                    validation_enforcement="repo_managed",
                    delegation_support="limited",
                    approval_gating="native",
                    memory_steering="repo_managed",
                    artifact_export="repo_managed",
                ),
                "host_constraints": [
                    "Verified against the shared repo contract through parity-report evidence; direct host-native execution should keep using the same bounded actions."
                ],
                "notes": "Repo-contract parity is now verified for Claude-style coding agents.",
            },
            {
                "adapter_id": "adapter_windsurf_thin",
                "name": "Windsurf Thin Adapter",
                "capability_type": "custom",
                "availability_status": "available",
                "supported_actions": [
                    "inspect_repo",
                    "run_superpower_loop",
                    "capture_review_findings",
                    "run_validation",
                    "export_artifacts",
                ],
                "requires_host_support": True,
                "verification_status": "verified",
                "used_by_default": adapter_name == "windsurf",
                "supported_mission_stages": ["discover", "align", "operate", "improve"],
                "prompt_pattern_capabilities": _adapter_capability_profile(
                    mission_routing="repo_managed",
                    task_boundary_visibility="repo_managed",
                    research_freshness="repo_managed",
                    validation_enforcement="repo_managed",
                    delegation_support="limited",
                    approval_gating="native",
                    memory_steering="repo_managed",
                    artifact_export="repo_managed",
                ),
                "host_constraints": [
                    "Verified against the shared repo contract through parity-report evidence; direct host-native execution should keep using the same bounded actions."
                ],
                "notes": "Repo-contract parity is now verified for Windsurf.",
            },
            {
                "adapter_id": "adapter_antigravity_thin",
                "name": "Antigravity Thin Adapter",
                "capability_type": "custom",
                "availability_status": "available",
                "supported_actions": [
                    "inspect_repo",
                    "run_superpower_loop",
                    "capture_review_findings",
                    "run_validation",
                    "export_artifacts",
                ],
                "requires_host_support": True,
                "verification_status": "verified",
                "used_by_default": adapter_name == "antigravity",
                "supported_mission_stages": ["discover", "align", "operate", "improve"],
                "prompt_pattern_capabilities": _adapter_capability_profile(
                    mission_routing="repo_managed",
                    task_boundary_visibility="repo_managed",
                    research_freshness="repo_managed",
                    validation_enforcement="repo_managed",
                    delegation_support="limited",
                    approval_gating="native",
                    memory_steering="repo_managed",
                    artifact_export="repo_managed",
                ),
                "host_constraints": [
                    "Verified against the shared repo contract through parity-report evidence; direct host-native execution should keep using the same bounded actions."
                ],
                "notes": "Repo-contract parity is now verified for Antigravity.",
            },
            {
                "adapter_id": "adapter_repo_filesystem",
                "name": "Repo Filesystem Adapter",
                "capability_type": "filesystem_access",
                "availability_status": "available",
                "supported_actions": [
                    "read_workspace_state",
                    "write_export_bundle",
                    "inspect_inbox_files",
                ],
                "requires_host_support": True,
                "verification_status": "verified",
                "used_by_default": True,
                "supported_mission_stages": ["discover", "align", "operate", "improve"],
                "prompt_pattern_capabilities": _adapter_capability_profile(
                    mission_routing="repo_managed",
                    task_boundary_visibility="unsupported",
                    research_freshness="unsupported",
                    validation_enforcement="limited",
                    delegation_support="unsupported",
                    approval_gating="unsupported",
                    memory_steering="limited",
                    artifact_export="native",
                ),
                "host_constraints": [
                    "Requires writable workspace access."
                ],
                "notes": "Canonical repo-backed control surface for the next-version CLI.",
            },
            {
                "adapter_id": "adapter_local_validation_runner",
                "name": "Local Validation Runner",
                "capability_type": "validation_runner",
                "availability_status": "available",
                "supported_actions": [
                    "run_schema_validation",
                    "run_pytest",
                    "validate_export_bundle",
                ],
                "requires_host_support": True,
                "verification_status": "verified",
                "used_by_default": True,
                "supported_mission_stages": ["discover", "align", "operate", "improve"],
                "prompt_pattern_capabilities": _adapter_capability_profile(
                    mission_routing="unsupported",
                    task_boundary_visibility="unsupported",
                    research_freshness="unsupported",
                    validation_enforcement="native",
                    delegation_support="unsupported",
                    approval_gating="unsupported",
                    memory_steering="unsupported",
                    artifact_export="unsupported",
                ),
                "host_constraints": [
                    "Requires local Python and pytest execution."
                ],
                "notes": "Common validation surface shared by every thin adapter.",
            },
        ],
        "evaluated_at": generated_at,
    }
    adapter_parity_report["generated_at"] = generated_at
    market_refresh_report["generated_at"] = generated_at

    discover_artifacts_persisted = persisted_discover_artifacts is not None
    discover_scorecard = _scorecard(
        workspace_id=workspace_id,
        feature_id="discover_to_prd_superpower",
        feature_name="Messy input to PRD superpower",
        loop_id="signal_to_product_decision",
        benchmark_ref=foundation_bundle["pm_superpower_benchmark"]["pm_superpower_benchmark_id"],
        validation_tier="tier_2",
        overall_score=5 if discover_artifacts_persisted else 4,
        scenarios=[
            {
                "scenario_id": "scn_discover_from_live_inbox",
                "title": "Route live inbox inputs into the decision package",
                "scenario_type": "dogfood_run",
                "result": "passed",
                "summary": (
                    "The repo ingests the live note and transcript inputs, produces a fresh problem brief, concept brief, and PRD package, "
                    "and keeps the route visible through the canonical CLI control surface."
                ),
                "evidence_refs": [
                    f"intake_routing_state_{workspace_id}_next_version",
                    discover_problem_brief["problem_brief_id"],
                    discover_prd["prd_id"],
                ],
            }
        ],
        evidence_refs=[
            f"intake_routing_state_{workspace_id}_next_version",
            discover_problem_brief["problem_brief_id"],
            discover_concept_brief["concept_brief_id"],
            discover_prd["prd_id"],
            eval_run_report["eval_run_report_id"],
        ],
        provenance_classification="real" if discover_artifacts_persisted else "mixed",
        score_basis=(
            ["persisted_discover_outputs", "live_inbox_evidence", "frozen_eval_suite"]
            if discover_artifacts_persisted
            else ["live_inbox_evidence", "context_pack", "frozen_eval_suite"]
        ),
        truthfulness_summary=(
            "The discover slice now scores from persisted workspace outputs rather than bundle-local narration, so the same-day decision package can be treated as a promotable source."
            if discover_artifacts_persisted
            else "The discover slice still produces strong live artifacts, but the final score remains watch-level because the runtime bundle mixes fresh outputs with generated release narration."
        ),
        context_pack_ref=context_pack["context_pack_id"],
        eval_run_ref=eval_run_report["eval_run_report_id"],
        dimension_scores=[
            {
                "dimension_key": "pm_leverage",
                "score": 5,
                "rationale": "The PM can now move from messy inputs to a reviewable decision package through one bounded repo-native path.",
                "evidence_refs": [
                    f"intake_routing_state_{workspace_id}_next_version",
                    discover_prd["prd_id"],
                ],
            },
            {
                "dimension_key": "output_quality",
                "score": 5,
                "rationale": "The live-input problem brief, concept brief, and PRD package are explicit, reviewable, and traceable back to the inbox evidence.",
                "evidence_refs": [
                    discover_problem_brief["problem_brief_id"],
                    discover_prd["prd_id"],
                ],
            },
            {
                "dimension_key": "reliability",
                "score": 5,
                "rationale": "The discover path now passes as a same-day, low-rewrite, repo-backed route with explicit evidence and approval points.",
                "evidence_refs": [
                    f"intake_routing_state_{workspace_id}_next_version",
                    foundation_bundle["pm_superpower_benchmark"]["pm_superpower_benchmark_id"],
                ],
            },
            {
                "dimension_key": "autonomy_quality",
                "score": 5,
                "rationale": "The CLI does the bounded synthesis work automatically while keeping the PM review gate explicit instead of hidden.",
                "evidence_refs": [
                    f"discover_execution_session_{workspace_id}",
                    discover_concept_brief["concept_brief_id"],
                ],
            },
            {
                "dimension_key": "repeatability",
                "score": 5,
                "rationale": "The bundle and CLI make the same discover path repeatable across adapter choices and export surfaces.",
                "evidence_refs": [
                    f"discover_execution_session_{workspace_id}",
                    foundation_bundle["pm_superpower_benchmark"]["pm_superpower_benchmark_id"],
                ],
            },
        ],
        reviewer_status="pass",
        reviewer_summary=(
            "The discover route is now backed by persisted workspace outputs and is ready to count as the discover standard for the current baseline."
            if discover_artifacts_persisted
            else "The live inbox route is strong, but the slice should stay internal-use until scoring and provenance are separated more cleanly."
        ),
        tester_status="pass" if discover_artifacts_persisted else "revise",
        tester_summary=(
            "The discover artifacts validate structurally and the score now points to persisted workspace outputs instead of bundle-local narration."
            if discover_artifacts_persisted
            else "The discover artifacts validate structurally, but evals still flag mixed-provenance scoring and watch-level truthfulness risk."
        ),
        manual_status="accept",
        manual_summary=(
            "Use the persisted discover package as the promotable same-day decision baseline."
            if discover_artifacts_persisted
            else "Keep discover-to-PRD active as a strong internal path while the remaining truthfulness controls mature."
        ),
        blocked_by=(
            []
            if discover_artifacts_persisted
            else ["Score-bearing discover claims still rely on mixed runtime provenance."]
        ),
        feedback_items=(
            []
            if discover_artifacts_persisted
            else [
                _feedback_item(
                    feedback_id="score_feedback_discover_provenance",
                    summary="Separate persisted discover outputs from bundle-local scoring before calling the discover slice fully promoted.",
                    impact_level="high",
                    recommended_action="Route discover scoring through persisted outputs and rerun the frozen eval suite.",
                    route_targets=["improvement_loop_state", "feedback_cluster_state"],
                    linked_dimension_keys=["reliability", "repeatability"],
                    linked_artifact_refs=[discover_prd["prd_id"], eval_run_report["eval_run_report_id"]],
                )
            ]
        ),
        next_action=(
            "Keep the persisted discover package as the standard source for same-day decision scoring and rerun the frozen eval suite after meaningful discover changes."
            if discover_artifacts_persisted
            else "Keep the discover slice in internal use, persist its outputs explicitly, and rescore it after the next eval run."
        ),
        generated_at=generated_at,
    )

    docs_alignment_scorecard = _scorecard(
        workspace_id=workspace_id,
        feature_id="docs_alignment_superpower",
        feature_name="Readable docs and alignment superpower",
        loop_id="decision_to_stakeholder_alignment",
        benchmark_ref=foundation_bundle["pm_superpower_benchmark"]["pm_superpower_benchmark_id"],
        validation_tier="tier_2",
        overall_score=4,
        scenarios=[
            {
                "scenario_id": "scn_docs_bundle_live_sync",
                "title": "Readable docs stay live and aligned from the repo bundle",
                "scenario_type": "dogfood_run",
                "result": "passed",
                "summary": "The repo now keeps the product, marketing, and planning docs in sync through the same governed next-version path that ships the discover package.",
                "evidence_refs": [
                    live_doc_sync_state["document_sync_state_id"],
                    completion_validation_report["validation_lane_report_id"],
                ],
            }
        ],
        evidence_refs=[
            live_doc_sync_state["document_sync_state_id"],
            "validation_lane_report_ws_productos_v2_live_docs",
            "manual_validation_record_ws_productos_v2_live_docs",
            completion_manual_record["manual_validation_record_id"],
            eval_run_report["eval_run_report_id"],
        ],
        provenance_classification="real",
        score_basis=["document_sync_state", "manual_validation", "frozen_eval_suite"],
        truthfulness_summary="The docs slice is largely grounded in persisted workspace artifacts, but the broader control surface still needs stronger release-level truth signaling.",
        context_pack_ref=context_pack["context_pack_id"],
        eval_run_ref=eval_run_report["eval_run_report_id"],
        dimension_scores=[
            {
                "dimension_key": "pm_leverage",
                "score": 5,
                "rationale": "The repo-native path now turns promoted product truth into readable docs without a separate PM rewrite loop.",
                "evidence_refs": [
                    live_doc_sync_state["document_sync_state_id"],
                    completion_manual_record["manual_validation_record_id"],
                ],
            },
            {
                "dimension_key": "output_quality",
                "score": 5,
                "rationale": "The current docs are readable, traceable, and strong enough to act as the standard aligned package for the self-hosting workspace.",
                "evidence_refs": [
                    "manual_validation_record_ws_productos_v2_live_docs",
                    live_doc_sync_state["document_sync_state_id"],
                ],
            },
            {
                "dimension_key": "reliability",
                "score": 5,
                "rationale": "Live-doc sync, validation, and Ralph review all passed on the same bundle now used by the next-version control surface.",
                "evidence_refs": [
                    "validation_lane_report_ws_productos_v2_live_docs",
                    completion_validation_report["validation_lane_report_id"],
                ],
            },
            {
                "dimension_key": "autonomy_quality",
                "score": 5,
                "rationale": "The docs now refresh through one governed loop and no longer need an extra manual translation step before internal adoption.",
                "evidence_refs": [
                    live_doc_sync_state["document_sync_state_id"],
                    completion_manual_record["manual_validation_record_id"],
                ],
            },
            {
                "dimension_key": "repeatability",
                "score": 5,
                "rationale": "The aligned docs bundle is now part of the repeated next-version baseline rather than a one-off V4 proof artifact.",
                "evidence_refs": [
                    live_doc_sync_state["document_sync_state_id"],
                    completion_validation_report["validation_lane_report_id"],
                ],
            },
        ],
        reviewer_status="pass",
        reviewer_summary="The readable-doc path remains one of the strongest slices and is good enough for internal default use.",
        tester_status="pass",
        tester_summary="Live-doc sync and validation remain clean, but broader promotion should wait for the control-surface hardening to finish.",
        manual_status="accept",
        manual_summary="Keep the readable-doc bundle as the default internal alignment path while the stable slice remains bounded.",
        blocked_by=[],
        feedback_items=[
            _feedback_item(
                feedback_id="score_feedback_docs_release_truth",
                summary="Keep the docs slice internal-use until the broader control surface stops overstating promotion status.",
                impact_level="medium",
                recommended_action="Retain docs as the default internal alignment path and rescore after the remaining truthfulness fixes land.",
                route_targets=["improvement_loop_state"],
                linked_dimension_keys=["reliability", "repeatability"],
                linked_artifact_refs=[live_doc_sync_state["document_sync_state_id"], eval_run_report["eval_run_report_id"]],
            )
        ],
        next_action="Use the readable-doc bundle internally, but do not let it hide broader truthfulness gaps elsewhere in the control surface.",
        generated_at=generated_at,
    )

    presentation_artifacts_persisted = persisted_presentation_artifacts is not None
    presentation_scorecard = _scorecard(
        workspace_id=workspace_id,
        feature_id="presentation_superpower",
        feature_name="PRD to deck and executive story",
        loop_id="decision_to_stakeholder_alignment",
        benchmark_ref=foundation_bundle["pm_superpower_benchmark"]["pm_superpower_benchmark_id"],
        validation_tier="tier_3",
        overall_score=5 if presentation_artifacts_persisted else 4,
        scenarios=[
            {
                "scenario_id": "scn_presentation_bundle_generation",
                "title": "Generate the promoted docs-and-deck package from the repo baseline",
                "scenario_type": "dogfood_run",
                "result": "passed",
                "summary": (
                    "The presentation package now reuses persisted story, render, and publish outputs as the governed docs-and-deck path from PRD to stakeholder-ready communication."
                    if presentation_artifacts_persisted
                    else "The presentation package now clears the bounded next-version release gate as part of the promoted aligned path from PRD to stakeholder-ready docs and deck."
                ),
                "evidence_refs": [
                    presentation_brief["presentation_brief_id"],
                    completion_validation_report["validation_lane_report_id"],
                ],
            }
        ],
        evidence_refs=[
            presentation_brief["presentation_brief_id"],
            presentation_story["presentation_story_id"],
            presentation_render_spec["render_spec_id"],
            presentation_publish_check["publish_check_id"],
            foundation_bundle["presentation_pattern_review"]["presentation_pattern_review_id"],
            completion_validation_report["validation_lane_report_id"],
            completion_manual_record["manual_validation_record_id"],
            eval_run_report["eval_run_report_id"],
        ],
        provenance_classification="real" if presentation_artifacts_persisted else "mixed",
        score_basis=(
            ["persisted_presentation_outputs", "presentation_bundle", "manual_validation", "frozen_eval_suite"]
            if presentation_artifacts_persisted
            else ["presentation_bundle", "manual_validation", "frozen_eval_suite"]
        ),
        truthfulness_summary=(
            "The presentation slice now scores from persisted story, render, and publish artifacts, so stakeholder communication can be treated as a real governed output rather than a bundle-local narration."
            if presentation_artifacts_persisted
            else "The presentation slice is high quality, but it still inherits some mixed provenance because the surrounding release narrative and promotion logic are not fully separated from generated bundle state."
        ),
        context_pack_ref=context_pack["context_pack_id"],
        eval_run_ref=eval_run_report["eval_run_report_id"],
        dimension_scores=[
            {
                "dimension_key": "pm_leverage",
                "score": 5,
                "rationale": "The repo now packages the approved PRD and doc bundle into a stakeholder-ready deck without a separate PM slide-building pass.",
                "evidence_refs": [
                    presentation_story["presentation_story_id"],
                    presentation_render_spec["render_spec_id"],
                ],
            },
            {
                "dimension_key": "output_quality",
                "score": 5,
                "rationale": "The story, render spec, and audience policy now act as the promoted next-version deck path for the self-hosting workspace.",
                "evidence_refs": [
                    foundation_bundle["presentation_pattern_review"]["presentation_pattern_review_id"],
                    completion_manual_record["manual_validation_record_id"],
                ],
            },
            {
                "dimension_key": "reliability",
                "score": 5,
                "rationale": "Publish checks, export planning, and the bounded completion gate now all agree the deck path is stable for the promoted baseline.",
                "evidence_refs": [
                    presentation_publish_check["publish_check_id"],
                    completion_validation_report["validation_lane_report_id"],
                ],
            },
            {
                "dimension_key": "autonomy_quality",
                "score": 5,
                "rationale": "The aligned path keeps the right manual approval boundary while still behaving like a real PM superpower inside the repo.",
                "evidence_refs": [
                    foundation_bundle["presentation_sample_record"]["presentation_sample_record_id"],
                    completion_manual_record["manual_validation_record_id"],
                ],
            },
            {
                "dimension_key": "repeatability",
                "score": 5,
                "rationale": "The same governed docs-and-deck path now ships as part of the repeatable next-version baseline rather than a one-off communication proof.",
                "evidence_refs": [
                    foundation_bundle["presentation_pattern_review"]["presentation_pattern_review_id"],
                    presentation_ppt_export_plan["ppt_export_plan_id"],
                ],
            },
        ],
        reviewer_status="pass",
        reviewer_summary=(
            "The presentation package is now backed by persisted story, render, and publish artifacts and can count as the governed communication standard for the bounded baseline."
            if presentation_artifacts_persisted
            else "The presentation package remains strong for internal and leadership-ready use, but its promotion claim should stay watch-level until the surrounding truth controls are explicit."
        ),
        tester_status="pass" if presentation_artifacts_persisted else "revise",
        tester_summary=(
            "Generation and publish checks now validate against persisted presentation artifacts, so the docs-and-deck path clears the bounded proof bar."
            if presentation_artifacts_persisted
            else "Generation and publish checks pass, but the broader release claim still depends on mixed control-surface evidence."
        ),
        manual_status="accept",
        manual_summary=(
            "Keep using the persisted story, render, and publish artifacts as the standard communication proof path."
            if presentation_artifacts_persisted
            else "Keep the docs-and-deck path active, but treat final promotion as pending the remaining truthfulness hardening slice."
        ),
        blocked_by=[] if presentation_artifacts_persisted else ["Presentation promotion still inherits mixed control-surface provenance."],
        feedback_items=(
            []
            if presentation_artifacts_persisted
            else [
                _feedback_item(
                    feedback_id="score_feedback_presentation_truth",
                    summary="Keep the presentation slice in internal-use status until release-level provenance becomes explicit.",
                    impact_level="medium",
                    recommended_action="Rescore the presentation path after the control surface and release narration stop mixing generated and persisted evidence.",
                    route_targets=["improvement_loop_state"],
                    linked_dimension_keys=["reliability", "repeatability"],
                    linked_artifact_refs=[
                        presentation_story["presentation_story_id"],
                        eval_run_report["eval_run_report_id"],
                    ],
                )
            ]
        ),
        next_action=(
            "Keep the persisted docs-and-deck outputs as the standard communication proof path and refresh them after meaningful product changes."
            if presentation_artifacts_persisted
            else "Keep using the governed docs-and-deck path, but rescore it only after the control-surface truth signals are explicit."
        ),
        generated_at=generated_at,
    )

    operate_artifacts_persisted = persisted_operate_artifacts is not None
    weekly_pm_autopilot_scorecard = _scorecard(
        workspace_id=workspace_id,
        feature_id="weekly_pm_autopilot",
        feature_name="Weekly PM autopilot",
        loop_id="feedback_to_accepted_improvement",
        benchmark_ref=foundation_bundle["pm_superpower_benchmark"]["pm_superpower_benchmark_id"],
        validation_tier="tier_2",
        overall_score=5 if operate_artifacts_persisted else 4,
        scenarios=[
            {
                "scenario_id": "scn_operator_from_current_queues",
                "title": "Operate weekly cadence from current queues and release state",
                "scenario_type": "dogfood_run",
                "result": "passed",
                "summary": (
                    "The repo now turns decisions, follow-ups, issue state, and release readiness into one supervised weekly operator session "
                    "with persisted operator outputs that can be reused outside the bundle."
                    if operate_artifacts_persisted
                    else "The repo now turns decisions, follow-ups, issue state, and release readiness into one supervised weekly operator session "
                    "with a review-ready status mail."
                ),
                "evidence_refs": [
                    decision_queue["decision_queue_id"],
                    follow_up_queue["follow_up_queue_id"],
                    status_mail["status_mail_id"],
                    issue_log["issue_log_id"],
                ],
            }
        ],
        evidence_refs=[
            decision_queue["decision_queue_id"],
            follow_up_queue["follow_up_queue_id"],
            status_mail["status_mail_id"],
            issue_log["issue_log_id"],
            completion_validation_report["validation_lane_report_id"],
            completion_manual_record["manual_validation_record_id"],
            eval_run_report["eval_run_report_id"],
        ],
        provenance_classification="real" if operate_artifacts_persisted else "mixed",
        score_basis=(
            ["persisted_operate_outputs", "queue_artifacts", "frozen_eval_suite"]
            if operate_artifacts_persisted
            else ["queue_artifacts", "status_mail", "frozen_eval_suite"]
        ),
        truthfulness_summary=(
            "The weekly operator path now scores from persisted workspace outputs, so the supervised autopilot loop can be treated as a real reusable operating slice."
            if operate_artifacts_persisted
            else "The weekly operator path still leans on seeded artifacts and has not yet earned a promotion claim under the new eval and provenance rules."
        ),
        context_pack_ref=context_pack["context_pack_id"],
        eval_run_ref=eval_run_report["eval_run_report_id"],
        dimension_scores=[
            {
                "dimension_key": "pm_leverage",
                "score": 5,
                "rationale": "The weekly operator session now collapses queue review, issue review, release context, and status drafting into one supervised flow.",
                "evidence_refs": [
                    decision_queue["decision_queue_id"],
                    status_mail["status_mail_id"],
                ],
            },
            {
                "dimension_key": "output_quality",
                "score": 5,
                "rationale": "The status mail, issue log, and queue outputs are now packaged as one coherent weekly operator bundle.",
                "evidence_refs": [
                    status_mail["status_mail_id"],
                    issue_log["issue_log_id"],
                    completion_manual_record["manual_validation_record_id"],
                ],
            },
            {
                "dimension_key": "reliability",
                "score": 5,
                "rationale": "The weekly operator session is now explicit in the repo bundle and passes the same bounded validation and manual review path as the rest of the promoted baseline.",
                "evidence_refs": [
                    completion_validation_report["validation_lane_report_id"],
                    completion_manual_record["manual_validation_record_id"],
                ],
            },
            {
                "dimension_key": "autonomy_quality",
                "score": 5,
                "rationale": "The control surface now feels like a supervised autopilot because it emits the weekly operating summary rather than only queue fragments.",
                "evidence_refs": [
                    status_mail["status_mail_id"],
                    follow_up_queue["follow_up_queue_id"],
                ],
            },
            {
                "dimension_key": "repeatability",
                "score": 5,
                "rationale": "The weekly operator loop is now a repeatable named session in the CLI and no longer depends on ad hoc PM synthesis outside the repo.",
                "evidence_refs": [
                    status_mail["status_mail_id"],
                    completion_validation_report["validation_lane_report_id"],
                ],
            },
        ],
        reviewer_status="pass",
        reviewer_summary=(
            "The weekly operator path is now backed by persisted workspace outputs and is ready to count as the supervised weekly operating standard."
            if operate_artifacts_persisted
            else "The weekly operator path is useful, but it still looks more seeded than live and should remain below the promotion bar."
        ),
        tester_status="pass" if operate_artifacts_persisted else "revise",
        tester_summary=(
            "The operator session now validates from persisted live outputs, so the weekly autopilot slice clears the bounded proof bar."
            if operate_artifacts_persisted
            else "The operator session validates structurally, but evals still flag mixed provenance and weak live-run proof."
        ),
        manual_status="accept",
        manual_summary=(
            "The weekly operator session can now be reused as the customer-safe supervised autopilot baseline."
            if operate_artifacts_persisted
            else "Keep the weekly operator session in bounded internal use while the stable slice improves live scoring and context handling."
        ),
        blocked_by=[] if operate_artifacts_persisted else ["Weekly PM autopilot still depends on mixed seeded and generated operating artifacts."],
        feedback_items=(
            []
            if operate_artifacts_persisted
            else [
                _feedback_item(
                    feedback_id="score_feedback_weekly_live_proof",
                    summary="Replace seeded operator artifacts with stronger persisted live-run proof before promoting weekly autopilot.",
                    impact_level="high",
                    recommended_action="Run the weekly operator slice from persisted live inputs and rerun the frozen eval suite.",
                    route_targets=["improvement_loop_state"],
                    linked_dimension_keys=["reliability", "autonomy_quality"],
                    linked_artifact_refs=[status_mail["status_mail_id"], eval_run_report["eval_run_report_id"]],
                )
            ]
        ),
        next_action=(
            "Keep the persisted weekly operator outputs as the standard proof path and reuse them in the release bundle."
            if operate_artifacts_persisted
            else "Refresh the weekly operator path from persisted live outputs and rerun the eval suite before promoting it."
        ),
        generated_at=generated_at,
    )

    market_distribution_report = market_bundle["market_distribution_report"]

    market_intelligence_scorecard = _scorecard(
        workspace_id=workspace_id,
        feature_id="market_intelligence_superpower",
        feature_name="Agentic market intelligence",
        loop_id="decision_to_stakeholder_alignment",
        benchmark_ref=foundation_bundle["pm_superpower_benchmark"]["pm_superpower_benchmark_id"],
        validation_tier="tier_2",
        overall_score=4,
        scenarios=[
            {
                "scenario_id": "scn_market_intelligence_slice",
                "title": "Run the agentic market-intelligence slice",
                "scenario_type": "dogfood_run",
                "result": "passed",
                "summary": "The market-intelligence slice is strong, governed, and now distributed through a leadership-ready path with refresh and claim boundaries intact.",
                "evidence_refs": [
                    market_bundle["research_feature_recommendation_brief"]["research_feature_recommendation_brief_id"],
                    market_bundle["ralph_loop_state"]["ralph_loop_state_id"],
                    market_refresh_report["runtime_scenario_report_id"],
                    market_distribution_report["runtime_scenario_report_id"],
                    market_bundle["leadership_review"]["leadership_review_id"],
                ],
            }
        ],
        evidence_refs=[
            market_bundle["research_notebook"]["research_notebook_id"],
            market_bundle["landscape_matrix"]["landscape_matrix_id"],
            market_bundle["competitor_dossier"]["competitor_dossier_id"],
            market_bundle["research_feature_recommendation_brief"]["research_feature_recommendation_brief_id"],
            market_bundle["ralph_loop_state"]["ralph_loop_state_id"],
            market_refresh_report["runtime_scenario_report_id"],
            market_distribution_report["runtime_scenario_report_id"],
            market_bundle["leadership_review"]["leadership_review_id"],
            market_bundle["portfolio_update"]["portfolio_update_id"],
            eval_run_report["eval_run_report_id"],
        ],
        provenance_classification="real",
        score_basis=["research_pack", "ralph_loop_state", "frozen_eval_suite"],
        truthfulness_summary="The market-intelligence slice remains strong and mostly grounded in persisted evidence, but the overall control surface is still in watch mode.",
        context_pack_ref=context_pack["context_pack_id"],
        eval_run_ref=eval_run_report["eval_run_report_id"],
        dimension_scores=[
            {
                "dimension_key": "pm_leverage",
                "score": 5,
                "rationale": "The slice compresses meaningful market research into decision-useful recommendations and now packages that output for leadership consumption without extra PM reconstruction.",
                "evidence_refs": [
                    market_bundle["research_feature_recommendation_brief"]["research_feature_recommendation_brief_id"],
                    market_bundle["leadership_review"]["leadership_review_id"],
                ],
            },
            {
                "dimension_key": "output_quality",
                "score": 5,
                "rationale": "The research pack now supports a leadership-ready digest and portfolio-facing summary without dropping evidence or claim boundaries.",
                "evidence_refs": [
                    market_bundle["leadership_review"]["leadership_review_id"],
                    market_bundle["portfolio_update"]["portfolio_update_id"],
                ],
            },
            {
                "dimension_key": "reliability",
                "score": 5,
                "rationale": "The Ralph loop, validation lanes, unattended-refresh proof, and leadership-distribution report keep the slice disciplined even as its audience expands.",
                "evidence_refs": [
                    market_bundle["ralph_loop_state"]["ralph_loop_state_id"],
                    market_bundle["validation_lane_report"]["validation_lane_report_id"],
                    market_refresh_report["runtime_scenario_report_id"],
                    market_distribution_report["runtime_scenario_report_id"],
                ],
            },
            {
                "dimension_key": "autonomy_quality",
                "score": 5,
                "rationale": "The slice keeps unattended-refresh thresholds, contradiction handling, escalation conditions, and leadership-review boundaries explicit before any broader claim is made.",
                "evidence_refs": [
                    market_refresh_report["runtime_scenario_report_id"],
                    market_bundle["leadership_review"]["leadership_review_id"],
                ],
            },
            {
                "dimension_key": "repeatability",
                "score": 5,
                "rationale": "Recurring refresh and leadership-ready distribution now both pass governed proof without changing the underlying research contract.",
                "evidence_refs": [
                    market_refresh_report["runtime_scenario_report_id"],
                    market_distribution_report["runtime_scenario_report_id"],
                    market_bundle["portfolio_update"]["portfolio_update_id"],
                ],
            },
        ],
        reviewer_status="pass",
        reviewer_summary="The market-intelligence slice remains one of the strongest evidence-backed paths in the repo.",
        tester_status="pass",
        tester_summary="The slice validates cleanly and remains a strong internal-use standard while the stable release claim stays bounded.",
        manual_status="accept",
        manual_summary="Keep using market intelligence internally while broader release claims stay gated by the remaining truthfulness work.",
        blocked_by=[],
        feedback_items=[
            _feedback_item(
                feedback_id="score_feedback_market_foundation_gate",
                summary="Do not let the strongest research slice create a false sense that the broader runtime is already fully promotable.",
                impact_level="medium",
                recommended_action="Keep market intelligence internal-use while the truthful control-surface and eval hardening slice completes.",
                route_targets=["improvement_loop_state"],
                linked_dimension_keys=["reliability"],
                linked_artifact_refs=[market_distribution_report["runtime_scenario_report_id"], eval_run_report["eval_run_report_id"]],
            )
        ],
        next_action="Keep the market-intelligence slice active, but do not use it to mask the weaker truthfulness state of the control surface.",
        generated_at=generated_at,
    )

    runtime_control_surface_scorecard = _scorecard(
        workspace_id=workspace_id,
        feature_id="runtime_control_surface",
        feature_name="Repo control surface and orchestration",
        loop_id="cross_cutting",
        benchmark_ref=foundation_bundle["pm_superpower_benchmark"]["pm_superpower_benchmark_id"],
        validation_tier="tier_2",
        overall_score=4,
        scenarios=[
            {
                "scenario_id": "scn_repo_cli_control_surface",
                "title": "Run next-version loops from one repo control surface",
                "scenario_type": "dogfood_run",
                "result": "passed",
                "summary": (
                    "The repo CLI is now the canonical bounded control surface for ingest, discover, review, export, and doctor flows."
                ),
                "evidence_refs": [
                    f"cockpit_state_{workspace_id}_next_version",
                    f"orchestration_state_{workspace_id}_next_version",
                ],
            }
        ],
        evidence_refs=[
            f"cockpit_state_{workspace_id}_next_version",
            f"orchestration_state_{workspace_id}_next_version",
            f"feature_portfolio_review_{workspace_id}_next_version_baseline",
            context_pack["context_pack_id"],
            eval_run_report["eval_run_report_id"],
        ],
        provenance_classification="mixed",
        score_basis=["context_pack", "frozen_eval_suite", "feature_portfolio_review"],
        truthfulness_summary="The repo CLI now reports blocked promotion and eval pressure honestly enough to stay in internal use, though some mixed-provenance control-surface claims still need cleanup before a stronger release story.",
        context_pack_ref=context_pack["context_pack_id"],
        eval_run_ref=eval_run_report["eval_run_report_id"],
        dimension_scores=[
            {
                "dimension_key": "pm_leverage",
                "score": 5,
                "rationale": "The CLI collapses discovery, review, export, and validation into one explicit PM-facing surface.",
                "evidence_refs": [
                    f"cockpit_state_{workspace_id}_next_version",
                    f"feature_portfolio_review_{workspace_id}_next_version_baseline",
                ],
            },
            {
                "dimension_key": "output_quality",
                "score": 4,
                "rationale": "The control surface stays explainable, bounded, and aligned to the actual ProductOS loops rather than hidden host-specific behavior.",
                "evidence_refs": [
                    f"orchestration_state_{workspace_id}_next_version",
                    f"cockpit_state_{workspace_id}_next_version",
                ],
            },
            {
                "dimension_key": "reliability",
                "score": 4,
                "rationale": "The CLI is repo-backed and now surfaces blocked promotion honestly; remaining mixed-provenance debt still limits broader promotion confidence.",
                "evidence_refs": [
                    f"orchestration_state_{workspace_id}_next_version",
                    f"runtime_adapter_registry_{workspace_id}_next_version",
                ],
            },
            {
                "dimension_key": "autonomy_quality",
                "score": 4,
                "rationale": "The control surface keeps the PM in supervised control while still automating bounded work, and it now exposes blockers directly instead of narrating everything as healthy.",
                "evidence_refs": [
                    f"cockpit_state_{workspace_id}_next_version",
                    f"discover_execution_session_{workspace_id}",
                ],
            },
            {
                "dimension_key": "repeatability",
                "score": 4,
                "rationale": "The CLI repeats the same surface across adapters, export paths, and bounded loops, though the score-bearing release story still needs more provenance cleanup.",
                "evidence_refs": [
                    f"discover_execution_session_{workspace_id}",
                    f"operate_execution_session_{workspace_id}",
                ],
            },
        ],
        reviewer_status="pass",
        reviewer_summary="The control surface is the right surface, and it now reports blocked promotion honestly enough to remain in internal use.",
        tester_status="revise",
        tester_summary="Schema validation passes, and blocked promotion is now explicit; the remaining issue is watch-level provenance debt rather than a hard truthfulness failure.",
        manual_status="accept",
        manual_summary="Keep the repo CLI as the canonical internal-use surface; it is materially better after the truthful-blocked-state hardening, but not yet a fully promoted release narrator.",
        blocked_by=[
            "Mixed provenance is not yet surfaced strongly enough in the current control surface.",
        ],
        feedback_items=[
            _feedback_item(
                feedback_id="score_feedback_truthful_control_surface",
                summary="Make truthfulness, regressions, and mixed provenance first-class doctor/status/review outputs.",
                impact_level="high",
                recommended_action="Ship the truthful control-surface hardening slice before promoting any fully healthy baseline claim.",
                route_targets=["improvement_loop_state", "feedback_cluster_state"],
                linked_dimension_keys=["reliability", "autonomy_quality", "repeatability"],
                linked_artifact_refs=[context_pack["context_pack_id"], eval_run_report["eval_run_report_id"]],
            )
        ],
        next_action="Keep the truthful blocked-state control surface in place as the internal-use standard, then reduce the remaining mixed-provenance claims while self-improvement stays the main gating target.",
        generated_at=generated_at,
    )

    agent_adapter_scorecard = _scorecard(
        workspace_id=workspace_id,
        feature_id="agent_adapter_layer",
        feature_name="Thin multi-agent adapter layer",
        loop_id="cross_cutting",
        benchmark_ref=foundation_bundle["pm_superpower_benchmark"]["pm_superpower_benchmark_id"],
        validation_tier="tier_2",
        overall_score=5,
        scenarios=[
            {
                "scenario_id": "scn_thin_adapter_registry",
                "title": "Support named agent drivers through one repo contract",
                "scenario_type": "workflow_run",
                "result": "passed",
                "summary": "Thin named adapters now clear the same repo-contract parity proof for Codex, Claude-style agents, Windsurf, and Antigravity.",
                "evidence_refs": [
                    runtime_adapter_registry["runtime_adapter_registry_id"],
                    "core/docs/thin-agent-adapter-model.md",
                    adapter_parity_report["runtime_scenario_report_id"],
                ],
            }
        ],
        evidence_refs=[
            runtime_adapter_registry["runtime_adapter_registry_id"],
            "core/docs/thin-agent-adapter-model.md",
            "core/docs/vendor-neutral-agent-harness-standard.md",
            adapter_parity_report["runtime_scenario_report_id"],
            eval_run_report["eval_run_report_id"],
        ],
        provenance_classification="real",
        score_basis=["adapter_registry", "parity_report", "frozen_eval_suite"],
        truthfulness_summary="The thin adapter layer remains one of the few slices that is already backed by explicit parity evidence rather than mixed release narration.",
        context_pack_ref=context_pack["context_pack_id"],
        eval_run_ref=eval_run_report["eval_run_report_id"],
        dimension_scores=[
            {
                "dimension_key": "pm_leverage",
                "score": 5,
                "rationale": "The adapter layer prevents the PM from rewriting ProductOS for each agent tool.",
                "evidence_refs": [
                    runtime_adapter_registry["runtime_adapter_registry_id"],
                    "core/docs/vendor-neutral-agent-harness-standard.md",
                ],
            },
            {
                "dimension_key": "output_quality",
                "score": 5,
                "rationale": "The repo contract is explicit, thin, and now directly parity-checked across the named adapters.",
                "evidence_refs": [
                    runtime_adapter_registry["runtime_adapter_registry_id"],
                    "core/docs/thin-agent-adapter-model.md",
                    adapter_parity_report["runtime_scenario_report_id"],
                ],
            },
            {
                "dimension_key": "reliability",
                "score": 5,
                "rationale": "The parity report verifies the same bounded contract across the supported named adapters.",
                "evidence_refs": [
                    runtime_adapter_registry["runtime_adapter_registry_id"],
                    adapter_parity_report["runtime_scenario_report_id"],
                ],
            },
            {
                "dimension_key": "autonomy_quality",
                "score": 5,
                "rationale": "The adapter layer stays thin and does not hide product logic inside tool-specific behavior.",
                "evidence_refs": [
                    runtime_adapter_registry["runtime_adapter_registry_id"],
                    "core/docs/vendor-neutral-agent-harness-standard.md",
                ],
            },
            {
                "dimension_key": "repeatability",
                "score": 5,
                "rationale": "The same repo-contract proof now covers Codex, Claude-style, Windsurf, and Antigravity without changing ProductOS logic.",
                "evidence_refs": [
                    adapter_parity_report["runtime_scenario_report_id"],
                    "core/docs/thin-agent-adapter-model.md",
                ],
            },
        ],
        reviewer_status="pass",
        reviewer_summary="The adapter layer is correctly thin, repo-owned, and now backed by parity proof.",
        tester_status="pass",
        tester_summary="The shared repo contract now verifies cleanly across the named non-Codex adapter paths.",
        manual_status="accept",
        manual_summary="Treat the thin adapter layer as verified across the named repo-contract hosts and keep adding future hosts through the same parity proof pattern.",
        blocked_by=[],
        feedback_items=[],
        next_action="Use the verified thin adapter layer as the standard portability contract and apply the same parity proof before adding future hosts.",
        generated_at=generated_at,
    )

    improve_review_persisted = persisted_improve_artifacts is not None
    persisted_improve_eval_run_report = (
        persisted_improve_artifacts["eval_run_report"] if improve_review_persisted else None
    )
    persisted_improve_feature_portfolio_review = (
        persisted_improve_artifacts["feature_portfolio_review"] if improve_review_persisted else None
    )
    persisted_improve_release_gate_decision = (
        persisted_improve_artifacts["release_gate_decision"] if improve_review_persisted else None
    )
    persisted_improve_gate_ready = (
        improve_review_persisted
        and persisted_improve_release_gate_decision is not None
        and persisted_improve_release_gate_decision.get("decision") == "go"
        and persisted_improve_eval_run_report is not None
        and persisted_improve_eval_run_report.get("status") == "passed"
        and int(persisted_improve_eval_run_report.get("regression_count", 0)) == 0
        and persisted_improve_feature_portfolio_review is not None
        and persisted_improve_feature_portfolio_review.get("truthfulness_status") == "healthy"
    )
    portfolio_review_ref = (
        persisted_improve_feature_portfolio_review["feature_portfolio_review_id"]
        if persisted_improve_feature_portfolio_review is not None
        else f"feature_portfolio_review_{workspace_id}_next_version_baseline"
    )
    improve_eval_run_ref = (
        persisted_improve_eval_run_report["eval_run_report_id"]
        if persisted_improve_eval_run_report is not None
        else eval_run_report["eval_run_report_id"]
    )
    improve_release_gate_ref = (
        persisted_improve_release_gate_decision["release_gate_decision_id"]
        if persisted_improve_release_gate_decision is not None
        else completion_release_gate_decision["release_gate_decision_id"]
    )

    self_improvement_scorecard = _scorecard(
        workspace_id=workspace_id,
        feature_id="self_improvement_loop",
        feature_name="Self-improvement and scoring loop",
        loop_id="feedback_to_accepted_improvement",
        benchmark_ref=foundation_bundle["pm_superpower_benchmark"]["pm_superpower_benchmark_id"],
        validation_tier="tier_2",
        overall_score=5 if persisted_improve_gate_ready else 4,
        scenarios=[
            {
                "scenario_id": "scn_sub_five_features_route_to_improvement",
                "title": "Route sub-5 features into the improvement loop",
                "scenario_type": "dogfood_run",
                "result": "passed",
                "summary": (
                    "Feature scoring now reuses a persisted improve-review snapshot and explicit release-gate decision, so the compounding-improvement loop is no longer grading only the same fresh bundle it just assembled."
                    if persisted_improve_gate_ready
                    else "Feature scoring, portfolio review, and repeated Ralph-gated releases now show a working compounding-improvement loop instead of one-off setup."
                ),
                "evidence_refs": [
                    improvement_loop_state["improvement_loop_state_id"],
                    portfolio_review_ref,
                    completion_validation_report["validation_lane_report_id"],
                ],
            }
        ],
        evidence_refs=[
            improvement_loop_state["improvement_loop_state_id"],
            portfolio_review_ref,
            decision_log["decision_log_id"],
            strategic_memory["strategic_memory_record_id"],
            completion_validation_report["validation_lane_report_id"],
            completion_manual_record["manual_validation_record_id"],
            improve_release_gate_ref,
            foundation_bundle["feature_scorecard"]["feature_scorecard_id"],
            "release_4_1_0",
            "release_4_2_0",
            "release_4_3_0",
            improve_eval_run_ref,
        ],
        provenance_classification="real",
        score_basis=(
            ["persisted_improve_review", "release_gate_decision", "decision_memory", "independent_validation", "frozen_eval_suite"]
            if persisted_improve_gate_ready
            else ["feature_scorecards", "portfolio_review", "decision_memory", "independent_validation", "frozen_eval_suite"]
        ),
        truthfulness_summary=(
            "The improvement loop now reuses a persisted improve-review snapshot and explicit release-gate decision, so promotion judgment is no longer tied only to the same fresh bundle assembly pass."
            if persisted_improve_gate_ready
            else "The improvement loop now consumes frozen eval, decision memory, validation, and release-gate evidence explicitly, but promotion judgment still remains watch-level because the same runtime assembles the overall bundle it is judging."
        ),
        context_pack_ref=context_pack["context_pack_id"],
        eval_run_ref=eval_run_report["eval_run_report_id"],
        dimension_scores=[
            {
                "dimension_key": "pm_leverage",
                "score": 5,
                "rationale": "The repo now converts sub-5 features into named bounded slices and releases instead of vague future work.",
                "evidence_refs": [
                    improvement_loop_state["improvement_loop_state_id"],
                    portfolio_review_ref,
                ],
            },
            {
                "dimension_key": "output_quality",
                "score": 5,
                "rationale": "The scoring, portfolio review, and release-gate artifacts now form one coherent improvement accounting system.",
                "evidence_refs": [
                    foundation_bundle["feature_scorecard"]["feature_scorecard_id"],
                    portfolio_review_ref,
                ],
            },
            {
                "dimension_key": "reliability",
                "score": 5 if persisted_improve_gate_ready else 4,
                "rationale": (
                    "The loop now cites a persisted improve-review snapshot and explicit release-gate decision, which makes the release judgment path materially more independent from the current bundle assembly pass."
                    if persisted_improve_gate_ready
                    else "The loop has refreshed across multiple promoted slices and now explicitly references eval, validation, and decision-memory evidence, but it is not yet independent enough for final promotion judgment."
                ),
                "evidence_refs": [
                    improvement_loop_state["improvement_loop_state_id"],
                    completion_validation_report["validation_lane_report_id"],
                    improve_release_gate_ref,
                    "release_4_2_0",
                    "release_4_3_0",
                ],
            },
            {
                "dimension_key": "autonomy_quality",
                "score": 5 if persisted_improve_gate_ready else 4,
                "rationale": (
                    "The loop stays supervised, but it now depends on a prior persisted review snapshot and explicit gate artifact instead of relying only on self-narration from the same run."
                    if persisted_improve_gate_ready
                    else "The loop stays supervised and now records the next bounded hardening cycle with explicit release-gate inputs instead of relying only on self-narration."
                ),
                "evidence_refs": [
                    improvement_loop_state["improvement_loop_state_id"],
                    completion_manual_record["manual_validation_record_id"],
                    decision_log["decision_log_id"],
                    improve_release_gate_ref,
                ],
            },
            {
                "dimension_key": "repeatability",
                "score": 5 if persisted_improve_gate_ready else 4,
                "rationale": (
                    "Persisted improve reviews and explicit gate artifacts now make the loop repeatable across runs without depending on a single fresh narrator pass."
                    if persisted_improve_gate_ready
                    else "Repeated slice scoring and Ralph promotion make the loop a stable operating behavior, though final promotion still needs stronger independence from the builder surface."
                ),
                "evidence_refs": [
                    "release_4_1_0",
                    "release_4_2_0",
                    "release_4_3_0",
                ],
            },
        ],
        reviewer_status="pass",
        reviewer_summary=(
            "The improvement loop now has a persisted improve-review and release-gate proof path, so it can count as the bounded scoring standard for this baseline."
            if persisted_improve_gate_ready
            else "The improvement loop should stay active and is materially stronger now that it consumes explicit eval, decision-memory, validation, and release-gate evidence, but it is still not an independent final judge of promotion."
        ),
        tester_status="pass" if persisted_improve_gate_ready else "revise",
        tester_summary=(
            "Cross-run persisted review evidence and the explicit release-gate artifact now give the scoring loop enough separation to clear the bounded proof bar."
            if persisted_improve_gate_ready
            else "Cross-references, validation, decision-memory, and release-gate references now strengthen the loop, but final promotion judgment is still too tightly coupled to the runtime that assembles the result."
        ),
        manual_status="accept",
        manual_summary=(
            "Keep using the persisted improve-review and release-gate path as the scoring standard for the bounded baseline."
            if persisted_improve_gate_ready
            else "Keep the scoring loop in place as a watch-level internal-use standard, but do not let it act as the final independent promotion judge yet."
        ),
        blocked_by=(
            []
            if persisted_improve_gate_ready
            else [
                "The scoring loop still assigns final promotion judgment from the same runtime surface that assembles the evidence bundle.",
            ]
        ),
        feedback_items=(
            []
            if persisted_improve_gate_ready
            else [
                _feedback_item(
                    feedback_id="score_feedback_independent_eval",
                    summary="Introduce a truly frozen eval suite and route promotion through it before letting the improvement loop call the baseline healthy.",
                    impact_level="high",
                    recommended_action="Use the frozen eval suite as the gating mechanism for future promotion decisions.",
                    route_targets=["improvement_loop_state", "release_scope_recommendation"],
                    linked_dimension_keys=["reliability", "repeatability"],
                    linked_artifact_refs=[eval_suite_manifest["eval_suite_manifest_id"], eval_run_report["eval_run_report_id"]],
                )
            ]
        ),
        next_action=(
            "Keep the persisted improve-review snapshot and release-gate decision as the scoring standard for future baseline refreshes."
            if persisted_improve_gate_ready
            else "Keep the eval suite, decision memory, validation, and release-gate evidence as first-class inputs while extending the selected V5 lifecycle-traceability bundle from the cleared bounded baseline."
        ),
        generated_at=generated_at,
    )
    eval_run_report = _build_eval_run_report(
        workspace_id=workspace_id,
        eval_suite_manifest=eval_suite_manifest,
        discover_scorecard=discover_scorecard,
        docs_alignment_scorecard=docs_alignment_scorecard,
        presentation_scorecard=presentation_scorecard,
        runtime_control_surface_scorecard=runtime_control_surface_scorecard,
        self_improvement_scorecard=self_improvement_scorecard,
        decision_log=decision_log,
        strategic_memory=strategic_memory,
        generated_at=generated_at,
    )
    context_pack = {
        "schema_version": "1.0.0",
        "context_pack_id": context_pack["context_pack_id"],
        "workspace_id": workspace_id,
        "request_summary": context_pack_request_summary,
        "decision_to_be_made": context_pack_decision_to_be_made,
        "status": "watch",
        "audience": context_pack_audience,
        "mission_router": mission_router,
        "steering_context": steering_context,
        "quality_contract": _quality_contract(
            audience=context_pack_audience,
            decision_needed="Decide whether the current runtime can score and narrate itself without stronger provenance and eval controls.",
            evidence=[
                "Current next-version scoring still combines generated state with seeded artifacts.",
                "The frozen eval suite now ties its blocked state to the actual weak slices instead of duplicated synthetic cases.",
            ],
            alternatives=[
                "Promote the runtime as-is and accept lower truthfulness.",
                "Keep the runtime in watch mode while the remaining bounded-baseline gaps are closed.",
            ],
            recommendation="Keep the bundle in watch mode and use the bounded baseline to make truthfulness, evals, and decision memory first-class release inputs.",
            metrics=[
                "regression_count",
                "mixed_provenance_feature_count",
                "stale_decision_review_count",
            ],
            risks=[
                "The control surface can still sound healthier than it is.",
                "Scores can drift if eval evidence is not frozen and visible.",
            ],
            owner="ProductOS PM",
            next_action="Route the truthful control surface and self-improvement loop back into bounded fixes before promotion.",
        ),
        "evidence_bundle": context_pack_evidence_bundle,
        "contradictions": [
            "The CLI previously reported an all-green baseline while the review model described unresolved truthfulness gaps.",
        ],
        "open_questions": context_pack_open_questions,
        "source_artifact_ids": context_pack_source_artifact_ids,
        "recommended_next_action": context_pack_recommended_next_action,
        "created_at": generated_at,
        "updated_at": generated_at,
    }
    autonomous_pm_swarm_plan = {
        "schema_version": "1.0.0",
        "autonomous_pm_swarm_plan_id": f"autonomous_pm_swarm_plan_{workspace_id}_internal_governed",
        "workspace_id": workspace_id,
        "status": "planned",
        "plan_scope": "Internal governed swarm expansion for broader autonomous PM coverage behind the repo control surface.",
        "mission_summary": (
            "Coordinate specialist personas across discovery, research, shaping, review, and validation so ProductOS can run "
            "broader autonomous PM missions without dropping PM gates or Ralph-loop discipline."
        ),
        "release_boundary": "deferred_external_claim",
        "operating_mode": "review_gated_autonomy",
        "active_persona_keys": [
            "ai_orchestrator",
            "ai_discoverer",
            "ai_researcher",
            "ai_product_shaper",
            "ai_reviewer",
            "ai_tester",
            "pm_builder",
        ],
        "success_metrics": [
            "time_from_signal_to_pm_reviewable_package",
            "blocked_loop_recovery_rate",
            "duplicate_route_prevention_rate",
        ],
        "swarm_routes": [
            {
                "route_id": "route_signal_triage",
                "persona_key": "ai_discoverer",
                "objective": "Route repeated or high-signal inputs into one bounded mission queue before downstream work starts.",
                "stage_refs": ["inspect", "refine", "validate"],
                "max_retries": 2,
                "exit_condition": "Only non-duplicate, explainable, and high-signal work reaches the active swarm mission queue.",
            },
            {
                "route_id": "route_problem_to_plan",
                "persona_key": "ai_product_shaper",
                "objective": "Turn validated evidence into a PM-reviewable recommendation pack with explicit unresolved questions.",
                "stage_refs": ["implement", "refine", "validate", "fix", "revalidate"],
                "max_retries": 2,
                "exit_condition": "The PM receives one reviewable package with clear evidence, recommendation, risks, and next action.",
            },
        ],
        "review_stack": [
            {
                "reviewer_role": "AI Reviewer",
                "trigger_condition": "Any route that changes problem framing, recommendation posture, or release implication.",
                "decision_scope": "Logic, traceability, and contradiction handling.",
            },
            {
                "reviewer_role": "AI Tester",
                "trigger_condition": "Any route that emits score-bearing artifacts or modifies control-surface state.",
                "decision_scope": "Schema, workflow, and regression validation.",
            },
            {
                "reviewer_role": "PM Builder",
                "trigger_condition": "Any route that requests scope commitment, stakeholder communication, or release movement.",
                "decision_scope": "Final approval, deferral, or rejection.",
            },
        ],
        "anti_loop_controls": {
            "max_parallel_routes": 3,
            "max_retries_per_stage": 2,
            "stale_loop_after_hours": 24,
            "duplicate_route_policy": "Collapse duplicate work into the active route and update the shared rationale instead of opening a second mission.",
            "contradiction_escalation": "Escalate conflicting recommendations to reviewer and PM gate before any route is allowed to advance.",
            "blocked_state_action": "Pause the affected route, record the blocker, and emit one explicit PM-visible next action.",
        },
        "ralph_plan": {
            "required_iteration_count": 7,
            "current_iteration_count": 7,
            "last_completed_stage": "refine",
            "next_stage": "validate",
        },
        "evidence_refs": [
            "core/docs/autonomous-pm-swarm-model.md",
            "core/docs/ai-agent-persona-operating-model.md",
            context_pack["context_pack_id"],
            eval_run_report["eval_run_report_id"],
            f"cockpit_state_{workspace_id}_next_version",
            f"orchestration_state_{workspace_id}_next_version",
        ],
        "source_artifact_ids": [
            context_pack["context_pack_id"],
            eval_run_report["eval_run_report_id"],
            improvement_loop_state["improvement_loop_state_id"],
            decision_log["decision_log_id"],
        ],
        "next_action": "Keep the swarm internal, validate the route plan against the next-version runtime, and only broaden the claim after repeated outcome-review proof exists.",
        "generated_at": generated_at,
    }
    autonomous_pm_swarm_scorecard = _scorecard(
        workspace_id=workspace_id,
        feature_id="autonomous_pm_swarm",
        feature_name="Governed autonomous PM swarm",
        loop_id="cross_cutting",
        benchmark_ref=foundation_bundle["pm_superpower_benchmark"]["pm_superpower_benchmark_id"],
        validation_tier="tier_2",
        overall_score=4,
        scenarios=[
            {
                "scenario_id": "scn_swarm_plan_definition",
                "title": "Define the governed swarm plan from current runtime contracts",
                "scenario_type": "workflow_run",
                "result": "passed",
                "summary": "ProductOS can now express the broader swarm as one internal governed plan with routes, review triggers, and anti-loop controls instead of prompt-only intent.",
                "evidence_refs": [
                    autonomous_pm_swarm_plan["autonomous_pm_swarm_plan_id"],
                    context_pack["context_pack_id"],
                ],
            },
            {
                "scenario_id": "scn_swarm_claim_boundary_review",
                "title": "Hold the external claim boundary while expanding internal swarm coverage",
                "scenario_type": "manual_review",
                "result": "passed",
                "summary": "The broader swarm is visible and actionable internally, but the release boundary still keeps autonomous PM replacement claims out of the external promise set.",
                "evidence_refs": [
                    autonomous_pm_swarm_plan["autonomous_pm_swarm_plan_id"],
                    "core/docs/v7-1-scope-brief.md",
                ],
            },
        ],
        evidence_refs=[
            autonomous_pm_swarm_plan["autonomous_pm_swarm_plan_id"],
            context_pack["context_pack_id"],
            eval_run_report["eval_run_report_id"],
            improvement_loop_state["improvement_loop_state_id"],
            f"cockpit_state_{workspace_id}_next_version",
            f"orchestration_state_{workspace_id}_next_version",
        ],
        provenance_classification="real",
        score_basis=["autonomous_pm_swarm_plan", "runtime_control_surface", "ralph_iteration_target"],
        truthfulness_summary="ProductOS now has a governed internal swarm plan and runtime surfacing for broader autonomous PM work, but the capability remains explicitly internal-only until repeated outcome proof exists.",
        context_pack_ref=context_pack["context_pack_id"],
        eval_run_ref=eval_run_report["eval_run_report_id"],
        dimension_scores=[
            {
                "dimension_key": "pm_leverage",
                "score": 4,
                "rationale": "The PM can supervise one bounded swarm mission without reconstructing the route plan or reviewer stack from scratch.",
                "evidence_refs": [
                    autonomous_pm_swarm_plan["autonomous_pm_swarm_plan_id"],
                    context_pack["context_pack_id"],
                ],
            },
            {
                "dimension_key": "output_quality",
                "score": 4,
                "rationale": "The swarm plan makes route ownership, review triggers, and exit conditions explicit enough to be reviewable and reusable.",
                "evidence_refs": [
                    autonomous_pm_swarm_plan["autonomous_pm_swarm_plan_id"],
                    "core/docs/autonomous-pm-swarm-model.md",
                ],
            },
            {
                "dimension_key": "reliability",
                "score": 4,
                "rationale": "Anti-loop controls, PM gates, and Ralph stage requirements are now encoded before broader execution begins.",
                "evidence_refs": [
                    autonomous_pm_swarm_plan["autonomous_pm_swarm_plan_id"],
                    eval_run_report["eval_run_report_id"],
                ],
            },
            {
                "dimension_key": "autonomy_quality",
                "score": 4,
                "rationale": "The plan expands autonomous coverage while keeping review-gated behavior and blocked-state handling explicit.",
                "evidence_refs": [
                    autonomous_pm_swarm_plan["autonomous_pm_swarm_plan_id"],
                    f"orchestration_state_{workspace_id}_next_version",
                ],
            },
            {
                "dimension_key": "repeatability",
                "score": 4,
                "rationale": "The swarm now has a repo-native plan artifact that can be scored, re-run, and hardened through the same improve phase on future iterations.",
                "evidence_refs": [
                    autonomous_pm_swarm_plan["autonomous_pm_swarm_plan_id"],
                    improvement_loop_state["improvement_loop_state_id"],
                ],
            },
        ],
        reviewer_status="pass",
        reviewer_summary="The swarm plan is bounded, legible, and keeps PM approval and contradiction escalation explicit.",
        tester_status="pass",
        tester_summary="The new swarm artifact validates structurally and now lives in the same runtime surface as the rest of the next-version bundle.",
        manual_status="accept",
        manual_summary="Keep the broader swarm in internal use while one bounded mission proves outcome movement before any release-scope change.",
        blocked_by=[
            "External autonomous PM replacement and open-ended swarm claims remain deferred until repeated real runs prove outcome movement."
        ],
        feedback_items=[
            _feedback_item(
                feedback_id="score_feedback_swarm_outcome_proof",
                summary="Run one bounded internal swarm mission and score its actual outcome movement before broadening the claim set.",
                impact_level="high",
                recommended_action="Route the next broader autonomous PM slice through the governed swarm plan, capture outcome review evidence, and rescore readiness.",
                route_targets=["improvement_loop_state", "feedback_cluster_state"],
                linked_dimension_keys=["pm_leverage", "repeatability"],
                linked_artifact_refs=[
                    autonomous_pm_swarm_plan["autonomous_pm_swarm_plan_id"],
                    improvement_loop_state["improvement_loop_state_id"],
                ],
            )
        ],
        next_action="Keep the swarm internal, run one bounded mission through outcome review, and rescore only after repeatable evidence exists.",
        generated_at=generated_at,
    )

    discover_scorecard_id = discover_scorecard["feature_scorecard_id"]
    docs_alignment_scorecard_id = docs_alignment_scorecard["feature_scorecard_id"]
    presentation_scorecard_id = presentation_scorecard["feature_scorecard_id"]
    weekly_pm_autopilot_scorecard_id = weekly_pm_autopilot_scorecard["feature_scorecard_id"]
    market_intelligence_scorecard_id = market_intelligence_scorecard["feature_scorecard_id"]
    runtime_control_surface_scorecard_id = runtime_control_surface_scorecard["feature_scorecard_id"]
    agent_adapter_scorecard_id = agent_adapter_scorecard["feature_scorecard_id"]
    self_improvement_scorecard_id = self_improvement_scorecard["feature_scorecard_id"]
    autonomous_pm_swarm_scorecard_id = autonomous_pm_swarm_scorecard["feature_scorecard_id"]
    feature_scorecards = [
        discover_scorecard,
        docs_alignment_scorecard,
        presentation_scorecard,
        weekly_pm_autopilot_scorecard,
        market_intelligence_scorecard,
        runtime_control_surface_scorecard,
        agent_adapter_scorecard,
        self_improvement_scorecard,
    ]
    scorecard_id_map = {scorecard["feature_id"]: scorecard["feature_scorecard_id"] for scorecard in feature_scorecards}
    prioritized_scorecards = sorted(
        feature_scorecards,
        key=lambda scorecard: (
            scorecard["overall_score"],
            0 if scorecard["provenance_classification"] == "mixed" else 1,
            scorecard["feature_name"],
        ),
    )
    next_priority_scorecard = prioritized_scorecards[0]
    next_priority_feature_id = next_priority_scorecard["feature_id"]
    next_priority_scorecard_id = next_priority_scorecard["feature_scorecard_id"]
    promoted_feature_ids = [scorecard["feature_id"] for scorecard in feature_scorecards if scorecard["overall_score"] == 5]
    internal_use_feature_ids = [
        scorecard["feature_id"]
        for scorecard in feature_scorecards
        if scorecard["overall_score"] == 4
    ]
    active_improvement_feature_ids = [
        scorecard["feature_id"]
        for scorecard in feature_scorecards
        if scorecard["overall_score"] < 4
    ]
    blocked_feature_ids = [
        scorecard["feature_id"]
        for scorecard in feature_scorecards
        if scorecard["adoption_recommendation"] == "block"
    ]
    mixed_provenance_feature_ids = [
        scorecard["feature_id"]
        for scorecard in feature_scorecards
        if scorecard["provenance_classification"] == "mixed"
    ]
    unresolved_mixed_provenance_feature_ids = [
        scorecard["feature_id"]
        for scorecard in feature_scorecards
        if scorecard["provenance_classification"] == "mixed" and scorecard["overall_score"] < 4
    ]
    research_gate_blockers = external_research_gate_blockers(
        research_brief=workspace_research_brief,
        external_research_plan=workspace_external_research_plan,
        external_research_source_discovery=workspace_external_research_source_discovery,
        external_research_feed_registry=workspace_external_research_feed_registry,
        selected_manifest=workspace_selected_research_manifest,
        external_research_review=workspace_external_research_review,
    )
    truthfulness_status = (
        "blocked"
        if research_gate_blockers
        else "watch" if unresolved_mixed_provenance_feature_ids or eval_run_report["regression_count"] else "healthy"
    )
    market_intelligence_gap_summary = (
        "Persisted governed external research still has unresolved readiness blockers, so customer-facing market claims remain blocked."
        if research_gate_blockers
        else "Evidence-backed and strong, but kept internal-use while broader release claims stay in watch mode."
    )
    discover_promoted = discover_scorecard["overall_score"] >= 4
    docs_alignment_promoted = docs_alignment_scorecard["overall_score"] >= 4
    presentation_promoted = presentation_scorecard["overall_score"] >= 4
    weekly_pm_autopilot_promoted = weekly_pm_autopilot_scorecard["overall_score"] >= 4
    runtime_control_surface_promoted = runtime_control_surface_scorecard["overall_score"] == 5
    self_improvement_promoted = self_improvement_scorecard["overall_score"] == 5
    next_version_baseline_promoted = False
    all_named_superpowers_promoted = False

    feature_portfolio_review = {
        "schema_version": "1.0.0",
        "feature_portfolio_review_id": f"feature_portfolio_review_{workspace_id}_next_version_baseline",
        "workspace_id": workspace_id,
        "review_scope": "Bounded baseline review across the current ProductOS self-hosting workspace, scored with explicit provenance and frozen eval inputs.",
        "benchmark_ref": foundation_bundle["pm_superpower_benchmark"]["pm_superpower_benchmark_id"],
        "adapter_registry_ref": runtime_adapter_registry["runtime_adapter_registry_id"],
        "truthfulness_status": truthfulness_status,
        "eval_run_ref": eval_run_report["eval_run_report_id"],
        "scorecard_refs": [
            discover_scorecard_id,
            docs_alignment_scorecard_id,
            presentation_scorecard_id,
            weekly_pm_autopilot_scorecard_id,
            market_intelligence_scorecard_id,
            runtime_control_surface_scorecard_id,
            agent_adapter_scorecard_id,
            self_improvement_scorecard_id,
        ],
        "feature_summaries": [
            {
                "feature_id": discover_scorecard["feature_id"],
                "feature_name": discover_scorecard["feature_name"],
                "loop_id": discover_scorecard["loop_id"],
                "scorecard_ref": discover_scorecard_id,
                "overall_score": discover_scorecard["overall_score"],
                "adoption_recommendation": discover_scorecard["adoption_recommendation"],
                "gap_summary": (
                    "Persisted discover outputs now back the promoted decision-package path."
                    if discover_scorecard["provenance_classification"] == "real"
                    else "Strong live-output path, but still scored as watch-level because the promotion logic mixes fresh outputs with generated bundle narration."
                ),
                "provenance_classification": discover_scorecard["provenance_classification"],
                "next_action": discover_scorecard["next_action"],
            },
            {
                "feature_id": docs_alignment_scorecard["feature_id"],
                "feature_name": docs_alignment_scorecard["feature_name"],
                "loop_id": docs_alignment_scorecard["loop_id"],
                "scorecard_ref": docs_alignment_scorecard_id,
                "overall_score": docs_alignment_scorecard["overall_score"],
                "adoption_recommendation": docs_alignment_scorecard["adoption_recommendation"],
                "gap_summary": "Strongest internal alignment slice, but broader promotion is still gated by the remaining truthfulness work.",
                "provenance_classification": docs_alignment_scorecard["provenance_classification"],
                "next_action": docs_alignment_scorecard["next_action"],
            },
            {
                "feature_id": presentation_scorecard["feature_id"],
                "feature_name": presentation_scorecard["feature_name"],
                "loop_id": presentation_scorecard["loop_id"],
                "scorecard_ref": presentation_scorecard_id,
                "overall_score": presentation_scorecard["overall_score"],
                "adoption_recommendation": presentation_scorecard["adoption_recommendation"],
                "gap_summary": (
                    "Persisted story, render, and publish artifacts now back the governed presentation path."
                    if presentation_scorecard["provenance_classification"] == "real"
                    else "High-quality internal presentation path, but still inherits mixed release provenance."
                ),
                "provenance_classification": presentation_scorecard["provenance_classification"],
                "next_action": presentation_scorecard["next_action"],
            },
            {
                "feature_id": weekly_pm_autopilot_scorecard["feature_id"],
                "feature_name": weekly_pm_autopilot_scorecard["feature_name"],
                "loop_id": weekly_pm_autopilot_scorecard["loop_id"],
                "scorecard_ref": weekly_pm_autopilot_scorecard_id,
                "overall_score": weekly_pm_autopilot_scorecard["overall_score"],
                "adoption_recommendation": weekly_pm_autopilot_scorecard["adoption_recommendation"],
                "gap_summary": (
                    "Persisted weekly operator outputs now back the supervised autopilot standard."
                    if weekly_pm_autopilot_scorecard["provenance_classification"] == "real"
                    else "Useful operator bundle, but still too seeded to claim a true weekly autopilot standard."
                ),
                "provenance_classification": weekly_pm_autopilot_scorecard["provenance_classification"],
                "next_action": weekly_pm_autopilot_scorecard["next_action"],
            },
            {
                "feature_id": market_intelligence_scorecard["feature_id"],
                "feature_name": market_intelligence_scorecard["feature_name"],
                "loop_id": market_intelligence_scorecard["loop_id"],
                "scorecard_ref": market_intelligence_scorecard_id,
                "overall_score": market_intelligence_scorecard["overall_score"],
                "adoption_recommendation": market_intelligence_scorecard["adoption_recommendation"],
                "gap_summary": market_intelligence_gap_summary,
                "provenance_classification": market_intelligence_scorecard["provenance_classification"],
                "next_action": market_intelligence_scorecard["next_action"],
            },
            {
                "feature_id": runtime_control_surface_scorecard["feature_id"],
                "feature_name": runtime_control_surface_scorecard["feature_name"],
                "loop_id": runtime_control_surface_scorecard["loop_id"],
                "scorecard_ref": runtime_control_surface_scorecard_id,
                "overall_score": runtime_control_surface_scorecard["overall_score"],
                "adoption_recommendation": runtime_control_surface_scorecard["adoption_recommendation"],
                "gap_summary": "The CLI now reports blocked promotion honestly, but it still stays in watch mode because mixed-provenance control-surface claims remain.",
                "provenance_classification": runtime_control_surface_scorecard["provenance_classification"],
                "next_action": runtime_control_surface_scorecard["next_action"],
            },
            {
                "feature_id": agent_adapter_scorecard["feature_id"],
                "feature_name": agent_adapter_scorecard["feature_name"],
                "loop_id": agent_adapter_scorecard["loop_id"],
                "scorecard_ref": agent_adapter_scorecard_id,
                "overall_score": agent_adapter_scorecard["overall_score"],
                "adoption_recommendation": agent_adapter_scorecard["adoption_recommendation"],
                "gap_summary": "Strongest promoted slice because parity proof remains explicit and mostly independent of the bundle narrator.",
                "provenance_classification": agent_adapter_scorecard["provenance_classification"],
                "next_action": agent_adapter_scorecard["next_action"],
            },
            {
                "feature_id": self_improvement_scorecard["feature_id"],
                "feature_name": self_improvement_scorecard["feature_name"],
                "loop_id": self_improvement_scorecard["loop_id"],
                "scorecard_ref": self_improvement_scorecard_id,
                "overall_score": self_improvement_scorecard["overall_score"],
                "adoption_recommendation": self_improvement_scorecard["adoption_recommendation"],
                "gap_summary": (
                    "Persisted improve-review and release-gate artifacts now back the scoring loop."
                    if self_improvement_scorecard["overall_score"] == 5
                    else "Top-priority bounded-baseline gap: scoring is still too coupled to the same runtime that generates the evidence bundle."
                ),
                "provenance_classification": self_improvement_scorecard["provenance_classification"],
                "next_action": self_improvement_scorecard["next_action"],
            },
        ],
        "top_priority_feature_id": next_priority_feature_id,
        "promoted_feature_ids": promoted_feature_ids,
        "internal_use_feature_ids": internal_use_feature_ids,
        "active_improvement_feature_ids": active_improvement_feature_ids,
        "blocked_feature_ids": blocked_feature_ids,
        "highlighted_risks": [
            "Mixed provenance still affects score-bearing control-surface and improvement-loop claims.",
            f"Frozen eval suite regressions currently total {eval_run_report['regression_count']} cases.",
            *research_gate_blockers,
        ],
        "next_action": (
            "Resolve the governed external research blockers, rerun the research refresh, and only then resume bounded-baseline promotion."
            if research_gate_blockers
            else "Treat self_improvement_loop as the first remaining hardening target, while keeping the improved truthful control surface in place and reducing its remaining provenance debt."
        ),
        "generated_at": generated_at,
    }
    if research_gate_blockers:
        feature_portfolio_review["top_priority_feature_id"] = "market_intelligence"
    promotion_gate = evaluate_promotion_gate(
        eval_run_report=eval_run_report,
        feature_portfolio_review=feature_portfolio_review,
        research_brief=workspace_research_brief,
        external_research_plan=workspace_external_research_plan,
        external_research_source_discovery=workspace_external_research_source_discovery,
        external_research_feed_registry=workspace_external_research_feed_registry,
        selected_manifest=workspace_selected_research_manifest,
        external_research_review=workspace_external_research_review,
    )
    next_version_release_gate_decision = {
        "schema_version": "1.0.0",
        "release_gate_decision_id": f"release_gate_decision_{workspace_id}_next_version",
        "workspace_id": workspace_id,
        "target_release": "v7_1_0",
        "decision": "go" if promotion_gate["status"] == "ready" else "no_go",
        "pm_benchmark_ref": foundation_bundle["pm_superpower_benchmark"]["pm_superpower_benchmark_id"],
        "runtime_scenario_report_ref": adapter_parity_report["runtime_scenario_report_id"],
        "release_readiness_ref": completion_validation_report["validation_lane_report_id"],
        "rationale": (
            "The bounded next-version baseline now clears the eval and truthfulness gate, so the release hardening slice is ready to act as the supervised external-release core."
            if promotion_gate["status"] == "ready"
            else (
                "The bounded next-version baseline still has governed external research blockers, so the external-release claim should stay blocked until the research loop clears its evidence posture."
                if research_gate_blockers
                else "The bounded next-version baseline still has open release hardening gaps, so the external-release claim should stay blocked until eval and truth signals agree."
            )
        ),
        "next_action": (
            "Keep the current baseline stable and use this gate artifact as the persisted scoring reference for future improve runs."
            if promotion_gate["status"] == "ready"
            else (
                "Resolve the governed external research blockers, persist refreshed research loop artifacts, and rerun the release gate."
                if research_gate_blockers
                else "Resolve the blocked gate reasons, persist a fresh improve review, and rerun the release gate."
            )
        ),
        "known_gaps": (
            ["No bounded-baseline gate blockers remain; keep future expansion scoped and evidence-backed."]
            if promotion_gate["status"] == "ready"
            else promotion_gate["blockers"]
        ),
        "blocker_categories": promotion_gate["blocker_categories"],
        "deferred_items": [
            "External autonomous PM and swarm claims remain out of scope for V7.1, even while the internal governed swarm plan continues to harden.",
            "External publishing and generalized market-intelligence expansion stay deferred until after the PM superpower core is proven.",
        ],
        "generated_at": generated_at,
    }
    if promotion_gate["status"] == "ready" and not active_improvement_feature_ids:
        next_priority_feature_id = "v5_bundle_selection"
        next_priority_scorecard_id = feature_portfolio_review["feature_portfolio_review_id"]
        feature_portfolio_review["top_priority_feature_id"] = next_priority_feature_id
        feature_portfolio_review["highlighted_risks"] = [
            "No bounded-baseline blockers remain; keep the next extension disciplined by choosing one bounded V5 slice before expanding scope."
        ]
        feature_portfolio_review["next_action"] = "The bounded baseline gate is cleared. Build the selected V5 lifecycle-traceability bundle and begin the next stable extension sequence."
        context_pack.update(
            {
                "request_summary": "Review the cleared bounded baseline and execute the selected V5 lifecycle-traceability bundle.",
                "decision_to_be_made": "How should ProductOS execute the selected V5 lifecycle-traceability bundle from the cleared bounded baseline?",
                "status": "ready",
                "quality_contract": _quality_contract(
                    audience=["PM", "engineering", "leadership"],
                    decision_needed="Execute the selected V5 lifecycle-traceability bundle while preserving the cleared evidence, eval, and decision-memory contracts.",
                    evidence=[
                        "The frozen eval suite passes with zero regressions.",
                        "Portfolio truthfulness is healthy across the bounded baseline.",
                        "The control surface and self-improvement loop now consume explicit eval, validation, decision-memory, and release-gate evidence strongly enough to clear the foundation gate.",
                    ],
                    alternatives=[
                        "Build the selected lifecycle-traceability bundle now and begin the bounded extension.",
                        "Hold on V5 execution and keep the cleared bounded baseline stable without broadening scope.",
                    ],
                    recommendation="Build the selected lifecycle-traceability bundle now and start the bounded extension while keeping V5 stable until parity and promotion pass.",
                    metrics=[
                        "regression_count",
                        "mixed_provenance_feature_count",
                        "stable_promotion_status",
                    ],
                    risks=[
                        "Choosing a broader V5 headline without preserving the current evidence and eval contracts would weaken trust.",
                        "Extending scope before V5 parity and stable-promotion checks complete would create avoidable migration risk.",
                    ],
                    owner="ProductOS PM",
                    next_action="Build the selected lifecycle-traceability bundle and start the bounded extension sequence.",
                ),
                "contradictions": [],
                "open_questions": [
                    "Which parity checks and migration checks should gate the lifecycle-traceability cutover after the bundle is built?"
                ],
                "recommended_next_action": "Build the selected lifecycle-traceability bundle and start the bounded extension while keeping V5 stable until parity and promotion pass.",
                "updated_at": generated_at,
            }
        )
    improvement_loop_state.update(
        {
            "status": "validation" if promotion_gate["status"] == "blocked" else improvement_loop_state["status"],
            "loop_goal": (
                "Use the frozen eval suite and decision-memory evidence to harden the runtime control surface and self-improvement loop before any stable promotion claim."
                if promotion_gate["status"] == "blocked"
                else improvement_loop_state["loop_goal"]
            ),
            "feature_scorecard_refs": [
                runtime_control_surface_scorecard_id,
                self_improvement_scorecard_id,
                autonomous_pm_swarm_scorecard_id,
                *[
                    ref
                    for ref in improvement_loop_state.get("feature_scorecard_refs", [])
                    if ref not in {
                        runtime_control_surface_scorecard_id,
                        self_improvement_scorecard_id,
                        autonomous_pm_swarm_scorecard_id,
                    }
                ],
            ],
            "active_workers": [
                {
                    "worker_name": "feedback_collector",
                    "status": "completed",
                    "current_task": "Collected repeated feedback on truthfulness gaps and preserved the blocked-promotion evidence in the review queue.",
                },
                {
                    "worker_name": "discovery_router",
                    "status": "completed",
                    "current_task": "Routed the weakest score-bearing slice into the current hardening cycle instead of broadening scope prematurely.",
                },
                {
                    "worker_name": "improvement_planner",
                    "status": "active" if promotion_gate["status"] == "blocked" else "completed",
                "current_task": (
                        "Treat frozen evals and decision memory as first-class promotion inputs until self_improvement_loop clears the gate and the control surface provenance debt is reduced."
                        if promotion_gate["status"] == "blocked"
                        else "Prepare the next bounded expansion choice now that the current named baseline is fully promoted."
                    ),
                },
            ],
            "validation_gate": {
                "status": "active" if promotion_gate["status"] == "blocked" else improvement_loop_state["validation_gate"]["status"],
                "owner": improvement_loop_state["validation_gate"]["owner"],
                "exit_condition": "Frozen eval results, decision-memory evidence, and score-bearing control-surface claims must agree before the loop can call the baseline healthy.",
            },
            "pm_decision_gate": {
                "status": "awaiting_pm" if promotion_gate["status"] == "blocked" else improvement_loop_state["pm_decision_gate"]["status"],
                "owner": improvement_loop_state["pm_decision_gate"]["owner"],
                "exit_condition": "The PM should defer stable promotion while frozen eval regressions or mixed-provenance control-surface claims remain visible.",
            },
            "next_recommended_action": (
                "Fix self_improvement_loop first, then rerun the eval-gated improvement review while keeping the truthful blocked-state control surface in place."
                if promotion_gate["status"] == "blocked"
                else improvement_loop_state["next_recommended_action"]
            ),
        }
    )

    orchestration_state_id = f"orchestration_state_{workspace_id}_next_version"
    discover_session_id = f"discover_execution_session_{workspace_id}"
    align_session_id = f"align_execution_session_{workspace_id}"
    operate_session_id = f"operate_execution_session_{workspace_id}"
    improve_session_id = f"improve_execution_session_{workspace_id}"
    intake_routing_state_id = f"intake_routing_state_{workspace_id}_next_version"
    memory_retrieval_state_id = f"memory_retrieval_state_{workspace_id}_next_version"

    intake_routing_state = {
        "schema_version": "1.0.0",
        "intake_routing_state_id": intake_routing_state_id,
        "workspace_id": workspace_id,
        "ingestion_mode": "manual",
        "status": "routing",
        "routing_summary": "The next-version dogfood loop is routing real inbox notes and transcripts into the discover-to-PRD superpower path.",
        "active_inbox_paths": [
            _relative_path(workspace_path / "inbox" / "raw-notes"),
            _relative_path(workspace_path / "inbox" / "transcripts"),
        ],
        "intake_items": intake_items,
        "blocked_item_ids": [],
        "created_at": generated_at,
        "updated_at": generated_at,
    }

    memory_retrieved_records = [
        {
            "record_type": "artifact",
            "record_id": problem_brief["problem_brief_id"],
            "source_artifact_id": problem_brief["problem_brief_id"],
            "reason": "The current problem framing anchors the next-version discover loop.",
            "freshness_status": "fresh",
            "confidence": 0.95,
            "provenance_ref": _relative_path(artifacts_dir / "problem_brief.json"),
        },
        {
            "record_type": "artifact",
            "record_id": concept_brief["concept_brief_id"],
            "source_artifact_id": concept_brief["concept_brief_id"],
            "reason": "The current concept framing remains the source of truth for next-version shaping.",
            "freshness_status": "fresh",
            "confidence": 0.94,
            "provenance_ref": _relative_path(artifacts_dir / "concept_brief.json"),
        },
        {
            "record_type": "artifact",
            "record_id": prd["prd_id"],
            "source_artifact_id": prd["prd_id"],
            "reason": "The current PRD is the downstream package the discover loop should eventually regenerate from live inputs.",
            "freshness_status": "fresh",
            "confidence": 0.96,
            "provenance_ref": _relative_path(artifacts_dir / "prd.json"),
        },
        {
            "record_type": "issue",
            "record_id": feedback_log["entries"][0]["feedback_id"],
            "source_artifact_id": feedback_log["feedback_log_id"],
            "reason": "Repeated PM pain should shape what becomes a next-version superpower first.",
            "freshness_status": "fresh",
            "confidence": 0.91,
            "provenance_ref": _relative_path(artifacts_dir / "productos_feedback_log.example.json"),
        },
        {
            "record_type": "artifact",
            "record_id": foundation_bundle["pm_superpower_benchmark"]["pm_superpower_benchmark_id"],
            "source_artifact_id": foundation_bundle["pm_superpower_benchmark"]["pm_superpower_benchmark_id"],
            "reason": "The benchmark remains the release bar for every next-version loop.",
            "freshness_status": "fresh",
            "confidence": 0.93,
            "provenance_ref": "generated_v4_foundation_bundle",
        },
        {
            "record_type": "artifact",
            "record_id": discover_prd["prd_id"],
            "source_artifact_id": discover_prd["prd_id"],
            "reason": "The promoted discover slice now proves the repo can generate a fresh next-version PRD package from live inbox inputs.",
            "freshness_status": "fresh",
            "confidence": 0.98,
            "provenance_ref": "generated_next_version_bundle",
        },
    ]
    if workspace_mission_brief is not None:
        memory_retrieved_records.insert(
            0,
            {
                "record_type": "artifact",
                "record_id": workspace_mission_brief["mission_brief_id"],
                "source_artifact_id": workspace_mission_brief["mission_brief_id"],
                "reason": "The mission brief defines the current PM-first execution goal and should stay visible across every downstream phase.",
                "freshness_status": "fresh",
                "confidence": 0.97,
                "provenance_ref": _relative_path(artifacts_dir / "mission_brief.json"),
            },
        )
    memory_retrieval_state = {
        "schema_version": "1.0.0",
        "memory_retrieval_state_id": memory_retrieval_state_id,
        "workspace_id": workspace_id,
        "request_summary": "Retrieve the current ProductOS evidence, decision package, and repeated feedback needed to build the next-version superpower loops.",
        "status": "ready",
        "retrieval_scope": [
            "decisions",
            "evidence",
            "prior_artifacts",
            "repeated_issues",
            "strategic_memory",
        ],
        "retrieval_strategy": {
            "mission_ref": (
                workspace_mission_brief["mission_brief_id"]
                if workspace_mission_brief is not None
                else f"mission_brief_{workspace_id}_implicit_next_version"
            ),
            "steering_refs": list(steering_context["steering_refs"]),
            "priority_order": list(steering_context["memory_priority_order"]),
            "retrieval_policy_summary": "Retrieve mission-defining decisions and evidence first, then pull supporting artifacts, repeated issues, and strategic memory in the steering-defined order.",
            "default_artifact_focus": list(steering_context["default_artifact_focus"]),
        },
        "provenance_status": "complete",
        "retrieved_records": memory_retrieved_records,
        "unresolved_questions": [
            (
                "Which external publication or packaging slice should follow the fully promoted baseline?"
                if all_named_superpowers_promoted
                else (
                    "Which broader distribution path should lead the next governed market-intelligence hardening cycle?"
                    if next_version_baseline_promoted
                    else "How should the weekly PM autopilot reuse the promoted discover control surface without adding unnecessary review noise?"
                )
            )
        ],
        "provenance_warnings": [],
        "created_at": generated_at,
        "updated_at": generated_at,
    }

    adapter_session_id = f"adapter_{adapter_name}_thin" if adapter_name != "claude" else "adapter_claude_style_thin"
    discover_session_status = "completed" if discover_promoted else "awaiting_review"
    discover_event_messages = [
        ("created", "Discover session created from the live inbox and current workspace artifacts."),
        ("started", "Discover loop routing started."),
        ("verification_passed", "The current route and output references are structurally valid."),
    ]
    if discover_promoted:
        discover_event_messages.append(
            ("completed", "The discover loop produced a fresh same-day decision package and was promoted as the current standard.")
        )
    else:
        discover_event_messages.append(
            ("review_requested", "PM review is needed before the discover loop can claim superpower status.")
        )
    align_session_status = "completed" if docs_alignment_promoted and presentation_promoted else "created"
    align_event_messages = [
        ("created", "Align session created from the current readable docs and presentation artifacts."),
    ]
    if docs_alignment_promoted and presentation_promoted:
        align_event_messages.extend(
            [
                ("started", "The aligned docs-and-deck path refreshed from the promoted discover package."),
                ("completed", "The readable-doc and presentation paths now act as the default aligned package for the next-version baseline."),
            ]
        )
    operate_session_status = "completed" if weekly_pm_autopilot_promoted else ("awaiting_review" if discover_promoted else "created")
    operate_event_messages = [
        ("created", "Operate session created from current queues, issue state, and release context."),
    ]
    if weekly_pm_autopilot_promoted:
        operate_event_messages.extend(
            [
                ("started", "Weekly operator routing started from the current queue, issue, and release bundle."),
                ("completed", "The weekly PM autopilot now emits the supervised operator summary as part of the promoted baseline."),
            ]
        )
    elif discover_promoted:
        operate_event_messages.append(
            ("review_requested", "Weekly PM autopilot is now the next bounded slice requiring PM review.")
        )
    improve_session_status = "completed" if self_improvement_promoted else "awaiting_review"
    improve_review_required = not self_improvement_promoted
    improve_event_messages = [
        ("created", "Improve session created from the new portfolio review and existing improvement loop."),
    ]
    if self_improvement_promoted:
        improve_event_messages.extend(
            [
                ("started", "The portfolio was refreshed after the promoted next-version baseline completed."),
                (
                    "completed",
                    "The refreshed portfolio now shows every named current slice at 5 out of 5 and is ready to choose the next bounded expansion slice."
                    if all_named_superpowers_promoted
                    else "The refreshed portfolio now routes the next hardening cycle to broader market-intelligence distribution posture.",
                ),
            ]
        )
    else:
        improve_event_messages.append(
            ("review_requested", "The bounded baseline now requires review of the frozen eval suite and scoring loop before promotion.")
        )

    discover_execution_session_state = _session_state(
        session_id=discover_session_id,
        workspace_id=workspace_id,
        session_name="Next-version discover to PRD session",
        status=discover_session_status,
        objective="Route live inbox inputs into a fresh next-version decision package and prove the same-day low-rewrite discover bar.",
        owner_agent="workflow",
        capability_adapter_id=selected_adapter_id,
        parent_orchestration_state_id=orchestration_state_id,
        input_refs=[item["item_id"] for item in intake_items],
        output_refs=[
            discover_problem_brief["problem_brief_id"],
            discover_concept_brief["concept_brief_id"],
            discover_prd["prd_id"],
            discover_scorecard_id,
        ],
        review_required=not discover_promoted,
        verification_status="passed",
        created_at=generated_at,
        event_messages=discover_event_messages,
    )

    align_execution_session_state = _session_state(
        session_id=align_session_id,
        workspace_id=workspace_id,
        session_name="Next-version docs and deck alignment session",
        status=align_session_status,
        objective="Package current ProductOS truth into docs and deck artifacts through one aligned path.",
        owner_agent="workflow",
        capability_adapter_id=selected_adapter_id,
        parent_orchestration_state_id=orchestration_state_id,
        input_refs=[
            prd["prd_id"],
            live_doc_sync_state["document_sync_state_id"],
            foundation_bundle["presentation_brief"]["presentation_brief_id"],
        ],
        output_refs=[
            live_doc_sync_state["document_sync_state_id"],
            docs_alignment_scorecard_id,
            presentation_scorecard_id,
        ],
        review_required=not (docs_alignment_promoted and presentation_promoted),
        verification_status="passed" if docs_alignment_promoted and presentation_promoted else "not_started",
        created_at=generated_at,
        event_messages=align_event_messages,
    )

    operate_execution_session_state = _session_state(
        session_id=operate_session_id,
        workspace_id=workspace_id,
        session_name="Next-version weekly PM operator session",
        status=operate_session_status,
        objective="Turn decisions, follow-ups, issues, and release state into one supervised weekly operator session.",
        owner_agent="workflow",
        capability_adapter_id=selected_adapter_id,
        parent_orchestration_state_id=orchestration_state_id,
        input_refs=[
            decision_queue["decision_queue_id"],
            follow_up_queue["follow_up_queue_id"],
            status_mail["status_mail_id"],
            issue_log["issue_log_id"],
        ],
        output_refs=[
            status_mail["status_mail_id"],
            issue_log["issue_log_id"],
            weekly_pm_autopilot_scorecard_id,
            runtime_control_surface_scorecard_id,
        ],
        review_required=not weekly_pm_autopilot_promoted,
        verification_status="passed" if weekly_pm_autopilot_promoted else "not_started",
        created_at=generated_at,
        event_messages=operate_event_messages,
    )

    improve_execution_session_state = _session_state(
        session_id=improve_session_id,
        workspace_id=workspace_id,
        session_name="Next-version scoring and improvement session",
        status=improve_session_status,
        objective=(
            "Route every sub-5 feature score into explicit next-version improvement work using frozen eval and decision-memory evidence as release gates."
            if promotion_gate["status"] == "blocked"
            else "Use the cleared bounded baseline to package the evidence bundle and hand off the selected V5 lifecycle-traceability build."
        ),
        owner_agent="improvement_planner",
        capability_adapter_id=selected_adapter_id,
        parent_orchestration_state_id=orchestration_state_id,
        input_refs=[
            feature_portfolio_review["feature_portfolio_review_id"],
            improvement_loop_state["improvement_loop_state_id"],
            decision_log["decision_log_id"],
            strategic_memory["strategic_memory_record_id"],
            eval_suite_manifest["eval_suite_manifest_id"],
            eval_run_report["eval_run_report_id"],
        ],
        output_refs=[
            self_improvement_scorecard_id,
            autonomous_pm_swarm_plan["autonomous_pm_swarm_plan_id"],
            autonomous_pm_swarm_scorecard_id,
            improvement_loop_state["improvement_loop_state_id"],
        ],
        review_required=improve_review_required,
        verification_status="passed" if self_improvement_promoted else "not_started",
        created_at=generated_at,
        event_messages=improve_event_messages,
    )

    mission_ref = (
        workspace_mission_brief["mission_brief_id"]
        if workspace_mission_brief is not None
        else f"mission_brief_{workspace_id}_implicit_next_version"
    )
    mission_title = (
        workspace_mission_brief["title"]
        if workspace_mission_brief is not None
        else "Implicit next-version ProductOS mission"
    )
    mission_stage = (
        "improve"
        if promotion_gate["status"] == "ready"
        else "operate" if discover_promoted else "discover"
    )
    mission_current_route_ref = (
        "route_score_and_improve"
        if promotion_gate["status"] == "ready"
        else "route_operator_autopilot" if discover_promoted else "route_discover_to_prd"
    )
    mission_next_route_ref = (
        "route_v5_bundle_selection"
        if promotion_gate["status"] == "ready"
        else "route_score_and_improve" if discover_promoted else "route_operator_autopilot"
    )
    mission_current_task_name = (
        "Choose the next bounded expansion slice"
        if promotion_gate["status"] == "ready"
        else "Promote the weekly PM autopilot route" if discover_promoted else "Promote the discover-to-PRD route"
    )
    mission_current_task_summary = (
        "The bounded baseline gate is clear, so the improvement loop should choose the next disciplined expansion instead of treating the current baseline as unfinished."
        if promotion_gate["status"] == "ready"
        else "The discover and control-surface slices are promoted, so weekly PM autopilot is now the next must-win route."
        if discover_promoted
        else "The discover route remains the first must-win mission and should turn live inbox input into a promoted decision package."
    )
    mission_current_task_status = (
        "ready_for_next_expansion"
        if promotion_gate["status"] == "ready"
        else "awaiting_pm_review" if discover_promoted else "awaiting_discover_promotion"
    )
    mission_reviewer_lane = "pm_builder" if promotion_gate["status"] == "ready" or discover_promoted else "pm_builder"
    mission_control = _mission_control_boundary(
        mission_ref=mission_ref,
        mission_title=mission_title,
        active_stage=mission_stage,
        current_route_ref=mission_current_route_ref,
        next_route_ref=mission_next_route_ref,
        current_task_name=mission_current_task_name,
        current_task_summary=mission_current_task_summary,
        current_task_status=mission_current_task_status,
        reviewer_lane=mission_reviewer_lane,
    )
    route_budget = _route_budget(
        max_parallel_routes=3,
        active_route_count=0 if promotion_gate["status"] == "ready" else 1,
        awaiting_review_count=0 if promotion_gate["status"] == "ready" else 1,
        blocked_route_count=0,
    )

    orchestration_state = {
        "schema_version": "1.0.0",
        "orchestration_state_id": orchestration_state_id,
        "workspace_id": workspace_id,
        "goal": "Operate the next-version ProductOS superpower build from one repo CLI surface while staying grounded in the current self-hosting workspace.",
        "status": "completed" if next_version_baseline_promoted else "awaiting_review",
        "coordination_summary": (
            "The discover, align, operate, and improve slices are now promoted as one repo-native next-version baseline, and every named current superpower slice now clears the 5 out of 5 bar."
            if all_named_superpowers_promoted
            else (
                "The discover, align, operate, and improve slices are now promoted as one repo-native next-version baseline; adapter parity is cleared and broader market-intelligence distribution is the next hardening surface."
                if next_version_baseline_promoted
                else (
                    "The discover and control-surface slices are now promoted, and the weekly PM autopilot is the next must-win route behind the same repo contract."
                    if discover_promoted
                    else "The discover loop is the current must-win slice, while align, operate, adapter, and improvement routes stay active behind the same repo contract."
                )
            )
        ),
        "initiating_agent": "cockpit",
        "mission_control": mission_control,
        "route_budget": route_budget,
        "active_route_ids": (
            []
            if next_version_baseline_promoted
            else (
                ["route_operator_autopilot", "route_score_and_improve"]
                if discover_promoted
                else ["route_discover_to_prd", "route_operator_autopilot"]
            )
        ),
        "blocked_route_ids": [],
        "awaiting_review_route_ids": (
            []
            if next_version_baseline_promoted
            else (
                ["route_operator_autopilot"]
                if discover_promoted
                else ["route_discover_to_prd"]
            )
        ),
        "linked_workflow_state_ids": ["wf_next_version_superpower_ops"],
        "linked_execution_session_state_ids": [
            discover_session_id,
            align_session_id,
            operate_session_id,
            improve_session_id,
        ],
        "route_plan": [
            {
                "route_id": "route_discover_to_prd",
                "agent_name": "workflow",
                "objective": "Turn live inbox notes and transcripts into a decision-ready path that can become the discover standard for the next version.",
                "rationale": (
                    "This route now anchors the promoted next-version baseline."
                    if next_version_baseline_promoted
                    else (
                        "This route is now promoted as the first completed next-version superpower slice."
                        if discover_promoted
                        else "This is the top priority feature in the current portfolio review and the clearest week-one value wedge."
                    )
                ),
                "stage": "discover",
                "status": "completed" if discover_promoted else "awaiting_review",
                "reviewer_lane": "pm_builder",
                "input_artifact_ids": [item["item_id"] for item in intake_items],
                "expected_output_artifact_ids": [
                    discover_problem_brief["problem_brief_id"],
                    discover_concept_brief["concept_brief_id"],
                    discover_prd["prd_id"],
                    discover_scorecard_id,
                ],
                "execution_session_state_id": discover_session_id,
                "next_action": (
                    "Keep the discover outputs as the current standard and hand the next bounded slice to the weekly PM autopilot route."
                    if discover_promoted
                    else "Run the live discover loop from the inbox inputs and promote the decision-ready package through PM review."
                ),
            },
            {
                "route_id": "route_docs_and_deck",
                "agent_name": "presentation",
                "objective": "Package current ProductOS truth into readable docs and a stakeholder-ready deck through one aligned path.",
                "rationale": "Alignment is now part of the promoted baseline and should refresh from the discover package without extra PM reconstruction." if next_version_baseline_promoted else "Alignment is already one of the strongest current slices and should stay usable during the next-version build.",
                "stage": "align",
                "status": "completed" if docs_alignment_promoted and presentation_promoted else "ready",
                "reviewer_lane": "ai_reviewer",
                "depends_on_route_ids": ["route_discover_to_prd"],
                "input_artifact_ids": [
                    prd["prd_id"],
                    live_doc_sync_state["document_sync_state_id"],
                    foundation_bundle["presentation_brief"]["presentation_brief_id"],
                ],
                "expected_output_artifact_ids": [
                    live_doc_sync_state["document_sync_state_id"],
                    docs_alignment_scorecard_id,
                    presentation_scorecard_id,
                ],
                "execution_session_state_id": align_session_id,
                "next_action": "Refresh the readable docs and deck from the promoted discover package whenever the mission package changes.",
            },
            {
                "route_id": "route_operator_autopilot",
                "agent_name": "cockpit",
                "objective": "Collapse current queue and release state into one supervised weekly operator path.",
                "rationale": (
                    "The weekly PM autopilot is now part of the promoted next-version baseline."
                    if next_version_baseline_promoted
                    else "The weekly PM autopilot is the next high-leverage slice after the discover loop."
                ),
                "stage": "operate",
                "status": "completed" if weekly_pm_autopilot_promoted else ("awaiting_review" if discover_promoted else "active"),
                "reviewer_lane": "pm_builder",
                "input_artifact_ids": [
                    decision_queue["decision_queue_id"],
                    follow_up_queue["follow_up_queue_id"],
                    status_mail["status_mail_id"],
                    issue_log["issue_log_id"],
                ],
                "expected_output_artifact_ids": [
                    status_mail["status_mail_id"],
                    issue_log["issue_log_id"],
                    weekly_pm_autopilot_scorecard_id,
                    runtime_control_surface_scorecard_id,
                ],
                "execution_session_state_id": operate_session_id,
                "next_action": (
                    "Keep the supervised weekly operator bundle active as part of the promoted baseline."
                    if weekly_pm_autopilot_promoted
                    else "Review the weekly PM autopilot scorecard and promote the minimum supervised operator path."
                ),
            },
            {
                "route_id": "route_score_and_improve",
                "agent_name": "improvement_planner",
                "objective": "Refresh the portfolio review and improvement loop after every major bounded slice.",
                "rationale": "Sub-5 features should always become explicit improvement work, and the loop must stay subordinate to frozen eval and decision-memory evidence before claiming promotion.",
                "stage": "improve",
                "status": "completed" if self_improvement_promoted else "awaiting_review",
                "reviewer_lane": "ai_tester",
                "depends_on_route_ids": ["route_discover_to_prd", "route_operator_autopilot"],
                "input_artifact_ids": [
                    feature_portfolio_review["feature_portfolio_review_id"],
                    improvement_loop_state["improvement_loop_state_id"],
                    decision_log["decision_log_id"],
                    strategic_memory["strategic_memory_record_id"],
                    eval_suite_manifest["eval_suite_manifest_id"],
                    eval_run_report["eval_run_report_id"],
                ],
                "expected_output_artifact_ids": [
                    self_improvement_scorecard_id,
                    autonomous_pm_swarm_plan["autonomous_pm_swarm_plan_id"],
                    autonomous_pm_swarm_scorecard_id,
                    improvement_loop_state["improvement_loop_state_id"],
                    eval_suite_manifest["eval_suite_manifest_id"],
                    eval_run_report["eval_run_report_id"],
                ],
                "execution_session_state_id": improve_session_id,
                "next_action": (
                    "Use the cleared score-refresh loop to choose the next bounded expansion slice."
                    if self_improvement_promoted
                    else "Review the weakest score-bearing slice and route the next bounded fix through frozen eval and decision memory."
                ),
            },
        ],
        "queue_impacts": [
            {
                "queue_type": "review_queue",
                "artifact_id": feature_portfolio_review["feature_portfolio_review_id"],
                "item_id": next_priority_feature_id,
                "recommended_action": "review_now",
                "reason": (
                    "The named current baseline is fully promoted, so the next review should choose the next bounded expansion slice."
                    if all_named_superpowers_promoted
                    else (
                        "The planned next-version slices are complete, so broader market-intelligence distribution posture is now the top-priority hardening surface."
                        if next_version_baseline_promoted
                        else (
                            "The weekly PM autopilot is now the top-priority feature and still sits below the promoted discover/control-surface bar."
                            if discover_promoted
                            else "The discover-to-PRD loop is the top priority feature and still sits at 3 out of 5."
                        )
                    )
                ),
                "status": "recommended",
            },
            {
                "queue_type": "follow_up_queue",
                "artifact_id": follow_up_queue["follow_up_queue_id"],
                "item_id": follow_up_queue["items"][0]["follow_up_id"],
                "recommended_action": "start",
                "reason": (
                    "Use the promoted weekly operator loop to clear the oldest recurring follow-up while the next bounded expansion slice is chosen."
                    if next_version_baseline_promoted
                    else "The weekly operator loop should absorb this recurring follow-up behavior next."
                ),
                "status": "queued",
            },
        ],
        "handoff_log": [
            {
                "timestamp": generated_at,
                "from_agent": "cockpit",
                "to_agent": "workflow",
                "handoff_type": "artifact_transfer",
                "status": "accepted",
                "artifact_ids": [feature_portfolio_review["feature_portfolio_review_id"]],
                "message": (
                    "The repo control surface completed the planned next-version slices, cleared the remaining market-intelligence distribution gap, and handed control back to the self-improvement loop for the next expansion choice."
                    if all_named_superpowers_promoted
                    else (
                        "The repo control surface completed the planned next-version slices, cleared adapter parity, and handed the next hardening cycle to broader market-intelligence distribution work."
                        if next_version_baseline_promoted
                        else (
                            "The repo control surface promoted discover and handed the next bounded slice to the weekly operator route."
                            if discover_promoted
                            else "The repo control surface handed the highest-priority next-version slice to the discover route."
                        )
                    )
                ),
            }
        ],
        "retry_events": [],
        "escalations": (
            [
                {
                    "timestamp": generated_at,
                    "owner": "ProductOS PM",
                    "reason": "Final completion review confirmed the repo-native next-version baseline is ready for stable promotion.",
                    "status": "resolved",
                }
            ]
            if next_version_baseline_promoted
            else []
        ),
        "created_at": generated_at,
        "updated_at": generated_at,
    }

    cockpit_state = {
        "schema_version": "1.0.0",
        "cockpit_state_id": f"cockpit_state_{workspace_id}_next_version",
        "workspace_id": workspace_id,
        "mode": "status" if next_version_baseline_promoted else ("review" if discover_promoted else "plan"),
        "status": "completed" if next_version_baseline_promoted else "awaiting_review",
        "coordination_status": "healthy",
        "mission_control": mission_control,
        "request_summary": (
            "Operate the completed next-version ProductOS baseline from one repo CLI surface."
            if next_version_baseline_promoted
            else "Operate the next-version ProductOS superpower build from one repo CLI surface."
        ),
        "current_focus": (
            "Keep the fully promoted discover, docs-and-deck, weekly operator, score-refresh, verified adapter, and distributed market-intelligence loops running as the standard baseline."
            if all_named_superpowers_promoted
            else (
                "Keep the promoted discover, docs-and-deck, weekly operator, score-refresh, and verified adapter loops running as the standard baseline while hardening broader market-intelligence distribution posture."
                if next_version_baseline_promoted
                else (
                    "Keep the promoted discover and control-surface slices as the standard while pushing weekly PM autopilot to 5 out of 5."
                    if discover_promoted
                    else "Push the discover-to-PRD loop to 5 out of 5 while keeping docs, deck, research, and improvement slices active internally."
                )
            )
        ),
        "recommended_next_step": {
            "action_summary": (
                "Review the self-improvement loop and choose the next bounded expansion slice."
                if all_named_superpowers_promoted
                else (
                    "Review the market-intelligence scorecard and start the next governed distribution hardening cycle."
                    if next_version_baseline_promoted
                    else (
                        "Review the weekly PM autopilot scorecard and drive the next bounded operator slice."
                        if discover_promoted
                        else "Review the discover-to-PRD scorecard and run the discover loop on the live inbox inputs."
                    )
                )
            ),
            "target_type": "pm_review",
            "target_ref": next_priority_scorecard_id,
            "rationale": (
                "All named current slices are promoted, so the next meaningful leverage gain should come from a newly chosen bounded expansion slice rather than more hardening on the existing baseline."
                if all_named_superpowers_promoted
                else (
                    "The planned next-version slices are complete, so the next meaningful leverage gain is broadening the refreshed market-intelligence slice beyond internal-use distribution."
                    if next_version_baseline_promoted
                    else (
                        "The discover and control-surface slices are promoted, so weekly PM autopilot is now the lowest-scoring high-impact route."
                        if discover_promoted
                        else "This is the lowest-scoring high-impact feature and the first must-win wedge for the next version."
                    )
                )
            ),
        },
        "active_agents": [
            {
                "agent_name": "cockpit",
                "status": "active",
                "current_task": "Keep the repo CLI surface, portfolio review, and next actions visible.",
            },
            {
                "agent_name": "workflow",
                "status": "completed" if discover_promoted else "awaiting_review",
                "current_task": (
                    "The fully promoted next-version baseline now keeps discover, alignment, and distribution paths refreshed from the repo surface."
                    if all_named_superpowers_promoted
                    else (
                        "The promoted next-version baseline now refreshes the discover and alignment paths from the repo surface while the next market-intelligence distribution hardening cycle is prepared."
                        if next_version_baseline_promoted
                        else (
                            "The discover route is promoted and the weekly operator route is now the next supervised slice."
                            if discover_promoted
                            else "Drive the live discover-to-PRD session from the inbox files into the current decision package."
                        )
                    )
                ),
            },
            {
                "agent_name": "improvement_planner",
                "status": "completed" if self_improvement_promoted else "awaiting_review",
                "current_task": (
                    "Keep the score-refresh loop subordinate to frozen evals and decision memory until the blocked promotion gate clears."
                    if promotion_gate["status"] == "blocked"
                    else "Support the selected V5 lifecycle-traceability build now that the bounded baseline gate is clear."
                ),
            },
        ],
        "active_queue_refs": [
            {
                "queue_type": "review_queue",
                "artifact_id": feature_portfolio_review["feature_portfolio_review_id"],
                "summary": (
                    "Review the self-improvement loop to choose the next bounded expansion slice."
                    if all_named_superpowers_promoted
                    else (
                        "Review market-intelligence distribution posture as the next hardening surface."
                        if next_version_baseline_promoted
                        else (
                            "Review the weekly PM autopilot as the next promoted slice."
                            if discover_promoted
                            else "Review the top-priority next-version feature and its current score."
                        )
                    )
                )
            },
            {
                "queue_type": "follow_up_queue",
                "artifact_id": follow_up_queue["follow_up_queue_id"],
                "summary": follow_up_queue["items"][0]["title"],
            },
        ],
        "queue_recommendations": [
            {
                "queue_type": "review_queue",
                "artifact_id": feature_portfolio_review["feature_portfolio_review_id"],
                "item_id": next_priority_feature_id,
                "recommended_action": "review_now",
                "urgency": "time_sensitive",
                "why_now": (
            "The repo-native next-version baseline is fully promoted, so the next review should choose a new bounded expansion slice rather than patching a remaining gap."
            if all_named_superpowers_promoted
                    else (
                        "The repo-native next-version baseline is promoted and adapter parity is cleared, so broader market-intelligence distribution is now the main remaining leverage gap."
                        if next_version_baseline_promoted
                        else (
                            "The discover and control-surface slices are promoted, so weekly PM autopilot is now the next release wedge."
                            if discover_promoted
                            else "The discover-to-PRD loop is the current top-priority feature and the first release wedge for the next version."
                        )
                    )
                ),
            },
            {
                "queue_type": "follow_up_queue",
                "artifact_id": follow_up_queue["follow_up_queue_id"],
                "item_id": follow_up_queue["items"][0]["follow_up_id"],
                "recommended_action": "start",
                "urgency": "routine",
                "why_now": (
                    "The promoted weekly operator loop can now absorb this recurring follow-up behavior by default while the next expansion choice is prepared."
                    if next_version_baseline_promoted
                    else "The weekly operator loop should absorb the current manual follow-up rhythm."
                ),
            },
        ],
        "active_orchestration_state_id": orchestration_state_id,
        "active_execution_session_state_ids": [
            discover_session_id,
            align_session_id,
            operate_session_id,
            improve_session_id,
        ],
        "active_workflow_state_ids": [
            "wf_next_version_superpower_ops",
            "wf_problem_brief_to_prd",
            "wf_artifact_to_readable_doc",
        ],
        "blocked_route_ids": [],
        "awaiting_review_route_ids": (
            []
            if next_version_baseline_promoted
            else (
                ["route_operator_autopilot"]
                if discover_promoted
                else ["route_discover_to_prd"]
            )
        ),
        "pending_review_points": (
            [
                "All named current superpower slices are now 5 out of 5 on the repo-native baseline.",
                "Use the self-improvement loop to choose the next bounded expansion slice rather than treating the current baseline as incomplete.",
            ]
            if all_named_superpowers_promoted
            else [
                (
                    "weekly_pm_autopilot is still 3 out of 5 and is now the next bounded slice to promote."
                    if discover_promoted
                    else "discover_to_prd_superpower is still 3 out of 5 and needs live same-day proof from the inbox files."
                ),
                (
                    "Readable docs, presentation, research, adapters, and self-improvement remain active internal slices below 5 out of 5."
                    if discover_promoted
                    else "Readable docs, presentation, research, runtime control, adapters, and self-improvement are all active but still below 5 out of 5."
                ),
            ]
        ),
        "missing_context_questions": [
            (
                "Which external publication or packaging slice should follow the fully promoted baseline?"
                if all_named_superpowers_promoted
                else (
                    "Which broader distribution path should lead the next governed market-intelligence hardening cycle?"
                    if next_version_baseline_promoted
                    else (
                        "What is the minimum supervised weekly operator path that feels like an autopilot instead of a queue dashboard?"
                        if discover_promoted
                        else "What parts of the current seeded decision package can be regenerated directly from the live inbox without manual reconstruction?"
                    )
                )
            )
        ],
        "blocking_reasons": promotion_gate["blockers"],
        "source_artifact_ids": [
            decision_log["decision_log_id"],
            strategic_memory["strategic_memory_record_id"],
            feature_portfolio_review["feature_portfolio_review_id"],
            autonomous_pm_swarm_plan["autonomous_pm_swarm_plan_id"],
            runtime_adapter_registry["runtime_adapter_registry_id"],
            adapter_parity_report["runtime_scenario_report_id"],
            market_refresh_report["runtime_scenario_report_id"],
            market_distribution_report["runtime_scenario_report_id"],
            discover_problem_brief["problem_brief_id"],
            discover_concept_brief["concept_brief_id"],
            discover_prd["prd_id"],
            live_doc_sync_state["document_sync_state_id"],
            status_mail["status_mail_id"],
            issue_log["issue_log_id"],
            discover_scorecard_id,
            docs_alignment_scorecard_id,
            presentation_scorecard_id,
            weekly_pm_autopilot_scorecard_id,
            market_intelligence_scorecard_id,
            runtime_control_surface_scorecard_id,
            agent_adapter_scorecard_id,
            self_improvement_scorecard_id,
            autonomous_pm_swarm_scorecard_id,
        ],
        "created_at": generated_at,
        "updated_at": generated_at,
    }

    for session in (
        discover_execution_session_state,
        align_execution_session_state,
        operate_execution_session_state,
        improve_execution_session_state,
    ):
        session["input_refs"] = [context_pack["context_pack_id"], *session["input_refs"]]
    improve_execution_session_state["output_refs"] = [
        self_improvement_scorecard_id,
        autonomous_pm_swarm_plan["autonomous_pm_swarm_plan_id"],
        autonomous_pm_swarm_scorecard_id,
        improvement_loop_state["improvement_loop_state_id"],
        eval_suite_manifest["eval_suite_manifest_id"],
        eval_run_report["eval_run_report_id"],
    ]
    if promotion_gate["status"] == "ready":
        improve_execution_session_state.update(
            {
                "status": "completed",
                "review_required": False,
                "verification_status": "passed",
                "completed_at": generated_at,
            }
        )
        for route in orchestration_state["route_plan"]:
            if route["route_id"] == "route_score_and_improve":
                route["status"] = "completed"
        for agent in cockpit_state["active_agents"]:
            if agent["agent_name"] == "improvement_planner":
                agent["status"] = "completed"
                agent["current_task"] = "Use the cleared bounded baseline to support the selected V5 lifecycle-traceability build and bounded-extension planning."
        orchestration_state.update(
            {
                "goal": "Use the cleared bounded baseline to build the selected V5 lifecycle-traceability bundle and start the bounded extension.",
                "status": "completed",
                "coordination_summary": "The bounded baseline now clears the frozen eval suite and portfolio truthfulness gate. The hardening cycle is complete, and the next step is building the selected V5 lifecycle-traceability bundle.",
                "active_route_ids": [],
                "awaiting_review_route_ids": [],
                "queue_impacts": [
                    {
                        "queue_type": "review_queue",
                        "artifact_id": feature_portfolio_review["feature_portfolio_review_id"],
                        "item_id": next_priority_feature_id,
                        "recommended_action": "review_now",
                        "reason": "The bounded baseline gate is clear, so the next review should move into the selected V5 lifecycle-traceability build instead of another hardening slice.",
                        "status": "recommended",
                    }
                ],
            }
        )
        cockpit_state.update(
            {
                "mode": "status",
                "status": "completed",
                "coordination_status": "healthy",
                "request_summary": "Operate the cleared bounded baseline from the repo CLI and move into the selected V5 lifecycle-traceability build.",
                "current_focus": "Build the selected V5 lifecycle-traceability bundle and prepare the bounded extension plan while keeping the cleared V5 stable slice intact.",
                "recommended_next_step": {
                    "action_summary": "Review the cleared bounded-baseline portfolio and begin the selected V5 lifecycle-traceability build.",
                    "target_type": "pm_review",
                    "target_ref": next_priority_scorecard_id,
                    "rationale": "The bounded baseline is complete, so the next bounded decision is executing the selected V5 lifecycle-traceability bundle rather than more hardening.",
                },
                "awaiting_review_route_ids": [],
                "pending_review_points": [
                    "Truthfulness status is `healthy` across the bounded-baseline portfolio.",
                    "The frozen eval suite now passes with no regressions.",
                    "The next decision is executing the selected V5 lifecycle-traceability bundle and beginning the bounded extension.",
                ],
                "blocking_reasons": [],
                "source_artifact_ids": [
                    context_pack["context_pack_id"],
                    eval_suite_manifest["eval_suite_manifest_id"],
                    eval_run_report["eval_run_report_id"],
                    *cockpit_state["source_artifact_ids"],
                ],
            }
        )
    else:
        orchestration_state.update(
            {
                "goal": "Harden the bounded baseline so ProductOS can fail honestly before claiming broader superpower promotion.",
                "status": "awaiting_review",
                "coordination_summary": "The bounded baseline now emits a context pack, frozen eval suite, eval run report, and an honestly blocked control surface. The main remaining gap is now independent scoring in the self-improvement loop.",
                "active_route_ids": ["route_score_and_improve"],
                "awaiting_review_route_ids": ["route_score_and_improve"],
                "queue_impacts": [
                    {
                        "queue_type": "review_queue",
                        "artifact_id": feature_portfolio_review["feature_portfolio_review_id"],
                        "item_id": next_priority_feature_id,
                        "recommended_action": "review_now",
                        "reason": "The portfolio now ranks foundation work by score and provenance; self-improvement is the weakest remaining slice after the control-surface hardening.",
                        "status": "recommended",
                    }
                ],
            }
        )
        cockpit_state.update(
            {
                "mode": "review",
                "status": "awaiting_review",
                "coordination_status": "blocked" if promotion_gate["status"] == "blocked" else truthfulness_status,
                "request_summary": "Operate the bounded-baseline hardening cycle from the repo CLI with explicit eval and provenance signals.",
                "current_focus": "Harden truthful control-surface reporting, make frozen evals first-class, and route decision memory into promotion logic.",
                "recommended_next_step": {
                    "action_summary": "Review the weakest score-bearing bounded-baseline slice and start the next bounded fix.",
                    "target_type": "pm_review",
                    "target_ref": next_priority_scorecard_id,
                    "rationale": "The bounded baseline now ranks work by score and provenance instead of assuming the stable claim is already broader than the evidence.",
                },
                "awaiting_review_route_ids": ["route_score_and_improve"],
                "pending_review_points": [
                    f"Truthfulness status is `{truthfulness_status}` because {len(unresolved_mixed_provenance_feature_ids)} unresolved score-bearing features still have mixed provenance.",
                    f"The frozen eval suite reports {eval_run_report['regression_count']} regression, so the current baseline is not promotable." if eval_run_report["regression_count"] == 1 else f"The frozen eval suite reports {eval_run_report['regression_count']} regressions, so the current baseline is not promotable.",
                    f"`{next_priority_feature_id}` is the top-priority bounded-baseline feature because it is the weakest slice by score and provenance.",
                ],
                "missing_context_questions": context_pack["open_questions"],
                "blocking_reasons": promotion_gate["blockers"],
                "source_artifact_ids": [
                    context_pack["context_pack_id"],
                    eval_suite_manifest["eval_suite_manifest_id"],
                    eval_run_report["eval_run_report_id"],
                    *cockpit_state["source_artifact_ids"],
                ],
            }
        )

    bundle = {
        "cockpit_state": cockpit_state,
        "orchestration_state": orchestration_state,
        "intake_routing_state": intake_routing_state,
        "memory_retrieval_state": memory_retrieval_state,
        "context_pack": context_pack,
        "autonomous_pm_swarm_plan": autonomous_pm_swarm_plan,
        "eval_suite_manifest": eval_suite_manifest,
        "eval_run_report": eval_run_report,
        "runtime_adapter_registry": runtime_adapter_registry,
        "adapter_parity_report": adapter_parity_report,
        "market_refresh_report": market_refresh_report,
        "market_distribution_report": market_distribution_report,
        "next_version_release_gate_decision": next_version_release_gate_decision,
        "presentation_brief": presentation_brief,
        "presentation_evidence_pack": presentation_evidence_pack,
        "presentation_story": presentation_story,
        "presentation_render_spec": presentation_render_spec,
        "presentation_publish_check": presentation_publish_check,
        "presentation_ppt_export_plan": presentation_ppt_export_plan,
        "discover_problem_brief": discover_problem_brief,
        "discover_concept_brief": discover_concept_brief,
        "discover_prd": discover_prd,
        "discover_execution_session_state": discover_execution_session_state,
        "align_execution_session_state": align_execution_session_state,
        "align_document_sync_state": live_doc_sync_state,
        "operate_execution_session_state": operate_execution_session_state,
        "operate_status_mail": status_mail,
        "operate_issue_log": issue_log,
        "improve_execution_session_state": improve_execution_session_state,
        "improve_improvement_loop_state": improvement_loop_state,
        "discover_feature_scorecard": discover_scorecard,
        "docs_alignment_feature_scorecard": docs_alignment_scorecard,
        "presentation_feature_scorecard": presentation_scorecard,
        "weekly_pm_autopilot_feature_scorecard": weekly_pm_autopilot_scorecard,
        "market_intelligence_feature_scorecard": market_intelligence_scorecard,
        "runtime_control_surface_feature_scorecard": runtime_control_surface_scorecard,
        "agent_adapter_feature_scorecard": agent_adapter_scorecard,
        "self_improvement_feature_scorecard": self_improvement_scorecard,
        "autonomous_pm_swarm_feature_scorecard": autonomous_pm_swarm_scorecard,
        "feature_portfolio_review": feature_portfolio_review,
    }
    include_governed_research_context = any(
        item is not None
        for item in [
            workspace_research_brief,
            workspace_external_research_source_discovery,
            workspace_external_research_feed_registry,
            workspace_selected_research_manifest,
            workspace_external_research_review,
        ]
    )
    if include_governed_research_context:
        if workspace_research_brief is not None:
            bundle["research_brief"] = workspace_research_brief
        if workspace_external_research_plan is not None:
            bundle["external_research_plan"] = workspace_external_research_plan
        if workspace_external_research_source_discovery is not None:
            bundle["external_research_source_discovery"] = workspace_external_research_source_discovery
        if workspace_external_research_feed_registry is not None:
            bundle["external_research_feed_registry"] = workspace_external_research_feed_registry
        if workspace_selected_research_manifest is not None:
            bundle["external_research_selected_manifest"] = workspace_selected_research_manifest
        if workspace_external_research_review is not None:
            bundle["external_research_review"] = workspace_external_research_review
    return bundle
