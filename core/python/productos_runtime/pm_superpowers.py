from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[3]
LIFECYCLE_PHASES = [
    "discovery",
    "validation",
    "delivery",
    "launch",
    "support_learning",
    "improve",
]
MATURITY_BANDS = [
    "zero_to_one",
    "one_to_ten",
    "ten_to_hundred",
    "hundred_to_thousand_plus",
]
PHASE_LABELS = {
    "discovery": "Discovery",
    "validation": "Validation",
    "delivery": "Delivery",
    "launch": "Launch",
    "support_learning": "Support / Learning",
    "improve": "Improve",
}
PHASE_EXPECTED_ARTIFACTS = {
    "discovery": ["mission_brief", "strategy_context_brief", "problem_brief", "research_notebook"],
    "validation": ["experiment_plan", "feedback_capture_log", "success_metric_review"],
    "delivery": ["prd", "story_pack", "acceptance_criteria_set"],
    "launch": ["release_readiness", "release_note", "go_to_market_checklist"],
    "support_learning": ["status_mail", "issue_log", "outcome_review"],
    "improve": ["feature_portfolio_review", "improvement_loop_state", "ralph_fix_plan"],
}
PHASE_TASK_TEMPLATES = {
    "discovery": [
        "Frame the problem in customer language before solution framing expands.",
        "Capture observed evidence and keep every inferred leap explicit.",
        "Build the first PM-visible backlog from the mission, not from generic templates.",
    ],
    "validation": [
        "Turn the riskiest assumptions into one bounded experiment plan.",
        "Define the minimum passing signal before more delivery work starts.",
        "Capture customer feedback in a reusable evidence trail.",
    ],
    "delivery": [
        "Translate the accepted concept into one reviewable PRD and backlog cut.",
        "Keep acceptance criteria and owner lanes explicit.",
        "Stop if execution scope outruns the accepted validation evidence.",
    ],
    "launch": [
        "Generate the launch checklist with segmentation and readiness gates visible.",
        "Keep pricing, packaging, and communications prompts tied to evidence.",
        "Block promotion until release evidence and approval are explicit.",
    ],
    "support_learning": [
        "Define the dashboard, watch metrics, and feedback loops before drift compounds.",
        "Capture support, usage, and rollout learning in one repo trail.",
        "Open a new mission if customer signals contradict launch assumptions.",
    ],
    "improve": [
        "Route observed issues back into a bounded Ralph mission.",
        "Prioritize fixes by evidence strength, PM leverage, and budget posture.",
        "Revalidate before broadening the public claim surface.",
    ],
}
MATURITY_GUIDANCE = {
    "zero_to_one": {
        "discovery": "Prioritize customer pain clarity, segmentation, and hypothesis sharpness over scale optimization.",
        "validation": "Use narrow experiments that prove demand or behavior change quickly.",
        "delivery": "Ship the smallest coherent wedge that creates learning velocity.",
        "launch": "Favor targeted rollout and high-touch feedback collection.",
        "support_learning": "Look for adoption friction and message mismatch before automation.",
        "improve": "Recycle the biggest contradicted assumption into the next mission.",
    },
    "one_to_ten": {
        "discovery": "Balance net-new discovery with repeated workflow and onboarding friction.",
        "validation": "Test activation, retention, and message resonance with small cohorts.",
        "delivery": "Protect focus and sequence work by user-facing leverage.",
        "launch": "Use segmentation and readiness checks to avoid confusing early expansion.",
        "support_learning": "Instrument the highest-friction moments and recurring support themes.",
        "improve": "Prefer changes that strengthen repeatability and trust.",
    },
    "ten_to_hundred": {
        "discovery": "Look for cross-team bottlenecks, adoption blockers, and category differentiation gaps.",
        "validation": "Require evidence that the next move scales across repeatable segments.",
        "delivery": "Keep dependencies, release posture, and execution tradeoffs visible.",
        "launch": "Plan controlled rollout with explicit enablement and communications.",
        "support_learning": "Track expansion quality, reliability, and operational burden.",
        "improve": "Convert repeated operational drag into bounded platform or workflow fixes.",
    },
    "hundred_to_thousand_plus": {
        "discovery": "Treat portfolio coordination, governance, and reliability as first-class product context.",
        "validation": "Validate at segment or market level with strong baseline comparisons.",
        "delivery": "Expose dependencies, approvals, and release risk early.",
        "launch": "Use staged rollout, governance, and measurement by default.",
        "support_learning": "Track large-scale feedback loops, cost posture, and release contradictions.",
        "improve": "Route issues based on enterprise impact, spend, and risk concentration.",
    },
}
DEFAULT_RALPH_STAGE_BY_PHASE = {
    "discovery": "inspect",
    "validation": "validate",
    "delivery": "implement",
    "launch": "validate",
    "support_learning": "revalidate",
    "improve": "refine",
}


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _relative_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return path.as_posix()


def _load_manifest(workspace_path: Path) -> dict[str, Any]:
    manifest_path = workspace_path / "workspace_manifest.yaml"
    if not manifest_path.exists():
        return {}
    return yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}


def _write_manifest(workspace_path: Path, manifest: dict[str, Any]) -> None:
    manifest_path = workspace_path / "workspace_manifest.yaml"
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")


def append_manifest_artifact_path(workspace_path: Path, relative_path: str) -> None:
    manifest = _load_manifest(workspace_path)
    if not manifest:
        return
    artifact_paths = manifest.setdefault("artifact_paths", [])
    if relative_path not in artifact_paths:
        artifact_paths.append(relative_path)
        _write_manifest(workspace_path, manifest)


def append_manifest_feedback_path(workspace_path: Path, relative_path: str) -> None:
    manifest = _load_manifest(workspace_path)
    if not manifest:
        return
    feedback_paths = manifest.setdefault("feedback_paths", [])
    if relative_path not in feedback_paths:
        feedback_paths.append(relative_path)
        _write_manifest(workspace_path, manifest)


def default_primary_outcomes(mission_brief: dict[str, Any]) -> list[str]:
    outcomes = list(mission_brief.get("primary_outcomes") or [])
    if outcomes:
        return outcomes
    return [mission_brief["business_goal"]]


def default_primary_kpis(mission_brief: dict[str, Any]) -> list[str]:
    primary_kpis = list(mission_brief.get("primary_kpis") or [])
    if primary_kpis:
        return primary_kpis
    return list(mission_brief.get("success_metrics") or ["time to reviewable PM package"])


