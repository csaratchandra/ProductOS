from __future__ import annotations

from pathlib import Path
from typing import Any

from .next_version import build_next_version_bundle_from_workspace
from .release import categorize_promotion_blockers, evaluate_promotion_gate, latest_release_metadata, parse_semver
from .v6 import build_v6_lifecycle_bundle_from_workspace
from .v7 import build_v7_lifecycle_bundle_from_workspace
from .v9 import build_v9_lifecycle_bundle_from_workspace, inspect_v9_lifecycle_enrichment_state


SELECTED_V5_BUNDLE_ID = "v5_lifecycle_traceability_prd_handoff"
SELECTED_V5_BUNDLE_NAME = "Lifecycle traceability through PRD handoff"
SELECTED_V5_BUNDLE_SCOPE = [
    "Ship item-first lifecycle traceability from signal intake through prd_handoff.",
    "Keep later lifecycle stages explicit but not_started until a later release extends them.",
    "Use the starter workspace as the clean reusable adoption surface for the same traceability model.",
]
SELECTED_V5_BUNDLE_EVIDENCE = [
    "templates/docs/discovery/discovery-review.md",
    "templates/README.md",
]
SELECTED_V6_BUNDLE_ID = "v6_lifecycle_traceability_release_readiness"
SELECTED_V6_BUNDLE_NAME = "Lifecycle traceability through release readiness"
SELECTED_V6_BUNDLE_SCOPE = [
    "Extend item-first lifecycle traceability from prd_handoff through story_planning, acceptance_ready, and release_readiness.",
    "Back every advertised trace focus area with concrete workspace snapshots across discovery, delivery, launch, outcomes, and full_lifecycle.",
    "Keep launch_preparation and outcome_review explicit but not_started until a later release extends them.",
    "Use the starter workspace as the clean reusable adoption surface for the same traceability model.",
]
SELECTED_V6_BUNDLE_EVIDENCE = [
    "templates/docs/delivery/release-readiness-review.md",
    "templates/docs/delivery/release-readiness-review.md",
    "README.md",
]
SELECTED_V7_BUNDLE_ID = "v7_lifecycle_traceability_launch_and_outcome"
SELECTED_V7_BUNDLE_NAME = "Lifecycle traceability through outcome review"
SELECTED_V7_BUNDLE_SCOPE = [
    "Extend item-first lifecycle traceability from release_readiness through launch_preparation and outcome_review.",
    "Attach release communication and post-release learning evidence to the same canonical item trace.",
    "Preserve discovery, delivery, launch, outcomes, and full_lifecycle snapshot parity across the self-hosting and starter workspaces.",
    "Keep external publication adapters and broader distribution packaging as later bounded releases.",
]
SELECTED_V7_BUNDLE_EVIDENCE = [
    "templates/docs/delivery/launch-outcome-review.md",
    "templates/docs/delivery/launch-outcome-review.md",
    "CHANGELOG.md",
]


