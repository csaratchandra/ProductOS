#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.python.productos_runtime.release import latest_release_metadata

PLAN_PATH = ROOT / "core" / "docs" / "v10-superpower-plan.md"
MANIFEST_PATH = ROOT / "core" / "docs" / "v10-superpower-manifest.json"
README_PATH = ROOT / "README.md"
CHANGELOG_PATH = ROOT / "CHANGELOG.md"
WORKSPACE_REGISTRATION_PATH = ROOT / "registry" / "workspaces" / "ws_productos_v2.registration.json"
SUITE_REGISTRATION_PATH = ROOT / "registry" / "suites" / "suite_productos.registration.json"
SELF_HOSTING_PATH = ROOT / "internal" / "ProductOS-Next"
SCHEMA_DIR = ROOT / "core" / "schemas" / "artifacts"
EXAMPLE_DIR = ROOT / "core" / "examples" / "artifacts"
SKILL_DIR = ROOT / "core" / "skills"

STANDARD_SKILL_HEADERS_V10 = [
    "1. Purpose",
    "2. Trigger / When To Use",
    "3. Prerequisites",
    "4. Input Specification",
    "5. Execution Steps",
    "6. Output Specification",
    "7. Guardrails",
    "8. Gold Standard Checklist",
    "9. Examples",
    "10. Cross-References",
    "11. Maturity Band Variations",
    "12. Validation Criteria",
]

DEFAULT_EXPECTED_SCHEMAS = [
    "maturity_band_profile",
    "artifact_freshness_state",
    "competitor_radar_state",
    "competitive_intelligence_alert",
    "competitive_feature_matrix",
    "regulatory_change_tracker",
    "pestle_analysis",
    "gold_standard_checklist",
    "persona_narrative_card",
    "empathy_map",
    "customer_journey_map",
    "user_journey_map",
    "decision_analysis",
    "pricing_analysis",
    "hypothesis_portfolio",
    "roadmap_scenario",
    "capacity_model",
    "win_loss_analysis",
    "experiment_design",
    "api_contract",
    "developer_handoff_pack",
    "design_token_set",
    "prototype_generation_plan",
    "prototype_comparison_matrix",
    "prototype_quality_report",
    "prototype_user_test_kit",
    "prototype_annotation",
    "story_map",
    "data_model_impact",
    "rollout_strategy",
    "help_manual_pack",
    "messaging_house",
    "battle_card",
    "blog_post_brief",
    "email_sequence",
    "social_media_pack",
    "investor_pitch_deck",
    "investor_memo",
    "demo_video_script",
    "one_pager",
    "stakeholder_map",
    "meeting_brief",
    "objection_playbook",
    "alignment_dashboard_state",
    "feedback_capture",
    "drift_detection_alert",
    "impact_propagation_map",
    "cohort_analysis",
    "funnel_analysis",
    "feature_adoption_report",
    "churn_prediction",
]

DEFAULT_EXPECTED_SKILLS = [
    "persona_evidence_synthesis",
    "competitive_radar_scan",
    "competitive_shift_analysis",
    "weak_signal_detection",
    "market_trend_extrapolation",
    "pestle_synthesis",
    "persona_narrative_generation",
    "empathy_map_generation",
    "customer_journey_synthesis",
    "user_journey_screen_flow",
    "trade_off_analysis",
    "decision_tree_construction",
    "sensitivity_analysis",
    "premortem_analysis",
    "pricing_analysis_synthesis",
    "pricing_model_design",
    "hypothesis_portfolio_management",
    "roadmap_scenario_generation",
    "capacity_vs_scope_modeling",
    "win_loss_pattern_detection",
    "experiment_design",
    "api_contract_generation",
    "non_functional_requirement_extraction",
    "prototype_html_generation",
    "prototype_quality_evaluation",
    "story_map_generation",
    "help_manual_generation",
    "messaging_house_construction",
    "battle_card_generation",
    "investor_content_generation",
    "stakeholder_management",
    "freshness_and_staleness_scan",
    "drift_and_impact_propagation",
    "health_dashboard_build",
]

PLAN_PLACEHOLDERS = [
    "`prototype_html_generation`, `prototype_quality_evaluation` + 2 more",
    "`story_map_generation`, `help_manual_generation` + 2 more",
    "`messaging_house_construction`, `battle_card_generation`, `investor_content_generation` + 3 more",
    "`cohort_analysis`, `funnel_analysis`, `feature_adoption_report`, `churn_prediction`, health dashboard panels",
    "`health_dashboard_build` + analytics skills",
    "Blueprint trace matrix",
    "Feature scorecards for all capabilities",
]