def workspace_identity(workspace_path: Path) -> dict[str, str]:
    manifest = _load_manifest(workspace_path)
    workspace_id = str(manifest.get("workspace_id", "")).strip() or f"ws_{_slug(workspace_path.name)}"
    workspace_name = str(manifest.get("name", "")).strip() or workspace_path.name
    active_increment_id = str(manifest.get("active_increment_id", "")).strip() or "pi_initial_01"
    mode = str(manifest.get("mode", "")).strip() or "startup"
    return {
        "workspace_id": workspace_id,
        "workspace_name": workspace_name,
        "active_increment_id": active_increment_id,
        "mode": mode,
    }


def build_product_record(
    workspace_dir: Path | str,
    *,
    mission_brief: dict[str, Any],
    generated_at: str,
    lifecycle_phase: str = "discovery",
) -> dict[str, Any]:
    workspace_path = Path(workspace_dir).resolve()
    identity = workspace_identity(workspace_path)
    mission_slug = _slug(mission_brief["title"])
    return {
        "schema_version": "1.0.0",
        "product_record_id": f"product_record_{identity['workspace_id']}",
        "workspace_id": identity["workspace_id"],
        "portfolio_id": mission_brief.get("portfolio_id", identity["workspace_id"]),
        "mission_ref": mission_brief["mission_brief_id"],
        "product_name": identity["workspace_name"],
        "lifecycle_stage": lifecycle_phase,
        "maturity_band": mission_brief.get("maturity_band", "zero_to_one"),
        "status": "on_track",
        "owner": mission_brief.get("review_gate_owner", "ProductOS PM"),
        "review_gate_owner": mission_brief.get("review_gate_owner", "ProductOS PM"),
        "primary_outcomes": default_primary_outcomes(mission_brief),
        "primary_kpis": default_primary_kpis(mission_brief),
        "target_release_or_increment": identity["active_increment_id"],
        "feature_record_ids": [f"feature_record_{mission_slug}_primary"],
        "dependency_ids": [],
        "risk_summary": list(mission_brief.get("known_risks") or ["Discovery assumptions still require product-specific evidence."]),
        "linked_artifact_ids": [mission_brief["mission_brief_id"]],
        "linked_decision_ids": [],
        "approvals": {
            "pm": "pending",
            "leadership": "not_needed",
            "customer_commitment": "not_needed",
            "compliance": "not_needed",
        },
        "last_updated_at": generated_at,
    }


def build_phase_packet(
    workspace_dir: Path | str,
    *,
    mission_brief: dict[str, Any],
    product_record: dict[str, Any],
    lifecycle_phase: str,
    generated_at: str,
) -> dict[str, Any]:
    workspace_path = Path(workspace_dir).resolve()
    identity = workspace_identity(workspace_path)
    maturity_band = mission_brief.get("maturity_band", "zero_to_one")
    mission_slug = _slug(mission_brief["title"])
    guidance = MATURITY_GUIDANCE[maturity_band][lifecycle_phase]
    stage_goals = mission_brief.get("stage_goals") or {}
    phase_goal = stage_goals.get(lifecycle_phase) or guidance
    review_gate_owner = mission_brief.get("review_gate_owner", "ProductOS PM")
    source_refs = [mission_brief["mission_brief_id"], product_record["product_record_id"]]
    question_prompts = [
        f"What is the highest-signal decision the PM needs from {PHASE_LABELS[lifecycle_phase].lower()}?",
        f"Which evidence is observed versus inferred for {mission_brief['title']}?",
        f"How should {maturity_band} defaults change the {PHASE_LABELS[lifecycle_phase].lower()} packet?",
    ]
    task_queue = []
    for index, summary in enumerate(PHASE_TASK_TEMPLATES[lifecycle_phase], start=1):
        task_queue.append(
            {
                "task_id": f"task_{mission_slug}_{lifecycle_phase}_{index:02d}",
                "title": f"{PHASE_LABELS[lifecycle_phase]} task {index}",
                "summary": summary,
                "owner": review_gate_owner,
                "status": "planned",
                "source_artifact_refs": source_refs,
            }
        )
    success_metrics = []
    for metric in default_primary_kpis(mission_brief):
        success_metrics.append(
            {
                "metric_name": metric,
                "target_signal": f"{PHASE_LABELS[lifecycle_phase]} should improve {metric.lower()} without weakening reviewability.",
                "measurement_posture": "observed",
            }
        )
    recommended_pm_actions = [
        {
            "recommendation_id": f"pm_action_{mission_slug}_{lifecycle_phase}",
            "summary": f"Approve the bounded {lifecycle_phase} packet only after the evidence trail and next decision stay legible.",
            "source_artifact_refs": source_refs,
            "observed_vs_inferred": "mixed",
            "assumption_note": "Task content is maturity-aware scaffolding until workspace-specific evidence replaces the starter defaults.",
        }
    ]
    return {
        "schema_version": "1.0.0",
        "phase_packet_id": f"phase_packet_{identity['workspace_id']}_{lifecycle_phase}",
        "workspace_id": identity["workspace_id"],
        "mission_ref": mission_brief["mission_brief_id"],
        "product_record_ref": product_record["product_record_id"],
        "lifecycle_phase": lifecycle_phase,
        "maturity_band": maturity_band,
        "phase_goal": phase_goal,
        "question_prompts": question_prompts,
        "task_queue": task_queue,
        "expected_artifacts": list(PHASE_EXPECTED_ARTIFACTS[lifecycle_phase]),
        "success_metrics": success_metrics,
        "approval_gates": [
            {
                "gate_id": f"approval_gate_{mission_slug}_{lifecycle_phase}",
                "title": f"{PHASE_LABELS[lifecycle_phase]} PM review",
                "owner": review_gate_owner,
                "status": "pending",
                "required_artifact_refs": source_refs,
            }
        ],
        "recommended_pm_actions": recommended_pm_actions,
        "source_artifact_ids": source_refs,
        "created_at": generated_at,
        "updated_at": generated_at,
    }


def format_phase_packet_markdown(phase_packet: dict[str, Any], mission_brief: dict[str, Any]) -> str:
    lines = [
        f"# {PHASE_LABELS[phase_packet['lifecycle_phase']]} Phase Packet",
        "",
        f"Mission: `{mission_brief['title']}`",
        f"Maturity Band: `{phase_packet['maturity_band']}`",
        f"Review Gate Owner: `{mission_brief.get('review_gate_owner', 'ProductOS PM')}`",
        "",
        "## Goal",
        "",
        phase_packet["phase_goal"],
        "",
        "## Questions",
        "",
    ]
    for question in phase_packet["question_prompts"]:
        lines.append(f"- {question}")
    lines.extend(["", "## Tasks", ""])
    for task in phase_packet["task_queue"]:
        lines.append(f"- {task['summary']}")
    lines.extend(["", "## Expected Artifacts", ""])
    for artifact in phase_packet["expected_artifacts"]:
        lines.append(f"- `{artifact}`")
    lines.extend(["", "## Success Metrics", ""])
    for metric in phase_packet["success_metrics"]:
        lines.append(f"- {metric['metric_name']}: {metric['target_signal']}")
    lines.append("")
    return "\n".join(lines)


