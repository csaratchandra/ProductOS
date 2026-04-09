#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.python.productos_runtime import (
    ADOPTION_ARTIFACT_SCHEMAS,
    RESEARCH_DISCOVERY_ARTIFACT_SCHEMAS,
    RESEARCH_FEED_REGISTRY_ARTIFACT_SCHEMAS,
    RESEARCH_PLANNING_ARTIFACT_SCHEMAS,
    RESEARCH_RUNTIME_ARTIFACT_SCHEMAS,
    adopt_workspace_from_source,
    build_external_research_feed_registry_from_workspace,
    build_external_research_plan_from_workspace,
    build_next_version_bundle_from_workspace,
    build_workspace_adoption_bundle_from_source,
    build_v5_lifecycle_bundle_from_workspace,
    build_v5_cutover_plan_from_workspace,
    build_v6_lifecycle_bundle_from_workspace,
    build_v6_cutover_plan_from_workspace,
    build_v7_lifecycle_bundle_from_workspace,
    build_v7_cutover_plan_from_workspace,
    format_item_lifecycle_state,
    format_lifecycle_stage_snapshot,
    format_v5_cutover_plan_markdown,
    format_v6_cutover_plan_markdown,
    format_v7_cutover_plan_markdown,
    init_workspace_from_template,
    load_item_lifecycle_state_from_workspace,
    load_lifecycle_stage_snapshot_from_workspace,
    discover_external_research_sources_from_workspace,
    research_workspace_from_manifest,
    run_external_research_loop_from_workspace,
    summarize_v5_lifecycle_bundle,
    summarize_v6_lifecycle_bundle,
    summarize_v7_lifecycle_bundle,
    init_mission_in_workspace,
    load_mission_brief_from_workspace,
    sync_canonical_discover_artifacts,
)
from core.python.productos_runtime.validation import inspect_workspace_source_note_card_refs
from core.python.productos_runtime.next_version import NEXT_VERSION_ARTIFACT_SCHEMAS
from core.python.productos_runtime.v5 import V5_ARTIFACT_SCHEMAS
from core.python.productos_runtime.v6 import V6_ARTIFACT_SCHEMAS
from core.python.productos_runtime.v7 import V7_ARTIFACT_SCHEMAS
from core.python.productos_runtime.release import evaluate_promotion_gate

SCHEMA_DIR = ROOT / "core" / "schemas" / "artifacts"
PHASE_ARTIFACTS = {
    "discover": [
        "cockpit_state",
        "orchestration_state",
        "intake_routing_state",
        "memory_retrieval_state",
        "context_pack",
        "discover_problem_brief",
        "discover_concept_brief",
        "discover_prd",
        "discover_execution_session_state",
        "discover_feature_scorecard",
    ],
    "align": [
        "cockpit_state",
        "orchestration_state",
        "context_pack",
        "align_execution_session_state",
        "align_document_sync_state",
        "market_distribution_report",
        "presentation_brief",
        "presentation_evidence_pack",
        "presentation_story",
        "presentation_render_spec",
        "presentation_publish_check",
        "presentation_ppt_export_plan",
        "docs_alignment_feature_scorecard",
        "presentation_feature_scorecard",
    ],
    "operate": [
        "cockpit_state",
        "orchestration_state",
        "context_pack",
        "operate_execution_session_state",
        "operate_status_mail",
        "operate_issue_log",
        "weekly_pm_autopilot_feature_scorecard",
        "runtime_control_surface_feature_scorecard",
    ],
    "improve": [
        "cockpit_state",
        "orchestration_state",
        "context_pack",
        "eval_suite_manifest",
        "eval_run_report",
        "next_version_release_gate_decision",
        "improve_execution_session_state",
        "improve_improvement_loop_state",
        "autonomous_pm_swarm_plan",
        "autonomous_pm_swarm_feature_scorecard",
        "adapter_parity_report",
        "market_refresh_report",
        "self_improvement_feature_scorecard",
        "feature_portfolio_review",
    ],
    "all": list(NEXT_VERSION_ARTIFACT_SCHEMAS.keys()),
}
ADOPTION_ARTIFACTS = list(ADOPTION_ARTIFACT_SCHEMAS.keys())
RESEARCH_RUNTIME_ARTIFACTS = list(RESEARCH_RUNTIME_ARTIFACT_SCHEMAS.keys())
RESEARCH_PLANNING_ARTIFACTS = list(RESEARCH_PLANNING_ARTIFACT_SCHEMAS.keys())
RESEARCH_FEED_REGISTRY_ARTIFACTS = list(RESEARCH_FEED_REGISTRY_ARTIFACT_SCHEMAS.keys())
RESEARCH_DISCOVERY_ARTIFACTS = list(RESEARCH_DISCOVERY_ARTIFACT_SCHEMAS.keys())


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _workspace_dir(args: argparse.Namespace) -> Path:
    if args.workspace_dir is not None:
        return args.workspace_dir

    private_workspace = ROOT / "internal" / "ProductOS-Next"
    if private_workspace.exists():
        return private_workspace

    raise SystemExit(
        "No default self-hosting workspace is included in this repo checkout. "
        "Pass --workspace-dir to run this command against a specific workspace."
    )