def build_v5_cutover_plan_from_workspace(
    workspace_dir,
    *,
    generated_at: str,
    adapter_name: str = "codex",
    target_version: str = "5.0.0",
) -> dict[str, Any]:
    bundle = build_next_version_bundle_from_workspace(
        workspace_dir,
        generated_at=generated_at,
        adapter_name=adapter_name,
    )
    portfolio = bundle["feature_portfolio_review"]
    eval_report = bundle["eval_run_report"]
    gate = evaluate_promotion_gate(
        eval_run_report=eval_report,
        feature_portfolio_review=portfolio,
        research_brief=bundle.get("research_brief"),
        external_research_plan=bundle.get("external_research_plan"),
        external_research_source_discovery=bundle.get("external_research_source_discovery"),
        external_research_feed_registry=bundle.get("external_research_feed_registry"),
        selected_manifest=bundle.get("external_research_selected_manifest"),
        external_research_review=bundle.get("external_research_review"),
    )
    root_dir = Path(__file__).resolve().parents[3]
    latest_release = latest_release_metadata(root_dir)
    promoted = parse_semver(latest_release["core_version"]) >= parse_semver(target_version)
    blocked_feature_ids = [
        item["feature_id"]
        for item in portfolio["feature_summaries"]
        if item["overall_score"] < 5
    ]

    if gate["status"] == "blocked":
        selection_status = "deferred"
        current_stage = "hold_stable_extension_gate"
    elif promoted:
        selection_status = "stable_active"
        current_stage = "extend_lifecycle_beyond_prd_handoff"
    else:
        selection_status = "selected_for_promotion"
        current_stage = "promote_v5_stable"
    required_steps = (
        [
            "Harden runtime_control_surface so the CLI reports watch and blocked states as strongly as the underlying eval evidence requires.",
            "Make self_improvement_loop depend on frozen eval and decision-memory evidence before it can narrate promotion.",
            "Keep V5 lifecycle-traceability scope stable until the promotion gate is healthy.",
            "Resolve the remaining proof gaps before broadening the lifecycle claim beyond prd_handoff.",
        ]
        if gate["status"] == "blocked"
        else [
            "Keep ProductOS V5.0.0 as the canonical stable line while preserving the selected lifecycle-traceability release evidence.",
            "Extend lifecycle traceability beyond prd_handoff only as a later bounded release.",
            "Keep the starter workspace as the default reusable adoption surface for the current V5 slice.",
        ]
        if promoted
        else [
            "Promote the selected V5 lifecycle-traceability bundle as the stable ProductOS line.",
            "Update stable-release metadata and docs to reflect the promoted V5 slice.",
        ]
    )

    top_priority_feature_id = (
        "extend_lifecycle_beyond_prd_handoff"
        if promoted and gate["status"] != "blocked"
        else portfolio["top_priority_feature_id"]
    )
    blocker_categories = categorize_promotion_blockers(gate["blockers"])

    return {
        "target_version": target_version,
        "source_baseline_version": eval_report["candidate_version"],
        "current_stage": current_stage,
        "selection_status": selection_status,
        "promotion_gate_status": gate["status"],
        "stable_release_version": latest_release["core_version"],
        "top_priority_feature_id": top_priority_feature_id,
        "blocking_feature_ids": blocked_feature_ids,
        "blockers": gate["blockers"],
        **blocker_categories,
        "build_strategy": "stabilize_then_extend",
        "selected_bundle_id": None if gate["status"] == "blocked" else SELECTED_V5_BUNDLE_ID,
        "selected_bundle_name": None if gate["status"] == "blocked" else SELECTED_V5_BUNDLE_NAME,
        "selected_bundle_scope": [] if gate["status"] == "blocked" else SELECTED_V5_BUNDLE_SCOPE,
        "selection_evidence_paths": [] if gate["status"] == "blocked" else SELECTED_V5_BUNDLE_EVIDENCE,
        "bundle_selection_rule": (
            "Do not broaden the V5 lifecycle headline beyond prd_handoff until the next bounded slice has passing proof."
        ),
        "retirement_rule": (
            "Keep the current V5 slice stable while later lifecycle stages remain explicitly deferred."
        ),
        "required_steps": required_steps,
        "generated_at": generated_at,
    }


def format_v5_cutover_plan_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# V5 Cutover Plan",
        "",
        f"Target Version: `{plan['target_version']}`",
        f"Source Baseline: `V{plan['source_baseline_version']}`",
        f"Current Stage: `{plan['current_stage']}`",
        f"Selection Status: `{plan['selection_status']}`",
        f"Promotion Gate: `{plan['promotion_gate_status']}`",
        f"Stable Release: `V{plan['stable_release_version']}`",
        "",
    ]
    if plan["selected_bundle_name"]:
        lines.extend(
            [
                "## Selected Bundle",
                "",
                f"- id: `{plan['selected_bundle_id']}`",
                f"- name: `{plan['selected_bundle_name']}`",
                *[f"- scope: {item}" for item in plan["selected_bundle_scope"]],
                *[f"- evidence: `{path}`" for path in plan["selection_evidence_paths"]],
                "",
            ]
        )
    lines.extend(
        [
            "## Build Strategy",
            "",
            "- keep V5.0.0 as the stable line for lifecycle traceability through prd_handoff",
            "- preserve release evidence and starter-workspace adoption parity for the current slice",
            "- extend beyond prd_handoff only through a later bounded release",
            "",
            "## Current Blockers",
            "",
        ]
    )
    if plan["blockers"]:
        for blocker in plan["blockers"]:
            lines.append(f"- {blocker}")
        if plan.get("feed_governance_blockers"):
            lines.extend(["", "## Feed Governance Blockers", ""])
            for blocker in plan["feed_governance_blockers"]:
                lines.append(f"- {blocker}")
        if plan.get("governed_research_blockers"):
            lines.extend(["", "## Governed Research Blockers", ""])
            for blocker in plan["governed_research_blockers"]:
                lines.append(f"- {blocker}")
        if plan.get("other_blockers"):
            lines.extend(["", "## Other Blockers", ""])
            for blocker in plan["other_blockers"]:
                lines.append(f"- {blocker}")
    elif plan["selection_status"] == "stable_active":
        lines.append("- ProductOS V5.0.0 is already the stable release.")
        lines.append("- The next bounded expansion is extending lifecycle traceability beyond prd_handoff.")
    else:
        lines.append("- The V5 lifecycle-traceability slice is selected and ready for stable promotion.")
    lines.extend(
        [
            f"- Top priority feature remains `{plan['top_priority_feature_id']}`.",
            "",
            "## Required Steps",
            "",
        ]
    )
    for step in plan["required_steps"]:
        lines.append(f"- {step}")
    lines.extend(
        [
            "",
            "## Rules",
            "",
            f"- {plan['bundle_selection_rule']}",
            f"- {plan['retirement_rule']}",
            "",
        ]
    )
    return "\n".join(lines)


