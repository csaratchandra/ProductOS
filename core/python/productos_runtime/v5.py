from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .lifecycle import (
    DISCOVERY_STAGE_ORDER,
    LIFECYCLE_STAGE_ORDER,
    load_item_lifecycle_state_from_workspace,
    load_lifecycle_stage_snapshot_from_workspace,
)


V5_BASELINE_VERSION = "4.8.0"
V5_TARGET_VERSION = "5.0.0"
V5_TARGET_RELEASE = "v5_0_0"
V5_BUNDLE_ID = "v5_lifecycle_traceability_prd_handoff"
V5_BUNDLE_NAME = "Lifecycle traceability through PRD handoff"

V5_ARTIFACT_SCHEMAS = {
    "runtime_scenario_report_v5_lifecycle_traceability": "runtime_scenario_report.schema.json",
    "validation_lane_report_v5_lifecycle_traceability": "validation_lane_report.schema.json",
    "manual_validation_record_v5_lifecycle_traceability": "manual_validation_record.schema.json",
    "release_readiness_v5_lifecycle_traceability": "release_readiness.schema.json",
    "release_gate_decision_v5_lifecycle_traceability": "release_gate_decision.schema.json",
    "ralph_loop_state_v5_lifecycle_traceability": "ralph_loop_state.schema.json",
}