DEFAULT_TARGETED_TESTS = [
    "tests/test_skill_consistency.py",
    "tests/test_artifact_schemas.py",
    "tests/test_v9_lifecycle_bundle.py",
]


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_scope_manifest(manifest_path: Path | None) -> dict:
    if manifest_path is None or not manifest_path.exists():
        return {
            "scope_source": "built_in_defaults",
            "manifest_path": str(manifest_path.relative_to(ROOT)) if manifest_path is not None else None,
            "target_version": "10.0.0",
            "plan_path": str(PLAN_PATH.relative_to(ROOT)),
            "treat_plan_drift_as_blocking": True,
            "named_schemas": list(DEFAULT_EXPECTED_SCHEMAS),
            "named_skills": list(DEFAULT_EXPECTED_SKILLS),
            "targeted_tests": list(DEFAULT_TARGETED_TESTS),
        }

    payload = _load_json(manifest_path)
    payload["scope_source"] = "manifest"
    payload["manifest_path"] = str(manifest_path.relative_to(ROOT))
    payload.setdefault("target_version", "10.0.0")
    payload.setdefault("plan_path", str(PLAN_PATH.relative_to(ROOT)))
    payload.setdefault("treat_plan_drift_as_blocking", False)
    payload.setdefault("named_schemas", list(DEFAULT_EXPECTED_SCHEMAS))
    payload.setdefault("named_skills", list(DEFAULT_EXPECTED_SKILLS))
    payload.setdefault("targeted_tests", list(DEFAULT_TARGETED_TESTS))
    return payload


def _run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=False)


def _git_index() -> tuple[set[str], dict[str, str]]:
    tracked_result = _run_command(["git", "ls-files"])
    tracked = {
        line.strip()
        for line in tracked_result.stdout.splitlines()
        if line.strip()
    }
    status_result = _run_command(["git", "status", "--short"])
    status_map: dict[str, str] = {}
    for line in status_result.stdout.splitlines():
        if len(line) < 4:
            continue
        status = line[:2]
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        status_map[path] = status
    return tracked, status_map


TRACKED_FILES, GIT_STATUS = _git_index()