def _starter_readme(mission_brief: dict[str, Any], product_record: dict[str, Any], phase_packet: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"# {mission_brief['title']}",
            "",
            mission_brief["mission_summary"],
            "",
            f"- Workspace: `{mission_brief['workspace_id']}`",
            f"- Portfolio: `{mission_brief.get('portfolio_id', mission_brief['workspace_id'])}`",
            f"- Maturity band: `{mission_brief.get('maturity_band', 'zero_to_one')}`",
            f"- Lifecycle phase: `{product_record['lifecycle_stage']}`",
            f"- Review gate owner: `{mission_brief.get('review_gate_owner', 'ProductOS PM')}`",
            "",
            "## Primary Outcomes",
            "",
            *[f"- {item}" for item in default_primary_outcomes(mission_brief)],
            "",
            "## Primary KPIs",
            "",
            *[f"- {item}" for item in default_primary_kpis(mission_brief)],
            "",
            "## Next Phase Packet",
            "",
            f"The active phase packet is `{phase_packet['phase_packet_id']}` and should drive the next PM-visible decisions, tasks, and approvals.",
            "",
        ]
    )


def _mission_log_markdown(mission_brief: dict[str, Any], phase_packet: dict[str, Any], generated_at: str) -> str:
    return "\n".join(
        [
            "# Mission Log",
            "",
            f"- Created: `{generated_at}`",
            f"- Mission: `{mission_brief['mission_brief_id']}`",
            f"- Active phase packet: `{phase_packet['phase_packet_id']}`",
            "",
            "## First Entry",
            "",
            f"The workspace was initialized for `{mission_brief['title']}` with `{mission_brief.get('maturity_band', 'zero_to_one')}` defaults and a `{phase_packet['lifecycle_phase']}` packet.",
            "",
        ]
    )


def _discovery_backlog_markdown(phase_packet: dict[str, Any]) -> str:
    lines = ["# Discovery Backlog", "", "## Seeded Tasks", ""]
    for task in phase_packet["task_queue"]:
        lines.append(f"- [ ] {task['summary']}")
    lines.append("")
    return "\n".join(lines)


def seed_pm_superpower_artifacts(
    workspace_dir: Path | str,
    *,
    mission_brief: dict[str, Any],
    generated_at: str,
) -> dict[str, dict[str, Any]]:
    workspace_path = Path(workspace_dir).resolve()
    artifacts_dir = workspace_path / "artifacts"
    planning_dir = workspace_path / "docs" / "planning"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    planning_dir.mkdir(parents=True, exist_ok=True)

    product_record = build_product_record(
        workspace_path,
        mission_brief=mission_brief,
        generated_at=generated_at,
    )
    phase_packet = build_phase_packet(
        workspace_path,
        mission_brief=mission_brief,
        product_record=product_record,
        lifecycle_phase=product_record["lifecycle_stage"],
        generated_at=generated_at,
    )

    product_record["linked_artifact_ids"].append(phase_packet["phase_packet_id"])
    _write_json(artifacts_dir / "product_record.json", product_record)
    _write_json(artifacts_dir / f"phase_packet_{product_record['lifecycle_stage']}.json", phase_packet)
    _write_text(planning_dir / f"phase-packet-{product_record['lifecycle_stage']}.md", format_phase_packet_markdown(phase_packet, mission_brief) + "\n")
    _write_text(planning_dir / "mission-log.md", _mission_log_markdown(mission_brief, phase_packet, generated_at) + "\n")
    if product_record["lifecycle_stage"] == "discovery":
        _write_text(planning_dir / "discovery-backlog.md", _discovery_backlog_markdown(phase_packet) + "\n")

    readme_path = workspace_path / "README.md"
    _write_text(readme_path, _starter_readme(mission_brief, product_record, phase_packet))

    append_manifest_artifact_path(workspace_path, "artifacts/product_record.json")
    append_manifest_artifact_path(workspace_path, f"artifacts/phase_packet_{product_record['lifecycle_stage']}.json")
    append_manifest_feedback_path(workspace_path, "docs/planning/mission-log.md")

    return {
        "product_record": product_record,
        "phase_packet": phase_packet,
    }


def load_product_record_from_workspace(workspace_dir: Path | str) -> dict[str, Any] | None:
    path = Path(workspace_dir).resolve() / "artifacts" / "product_record.json"
    if not path.exists():
        return None
    return _load_json(path)


def load_phase_packet_from_workspace(workspace_dir: Path | str, lifecycle_phase: str | None = None) -> dict[str, Any] | None:
    workspace_path = Path(workspace_dir).resolve()
    if lifecycle_phase is None:
        product_record = load_product_record_from_workspace(workspace_path)
        lifecycle_phase = (
            str(product_record.get("lifecycle_stage", "discovery"))
            if product_record is not None
            else "discovery"
        )
    path = workspace_path / "artifacts" / f"phase_packet_{lifecycle_phase}.json"
    if not path.exists():
        return None
    return _load_json(path)


def write_phase_packet_for_workspace(
    workspace_dir: Path | str,
    *,
    mission_brief: dict[str, Any],
    lifecycle_phase: str,
    generated_at: str,
) -> dict[str, Any]:
    workspace_path = Path(workspace_dir).resolve()
    product_record = load_product_record_from_workspace(workspace_path)
    if product_record is None:
        product_record = build_product_record(
            workspace_path,
            mission_brief=mission_brief,
            generated_at=generated_at,
            lifecycle_phase=lifecycle_phase,
        )
    else:
        product_record["lifecycle_stage"] = lifecycle_phase
        product_record["last_updated_at"] = generated_at
    phase_packet = build_phase_packet(
        workspace_path,
        mission_brief=mission_brief,
        product_record=product_record,
        lifecycle_phase=lifecycle_phase,
        generated_at=generated_at,
    )
    product_record["linked_artifact_ids"] = list(
        dict.fromkeys(
            [
                *product_record.get("linked_artifact_ids", []),
                mission_brief["mission_brief_id"],
                phase_packet["phase_packet_id"],
            ]
        )
    )
    artifacts_dir = workspace_path / "artifacts"
    planning_dir = workspace_path / "docs" / "planning"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    planning_dir.mkdir(parents=True, exist_ok=True)
    _write_json(artifacts_dir / "product_record.json", product_record)
    _write_json(artifacts_dir / f"phase_packet_{lifecycle_phase}.json", phase_packet)
    _write_text(planning_dir / f"phase-packet-{lifecycle_phase}.md", format_phase_packet_markdown(phase_packet, mission_brief) + "\n")
    append_manifest_artifact_path(workspace_path, "artifacts/product_record.json")
    append_manifest_artifact_path(workspace_path, f"artifacts/phase_packet_{lifecycle_phase}.json")
    return phase_packet


