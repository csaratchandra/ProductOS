from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .baseline import (
    build_foundation_bundle_from_workspace,
    build_market_intelligence_bundle_from_workspace,
)
from .release import evaluate_promotion_gate


ROOT = Path(__file__).resolve().parents[3]
BASELINE_VERSION = "4.7.0"
CANDIDATE_VERSION = "4.8.0"
NEXT_VERSION_ARTIFACT_SCHEMAS: dict[str, str] = {
    "cockpit_state": "cockpit_state.schema.json",
    "orchestration_state": "orchestration_state.schema.json",
    "intake_routing_state": "intake_routing_state.schema.json",
    "memory_retrieval_state": "memory_retrieval_state.schema.json",
    "context_pack": "context_pack.schema.json",
    "eval_suite_manifest": "eval_suite_manifest.schema.json",
    "eval_run_report": "eval_run_report.schema.json",
    "runtime_adapter_registry": "runtime_adapter_registry.schema.json",
    "adapter_parity_report": "runtime_scenario_report.schema.json",
    "market_refresh_report": "runtime_scenario_report.schema.json",
    "market_distribution_report": "runtime_scenario_report.schema.json",
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
    "feature_portfolio_review": "feature_portfolio_review.schema.json",
}


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _artifact_path_with_archive_fallback(artifacts_dir: Path, filename: str) -> Path:
    return artifacts_dir / filename