def build_v6_cutover_plan_from_workspace(
    workspace_dir,
    *,
    generated_at: str,
    target_version: str = "6.0.0",
) -> dict[str, Any]:
    bundle = build_v6_lifecycle_bundle_from_workspace(
        workspace_dir,
        generated_at=generated_at,
        target_version=target_version,
    )
    readiness = bundle["release_readiness_v6_lifecycle_traceability"]
    release_gate = bundle["release_gate_decision_v6_lifecycle_traceability"]
    root_dir = Path(__file__).resolve().parents[3]
    latest_release = latest_release_metadata(root_dir)
    promoted = parse_semver(latest_release["core_version"]) >= parse_semver(target_version)

    blockers = [
        f"{check['name']}: {check['notes']}"
        for check in readiness["checks"]
        if check["status"] != "passed"
    ]
    gate_status = "ready" if release_gate["decision"] == "go" else "blocked"

    if gate_status == "blocked":
        selection_status = "deferred"
        current_stage = "hold_stable_extension_gate"
    elif promoted:
        selection_status = "stable_active"
        current_stage = "extend_lifecycle_beyond_release_readiness"
    else:
        selection_status = "selected_for_promotion"
        current_stage = "promote_v6_stable"

    required_steps = (
        [
            "Resolve the remaining release-readiness lifecycle proof gaps before broadening the stable line.",
            "Back every advertised trace focus area with concrete workspace snapshots before claiming full control-surface parity.",
            "Keep the V5.0.0 stable slice available until the V6 release gate is healthy.",
        ]
        if gate_status == "blocked"
        else [
            "Keep ProductOS V6.0.0 as the canonical stable line while preserving the selected release-readiness lifecycle evidence.",
            "Extend lifecycle traceability beyond release_readiness only as a later bounded release.",
            "Keep the starter workspace as the default reusable adoption surface for the current V6 slice.",
        ]
        if promoted
        else [
            "Promote the selected V6 lifecycle-traceability bundle as the stable ProductOS line.",
            "Update stable-release metadata and docs to reflect the promoted V6 slice.",
        ]
    )

    return {
        "target_version": target_version,
        "source_baseline_version": bundle["runtime_scenario_report_v6_lifecycle_traceability"]["baseline_version"],
        "current_stage": current_stage,
        "selection_status": selection_status,
        "promotion_gate_status": gate_status,
        "stable_release_version": latest_release["core_version"],
        "top_priority_feature_id": (
            "extend_lifecycle_beyond_release_readiness"
            if promoted and gate_status != "blocked"
            else "v6_bundle_selection"
        ),
        "blocking_feature_ids": ["v6_lifecycle_traceability_release_readiness"] if blockers else [],
        "blockers": blockers,
        "build_strategy": "stabilize_then_extend",
        "selected_bundle_id": None if gate_status == "blocked" else SELECTED_V6_BUNDLE_ID,
        "selected_bundle_name": None if gate_status == "blocked" else SELECTED_V6_BUNDLE_NAME,
        "selected_bundle_scope": [] if gate_status == "blocked" else SELECTED_V6_BUNDLE_SCOPE,
        "selection_evidence_paths": [] if gate_status == "blocked" else SELECTED_V6_BUNDLE_EVIDENCE,
        "bundle_selection_rule": (
            "Do not broaden the V6 lifecycle headline beyond release_readiness until the next bounded slice has passing proof."
        ),
        "retirement_rule": (
            "Keep the current V6 slice stable while launch and outcome stages remain explicitly deferred."
        ),
        "required_steps": required_steps,
        "generated_at": generated_at,
    }