def build_workspace_tree_state(
    workspace_dir: Path | str,
    *,
    mission_brief: dict[str, Any],
    product_record: dict[str, Any],
    generated_at: str,
) -> dict[str, Any]:
    workspace_path = Path(workspace_dir).resolve()
    identity = workspace_identity(workspace_path)
    portfolio_id = mission_brief.get("portfolio_id", identity["workspace_id"])
    artifact_paths = sorted((workspace_path / "artifacts").glob("*.json"))
    doc_paths = sorted((workspace_path / "docs").rglob("*.md"))
    mission_node_id = f"tree_node_mission_{identity['workspace_id']}"
    artifact_children = [
        {
            "node_id": f"tree_node_artifact_{path.stem}",
            "node_type": "artifact",
            "label": path.name,
            "ref": _relative_path(path),
            "children": [],
        }
        for path in artifact_paths
    ]
    doc_children = [
        {
            "node_id": f"tree_node_doc_{_slug(str(path.relative_to(workspace_path)))}",
            "node_type": "document",
            "label": str(path.relative_to(workspace_path)),
            "ref": _relative_path(path),
            "children": [],
        }
        for path in doc_paths
    ]
    return {
        "schema_version": "1.0.0",
        "workspace_tree_state_id": f"workspace_tree_state_{identity['workspace_id']}",
        "workspace_id": identity["workspace_id"],
        "portfolio_id": portfolio_id,
        "root": {
            "node_id": f"tree_node_portfolio_{_slug(portfolio_id)}",
            "node_type": "portfolio",
            "label": portfolio_id,
            "children": [
                {
                    "node_id": f"tree_node_workspace_{identity['workspace_id']}",
                    "node_type": "workspace",
                    "label": identity["workspace_name"],
                    "ref": _relative_path(workspace_path),
                    "children": [
                        {
                            "node_id": mission_node_id,
                            "node_type": "mission",
                            "label": mission_brief["title"],
                            "ref": "artifacts/mission_brief.json",
                            "children": [],
                        },
                        {
                            "node_id": f"tree_node_docs_{identity['workspace_id']}",
                            "node_type": "collection",
                            "label": "Docs",
                            "ref": _relative_path(workspace_path / "docs"),
                            "children": doc_children,
                        },
                        {
                            "node_id": f"tree_node_artifacts_{identity['workspace_id']}",
                            "node_type": "collection",
                            "label": "Artifacts",
                            "ref": _relative_path(workspace_path / "artifacts"),
                            "children": artifact_children,
                        },
                    ],
                }
            ],
        },
        "active_mission_ref": mission_brief["mission_brief_id"],
        "active_product_record_ref": product_record["product_record_id"],
        "generated_at": generated_at,
    }


def _build_context_view_refs(workspace_path: Path) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    candidates = [
        ("readme", workspace_path / "README.md", "document"),
        ("mission_brief", workspace_path / "artifacts" / "mission_brief.json", "artifact"),
        ("product_record", workspace_path / "artifacts" / "product_record.json", "artifact"),
        ("strategy_context_brief", workspace_path / "artifacts" / "strategy_context_brief.json", "artifact"),
        ("prd", workspace_path / "artifacts" / "prd.json", "artifact"),
        ("mission_log", workspace_path / "docs" / "planning" / "mission-log.md", "document"),
    ]
    for label, path, ref_type in candidates:
        if not path.exists():
            continue
        refs.append(
            {
                "view_id": f"context_view_{_slug(label)}",
                "label": label.replace("_", " ").title(),
                "ref_type": ref_type,
                "ref_path": _relative_path(path),
            }
        )
    return refs


def _approval_queue(
    *,
    mission_brief: dict[str, Any],
    phase_packet: dict[str, Any],
    next_version_bundle: dict[str, Any],
) -> list[dict[str, Any]]:
    owner = mission_brief.get("review_gate_owner", "ProductOS PM")
    queue = [
        {
            "approval_id": phase_packet["approval_gates"][0]["gate_id"],
            "title": phase_packet["approval_gates"][0]["title"],
            "owner": owner,
            "status": phase_packet["approval_gates"][0]["status"],
            "artifact_refs": list(phase_packet["approval_gates"][0]["required_artifact_refs"]),
        }
    ]
    release_gate = next_version_bundle.get("next_version_release_gate_decision")
    if release_gate is not None:
        queue.append(
            {
                "approval_id": release_gate["release_gate_decision_id"],
                "title": "Release gate decision",
                "owner": owner,
                "status": "approved" if release_gate.get("decision") in {"go", "conditional_go"} else "pending",
                "artifact_refs": [release_gate["release_gate_decision_id"]],
            }
        )
    return queue


def _budget_status(orchestration_state: dict[str, Any], eval_run_report: dict[str, Any]) -> dict[str, Any]:
    route_budget = orchestration_state["route_budget"]
    blocked = eval_run_report.get("regression_count", 0) > 0 or route_budget["blocked_route_count"] > 0
    return {
        "status": "paused" if blocked else "within_threshold",
        "visible_route_count": len(orchestration_state.get("route_plan", [])),
        "review_threshold": route_budget.get("route_review_threshold", 1),
        "pause_threshold": route_budget.get("route_pause_threshold", 2),
        "pause_reason": (
            "Budget posture is paused until regressions clear or blocked routes are resolved."
            if blocked
            else "No route-level budget threshold is currently breached."
        ),
    }


def _recommendation_trace(
    *,
    recommendation_id: str,
    summary: str,
    source_artifact_refs: list[str],
    observed_vs_inferred: str,
    assumption_note: str,
) -> dict[str, Any]:
    return {
        "recommendation_id": recommendation_id,
        "summary": summary,
        "source_artifact_refs": source_artifact_refs,
        "observed_vs_inferred": observed_vs_inferred,
        "assumption_note": assumption_note,
    }