def _build_bundle(args: argparse.Namespace) -> dict[str, dict]:
    return build_next_version_bundle_from_workspace(
        _workspace_dir(args),
        generated_at=args.generated_at,
        adapter_name=args.adapter,
    )


def _validate_bundle(bundle: dict[str, dict]) -> list[str]:
    failures: list[str] = []
    for artifact_name, schema_name in NEXT_VERSION_ARTIFACT_SCHEMAS.items():
        validator = Draft202012Validator(_load_json(SCHEMA_DIR / schema_name))
        errors = sorted(validator.iter_errors(bundle[artifact_name]), key=lambda item: list(item.path))
        if errors:
            failures.extend(
                f"{artifact_name} failed {schema_name}: {error.message}"
                for error in errors
            )
    return failures


def _validate_named_bundle(bundle: dict[str, dict], schema_map: dict[str, str]) -> list[str]:
    failures: list[str] = []
    for artifact_name, schema_name in schema_map.items():
        validator = Draft202012Validator(_load_json(SCHEMA_DIR / schema_name))
        errors = sorted(validator.iter_errors(bundle[artifact_name]), key=lambda item: list(item.path))
        if errors:
            failures.extend(
                f"{artifact_name} failed {schema_name}: {error.message}"
                for error in errors
            )
    return failures


