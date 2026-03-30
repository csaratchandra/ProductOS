from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_v3_evolution_bundle_from_workspace(
    workspace_dir: Path | str,
    *,
    generated_at: str,
) -> dict[str, dict[str, Any]]:
    workspace_path = Path(workspace_dir).resolve()
    artifacts_dir = workspace_path / "artifacts"

    concept_brief = _load_json(artifacts_dir / "concept_brief.json")
    prototype_record = _load_json(artifacts_dir / "prototype_record.json")
    prd = _load_json(artifacts_dir / "prd.json")
    increment_plan = _load_json(artifacts_dir / "increment_plan.json")
    feedback_log = _load_json(artifacts_dir / "productos_feedback_log.example.json")

    workspace_id = concept_brief["workspace_id"]

    feedback_ids = {entry["feedback_id"] for entry in feedback_log["entries"]}
    docs_gap_ids = [feedback_id for feedback_id in ["pfb_006", "pfb_007"] if feedback_id in feedback_ids]

    ux_design_review = {
        "schema_version": "1.0.0",
        "ux_design_review_id": f"ux_design_review_{workspace_id}_v3_1",
        "workspace_id": workspace_id,
        "request_summary": "Review the PM operating rhythm concept and prototype before expanding into V3.1 UX and visual superpowers.",
        "status": "approved",
        "target_artifact_ids": [
            concept_brief["concept_brief_id"],
            prototype_record["prototype_record_id"],
            prd["prd_id"],
        ],
        "primary_persona": "Product manager",
        "user_flow_summary": "The PM should move from signal review to decision, communication, and roadmap updates without rebuilding context manually.",
        "information_architecture_summary": "Cockpit, queue, evidence, design review, and readable docs should be distinct but cross-linked.",
        "interaction_model_summary": "The next recommended action, evidence, critique, and review state should remain visible through one routed PM flow.",
        "prototype_quality_rating": "acceptable",
        "quality_summary": "The reviewed concept is internally usable, but the prototype still needs stronger interaction sharpness before it can count as a reference-quality PM surface.",
        "quality_dimension_reviews": [
            {
                "dimension_key": "interaction_clarity",
                "rating": "acceptable",
                "rationale": "The main path is understandable, but the transitions between states remain too text-heavy.",
            },
            {
                "dimension_key": "workflow_credibility",
                "rating": "acceptable",
                "rationale": "The PM flow is plausible, though the handoff moments still need more realistic state behavior.",
            },
            {
                "dimension_key": "information_hierarchy",
                "rating": "acceptable",
                "rationale": "The surfaces are separated correctly, but current priority and blockers need stronger emphasis.",
            },
            {
                "dimension_key": "trust_and_traceability",
                "rating": "excellent",
                "rationale": "Evidence-backed recommendations and the PM approval boundary remain visible throughout the flow.",
            },
            {
                "dimension_key": "visual_intent",
                "rating": "acceptable",
                "rationale": "The interaction model is deliberate, but it is not yet distinctive enough to serve as a top-tier reference surface.",
            },
            {
                "dimension_key": "accessibility_resilience",
                "rating": "acceptable",
                "rationale": "Plain-text structure is preserved, but more redundant state cues are still needed.",
            },
        ],
        "quality_reference_examples": [
            "A PM control surface that feels decision-ready without presenter narration.",
        ],
        "accessibility_considerations": [
            "Status and blocker meaning should not depend only on color.",
            "Readable and visual outputs should preserve hierarchy in plain text and structured form.",
        ],
        "trust_considerations": [
            "Design recommendations must distinguish evidence from inference.",
            "The PM should remain the approval gate before UX recommendations harden into PRD scope.",
        ],
        "improvement_actions": [
            "Sharpen state transitions so queue, decision, and communication steps feel like one continuous workflow.",
            "Increase visual distinction around required review, blockers, and current priority.",
        ],
        "recommended_next_step": "prd",
        "evidence_refs": [
            concept_brief["concept_brief_id"],
            prototype_record["prototype_record_id"],
            prd["prd_id"],
        ],
        "generated_at": generated_at,
    }

    visual_reasoning_state = {
        "schema_version": "1.0.0",
        "visual_reasoning_state_id": f"visual_reasoning_state_{workspace_id}_v3_1",
        "workspace_id": workspace_id,
        "status": "reviewed",
        "goal": "Use visual reasoning to make PM operating flow, dependency risk, and stakeholder communication easier to explain and review.",
        "visual_specs": [
            {
                "visual_map_spec_id": "visual_map_spec_v3_1_workflow",
                "map_type": "workflow_map",
                "purpose": "Show the PM operating loop from signal intake through communication output.",
                "audience": "PM and engineering",
                "status": "approved",
                "primary_message": "The runtime, queues, docs, and review gates should form one continuous PM workflow.",
            },
            {
                "visual_map_spec_id": "visual_map_spec_v3_1_journey",
                "map_type": "user_journey_map",
                "purpose": "Explain where PM cognitive load is reduced compared with the V3.0 baseline.",
                "audience": "Leadership",
                "status": "reviewed",
                "primary_message": "Visual reasoning should improve persuasion and clarity, not only runtime introspection.",
            },
        ],
        "benchmark_hypotheses": [
            "A workflow map should reduce the time needed to explain the PM operating loop to engineering.",
            "A journey-style explanation should improve leadership understanding of where PM load is reduced.",
        ],
        "linked_artifact_ids": [
            ux_design_review["ux_design_review_id"],
            prd["prd_id"],
            increment_plan["increment_plan_id"],
        ],
        "generated_at": generated_at,
    }

    superpower_benchmark = {
        "schema_version": "1.0.0",
        "superpower_benchmark_id": f"superpower_benchmark_{workspace_id}_v3_1",
        "workspace_id": workspace_id,
        "baseline_version": "3.0.0",
        "candidate_version": "3.1.0",
        "status": "passed",
        "summary": "The first V3.1 superpower slice improves PM design and communication workflows relative to V3.0.",
        "scenarios": [
            {
                "scenario_id": "scenario_ux_review_before_prd",
                "name": "UX review before PRD commitment",
                "status": "passed",
                "metric_deltas": [
                    {
                        "metric_name": "time_to_identify_usability_risk_minutes",
                        "baseline_value": 45,
                        "candidate_value": 12,
                        "unit": "minutes",
                        "trend": "improved",
                    }
                ],
                "evidence_refs": [ux_design_review["ux_design_review_id"]],
                "gaps": [],
            },
            {
                "scenario_id": "scenario_visual_reasoning_for_alignment",
                "name": "Visual reasoning for stakeholder alignment",
                "status": "passed",
                "metric_deltas": [
                    {
                        "metric_name": "time_to_explain_pm_operating_flow_minutes",
                        "baseline_value": 20,
                        "candidate_value": 7,
                        "unit": "minutes",
                        "trend": "improved",
                    }
                ],
                "evidence_refs": [visual_reasoning_state["visual_reasoning_state_id"]],
                "gaps": [],
            },
        ],
        "generated_at": generated_at,
    }

    gap_cluster_state = {
        "schema_version": "1.0.0",
        "gap_cluster_state_id": f"gap_cluster_state_{workspace_id}_post_v3_1",
        "workspace_id": workspace_id,
        "evaluation_scope": "post_v3_1",
        "status": "ready_for_decision",
        "clusters": [
            {
                "cluster_id": "cluster_deeper_visual_reasoning",
                "label": "Deeper visual reasoning and explanation",
                "feedback_ids": docs_gap_ids[:1] or [feedback_log["entries"][0]["feedback_id"]],
                "impact_level": "medium",
                "recommended_release": "v3_2",
                "rationale": "If repeated after the first V3.1 slice, deeper visual explanation still belongs in V3 rather than V4.",
            },
            {
                "cluster_id": "cluster_pm_communication_docs",
                "label": "PM communication and readable product documents",
                "feedback_ids": docs_gap_ids or [feedback_log["entries"][-1]["feedback_id"]],
                "impact_level": "high",
                "recommended_release": "v4",
                "rationale": "Readable docs and the auto-improvement loop form a broader communication and operating-system upgrade better suited to V4.",
            },
        ],
        "generated_at": generated_at,
    }

    improvement_loop_state = {
        "schema_version": "1.0.0",
        "improvement_loop_state_id": f"improvement_loop_state_{workspace_id}_v4",
        "workspace_id": workspace_id,
        "status": "awaiting_pm",
        "loop_goal": "Turn repeated communication and release-planning pain into a bounded V4 improvement loop.",
        "source_feedback_ids": docs_gap_ids or [feedback_log["entries"][-1]["feedback_id"]],
        "routed_problem_ids": ["problem_brief_pm_operating_rhythm"],
        "routed_idea_ids": [concept_brief["idea_record_ids"][0]],
        "active_workers": [
            {
                "worker_name": "feedback_collector",
                "status": "completed",
                "current_task": "Collected repeated communication and planning pain from workspace feedback.",
            },
            {
                "worker_name": "discovery_router",
                "status": "completed",
                "current_task": "Routed repeated pain into problem, idea, and next-stage planning paths.",
            },
            {
                "worker_name": "improvement_planner",
                "status": "active",
                "current_task": "Prepare the next bounded V4 slice for docs and the auto-improvement loop.",
            },
        ],
        "review_gate": {
            "status": "passed",
            "owner": "critic",
            "exit_condition": "The proposed fix must directly address the observed PM communication and planning pain.",
        },
        "validation_gate": {
            "status": "passed",
            "owner": "validation",
            "exit_condition": "The fix must reduce manual rewrite and planning translation work relative to the prior baseline.",
        },
        "pm_decision_gate": {
            "status": "awaiting_pm",
            "owner": "ProductOS PM",
            "exit_condition": "The PM must accept, defer, or reject the proposed next bounded slice.",
        },
        "next_recommended_action": "Approve the next bounded V4 slice for human-readable docs and the automated improvement loop.",
        "generated_at": generated_at,
    }

    return {
        "ux_design_review": ux_design_review,
        "visual_reasoning_state": visual_reasoning_state,
        "superpower_benchmark": superpower_benchmark,
        "gap_cluster_state": gap_cluster_state,
        "improvement_loop_state": improvement_loop_state,
    }