def enrich_runtime_states(
    *,
    mission_brief: dict[str, Any],
    product_record: dict[str, Any],
    phase_packet: dict[str, Any],
    workspace_tree_state: dict[str, Any],
    next_version_bundle: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    cockpit_state = copy.deepcopy(next_version_bundle["cockpit_state"])
    orchestration_state = copy.deepcopy(next_version_bundle["orchestration_state"])
    eval_run_report = next_version_bundle["eval_run_report"]
    route_budget = orchestration_state["route_budget"]
    route_budget.update(
        {
            "route_review_threshold": 1,
            "route_pause_threshold": 2,
            "auto_pause_on_threshold": True,
        }
    )
    approval_checkpoints = []
    for route in orchestration_state.get("route_plan", []):
        route.setdefault("estimated_spend_points", 1)
        route.setdefault("spent_points", 1 if route.get("status") in {"active", "completed", "awaiting_review"} else 0)
        route["budget_status"] = "paused" if route.get("status") == "blocked" else "within_threshold"
        route["pause_reason"] = "Explicit PM approval required before release movement." if route.get("status") == "awaiting_review" else ""
        if route.get("status") in {"awaiting_review", "blocked"}:
            approval_checkpoints.append(
                {
                    "checkpoint_id": f"approval_checkpoint_{route['route_id']}",
                    "route_id": route["route_id"],
                    "title": f"Approve {route['route_id']}",
                    "owner": mission_brief.get("review_gate_owner", "ProductOS PM"),
                    "status": "pending",
                    "required_evidence_refs": list(route.get("expected_output_artifact_ids", []))[:3] or list(route.get("input_artifact_ids", []))[:3],
                    "blocked_reason": route.get("pause_reason") or "Route is waiting on explicit PM review.",
                }
            )
    if eval_run_report.get("regression_count", 0) > 0:
        pause_reasons = [f"{eval_run_report['regression_count']} regression(s) are still open in the frozen eval suite."]
    else:
        pause_reasons = []
    orchestration_state["pause_reasons"] = pause_reasons
    orchestration_state["approval_checkpoints"] = approval_checkpoints

    context_view_refs = _build_context_view_refs((ROOT / mission_brief["source_refs"][0]).parents[1]) if mission_brief.get("source_refs") else []
    if not context_view_refs:
        workspace_dir = ROOT / workspace_tree_state["root"]["children"][0]["ref"]
        context_view_refs = _build_context_view_refs(workspace_dir)
    recommendations = [
        _recommendation_trace(
            recommendation_id=f"recommended_pm_action_{phase_packet['lifecycle_phase']}",
            summary=f"Review the {phase_packet['lifecycle_phase']} packet and decide whether the next phase should open.",
            source_artifact_refs=[phase_packet["phase_packet_id"], mission_brief["mission_brief_id"]],
            observed_vs_inferred="mixed",
            assumption_note="The packet is seeded from repo-native defaults until the workspace replaces them with product-specific evidence.",
        )
    ]
    for item in cockpit_state.get("queue_recommendations", [])[:2]:
        recommendations.append(
            _recommendation_trace(
                recommendation_id=f"queue_action_{item['item_id']}",
                summary=item["why_now"],
                source_artifact_refs=[item["artifact_id"]],
                observed_vs_inferred="observed",
                assumption_note="This trace is derived directly from the current queue recommendation.",
            )
        )

    cockpit_state["ralph_stage"] = DEFAULT_RALPH_STAGE_BY_PHASE.get(product_record["lifecycle_stage"], "inspect")
    cockpit_state["approval_queue"] = _approval_queue(
        mission_brief=mission_brief,
        phase_packet=phase_packet,
        next_version_bundle=next_version_bundle,
    )
    cockpit_state["budget_status"] = _budget_status(orchestration_state, eval_run_report)
    cockpit_state["workspace_tree_ref"] = workspace_tree_state["workspace_tree_state_id"]
    cockpit_state["context_view_refs"] = context_view_refs
    cockpit_state["recommended_pm_actions"] = recommendations
    cockpit_state["source_artifact_ids"] = list(
        dict.fromkeys(
            [
                workspace_tree_state["workspace_tree_state_id"],
                phase_packet["phase_packet_id"],
                product_record["product_record_id"],
                *cockpit_state.get("source_artifact_ids", []),
            ]
        )
    )
    return cockpit_state, orchestration_state


def build_cross_product_insight_index(
    workspace_dirs: list[Path | str],
    *,
    generated_at: str,
    portfolio_id: str | None = None,
) -> dict[str, Any]:
    insights = []
    resolved_paths = [Path(path).resolve() for path in workspace_dirs]
    inferred_portfolio_id = portfolio_id
    for workspace_path in resolved_paths:
        mission_path = workspace_path / "artifacts" / "mission_brief.json"
        product_path = workspace_path / "artifacts" / "product_record.json"
        if not mission_path.exists():
            continue
        mission_brief = _load_json(mission_path)
        product_record = (
            _load_json(product_path)
            if product_path.exists()
            else build_product_record(workspace_path, mission_brief=mission_brief, generated_at=generated_at)
        )
        inferred_portfolio_id = inferred_portfolio_id or mission_brief.get("portfolio_id") or product_record.get("portfolio_id")
        insight_tags = [
            mission_brief.get("maturity_band", "zero_to_one"),
            product_record.get("lifecycle_stage", "discovery"),
            "pm_superpower",
        ]
        insights.append(
            {
                "insight_id": f"insight_{product_record['workspace_id']}",
                "workspace_id": product_record["workspace_id"],
                "mission_ref": mission_brief["mission_brief_id"],
                "title": f"Reuse signals from {mission_brief['title']}",
                "summary": f"{mission_brief['title']} already captures a bounded mission, explicit KPIs, and a review owner for the current workspace.",
                "tags": insight_tags,
                "observed_vs_inferred": "observed",
                "evidence_refs": [mission_brief["mission_brief_id"], product_record["product_record_id"]],
                "reusable_recommendation": "Reuse the mission intake, KPI framing, and approval posture before opening a parallel workspace flow.",
            }
        )
    return {
        "schema_version": "1.0.0",
        "cross_product_insight_index_id": f"cross_product_insight_index_{_slug(inferred_portfolio_id or 'workspace_portfolio')}",
        "portfolio_id": inferred_portfolio_id or "workspace_portfolio",
        "insights": insights or [
            {
                "insight_id": "insight_seeded_defaults",
                "workspace_id": "unknown",
                "mission_ref": "unknown",
                "title": "Seeded mission defaults still need workspace evidence",
                "summary": "No workspace-level product record was available, so only the starter cross-product scaffold could be generated.",
                "tags": ["seeded", "pm_superpower"],
                "observed_vs_inferred": "inferred",
                "evidence_refs": [],
                "reusable_recommendation": "Create a mission brief and product record before relying on cross-product reuse suggestions.",
            }
        ],
        "generated_at": generated_at,
    }


def build_portfolio_state_from_workspaces(
    workspace_dirs: list[Path | str],
    *,
    generated_at: str,
    suite_id: str | None = None,
) -> dict[str, Any]:
    product_summaries = []
    primary_outcomes: list[str] = []
    primary_kpis: list[str] = []
    portfolio_risks: list[str] = []
    review_gate_owner = "Portfolio PM"
    resolved_paths = [Path(path).resolve() for path in workspace_dirs]
    for workspace_path in resolved_paths:
        mission_path = workspace_path / "artifacts" / "mission_brief.json"
        product_path = workspace_path / "artifacts" / "product_record.json"
        if not mission_path.exists():
            portfolio_risks.append(f"Workspace '{workspace_path.name}' is missing mission or product state.")
            continue
        mission_brief = _load_json(mission_path)
        product_record = (
            _load_json(product_path)
            if product_path.exists()
            else build_product_record(workspace_path, mission_brief=mission_brief, generated_at=generated_at)
        )
        product_summaries.append(
            {
                "product_record_id": product_record["product_record_id"],
                "workspace_id": product_record["workspace_id"],
                "product_name": product_record["product_name"],
                "lifecycle_stage": product_record["lifecycle_stage"],
                "maturity_band": product_record["maturity_band"],
                "status": product_record["status"],
                "owner": product_record["owner"],
                "review_gate_owner": product_record["review_gate_owner"],
                "target_release_or_increment": product_record["target_release_or_increment"],
                "feature_count": len(product_record.get("feature_record_ids", [])),
                "primary_outcomes": list(product_record.get("primary_outcomes", [])),
                "primary_kpis": list(product_record.get("primary_kpis", [])),
                "top_mission_title": mission_brief["title"],
                "next_approval_needed": f"{product_record['lifecycle_stage']} PM review",
            }
        )
        primary_outcomes.extend(product_record.get("primary_outcomes", []))
        primary_kpis.extend(product_record.get("primary_kpis", []))
        review_gate_owner = product_record.get("review_gate_owner", review_gate_owner)
    normalized_suite_id = suite_id or (product_summaries[0]["workspace_id"] if product_summaries else "workspace_portfolio")
    summary = (
        f"The portfolio currently tracks {len(product_summaries)} workspace(s) through one mission-first PM control plane."
        if product_summaries
        else "No valid workspace product records were available for the portfolio rollup."
    )
    return {
        "schema_version": "1.0.0",
        "portfolio_state_id": f"portfolio_state_{_slug(normalized_suite_id)}",
        "suite_id": normalized_suite_id,
        "review_gate_owner": review_gate_owner,
        "primary_outcomes": list(dict.fromkeys(primary_outcomes)) or ["Establish one mission-first PM control plane."],
        "primary_kpis": list(dict.fromkeys(primary_kpis)) or ["time to reviewable PM package"],
        "summary": summary,
        "product_summaries": product_summaries or [
            {
                "product_record_id": "product_record_missing",
                "workspace_id": "unknown",
                "product_name": "Unknown workspace",
                "lifecycle_stage": "discovery",
                "maturity_band": "zero_to_one",
                "status": "blocked",
                "owner": "Portfolio PM",
                "review_gate_owner": "Portfolio PM",
                "target_release_or_increment": "pi_initial_01",
                "feature_count": 0,
                "primary_outcomes": ["Create the first valid product record."],
                "primary_kpis": ["artifact completeness"],
                "top_mission_title": "Missing mission brief",
                "next_approval_needed": "Initialize workspace state",
            }
        ],
        "opportunity_portfolio_summary": [],
        "cross_product_dependencies": [],
        "portfolio_risks": list(dict.fromkeys(portfolio_risks)),
        "generated_at": generated_at,
    }


def summarize_research_posture(bundle: dict[str, Any]) -> dict[str, Any]:
    research_plan = bundle.get("external_research_plan") or bundle.get("discover_external_research_plan") or {}
    source_discovery = bundle.get("external_research_source_discovery") or bundle.get("discover_external_research_source_discovery") or {}
    selected_manifest = bundle.get("external_research_selected_manifest") or bundle.get("discover_selected_research_manifest") or {}
    review = bundle.get("external_research_review") or bundle.get("discover_external_research_review") or {}
    feed_registry = bundle.get("external_research_feed_registry") or {}

    question_count = len(research_plan.get("prioritized_questions", [])) if isinstance(research_plan, dict) else 0
    candidate_count = len(source_discovery.get("candidate_sources", [])) if isinstance(source_discovery, dict) else 0
    selected_source_count = len(selected_manifest.get("sources", [])) if isinstance(selected_manifest, dict) else 0
    contradiction_count = len(review.get("contradiction_items", [])) if isinstance(review, dict) else 0

    if isinstance(review, dict) and review:
        review_status = str(review.get("review_status", "not_started"))
    elif isinstance(research_plan, dict) and research_plan:
        review_status = "planned"
    else:
        review_status = "not_started"

    if isinstance(source_discovery, dict) and source_discovery:
        search_status = str(source_discovery.get("search_status", "planned"))
    elif isinstance(research_plan, dict) and research_plan:
        search_status = "planned"
    else:
        search_status = "not_started"

    if isinstance(review, dict) and review.get("review_items"):
        recommendation = str(review["review_items"][0])
    elif isinstance(review, dict) and review.get("recommendation"):
        recommendation = str(review["recommendation"]).replace("_", " ")
    elif isinstance(research_plan, dict):
        recommendation = str(
            research_plan.get("coverage_summary", {}).get(
                "recommended_next_step",
                "No research recommendation recorded.",
            )
        )
    else:
        recommendation = "No research recommendation recorded."

    freshness_summary = "not_available"
    if isinstance(feed_registry, dict) and feed_registry.get("feeds"):
        cadence_counts: dict[str, int] = {}
        for feed in feed_registry.get("feeds", []):
            status = str(feed.get("cadence_status", "unknown"))
            cadence_counts[status] = cadence_counts.get(status, 0) + 1
        freshness_summary = "feed registry " + ", ".join(
            f"{cadence_counts[key]} {key}"
            for key in ("current", "due", "stale")
            if cadence_counts.get(key)
        )
        if freshness_summary == "feed registry ":
            freshness_summary = "feed registry cadence unavailable"
    elif isinstance(source_discovery, dict) and source_discovery.get("candidate_sources"):
        candidate_counts: dict[str, int] = {}
        for candidate in source_discovery.get("candidate_sources", []):
            status = str(
                candidate.get("detected_freshness_status")
                or candidate.get("freshness_expectation")
                or "unknown"
            )
            candidate_counts[status] = candidate_counts.get(status, 0) + 1
        freshness_summary = "candidate sources " + ", ".join(
            f"{candidate_counts[key]} {key}" for key in sorted(candidate_counts)
        )

    return {
        "review_status": review_status,
        "contradiction_count": contradiction_count,
        "search_status": search_status,
        "question_count": question_count,
        "candidate_count": candidate_count,
        "selected_source_count": selected_source_count,
        "freshness_summary": freshness_summary,
        "recommendation": recommendation,
    }


def summarize_strategy_refresh_posture(bundle: dict[str, Any]) -> dict[str, Any]:
    research_posture = summarize_research_posture(bundle)
    evidence_refs = {
        "market_analysis_brief": bundle.get("market_analysis_brief") or bundle.get("discover_market_analysis_brief"),
        "competitor_dossier": bundle.get("competitor_dossier") or bundle.get("discover_competitor_dossier"),
        "customer_pulse": bundle.get("customer_pulse") or bundle.get("discover_customer_pulse"),
    }
    downstream_refs = {
        "opportunity_portfolio_view": bundle.get("opportunity_portfolio_view") or bundle.get("discover_opportunity_portfolio_view"),
        "prioritization_decision_record": bundle.get("prioritization_decision_record") or bundle.get("discover_prioritization_decision_record"),
        "feature_prioritization_brief": bundle.get("feature_prioritization_brief") or bundle.get("discover_feature_prioritization_brief"),
    }

    available_evidence = [name for name, payload in evidence_refs.items() if isinstance(payload, dict) and payload]
    available_downstream = [name for name, payload in downstream_refs.items() if isinstance(payload, dict) and payload]
    missing_downstream = [name for name in downstream_refs if name not in available_downstream]

    if not available_evidence and research_posture["question_count"] == 0:
        status = "not_started"
        recommendation = "Generate the governed research packet before refreshing the strategy spine."
    elif research_posture["review_status"] == "review_required":
        status = "blocked_on_research_review"
        recommendation = research_posture["recommendation"]
    elif research_posture["review_status"] != "clear":
        status = "research_in_progress"
        recommendation = "Finish governed research review before refreshing the strategy spine."
    elif missing_downstream:
        status = "ready_for_strategy_refresh"
        recommendation = (
            "Refresh the canonical strategy packet from the governed research surface, then persist the missing "
            f"downstream packet artifacts: {', '.join(missing_downstream)}."
        )
    else:
        status = "ready_for_downstream_packet"
        recommendation = (
            "Refresh the canonical strategy packet and keep the downstream opportunity, prioritization, and feature "
            "brief packet aligned to the same governed research evidence."
        )

    return {
        "status": status,
        "available_evidence_count": len(available_evidence),
        "available_evidence_types": available_evidence,
        "downstream_packet_status": "available" if not missing_downstream else "missing",
        "available_downstream_count": len(available_downstream),
        "missing_downstream_types": missing_downstream,
        "recommendation": recommendation,
    }


def render_cockpit_html(cockpit_bundle: dict[str, Any]) -> str:
    cockpit = cockpit_bundle["cockpit_state"]
    mission = cockpit_bundle["mission_brief"]
    phase_packet = cockpit_bundle["active_phase_packet"]
    product_record = cockpit_bundle["product_record"]
    research_posture = cockpit_bundle.get("research_posture") or {
        "review_status": "not_started",
        "contradiction_count": 0,
        "search_status": "not_started",
        "question_count": 0,
        "candidate_count": 0,
        "selected_source_count": 0,
        "freshness_summary": "not_available",
        "recommendation": "No research recommendation recorded.",
    }
    strategy_refresh_posture = cockpit_bundle.get("strategy_refresh_posture") or {
        "status": "not_started",
        "available_evidence_count": 0,
        "available_evidence_types": [],
        "downstream_packet_status": "missing",
        "available_downstream_count": 0,
        "missing_downstream_types": [],
        "recommendation": "Generate the governed research packet before refreshing the strategy spine.",
    }
    claim_boundary_note = (
        "This cockpit is a bounded PM control-plane surface. It summarizes repo-native mission, phase, "
        "approval, and evidence context, but it does not by itself prove broader autonomy or expand the "
        "public release claim boundary."
    )
    nav_items = "".join(
        f"<li>{child['label']}</li>"
        for child in cockpit_bundle["workspace_tree_state"]["root"]["children"][0]["children"]
    )
    context_items = "".join(
        f"<li><code>{item['label']}</code> - {item['ref_path']}</li>"
        for item in cockpit.get("context_view_refs", [])
    )
    approval_items = "".join(
        f"<li>{item['title']} ({item['status']})</li>"
        for item in cockpit.get("approval_queue", [])
    )
    recommendation_items = "".join(
        f"<li>{item['summary']}</li>"
        for item in cockpit.get("recommended_pm_actions", [])
    )
    task_items = "".join(
        f"<li>{task['summary']}</li>"
        for task in phase_packet["task_queue"]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{mission['title']} cockpit</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {{
      --bg: #f4efe7;
      --panel: #fffaf3;
      --ink: #172022;
      --muted: #58656c;
      --line: #d7cec0;
      --accent: #b85c38;
      --accent-2: #31525b;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Georgia, "Iowan Old Style", serif; background: radial-gradient(circle at top left, #fff7e8, var(--bg)); color: var(--ink); }}
    .shell {{ display: grid; grid-template-columns: 260px 1fr 320px; gap: 16px; min-height: 100vh; padding: 16px; }}
    .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 18px; padding: 16px; box-shadow: 0 12px 32px rgba(23, 32, 34, 0.08); }}
    h1, h2, h3 {{ margin: 0 0 12px; font-weight: 600; }}
    h1 {{ font-size: 2rem; }}
    h2 {{ font-size: 1rem; letter-spacing: 0.02em; text-transform: uppercase; color: var(--accent-2); }}
    p, li {{ line-height: 1.45; }}
    .eyebrow {{ color: var(--accent); text-transform: uppercase; letter-spacing: 0.1em; font-size: 0.75rem; }}
    .metric {{ padding: 10px 12px; border-radius: 14px; background: #f8f1e4; margin-bottom: 10px; }}
    .notice {{ padding: 12px 14px; border-radius: 14px; background: #f5e6d7; border: 1px solid #d7b28e; color: #533724; }}
    ul {{ padding-left: 18px; margin: 0; }}
    .stack > * + * {{ margin-top: 14px; }}
    @media (max-width: 980px) {{
      .shell {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <aside class="panel stack">
      <div>
        <div class="eyebrow">Workspace Tree</div>
        <h2>{product_record['product_name']}</h2>
        <ul>{nav_items}</ul>
      </div>
      <div>
        <div class="eyebrow">Portfolio</div>
        <p><code>{cockpit_bundle['portfolio_state']['suite_id']}</code></p>
        <p>Maturity: <code>{mission['maturity_band']}</code></p>
      </div>
    </aside>
    <main class="panel stack">
      <div>
        <div class="eyebrow">Mission</div>
        <h1>{mission['title']}</h1>
        <p>{mission['mission_summary']}</p>
      </div>
      <div class="notice">{claim_boundary_note}</div>
      <div class="metric">Ralph stage: <strong>{cockpit['ralph_stage']}</strong></div>
      <div class="metric">Current phase: <strong>{phase_packet['lifecycle_phase']}</strong></div>
      <div class="metric">Budget status: <strong>{cockpit['budget_status']['status']}</strong></div>
      <div>
        <h2>Today View</h2>
        <p>{cockpit['recommended_next_step']['action_summary']}</p>
      </div>
      <div>
        <h2>Phase Tasks</h2>
        <ul>{task_items}</ul>
      </div>
      <div>
        <h2>Research Posture</h2>
        <ul>
          <li>Review: {research_posture['review_status']}</li>
          <li>Search: {research_posture['search_status']}</li>
          <li>Freshness: {research_posture['freshness_summary']}</li>
          <li>Candidates / Selected: {research_posture['candidate_count']} / {research_posture['selected_source_count']}</li>
          <li>Contradictions: {research_posture['contradiction_count']}</li>
          <li>Next research action: {research_posture['recommendation']}</li>
        </ul>
      </div>
      <div>
        <h2>Strategy Spine</h2>
        <ul>
          <li>Refresh status: {strategy_refresh_posture['status']}</li>
          <li>Evidence inputs: {strategy_refresh_posture['available_evidence_count']} ({', '.join(strategy_refresh_posture['available_evidence_types']) or 'none'})</li>
          <li>Downstream packet: {strategy_refresh_posture['downstream_packet_status']}</li>
          <li>Missing downstream artifacts: {', '.join(strategy_refresh_posture['missing_downstream_types']) or 'none'}</li>
          <li>Next strategy action: {strategy_refresh_posture['recommendation']}</li>
        </ul>
      </div>
      <div>
        <h2>Context</h2>
        <ul>{context_items}</ul>
      </div>
    </main>
    <section class="panel stack">
      <div>
        <div class="eyebrow">Approvals</div>
        <h2>Queue</h2>
        <ul>{approval_items}</ul>
      </div>
      <div>
        <h2>Why This Recommendation</h2>
        <ul>{recommendation_items}</ul>
      </div>
    </section>
  </div>
</body>
</html>
"""


def build_cockpit_bundle_from_workspace(
    workspace_dir: Path | str,
    *,
    generated_at: str,
    adapter_name: str = "codex",
) -> dict[str, Any]:
    from .mission import load_mission_brief_from_workspace
    from .next_version import build_next_version_bundle_from_workspace

    workspace_path = Path(workspace_dir).resolve()
    mission_brief = load_mission_brief_from_workspace(workspace_path)
    if mission_brief is None:
        raise FileNotFoundError(f"No mission_brief.json found in {workspace_path / 'artifacts'}")
    product_record = load_product_record_from_workspace(workspace_path)
    if product_record is None:
        product_record = build_product_record(
            workspace_path,
            mission_brief=mission_brief,
            generated_at=generated_at,
        )
    phase_packet = load_phase_packet_from_workspace(workspace_path, product_record["lifecycle_stage"])
    if phase_packet is None:
        phase_packet = build_phase_packet(
            workspace_path,
            mission_brief=mission_brief,
            product_record=product_record,
            lifecycle_phase=product_record["lifecycle_stage"],
            generated_at=generated_at,
        )
    workspace_tree_state = build_workspace_tree_state(
        workspace_path,
        mission_brief=mission_brief,
        product_record=product_record,
        generated_at=generated_at,
    )
    next_version_bundle = build_next_version_bundle_from_workspace(
        workspace_path,
        generated_at=generated_at,
        adapter_name=adapter_name,
    )
    cockpit_state, orchestration_state = enrich_runtime_states(
        mission_brief=mission_brief,
        product_record=product_record,
        phase_packet=phase_packet,
        workspace_tree_state=workspace_tree_state,
        next_version_bundle=next_version_bundle,
    )
    portfolio_state = build_portfolio_state_from_workspaces(
        [workspace_path],
        generated_at=generated_at,
        suite_id=mission_brief.get("portfolio_id") or product_record.get("portfolio_id"),
    )
    cross_product_insight_index = build_cross_product_insight_index(
        [workspace_path],
        generated_at=generated_at,
        portfolio_id=mission_brief.get("portfolio_id") or product_record.get("portfolio_id"),
    )
    research_posture = summarize_research_posture(next_version_bundle)
    strategy_refresh_posture = summarize_strategy_refresh_posture(next_version_bundle)
    html_path = workspace_path / "outputs" / "cockpit" / "control-center.html"
    return {
        "schema_version": "1.0.0",
        "cockpit_bundle_id": f"cockpit_bundle_{product_record['workspace_id']}",
        "workspace_id": product_record["workspace_id"],
        "portfolio_id": mission_brief.get("portfolio_id") or product_record.get("portfolio_id"),
        "mission_ref": mission_brief["mission_brief_id"],
        "product_record_ref": product_record["product_record_id"],
        "bundle_status": cockpit_state["status"],
        "ralph_stage": cockpit_state["ralph_stage"],
        "mission_brief": mission_brief,
        "product_record": product_record,
        "portfolio_state": portfolio_state,
        "workspace_tree_state": workspace_tree_state,
        "active_phase_packet": phase_packet,
        "cockpit_state": cockpit_state,
        "orchestration_state": orchestration_state,
        "cross_product_insight_index": cross_product_insight_index,
        "research_posture": research_posture,
        "strategy_refresh_posture": strategy_refresh_posture,
        "context_view_refs": cockpit_state["context_view_refs"],
        "recommended_pm_actions": cockpit_state["recommended_pm_actions"],
        "generated_html_ref": _relative_path(html_path),
        "source_artifact_ids": list(
            dict.fromkeys(
                [
                    mission_brief["mission_brief_id"],
                    product_record["product_record_id"],
                    phase_packet["phase_packet_id"],
                    workspace_tree_state["workspace_tree_state_id"],
                    *cockpit_state.get("source_artifact_ids", []),
                ]
            )
        ),
        "generated_at": generated_at,
    }