def _git_state(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if not path.exists():
        return "missing"
    status = GIT_STATUS.get(rel)
    if status == "??":
        return "untracked"
    current = Path(rel)
    for parent in current.parents:
        if str(parent) == ".":
            continue
        parent_key = parent.as_posix().rstrip("/") + "/"
        if GIT_STATUS.get(parent_key) == "??":
            return "untracked"
    if rel in TRACKED_FILES:
        if status is None:
            return "tracked_clean"
        return f"tracked_dirty:{status.strip()}"
    return "present_not_indexed"


def _readme_stable_version(text: str) -> str | None:
    match = re.search(r"ProductOS V(\d+\.\d+\.\d+) is the current stable ProductOS Core line\.", text)
    return match.group(1) if match else None


def _changelog_latest_version(text: str) -> str | None:
    match = re.search(r"^## V(\d+\.\d+\.\d+) ", text, re.MULTILINE)
    return match.group(1) if match else None


def _skill_headers(text: str) -> list[str]:
    return re.findall(r"^##\s+(.+)$", text, re.MULTILINE)


def _skill_test_refs(text: str) -> list[str]:
    refs = re.findall(r"`(tests/[^`]+\.py)`", text)
    deduped: list[str] = []
    seen: set[str] = set()
    for ref in refs:
        if ref not in seen:
            deduped.append(ref)
            seen.add(ref)
    return deduped


def _collect_plan_findings(plan_text: str) -> list[str]:
    findings: list[str] = []
    if "Status: **Complete**" in plan_text and "### Remaining (Sprints 11-20)" in plan_text:
        findings.append("Plan says `Status: Complete` while also listing `Remaining (Sprints 11-20)`.")
    for placeholder in PLAN_PLACEHOLDERS:
        if placeholder in plan_text:
            findings.append(f"Plan still contains unresolved placeholder scope: `{placeholder}`.")
    return findings


def _collect_schema_results(expected_schemas: list[str]) -> tuple[list[dict], list[str]]:
    rows: list[dict] = []
    blockers: list[str] = []
    for name in expected_schemas:
        schema_path = SCHEMA_DIR / f"{name}.schema.json"
        example_path = EXAMPLE_DIR / f"{name}.example.json"
        schema_exists = schema_path.exists()
        example_exists = example_path.exists()
        row = {
            "name": name,
            "schema_exists": schema_exists,
            "example_exists": example_exists,
            "schema_git_state": _git_state(schema_path),
            "example_git_state": _git_state(example_path),
        }
        rows.append(row)
        if not schema_exists:
            blockers.append(f"Missing schema: `{name}`.")
        if schema_exists and not example_exists:
            blockers.append(f"Missing example for schema: `{name}`.")
    return rows, blockers


def _collect_skill_results(expected_skills: list[str]) -> tuple[list[dict], list[str]]:
    rows: list[dict] = []
    blockers: list[str] = []
    for name in expected_skills:
        skill_path = SKILL_DIR / name / "SKILL.md"
        exists = skill_path.exists()
        row = {
            "name": name,
            "exists": exists,
            "git_state": _git_state(skill_path),
            "headers_match": False,
            "missing_test_refs": [],
            "declares_to_be_created": False,
        }
        if not exists:
            blockers.append(f"Missing skill: `{name}`.")
            rows.append(row)
            continue
        text = _read_text(skill_path)
        headers = _skill_headers(text)
        row["headers_match"] = headers == STANDARD_SKILL_HEADERS_V10
        test_refs = _skill_test_refs(text)
        missing_test_refs = [
            ref for ref in test_refs if not (ROOT / ref).exists()
        ]
        row["missing_test_refs"] = missing_test_refs
        row["declares_to_be_created"] = "to be created" in text.lower()
        if not row["headers_match"]:
            blockers.append(f"Skill does not follow V10 12-section contract: `{name}`.")
        if missing_test_refs:
            blockers.append(
                f"Skill references missing tests: `{name}` -> {', '.join(f'`{ref}`' for ref in missing_test_refs)}."
            )
        rows.append(row)
    return rows, blockers


def _collect_release_findings(target_version: str) -> tuple[dict, list[str]]:
    latest_release = latest_release_metadata(ROOT)
    latest_version = latest_release["core_version"]
    readme_text = _read_text(README_PATH)
    changelog_text = _read_text(CHANGELOG_PATH)
    workspace_payload = _load_json(WORKSPACE_REGISTRATION_PATH)
    suite_payload = _load_json(SUITE_REGISTRATION_PATH)
    readme_version = _readme_stable_version(readme_text)
    changelog_version = _changelog_latest_version(changelog_text)
    findings: list[str] = []

    if latest_version != target_version:
        findings.append(
            f"Latest release metadata is `V{latest_version}` while the V10 manifest targets `V{target_version}`."
        )
    if readme_version != target_version:
        findings.append(
            f"README stable line is `V{readme_version}` while the V10 manifest targets `V{target_version}`."
        )
    if workspace_payload["current_core_version"] != target_version:
        findings.append(
            "Workspace registration remains on "
            f"`V{workspace_payload['current_core_version']}` while the V10 manifest targets `V{target_version}`."
        )
    if suite_payload["current_core_version"] != target_version:
        findings.append(
            "Suite registration remains on "
            f"`V{suite_payload['current_core_version']}` while the V10 manifest targets `V{target_version}`."
        )
    if changelog_version != target_version:
        findings.append(
            f"CHANGELOG latest section is `V{changelog_version}` while the V10 manifest targets `V{target_version}`."
        )
    release_record_state = _git_state(ROOT / "registry" / "releases" / "release_10_0_0.json")
    if release_record_state in {"missing", "untracked", "present_not_indexed"}:
        findings.append(
            "The `V10.0.0` release record is not part of the tracked repo state."
        )

    return {
        "target_version": target_version,
        "latest_version": latest_version,
        "readme_version": readme_version,
        "changelog_version": changelog_version,
        "workspace_version": workspace_payload["current_core_version"],
        "suite_version": suite_payload["current_core_version"],
        "release_record_git_state": release_record_state,
        "readme_git_state": _git_state(README_PATH),
        "changelog_git_state": _git_state(CHANGELOG_PATH),
        "workspace_git_state": _git_state(WORKSPACE_REGISTRATION_PATH),
        "suite_git_state": _git_state(SUITE_REGISTRATION_PATH),
        "self_hosting_exists": SELF_HOSTING_PATH.exists(),
    }, findings


def _run_targeted_tests(targeted_tests: list[str]) -> dict:
    result = _run_command(["pytest", "-q", *targeted_tests])
    combined_output = (result.stdout + result.stderr).strip()
    failure_snippet = ""
    if result.returncode != 0:
        lines = combined_output.splitlines()
        failure_snippet = "\n".join(lines[-20:])
    return {
        "command": "pytest -q " + " ".join(targeted_tests),
        "returncode": result.returncode,
        "passed": result.returncode == 0,
        "output": combined_output,
        "failure_snippet": failure_snippet,
    }


def build_audit_report(
    run_tests: bool,
    *,
    manifest_path: Path | None = MANIFEST_PATH,
    strict_plan_sync: bool = False,
) -> dict:
    manifest = _load_scope_manifest(manifest_path)
    plan_text = _read_text(ROOT / manifest["plan_path"])
    plan_findings = _collect_plan_findings(plan_text)
    schema_rows, schema_findings = _collect_schema_results(manifest["named_schemas"])
    skill_rows, skill_findings = _collect_skill_results(manifest["named_skills"])
    release_state, release_findings = _collect_release_findings(manifest["target_version"])
    test_state = _run_targeted_tests(manifest["targeted_tests"]) if run_tests else None

    untracked_named_paths = []
    for row in schema_rows:
        if row["schema_git_state"] == "untracked":
            untracked_named_paths.append(f"core/schemas/artifacts/{row['name']}.schema.json")
        if row["example_git_state"] == "untracked":
            untracked_named_paths.append(f"core/examples/artifacts/{row['name']}.example.json")
    for row in skill_rows:
        if row["git_state"] == "untracked":
            untracked_named_paths.append(f"core/skills/{row['name']}/SKILL.md")

    findings = {
        "scope_manifest": [],
        "schemas": schema_findings,
        "skills": skill_findings,
        "release": release_findings,
        "tests": [],
    }
    advisories = {
        "plan_sync": [],
    }

    if manifest["scope_source"] != "manifest":
        findings["scope_manifest"].append(
            "Scope manifest is missing, so the audit is falling back to built-in defaults."
        )
    elif plan_findings:
        if strict_plan_sync or manifest.get("treat_plan_drift_as_blocking", False):
            findings["scope_manifest"].extend(plan_findings)
        else:
            advisories["plan_sync"].extend(plan_findings)

    if test_state is not None and not test_state["passed"]:
        findings["tests"].append(
            f"Targeted validation command failed: `{test_state['command']}`."
        )

    schema_complete = sum(1 for row in schema_rows if row["schema_exists"] and row["example_exists"])
    skill_complete = sum(1 for row in skill_rows if row["exists"])
    missing_skill_test_refs = [
        row for row in skill_rows if row["missing_test_refs"]
    ]

    return {
        "generated_at": _utc_now(),
        "summary": {
            "scope_source": manifest["scope_source"],
            "named_schema_count": len(manifest["named_schemas"]),
            "named_schema_complete_count": schema_complete,
            "named_skill_count": len(manifest["named_skills"]),
            "named_skill_complete_count": skill_complete,
            "skills_with_missing_test_refs": len(missing_skill_test_refs),
            "plan_has_blockers": bool(findings["scope_manifest"]),
            "plan_has_advisories": bool(advisories["plan_sync"]),
            "release_has_blockers": bool(release_findings),
            "tests_passed": test_state["passed"] if test_state is not None else None,
            "untracked_named_path_count": len(untracked_named_paths),
        },
        "manifest": manifest,
        "schema_rows": schema_rows,
        "skill_rows": skill_rows,
        "release_state": release_state,
        "test_state": test_state,
        "findings": findings,
        "advisories": advisories,
        "untracked_named_paths": sorted(untracked_named_paths),
    }


def _render_bullets(items: list[str]) -> list[str]:
    if not items:
        return ["- None"]
    return [f"- {item}" for item in items]


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    manifest = report["manifest"]
    release_state = report["release_state"]
    test_state = report["test_state"]
    lines = [
        "# V10 Implementation Audit",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "## Verdict",
        "",
    ]

    verdict_parts: list[str] = []
    if summary["plan_has_blockers"]:
        verdict_parts.append("scope manifest and plan are out of sync in a blocking way")
    if summary["release_has_blockers"]:
        verdict_parts.append("release-proof surfaces are inconsistent")
    if test_state is not None and not test_state["passed"]:
        verdict_parts.append("targeted validation is failing")
    if summary["named_schema_complete_count"] != summary["named_schema_count"]:
        verdict_parts.append("some named schemas are missing")
    if summary["named_skill_complete_count"] != summary["named_skill_count"]:
        verdict_parts.append("some named skills are missing")
    if summary["skills_with_missing_test_refs"]:
        verdict_parts.append("multiple skills reference nonexistent tests")
    if summary["untracked_named_path_count"]:
        verdict_parts.append("some named V10 files are still untracked")

    if verdict_parts:
        lines.append("- V10 cannot be verified as fully implemented in the current repo state.")
        for part in verdict_parts:
            lines.append(f"- Blocking reason: {part}.")
    else:
        lines.append("- V10 is fully implemented and release-proof in the current repo state.")

    lines.extend(
        [
            "",
            "## Snapshot",
            "",
            f"- Scope source: `{summary['scope_source']}`",
            f"- Scope manifest: `{manifest['manifest_path']}`",
            f"- Target version: `V{release_state['target_version']}`",
            f"- Named schemas complete: `{summary['named_schema_complete_count']}/{summary['named_schema_count']}`",
            f"- Named skills present: `{summary['named_skill_complete_count']}/{summary['named_skill_count']}`",
            f"- Skills with missing test refs: `{summary['skills_with_missing_test_refs']}`",
            f"- Untracked named V10 paths: `{summary['untracked_named_path_count']}`",
            f"- Latest release metadata: `V{release_state['latest_version']}`",
            f"- README stable line: `V{release_state['readme_version']}`",
            f"- Workspace registration: `V{release_state['workspace_version']}`",
            f"- Suite registration: `V{release_state['suite_version']}`",
        ]
    )
    if test_state is not None:
        lines.append(f"- Targeted validation: `{'passed' if test_state['passed'] else 'failed'}`")

    lines.extend(
        [
            "",
            "## Findings",
            "",
            "### Scope Manifest",
            "",
            *_render_bullets(report["findings"]["scope_manifest"]),
            "",
            "### Plan Drift",
            "",
            *_render_bullets(report["advisories"]["plan_sync"]),
            "",
            "### Release Proof",
            "",
            *_render_bullets(report["findings"]["release"]),
            "",
            "### Schemas",
            "",
            *_render_bullets(report["findings"]["schemas"]),
            "",
            "### Skills",
            "",
            *_render_bullets(report["findings"]["skills"]),
            "",
            "### Validation",
            "",
            *_render_bullets(report["findings"]["tests"]),
        ]
    )

    if test_state is not None and test_state["failure_snippet"]:
        lines.extend(
            [
                "",
                "```text",
                test_state["failure_snippet"],
                "```",
            ]
        )

    if report["untracked_named_paths"]:
        lines.extend(
            [
                "",
                "## Untracked Named Paths",
                "",
            ]
        )
        lines.extend(_render_bullets([f"`{path}`" for path in report["untracked_named_paths"]]))

    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit ProductOS V10 plan coverage and release-proof consistency."
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format.",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip targeted pytest validation during the audit.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=MANIFEST_PATH,
        help="Optional scope manifest path. Defaults to core/docs/v10-superpower-manifest.json.",
    )
    parser.add_argument(
        "--strict-plan-sync",
        action="store_true",
        help="Treat drift between the prose plan and the scope manifest as a blocking failure.",
    )
    parser.add_argument(
        "--write-report",
        type=Path,
        help="Optional file path to write the rendered report.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_audit_report(
        run_tests=not args.skip_tests,
        manifest_path=args.manifest,
        strict_plan_sync=args.strict_plan_sync,
    )
    if args.format == "json":
        rendered = json.dumps(report, indent=2) + "\n"
    else:
        rendered = render_markdown(report)
    if args.write_report is not None:
        output_path = args.write_report
        if not output_path.is_absolute():
            output_path = ROOT / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
    sys.stdout.write(rendered)

    findings = report["findings"]
    has_blockers = any(findings[key] for key in findings)
    return 1 if has_blockers else 0


if __name__ == "__main__":
    raise SystemExit(main())