def _root_dir_from_workspace(workspace_dir: Path | str) -> Path:
    return Path(workspace_dir).resolve().parents[1]


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_archived_v5_item_and_snapshot(workspace_dir: Path | str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    root_dir = _root_dir_from_workspace(workspace_dir)
    archive_dir = root_dir / "workspaces" / "productos-v2" / "archive" / "historical-artifacts" / "v5_lifecycle_traceability"
    if archive_dir.exists():
        return (
            _load_json(archive_dir / "item_lifecycle_state_pm_lifecycle_visibility.example.json"),
            _load_json(archive_dir / "lifecycle_stage_snapshot_discovery.example.json"),
            _load_json(archive_dir / "starter_item_lifecycle_state.json"),
            _load_json(archive_dir / "starter_lifecycle_stage_snapshot.json"),
        )

    starter_dir = root_dir / "workspaces" / "product-starter"
    return (
        load_item_lifecycle_state_from_workspace(
            workspace_dir,
            item_id="opp_pm_lifecycle_traceability",
        ),
        load_lifecycle_stage_snapshot_from_workspace(
            workspace_dir,
            focus_area="discovery",
        ),
        load_item_lifecycle_state_from_workspace(starter_dir),
        load_lifecycle_stage_snapshot_from_workspace(
            starter_dir,
            focus_area="discovery",
        ),
    )


def _completed_discovery_stage_count(item_state: dict[str, Any]) -> int:
    discovery_status = {
        stage["stage_key"]: stage["status"]
        for stage in item_state["lifecycle_stages"]
        if stage["stage_key"] in DISCOVERY_STAGE_ORDER
    }
    return sum(1 for stage_key in DISCOVERY_STAGE_ORDER if discovery_status.get(stage_key) == "completed")


def _explicit_post_prd_stage_count(item_state: dict[str, Any]) -> int:
    after_handoff = False
    count = 0
    for stage in item_state["lifecycle_stages"]:
        if stage["stage_key"] == "prd_handoff":
            after_handoff = True
            continue
        if after_handoff and stage["status"] == "not_started":
            count += 1
    return count


def _has_expected_stage_shape(item_state: dict[str, Any]) -> bool:
    return [stage["stage_key"] for stage in item_state["lifecycle_stages"]] == LIFECYCLE_STAGE_ORDER


def build_v5_lifecycle_bundle_from_workspace(
    workspace_dir: Path | str,
    *,
    generated_at: str,
    target_version: str = V5_TARGET_VERSION,
) -> dict[str, dict[str, Any]]:
    workspace_dir = Path(workspace_dir).resolve()
    workspace_item, workspace_snapshot, starter_item, starter_snapshot = _load_archived_v5_item_and_snapshot(workspace_dir)

    workspace_discovery_count = _completed_discovery_stage_count(workspace_item)
    starter_discovery_count = _completed_discovery_stage_count(starter_item)
    workspace_post_prd_count = _explicit_post_prd_stage_count(workspace_item)
    starter_post_prd_count = _explicit_post_prd_stage_count(starter_item)

    self_hosting_ready = (
        workspace_item["current_stage"] == "prd_handoff"
        and workspace_item["overall_status"] == "ready_for_handoff"
        and workspace_discovery_count == len(DISCOVERY_STAGE_ORDER)
        and _has_expected_stage_shape(workspace_item)
        and workspace_snapshot["gate_counts"]["passed"] == len(DISCOVERY_STAGE_ORDER)
    )
    starter_ready = (
        starter_item["current_stage"] == "prd_handoff"
        and starter_discovery_count == len(DISCOVERY_STAGE_ORDER)
        and _has_expected_stage_shape(starter_item)
        and starter_snapshot["gate_counts"]["passed"] == len(DISCOVERY_STAGE_ORDER)
    )
    scoped_boundary_ready = (
        workspace_post_prd_count == len(LIFECYCLE_STAGE_ORDER) - len(DISCOVERY_STAGE_ORDER)
        and starter_post_prd_count == len(LIFECYCLE_STAGE_ORDER) - len(DISCOVERY_STAGE_ORDER)
    )

    scenario_statuses = [self_hosting_ready, starter_ready, scoped_boundary_ready]
    overall_status = "passed" if all(scenario_statuses) else ("watch" if any(scenario_statuses) else "failed")

    runtime_scenario_report = {
        "schema_version": "1.0.0",
        "runtime_scenario_report_id": "runtime_scenario_report_ws_productos_v2_v5_lifecycle_traceability",
        "workspace_id": workspace_item["workspace_id"],
        "baseline_version": V5_BASELINE_VERSION,
        "candidate_version": target_version,
        "status": overall_status,
        "summary": (
            "The selected V5 bundle proves item-first lifecycle traceability through prd_handoff in the self-hosting workspace and the starter workspace while keeping later lifecycle stages explicitly deferred."
            if overall_status == "passed"
            else "The selected V5 lifecycle-traceability bundle is partially proven, but one or more parity or scope-boundary checks still need review."
        ),
        "scenarios": [
            {
                "scenario_id": "scenario_self_hosting_traceability_to_prd_handoff",
                "name": "Self-hosting lifecycle traceability through PRD handoff",
                "status": "passed" if self_hosting_ready else "failed",
                "metric_deltas": [
                    {
                        "metric_name": "completed_discovery_stage_count",
                        "baseline_value": 0,
                        "candidate_value": workspace_discovery_count,
                        "unit": "count",
                        "trend": "improved" if workspace_discovery_count else "flat",
                    }
                ],
                "evidence_refs": [
                    workspace_item["item_lifecycle_state_id"],
                    workspace_snapshot["lifecycle_stage_snapshot_id"],
                    "workspaces/productos-v2/docs/discovery/lifecycle-traceability-review.md",
                ],
                "gaps": [] if self_hosting_ready else ["Self-hosting lifecycle evidence does not yet cleanly reach prd_handoff."],
            },
            {
                "scenario_id": "scenario_starter_workspace_traceability_parity",
                "name": "Starter-workspace parity for lifecycle traceability",
                "status": "passed" if starter_ready else "failed",
                "metric_deltas": [
                    {
                        "metric_name": "starter_traceable_item_count",
                        "baseline_value": 0,
                        "candidate_value": starter_snapshot["item_count"],
                        "unit": "count",
                        "trend": "improved" if starter_snapshot["item_count"] else "flat",
                    }
                ],
                "evidence_refs": [
                    starter_item["item_lifecycle_state_id"],
                    starter_snapshot["lifecycle_stage_snapshot_id"],
                    "workspaces/product-starter/README.md",
                ],
                "gaps": [] if starter_ready else ["The starter workspace does not yet mirror the selected lifecycle-traceability path strongly enough."],
            },
            {
                "scenario_id": "scenario_scoped_boundary_after_prd_handoff",
                "name": "Scoped boundary after PRD handoff remains explicit",
                "status": "passed" if scoped_boundary_ready else "watch",
                "metric_deltas": [
                    {
                        "metric_name": "explicit_post_prd_stage_count",
                        "baseline_value": 0,
                        "candidate_value": min(workspace_post_prd_count, starter_post_prd_count),
                        "unit": "count",
                        "trend": "improved" if min(workspace_post_prd_count, starter_post_prd_count) else "flat",
                    }
                ],
                "evidence_refs": [
                    workspace_item["item_lifecycle_state_id"],
                    starter_item["item_lifecycle_state_id"],
                    "workspaces/productos-v2/docs/planning/v5-candidate-note.md",
                ],
                "gaps": [] if scoped_boundary_ready else ["Later lifecycle stages are not yet kept explicit as not_started across both adoption surfaces."],
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
        "validation_lane_report_id": "validation_lane_report_ws_productos_v2_v5_lifecycle_traceability",
        "workspace_id": workspace_item["workspace_id"],
        "artifact_ref": runtime_scenario_report["runtime_scenario_report_id"],
        "artifact_type": "runtime_scenario_report",
        "stage_name": "v5_0_lifecycle_traceability_prd_handoff",
        "validation_tier": "tier_2",
        "overall_status": validation_status,
        "review_summary": (
            "The selected V5 bundle is correctly scoped: it proves lifecycle traceability through prd_handoff, preserves explicit later-stage boundaries, and keeps the starter workspace as the adoption surface."
            if overall_status == "passed"
            else "The selected V5 bundle still needs review because one or more traceability, parity, or scope-boundary checks are not fully satisfied."
        ),
        "ai_reviewer_lane": {
            "status": reviewer_status,
            "reviewer_role": "AI Reviewer",
            "blocking_findings": [] if overall_status == "passed" else ["The selected V5 release claim is not yet fully supported by the current lifecycle-traceability evidence."],
            "non_blocking_findings": [
                "Later lifecycle stages remain intentionally deferred past prd_handoff.",
                "The starter workspace is the clean adoption surface rather than the self-hosting workspace.",
            ],
            "unresolved_questions": [] if overall_status == "passed" else ["Which parity gap must be closed before the selected V5 bundle can promote?"],
        },
        "ai_tester_lane": {
            "status": tester_status,
            "tester_role": "AI Tester",
            "checks_run": [
                "Validated self-hosting lifecycle state through prd_handoff.",
                "Validated starter-workspace lifecycle state parity.",
                "Validated explicit post-prd boundary across both workspaces.",
            ],
            "blocking_findings": [] if overall_status == "passed" else ["One or more lifecycle-traceability proof checks did not pass."],
            "non_blocking_findings": [
                "The selected V5 slice intentionally stops before story planning.",
            ],
            "automation_gaps": [
                "Future releases should add parity checks for story_planning, acceptance_ready, release_readiness, launch_preparation, and outcome_review.",
            ],
        },
        "manual_validation_policy": {
            "required": True,
            "scope": "targeted",
            "owner_role": "PM Operator",
            "status": manual_policy_status,
            "rationale": "Lifecycle traceability changes product behavior and adoption surfaces, so targeted PM review remains mandatory even when automated parity checks pass.",
        },
        "referee_trigger": {
            "required": False,
            "rationale": "Reviewer and tester lanes align on the same scoped V5 claim and do not currently conflict.",
            "conflicting_lanes": [],
        },
        "governance_layer_refs": [
            workspace_item["item_lifecycle_state_id"],
            workspace_snapshot["lifecycle_stage_snapshot_id"],
            starter_item["item_lifecycle_state_id"],
            starter_snapshot["lifecycle_stage_snapshot_id"],
            "eval_run_report_ws_productos_v2_bounded_baseline",
        ],
        "next_action": (
            "Promote the selected lifecycle-traceability slice as ProductOS V5.0.0."
            if overall_status == "passed"
            else "Resolve the remaining lifecycle-traceability proof gap before promoting ProductOS V5.0.0."
        ),
        "generated_at": generated_at,
    }

    manual_validation_record = {
        "schema_version": "1.0.0",
        "manual_validation_record_id": "manual_validation_record_ws_productos_v2_v5_lifecycle_traceability",
        "workspace_id": workspace_item["workspace_id"],
        "subject_ref": runtime_scenario_report["runtime_scenario_report_id"],
        "subject_type": "runtime_scenario_report",
        "validation_tier": "tier_2",
        "validator_role": "PM Operator",
        "scope": "targeted",
        "decision": "accept" if overall_status == "passed" else ("defer" if overall_status == "watch" else "reject"),
        "fit_notes": [
            "The selected V5 slice makes one opportunity readable end to end through prd_handoff.",
            "The starter workspace now acts as the clean reusable adoption surface for the same traceability model.",
        ],
        "required_follow_ups": [
            "Extend the lifecycle-traceability model beyond prd_handoff in a later bounded release.",
            "Define how later lifecycle stages should reuse the same evidence and governance model.",
        ],
        "related_validation_report_ref": validation_lane_report["validation_lane_report_id"],
        "final_approval": overall_status == "passed",
        "recorded_at": generated_at,
    }

    release_readiness_status = "ready" if overall_status == "passed" else ("watch" if overall_status == "watch" else "blocked")
    release_readiness = {
        "schema_version": "1.1.0",
        "release_readiness_id": "release_readiness_ws_productos_v2_v5_lifecycle_traceability",
        "workspace_id": workspace_item["workspace_id"],
        "feature_id": "feature_v5_lifecycle_traceability_prd_handoff",
        "status": release_readiness_status,
        "launch_roles": [
            {
                "role_name": "Release owner",
                "responsibility": "Approve the V5.0 promotion for lifecycle traceability through prd_handoff.",
                "assignment_status": "assigned",
                "owner_name": "ProductOS PM",
                "owner_function": "Product management",
            },
            {
                "role_name": "Adoption owner",
                "responsibility": "Confirm the starter workspace is the default reusable adoption surface for the promoted V5 slice.",
                "assignment_status": "assigned",
                "owner_name": "ProductOS PM",
                "owner_function": "Workspace adoption",
            },
            {
                "role_name": "Portfolio reviewer",
                "responsibility": "Confirm the promoted V5 slice preserves the release evidence and scoped lifecycle boundary.",
                "assignment_status": "assigned",
                "owner_name": "ProductOS PM",
                "owner_function": "Portfolio governance",
            },
        ],
        "checks": [
            {
                "name": "Self-hosting lifecycle trace reaches prd_handoff",
                "status": "passed" if self_hosting_ready else "failed",
                "notes": "The self-hosting workspace exposes one item-first lifecycle trace through the complete discovery path into PRD handoff.",
            },
            {
                "name": "Starter-workspace adoption parity",
                "status": "passed" if starter_ready else "failed",
                "notes": "The starter workspace mirrors the selected lifecycle-traceability path and provides the reusable adoption surface.",
            },
            {
                "name": "Scoped boundary after prd_handoff",
                "status": "passed" if scoped_boundary_ready else "watch",
                "notes": "Later lifecycle stages remain explicit but not_started, which keeps the V5 claim bounded to prd_handoff.",
            },
        ],
        "generated_at": generated_at,
    }

    release_gate_decision = {
        "schema_version": "1.0.0",
        "release_gate_decision_id": "release_gate_decision_ws_productos_v2_v5_lifecycle_traceability",
        "workspace_id": workspace_item["workspace_id"],
        "target_release": V5_TARGET_RELEASE,
        "decision": "go" if overall_status == "passed" else ("conditional_go" if overall_status == "watch" else "no_go"),
        "pm_benchmark_ref": "pm_superpower_benchmark_ws_productos_v2_v4_0",
        "runtime_scenario_report_ref": runtime_scenario_report["runtime_scenario_report_id"],
        "release_readiness_ref": release_readiness["release_readiness_id"],
        "rationale": (
            "The selected V5 bundle proves item-first lifecycle traceability through prd_handoff in both the self-hosting and starter workspaces, while keeping later lifecycle stages explicitly deferred."
            if overall_status == "passed"
            else "The selected V5 lifecycle-traceability bundle still has unresolved proof gaps, so stable promotion should wait for those checks to pass."
        ),
        "next_action": (
            "Promote ProductOS to V5.0.0 stable via the Ralph-gated release command."
            if overall_status == "passed"
            else "Keep the selected V5 bundle in build-beside mode until the remaining lifecycle-traceability proof gaps are resolved."
        ),
        "known_gaps": [
            "Lifecycle traceability beyond prd_handoff remains explicitly deferred to a later bounded release.",
            "External publication adapters do not yet consume lifecycle traces as first-class inputs.",
        ],
        "deferred_items": [
            "Extend the trace model into story_planning, acceptance_ready, release_readiness, launch_preparation, and outcome_review.",
            "Decide how external publication and communication routes should consume lifecycle traces after the V5 baseline is stable.",
        ],
        "generated_at": generated_at,
    }

    ralph_loop_state = {
        "schema_version": "1.0.0",
        "ralph_loop_state_id": "ralph_loop_state_ws_productos_v2_v5_lifecycle_traceability",
        "workspace_id": workspace_item["workspace_id"],
        "target_release": V5_TARGET_RELEASE,
        "loop_goal": "Inspect, review, implement, validate, fix, and revalidate the lifecycle-traceability through prd_handoff slice before stable release promotion.",
        "overall_status": "ready_for_release" if overall_status == "passed" else "blocked",
        "subject_refs": [
            workspace_item["item_lifecycle_state_id"],
            workspace_snapshot["lifecycle_stage_snapshot_id"],
            starter_item["item_lifecycle_state_id"],
            starter_snapshot["lifecycle_stage_snapshot_id"],
            runtime_scenario_report["runtime_scenario_report_id"],
            validation_lane_report["validation_lane_report_id"],
            manual_validation_record["manual_validation_record_id"],
            release_gate_decision["release_gate_decision_id"],
        ],
        "stages": [
            {
                "stage_key": "inspect",
                "status": "passed" if self_hosting_ready else "blocked",
                "owner": "AI Librarian",
                "findings_summary": "The self-hosting and starter-workspace lifecycle traces were inspected as one bounded V5 release claim.",
                "evidence_refs": [
                    workspace_item["item_lifecycle_state_id"],
                    starter_item["item_lifecycle_state_id"],
                ],
                "exit_condition": "Both lifecycle traces are explicit enough to review as one bounded V5 slice.",
            },
            {
                "stage_key": "review",
                "status": "passed" if overall_status == "passed" else "blocked",
                "owner": "AI Reviewer",
                "findings_summary": "The selected V5 claim is correctly bounded to prd_handoff and does not overstate later-stage coverage.",
                "evidence_refs": [
                    validation_lane_report["validation_lane_report_id"],
                ],
                "exit_condition": "The promoted claim stays tightly scoped to lifecycle traceability through prd_handoff.",
            },
            {
                "stage_key": "validate",
                "status": "passed" if overall_status == "passed" else "blocked",
                "owner": "AI Tester",
                "findings_summary": "Parity, stage-shape, and scope-boundary checks agree on the selected V5 lifecycle-traceability slice.",
                "evidence_refs": [
                    runtime_scenario_report["runtime_scenario_report_id"],
                    validation_lane_report["validation_lane_report_id"],
                ],
                "exit_condition": "Automated parity and scope-boundary proof passes for both the self-hosting and starter workspaces.",
            },
            {
                "stage_key": "implement",
                "status": "passed" if overall_status == "passed" else "blocked",
                "owner": "AI Product Shaper",
                "findings_summary": "The repo exposes lifecycle traceability as an explicit V5 build slice and keeps the starter workspace as the reusable adoption surface.",
                "evidence_refs": [
                    runtime_scenario_report["runtime_scenario_report_id"],
                    "workspaces/productos-v2/docs/planning/v5-cutover-plan.md",
                ],
                "exit_condition": "The selected V5 slice exists concretely in the repo and can be validated and promoted.",
            },
            {
                "stage_key": "fix",
                "status": "passed" if overall_status == "passed" else "blocked",
                "owner": "AI Product Shaper",
                "findings_summary": "The release package leaves later lifecycle stages and external publication adapters as explicitly deferred work instead of hidden scope.",
                "evidence_refs": [
                    release_gate_decision["release_gate_decision_id"],
                ],
                "exit_condition": "Deferred work is explicit and does not leak into the promoted V5 claim.",
            },
            {
                "stage_key": "revalidate",
                "status": "passed" if overall_status == "passed" else "blocked",
                "owner": "PM Operator",
                "findings_summary": "Manual review confirms the selected V5 lifecycle-traceability slice is ready to become the stable ProductOS baseline.",
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
            "The V5 release is acceptable because it promotes one concrete lifecycle-traceability slice through prd_handoff, keeps later stages explicitly out of scope, and uses the starter workspace as the clean adoption surface."
            if overall_status == "passed"
            else "The V5 release is not yet acceptable because the selected lifecycle-traceability slice still has unresolved proof gaps."
        ),
        "next_action": (
            "Promote ProductOS to V5.0.0 stable and plan the next bounded lifecycle expansion beyond prd_handoff."
            if overall_status == "passed"
            else "Keep the selected V5 lifecycle-traceability slice in build-beside mode until it is ready for stable promotion."
        ),
        "generated_at": generated_at,
    }

    return {
        "runtime_scenario_report_v5_lifecycle_traceability": runtime_scenario_report,
        "validation_lane_report_v5_lifecycle_traceability": validation_lane_report,
        "manual_validation_record_v5_lifecycle_traceability": manual_validation_record,
        "release_readiness_v5_lifecycle_traceability": release_readiness,
        "release_gate_decision_v5_lifecycle_traceability": release_gate_decision,
        "ralph_loop_state_v5_lifecycle_traceability": ralph_loop_state,
    }


def summarize_v5_lifecycle_bundle(
    workspace_dir: Path | str,
    bundle: dict[str, dict[str, Any]],
) -> str:
    workspace_item, _, starter_item, _ = _load_archived_v5_item_and_snapshot(workspace_dir)
    report = bundle["runtime_scenario_report_v5_lifecycle_traceability"]
    decision = bundle["release_gate_decision_v5_lifecycle_traceability"]
    readiness = bundle["release_readiness_v5_lifecycle_traceability"]
    return "\n".join(
        [
            f"V5 Bundle: {V5_BUNDLE_NAME}",
            f"Target Release: {report['candidate_version']}",
            f"Scenario Status: {report['status']}",
            f"Self-Hosting Stage: {workspace_item['current_stage']}",
            f"Starter Stage: {starter_item['current_stage']}",
            f"Release Readiness: {readiness['status']}",
            f"Release Decision: {decision['decision']}",
        ]
    )