def _write_artifacts(output_dir: Path, bundle: dict[str, dict], names: list[str]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for name in names:
        with (output_dir / f"{name}.json").open("w", encoding="utf-8") as handle:
            json.dump(bundle[name], handle, indent=2)
            handle.write("\n")


def _write_release_review_markdown(output_dir: Path, bundle: dict[str, dict]) -> None:
    release_gate = bundle.get("next_version_release_gate_decision")
    portfolio = bundle.get("feature_portfolio_review")
    if release_gate is None or portfolio is None:
        return

    lines = [
        "# Next-Version Release Review",
        "",
        f"- Decision: `{release_gate['decision']}`",
        f"- Target release: `{release_gate['target_release']}`",
        f"- Truthfulness: `{portfolio['truthfulness_status']}`",
        f"- Top priority feature: `{portfolio['top_priority_feature_id']}`",
        "",
        "## Rationale",
        "",
        release_gate["rationale"],
        "",
        "## Next Action",
        "",
        release_gate.get("next_action", "No next action recorded."),
        "",
    ]

    categories = release_gate.get("blocker_categories", {})
    grouped_sections = [
        ("Feed Governance Blockers", list(categories.get("feed_governance_blockers", [])) if isinstance(categories, dict) else []),
        ("Governed Research Blockers", list(categories.get("governed_research_blockers", [])) if isinstance(categories, dict) else []),
        ("Other Blockers", list(categories.get("other_blockers", [])) if isinstance(categories, dict) else []),
    ]
    rendered = False
    for title, items in grouped_sections:
        if not items:
            continue
        rendered = True
        lines.extend([f"## {title}", ""])
        for item in items:
            lines.append(f"- {item}")
        lines.append("")

    if not rendered:
        lines.extend(["## Blockers", ""])
        for item in release_gate.get("known_gaps", []):
            lines.append(f"- {item}")
        lines.append("")

    lines.extend(["## Deferred Items", ""])
    for item in release_gate.get("deferred_items", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Active Improvement Features", ""])
    for feature_id in portfolio.get("active_improvement_feature_ids", []) or ["None."]:
        lines.append(f"- {feature_id}")

    (output_dir / "next_version_release_review.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_workspace_release_review_markdown(workspace_dir: Path, bundle: dict[str, dict]) -> None:
    docs_dir = workspace_dir / "docs" / "planning"
    docs_dir.mkdir(parents=True, exist_ok=True)
    _write_release_review_markdown(docs_dir, bundle)
    source = docs_dir / "next_version_release_review.md"
    target = docs_dir / "next-version-release-review.md"
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    source.unlink()


def _phase_output_dir(workspace_dir: Path, phase: str) -> Path:
    return workspace_dir / "outputs" / phase


def _print_mission_summary(workspace_dir: Path) -> None:
    mission_brief = load_mission_brief_from_workspace(workspace_dir)
    if mission_brief is None:
        return
    print(f"Mission: {mission_brief['title']}")
    print(f"Mission Mode: {mission_brief['operating_mode']}")


def _promotion_gate(bundle: dict[str, dict]) -> dict[str, object]:
    return evaluate_promotion_gate(
        eval_run_report=bundle["eval_run_report"],
        feature_portfolio_review=bundle["feature_portfolio_review"],
        research_brief=bundle.get("research_brief"),
        external_research_plan=bundle.get("external_research_plan"),
        external_research_source_discovery=bundle.get("external_research_source_discovery"),
        external_research_feed_registry=bundle.get("external_research_feed_registry"),
        selected_manifest=bundle.get("external_research_selected_manifest"),
        external_research_review=bundle.get("external_research_review"),
    )


def _governed_research_status(bundle: dict[str, dict]) -> str:
    if bundle.get("external_research_review") is not None:
        review = bundle["external_research_review"]
        return "review_required" if review.get("review_status") == "review_required" else "clear"
    if bundle.get("external_research_selected_manifest") is not None:
        selected_manifest = bundle["external_research_selected_manifest"]
        return "selected_sources" if selected_manifest.get("sources") else "blocked"
    if bundle.get("external_research_source_discovery") is not None:
        return bundle["external_research_source_discovery"].get("search_status", "planned")
    if bundle.get("research_brief") is not None and bundle.get("external_research_plan") is not None:
        return "planned"
    return "not_required"


def _feed_governance_alerts(bundle: dict[str, dict]) -> list[str]:
    registry = bundle.get("external_research_feed_registry")
    if registry is None:
        return []
    alerts: list[str] = []
    for feed in registry.get("feeds", []):
        feed_id = feed.get("feed_id", feed.get("title", "unknown"))
        health_status = feed.get("health_status")
        if health_status in {"error", "unconfigured", "empty"}:
            alerts.append(
                f"{feed_id}: {health_status} ({feed.get('health_reason', 'feed health needs review')})"
            )
        cadence_status = feed.get("cadence_status")
        if cadence_status in {"due", "stale"}:
            alerts.append(
                f"{feed_id}: cadence {cadence_status} ({feed.get('cadence_reason', 'feed freshness needs review')})"
            )
    return alerts


def _feed_governance_status(bundle: dict[str, dict]) -> str:
    registry = bundle.get("external_research_feed_registry")
    if registry is None:
        return "not_configured"
    feeds = list(registry.get("feeds", []))
    if not feeds:
        return "not_configured"

    counts = {
        "error": 0,
        "unconfigured": 0,
        "empty": 0,
        "stale": 0,
        "due": 0,
    }
    for feed in feeds:
        health_status = feed.get("health_status")
        cadence_status = feed.get("cadence_status")
        if health_status in counts:
            counts[health_status] += 1
        if cadence_status in {"stale", "due"}:
            counts[cadence_status] += 1

    if counts["error"] or counts["unconfigured"] or counts["stale"]:
        details = []
        for key in ("error", "unconfigured", "stale", "empty", "due"):
            if counts[key]:
                details.append(f"{counts[key]} {key}")
        return f"degraded ({', '.join(details)})"
    if counts["empty"] or counts["due"]:
        details = []
        for key in ("empty", "due"):
            if counts[key]:
                details.append(f"{counts[key]} {key}")
        return f"review ({', '.join(details)})"
    return f"healthy ({len(feeds)} feeds)"


def _print_promotion_blockers(gate: dict[str, object]) -> None:
    blockers = list(gate.get("blockers", []))
    if not blockers:
        return
    categories = gate.get("blocker_categories", {})
    print("Promotion Blockers:")
    grouped_sections = [
        ("Feed Governance", list(categories.get("feed_governance_blockers", [])) if isinstance(categories, dict) else []),
        ("Governed Research", list(categories.get("governed_research_blockers", [])) if isinstance(categories, dict) else []),
        ("Other", list(categories.get("other_blockers", [])) if isinstance(categories, dict) else []),
    ]
    rendered = False
    for title, items in grouped_sections:
        if not items:
            continue
        rendered = True
        print(f"- {title}:")
        for item in items:
            print(f"- {item}")
    if not rendered:
        for blocker in blockers:
            print(f"- {blocker}")


def cmd_status(args: argparse.Namespace) -> int:
    bundle = _build_bundle(args)
    workspace_dir = _workspace_dir(args)
    cockpit = bundle["cockpit_state"]
    review = bundle["feature_portfolio_review"]
    eval_report = bundle["eval_run_report"]
    swarm_plan = bundle["autonomous_pm_swarm_plan"]
    swarm_scorecard = bundle["autonomous_pm_swarm_feature_scorecard"]
    gate = _promotion_gate(bundle)
    cutover_plan = build_v6_cutover_plan_from_workspace(
        workspace_dir,
        generated_at=args.generated_at,
    )
    if cutover_plan["selection_status"] == "stable_active":
        cutover_plan = build_v7_cutover_plan_from_workspace(
            workspace_dir,
            generated_at=args.generated_at,
        )
    focus = cockpit["current_focus"]
    top_priority_feature = review["top_priority_feature_id"]
    if cutover_plan["selection_status"] == "stable_active" and cutover_plan["stable_release_version"] == "7.0.0":
        focus = "Keep ProductOS V7.0.0 stable for lifecycle traceability through outcome_review and prepare the next external publication slice."
        top_priority_feature = cutover_plan["top_priority_feature_id"]
    elif cutover_plan["selection_status"] == "stable_active" and cutover_plan["stable_release_version"] == "6.0.0":
        focus = "Keep ProductOS V6.0.0 stable for lifecycle traceability through release_readiness and prepare the next bounded lifecycle expansion."
        top_priority_feature = cutover_plan["top_priority_feature_id"]
    print(f"Mode: {cockpit['mode']}")
    print(f"Status: {cockpit['status']}")
    print(f"Focus: {focus}")
    _print_mission_summary(workspace_dir)
    print(f"Top Priority Feature: {top_priority_feature}")
    print(f"Truthfulness Status: {review['truthfulness_status']}")
    print(f"Eval Status: {eval_report['status']} ({eval_report['regression_count']} regressions)")
    print(f"Governed Research: {_governed_research_status(bundle)}")
    print(f"Feed Governance: {_feed_governance_status(bundle)}")
    print(f"Swarm Plan: {swarm_plan['status']} ({swarm_plan['operating_mode']})")
    print(f"Swarm Readiness: {swarm_scorecard['overall_score']}/5 ({swarm_scorecard['adoption_recommendation']})")
    print(f"Stable Promotion: {gate['status']}")
    _print_promotion_blockers(gate)
    feed_alerts = _feed_governance_alerts(bundle)
    if feed_alerts:
        print("Feed Governance Alerts:")
        for alert in feed_alerts:
            print(f"- {alert}")
    print(f"Internal Use Features: {len(review['internal_use_feature_ids'])}")
    print(f"Active Improvement Features: {len(review['active_improvement_feature_ids'])}")
    return 0


def cmd_ingest(args: argparse.Namespace) -> int:
    bundle = _build_bundle(args)
    intake = bundle["intake_routing_state"]
    print(f"Ingestion Mode: {intake['ingestion_mode']}")
    print(f"Intake Items: {len(intake['intake_items'])}")
    for item in intake["intake_items"]:
        print(f"- {item['item_id']}: {item['input_type']} -> {', '.join(item['recommended_workflow_ids'])}")
    if args.output_dir:
        _write_artifacts(args.output_dir, bundle, ["intake_routing_state"])
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    bundle = _build_bundle(args)
    workspace_dir = _workspace_dir(args)
    names = PHASE_ARTIFACTS[args.phase]
    if args.output_dir:
        _write_artifacts(args.output_dir, bundle, names)
        if args.phase in {"improve", "all"}:
            _write_release_review_markdown(args.output_dir, bundle)
    if args.persist:
        output_dir = _phase_output_dir(workspace_dir, args.phase)
        _write_artifacts(output_dir, bundle, names)
        if args.phase in {"discover", "all"}:
            mission_brief = load_mission_brief_from_workspace(workspace_dir)
            if mission_brief is not None:
                sync_canonical_discover_artifacts(
                    workspace_dir,
                    mission_brief=mission_brief,
                    generated_at=args.generated_at,
                    problem_brief=bundle.get("discover_problem_brief"),
                    concept_brief=bundle.get("discover_concept_brief"),
                    prd=bundle.get("discover_prd"),
                )
        if args.phase in {"improve", "all"}:
            _write_release_review_markdown(output_dir, bundle)
            _write_workspace_release_review_markdown(workspace_dir, bundle)
    session_name = f"{args.phase}_execution_session_state" if args.phase != "all" else "discover_execution_session_state"
    if args.phase != "all":
        session = bundle[session_name]
        print(f"Phase: {args.phase}")
        print(f"Session Status: {session['status']}")
        print(f"Objective: {session['objective']}")
        print(f"Context Pack: {bundle['context_pack']['context_pack_id']}")
        print("Outputs:")
        for ref in session["output_refs"]:
            print(f"- {ref}")
    else:
        print(f"Export-ready artifacts: {len(names)}")
    return 0


def cmd_review(args: argparse.Namespace) -> int:
    bundle = _build_bundle(args)
    workspace_dir = _workspace_dir(args)
    cockpit = bundle["cockpit_state"]
    portfolio = bundle["feature_portfolio_review"]
    eval_report = bundle["eval_run_report"]
    swarm_plan = bundle["autonomous_pm_swarm_plan"]
    swarm_scorecard = bundle["autonomous_pm_swarm_feature_scorecard"]
    gate = _promotion_gate(bundle)
    _print_mission_summary(workspace_dir)
    print(f"Governed Research: {_governed_research_status(bundle)}")
    print(f"Feed Governance: {_feed_governance_status(bundle)}")
    print(f"Swarm Plan: {swarm_plan['status']} ({swarm_plan['release_boundary']})")
    print(f"Swarm Readiness: {swarm_scorecard['overall_score']}/5 -> {swarm_scorecard['next_action']}")
    print("Pending Review Points:")
    for point in cockpit["pending_review_points"]:
        print(f"- {point}")
    feed_alerts = _feed_governance_alerts(bundle)
    if feed_alerts:
        print("Feed Governance Alerts:")
        for alert in feed_alerts:
            print(f"- {alert}")
    print(f"Stable Promotion: {gate['status']}")
    _print_promotion_blockers(gate)
    print(f"Eval Summary: {eval_report['summary']}")
    print("Sub-5 Features:")
    for item in portfolio["feature_summaries"]:
        if item["overall_score"] < 5:
            print(
                f"- {item['feature_id']}: {item['overall_score']}/5 "
                f"({item['provenance_classification']}) -> {item['next_action']}"
            )
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    bundle = _build_bundle(args)
    _write_artifacts(args.output_dir, bundle, list(bundle.keys()))
    _write_release_review_markdown(args.output_dir, bundle)
    print(f"Exported {len(bundle)} artifacts to {args.output_dir}")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    bundle = _build_bundle(args)
    workspace_dir = _workspace_dir(args)
    failures = _validate_bundle(bundle)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    adapter_registry = bundle["runtime_adapter_registry"]
    adapter = next(
        item for item in adapter_registry["adapters"]
        if item["adapter_id"] == {
            "codex": "adapter_codex_thin",
            "claude": "adapter_claude_style_thin",
            "windsurf": "adapter_windsurf_thin",
            "antigravity": "adapter_antigravity_thin",
        }[args.adapter]
    )
    review = bundle["feature_portfolio_review"]
    eval_report = bundle["eval_run_report"]
    swarm_plan = bundle["autonomous_pm_swarm_plan"]
    swarm_scorecard = bundle["autonomous_pm_swarm_feature_scorecard"]
    gate = _promotion_gate(bundle)
    cutover_plan = build_v6_cutover_plan_from_workspace(
        workspace_dir,
        generated_at=args.generated_at,
    )
    if cutover_plan["selection_status"] == "stable_active":
        cutover_plan = build_v7_cutover_plan_from_workspace(
            workspace_dir,
            generated_at=args.generated_at,
        )
    top_priority_feature = (
        cutover_plan["top_priority_feature_id"]
        if cutover_plan["selection_status"] == "stable_active" and cutover_plan["stable_release_version"] == "7.0.0"
        else review["top_priority_feature_id"]
    )
    status_label = (
        "blocked"
        if review["truthfulness_status"] == "blocked" or gate["status"] == "blocked"
        else "healthy" if review["truthfulness_status"] == "healthy" and eval_report["status"] == "passed" else "watch"
    )
    print(f"Bundle Status: {status_label} ({len(bundle)} artifacts validated)")
    _print_mission_summary(workspace_dir)
    print(f"Governed Research: {_governed_research_status(bundle)}")
    print(f"Feed Governance: {_feed_governance_status(bundle)}")
    print(f"Swarm Plan: {swarm_plan['status']} ({swarm_plan['operating_mode']})")
    print(f"Swarm Readiness: {swarm_scorecard['overall_score']}/5 ({swarm_scorecard['adoption_recommendation']})")
    print(f"Stable Promotion: {gate['status']}")
    _print_promotion_blockers(gate)
    feed_alerts = _feed_governance_alerts(bundle)
    if feed_alerts:
        print("Feed Governance Alerts:")
        for alert in feed_alerts:
            print(f"- {alert}")
    print(f"Selected Adapter: {adapter['name']} ({adapter['verification_status']})")
    print(f"Intake Items: {len(bundle['intake_routing_state']['intake_items'])}")
    print(f"Truthfulness Status: {review['truthfulness_status']}")
    print(f"Eval Status: {eval_report['status']} ({eval_report['regression_count']} regressions)")
    print(f"Top Priority Feature: {top_priority_feature}")
    return 0


def cmd_cutover(args: argparse.Namespace) -> int:
    if args.target_version.startswith("5."):
        plan = build_v5_cutover_plan_from_workspace(
            _workspace_dir(args),
            generated_at=args.generated_at,
            adapter_name=args.adapter,
            target_version=args.target_version,
        )
        formatter = format_v5_cutover_plan_markdown
    elif args.target_version.startswith("6."):
        plan = build_v6_cutover_plan_from_workspace(
            _workspace_dir(args),
            generated_at=args.generated_at,
            target_version=args.target_version,
        )
        formatter = format_v6_cutover_plan_markdown
    else:
        plan = build_v7_cutover_plan_from_workspace(
            _workspace_dir(args),
            generated_at=args.generated_at,
            target_version=args.target_version,
        )
        formatter = format_v7_cutover_plan_markdown
    print(f"Target Version: {plan['target_version']}")
    print(f"Source Baseline: V{plan['source_baseline_version']}")
    print(f"Selection Status: {plan['selection_status']}")
    print(f"Promotion Gate: {plan['promotion_gate_status']}")
    print(f"Stable Release: V{plan['stable_release_version']}")
    print(f"Build Strategy: {plan['build_strategy']}")
    if plan["selected_bundle_name"]:
        print(f"Selected Bundle: {plan['selected_bundle_name']}")
    print(f"Top Priority Feature: {plan['top_priority_feature_id']}")
    print("Blockers:")
    for blocker in plan["blockers"]:
        print(f"- {blocker}")
    if args.output_path:
        args.output_path.parent.mkdir(parents=True, exist_ok=True)
        args.output_path.write_text(formatter(plan) + "\n", encoding="utf-8")
        print(f"Wrote cutover plan to {args.output_path}")
    return 0


def cmd_v5(args: argparse.Namespace) -> int:
    bundle = build_v5_lifecycle_bundle_from_workspace(
        _workspace_dir(args),
        generated_at=args.generated_at,
    )
    print(summarize_v5_lifecycle_bundle(_workspace_dir(args), bundle))
    if args.output_dir:
        _write_artifacts(args.output_dir, bundle, list(V5_ARTIFACT_SCHEMAS.keys()))
    return 0


def cmd_v6(args: argparse.Namespace) -> int:
    bundle = build_v6_lifecycle_bundle_from_workspace(
        _workspace_dir(args),
        generated_at=args.generated_at,
    )
    print(summarize_v6_lifecycle_bundle(_workspace_dir(args), bundle))
    if args.output_dir:
        _write_artifacts(args.output_dir, bundle, list(V6_ARTIFACT_SCHEMAS.keys()))
    return 0


def cmd_v7(args: argparse.Namespace) -> int:
    bundle = build_v7_lifecycle_bundle_from_workspace(
        _workspace_dir(args),
        generated_at=args.generated_at,
    )
    print(summarize_v7_lifecycle_bundle(_workspace_dir(args), bundle))
    if args.output_dir:
        _write_artifacts(args.output_dir, bundle, list(V7_ARTIFACT_SCHEMAS.keys()))
    return 0


def cmd_trace(args: argparse.Namespace) -> int:
    if args.item_id:
        payload = load_item_lifecycle_state_from_workspace(_workspace_dir(args), item_id=args.item_id)
        print(format_item_lifecycle_state(payload))
        return 0

    payload = load_lifecycle_stage_snapshot_from_workspace(_workspace_dir(args), focus_area=args.stage)
    print(format_lifecycle_stage_snapshot(payload))
    return 0


def cmd_init_workspace(args: argparse.Namespace) -> int:
    init_workspace_from_template(
        ROOT,
        template_name=args.template,
        dest=args.dest,
        workspace_id=args.workspace_id,
        name=args.name,
        mode=args.mode,
    )
    print(f"Initialized workspace from templates at {args.dest}")
    return 0


def cmd_init_mission(args: argparse.Namespace) -> int:
    workspace_dir = _workspace_dir(args)
    mission_brief = init_mission_in_workspace(
        workspace_dir,
        title=args.title,
        target_user=args.target_user,
        customer_problem=args.customer_problem,
        business_goal=args.business_goal,
        success_metrics=args.success_metric,
        constraints=args.constraint,
        audience=args.audience,
        operating_mode=args.operating_mode,
        generated_at=args.generated_at,
    )
    print(f"Mission Brief: {mission_brief['mission_brief_id']}")
    print(f"Workspace: {workspace_dir}")
    print(f"Operating Mode: {mission_brief['operating_mode']}")
    print(f"Primary Workflows: {len(mission_brief['primary_workflow_refs'])}")
    print(f"Next Action: {mission_brief['next_action']}")
    return 0


def cmd_validate_workspace(args: argparse.Namespace) -> int:
    summary, failures = inspect_workspace_source_note_card_refs(_workspace_dir(args))
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print(
        "Workspace validation passed: "
        f"{summary['artifact_count']} artifacts checked, "
        f"{summary['source_note_card_count']} source note cards indexed."
    )
    return 0


def cmd_adopt_workspace(args: argparse.Namespace) -> int:
    bundle = build_workspace_adoption_bundle_from_source(
        ROOT,
        source_dir=args.source,
        workspace_id=args.workspace_id,
        name=args.name,
        generated_at=args.generated_at,
        review_threshold=args.review_threshold,
    )
    failures = _validate_named_bundle(bundle, ADOPTION_ARTIFACT_SCHEMAS)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    if args.output_dir:
        _write_artifacts(args.output_dir, bundle, ADOPTION_ARTIFACTS)

    report = bundle["workspace_adoption_report"]
    review_queue = bundle["adoption_review_queue"]
    print(f"Source Workspace Mode: {report['source_workspace_mode']}")
    print(f"Source Files: {report['source_file_count']}")
    print(f"Generated Artifacts: {len(report['generated_artifact_ids'])}")
    print(f"Review Items: {review_queue['review_items'] and len(review_queue['review_items']) or 0}")

    if args.dry_run:
        print("Adoption Status: dry-run")
        print("Dry Run: no workspace files were written.")
        return 0

    destination, adopted_bundle = adopt_workspace_from_source(
        ROOT,
        source_dir=args.source,
        dest=args.dest,
        workspace_id=args.workspace_id,
        name=args.name,
        mode=args.mode,
        generated_at=args.generated_at,
        review_threshold=args.review_threshold,
        emit_report=args.emit_report,
        include_runtime_support_assets=args.include_runtime_support_assets,
    )
    print("Adoption Status: completed")
    print(f"Destination: {destination}")
    print(f"Lifecycle Item: {adopted_bundle['item_lifecycle_state']['item_ref']['entity_id']}")
    return 0


def cmd_research_workspace(args: argparse.Namespace) -> int:
    bundle = research_workspace_from_manifest(
        ROOT,
        workspace_dir=_workspace_dir(args),
        manifest_path=args.input_manifest,
        generated_at=args.generated_at,
        persist=not args.no_persist,
    )
    failures = _validate_named_bundle(bundle, RESEARCH_RUNTIME_ARTIFACT_SCHEMAS)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    if args.output_dir:
        _write_artifacts(args.output_dir, bundle, RESEARCH_RUNTIME_ARTIFACTS)
    print(f"Research Sources: {args.input_manifest}")
    print(f"Artifacts Refreshed: {len(bundle)}")
    print(f"Competitor Dossier: {bundle['competitor_dossier']['competitor_dossier_id']}")
    print(f"Customer Pulse: {bundle['customer_pulse']['customer_pulse_id']}")
    print(f"Market Analysis: {bundle['market_analysis_brief']['market_analysis_brief_id']}")
    return 0


def cmd_plan_research(args: argparse.Namespace) -> int:
    bundle = build_external_research_plan_from_workspace(
        ROOT,
        workspace_dir=_workspace_dir(args),
        generated_at=args.generated_at,
        persist=not args.no_persist,
    )
    failures = _validate_named_bundle(bundle, RESEARCH_PLANNING_ARTIFACT_SCHEMAS)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    if args.output_dir:
        _write_artifacts(args.output_dir, bundle, RESEARCH_PLANNING_ARTIFACTS)
    plan = bundle["external_research_plan"]
    print(f"Research Plan: {plan['external_research_plan_id']}")
    print(f"Planned Questions: {len(plan['prioritized_questions'])}")
    print(f"Suggested Sources: {len(plan['suggested_manifest_sources'])}")
    print(f"Next Step: {plan['coverage_summary']['recommended_next_step']}")
    return 0


def cmd_init_feed_registry(args: argparse.Namespace) -> int:
    bundle = build_external_research_feed_registry_from_workspace(
        ROOT,
        workspace_dir=_workspace_dir(args),
        generated_at=args.generated_at,
        persist=not args.no_persist,
    )
    failures = _validate_named_bundle(bundle, RESEARCH_FEED_REGISTRY_ARTIFACT_SCHEMAS)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    if args.output_dir:
        _write_artifacts(args.output_dir, bundle, RESEARCH_FEED_REGISTRY_ARTIFACTS)
    registry = bundle["external_research_feed_registry"]
    print(f"Feed Registry: {registry['external_research_feed_registry_id']}")
    print(f"Registered Feeds: {len(registry['feeds'])}")
    return 0


def cmd_discover_research_sources(args: argparse.Namespace) -> int:
    bundle = discover_external_research_sources_from_workspace(
        ROOT,
        workspace_dir=_workspace_dir(args),
        generated_at=args.generated_at,
        persist=not args.no_persist,
        search_result_limit=args.search_result_limit,
        search_fixture_dir=args.search_fixture_dir,
        search_provider_chain=args.search_provider_chain,
        feed_registry_path=args.feed_registry_path,
    )
    failures = _validate_named_bundle(bundle, RESEARCH_DISCOVERY_ARTIFACT_SCHEMAS)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    if args.output_dir:
        _write_artifacts(args.output_dir, bundle, RESEARCH_DISCOVERY_ARTIFACTS)
    discovery = bundle["external_research_source_discovery"]
    print(f"Source Discovery: {discovery['external_research_source_discovery_id']}")
    print(f"Search Provider: {discovery['search_provider']}")
    print(f"Search Status: {discovery['search_status']}")
    print(f"Candidate Sources: {len(discovery['candidate_sources'])}")
    return 0


def cmd_run_research_loop(args: argparse.Namespace) -> int:
    bundle, summary = run_external_research_loop_from_workspace(
        ROOT,
        workspace_dir=_workspace_dir(args),
        generated_at=args.generated_at,
        persist=not args.no_persist,
        search_result_limit=args.search_result_limit,
        search_fixture_dir=args.search_fixture_dir,
        search_provider_chain=args.search_provider_chain,
        feed_registry_path=args.feed_registry_path,
    )
    for schema_map in (
        RESEARCH_PLANNING_ARTIFACT_SCHEMAS,
        RESEARCH_DISCOVERY_ARTIFACT_SCHEMAS,
        RESEARCH_RUNTIME_ARTIFACT_SCHEMAS if summary["refresh_status"] == "completed" else {},
    ):
        failures = _validate_named_bundle(bundle, schema_map) if schema_map else []
        if failures:
            for failure in failures:
                print(f"FAIL: {failure}")
            return 1
    output_names = list(RESEARCH_PLANNING_ARTIFACTS) + list(RESEARCH_DISCOVERY_ARTIFACTS)
    if summary["refresh_status"] == "completed":
        output_names.extend(RESEARCH_RUNTIME_ARTIFACTS)
    if args.output_dir:
        _write_artifacts(args.output_dir, bundle, output_names)
    print(f"Research Loop Coverage: {summary['coverage_status']}")
    print(f"Research Refresh: {summary['refresh_status']}")
    print(f"Planned Questions: {summary['planned_question_count']}")
    print(f"Candidate Sources: {summary['candidate_source_count']}")
    print(f"Selected Sources: {summary['selected_source_count']}")
    print(f"Review Required: {len(summary['review_items'])}")
    for item in summary["review_items"]:
        print(f"- {item}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ProductOS next-version repo CLI.")
    parser.add_argument("--workspace-dir", type=Path)
    parser.add_argument("--generated-at", default="2026-03-22T08:00:00Z")
    parser.add_argument(
        "--adapter",
        default="codex",
        choices=["codex", "claude", "windsurf", "antigravity"],
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status")
    subparsers.add_parser("review")
    ingest = subparsers.add_parser("ingest")
    ingest.add_argument("--output-dir", type=Path)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("phase", choices=["discover", "align", "operate", "improve", "all"])
    run_parser.add_argument("--output-dir", type=Path)
    run_parser.add_argument("--persist", action="store_true")

    export_parser = subparsers.add_parser("export")
    export_parser.add_argument("--output-dir", type=Path, required=True)

    trace_parser = subparsers.add_parser("trace")
    trace_group = trace_parser.add_mutually_exclusive_group(required=True)
    trace_group.add_argument("--item-id")
    trace_group.add_argument("--stage", choices=["discovery", "delivery", "launch", "outcomes", "full_lifecycle"])

    init_parser = subparsers.add_parser("init-workspace")
    init_parser.add_argument("--template", choices=["templates"], default="templates")
    init_parser.add_argument("--dest", type=Path, required=True)
    init_parser.add_argument("--workspace-id", required=True)
    init_parser.add_argument("--name", required=True)
    init_parser.add_argument("--mode", required=True)

    mission_parser = subparsers.add_parser("init-mission")
    mission_parser.add_argument("--title", required=True)
    mission_parser.add_argument("--target-user", required=True)
    mission_parser.add_argument("--customer-problem", required=True)
    mission_parser.add_argument("--business-goal", required=True)
    mission_parser.add_argument("--success-metric", action="append", required=True)
    mission_parser.add_argument("--constraint", action="append")
    mission_parser.add_argument("--audience", action="append")
    mission_parser.add_argument(
        "--operating-mode",
        choices=["discover", "discover_to_align", "full_loop"],
        default="discover_to_align",
    )

    adopt_parser = subparsers.add_parser("adopt-workspace")
    adopt_parser.add_argument("--source", type=Path, required=True)
    adopt_parser.add_argument("--dest", type=Path, required=True)
    adopt_parser.add_argument("--workspace-id", required=True)
    adopt_parser.add_argument("--name", required=True)
    adopt_parser.add_argument("--mode", required=True)
    adopt_parser.add_argument("--review-threshold", choices=["medium", "high"], default="medium")
    adopt_parser.add_argument("--output-dir", type=Path)
    adopt_parser.add_argument("--dry-run", action="store_true")
    adopt_parser.add_argument("--emit-report", action="store_true")
    adopt_parser.add_argument(
        "--include-runtime-support-assets",
        action="store_true",
        help="Seed internal runtime/example support artifacts for dogfood use instead of creating a customer-clean workspace.",
    )

    research_parser = subparsers.add_parser("research-workspace")
    research_parser.add_argument("--input-manifest", type=Path, required=True)
    research_parser.add_argument("--output-dir", type=Path)
    research_parser.add_argument("--no-persist", action="store_true")

    plan_research_parser = subparsers.add_parser("plan-research")
    plan_research_parser.add_argument("--output-dir", type=Path)
    plan_research_parser.add_argument("--no-persist", action="store_true")

    init_feed_registry_parser = subparsers.add_parser("init-feed-registry")
    init_feed_registry_parser.add_argument("--output-dir", type=Path)
    init_feed_registry_parser.add_argument("--no-persist", action="store_true")

    discover_research_parser = subparsers.add_parser("discover-research-sources")
    discover_research_parser.add_argument("--output-dir", type=Path)
    discover_research_parser.add_argument("--no-persist", action="store_true")
    discover_research_parser.add_argument("--search-result-limit", type=int, default=3)
    discover_research_parser.add_argument("--search-fixture-dir", type=Path)
    discover_research_parser.add_argument("--search-provider-chain")
    discover_research_parser.add_argument("--feed-registry-path", type=Path)

    run_research_parser = subparsers.add_parser("run-research-loop")
    run_research_parser.add_argument("--output-dir", type=Path)
    run_research_parser.add_argument("--no-persist", action="store_true")
    run_research_parser.add_argument("--search-result-limit", type=int, default=3)
    run_research_parser.add_argument("--search-fixture-dir", type=Path)
    run_research_parser.add_argument("--search-provider-chain")
    run_research_parser.add_argument("--feed-registry-path", type=Path)

    subparsers.add_parser("doctor")
    subparsers.add_parser("validate-workspace")
    v5_parser = subparsers.add_parser("v5")
    v5_parser.add_argument("--output-dir", type=Path)
    v6_parser = subparsers.add_parser("v6")
    v6_parser.add_argument("--output-dir", type=Path)
    v7_parser = subparsers.add_parser("v7")
    v7_parser.add_argument("--output-dir", type=Path)
    cutover_parser = subparsers.add_parser("cutover")
    cutover_parser.add_argument("--target-version", default="7.0.0")
    cutover_parser.add_argument("--output-path", type=Path)

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "status":
        return cmd_status(args)
    if args.command == "ingest":
        return cmd_ingest(args)
    if args.command == "run":
        return cmd_run(args)
    if args.command == "review":
        return cmd_review(args)
    if args.command == "export":
        return cmd_export(args)
    if args.command == "trace":
        return cmd_trace(args)
    if args.command == "init-workspace":
        return cmd_init_workspace(args)
    if args.command == "init-mission":
        return cmd_init_mission(args)
    if args.command == "doctor":
        return cmd_doctor(args)
    if args.command == "validate-workspace":
        return cmd_validate_workspace(args)
    if args.command == "adopt-workspace":
        return cmd_adopt_workspace(args)
    if args.command == "research-workspace":
        return cmd_research_workspace(args)
    if args.command == "plan-research":
        return cmd_plan_research(args)
    if args.command == "init-feed-registry":
        return cmd_init_feed_registry(args)
    if args.command == "discover-research-sources":
        return cmd_discover_research_sources(args)
    if args.command == "run-research-loop":
        return cmd_run_research_loop(args)
    if args.command == "v5":
        return cmd_v5(args)
    if args.command == "v6":
        return cmd_v6(args)
    if args.command == "v7":
        return cmd_v7(args)
    if args.command == "cutover":
        return cmd_cutover(args)
    raise AssertionError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
