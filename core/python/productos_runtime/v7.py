from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .lifecycle import (
    LIFECYCLE_STAGE_ORDER,
    load_item_lifecycle_state_from_workspace,
    load_lifecycle_stage_snapshot_from_workspace,
)


V7_BASELINE_VERSION = "6.0.0"
V7_TARGET_VERSION = "7.0.0"
V7_TARGET_RELEASE = "v7_0_0"
V7_BUNDLE_ID = "v7_lifecycle_traceability_launch_and_outcome"
V7_BUNDLE_NAME = "Lifecycle traceability through outcome review"
V7_COMPLETION_STAGE_ORDER = [
    "launch_preparation",
    "outcome_review",
]

V7_ARTIFACT_SCHEMAS = {
    "runtime_scenario_report_v7_lifecycle_traceability": "runtime_scenario_report.schema.json",
    "validation_lane_report_v7_lifecycle_traceability": "validation_lane_report.schema.json",
    "manual_validation_record_v7_lifecycle_traceability": "manual_validation_record.schema.json",
    "release_readiness_v7_lifecycle_traceability": "release_readiness.schema.json",
    "release_gate_decision_v7_lifecycle_traceability": "release_gate_decision.schema.json",
    "ralph_loop_state_v7_lifecycle_traceability": "ralph_loop_state.schema.json",
}


def _root_dir_from_workspace(workspace_dir: Path | str) -> Path:
    return Path(__file__).resolve().parents[3]


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _completed_stage_count(item_state: dict[str, Any], stage_order: list[str]) -> int:
    stage_status = {
        stage["stage_key"]: stage["status"]
        for stage in item_state["lifecycle_stages"]
        if stage["stage_key"] in stage_order
    }
    return sum(1 for stage_key in stage_order if stage_status.get(stage_key) == "completed")


def _has_expected_stage_shape(item_state: dict[str, Any]) -> bool:
    return [stage["stage_key"] for stage in item_state["lifecycle_stages"]] == LIFECYCLE_STAGE_ORDER


def _all_required_focus_areas_exist(workspace_dir: Path) -> bool:
    for focus_area in ("discovery", "delivery", "launch", "outcomes", "full_lifecycle"):
        try:
            load_lifecycle_stage_snapshot_from_workspace(workspace_dir, focus_area=focus_area)
        except KeyError:
            return False
    return True