def format_v6_cutover_plan_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# V6 Cutover Plan",
        "",
        f"Target Version: `{plan['target_version']}`",
        f"Source Baseline: `V{plan['source_baseline_version']}`",
        f"Current Stage: `{plan['current_stage']}`",
        f"Selection Status: `{plan['selection_status']}`",
        f"Promotion Gate: `{plan['promotion_gate_status']}`",
        f"Stable Release: `V{plan['stable_release_version']}`",
        "",
    ]
    if plan["selected_bundle_name"]:
        lines.extend(
            [
                "## Selected Bundle",
                "",
                f"- id: `{plan['selected_bundle_id']}`",
                f"- name: `{plan['selected_bundle_name']}`",
                *[f"- scope: {item}" for item in plan["selected_bundle_scope"]],
                *[f"- evidence: `{path}`" for path in plan["selection_evidence_paths"]],
                "",
            ]
        )
    lines.extend(
        [
            "## Build Strategy",
            "",
            "- keep V6.0.0 as the stable line for lifecycle traceability through release_readiness",
            "- preserve release evidence, trace focus-area coverage, and starter-workspace adoption parity for the current slice",
            "- extend beyond release_readiness only through a later bounded release",
            "",
            "## Current Blockers",
            "",
        ]
    )
    if plan["blockers"]:
        for blocker in plan["blockers"]:
            lines.append(f"- {blocker}")
    elif plan["selection_status"] == "stable_active":
        lines.append("- ProductOS V6.0.0 is already the stable release.")
        lines.append("- The next bounded expansion is extending lifecycle traceability beyond release_readiness.")
    else:
        lines.append("- The V6 lifecycle-traceability slice is selected and ready for stable promotion.")
    lines.extend(
        [
            f"- Top priority feature remains `{plan['top_priority_feature_id']}`.",
            "",
            "## Required Steps",
            "",
        ]
    )
    for step in plan["required_steps"]:
        lines.append(f"- {step}")
    lines.extend(
        [
            "",
            "## Rules",
            "",
            f"- {plan['bundle_selection_rule']}",
            f"- {plan['retirement_rule']}",
            "",
        ]
    )
    return "\n".join(lines)


def build_v7_cutover_plan_from_workspace(
    workspace_dir,
    *,
    generated_at: str,
    target_version: str = "7.0.0",
) -> dict[str, Any]:
    bundle = build_v7_lifecycle_bundle_from_workspace(
        workspace_dir,
        generated_at=generated_at,
        target_version=target_version,
    )
    readiness = bundle["release_readiness_v7_lifecycle_traceability"]
    release_gate = bundle["release_gate_decision_v7_lifecycle_traceability"]
    root_dir = Path(__file__).resolve().parents[3]
    latest_release = latest_release_metadata(root_dir)
    promoted = parse_semver(latest_release["core_version"]) >= parse_semver(target_version)

    blockers = [
        f"{check['name']}: {check['notes']}"
        for check in readiness["checks"]
        if check["status"] != "passed"
    ]
    gate_status = "ready" if release_gate["decision"] == "go" else "blocked"

    if gate_status == "blocked":
        selection_status = "deferred"
        current_stage = "hold_stable_extension_gate"
    elif promoted:
        selection_status = "stable_active"
        current_stage = "externalize_lifecycle_publication"
    else:
        selection_status = "selected_for_promotion"
        current_stage = "promote_v7_stable"

    required_steps = (
        [
            "Resolve the remaining launch, outcome, or parity proof gaps before broadening the stable line.",
            "Keep the V6.0.0 stable slice available until the V7 release gate is healthy.",
            "Do not claim external publication coverage until publication adapters consume lifecycle traces as first-class inputs.",
        ]
        if gate_status == "blocked"
        else [
            f"Keep ProductOS V{latest_release['core_version']} as the canonical stable line while preserving the selected full-lifecycle evidence.",
            "Extend ProductOS only through a later bounded release with explicit proof.",
            "Keep the starter workspace as the default reusable adoption surface for the currently promoted stable line.",
        ]
        if promoted
        else [
            "Promote the selected V7 lifecycle-traceability bundle as the stable ProductOS line.",
            "Update stable-release metadata and docs to reflect the promoted V7 slice.",
        ]
    )

    return {
        "target_version": target_version,
        "source_baseline_version": bundle["runtime_scenario_report_v7_lifecycle_traceability"]["baseline_version"],
        "current_stage": current_stage,
        "selection_status": selection_status,
        "promotion_gate_status": gate_status,
        "stable_release_version": latest_release["core_version"],
        "top_priority_feature_id": (
            "external_publication_adapters"
            if promoted and gate_status != "blocked"
            else "v7_bundle_selection"
        ),
        "blocking_feature_ids": ["v7_lifecycle_traceability_outcome_review"] if blockers else [],
        "blockers": blockers,
        "build_strategy": "stabilize_then_externalize",
        "selected_bundle_id": None if gate_status == "blocked" else SELECTED_V7_BUNDLE_ID,
        "selected_bundle_name": None if gate_status == "blocked" else SELECTED_V7_BUNDLE_NAME,
        "selected_bundle_scope": [] if gate_status == "blocked" else SELECTED_V7_BUNDLE_SCOPE,
        "selection_evidence_paths": [] if gate_status == "blocked" else SELECTED_V7_BUNDLE_EVIDENCE,
        "bundle_selection_rule": (
            "Do not broaden the V7 lifecycle headline beyond outcome_review until the next bounded externalization slice has passing proof."
        ),
        "retirement_rule": (
            "Keep the current V7 slice stable while publication adapters and broader distribution packaging remain explicitly deferred."
        ),
        "required_steps": required_steps,
        "generated_at": generated_at,
    }