def _relative_path(path: Path) -> str:
    return str(path.relative_to(ROOT))


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
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    raw_note_path = workspace_path / "inbox" / "raw-notes" / "2026-03-22-next-version-superpowers.md"
    transcript_path = workspace_path / "inbox" / "transcripts" / "2026-03-22-dogfood-next-version-session.txt"

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

    problem_brief = _load_json(artifacts_dir / "problem_brief.json")
    concept_brief = _load_json(artifacts_dir / "concept_brief.json")
    prd = _load_json(artifacts_dir / "prd.json")
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
    strategic_memory = _load_json(ROOT / "core" / "examples" / "artifacts" / "strategic_memory_record.example.json")
    workspace_id = problem_brief["workspace_id"]

    intake_items = _collect_inbox_items(workspace_path, generated_at)
    discover_problem_brief, discover_concept_brief, discover_prd = _build_live_discover_artifacts(
        workspace_path,
        workspace_id=workspace_id,
        generated_at=generated_at,
    )
    eval_suite_manifest = _build_eval_suite_manifest(
        workspace_id=workspace_id,
        generated_at=generated_at,
    )
    eval_run_report = {"eval_run_report_id": f"eval_run_report_{workspace_id}_bounded_baseline"}
    context_pack = {"context_pack_id": f"context_pack_{workspace_id}_bounded_baseline"}

    runtime_adapter_registry = {
        "schema_version": "1.0.0",
        "runtime_adapter_registry_id": f"runtime_adapter_registry_{workspace_id}_next_version",
        "workspace_id": workspace_id,
        "status": "healthy",
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

    discover_scorecard = _scorecard(
        workspace_id=workspace_id,
        feature_id="discover_to_prd_superpower",
        feature_name="Messy input to PRD superpower",
        loop_id="signal_to_product_decision",
        benchmark_ref=foundation_bundle["pm_superpower_benchmark"]["pm_superpower_benchmark_id"],
        validation_tier="tier_2",
        overall_score=4,
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
        provenance_classification="mixed",
        score_basis=["live_inbox_evidence", "context_pack", "frozen_eval_suite"],
        truthfulness_summary="The discover slice still produces strong live artifacts, but the final score remains watch-level because the runtime bundle mixes fresh outputs with generated release narration.",
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
        reviewer_summary="The live inbox route is strong, but the slice should stay internal-use until scoring and provenance are separated more cleanly.",
        tester_status="revise",
        tester_summary="The discover artifacts validate structurally, but evals still flag mixed-provenance scoring and watch-level truthfulness risk.",
        manual_status="accept",
        manual_summary="Keep discover-to-PRD active as a strong internal path while the remaining truthfulness controls mature.",
        blocked_by=["Score-bearing discover claims still rely on mixed runtime provenance."],
        feedback_items=[
            _feedback_item(
                feedback_id="score_feedback_discover_provenance",
                summary="Separate persisted discover outputs from bundle-local scoring before calling the discover slice fully promoted.",
                impact_level="high",
                recommended_action="Route discover scoring through persisted outputs and rerun the frozen eval suite.",
                route_targets=["improvement_loop_state", "feedback_cluster_state"],
                linked_dimension_keys=["reliability", "repeatability"],
                linked_artifact_refs=[discover_prd["prd_id"], eval_run_report["eval_run_report_id"]],
            )
        ],
        next_action="Keep the discover slice in internal use, persist its outputs explicitly, and rescore it after the next eval run.",
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

    presentation_scorecard = _scorecard(
        workspace_id=workspace_id,
        feature_id="presentation_superpower",
        feature_name="PRD to deck and executive story",
        loop_id="decision_to_stakeholder_alignment",
        benchmark_ref=foundation_bundle["pm_superpower_benchmark"]["pm_superpower_benchmark_id"],
        validation_tier="tier_3",
        overall_score=4,
        scenarios=[
            {
                "scenario_id": "scn_presentation_bundle_generation",
                "title": "Generate the promoted docs-and-deck package from the repo baseline",
                "scenario_type": "dogfood_run",
                "result": "passed",
                "summary": "The presentation package now clears the bounded next-version release gate as part of the promoted aligned path from PRD to stakeholder-ready docs and deck.",
                "evidence_refs": [
                    foundation_bundle["presentation_brief"]["presentation_brief_id"],
                    completion_validation_report["validation_lane_report_id"],
                ],
            }
        ],
        evidence_refs=[
            foundation_bundle["presentation_brief"]["presentation_brief_id"],
            foundation_bundle["presentation_story"]["presentation_story_id"],
            foundation_bundle["presentation_render_spec"]["render_spec_id"],
            foundation_bundle["presentation_publish_check"]["publish_check_id"],
            foundation_bundle["presentation_pattern_review"]["presentation_pattern_review_id"],
            completion_validation_report["validation_lane_report_id"],
            completion_manual_record["manual_validation_record_id"],
            eval_run_report["eval_run_report_id"],
        ],
        provenance_classification="mixed",
        score_basis=["presentation_bundle", "manual_validation", "frozen_eval_suite"],
        truthfulness_summary="The presentation slice is high quality, but it still inherits some mixed provenance because the surrounding release narrative and promotion logic are not fully separated from generated bundle state.",
        context_pack_ref=context_pack["context_pack_id"],
        eval_run_ref=eval_run_report["eval_run_report_id"],
        dimension_scores=[
            {
                "dimension_key": "pm_leverage",
                "score": 5,
                "rationale": "The repo now packages the approved PRD and doc bundle into a stakeholder-ready deck without a separate PM slide-building pass.",
                "evidence_refs": [
                    foundation_bundle["presentation_story"]["presentation_story_id"],
                    foundation_bundle["presentation_render_spec"]["render_spec_id"],
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
                    foundation_bundle["presentation_publish_check"]["publish_check_id"],
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
                    foundation_bundle["presentation_ppt_export_plan"]["ppt_export_plan_id"],
                ],
            },
        ],
        reviewer_status="pass",
        reviewer_summary="The presentation package remains strong for internal and leadership-ready use, but its promotion claim should stay watch-level until the surrounding truth controls are explicit.",
        tester_status="revise",
        tester_summary="Generation and publish checks pass, but the broader release claim still depends on mixed control-surface evidence.",
        manual_status="accept",
        manual_summary="Keep the docs-and-deck path active, but treat final promotion as pending the remaining truthfulness hardening slice.",
        blocked_by=["Presentation promotion still inherits mixed control-surface provenance."],
        feedback_items=[
            _feedback_item(
                feedback_id="score_feedback_presentation_truth",
                summary="Keep the presentation slice in internal-use status until release-level provenance becomes explicit.",
                impact_level="medium",
                recommended_action="Rescore the presentation path after the control surface and release narration stop mixing generated and persisted evidence.",
                route_targets=["improvement_loop_state"],
                linked_dimension_keys=["reliability", "repeatability"],
                linked_artifact_refs=[
                    foundation_bundle["presentation_story"]["presentation_story_id"],
                    eval_run_report["eval_run_report_id"],
                ],
            )
        ],
        next_action="Keep using the governed docs-and-deck path, but rescore it only after the control-surface truth signals are explicit.",
        generated_at=generated_at,
    )

    weekly_pm_autopilot_scorecard = _scorecard(
        workspace_id=workspace_id,
        feature_id="weekly_pm_autopilot",
        feature_name="Weekly PM autopilot",
        loop_id="feedback_to_accepted_improvement",
        benchmark_ref=foundation_bundle["pm_superpower_benchmark"]["pm_superpower_benchmark_id"],
        validation_tier="tier_2",
        overall_score=4,
        scenarios=[
            {
                "scenario_id": "scn_operator_from_current_queues",
                "title": "Operate weekly cadence from current queues and release state",
                "scenario_type": "dogfood_run",
                "result": "passed",
                "summary": "The repo now turns decisions, follow-ups, issue state, and release readiness into one supervised weekly operator session with a review-ready status mail.",
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
        provenance_classification="mixed",
        score_basis=["queue_artifacts", "status_mail", "frozen_eval_suite"],
        truthfulness_summary="The weekly operator path still leans on seeded artifacts and has not yet earned a promotion claim under the new eval and provenance rules.",
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
        reviewer_summary="The weekly operator path is useful, but it still looks more seeded than live and should remain below the promotion bar.",
        tester_status="revise",
        tester_summary="The operator session validates structurally, but evals still flag mixed provenance and weak live-run proof.",
        manual_status="accept",
        manual_summary="Keep the weekly operator session in bounded internal use while the stable slice improves live scoring and context handling.",
        blocked_by=["Weekly PM autopilot still depends on mixed seeded and generated operating artifacts."],
        feedback_items=[
            _feedback_item(
                feedback_id="score_feedback_weekly_live_proof",
                summary="Replace seeded operator artifacts with stronger persisted live-run proof before promoting weekly autopilot.",
                impact_level="high",
                recommended_action="Run the weekly operator slice from persisted live inputs and rerun the frozen eval suite.",
                route_targets=["improvement_loop_state"],
                linked_dimension_keys=["reliability", "autonomy_quality"],
                linked_artifact_refs=[status_mail["status_mail_id"], eval_run_report["eval_run_report_id"]],
            )
        ],
        next_action="Refresh the weekly operator path from persisted live outputs and rerun the eval suite before promoting it.",
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

    self_improvement_scorecard = _scorecard(
        workspace_id=workspace_id,
        feature_id="self_improvement_loop",
        feature_name="Self-improvement and scoring loop",
        loop_id="feedback_to_accepted_improvement",
        benchmark_ref=foundation_bundle["pm_superpower_benchmark"]["pm_superpower_benchmark_id"],
        validation_tier="tier_2",
        overall_score=4,
        scenarios=[
            {
                "scenario_id": "scn_sub_five_features_route_to_improvement",
                "title": "Route sub-5 features into the improvement loop",
                "scenario_type": "dogfood_run",
                "result": "passed",
                "summary": "Feature scoring, portfolio review, and repeated Ralph-gated releases now show a working compounding-improvement loop instead of one-off setup.",
                "evidence_refs": [
                    improvement_loop_state["improvement_loop_state_id"],
                    f"feature_portfolio_review_{workspace_id}_next_version_baseline",
                    completion_validation_report["validation_lane_report_id"],
                ],
            }
        ],
        evidence_refs=[
            improvement_loop_state["improvement_loop_state_id"],
            f"feature_portfolio_review_{workspace_id}_next_version_baseline",
            decision_log["decision_log_id"],
            strategic_memory["strategic_memory_record_id"],
            completion_validation_report["validation_lane_report_id"],
            completion_manual_record["manual_validation_record_id"],
            completion_release_gate_decision["release_gate_decision_id"],
            foundation_bundle["feature_scorecard"]["feature_scorecard_id"],
            "release_4_1_0",
            "release_4_2_0",
            "release_4_3_0",
            eval_run_report["eval_run_report_id"],
        ],
        provenance_classification="real",
        score_basis=["feature_scorecards", "portfolio_review", "decision_memory", "independent_validation", "frozen_eval_suite"],
        truthfulness_summary="The improvement loop now consumes frozen eval, decision memory, validation, and release-gate evidence explicitly, but promotion judgment still remains watch-level because the same runtime assembles the overall bundle it is judging.",
        context_pack_ref=context_pack["context_pack_id"],
        eval_run_ref=eval_run_report["eval_run_report_id"],
        dimension_scores=[
            {
                "dimension_key": "pm_leverage",
                "score": 5,
                "rationale": "The repo now converts sub-5 features into named bounded slices and releases instead of vague future work.",
                "evidence_refs": [
                    improvement_loop_state["improvement_loop_state_id"],
                    f"feature_portfolio_review_{workspace_id}_next_version_baseline",
                ],
            },
            {
                "dimension_key": "output_quality",
                "score": 5,
                "rationale": "The scoring, portfolio review, and release-gate artifacts now form one coherent improvement accounting system.",
                "evidence_refs": [
                    foundation_bundle["feature_scorecard"]["feature_scorecard_id"],
                    f"feature_portfolio_review_{workspace_id}_next_version_baseline",
                ],
            },
            {
                "dimension_key": "reliability",
                "score": 4,
                "rationale": "The loop has refreshed across multiple promoted slices and now explicitly references eval, validation, and decision-memory evidence, but it is not yet independent enough for final promotion judgment.",
                "evidence_refs": [
                    improvement_loop_state["improvement_loop_state_id"],
                    completion_validation_report["validation_lane_report_id"],
                    completion_release_gate_decision["release_gate_decision_id"],
                    "release_4_2_0",
                    "release_4_3_0",
                ],
            },
            {
                "dimension_key": "autonomy_quality",
                "score": 4,
                "rationale": "The loop stays supervised and now records the next bounded hardening cycle with explicit release-gate inputs instead of relying only on self-narration.",
                "evidence_refs": [
                    improvement_loop_state["improvement_loop_state_id"],
                    completion_manual_record["manual_validation_record_id"],
                    decision_log["decision_log_id"],
                    completion_release_gate_decision["release_gate_decision_id"],
                ],
            },
            {
                "dimension_key": "repeatability",
                "score": 4,
                "rationale": "Repeated slice scoring and Ralph promotion make the loop a stable operating behavior, though final promotion still needs stronger independence from the builder surface.",
                "evidence_refs": [
                    "release_4_1_0",
                    "release_4_2_0",
                    "release_4_3_0",
                ],
            },
        ],
        reviewer_status="pass",
        reviewer_summary="The improvement loop should stay active and is materially stronger now that it consumes explicit eval, decision-memory, validation, and release-gate evidence, but it is still not an independent final judge of promotion.",
        tester_status="revise",
        tester_summary="Cross-references, validation, decision-memory, and release-gate references now strengthen the loop, but final promotion judgment is still too tightly coupled to the runtime that assembles the result.",
        manual_status="accept",
        manual_summary="Keep the scoring loop in place as a watch-level internal-use standard, but do not let it act as the final independent promotion judge yet.",
        blocked_by=[
            "The scoring loop still assigns final promotion judgment from the same runtime surface that assembles the evidence bundle.",
        ],
        feedback_items=[
            _feedback_item(
                feedback_id="score_feedback_independent_eval",
                summary="Introduce a truly frozen eval suite and route promotion through it before letting the improvement loop call the baseline healthy.",
                impact_level="high",
                recommended_action="Use the frozen eval suite as the gating mechanism for future promotion decisions.",
                route_targets=["improvement_loop_state", "release_scope_recommendation"],
                linked_dimension_keys=["reliability", "repeatability"],
                linked_artifact_refs=[eval_suite_manifest["eval_suite_manifest_id"], eval_run_report["eval_run_report_id"]],
            )
        ],
        next_action="Keep the eval suite, decision memory, validation, and release-gate evidence as first-class inputs while extending the selected V5 lifecycle-traceability bundle from the cleared bounded baseline.",
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
        "request_summary": "Assemble the evidence, memory, and decision context needed to review the current bounded baseline.",
        "decision_to_be_made": "Should ProductOS treat the current next-version runtime as trustworthy enough to score and promote release claims?",
        "status": "watch",
        "audience": ["PM", "engineering", "leadership"],
        "quality_contract": _quality_contract(
            audience=["PM", "engineering", "leadership"],
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
        "evidence_bundle": [
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
                "summary": eval_run_report["summary"],
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
        ],
        "contradictions": [
            "The CLI previously reported an all-green baseline while the review model described unresolved truthfulness gaps.",
        ],
        "open_questions": [
            "Which remaining mixed-provenance feature should be forced through the next bounded hardening cycle first?"
        ],
        "source_artifact_ids": [
            decision_log["decision_log_id"],
            strategic_memory["strategic_memory_record_id"],
            eval_run_report["eval_run_report_id"],
            discover_prd["prd_id"],
        ],
        "recommended_next_action": "Use the bounded baseline to make truthfulness, frozen evals, and decision memory visible in every promotion decision.",
        "created_at": generated_at,
        "updated_at": generated_at,
    }

    discover_scorecard_id = discover_scorecard["feature_scorecard_id"]
    docs_alignment_scorecard_id = docs_alignment_scorecard["feature_scorecard_id"]
    presentation_scorecard_id = presentation_scorecard["feature_scorecard_id"]
    weekly_pm_autopilot_scorecard_id = weekly_pm_autopilot_scorecard["feature_scorecard_id"]
    market_intelligence_scorecard_id = market_intelligence_scorecard["feature_scorecard_id"]
    runtime_control_surface_scorecard_id = runtime_control_surface_scorecard["feature_scorecard_id"]
    agent_adapter_scorecard_id = agent_adapter_scorecard["feature_scorecard_id"]
    self_improvement_scorecard_id = self_improvement_scorecard["feature_scorecard_id"]
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
    truthfulness_status = "watch" if unresolved_mixed_provenance_feature_ids or eval_run_report["regression_count"] else "healthy"
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
                "gap_summary": "Strong live-output path, but still scored as watch-level because the promotion logic mixes fresh outputs with generated bundle narration.",
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
                "gap_summary": "High-quality internal presentation path, but still inherits mixed release provenance.",
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
                "gap_summary": "Useful operator bundle, but still too seeded to claim a true weekly autopilot standard.",
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
                "gap_summary": "Evidence-backed and strong, but kept internal-use while broader release claims stay in watch mode.",
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
                "gap_summary": "Top-priority bounded-baseline gap: scoring is still too coupled to the same runtime that generates the evidence bundle.",
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
        ],
        "next_action": "Treat self_improvement_loop as the first remaining hardening target, while keeping the improved truthful control surface in place and reducing its remaining provenance debt.",
        "generated_at": generated_at,
    }
    promotion_gate = evaluate_promotion_gate(
        eval_run_report=eval_run_report,
        feature_portfolio_review=feature_portfolio_review,
    )
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
                *[
                    ref
                    for ref in improvement_loop_state.get("feature_scorecard_refs", [])
                    if ref not in {runtime_control_surface_scorecard_id, self_improvement_scorecard_id}
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
        "provenance_status": "complete",
        "retrieved_records": [
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
        ],
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
    if adapter_name == "codex":
        selected_adapter_id = "adapter_codex_thin"
    elif adapter_name == "claude":
        selected_adapter_id = "adapter_claude_style_thin"
    elif adapter_name == "windsurf":
        selected_adapter_id = "adapter_windsurf_thin"
    elif adapter_name == "antigravity":
        selected_adapter_id = "adapter_antigravity_thin"
    else:
        selected_adapter_id = "adapter_codex_thin"
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
            improvement_loop_state["improvement_loop_state_id"],
        ],
        review_required=improve_review_required,
        verification_status="passed" if self_improvement_promoted else "not_started",
        created_at=generated_at,
        event_messages=improve_event_messages,
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
                "status": "completed" if discover_promoted else "awaiting_review",
                "input_artifact_ids": [item["item_id"] for item in intake_items],
                "expected_output_artifact_ids": [
                    discover_problem_brief["problem_brief_id"],
                    discover_concept_brief["concept_brief_id"],
                    discover_prd["prd_id"],
                    discover_scorecard_id,
                ],
                "execution_session_state_id": discover_session_id,
            },
            {
                "route_id": "route_docs_and_deck",
                "agent_name": "presentation",
                "objective": "Package current ProductOS truth into readable docs and a stakeholder-ready deck through one aligned path.",
                "rationale": "Alignment is now part of the promoted baseline and should refresh from the discover package without extra PM reconstruction." if next_version_baseline_promoted else "Alignment is already one of the strongest current slices and should stay usable during the next-version build.",
                "status": "completed" if docs_alignment_promoted and presentation_promoted else "ready",
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
                "status": "completed" if weekly_pm_autopilot_promoted else ("awaiting_review" if discover_promoted else "active"),
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
            },
            {
                "route_id": "route_score_and_improve",
                "agent_name": "improvement_planner",
                "objective": "Refresh the portfolio review and improvement loop after every major bounded slice.",
                "rationale": "Sub-5 features should always become explicit improvement work, and the loop must stay subordinate to frozen eval and decision-memory evidence before claiming promotion.",
                "status": "completed" if self_improvement_promoted else "awaiting_review",
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
                    improvement_loop_state["improvement_loop_state_id"],
                    eval_suite_manifest["eval_suite_manifest_id"],
                    eval_run_report["eval_run_report_id"],
                ],
                "execution_session_state_id": improve_session_id,
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

    return {
        "cockpit_state": cockpit_state,
        "orchestration_state": orchestration_state,
        "intake_routing_state": intake_routing_state,
        "memory_retrieval_state": memory_retrieval_state,
        "context_pack": context_pack,
        "eval_suite_manifest": eval_suite_manifest,
        "eval_run_report": eval_run_report,
        "runtime_adapter_registry": runtime_adapter_registry,
        "adapter_parity_report": adapter_parity_report,
        "market_refresh_report": market_refresh_report,
        "market_distribution_report": market_distribution_report,
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
        "feature_portfolio_review": feature_portfolio_review,
    }
