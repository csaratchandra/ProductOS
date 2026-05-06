from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .lifecycle import (
    LIFECYCLE_STAGE_ORDER,
    load_item_lifecycle_state_from_workspace,
    load_lifecycle_stage_snapshot_from_workspace,
)


V6_BASELINE_VERSION = "5.0.0"
V6_TARGET_VERSION = "6.0.0"
V6_TARGET_RELEASE = "v6_0_0"
V6_BUNDLE_ID = "v6_lifecycle_traceability_release_readiness"
V6_BUNDLE_NAME = "Lifecycle traceability through release readiness"
V6_DELIVERY_STAGE_ORDER = [
    "story_planning",
    "acceptance_ready",
    "release_readiness",
]
V6_DEFERRED_STAGE_ORDER = [
    "launch_preparation",
    "outcome_review",
]

V6_ARTIFACT_SCHEMAS = {
    "runtime_scenario_report_v6_lifecycle_traceability": "runtime_scenario_report.schema.json",
    "validation_lane_report_v6_lifecycle_traceability": "validation_lane_report.schema.json",
    "manual_validation_record_v6_lifecycle_traceability": "manual_validation_record.schema.json",
    "release_readiness_v6_lifecycle_traceability": "release_readiness.schema.json",
    "release_gate_decision_v6_lifecycle_traceability": "release_gate_decision.schema.json",
    "ralph_loop_state_v6_lifecycle_traceability": "ralph_loop_state.schema.json",
}


