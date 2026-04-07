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
    build_next_version_bundle_from_workspace,
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
    summarize_v5_lifecycle_bundle,
    summarize_v6_lifecycle_bundle,
    summarize_v7_lifecycle_bundle,
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
        "improve_execution_session_state",
        "improve_improvement_loop_state",
        "adapter_parity_report",
        "market_refresh_report",
        "self_improvement_feature_scorecard",
        "feature_portfolio_review",
    ],
    "all": list(NEXT_VERSION_ARTIFACT_SCHEMAS.keys()),
}


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


def _write_artifacts(output_dir: Path, bundle: dict[str, dict], names: list[str]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for name in names:
        with (output_dir / f"{name}.json").open("w", encoding="utf-8") as handle:
            json.dump(bundle[name], handle, indent=2)
            handle.write("\n")


def _promotion_gate(bundle: dict[str, dict]) -> dict[str, object]:
    return evaluate_promotion_gate(
        eval_run_report=bundle["eval_run_report"],
        feature_portfolio_review=bundle["feature_portfolio_review"],
    )


def cmd_status(args: argparse.Namespace) -> int:
    bundle = _build_bundle(args)
    cockpit = bundle["cockpit_state"]
    review = bundle["feature_portfolio_review"]
    eval_report = bundle["eval_run_report"]
    gate = _promotion_gate(bundle)
    cutover_plan = build_v6_cutover_plan_from_workspace(
        _workspace_dir(args),
        generated_at=args.generated_at,
    )
    if cutover_plan["selection_status"] == "stable_active":
        cutover_plan = build_v7_cutover_plan_from_workspace(
            _workspace_dir(args),
            generated_at=args.generated_at,
        )
    focus = cockpit["current_focus"]
    top_priority_feature = review["top_priority_feature_id"]
    if cutover_plan["selection_status"] == "stable_active" and cutover_plan["target_version"] == "7.0.0":
        focus = "Keep ProductOS V7.0.0 stable for lifecycle traceability through outcome_review and prepare the next external publication slice."
        top_priority_feature = cutover_plan["top_priority_feature_id"]
    elif cutover_plan["selection_status"] == "stable_active":
        focus = "Keep ProductOS V6.0.0 stable for lifecycle traceability through release_readiness and prepare the next bounded lifecycle expansion."
        top_priority_feature = cutover_plan["top_priority_feature_id"]
    print(f"Mode: {cockpit['mode']}")
    print(f"Status: {cockpit['status']}")
    print(f"Focus: {focus}")
    print(f"Top Priority Feature: {top_priority_feature}")
    print(f"Truthfulness Status: {review['truthfulness_status']}")
    print(f"Eval Status: {eval_report['status']} ({eval_report['regression_count']} regressions)")
    print(f"Stable Promotion: {gate['status']}")
    if gate["blockers"]:
        print("Promotion Blockers:")
        for blocker in gate["blockers"]:
            print(f"- {blocker}")
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
    names = PHASE_ARTIFACTS[args.phase]
    if args.output_dir:
        _write_artifacts(args.output_dir, bundle, names)
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
    cockpit = bundle["cockpit_state"]
    portfolio = bundle["feature_portfolio_review"]
    eval_report = bundle["eval_run_report"]
    gate = _promotion_gate(bundle)
    print("Pending Review Points:")
    for point in cockpit["pending_review_points"]:
        print(f"- {point}")
    print(f"Stable Promotion: {gate['status']}")
    if gate["blockers"]:
        print("Promotion Blockers:")
        for blocker in gate["blockers"]:
            print(f"- {blocker}")
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
    print(f"Exported {len(bundle)} artifacts to {args.output_dir}")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    bundle = _build_bundle(args)
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
    gate = _promotion_gate(bundle)
    cutover_plan = build_v6_cutover_plan_from_workspace(
        _workspace_dir(args),
        generated_at=args.generated_at,
    )
    if cutover_plan["selection_status"] == "stable_active":
        cutover_plan = build_v7_cutover_plan_from_workspace(
            _workspace_dir(args),
            generated_at=args.generated_at,
        )
    top_priority_feature = (
        cutover_plan["top_priority_feature_id"]
        if cutover_plan["selection_status"] == "stable_active"
        else review["top_priority_feature_id"]
    )
    status_label = "healthy" if review["truthfulness_status"] == "healthy" and eval_report["status"] == "passed" else "watch"
    print(f"Bundle Status: {status_label} ({len(bundle)} artifacts validated)")
    print(f"Stable Promotion: {gate['status']}")
    if gate["blockers"]:
        print("Promotion Blockers:")
        for blocker in gate["blockers"]:
            print(f"- {blocker}")
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
    if args.command == "doctor":
        return cmd_doctor(args)
    if args.command == "validate-workspace":
        return cmd_validate_workspace(args)
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