def build_v7_lifecycle_bundle_from_workspace(
    workspace_dir: Path | str,
    *,
    generated_at: str,
    target_version: str = V7_TARGET_VERSION,
) -> dict[str, dict[str, Any]]:
    workspace_dir = Path(workspace_dir).resolve()
    root_dir = _root_dir_from_workspace(workspace_dir)
    starter_dir = root_dir / "templates"

    workspace_item = load_item_lifecycle_state_from_workspace(
        workspace_dir,
        item_id="opp_pm_lifecycle_traceability",
    )
    workspace_launch_snapshot = load_lifecycle_stage_snapshot_from_workspace(
        workspace_dir,
        focus_area="launch",
    )
    workspace_outcomes_snapshot = load_lifecycle_stage_snapshot_from_workspace(
        workspace_dir,
        focus_area="outcomes",
    )
    workspace_full_snapshot = load_lifecycle_stage_snapshot_from_workspace(
        workspace_dir,
        focus_area="full_lifecycle",
    )
    starter_item = load_item_lifecycle_state_from_workspace(starter_dir)
    starter_launch_snapshot = load_lifecycle_stage_snapshot_from_workspace(
        starter_dir,
        focus_area="launch",
    )
    starter_outcomes_snapshot = load_lifecycle_stage_snapshot_from_workspace(
        starter_dir,
        focus_area="outcomes",
    )
    starter_full_snapshot = load_lifecycle_stage_snapshot_from_workspace(
        starter_dir,
        focus_area="full_lifecycle",
    )

    workspace_completion_count = _completed_stage_count(workspace_item, V7_COMPLETION_STAGE_ORDER)
    starter_completion_count = _completed_stage_count(starter_item, V7_COMPLETION_STAGE_ORDER)

    reference_workspace_ready = (
        workspace_item["current_stage"] == "outcome_review"
        and workspace_item["overall_status"] == "completed"
        and workspace_completion_count == len(V7_COMPLETION_STAGE_ORDER)
        and _has_expected_stage_shape(workspace_item)
        and workspace_launch_snapshot["gate_counts"]["passed"] == 1
        and workspace_outcomes_snapshot["gate_counts"]["passed"] == 1
        and workspace_full_snapshot["gate_counts"]["passed"] == len(LIFECYCLE_STAGE_ORDER)
    )
    starter_ready = (
        starter_item["current_stage"] == "outcome_review"
        and starter_item["overall_status"] == "completed"
        and starter_completion_count == len(V7_COMPLETION_STAGE_ORDER)
        and _has_expected_stage_shape(starter_item)
        and starter_launch_snapshot["gate_counts"]["passed"] == 1
        and starter_outcomes_snapshot["gate_counts"]["passed"] == 1
        and starter_full_snapshot["gate_counts"]["passed"] == len(LIFECYCLE_STAGE_ORDER)
    )
    focus_area_coverage_ready = _all_required_focus_areas_exist(workspace_dir) and _all_required_focus_areas_exist(starter_dir)
    full_lifecycle_completion_ready = (
        workspace_full_snapshot["gate_counts"]["not_started"] == 0
        and starter_full_snapshot["gate_counts"]["not_started"] == 0
    )

    scenario_statuses = [
        reference_workspace_ready,
        starter_ready,
        focus_area_coverage_ready,
        full_lifecycle_completion_ready,
    ]
    overall_status = "passed" if all(scenario_statuses) else ("watch" if any(scenario_statuses) else "failed")

    runtime_scenario_report = {
        "schema_version": "1.0.0",
        "runtime_scenario_report_id": "runtime_scenario_report_ws_productos_v2_v7_lifecycle_traceability",
        "workspace_id": workspace_item["workspace_id"],
        "baseline_version": V7_BASELINE_VERSION,
        "candidate_version": target_version,
        "status": overall_status,
        "summary": (
            "The selected V7 bundle proves one canonical lifecycle trace through launch preparation and post-release outcome review in both the reference and starter workspaces."
            if overall_status == "passed"
            else "The selected V7 lifecycle-traceability bundle is partially proven, but one or more launch, outcome, parity, or full-lifecycle checks still need review."
        ),
        "scenarios": [
            {
                "scenario_id": "scenario_reference_workspace_traceability_to_outcome_review",
                "name": "Reference workspace lifecycle traceability through outcome review",
                "status": "passed" if reference_workspace_ready else "failed",
                "metric_deltas": [
                    {
                        "metric_name": "completed_launch_and_outcome_stage_count",
                        "baseline_value": 0,
                        "candidate_value": workspace_completion_count,
                        "unit": "count",
                        "trend": "improved" if workspace_completion_count else "flat",
                    }
                ],
                "evidence_refs": [
                    workspace_item["item_lifecycle_state_id"],
                    workspace_launch_snapshot["lifecycle_stage_snapshot_id"],
                    workspace_outcomes_snapshot["lifecycle_stage_snapshot_id"],
                    "templates/docs/delivery/launch-outcome-review.md",
                ],
                "gaps": [] if reference_workspace_ready else ["Reference workspace lifecycle evidence does not yet cleanly reach launch preparation and outcome review."],
            },
            {
                "scenario_id": "scenario_starter_workspace_traceability_to_outcome_review",
                "name": "Starter-workspace parity through outcome review",
                "status": "passed" if starter_ready else "failed",
                "metric_deltas": [
                    {
                        "metric_name": "starter_completed_launch_and_outcome_stage_count",
                        "baseline_value": 0,
                        "candidate_value": starter_completion_count,
                        "unit": "count",
                        "trend": "improved" if starter_completion_count else "flat",
                    }
                ],
                "evidence_refs": [
                    starter_item["item_lifecycle_state_id"],
                    starter_launch_snapshot["lifecycle_stage_snapshot_id"],
                    starter_outcomes_snapshot["lifecycle_stage_snapshot_id"],
                    "templates/docs/delivery/launch-outcome-review.md",
                ],
                "gaps": [] if starter_ready else ["The starter workspace does not yet mirror the selected launch and outcome trace strongly enough."],
            },
            {
                "scenario_id": "scenario_trace_focus_area_coverage",
                "name": "Trace focus-area coverage remains aligned with the CLI contract",
                "status": "passed" if focus_area_coverage_ready else "failed",
                "metric_deltas": [
                    {
                        "metric_name": "available_trace_focus_area_count",
                        "baseline_value": 5,
                        "candidate_value": 5 if focus_area_coverage_ready else 0,
                        "unit": "count",
                        "trend": "flat" if focus_area_coverage_ready else "regressed",
                    }
                ],
                "evidence_refs": [
                    workspace_full_snapshot["lifecycle_stage_snapshot_id"],
                    starter_full_snapshot["lifecycle_stage_snapshot_id"],
                    "README.md",
                ],
                "gaps": [] if focus_area_coverage_ready else ["The advertised trace focus areas are not all backed by workspace snapshots."],
            },
            {
                "scenario_id": "scenario_full_lifecycle_completion",
                "name": "Launch and outcome stages are no longer deferred",
                "status": "passed" if full_lifecycle_completion_ready else "watch",
                "metric_deltas": [
                    {
                        "metric_name": "not_started_stage_count_after_release_readiness",
                        "baseline_value": 2,
                        "candidate_value": workspace_full_snapshot["gate_counts"]["not_started"],
                        "unit": "count",
                        "trend": "improved" if workspace_full_snapshot["gate_counts"]["not_started"] == 0 else "flat",
                    }
                ],
                "evidence_refs": [
                    workspace_item["item_lifecycle_state_id"],
                    starter_item["item_lifecycle_state_id"],
                    "CHANGELOG.md",
                ],
                "gaps": [] if full_lifecycle_completion_ready else ["Launch preparation and outcome review are not yet completed across both adoption surfaces."],
            },
        ],
        "generated_at": generated_at,
    }

    validation_status = "passed" if overall_status == "passed" else ("ready_for_manual_validation" if overall_status == "watch" else "blocked")
    reviewer_status = "proceed" if overall_status == "passed" else ("revise" if overall_status == "watch" else "block")
    tester_status = "passed" if overall_status == "passed" else ("revise" if overall_status == "watch" else "failed")
    manual_policy_status = "passed" if overall_status == "passed" else ("pending" if overall_status == "watch" else "rejected")

    validation_lane_report = {
        "schema_version": "1.0.0",
        "validation_lane_report_id": "validation_lane_report_ws_productos_v2_v7_lifecycle_traceability",
        "workspace_id": workspace_item["workspace_id"],
        "artifact_ref": runtime_scenario_report["runtime_scenario_report_id"],
        "artifact_type": "runtime_scenario_report",
        "stage_name": "v7_0_lifecycle_traceability_outcome_review",
        "validation_tier": "tier_2",
        "overall_status": validation_status,
        "review_summary": (
            "The selected V7 bundle is correctly scoped: it extends the canonical item trace through launch preparation and post-release outcome review while preserving starter-workspace parity."
            if overall_status == "passed"
            else "The selected V7 bundle still needs review because one or more launch, outcome, parity, or full-lifecycle checks are not fully satisfied."
        ),
        "ai_reviewer_lane": {
            "status": reviewer_status,
            "reviewer_role": "AI Reviewer",
            "blocking_findings": [] if overall_status == "passed" else ["The selected V7 release claim is not yet fully supported by the current launch and outcome lifecycle evidence."],
            "non_blocking_findings": [
                "The current bundle now includes explicit launch-preparation evidence and a post-release outcome review.",
                "External publication adapters remain intentionally out of scope for this lifecycle-only promotion.",
            ],
            "unresolved_questions": [] if overall_status == "passed" else ["Which launch, outcome, or parity gap must be closed before the selected V7 bundle can promote?"],
        },
        "ai_tester_lane": {
            "status": tester_status,
            "tester_role": "AI Tester",
            "checks_run": [
                "Validated reference-workspace lifecycle state through launch preparation and outcome review.",
                "Validated starter-workspace lifecycle state parity through launch preparation and outcome review.",
                "Validated discovery, delivery, launch, outcomes, and full_lifecycle snapshot coverage.",
                "Validated that no post-release_readiness stages remain not_started in the promoted slice.",
            ],
            "blocking_findings": [] if overall_status == "passed" else ["One or more launch or outcome lifecycle proof checks did not pass."],
            "non_blocking_findings": [
                "The promoted V7 slice still keeps external publication adapters outside the stable claim.",
            ],
            "automation_gaps": [
                "Future releases should add parity checks for external publication adapters and broader distribution packaging that consume lifecycle traces.",
            ],
        },
        "manual_validation_policy": {
            "required": True,
            "scope": "targeted",
            "owner_role": "PM Operator",
            "status": manual_policy_status,
            "rationale": "Full-lifecycle traceability changes the stable product claim, so targeted PM review remains mandatory even when automated proof passes.",
        },
        "referee_trigger": {
            "required": False,
            "rationale": "Reviewer and tester lanes align on the same scoped V7 claim and do not currently conflict.",
            "conflicting_lanes": [],
        },
        "governance_layer_refs": [
            workspace_item["item_lifecycle_state_id"],
            workspace_launch_snapshot["lifecycle_stage_snapshot_id"],
            workspace_outcomes_snapshot["lifecycle_stage_snapshot_id"],
            workspace_full_snapshot["lifecycle_stage_snapshot_id"],
            starter_item["item_lifecycle_state_id"],
            starter_launch_snapshot["lifecycle_stage_snapshot_id"],
            starter_outcomes_snapshot["lifecycle_stage_snapshot_id"],
            starter_full_snapshot["lifecycle_stage_snapshot_id"],
            "release_readiness_ws_productos_v2_v6_lifecycle_traceability",
        ],
        "next_action": (
            "Promote the selected lifecycle-traceability slice as ProductOS V7.0.0."
            if overall_status == "passed"
            else "Resolve the remaining lifecycle-traceability proof gap before promoting ProductOS V7.0.0."
        ),
        "generated_at": generated_at,
    }

    manual_validation_record = {
        "schema_version": "1.0.0",
        "manual_validation_record_id": "manual_validation_record_ws_productos_v2_v7_lifecycle_traceability",
        "workspace_id": workspace_item["workspace_id"],
        "subject_ref": runtime_scenario_report["runtime_scenario_report_id"],
        "subject_type": "runtime_scenario_report",
        "validation_tier": "tier_2",
        "validator_role": "PM Operator",
        "scope": "targeted",
        "decision": "accept" if overall_status == "passed" else ("defer" if overall_status == "watch" else "reject"),
        "fit_notes": [
            "The selected V7 slice keeps one canonical opportunity readable from intake through release communication and post-release learning.",
            "The trace command remains aligned with concrete discovery, delivery, launch, outcomes, and full-lifecycle snapshots.",
        ],
        "required_follow_ups": [
            "Extend lifecycle traces into external publication adapters as first-class inputs in a later bounded release.",
            "Define broader reusable distribution packaging that preserves release and outcome provenance.",
        ],
        "related_validation_report_ref": validation_lane_report["validation_lane_report_id"],
        "final_approval": overall_status == "passed",
        "recorded_at": generated_at,
    }

    release_readiness_status = "ready" if overall_status == "passed" else ("watch" if overall_status == "watch" else "blocked")
    release_gate_decision_id = "release_gate_decision_ws_productos_v2_v7_lifecycle_traceability"
    release_readiness = {
        "schema_version": "1.2.0",
        "release_readiness_id": "release_readiness_ws_productos_v2_v7_lifecycle_traceability",
        "workspace_id": workspace_item["workspace_id"],
        "feature_id": "feature_v7_lifecycle_traceability_outcome_review",
        "status": release_readiness_status,
        "decision_summary": "The V7 slice is ready when launch preparation and outcome review are completed in both adoption surfaces and the claim remains tightly bounded to that lifecycle proof.",
        "launch_roles": [
            {
                "role_name": "Release owner",
                "responsibility": "Approve the V7.0 promotion for lifecycle traceability through outcome review.",
                "assignment_status": "assigned",
                "owner_name": "ProductOS PM",
                "owner_function": "Product management",
            },
            {
                "role_name": "Adoption owner",
                "responsibility": "Confirm the starter workspace remains the reusable adoption surface for the promoted V7 slice.",
                "assignment_status": "assigned",
                "owner_name": "ProductOS PM",
                "owner_function": "Workspace adoption",
            },
            {
                "role_name": "Lifecycle reviewer",
                "responsibility": "Confirm launch preparation, release communication, and outcome review are explicitly attached to the canonical item trace.",
                "assignment_status": "assigned",
                "owner_name": "ProductOS PM",
                "owner_function": "Runtime governance",
            },
        ],
        "claim_readiness": [
            {
                "claim": "The V7 bundle proves lifecycle traceability through launch preparation and outcome review in both adoption surfaces.",
                "status": "verified" if reference_workspace_ready and starter_ready else "blocked",
                "evidence_refs": [runtime_scenario_report["runtime_scenario_report_id"], manual_validation_record["manual_validation_record_id"]],
            },
            {
                "claim": "The V7 release communication remains bounded to lifecycle traceability rather than broader publication-platform scope.",
                "status": "bounded",
                "evidence_refs": [release_gate_decision_id],
            },
        ],
        "blocking_evidence_refs": [runtime_scenario_report["runtime_scenario_report_id"]],
        "checks": [
            {
                "name": "Reference workspace lifecycle trace reaches outcome_review",
                "status": "passed" if reference_workspace_ready else "failed",
                "notes": "The reference workspace exposes one item-first lifecycle trace from discovery through launch preparation and outcome review.",
            },
            {
                "name": "Starter-workspace adoption parity through outcome_review",
                "status": "passed" if starter_ready else "failed",
                "notes": "The starter workspace mirrors the selected lifecycle-traceability path through launch preparation and outcome review.",
            },
            {
                "name": "Trace focus-area coverage",
                "status": "passed" if focus_area_coverage_ready else "failed",
                "notes": "All advertised trace focus areas remain backed by concrete workspace snapshots behind the CLI surface.",
            },
            {
                "name": "No deferred post-release_readiness stages remain",
                "status": "passed" if full_lifecycle_completion_ready else "watch",
                "notes": "Launch preparation and outcome review are completed across both adoption surfaces in the promoted V7 slice.",
            },
        ],
        "generated_at": generated_at,
    }

    release_gate_decision = {
        "schema_version": "1.0.0",
        "release_gate_decision_id": release_gate_decision_id,
        "workspace_id": workspace_item["workspace_id"],
        "target_release": V7_TARGET_RELEASE,
        "decision": "go" if overall_status == "passed" else ("conditional_go" if overall_status == "watch" else "no_go"),
        "pm_benchmark_ref": "pm_superpower_benchmark_ws_productos_v2_v4_0",
        "runtime_scenario_report_ref": runtime_scenario_report["runtime_scenario_report_id"],
        "release_readiness_ref": release_readiness["release_readiness_id"],
        "rationale": (
            "The selected V7 bundle proves one canonical lifecycle trace through launch preparation and post-release outcome review in both the reference and starter workspaces."
            if overall_status == "passed"
            else "The selected V7 lifecycle-traceability bundle still has unresolved proof gaps, so stable promotion should wait for those checks to pass."
        ),
        "next_action": (
            "Promote ProductOS to V7.0.0 stable via the Ralph-gated release command."
            if overall_status == "passed"
            else "Keep the selected V7 bundle in build-beside mode until the remaining lifecycle-traceability proof gaps are resolved."
        ),
        "known_gaps": [
            "External publication adapters do not yet consume lifecycle traces as first-class inputs.",
            "Broader distribution packaging beyond the current internal and starter surfaces remains deferred to a later bounded release.",
        ],
        "deferred_items": [
            "Extend the trace model into external publication adapters and governed sync routes.",
            "Define broader reusable distribution packaging that preserves lifecycle provenance outside the repo and starter surfaces.",
        ],
        "generated_at": generated_at,
    }

    ralph_loop_state = {
        "schema_version": "1.0.0",
        "ralph_loop_state_id": "ralph_loop_state_ws_productos_v2_v7_lifecycle_traceability",
        "workspace_id": workspace_item["workspace_id"],
        "target_release": V7_TARGET_RELEASE,
        "loop_goal": "Inspect, review, implement, validate, fix, and revalidate the lifecycle-traceability through outcome review slice before stable release promotion.",
        "overall_status": "ready_for_release" if overall_status == "passed" else "blocked",
        "subject_refs": [
            workspace_item["item_lifecycle_state_id"],
            workspace_launch_snapshot["lifecycle_stage_snapshot_id"],
            workspace_outcomes_snapshot["lifecycle_stage_snapshot_id"],
            workspace_full_snapshot["lifecycle_stage_snapshot_id"],
            starter_item["item_lifecycle_state_id"],
            starter_launch_snapshot["lifecycle_stage_snapshot_id"],
            starter_outcomes_snapshot["lifecycle_stage_snapshot_id"],
            starter_full_snapshot["lifecycle_stage_snapshot_id"],
            runtime_scenario_report["runtime_scenario_report_id"],
            validation_lane_report["validation_lane_report_id"],
            manual_validation_record["manual_validation_record_id"],
            release_gate_decision["release_gate_decision_id"],
        ],
        "stages": [
            {
                "stage_key": "inspect",
                "status": "passed" if reference_workspace_ready else "blocked",
                "owner": "AI Librarian",
                "findings_summary": "The reference and starter-workspace lifecycle traces were inspected as one bounded V7 release claim through launch preparation and outcome review.",
                "evidence_refs": [
                    workspace_item["item_lifecycle_state_id"],
                    starter_item["item_lifecycle_state_id"],
                ],
                "exit_condition": "Both lifecycle traces are explicit enough to review as one bounded V7 slice.",
            },
            {
                "stage_key": "review",
                "status": "passed" if overall_status == "passed" else "blocked",
                "owner": "AI Reviewer",
                "findings_summary": "The selected V7 claim is correctly bounded to full lifecycle traceability and does not overstate external publication coverage.",
                "evidence_refs": [
                    validation_lane_report["validation_lane_report_id"],
                ],
                "exit_condition": "The promoted claim stays tightly scoped to lifecycle traceability through outcome review.",
            },
            {
                "stage_key": "validate",
                "status": "passed" if overall_status == "passed" else "blocked",
                "owner": "AI Tester",
                "findings_summary": "Parity, focus-area coverage, stage-shape, and full-lifecycle completion checks agree on the selected V7 slice.",
                "evidence_refs": [
                    runtime_scenario_report["runtime_scenario_report_id"],
                    validation_lane_report["validation_lane_report_id"],
                ],
                "exit_condition": "Automated parity, focus-area, and full-lifecycle proof passes for both the reference and starter workspaces.",
            },
            {
                "stage_key": "implement",
                "status": "passed" if overall_status == "passed" else "blocked",
                "owner": "AI Product Shaper",
                "findings_summary": "The repo exposes lifecycle traceability through outcome review as an explicit V7 build slice.",
                "evidence_refs": [
                    runtime_scenario_report["runtime_scenario_report_id"],
                    "CHANGELOG.md",
                ],
                "exit_condition": "The selected V7 slice exists concretely in the repo and can be validated and promoted.",
            },
            {
                "stage_key": "fix",
                "status": "passed" if overall_status == "passed" else "blocked",
                "owner": "AI Product Shaper",
                "findings_summary": "The release package leaves publication adapters and broader distribution packaging as explicit deferred work instead of hidden scope.",
                "evidence_refs": [
                    release_gate_decision["release_gate_decision_id"],
                ],
                "exit_condition": "Deferred work is explicit and does not leak into the promoted V7 claim.",
            },
            {
                "stage_key": "revalidate",
                "status": "passed" if overall_status == "passed" else "blocked",
                "owner": "PM Operator",
                "findings_summary": "Manual review confirms the selected V7 lifecycle-traceability slice is ready to become the stable ProductOS baseline.",
                "evidence_refs": [
                    manual_validation_record["manual_validation_record_id"],
                ],
                "exit_condition": "One explicit proceed decision exists and no unresolved blocking disagreement remains.",
            },
        ],
        "validation_report_refs": [
            validation_lane_report["validation_lane_report_id"],
        ],
        "manual_review_summary": (
            "The V7 release is acceptable because it promotes one concrete lifecycle-traceability slice through launch preparation and outcome review while keeping publication adapters out of scope."
            if overall_status == "passed"
            else "The V7 release is not yet acceptable because the selected lifecycle-traceability slice still has unresolved proof gaps."
        ),
        "next_action": (
            "Promote ProductOS to V7.0.0 stable and plan the next bounded external-publication expansion."
            if overall_status == "passed"
            else "Keep the selected V7 lifecycle-traceability slice in build-beside mode until it is ready for stable promotion."
        ),
        "generated_at": generated_at,
    }

    return {
        "runtime_scenario_report_v7_lifecycle_traceability": runtime_scenario_report,
        "validation_lane_report_v7_lifecycle_traceability": validation_lane_report,
        "manual_validation_record_v7_lifecycle_traceability": manual_validation_record,
        "release_readiness_v7_lifecycle_traceability": release_readiness,
        "release_gate_decision_v7_lifecycle_traceability": release_gate_decision,
        "ralph_loop_state_v7_lifecycle_traceability": ralph_loop_state,
    }


def summarize_v7_lifecycle_bundle(
    workspace_dir: Path | str,
    bundle: dict[str, dict[str, Any]],
) -> str:
    workspace_item = load_item_lifecycle_state_from_workspace(
        workspace_dir,
        item_id="opp_pm_lifecycle_traceability",
    )
    starter_item = load_item_lifecycle_state_from_workspace(
        _root_dir_from_workspace(workspace_dir) / "templates"
    )
    report = bundle["runtime_scenario_report_v7_lifecycle_traceability"]
    decision = bundle["release_gate_decision_v7_lifecycle_traceability"]
    readiness = bundle["release_readiness_v7_lifecycle_traceability"]
    return "\n".join(
        [
            f"V7 Bundle: {V7_BUNDLE_NAME}",
            f"Target Release: {report['candidate_version']}",
            f"Scenario Status: {report['status']}",
            f"Reference Stage: {workspace_item['current_stage']}",
            f"Starter Stage: {starter_item['current_stage']}",
            f"Release Readiness: {readiness['status']}",
            f"Release Decision: {decision['decision']}",
        ]
    )