def _root_dir_from_workspace(workspace_dir: Path | str) -> Path:
    return Path(__file__).resolve().parents[3]


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_archived_v6_surfaces(
    workspace_dir: Path | str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    root_dir = _root_dir_from_workspace(workspace_dir)
    archive_dir = root_dir / "tests" / "fixtures" / "workspaces" / "productos-sample" / "archive" / "historical-artifacts" / "v6_lifecycle_traceability"
    if archive_dir.exists():
        return (
            _load_json(archive_dir / "internal" / "item_lifecycle_state_pm_lifecycle_visibility.example.json"),
            _load_json(archive_dir / "internal" / "lifecycle_stage_snapshot_delivery.example.json"),
            _load_json(archive_dir / "internal" / "lifecycle_stage_snapshot_full_lifecycle.example.json"),
            _load_json(archive_dir / "starter" / "item_lifecycle_state.json"),
            _load_json(archive_dir / "starter" / "lifecycle_stage_snapshot_delivery.json"),
            _load_json(archive_dir / "starter" / "lifecycle_stage_snapshot_full_lifecycle.json"),
        )

    workspace_path = Path(workspace_dir).resolve()
    starter_dir = root_dir / "templates"
    return (
        load_item_lifecycle_state_from_workspace(
            workspace_path,
            item_id="opp_pm_lifecycle_traceability",
        ),
        load_lifecycle_stage_snapshot_from_workspace(
            workspace_path,
            focus_area="delivery",
        ),
        load_lifecycle_stage_snapshot_from_workspace(
            workspace_path,
            focus_area="full_lifecycle",
        ),
        load_item_lifecycle_state_from_workspace(starter_dir),
        load_lifecycle_stage_snapshot_from_workspace(
            starter_dir,
            focus_area="delivery",
        ),
        load_lifecycle_stage_snapshot_from_workspace(
            starter_dir,
            focus_area="full_lifecycle",
        ),
    )


def _completed_stage_count(item_state: dict[str, Any], stage_order: list[str]) -> int:
    stage_status = {
        stage["stage_key"]: stage["status"]
        for stage in item_state["lifecycle_stages"]
        if stage["stage_key"] in stage_order
    }
    return sum(1 for stage_key in stage_order if stage_status.get(stage_key) == "completed")


def _explicit_deferred_stage_count(item_state: dict[str, Any]) -> int:
    stage_status = {
        stage["stage_key"]: stage["status"]
        for stage in item_state["lifecycle_stages"]
        if stage["stage_key"] in V6_DEFERRED_STAGE_ORDER
    }
    return sum(1 for stage_key in V6_DEFERRED_STAGE_ORDER if stage_status.get(stage_key) == "not_started")


def _has_expected_stage_shape(item_state: dict[str, Any]) -> bool:
    return [stage["stage_key"] for stage in item_state["lifecycle_stages"]] == LIFECYCLE_STAGE_ORDER


def _snapshot_gate_passed_count(snapshot: dict[str, Any], expected_stage_count: int) -> bool:
    return snapshot["gate_counts"]["passed"] == expected_stage_count


def _all_required_focus_areas_exist(workspace_dir: Path) -> bool:
    for focus_area in ("discovery", "delivery", "launch", "outcomes", "full_lifecycle"):
        try:
            load_lifecycle_stage_snapshot_from_workspace(workspace_dir, focus_area=focus_area)
        except KeyError:
            return False
    return True


def build_v6_lifecycle_bundle_from_workspace(
    workspace_dir: Path | str,
    *,
    generated_at: str,
    target_version: str = V6_TARGET_VERSION,
) -> dict[str, dict[str, Any]]:
    workspace_dir = Path(workspace_dir).resolve()
    root_dir = _root_dir_from_workspace(workspace_dir)
    starter_dir = root_dir / "templates"
    (
        workspace_item,
        workspace_delivery_snapshot,
        workspace_full_snapshot,
        starter_item,
        starter_delivery_snapshot,
        starter_full_snapshot,
    ) = _load_archived_v6_surfaces(workspace_dir)

    workspace_delivery_count = _completed_stage_count(workspace_item, V6_DELIVERY_STAGE_ORDER)
    starter_delivery_count = _completed_stage_count(starter_item, V6_DELIVERY_STAGE_ORDER)
    workspace_deferred_count = _explicit_deferred_stage_count(workspace_item)
    starter_deferred_count = _explicit_deferred_stage_count(starter_item)

    self_hosting_ready = (
        workspace_item["current_stage"] == "release_readiness"
        and workspace_item["overall_status"] == "completed"
        and workspace_delivery_count == len(V6_DELIVERY_STAGE_ORDER)
        and _has_expected_stage_shape(workspace_item)
        and _snapshot_gate_passed_count(workspace_delivery_snapshot, len(V6_DELIVERY_STAGE_ORDER))
        and workspace_full_snapshot["gate_counts"]["passed"] == len(LIFECYCLE_STAGE_ORDER) - len(V6_DEFERRED_STAGE_ORDER)
    )
    starter_ready = (
        starter_item["current_stage"] == "release_readiness"
        and starter_item["overall_status"] == "completed"
        and starter_delivery_count == len(V6_DELIVERY_STAGE_ORDER)
        and _has_expected_stage_shape(starter_item)
        and _snapshot_gate_passed_count(starter_delivery_snapshot, len(V6_DELIVERY_STAGE_ORDER))
        and starter_full_snapshot["gate_counts"]["passed"] == len(LIFECYCLE_STAGE_ORDER) - len(V6_DEFERRED_STAGE_ORDER)
    )
    focus_area_coverage_ready = _all_required_focus_areas_exist(workspace_dir) and _all_required_focus_areas_exist(starter_dir)
    scoped_boundary_ready = (
        workspace_deferred_count == len(V6_DEFERRED_STAGE_ORDER)
        and starter_deferred_count == len(V6_DEFERRED_STAGE_ORDER)
    )

    scenario_statuses = [
        self_hosting_ready,
        starter_ready,
        focus_area_coverage_ready,
        scoped_boundary_ready,
    ]
    overall_status = "passed" if all(scenario_statuses) else ("watch" if any(scenario_statuses) else "failed")

    runtime_scenario_report = {
        "schema_version": "1.0.0",
        "runtime_scenario_report_id": "runtime_scenario_report_ws_productos_v2_v6_lifecycle_traceability",
        "workspace_id": workspace_item["workspace_id"],
        "baseline_version": V6_BASELINE_VERSION,
        "candidate_version": target_version,
        "status": overall_status,
        "summary": (
            "The selected V6 bundle proves item-first lifecycle traceability through release_readiness in the reference and starter workspaces, fixes the advertised trace focus-area coverage, and keeps launch and outcome stages explicitly deferred."
            if overall_status == "passed"
            else "The selected V6 lifecycle-traceability bundle is partially proven, but one or more release-readiness, parity, trace-surface, or scope-boundary checks still need review."
        ),
        "scenarios": [
            {
                "scenario_id": "scenario_self_hosting_traceability_to_release_readiness",
                "name": "Self-hosting lifecycle traceability through release readiness",
                "status": "passed" if self_hosting_ready else "failed",
                "metric_deltas": [
                    {
                        "metric_name": "completed_delivery_stage_count",
                        "baseline_value": 0,
                        "candidate_value": workspace_delivery_count,
                        "unit": "count",
                        "trend": "improved" if workspace_delivery_count else "flat",
                    }
                ],
                "evidence_refs": [
                    workspace_item["item_lifecycle_state_id"],
                    workspace_delivery_snapshot["lifecycle_stage_snapshot_id"],
                    "templates/docs/delivery/release-readiness-review.md",
                ],
                "gaps": [] if self_hosting_ready else ["Self-hosting lifecycle evidence does not yet cleanly reach release_readiness."],
            },
            {
                "scenario_id": "scenario_starter_workspace_traceability_to_release_readiness",
                "name": "Starter-workspace parity through release readiness",
                "status": "passed" if starter_ready else "failed",
                "metric_deltas": [
                    {
                        "metric_name": "starter_completed_delivery_stage_count",
                        "baseline_value": 0,
                        "candidate_value": starter_delivery_count,
                        "unit": "count",
                        "trend": "improved" if starter_delivery_count else "flat",
                    }
                ],
                "evidence_refs": [
                    starter_item["item_lifecycle_state_id"],
                    starter_delivery_snapshot["lifecycle_stage_snapshot_id"],
                    "templates/docs/delivery/release-readiness-review.md",
                ],
                "gaps": [] if starter_ready else ["The starter workspace does not yet mirror the selected release-readiness trace strongly enough."],
            },
            {
                "scenario_id": "scenario_trace_focus_area_coverage",
                "name": "Trace focus-area coverage matches the CLI contract",
                "status": "passed" if focus_area_coverage_ready else "failed",
                "metric_deltas": [
                    {
                        "metric_name": "available_trace_focus_area_count",
                        "baseline_value": 1,
                        "candidate_value": 5 if focus_area_coverage_ready else 0,
                        "unit": "count",
                        "trend": "improved" if focus_area_coverage_ready else "flat",
                    }
                ],
                "evidence_refs": [
                    workspace_full_snapshot["lifecycle_stage_snapshot_id"],
                    starter_full_snapshot["lifecycle_stage_snapshot_id"],
                    "README.md",
                ],
                "gaps": [] if focus_area_coverage_ready else ["The advertised trace focus areas are still not all backed by workspace snapshots."],
            },
            {
                "scenario_id": "scenario_scoped_boundary_after_release_readiness",
                "name": "Scoped boundary after release readiness remains explicit",
                "status": "passed" if scoped_boundary_ready else "watch",
                "metric_deltas": [
                    {
                        "metric_name": "explicit_post_release_readiness_stage_count",
                        "baseline_value": 0,
                        "candidate_value": min(workspace_deferred_count, starter_deferred_count),
                        "unit": "count",
                        "trend": "improved" if min(workspace_deferred_count, starter_deferred_count) else "flat",
                    }
                ],
                "evidence_refs": [
                    workspace_item["item_lifecycle_state_id"],
                    starter_item["item_lifecycle_state_id"],
                    "templates/README.md",
                ],
                "gaps": [] if scoped_boundary_ready else ["Launch and outcome stages are not yet kept explicit as not_started across both adoption surfaces."],
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
        "validation_lane_report_id": "validation_lane_report_ws_productos_v2_v6_lifecycle_traceability",
        "workspace_id": workspace_item["workspace_id"],
        "artifact_ref": runtime_scenario_report["runtime_scenario_report_id"],
        "artifact_type": "runtime_scenario_report",
        "stage_name": "v6_0_lifecycle_traceability_release_readiness",
        "validation_tier": "tier_2",
        "overall_status": validation_status,
        "review_summary": (
            "The selected V6 bundle is correctly scoped: it proves lifecycle traceability through release_readiness, closes the trace focus-area contract gap, preserves starter-workspace parity, and keeps launch and outcome stages explicitly deferred."
            if overall_status == "passed"
            else "The selected V6 bundle still needs review because one or more release-readiness, parity, focus-area, or deferred-boundary checks are not fully satisfied."
        ),
        "ai_reviewer_lane": {
            "status": reviewer_status,
            "reviewer_role": "AI Reviewer",
            "blocking_findings": [] if overall_status == "passed" else ["The selected V6 release claim is not yet fully supported by the current release-readiness lifecycle evidence."],
            "non_blocking_findings": [
                "Launch preparation remains intentionally deferred past release_readiness.",
                "Outcome review remains intentionally deferred until after the shipped slice exists.",
            ],
            "unresolved_questions": [] if overall_status == "passed" else ["Which parity or trace-surface gap must be closed before the selected V6 bundle can promote?"],
        },
        "ai_tester_lane": {
            "status": tester_status,
            "tester_role": "AI Tester",
            "checks_run": [
                "Validated reference-workspace lifecycle state through release_readiness.",
                "Validated starter-workspace lifecycle state parity through release_readiness.",
                "Validated discovery, delivery, launch, outcomes, and full_lifecycle snapshot coverage.",
                "Validated explicit post-release_readiness boundary across both workspaces.",
            ],
            "blocking_findings": [] if overall_status == "passed" else ["One or more release-readiness lifecycle proof checks did not pass."],
            "non_blocking_findings": [
                "The selected V6 slice intentionally stops before launch_preparation and outcome_review.",
            ],
            "automation_gaps": [
                "Future releases should add parity checks for launch_preparation completion and post-release outcome review linkage.",
            ],
        },
        "manual_validation_policy": {
            "required": True,
            "scope": "targeted",
            "owner_role": "PM Operator",
            "status": manual_policy_status,
            "rationale": "Lifecycle traceability through release readiness changes product behavior, control-surface claims, and starter adoption surfaces, so targeted PM review remains mandatory even when automated proof passes.",
        },
        "referee_trigger": {
            "required": False,
            "rationale": "Reviewer and tester lanes align on the same scoped V6 claim and do not currently conflict.",
            "conflicting_lanes": [],
        },
        "governance_layer_refs": [
            workspace_item["item_lifecycle_state_id"],
            workspace_delivery_snapshot["lifecycle_stage_snapshot_id"],
            workspace_full_snapshot["lifecycle_stage_snapshot_id"],
            starter_item["item_lifecycle_state_id"],
            starter_delivery_snapshot["lifecycle_stage_snapshot_id"],
            starter_full_snapshot["lifecycle_stage_snapshot_id"],
            "release_readiness_ws_productos_v2_v5_lifecycle_traceability",
        ],
        "next_action": (
            "Promote the selected lifecycle-traceability slice as ProductOS V6.0.0."
            if overall_status == "passed"
            else "Resolve the remaining lifecycle-traceability proof gap before promoting ProductOS V6.0.0."
        ),
        "generated_at": generated_at,
    }

    manual_validation_record = {
        "schema_version": "1.0.0",
        "manual_validation_record_id": "manual_validation_record_ws_productos_v2_v6_lifecycle_traceability",
        "workspace_id": workspace_item["workspace_id"],
        "subject_ref": runtime_scenario_report["runtime_scenario_report_id"],
        "subject_type": "runtime_scenario_report",
        "validation_tier": "tier_2",
        "validator_role": "PM Operator",
        "scope": "targeted",
        "decision": "accept" if overall_status == "passed" else ("defer" if overall_status == "watch" else "reject"),
        "fit_notes": [
            "The selected V6 slice keeps one opportunity readable from intake through release_readiness without reopening hidden side channels.",
            "The trace command now has concrete coverage for all advertised lifecycle focus areas.",
        ],
        "required_follow_ups": [
            "Extend the lifecycle-traceability model into launch_preparation and outcome_review in a later bounded release.",
            "Decide how external publication and communication routes should consume launch and outcome lifecycle traces.",
        ],
        "related_validation_report_ref": validation_lane_report["validation_lane_report_id"],
        "final_approval": overall_status == "passed",
        "recorded_at": generated_at,
    }

    release_readiness_status = "ready" if overall_status == "passed" else ("watch" if overall_status == "watch" else "blocked")
    release_gate_decision_id = "release_gate_decision_ws_productos_v2_v6_lifecycle_traceability"
    release_readiness = {
        "schema_version": "1.2.0",
        "release_readiness_id": "release_readiness_ws_productos_v2_v6_lifecycle_traceability",
        "workspace_id": workspace_item["workspace_id"],
        "feature_id": "feature_v6_lifecycle_traceability_release_readiness",
        "status": release_readiness_status,
        "decision_summary": "The V6 slice is ready when reference and starter traces both reach release_readiness and the post-release boundary remains explicit.",
        "launch_roles": [
            {
                "role_name": "Release owner",
                "responsibility": "Approve the V6.0 promotion for lifecycle traceability through release_readiness.",
                "assignment_status": "assigned",
                "owner_name": "ProductOS PM",
                "owner_function": "Product management",
            },
            {
                "role_name": "Adoption owner",
                "responsibility": "Confirm the starter workspace remains the reusable adoption surface for the promoted V6 slice.",
                "assignment_status": "assigned",
                "owner_name": "ProductOS PM",
                "owner_function": "Workspace adoption",
            },
            {
                "role_name": "Control-surface reviewer",
                "responsibility": "Confirm the trace command and workspace snapshots agree on delivery, launch, outcome, and full-lifecycle coverage.",
                "assignment_status": "assigned",
                "owner_name": "ProductOS PM",
                "owner_function": "Runtime governance",
            },
        ],
        "claim_readiness": [
            {
                "claim": "The V6 bundle proves lifecycle traceability through release_readiness in both adoption surfaces.",
                "status": "verified" if self_hosting_ready and starter_ready else "blocked",
                "evidence_refs": [runtime_scenario_report["runtime_scenario_report_id"], manual_validation_record["manual_validation_record_id"]],
            },
            {
                "claim": "Launch preparation and outcome review remain explicit but out of scope for the promoted V6 claim.",
                "status": "bounded",
                "evidence_refs": [release_gate_decision_id],
            },
        ],
        "blocking_evidence_refs": [runtime_scenario_report["runtime_scenario_report_id"]],
        "checks": [
            {
                "name": "Self-hosting lifecycle trace reaches release_readiness",
                "status": "passed" if self_hosting_ready else "failed",
                "notes": "The reference workspace exposes one item-first lifecycle trace from discovery through delivery planning and release_readiness.",
            },
            {
                "name": "Starter-workspace adoption parity through release_readiness",
                "status": "passed" if starter_ready else "failed",
                "notes": "The starter workspace mirrors the selected lifecycle-traceability path through release_readiness.",
            },
            {
                "name": "Trace focus-area coverage",
                "status": "passed" if focus_area_coverage_ready else "failed",
                "notes": "All advertised trace focus areas now have concrete workspace snapshots behind the CLI surface.",
            },
            {
                "name": "Scoped boundary after release_readiness",
                "status": "passed" if scoped_boundary_ready else "watch",
                "notes": "Launch preparation and outcome review remain explicit but not_started, which keeps the V6 claim bounded to release_readiness.",
            },
        ],
        "generated_at": generated_at,
    }

    release_gate_decision = {
        "schema_version": "1.0.0",
        "release_gate_decision_id": release_gate_decision_id,
        "workspace_id": workspace_item["workspace_id"],
        "target_release": V6_TARGET_RELEASE,
        "decision": "go" if overall_status == "passed" else ("conditional_go" if overall_status == "watch" else "no_go"),
        "pm_benchmark_ref": "pm_superpower_benchmark_ws_productos_v2_v4_0",
        "runtime_scenario_report_ref": runtime_scenario_report["runtime_scenario_report_id"],
        "release_readiness_ref": release_readiness["release_readiness_id"],
        "rationale": (
            "The selected V6 bundle proves item-first lifecycle traceability through release_readiness in both the reference and starter workspaces, closes the trace focus-area control-surface gap, and keeps later launch and outcome work explicitly deferred."
            if overall_status == "passed"
            else "The selected V6 lifecycle-traceability bundle still has unresolved proof gaps, so stable promotion should wait for those checks to pass."
        ),
        "next_action": (
            "Promote ProductOS to V6.0.0 stable via the Ralph-gated release command."
            if overall_status == "passed"
            else "Keep the selected V6 bundle in build-beside mode until the remaining lifecycle-traceability proof gaps are resolved."
        ),
        "known_gaps": [
            "Lifecycle traceability beyond release_readiness remains explicitly deferred to a later bounded release.",
            "External publication adapters do not yet consume launch or outcome lifecycle traces as first-class inputs.",
        ],
        "deferred_items": [
            "Extend the trace model into launch_preparation and outcome_review.",
            "Decide how external publication and communication routes should consume lifecycle traces after the V6 baseline is stable.",
        ],
        "generated_at": generated_at,
    }

    ralph_loop_state = {
        "schema_version": "1.0.0",
        "ralph_loop_state_id": "ralph_loop_state_ws_productos_v2_v6_lifecycle_traceability",
        "workspace_id": workspace_item["workspace_id"],
        "target_release": V6_TARGET_RELEASE,
        "loop_goal": "Inspect, review, implement, validate, fix, and revalidate the lifecycle-traceability through release_readiness slice before stable release promotion.",
        "overall_status": "ready_for_release" if overall_status == "passed" else "blocked",
        "subject_refs": [
            workspace_item["item_lifecycle_state_id"],
            workspace_delivery_snapshot["lifecycle_stage_snapshot_id"],
            workspace_full_snapshot["lifecycle_stage_snapshot_id"],
            starter_item["item_lifecycle_state_id"],
            starter_delivery_snapshot["lifecycle_stage_snapshot_id"],
            starter_full_snapshot["lifecycle_stage_snapshot_id"],
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
                "findings_summary": "The reference and starter-workspace lifecycle traces were inspected as one bounded V6 release claim through release_readiness.",
                "evidence_refs": [
                    workspace_item["item_lifecycle_state_id"],
                    starter_item["item_lifecycle_state_id"],
                ],
                "exit_condition": "Both lifecycle traces are explicit enough to review as one bounded V6 slice.",
            },
            {
                "stage_key": "review",
                "status": "passed" if overall_status == "passed" else "blocked",
                "owner": "AI Reviewer",
                "findings_summary": "The selected V6 claim is correctly bounded to release_readiness and does not overstate launch or outcome coverage.",
                "evidence_refs": [
                    validation_lane_report["validation_lane_report_id"],
                ],
                "exit_condition": "The promoted claim stays tightly scoped to lifecycle traceability through release_readiness.",
            },
            {
                "stage_key": "validate",
                "status": "passed" if overall_status == "passed" else "blocked",
                "owner": "AI Tester",
                "findings_summary": "Parity, focus-area coverage, stage-shape, and scope-boundary checks agree on the selected V6 lifecycle-traceability slice.",
                "evidence_refs": [
                    runtime_scenario_report["runtime_scenario_report_id"],
                    validation_lane_report["validation_lane_report_id"],
                ],
                "exit_condition": "Automated parity, focus-area, and scope-boundary proof passes for both the reference and starter workspaces.",
            },
            {
                "stage_key": "implement",
                "status": "passed" if overall_status == "passed" else "blocked",
                "owner": "AI Product Shaper",
                "findings_summary": "The repo exposes lifecycle traceability through release_readiness as an explicit V6 build slice and closes the trace command contract gap.",
                "evidence_refs": [
                    runtime_scenario_report["runtime_scenario_report_id"],
                    "README.md",
                ],
                "exit_condition": "The selected V6 slice exists concretely in the repo and can be validated and promoted.",
            },
            {
                "stage_key": "fix",
                "status": "passed" if overall_status == "passed" else "blocked",
                "owner": "AI Product Shaper",
                "findings_summary": "The release package leaves launch, outcomes, and external publication adapters as explicit deferred work instead of hidden scope.",
                "evidence_refs": [
                    release_gate_decision["release_gate_decision_id"],
                ],
                "exit_condition": "Deferred work is explicit and does not leak into the promoted V6 claim.",
            },
            {
                "stage_key": "revalidate",
                "status": "passed" if overall_status == "passed" else "blocked",
                "owner": "PM Operator",
                "findings_summary": "Manual review confirms the selected V6 lifecycle-traceability slice is ready to become the stable ProductOS baseline.",
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
            "The V6 release is acceptable because it promotes one concrete lifecycle-traceability slice through release_readiness, fixes the trace focus-area contract gap, keeps launch and outcome stages explicitly out of scope, and uses the starter workspace as the clean adoption surface."
            if overall_status == "passed"
            else "The V6 release is not yet acceptable because the selected lifecycle-traceability slice still has unresolved proof gaps."
        ),
        "next_action": (
            "Promote ProductOS to V6.0.0 stable and plan the next bounded lifecycle expansion beyond release_readiness."
            if overall_status == "passed"
            else "Keep the selected V6 lifecycle-traceability slice in build-beside mode until it is ready for stable promotion."
        ),
        "generated_at": generated_at,
    }

    return {
        "runtime_scenario_report_v6_lifecycle_traceability": runtime_scenario_report,
        "validation_lane_report_v6_lifecycle_traceability": validation_lane_report,
        "manual_validation_record_v6_lifecycle_traceability": manual_validation_record,
        "release_readiness_v6_lifecycle_traceability": release_readiness,
        "release_gate_decision_v6_lifecycle_traceability": release_gate_decision,
        "ralph_loop_state_v6_lifecycle_traceability": ralph_loop_state,
    }


def summarize_v6_lifecycle_bundle(
    workspace_dir: Path | str,
    bundle: dict[str, dict[str, Any]],
) -> str:
    workspace_item, _, _, starter_item, _, _ = _load_archived_v6_surfaces(workspace_dir)
    report = bundle["runtime_scenario_report_v6_lifecycle_traceability"]
    decision = bundle["release_gate_decision_v6_lifecycle_traceability"]
    readiness = bundle["release_readiness_v6_lifecycle_traceability"]
    return "\n".join(
        [
            f"V6 Bundle: {V6_BUNDLE_NAME}",
            f"Target Release: {report['candidate_version']}",
            f"Scenario Status: {report['status']}",
            f"Reference Stage: {workspace_item['current_stage']}",
            f"Starter Stage: {starter_item['current_stage']}",
            f"Release Readiness: {readiness['status']}",
            f"Release Decision: {decision['decision']}",
        ]
    )