def format_v7_cutover_plan_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# V7 Cutover Plan",
        "",
        f"Target Version: `{plan['target_version']}`",
        f"Source Baseline: `V{plan['source_baseline_version']}`",
        f"Current Stage: `{plan['current_stage']}`",
        f"Selection Status: `{plan['selection_status']}`",
        f"Promotion Gate: `{plan['promotion_gate_status']}`",
        f"Stable Release: `V{plan['stable_release_version']}`",
        "",
    ]
    if plan["selected_bundle_name"]:
        lines.extend(
            [
                "## Selected Bundle",
                "",
                f"- id: `{plan['selected_bundle_id']}`",
                f"- name: `{plan['selected_bundle_name']}`",
                *[f"- scope: {item}" for item in plan["selected_bundle_scope"]],
                *[f"- evidence: `{path}`" for path in plan["selection_evidence_paths"]],
                "",
            ]
        )
    lines.extend(
        [
            "## Build Strategy",
            "",
            f"- keep V{plan['stable_release_version']} as the stable line while preserving the promoted PM superpower core",
            "- preserve lifecycle traceability, governed research, docs-and-deck evidence, weekly PM autopilot, and release-gate truthfulness in the current stable line",
            "- extend beyond the current PM superpower core only through a later bounded release with explicit proof",
            "",
            "## Current Blockers",
            "",
        ]
    )
    if plan["blockers"]:
        for blocker in plan["blockers"]:
            lines.append(f"- {blocker}")
    elif plan["selection_status"] == "stable_active":
        lines.append(f"- ProductOS V{plan['stable_release_version']} is already the stable release.")
        lines.append("- The next bounded expansion should stay explicitly scoped and evidence-backed.")
    else:
        lines.append("- The V7 lifecycle-traceability slice is selected and ready for stable promotion.")
    lines.extend(
        [
            f"- Top priority feature remains `{plan['top_priority_feature_id']}`.",
            "",
            "## Required Steps",
            "",
        ]
    )
    for step in plan["required_steps"]:
        lines.append(f"- {step}")
    lines.extend(
        [
            "",
            "## Rules",
            "",
            f"- {plan['bundle_selection_rule']}",
            f"- {plan['retirement_rule']}",
            "",
        ]
    )
    return "\n".join(lines)


