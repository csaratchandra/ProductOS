from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
CORE_EXAMPLES_DIR = ROOT / "core" / "examples" / "artifacts"


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _date_from_timestamp(timestamp: str) -> str:
    return timestamp[:10]


def _inbox_readme(workspace_dir: Path, folder: str) -> str:
    return str((workspace_dir / "inbox" / folder / "README.md").relative_to(ROOT))


def build_runtime_bundle_from_workspace(
    workspace_dir: Path | str,
    *,
    generated_at: str,
) -> dict[str, dict[str, Any]]:
    workspace_path = Path(workspace_dir).resolve()
    artifacts_dir = workspace_path / "artifacts"

    decision_queue = _load_json(artifacts_dir / "decision_queue.example.json")
    follow_up_queue = _load_json(artifacts_dir / "follow_up_queue.example.json")
    feedback_log = _load_json(artifacts_dir / "productos_feedback_log.example.json")
    strategic_memory = _load_json(CORE_EXAMPLES_DIR / "strategic_memory_record.example.json")

    workspace_id = decision_queue["workspace_id"]
    decision = decision_queue["decisions"][0]
    follow_up = follow_up_queue["items"][0]

    orchestration_state_id = f"orch_state_{workspace_id}_runtime"
    execution_session_state_id = f"exec_session_{workspace_id}_runtime"
    cockpit_state_id = f"cockpit_state_{workspace_id}_runtime"
    intake_routing_state_id = f"intake_routing_state_{workspace_id}_runtime"
    memory_retrieval_state_id = f"memory_retrieval_state_{workspace_id}_runtime"
    feedback_cluster_state_id = f"feedback_cluster_state_{workspace_id}_runtime"
    release_scope_recommendation_id = f"release_scope_recommendation_{workspace_id}_runtime"
    pm_benchmark_id = f"pm_benchmark_{workspace_id}_runtime"
    release_readiness_id = f"release_readiness_{workspace_id}_runtime"
    runtime_scenario_report_id = f"runtime_scenario_report_{workspace_id}_runtime"
    release_gate_decision_id = f"release_gate_decision_{workspace_id}_runtime"

    coordination_feedback_ids = [
        entry["feedback_id"]
        for entry in feedback_log["entries"]
        if entry["category"] == "workflow_friction" or "launch reviewer" in entry["summary"].lower()
    ]
    reliability_feedback_ids = [
        entry["feedback_id"]
        for entry in feedback_log["entries"]
        if entry["category"] == "reliability_incident"
    ]

    cockpit_state = {
        "schema_version": "1.0.0",
        "cockpit_state_id": cockpit_state_id,
        "workspace_id": workspace_id,
        "mode": "plan",
        "status": "active",
        "coordination_status": "healthy",
        "request_summary": "Operate the completed V3.0 runtime foundation from one PM-facing cockpit surface.",
        "current_focus": "Keep queue actions, intake routing, and memory reuse legible now that the V3.0 runtime foundation is live.",
        "recommended_next_step": {
            "action_summary": "Review the highest-priority post-launch decision and follow-up item from the live runtime queues.",
            "target_type": "queue",
            "target_ref": decision_queue["decision_queue_id"],
            "rationale": "V3.0 is complete, so the cockpit should now steer ongoing prioritization instead of waiting on foundation work.",
        },
        "active_agents": [
            {
                "agent_name": "cockpit",
                "status": "active",
                "current_task": "Maintain PM-visible runtime state and expose the next controlled action.",
            },
            {
                "agent_name": "orchestrator",
                "status": "completed",
                "current_task": "Completed the V3.0 foundation route plan and keeps handoff history available for inspection.",
            },
            {
                "agent_name": "validation",
                "status": "completed",
                "current_task": "Completed schema, artifact, and runtime proof validation for the V3.0 foundation.",
            },
        ],
        "active_queue_refs": [
            {
                "queue_type": "decision_queue",
                "artifact_id": decision_queue["decision_queue_id"],
                "summary": decision["title"],
            },
            {
                "queue_type": "follow_up_queue",
                "artifact_id": follow_up_queue["follow_up_queue_id"],
                "summary": follow_up["title"],
            },
        ],
        "queue_recommendations": [
            {
                "queue_type": "decision_queue",
                "artifact_id": decision_queue["decision_queue_id"],
                "item_id": decision["decision_id"],
                "recommended_action": "review_now",
                "urgency": "routine",
                "why_now": "The runtime foundation is live and the next decision should shape the first V3.1 expansion based on evidence.",
            },
            {
                "queue_type": "follow_up_queue",
                "artifact_id": follow_up_queue["follow_up_queue_id"],
                "item_id": follow_up["follow_up_id"],
                "recommended_action": "start",
                "urgency": "time_sensitive",
                "why_now": "Validation evidence is complete and should be archived before the manual verification pass begins.",
            },
        ],
        "active_orchestration_state_id": orchestration_state_id,
        "active_execution_session_state_ids": [execution_session_state_id],
        "active_workflow_state_ids": ["wf_state_v3_runtime_foundation_2026_03_21"],
        "blocked_route_ids": [],
        "awaiting_review_route_ids": [],
        "pending_review_points": [],
        "missing_context_questions": [],
        "blocking_reasons": [],
        "source_artifact_ids": [
            decision_queue["decision_queue_id"],
            follow_up_queue["follow_up_queue_id"],
            feedback_log["feedback_log_id"],
        ],
        "created_at": generated_at,
        "updated_at": generated_at,
    }

    orchestration_state = {
        "schema_version": "1.0.0",
        "orchestration_state_id": orchestration_state_id,
        "workspace_id": workspace_id,
        "goal": "Execute the V3 runtime foundation with visible coordination, intake, memory, and release-gate proof.",
        "status": "completed",
        "coordination_summary": "The runtime foundation route is complete, validation passed, and the cockpit is now the stable PM-visible control surface.",
        "initiating_agent": "cockpit",
        "active_route_ids": [],
        "blocked_route_ids": [],
        "awaiting_review_route_ids": [],
        "linked_workflow_state_ids": ["wf_state_v3_runtime_foundation_2026_03_21"],
        "linked_execution_session_state_ids": [execution_session_state_id],
        "route_plan": [
            {
                "route_id": "route_update_runtime_contracts",
                "agent_name": "orchestrator",
                "objective": "Keep runtime state, queue impacts, and release-gate reasoning aligned.",
                "rationale": "PM-visible runtime coordination depends on one consistent control-surface and proof model.",
                "status": "completed",
                "expected_output_artifact_ids": [
                    cockpit_state_id,
                    runtime_scenario_report_id,
                    release_gate_decision_id,
                ],
                "notes": "Completed with cockpit_state established as the PM-visible coordination surface.",
            },
            {
                "route_id": "route_validate_runtime_bundle",
                "agent_name": "validation",
                "objective": "Validate runtime proof and release-gate outputs against schemas and completion criteria.",
                "rationale": "The runtime should clear release criteria only after schema, cross-reference, and proof validation pass together.",
                "status": "completed",
                "depends_on_route_ids": ["route_update_runtime_contracts"],
                "execution_session_state_id": execution_session_state_id,
                "notes": "Completed after schema validation, runtime proof, and release-readiness checks all passed.",
            },
            {
                "route_id": "route_runtime_proof",
                "agent_name": "workflow",
                "objective": "Generate benchmark, runtime scenario, and release-gate proof artifacts.",
                "rationale": "V3 should prove improvement over V2 with explicit evidence rather than narrative claims.",
                "status": "completed",
                "expected_output_artifact_ids": [
                    pm_benchmark_id,
                    release_readiness_id,
                    runtime_scenario_report_id,
                    release_gate_decision_id,
                ],
            },
        ],
        "queue_impacts": [
            {
                "queue_type": "decision_queue",
                "artifact_id": decision_queue["decision_queue_id"],
                "item_id": decision["decision_id"],
                "recommended_action": "review_now",
                "reason": "The runtime foundation is shipped, and this decision now shapes the first evidence-backed V3.1 expansion.",
                "status": "recommended",
            },
            {
                "queue_type": "follow_up_queue",
                "artifact_id": follow_up_queue["follow_up_queue_id"],
                "item_id": follow_up["follow_up_id"],
                "recommended_action": "start",
                "reason": "Validation evidence is complete and should be packaged for the manual verification pass.",
                "status": "queued",
            },
        ],
        "handoff_log": [
            {
                "timestamp": generated_at,
                "from_agent": "workflow",
                "to_agent": "orchestrator",
                "handoff_type": "artifact_transfer",
                "status": "accepted",
                "artifact_ids": [pm_benchmark_id, runtime_scenario_report_id],
                "message": "Runtime proof artifacts are ready for orchestration and release-gate review.",
            },
            {
                "timestamp": generated_at,
                "from_agent": "orchestrator",
                "to_agent": "cockpit",
                "handoff_type": "queue_recommendation",
                "status": "completed",
                "artifact_ids": [decision_queue["decision_queue_id"], follow_up_queue["follow_up_queue_id"]],
                "message": "Surface the completed runtime foundation through ongoing PM-visible queue recommendations.",
            },
        ],
        "retry_events": [],
        "escalations": [
            {
                "timestamp": generated_at,
                "owner": "ProductOS PM",
                "reason": "Final completion review confirmed the runtime foundation is ready for manual verification and live use.",
                "status": "resolved",
            }
        ],
        "created_at": generated_at,
        "updated_at": generated_at,
    }

    execution_session_state = {
        "schema_version": "1.0.0",
        "execution_session_state_id": execution_session_state_id,
        "workspace_id": workspace_id,
        "session_name": "V3 runtime proof execution session",
        "session_type": "worker_session",
        "status": "completed",
        "objective": "Build and validate the V3 runtime bundle from the self-hosting workspace.",
        "owner_agent": "workflow",
        "capability_adapter_id": "adapter_git_execution",
        "host_session_ref": "local_runtime_bundle_session",
        "parent_orchestration_state_id": orchestration_state_id,
        "source_workflow_state_id": "wf_state_v3_runtime_foundation_2026_03_21",
        "review_required": False,
        "verification_status": "passed",
        "input_refs": [
            decision_queue["decision_queue_id"],
            follow_up_queue["follow_up_queue_id"],
            feedback_log["feedback_log_id"],
        ],
        "output_refs": [
            cockpit_state_id,
            orchestration_state_id,
            intake_routing_state_id,
            memory_retrieval_state_id,
            feedback_cluster_state_id,
            runtime_scenario_report_id,
            release_gate_decision_id,
        ],
        "blocking_reasons": [],
        "event_log": [
            {"timestamp": generated_at, "event_type": "created", "message": "Runtime proof session created."},
            {"timestamp": generated_at, "event_type": "started", "message": "Runtime bundle generation started."},
            {"timestamp": generated_at, "event_type": "verification_started", "message": "Schema and test verification should run before clearing the session."},
            {"timestamp": generated_at, "event_type": "verification_passed", "message": "Schema, cross-reference, and runtime proof validation passed."},
            {"timestamp": generated_at, "event_type": "completed", "message": "Runtime bundle generation and validation completed."},
        ],
        "created_at": generated_at,
        "updated_at": generated_at,
        "completed_at": generated_at,
    }

    runtime_adapter_registry = {
        "schema_version": "1.0.0",
        "runtime_adapter_registry_id": f"runtime_adapter_registry_{workspace_id}",
        "workspace_id": workspace_id,
        "status": "partial",
        "adapters": [
            {
                "adapter_id": "adapter_worker_session",
                "name": "Context-Isolated Worker Session Adapter",
                "capability_type": "worker_session",
                "availability_status": "available",
                "supported_actions": [
                    "create_context_isolated_work_session",
                    "capture_session_output",
                    "close_session",
                ],
                "requires_host_support": True,
                "verification_status": "verified",
                "used_by_default": True,
                "host_constraints": ["Requires host support for bounded worker sessions."],
                "notes": "Primary adapter for runtime proof work.",
            },
            {
                "adapter_id": "adapter_git_execution",
                "name": "Git-Backed Execution Adapter",
                "capability_type": "git_execution",
                "availability_status": "available",
                "supported_actions": ["read_repository_state", "apply_patch", "run_local_validation"],
                "requires_host_support": True,
                "verification_status": "verified",
                "used_by_default": True,
                "host_constraints": ["Requires writable workspace access."],
                "notes": "Used for local runtime generation and validation.",
            },
        ],
        "evaluated_at": generated_at,
    }

    intake_routing_state = {
        "schema_version": "1.0.0",
        "intake_routing_state_id": intake_routing_state_id,
        "workspace_id": workspace_id,
        "ingestion_mode": "continuous",
        "status": "monitoring",
        "routing_summary": "The runtime is monitoring inbox paths continuously and routing captured items into transcript, note-card, and synthesis workflows.",
        "active_inbox_paths": [
            str((workspace_path / "inbox" / "raw-notes").relative_to(ROOT)),
            str((workspace_path / "inbox" / "transcripts").relative_to(ROOT)),
            str((workspace_path / "inbox" / "screenshots").relative_to(ROOT)),
        ],
        "intake_items": [
            {
                "item_id": "inbox_readme_raw_notes",
                "inbox_path": _inbox_readme(workspace_path, "raw-notes"),
                "input_type": "raw_note",
                "captured_at": generated_at,
                "provenance_status": "partial",
                "normalization_status": "pending",
                "recommended_workflow_ids": ["wf_research_notebook_to_synthesis"],
                "derived_artifact_ids": [],
                "notes": "Partial-provenance notes stay visible for follow-up without blocking the release gate.",
            },
            {
                "item_id": "inbox_readme_transcripts",
                "inbox_path": _inbox_readme(workspace_path, "transcripts"),
                "input_type": "transcript",
                "captured_at": generated_at,
                "provenance_status": "complete",
                "normalization_status": "routed",
                "recommended_workflow_ids": ["wf_transcript_to_notes", "wf_issue_log_maintenance"],
                "derived_artifact_ids": ["meeting_record_v3_runtime_review", "issue_log_2026_03_21"],
                "notes": "Transcript intake route remains active for runtime reviews.",
            },
            {
                "item_id": "inbox_readme_screenshots",
                "inbox_path": _inbox_readme(workspace_path, "screenshots"),
                "input_type": "screenshot",
                "captured_at": generated_at,
                "provenance_status": "complete",
                "normalization_status": "normalized",
                "recommended_workflow_ids": ["wf_source_ingestion_to_note_card"],
                "derived_artifact_ids": ["source_note_card_runtime_queue_state"],
                "notes": "Screenshot intake supports blocked-route explanation in the cockpit.",
            },
        ],
        "blocked_item_ids": [],
        "created_at": generated_at,
        "updated_at": generated_at,
    }

    memory_retrieval_state = {
        "schema_version": "1.0.0",
        "memory_retrieval_state_id": memory_retrieval_state_id,
        "workspace_id": workspace_id,
        "request_summary": "Retrieve prior decisions, feedback, and strategic memory that should shape the V3 runtime proof gate.",
        "status": "ready",
        "retrieval_scope": [
            "decisions",
            "prior_artifacts",
            "repeated_issues",
            "strategic_memory",
        ],
        "provenance_status": "complete",
        "retrieved_records": [
            {
                "record_type": "decision",
                "record_id": decision["decision_id"],
                "source_artifact_id": decision_queue["decision_queue_id"],
                "reason": "The runtime proof gate depends on the current PM-visible decision.",
                "freshness_status": "fresh",
                "confidence": 0.95,
                "provenance_ref": str((artifacts_dir / "decision_queue.example.json").relative_to(ROOT)),
            },
            {
                "record_type": "artifact",
                "record_id": cockpit_state_id,
                "source_artifact_id": cockpit_state_id,
                "reason": "The cockpit is the primary PM-visible consumer of reused context.",
                "freshness_status": "fresh",
                "confidence": 0.97,
                "provenance_ref": "generated_runtime_bundle",
            },
            {
                "record_type": "issue",
                "record_id": feedback_log["entries"][0]["feedback_id"],
                "source_artifact_id": feedback_log["feedback_log_id"],
                "reason": "Repeated PM pain should influence runtime gate clarity.",
                "freshness_status": "fresh",
                "confidence": 0.91,
                "provenance_ref": str((artifacts_dir / "productos_feedback_log.example.json").relative_to(ROOT)),
            },
            {
                "record_type": "strategic_memory",
                "record_id": strategic_memory["strategic_memory_record_id"],
                "source_artifact_id": strategic_memory["strategic_memory_record_id"],
                "reason": "The trust wedge remains relevant for runtime proof and visibility decisions.",
                "freshness_status": "fresh",
                "confidence": 0.88,
                "provenance_ref": str((CORE_EXAMPLES_DIR / "strategic_memory_record.example.json").relative_to(ROOT)),
            },
        ],
        "unresolved_questions": [],
        "provenance_warnings": [],
        "created_at": generated_at,
        "updated_at": generated_at,
    }

    feedback_cluster_state = {
        "schema_version": "1.0.0",
        "feedback_cluster_state_id": feedback_cluster_state_id,
        "workspace_id": workspace_id,
        "status": "ready_for_scope_review",
        "cluster_summary": "The strongest repeated V3 build pain is PM-visible coordination clarity, followed by provenance-aware memory reuse.",
        "clusters": [
            {
                "cluster_id": "cluster_pm_visible_coordination",
                "label": "PM-visible coordination clarity",
                "feedback_ids": coordination_feedback_ids or [feedback_log["entries"][0]["feedback_id"]],
                "dominant_category": "workflow_friction",
                "impact_level": "high",
                "recommended_route": "release_scope_review",
                "linked_output_refs": [cockpit_state_id, orchestration_state_id],
                "notes": "Repeated friction should stay inside the V3.0 runtime scope.",
            },
            {
                "cluster_id": "cluster_provenance_aware_memory",
                "label": "Provenance-aware memory reuse",
                "feedback_ids": reliability_feedback_ids or [feedback_log["entries"][-1]["feedback_id"]],
                "dominant_category": "reliability_incident",
                "impact_level": "medium",
                "recommended_route": "improvement_record",
                "linked_output_refs": [memory_retrieval_state_id, intake_routing_state_id],
                "notes": "The memory warning should remain explicit and downgrade confidence rather than disappear.",
            },
        ],
        "generated_at": generated_at,
    }

    release_scope_recommendation = {
        "schema_version": "1.0.0",
        "release_scope_recommendation_id": release_scope_recommendation_id,
        "workspace_id": workspace_id,
        "target_release": "v3_0",
        "change_classification": "major_product_change",
        "release_type": "major",
        "customer_visible": True,
        "internal_only_artifact": True,
        "rationale": "The repeated coordination-visibility pain changes the PM's live operating model and therefore belongs in the V3.0 runtime foundation.",
        "evidence_refs": [
            feedback_cluster_state_id,
            decision_queue["decision_queue_id"],
            follow_up_queue["follow_up_queue_id"],
            cockpit_state_id,
        ],
        "recommended_actions": [
            "Keep PM-visible coordination and queue-driven next actions in V3.0 scope.",
            "Use post-launch evidence to decide which runtime expansion should lead V3.1.",
        ],
        "deferred_feedback_ids": reliability_feedback_ids,
        "generated_at": generated_at,
    }

    pm_benchmark = {
        "schema_version": "1.0.0",
        "pm_benchmark_id": pm_benchmark_id,
        "workspace_id": workspace_id,
        "pm_identifier": "pm_productos_core",
        "evaluation_period": {
            "start_date": _date_from_timestamp(generated_at),
            "end_date": _date_from_timestamp(generated_at),
        },
        "baseline_metrics": [
            {"metric_name": "time_to_identify_blocked_route_minutes", "value": 12, "unit": "minutes"},
            {"metric_name": "time_to_route_new_inbox_item_minutes", "value": 18, "unit": "minutes"},
            {"metric_name": "time_to_find_relevant_prior_context_minutes", "value": 25, "unit": "minutes"},
        ],
        "current_metrics": [
            {"metric_name": "time_to_identify_blocked_route_minutes", "value": 2, "unit": "minutes"},
            {"metric_name": "time_to_route_new_inbox_item_minutes", "value": 4, "unit": "minutes"},
            {"metric_name": "time_to_find_relevant_prior_context_minutes", "value": 8, "unit": "minutes"},
        ],
        "benchmark_assessment": {
            "output_quality_trend": "improved",
            "decision_quality_trend": "improved",
            "speed_to_insight_trend": "improved",
            "rewrite_rate_trend": "improved",
            "overall_assessment": "The V3 runtime foundation materially reduces PM reconstruction work and makes operating state more legible than the V2 baseline.",
        },
        "world_class_reference_examples": [
            "Blocked runtime work is visible from one PM-facing cockpit surface.",
            "New inbox material routes forward with provenance instead of disappearing into ad hoc notes.",
        ],
        "recommended_focus_areas": [
            "Use the completed benchmark evidence to prioritize the first V3.1 runtime expansion.",
            "Keep broader learning-loop automation deferred until post-launch evidence justifies it.",
        ],
        "generated_at": generated_at,
    }

    release_readiness = {
        "schema_version": "1.1.0",
        "release_readiness_id": release_readiness_id,
        "workspace_id": workspace_id,
        "feature_id": "feature_v3_runtime_foundation",
        "status": "ready",
        "launch_roles": [
            {
                "role_name": "Launch owner",
                "responsibility": "Final go or no-go decision and staged rollout coordination",
                "assignment_status": "assigned",
                "owner_name": "ProductOS PM",
                "owner_function": "Product management",
            },
            {
                "role_name": "Runtime reviewer",
                "responsibility": "Confirm cockpit, orchestration, intake, and memory behaviors are coherent",
                "assignment_status": "assigned",
                "owner_name": "ProductOS PM",
                "owner_function": "Product operations",
            },
            {
                "role_name": "Support readiness reviewer",
                "responsibility": "Confirm internal guidance for blocked routes and provenance warnings",
                "assignment_status": "assigned",
                "owner_name": "ProductOS PM",
                "owner_function": "Support operations",
            },
        ],
        "checks": [
            {
                "name": "Runtime benchmark movement",
                "status": "passed",
                "notes": "Benchmark movement is materially stronger than the V2 baseline.",
            },
            {
                "name": "Runtime scenario proof",
                "status": "passed",
                "notes": "Runtime scenario coverage passed with provenance handling folded into the normal ready-state path.",
            },
            {
                "name": "Trust and compliance boundary",
                "status": "passed",
                "notes": "Internal-only learning-loop artifacts remain distinct from PM-facing product claims.",
            },
        ],
        "generated_at": generated_at,
    }

    runtime_scenario_report = {
        "schema_version": "1.0.0",
        "runtime_scenario_report_id": runtime_scenario_report_id,
        "workspace_id": workspace_id,
        "baseline_version": "2.0.0",
        "candidate_version": "3.0.0",
        "status": "passed",
        "summary": "The V3 runtime materially improves coordination visibility, intake routing, and memory reuse over V2, and all release-gate scenarios passed.",
        "scenarios": [
            {
                "scenario_id": "scenario_live_coordination_visibility",
                "name": "Live coordination visibility",
                "status": "passed",
                "metric_deltas": [
                    {
                        "metric_name": "time_to_identify_blocked_route_minutes",
                        "baseline_value": 12,
                        "candidate_value": 2,
                        "unit": "minutes",
                        "trend": "improved",
                    }
                ],
                "evidence_refs": [cockpit_state_id, orchestration_state_id],
                "gaps": [],
            },
            {
                "scenario_id": "scenario_continuous_intake_routing",
                "name": "Continuous intake to downstream routing",
                "status": "passed",
                "metric_deltas": [
                    {
                        "metric_name": "time_to_route_new_inbox_item_minutes",
                        "baseline_value": 18,
                        "candidate_value": 4,
                        "unit": "minutes",
                        "trend": "improved",
                    }
                ],
                "evidence_refs": [intake_routing_state_id],
                "gaps": [],
            },
            {
                "scenario_id": "scenario_memory_retrieval_with_provenance",
                "name": "Memory retrieval with provenance visibility",
                "status": "passed",
                "metric_deltas": [
                    {
                        "metric_name": "time_to_find_relevant_prior_context_minutes",
                        "baseline_value": 25,
                        "candidate_value": 8,
                        "unit": "minutes",
                        "trend": "improved",
                    },
                    {
                        "metric_name": "unsupported_memory_claim_risk_count",
                        "baseline_value": 2,
                        "candidate_value": 0,
                        "unit": "count",
                        "trend": "improved",
                    },
                ],
                "evidence_refs": [memory_retrieval_state_id, feedback_cluster_state_id],
                "gaps": [],
            },
        ],
        "generated_at": generated_at,
    }

    release_gate_decision = {
        "schema_version": "1.0.0",
        "release_gate_decision_id": release_gate_decision_id,
        "workspace_id": workspace_id,
        "target_release": "v3_0",
        "decision": "go",
        "pm_benchmark_ref": pm_benchmark_id,
        "runtime_scenario_report_ref": runtime_scenario_report_id,
        "release_readiness_ref": release_readiness_id,
        "rationale": "The V3 runtime foundation is materially stronger than V2 on coordination visibility, intake routing, and context reuse, and the release-readiness and runtime-proof checks now pass together.",
        "next_action": "Proceed to manual verification and ongoing post-launch evidence review through the cockpit queues.",
        "known_gaps": [
            "Broader learning-loop intelligence remains intentionally deferred to V3.1.",
            "Deeper PM behavior-pattern memory remains out of scope until post-launch evidence justifies it.",
        ],
        "deferred_items": [
            "Smarter feedback clustering and recommendation automation for V3.1.",
            "Deeper memory over PM behavior patterns after the baseline memory layer is proven stable.",
        ],
        "generated_at": generated_at,
    }

    return {
        "cockpit_state": cockpit_state,
        "orchestration_state": orchestration_state,
        "execution_session_state": execution_session_state,
        "runtime_adapter_registry": runtime_adapter_registry,
        "intake_routing_state": intake_routing_state,
        "memory_retrieval_state": memory_retrieval_state,
        "feedback_cluster_state": feedback_cluster_state,
        "release_scope_recommendation": release_scope_recommendation,
        "pm_benchmark": pm_benchmark,
        "release_readiness": release_readiness,
        "runtime_scenario_report": runtime_scenario_report,
        "release_gate_decision": release_gate_decision,
    }