def build_v9_cutover_plan_from_workspace(
    workspace_dir,
    *,
    generated_at: str,
    target_version: str = "9.0.0",
    adapter_name: str = "codex",
) -> dict[str, Any]:
    bundle = build_v9_lifecycle_bundle_from_workspace(
        workspace_dir,
        generated_at=generated_at,
        target_version=target_version,
        adapter_name=adapter_name,
    )
    program_state = inspect_v9_lifecycle_enrichment_state(
        workspace_dir,
        generated_at=generated_at,
        adapter_name=adapter_name,
    )
    release_gate = bundle["release_gate_decision_v9_lifecycle_enrichment"]
    readiness = bundle["release_readiness_v9_lifecycle_enrichment"]
    latest_release = latest_release_metadata(Path(__file__).resolve().parents[3])
    promoted = parse_semver(latest_release["core_version"]) >= parse_semver(target_version)
    blockers = [
        f"{check['name']}: {check['notes']}"
        for check in readiness["checks"]
        if check["status"] != "passed"
    ]
    gate_status = "ready" if release_gate["decision"] == "go" else "blocked"

    if gate_status == "blocked":
        selection_status = "deferred"
        current_stage = "hold_lifecycle_enrichment_gate"
    elif promoted:
        selection_status = "stable_active"
        current_stage = "operate_v9_stable"
    else:
        selection_status = "selected_for_promotion"
        current_stage = "promote_v9_stable"

    return {
        "target_version": target_version,
        "source_baseline_version": bundle["runtime_scenario_report_v9_lifecycle_enrichment"]["baseline_version"],
        "current_stage": current_stage,
        "selection_status": selection_status,
        "promotion_gate_status": gate_status,
        "stable_release_version": latest_release["core_version"],
        "top_priority_feature_id": "lifecycle_enrichment_program",
        "blocking_feature_ids": [
            track_id.lower()
            for track_id, track_state in program_state["track_states"].items()
            if track_state["status"] != "passed"
        ],
        "blockers": blockers,
        "build_strategy": "promote_only_after_shared_gate",
        "selected_bundle_id": None if gate_status == "blocked" else "v9_lifecycle_enrichment_program",
        "selected_bundle_name": None if gate_status == "blocked" else "Lifecycle enrichment through governed research and reopen readiness",
        "selected_bundle_scope": (
            []
            if gate_status == "blocked"
            else [
                "Promote the lifecycle-enrichment program only after P0, P1, and P2 all pass one shared release gate.",
                "Keep V8.4.0 stable until workspace coherence, governed research, and downstream reopen loops are all artifact-backed.",
                "Ignore superseded March increment and next-version release-gate artifacts when evaluating V9 proof.",
            ]
        ),
        "selection_evidence_paths": [] if gate_status == "blocked" else [
            "internal/ProductOS-Next/docs/planning/current-plan.md",
            "internal/ProductOS-Next/docs/planning/next-version-release-review.md",
            "internal/ProductOS-Next/docs/planning/roadmap.md",
        ],
        "bundle_selection_rule": (
            "Do not promote V9 until runtime coherence, governed research, and downstream learning loops all clear as artifact-backed in one shared gate."
        ),
        "retirement_rule": (
            "Keep V8.4.0 as the public stable line until the V9 lifecycle-enrichment gate is explicitly go."
        ),
        "required_steps": (
            [
                "Remove the remaining fallback and deferred evidence from the lifecycle-enrichment program.",
                "Keep public stable-line surfaces on V8.4.0 while the shared V9 gate remains blocked.",
                "Rerun the V9 bundle and promote only after P0, P1, and P2 all pass together.",
            ]
            if gate_status == "blocked"
            else [
                "Promote ProductOS V9.0.0 across the stable release metadata and public docs.",
                "Update workspace and suite registrations to V9.0.0 in the same promotion step.",
            ]
        ),
        "generated_at": generated_at,
    }


def format_v9_cutover_plan_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# V9 Cutover Plan",
        "",
        f"Target Version: `{plan['target_version']}`",
        f"Source Baseline: `V{plan['source_baseline_version']}`",
        f"Current Stage: `{plan['current_stage']}`",
        f"Selection Status: `{plan['selection_status']}`",
        f"Promotion Gate: `{plan['promotion_gate_status']}`",
        f"Stable Release: `V{plan['stable_release_version']}`",
        "",
        "## Build Strategy",
        "",
        "- keep V8.4.0 public until the full lifecycle-enrichment gate is go",
        "- require P0 runtime coherence, P1 governed research, and P2 downstream reopen loops to pass together",
        "- treat the April 27 planning docs as canonical and ignore superseded March release inputs",
        "",
        "## Current Blockers",
        "",
    ]
    if plan["blockers"]:
        for blocker in plan["blockers"]:
            lines.append(f"- {blocker}")
    else:
        lines.append("- The V9 lifecycle-enrichment bundle is selected and ready for stable promotion.")
    lines.extend(
        [
            "",
            "## Required Steps",
            "",
            *[f"- {step}" for step in plan["required_steps"]],
            "",
            "## Rules",
            "",
            f"- {plan['bundle_selection_rule']}",
            f"- {plan['retirement_rule']}",
            "",
        ]
    )
    return "\n".join(lines)
