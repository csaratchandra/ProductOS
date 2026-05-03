from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

from .governed_docs import render_governed_markdown
from .lifecycle import DISCOVERY_STAGE_ORDER, LIFECYCLE_STAGE_ORDER
from .pm_superpowers import seed_pm_superpower_artifacts


ROOT = Path(__file__).resolve().parents[3]

DELIVERY_STAGE_ORDER = ["story_planning", "acceptance_ready", "release_readiness"]
LAUNCH_STAGE_ORDER = ["launch_preparation"]
OUTCOMES_STAGE_ORDER = ["outcome_review"]
SNAPSHOT_STAGE_KEYS = {
    "discovery": DISCOVERY_STAGE_ORDER,
    "delivery": DELIVERY_STAGE_ORDER,
    "launch": LAUNCH_STAGE_ORDER,
    "outcomes": OUTCOMES_STAGE_ORDER,
    "full_lifecycle": LIFECYCLE_STAGE_ORDER,
}

MISSION_WORKFLOW_REFS = {
    "discover": [
        "../../core/workflows/workspace-ingestion/inbox-to-normalized-evidence-workflow.md",
        "../../core/workflows/decision-intelligence/mission-to-strategy-spine-workflow.md",
        "../../core/workflows/decision-intelligence/strategy-option-generation-workflow.md",
        "../../core/workflows/decision-intelligence/market-strategy-definition-workflow.md",
        "../../core/workflows/discovery/idea-to-concept-workflow.md",
        "../../core/workflows/research/research-command-center-workflow.md",
        "../../core/workflows/delivery/problem-brief-to-prd-workflow.md",
    ],
    "discover_to_align": [
        "../../core/workflows/workspace-ingestion/inbox-to-normalized-evidence-workflow.md",
        "../../core/workflows/decision-intelligence/mission-to-strategy-spine-workflow.md",
        "../../core/workflows/decision-intelligence/strategy-option-generation-workflow.md",
        "../../core/workflows/decision-intelligence/market-strategy-definition-workflow.md",
        "../../core/workflows/discovery/idea-to-concept-workflow.md",
        "../../core/workflows/research/research-command-center-workflow.md",
        "../../core/workflows/delivery/problem-brief-to-prd-workflow.md",
        "../../core/workflows/mastery/readable-doc-review-and-sync-workflow.md",
        "../../core/workflows/mastery/document-to-presentation-packaging-workflow.md",
    ],
    "full_loop": [
        "../../core/workflows/workspace-ingestion/inbox-to-normalized-evidence-workflow.md",
        "../../core/workflows/decision-intelligence/mission-to-strategy-spine-workflow.md",
        "../../core/workflows/decision-intelligence/strategy-option-generation-workflow.md",
        "../../core/workflows/decision-intelligence/market-strategy-definition-workflow.md",
        "../../core/workflows/discovery/idea-to-concept-workflow.md",
        "../../core/workflows/research/research-command-center-workflow.md",
        "../../core/workflows/delivery/problem-brief-to-prd-workflow.md",
        "../../core/workflows/delivery/prd-to-stories-workflow.md",
        "../../core/workflows/delivery/stories-to-acceptance-workflow.md",
        "../../core/workflows/launch/release-readiness-workflow.md",
        "../../core/workflows/mastery/post-release-outcome-review-workflow.md",
        "../../core/workflows/mastery/bounded-improvement-workflow.md",
    ],
}

MISSION_MEMORY_PRIORITY_ORDER = [
    "decisions",
    "evidence",
    "prior_artifacts",
    "repeated_issues",
    "strategic_memory",
]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _unique_strings(values: list[str]) -> list[str]:
    cleaned: list[str] = []
    for value in values:
        stripped = value.strip()
        if stripped and stripped not in cleaned:
            cleaned.append(stripped)
    return cleaned


def _relative_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return path.as_posix()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _append_once(text: str, extra: str) -> str:
    return text if extra in text else f"{text} {extra}".strip()


def _priority_profile(
    *,
    lane: str,
    priority_score: int,
    confidence: str,
    agentic_delivery_burden: str,
    rationale: str,
    reviewer_handoff: str,
) -> dict[str, Any]:
    return {
        "lane": lane,
        "priority_score": priority_score,
        "confidence": confidence,
        "agentic_delivery_burden": agentic_delivery_burden,
        "priority_rationale": rationale,
        "reviewer_handoff": reviewer_handoff,
    }


def _can_replace_discover_artifact(path: Path) -> bool:
    if not path.exists():
        return True
    payload = _load_json(path)
    artifact_id_keys = [
        "strategy_context_brief_id",
        "product_vision_brief_id",
        "strategy_option_set_id",
        "market_strategy_brief_id",
        "problem_brief_id",
        "concept_brief_id",
        "prd_id",
    ]
    artifact_id = next((payload.get(key) for key in artifact_id_keys if payload.get(key)), "")
    return (
        artifact_id.endswith("_mission_strategy")
        or artifact_id.endswith("_mission_discover")
        or artifact_id.endswith("_starter_trace_demo")
    )


def _can_replace_lifecycle_artifact(path: Path) -> bool:
    if not path.exists():
        return False
    payload = _load_json(path)
    artifact_id = payload.get("item_lifecycle_state_id") or payload.get("lifecycle_stage_snapshot_id", "")
    return artifact_id.endswith("_starter_trace_demo") or artifact_id.endswith("_mission_trace")


def _merge_entity_refs(
    refs: list[dict[str, Any]],
    *,
    replacements: list[dict[str, str]],
    replace_entity_types: set[str],
) -> list[dict[str, str]]:
    merged: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for ref in refs:
        entity_type = str(ref.get("entity_type", ""))
        entity_id = str(ref.get("entity_id", ""))
        if entity_type in replace_entity_types or not entity_type or not entity_id:
            continue
        key = (entity_type, entity_id)
        if key in seen:
            continue
        merged.append({"entity_type": entity_type, "entity_id": entity_id})
        seen.add(key)
    for ref in replacements:
        key = (ref["entity_type"], ref["entity_id"])
        if key in seen:
            continue
        merged.append(ref)
        seen.add(key)
    return merged


def _mission_trace_identity(mission_brief: dict[str, Any]) -> dict[str, str]:
    mission_slug = _slug(mission_brief["title"])
    return {
        "problem_id": f"problem_{mission_slug}",
        "outcome_id": f"outcome_{mission_slug}",
        "opportunity_id": f"opportunity_{mission_slug}",
        "feature_id": f"feature_{mission_slug}_discover_loop",
        "item_lifecycle_state_id": f"item_lifecycle_state_{mission_slug}_mission_trace",
        "discovery_snapshot_id": f"lifecycle_stage_snapshot_discovery_{mission_slug}_mission_trace",
        "delivery_snapshot_id": f"lifecycle_stage_snapshot_delivery_{mission_slug}_mission_trace",
        "launch_snapshot_id": f"lifecycle_stage_snapshot_launch_{mission_slug}_mission_trace",
        "outcomes_snapshot_id": f"lifecycle_stage_snapshot_outcomes_{mission_slug}_mission_trace",
        "full_lifecycle_snapshot_id": f"lifecycle_stage_snapshot_full_lifecycle_{mission_slug}_mission_trace",
    }


def _mission_router_for_mode(operating_mode: str) -> dict[str, Any]:
    if operating_mode == "discover":
        return {
            "entry_phase": "discover",
            "phase_sequence": ["discover"],
            "primary_reviewer_lane": "pm_builder",
            "routing_rationale": "Keep the first mission route discover-only until the PM accepts a reviewable decision package.",
            "stop_conditions": [
                "Stop if evidence freshness or provenance becomes unclear.",
                "Stop if the discover outputs are not reviewable by the PM.",
                "Stop before downstream execution unless the PM explicitly approves expansion.",
            ],
        }
    if operating_mode == "discover_to_align":
        return {
            "entry_phase": "discover",
            "phase_sequence": ["discover", "align"],
            "primary_reviewer_lane": "pm_builder",
            "routing_rationale": "Use discover to establish product truth, then allow one bounded alignment step for docs and deck outputs.",
            "stop_conditions": [
                "Stop if discover outputs are not accepted as the source package.",
                "Stop if alignment outputs drift from the accepted discover package.",
                "Stop before weekly operation or release movement unless the PM approves expansion.",
            ],
        }
    return {
        "entry_phase": "discover",
        "phase_sequence": ["discover", "align", "operate", "improve"],
        "primary_reviewer_lane": "pm_builder",
        "routing_rationale": "Run the full PM loop from a mission-first discover start while keeping PM approval explicit at every decision-driving boundary.",
        "stop_conditions": [
            "Stop if any phase loses provenance, reviewability, or PM approval visibility.",
            "Stop if downstream phases outrun the accepted mission package.",
            "Stop if release-facing claims exceed the current evidence-backed boundary.",
        ],
    }


def _default_artifact_focus_for_mode(operating_mode: str) -> list[str]:
    if operating_mode == "discover":
        return [
            "mission_brief",
            "strategy_context_brief",
            "product_vision_brief",
            "strategy_option_set",
            "market_strategy_brief",
            "problem_brief",
            "concept_brief",
            "prd",
        ]
    if operating_mode == "discover_to_align":
        return [
            "mission_brief",
            "strategy_context_brief",
            "product_vision_brief",
            "strategy_option_set",
            "market_strategy_brief",
            "problem_brief",
            "concept_brief",
            "prd",
            "document_sync_state",
            "presentation_brief",
        ]
    return [
        "mission_brief",
        "strategy_context_brief",
        "product_vision_brief",
        "strategy_option_set",
        "market_strategy_brief",
        "problem_brief",
        "concept_brief",
        "prd",
        "document_sync_state",
        "presentation_brief",
        "status_mail",
        "feature_portfolio_review",
    ]


def _steering_context_for_workspace(workspace_path: Path, operating_mode: str) -> dict[str, Any]:
    steering_doc = _relative_path(workspace_path / "docs" / "planning" / "steering-context.md")
    return {
        "steering_refs": [
            steering_doc,
            "core/docs/vendor-neutral-agent-harness-standard.md",
            "core/docs/ralph-loop-model.md",
        ],
        "operating_norms": [
            "Treat the repository as the system of record.",
            "Keep PM approval explicit for decision-driving scope, stakeholder-facing output, and release movement.",
            "Preserve observed versus inferred claims when evidence is incomplete.",
            "Prefer the smallest coherent slice that can be reviewed and validated end to end.",
        ],
        "memory_priority_order": list(MISSION_MEMORY_PRIORITY_ORDER),
        "default_artifact_focus": _default_artifact_focus_for_mode(operating_mode),
    }


def format_steering_context_markdown(mission_brief: dict[str, Any]) -> str:
    router = mission_brief["mission_router"]
    steering = mission_brief["steering_context"]
    lines = [
        "# Steering Context",
        "",
        f"Mission: `{mission_brief['title']}`",
        f"Operating Mode: `{mission_brief['operating_mode']}`",
        "",
        "## Mission Router",
        "",
        f"- Entry phase: `{router['entry_phase']}`",
        f"- Phase sequence: {', '.join(f'`{item}`' for item in router['phase_sequence'])}",
        f"- Primary reviewer lane: `{router['primary_reviewer_lane']}`",
        "",
        router["routing_rationale"],
        "",
        "## Stop Conditions",
        "",
    ]
    for item in router["stop_conditions"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Operating Norms", ""])
    for item in steering["operating_norms"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Memory Priority Order", ""])
    for item in steering["memory_priority_order"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Default Artifact Focus", ""])
    for item in steering["default_artifact_focus"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Steering References", ""])
    for item in steering["steering_refs"]:
        lines.append(f"- `{item}`")
    lines.append("")
    return "\n".join(lines)


def _snapshot_summary_for_focus(focus_area: str, mission_title: str) -> str:
    if focus_area == "discovery":
        return (
            f"The mission-backed discovery trace for '{mission_title}' now points to the canonical mission brief, "
            "problem brief, concept brief, and PRD artifacts."
        )
    if focus_area == "delivery":
        return f"Delivery trace for '{mission_title}' stays tied to the same mission-backed lifecycle item through release readiness."
    if focus_area == "launch":
        return f"Launch trace for '{mission_title}' keeps the seeded release communication on the same mission-backed lifecycle item."
    if focus_area == "outcomes":
        return f"Outcome trace for '{mission_title}' keeps post-release review attached to the same mission-backed lifecycle item."
    return f"The full lifecycle trace for '{mission_title}' now stays coherent from mission intake through outcome review."


def _gate_counts_from_stages(stages: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"passed": 0, "pending": 0, "blocked": 0, "not_started": 0}
    for stage in stages:
        gate_status = stage.get("gate_status", "not_started")
        counts[gate_status] = counts.get(gate_status, 0) + 1
    return counts


def _build_snapshot_stage_summaries(
    stages: list[dict[str, Any]],
    *,
    opportunity_id: str,
) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for stage in stages:
        gate_counts = {"passed": 0, "pending": 0, "blocked": 0, "not_started": 0}
        gate_status = stage.get("gate_status", "not_started")
        gate_counts[gate_status] = 1
        summaries.append(
            {
                "stage_key": stage["stage_key"],
                "item_ids": [opportunity_id],
                "artifact_ids": list(stage.get("artifact_ids", [])),
                "gate_status_counts": gate_counts,
                "summary": stage["summary"],
            }
        )
    return summaries


def _rebase_safe_lifecycle_trace(
    workspace_path: Path,
    *,
    mission_brief: dict[str, Any],
    generated_at: str,
) -> bool:
    artifacts_dir = workspace_path / "artifacts"
    item_path = artifacts_dir / "item_lifecycle_state.json"
    snapshot_paths = {
        "discovery": artifacts_dir / "lifecycle_stage_snapshot.json",
        "delivery": artifacts_dir / "lifecycle_stage_snapshot_delivery.json",
        "launch": artifacts_dir / "lifecycle_stage_snapshot_launch.json",
        "outcomes": artifacts_dir / "lifecycle_stage_snapshot_outcomes.json",
        "full_lifecycle": artifacts_dir / "lifecycle_stage_snapshot_full_lifecycle.json",
    }
    if not _can_replace_lifecycle_artifact(item_path):
        return False
    safe_snapshot_paths = {focus: path for focus, path in snapshot_paths.items() if _can_replace_lifecycle_artifact(path)}
    if not safe_snapshot_paths:
        return False

    mission_title = mission_brief["title"]
    mission_id = mission_brief["mission_brief_id"]
    mission_problem = mission_brief["customer_problem"]
    mission_slug = _slug(mission_title)
    trace_identity = _mission_trace_identity(mission_brief)
    mission_prd_id = f"prd_{mission_slug}_mission_discover"
    mission_persona_archetype_pack_id = f"persona_archetype_pack_{mission_slug}_mission_strategy"
    mission_entity_refs = [
        {"entity_type": "problem", "entity_id": trace_identity["problem_id"]},
        {"entity_type": "outcome", "entity_id": trace_identity["outcome_id"]},
        {"entity_type": "opportunity", "entity_id": trace_identity["opportunity_id"]},
        {"entity_type": "feature", "entity_id": trace_identity["feature_id"]},
    ]

    story_pack_path = artifacts_dir / "story_pack.json"
    story_pack_id = None
    if story_pack_path.exists():
        story_pack = _load_json(story_pack_path)
        story_pack_id = story_pack.get("story_pack_id")
        story_pack["feature_id"] = trace_identity["feature_id"]
        story_pack["source_prd_id"] = mission_prd_id
        story_pack["canonical_persona_archetype_pack_id"] = mission_persona_archetype_pack_id
        for story in story_pack.get("stories", []):
            story["linked_entity_refs"] = _merge_entity_refs(
                list(story.get("linked_entity_refs", [])),
                replacements=mission_entity_refs,
                replace_entity_types={"problem", "outcome", "opportunity", "feature"},
            )
        _write_json(story_pack_path, story_pack)

    acceptance_path = artifacts_dir / "acceptance_criteria_set.json"
    acceptance_id = None
    if acceptance_path.exists():
        acceptance = _load_json(acceptance_path)
        acceptance_id = acceptance.get("acceptance_criteria_set_id")
        acceptance["source_prd_id"] = mission_prd_id
        acceptance["canonical_persona_archetype_pack_id"] = mission_persona_archetype_pack_id
        _write_json(acceptance_path, acceptance)

    release_readiness_path = artifacts_dir / "release_readiness.json"
    release_readiness_id = None
    if release_readiness_path.exists():
        release_readiness = _load_json(release_readiness_path)
        release_readiness_id = release_readiness.get("release_readiness_id")
        release_readiness["feature_id"] = trace_identity["feature_id"]
        _write_json(release_readiness_path, release_readiness)

    release_note_path = artifacts_dir / "release_note.json"
    release_note_id = None
    if release_note_path.exists():
        release_note = _load_json(release_note_path)
        release_note_id = release_note.get("release_note_id")
        release_note["feature_ids"] = [trace_identity["feature_id"]]
        _write_json(release_note_path, release_note)

    item_state = _load_json(item_path)
    original_item_state_id = item_state["item_lifecycle_state_id"]
    item_state["item_lifecycle_state_id"] = trace_identity["item_lifecycle_state_id"]
    item_state["title"] = f"Mission lifecycle trace for {mission_title}"
    item_state["item_ref"] = {
        "entity_type": "opportunity",
        "entity_id": trace_identity["opportunity_id"],
    }
    item_state["linked_entity_refs"] = mission_entity_refs

    stage_map = {stage["stage_key"]: stage for stage in item_state.get("lifecycle_stages", [])}
    if "signal_intake" in stage_map:
        stage_map["signal_intake"]["artifact_ids"] = [mission_id]
        stage_map["signal_intake"]["summary"] = f"The mission '{mission_title}' is now the canonical intake for this workspace."
    if "problem_framing" in stage_map:
        stage_map["problem_framing"]["artifact_ids"] = [
            _load_json(artifacts_dir / "problem_brief.json")["problem_brief_id"]
        ]
        stage_map["problem_framing"]["summary"] = f"The mission problem is now framed explicitly: {mission_problem}"
    if "concept_shaping" in stage_map:
        stage_map["concept_shaping"]["artifact_ids"] = [
            _load_json(artifacts_dir / "concept_brief.json")["concept_brief_id"]
        ]
        stage_map["concept_shaping"]["summary"] = f"The selected concept now inherits the mission '{mission_title}' directly."
    if "prd_handoff" in stage_map:
        existing_artifact_ids = list(stage_map["prd_handoff"].get("artifact_ids", []))
        prd_id = _load_json(artifacts_dir / "prd.json")["prd_id"]
        stage_map["prd_handoff"]["artifact_ids"] = [prd_id, *[artifact_id for artifact_id in existing_artifact_ids if artifact_id != prd_id]]
        stage_map["prd_handoff"]["summary"] = f"The PRD handoff now points at the mission-backed PRD for '{mission_title}'."
    if "story_planning" in stage_map and story_pack_id:
        stage_map["story_planning"]["artifact_ids"] = [story_pack_id]
        stage_map["story_planning"]["summary"] = f"Story planning now extends the mission '{mission_title}' into a bounded delivery slice."
    if "acceptance_ready" in stage_map and acceptance_id:
        stage_map["acceptance_ready"]["artifact_ids"] = [acceptance_id]
        stage_map["acceptance_ready"]["summary"] = f"Acceptance criteria now keep the mission '{mission_title}' explicit at handoff."
    if "release_readiness" in stage_map and release_readiness_id:
        stage_map["release_readiness"]["artifact_ids"] = [release_readiness_id]
        stage_map["release_readiness"]["summary"] = f"Release readiness now evaluates the mission '{mission_title}' on the same canonical item."
    if "launch_preparation" in stage_map and release_note_id:
        stage_map["launch_preparation"]["artifact_ids"] = [release_note_id]
        stage_map["launch_preparation"]["summary"] = f"Launch preparation now keeps the mission '{mission_title}' explicit in release communication."

    outcome_review_path = artifacts_dir / "outcome_review.json"
    outcome_review_id = None
    if outcome_review_path.exists():
        outcome_review = _load_json(outcome_review_path)
        outcome_review_id = outcome_review.get("outcome_review_id")
        evidence_refs = []
        for artifact_id in outcome_review.get("evidence_refs", []):
            if artifact_id == original_item_state_id:
                continue
            evidence_refs.append(artifact_id)
        outcome_review["evidence_refs"] = list(
            dict.fromkeys([*evidence_refs, item_state["item_lifecycle_state_id"], mission_id])
        )
        _write_json(outcome_review_path, outcome_review)
    if "outcome_review" in stage_map and outcome_review_id:
        stage_map["outcome_review"]["artifact_ids"] = [outcome_review_id]
        stage_map["outcome_review"]["summary"] = f"Outcome review now measures whether '{mission_title}' still advances after release."

    item_state["pending_questions"] = [
        f"Which first-party evidence source should replace the seeded starter research for the mission '{mission_title}'?"
    ]
    item_state["audit_log"] = [
        *item_state.get("audit_log", []),
        {
            "timestamp": generated_at,
            "actor": "Mission Builder",
            "event_type": "status_changed",
            "summary": f"The starter lifecycle trace was rebased onto the mission '{mission_title}'.",
        },
    ]
    item_state["updated_at"] = generated_at
    _write_json(item_path, item_state)

    snapshot_id_keys = {
        "discovery": "discovery_snapshot_id",
        "delivery": "delivery_snapshot_id",
        "launch": "launch_snapshot_id",
        "outcomes": "outcomes_snapshot_id",
        "full_lifecycle": "full_lifecycle_snapshot_id",
    }
    current_stages = {stage["stage_key"]: stage for stage in item_state["lifecycle_stages"]}
    for focus_area, path in safe_snapshot_paths.items():
        snapshot = _load_json(path)
        focus_stages = [current_stages[stage_key] for stage_key in SNAPSHOT_STAGE_KEYS[focus_area] if stage_key in current_stages]
        snapshot["lifecycle_stage_snapshot_id"] = trace_identity[snapshot_id_keys[focus_area]]
        snapshot["active_item_ids"] = [trace_identity["opportunity_id"]]
        snapshot["segment_count"] = len(item_state.get("target_segment_refs", []))
        snapshot["persona_count"] = len(item_state.get("target_persona_refs", []))
        snapshot["item_count"] = 1
        snapshot["gate_counts"] = _gate_counts_from_stages(focus_stages)
        snapshot["stage_summaries"] = _build_snapshot_stage_summaries(
            focus_stages,
            opportunity_id=trace_identity["opportunity_id"],
        )
        snapshot["snapshot_summary"] = _snapshot_summary_for_focus(focus_area, mission_title)
        snapshot["created_at"] = generated_at
        _write_json(path, snapshot)

    return True


def _workspace_metadata(workspace_dir: Path) -> tuple[str, str, list[str]]:
    workspace_manifest = workspace_dir / "workspace_manifest.yaml"
    source_refs: list[str] = []
    workspace_id = ""
    workspace_name = workspace_dir.name
    if workspace_manifest.exists():
        manifest = yaml.safe_load(workspace_manifest.read_text(encoding="utf-8")) or {}
        workspace_id = str(manifest.get("workspace_id", "")).strip()
        workspace_name = str(manifest.get("name", workspace_name)).strip() or workspace_name
        source_refs.append(_relative_path(workspace_manifest))

    problem_brief_path = workspace_dir / "artifacts" / "problem_brief.json"
    if problem_brief_path.exists():
        problem_brief = _load_json(problem_brief_path)
        workspace_id = workspace_id or str(problem_brief.get("workspace_id", "")).strip()
        source_refs.append(_relative_path(problem_brief_path))

    if not workspace_id:
        workspace_id = f"ws_{_slug(workspace_name)}"

    return workspace_id, workspace_name, _unique_strings(source_refs or [_relative_path(workspace_dir)])


def build_mission_brief(
    workspace_dir: Path | str,
    *,
    title: str,
    target_user: str,
    customer_problem: str,
    business_goal: str,
    success_metrics: list[str],
    constraints: list[str] | None,
    audience: list[str] | None,
    operating_mode: str,
    generated_at: str,
    maturity_band: str = "zero_to_one",
    primary_outcomes: list[str] | None = None,
    primary_kpis: list[str] | None = None,
    review_gate_owner: str = "ProductOS PM",
    portfolio_id: str | None = None,
    stage_goals: dict[str, str] | None = None,
    known_risks: list[str] | None = None,
) -> dict[str, Any]:
    workspace_path = Path(workspace_dir).resolve()
    workspace_id, workspace_name, source_refs = _workspace_metadata(workspace_path)
    mission_brief_id = f"mission_brief_{workspace_id}_{_slug(title)}"
    mission_audience = _unique_strings(audience or ["PM", "engineering", "design", "leadership"])
    mission_constraints = _unique_strings(
        constraints
        or [
            "Keep PM approval explicit for decision-driving scope and release movement.",
            "Preserve observed versus inferred claims when evidence is incomplete.",
        ]
    )
    metrics = _unique_strings(success_metrics)
    workflow_refs = list(MISSION_WORKFLOW_REFS[operating_mode])
    mission_router = _mission_router_for_mode(operating_mode)
    steering_context = _steering_context_for_workspace(workspace_path, operating_mode)
    return {
        "schema_version": "1.0.0",
        "mission_brief_id": mission_brief_id,
        "workspace_id": workspace_id,
        "portfolio_id": portfolio_id or workspace_id,
        "title": title,
        "mission_summary": (
            f"{workspace_name} should help {target_user} solve {customer_problem.lower()} while driving "
            f"{business_goal.lower()} through a governed ProductOS loop."
        ),
        "target_user": target_user,
        "customer_problem": customer_problem,
        "business_goal": business_goal,
        "maturity_band": maturity_band,
        "primary_outcomes": _unique_strings(primary_outcomes or [business_goal]),
        "primary_kpis": _unique_strings(primary_kpis or metrics),
        "review_gate_owner": review_gate_owner,
        "success_metrics": metrics,
        "constraints": mission_constraints,
        "audience": mission_audience,
        "operating_mode": operating_mode,
        "mission_router": mission_router,
        "steering_context": steering_context,
        "primary_workflow_refs": workflow_refs,
        "source_refs": source_refs,
        "stage_goals": stage_goals or {},
        "known_risks": _unique_strings(
            known_risks
            or [
                "Starter defaults still need workspace-specific evidence before they should drive release movement.",
            ]
        ),
        "next_action": "Run the mission through the strategy spine first, keep evidence and approvals explicit, then expand phase coverage only when the prior outputs stay reviewable.",
        "created_at": generated_at,
        "updated_at": generated_at,
    }


def build_discover_artifacts_from_mission(
    *,
    workspace_id: str,
    generated_at: str,
    mission_brief: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    bundle = build_strategy_discover_bundle_from_mission(
        workspace_id=workspace_id,
        generated_at=generated_at,
        mission_brief=mission_brief,
    )
    return bundle["problem_brief"], bundle["concept_brief"], bundle["prd"]


def build_strategy_discover_bundle_from_mission(
    *,
    workspace_id: str,
    generated_at: str,
    mission_brief: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    mission_slug = _slug(mission_brief["title"])
    mission_source_refs = list(mission_brief.get("source_refs", []))
    mission_target_user = mission_brief["target_user"]
    mission_operating_mode = mission_brief["operating_mode"]
    business_goal = mission_brief["business_goal"]
    customer_problem = mission_brief["customer_problem"]
    success_metrics = list(mission_brief.get("success_metrics", []))
    primary_metric = success_metrics[0] if success_metrics else "time to a reviewable PM package"
    mission_id = mission_brief["mission_brief_id"]
    mission_title = mission_brief["title"]
    evidence_refs = [
        {
            "source_type": "other",
            "source_id": source_ref,
            "justification": f"Mission intake source kept as repo-visible input for discover generation: {source_ref}",
        }
        for source_ref in mission_source_refs
    ] or [
        {
            "source_type": "other",
            "source_id": mission_id,
            "justification": "Mission brief defines the bounded PM-first execution intent for this workspace.",
        }
    ]
    strategy_context_id = f"strategy_context_brief_{mission_slug}_mission_strategy"
    product_vision_id = f"product_vision_brief_{mission_slug}_mission_strategy"
    strategy_option_set_id = f"strategy_option_set_{mission_slug}_mission_strategy"
    market_strategy_id = f"market_strategy_brief_{mission_slug}_mission_strategy"
    persona_archetype_pack_id = f"persona_archetype_pack_{mission_slug}_mission_strategy"
    segment_refs = [{"entity_type": "segment", "entity_id": "segment_b2b_product_teams"}]
    persona_refs = [{"entity_type": "persona", "entity_id": "persona_product_manager"}]
    linked_entity_refs = [
        {"entity_type": "problem", "entity_id": f"problem_{mission_slug}"},
        {"entity_type": "outcome", "entity_id": f"outcome_{mission_slug}"},
        {"entity_type": "opportunity", "entity_id": f"opportunity_{mission_slug}"},
        {"entity_type": "feature", "entity_id": f"feature_{mission_slug}_discover_loop"},
    ]

    strategy_context = {
        "schema_version": "1.0.0",
        "strategy_context_brief_id": strategy_context_id,
        "workspace_id": workspace_id,
        "title": f"Strategy context brief: {mission_title}",
        "mission_ref": mission_id,
        "context_summary": (
            f"ProductOS should use the mission '{mission_title}' to make strategy linkage, product vision, and market posture explicit "
            "before downstream problem framing or PRD work expands."
        ),
        "enterprise_goal_links": [
            {
                "goal_name": business_goal,
                "goal_type": "growth",
                "linkage_summary": (
                    "The strategy spine should connect the mission directly to a buyer-visible product bet instead of making the PM reconstruct that logic later."
                ),
                "success_signal": primary_metric,
            }
        ],
        "portfolio_bets": [
            {
                "bet_name": "Mission-linked PM judgment amplifier",
                "fit": "core",
                "rationale": "The repo already governs execution well, so the next leverage is making strategy logic explicit before delivery artifacts are generated.",
            }
        ],
        "business_model_outcomes": [
            {
                "outcome_name": "Make ProductOS easier to trust",
                "outcome_type": "adoption",
                "linkage_summary": "Clear strategy linkage should make the product easier to evaluate and safer to adopt without widening the claim boundary.",
            },
            {
                "outcome_name": "Preserve evidence-backed positioning",
                "outcome_type": "strategic_position",
                "linkage_summary": "The mission should improve judgment quality and clarity before broader autonomy or publishing claims advance.",
            },
        ],
        "strategic_constraints": [
            {
                "constraint": "Keep PM approval explicit for decision-driving scope and release movement.",
                "constraint_type": "governance",
                "consequence": "The strategy packet must stay reviewable and must not auto-commit the product beyond the accepted mission.",
            },
            {
                "constraint": "Do not broaden autonomous PM claims past the current evidence-backed release boundary.",
                "constraint_type": "evidence",
                "consequence": "The near-term goal should sharpen PM judgment rather than imply broader unsupported autonomy.",
            },
        ],
        "linked_artifact_ids": [mission_id],
        "open_questions": [
            f"Which downstream phase should follow the current {mission_operating_mode} mission mode once the strategy packet is accepted?"
        ],
        "evidence_refs": [
            {
                "source_type": "mission",
                "source_id": mission_id,
                "justification": "The mission brief defines the customer problem, business goal, and review boundary for the strategy packet.",
            }
        ],
        "recommendation": "proceed_to_product_vision",
        "created_at": generated_at,
    }

    product_vision = {
        "schema_version": "1.0.0",
        "product_vision_brief_id": product_vision_id,
        "workspace_id": workspace_id,
        "title": f"Product vision brief: {mission_title}",
        "strategy_context_ref": strategy_context_id,
        "durable_vision": (
            "ProductOS becomes the repo-native operating system that helps a PM understand the bet, carry strategy into execution, "
            "and move from evidence to action without rebuilding context by hand."
        ),
        "near_term_product_goal": (
            f"Turn the mission '{mission_title}' into a strategy-ready decision packet before concept and PRD work expands."
        ),
        "problem_space_summary": (
            "ProductOS can generate downstream artifacts, but it still needs a clearer strategy spine so product direction, value, and metric logic stay explicit."
        ),
        "solution_direction_summary": (
            "Generate strategy context, product vision, and market posture before downstream problem framing so the mission stays coherent through the full loop."
        ),
        "target_segment_refs": segment_refs,
        "priority_persona_refs": persona_refs,
        "customer_value_statement": (
            f"{mission_target_user} should spend less time reconstructing strategic intent and more time deciding what to believe, prioritize, and test next."
        ),
        "business_value_statement": (
            f"A strategy-ready mission packet supports {business_goal.lower()} while keeping ProductOS grounded in explicit repo-visible evidence."
        ),
        "differentiation_statement": (
            "ProductOS links mission, strategy, market posture, and downstream delivery artifacts through repo-native contracts instead of loose prompts or disconnected docs."
        ),
        "north_star_metric": "time_to_strategy_ready_discovery_packet_hours",
        "north_star_definition": (
            "Elapsed time from mission intake to a reviewable strategy and problem-framing packet that a PM can use to choose the next bet."
        ),
        "input_guardrail_metrics": [
            {
                "metric_name": "mission_to_strategy_trace_completeness",
                "metric_type": "input",
                "definition": "Percent of accepted discovery packets that preserve mission, strategy, and market references.",
                "target": "100%",
            },
            {
                "metric_name": "unsupported_strategy_claim_incidents",
                "metric_type": "guardrail",
                "definition": "Count of strategy recommendations that cannot be traced to mission evidence or accepted artifacts.",
                "target": "0",
            },
        ],
        "next_bets": [
            "Preserve the strategy packet through problem framing and PRD generation.",
            "Use the accepted strategy refs to constrain later document sync and presentation work.",
        ],
        "open_questions": [
            "Which strategy signals should be visible in the default PM-facing packet?"
        ],
        "evidence_refs": [
            {
                "source_type": "strategy_context",
                "source_id": strategy_context_id,
                "justification": "The strategy context defines the mission linkage, business outcomes, and constraints for the near-term product goal.",
            }
        ],
        "created_at": generated_at,
    }

    strategy_option_set = {
        "schema_version": "1.0.0",
        "strategy_option_set_id": strategy_option_set_id,
        "workspace_id": workspace_id,
        "decision_statement": (
            f"Which ProductOS strategy path should the mission '{mission_title}' use to create the fastest reviewable PM value?"
        ),
        "options": [
            {
                "option_id": "option_traceability_first",
                "title": "Lead with mission-linked traceability",
                "option_thesis": "Win by turning one mission into a reviewable strategy and execution packet with less PM reconstruction.",
                "upside_case": "ProductOS becomes easier to trust because mission, strategy, and downstream work stay linked.",
                "failure_mode": "The packet is coherent but buyers still want more visible automation before they care.",
                "dependency_burden": "low",
                "reversibility": "easy",
                "portfolio_interaction": "Strengthens the repo-native evidence and validation posture already present in the product.",
                "org_capability_requirement": "Strong schema discipline and reliable downstream artifact linkage.",
            },
            {
                "option_id": "option_autonomy_first",
                "title": "Lead with broader autonomous drafting",
                "option_thesis": "Win by making ProductOS feel much more autonomous across early PM phases right away.",
                "upside_case": "The product appears faster and more impressive in short demos.",
                "failure_mode": "Claim quality and PM trust weaken because autonomy expands before strategy and evidence are explicit.",
                "dependency_burden": "high",
                "reversibility": "moderate",
                "portfolio_interaction": "Pulls focus toward visible drafting breadth instead of decision quality and traceability.",
                "org_capability_requirement": "Higher tolerance for evidence ambiguity and broader prompt-driven behavior.",
            },
            {
                "option_id": "option_services_first",
                "title": "Lead with services-heavy mission setup",
                "option_thesis": "Win by using hands-on setup and review support to make the mission packet work before more productization happens.",
                "upside_case": "Early customers get stronger guided outcomes despite product gaps.",
                "failure_mode": "The workflow depends too much on human setup and does not prove a scalable product wedge.",
                "dependency_burden": "moderate",
                "reversibility": "easy",
                "portfolio_interaction": "May help early adoption but weakens the signal that ProductOS itself creates the value.",
                "org_capability_requirement": "High PM and implementation support capacity.",
            },
        ],
        "recommended_option_id": "option_traceability_first",
        "created_at": generated_at,
    }

    market_strategy = {
        "schema_version": "1.0.0",
        "market_strategy_brief_id": market_strategy_id,
        "workspace_id": workspace_id,
        "title": f"Market strategy brief: {mission_title}",
        "strategy_question": (
            f"How should ProductOS win for the mission '{mission_title}' while improving PM judgment before expanding broader automation?"
        ),
        "category_definition": (
            "AI-assisted PM operating systems that turn mission, evidence, and decisions into strategy-ready execution with less reconstruction."
        ),
        "category_maturity": "growing",
        "strategic_posture": "challenger",
        "market_role_goal": (
            "Beat broad work platforms on traceability, decision quality, and PM-specific strategy framing rather than generic workspace breadth."
        ),
        "target_market_scope": (
            "B2B product teams that already feel recurring planning and execution reconstruction costs and want a PM-specific operating layer."
        ),
        "strategy_context_ref": strategy_context_id,
        "product_vision_ref": product_vision_id,
        "market_analysis_ref": f"market_analysis_brief_{workspace_id}",
        "competitor_dossier_ref": f"competitor_dossier_{workspace_id}",
        "strategy_option_set_ref": strategy_option_set_id,
        "beachhead_segment_refs": segment_refs,
        "priority_persona_refs": persona_refs,
        "buyer_archetype_refs": persona_refs,
        "operator_archetype_refs": persona_refs,
        "competitive_reference_set": [
            "Broad PM platforms",
            "Execution suites",
            "Internal PM templates and docs",
            "Status quo manual reconstruction",
        ],
        "offering_definition": (
            "A mission-to-strategy operating layer that turns fragmented PM state into traceable, reviewable decision packets and downstream artifacts."
        ),
        "offering_type": "decision_layer",
        "positioning_statement": (
            "For PM teams that already have tools but still rebuild context by hand, ProductOS is the operating layer that keeps mission, strategy, and execution traceable enough to trust."
        ),
        "value_wedge": "Mission-linked strategy clarity with PM-specific traceability.",
        "right_to_win": (
            "ProductOS already combines structured artifacts, workflow state, and validation in a repo-native surface that broad suites do not center."
        ),
        "critical_assumptions": [
            "PMs will value a mission-linked strategy packet enough to review it before broader automation is added.",
            "The repo-native artifact chain is a real buyer-facing wedge instead of an internal implementation detail.",
        ],
        "proof_requirements": [
            "PMs can move from mission to strategy-ready problem framing without reopening raw source notes.",
            "The system preserves mission, strategy, and market refs when strategy is carried into downstream problem framing.",
            "The strategy spine sharpens judgment without broadening autonomous PM claims.",
        ],
        "proof_plan": [
            {
                "claim": "Mission-linked traceability is a differentiated wedge.",
                "proof_requirement": "PMs can explain the strategy packet and its downstream reuse without reconstructing the story from notes.",
                "validation_signal": "PM review confirms the packet is reviewable before concept and PRD work expand.",
                "owner": "PM",
            },
            {
                "claim": "The market posture can coexist with current PM tooling.",
                "proof_requirement": "ProductOS outputs can be carried into downstream artifacts without forcing replacement of incumbent tools.",
                "validation_signal": "Problem and PRD artifacts preserve the strategy refs without introducing disconnected workflow state.",
                "owner": "PM + Engineering",
            },
        ],
        "pricing_packaging_hypothesis": (
            "Team-based SaaS pricing with a premium governance tier for strategy traceability, validation, and cross-workspace support."
        ),
        "gtm_motion": (
            "Land with PM leaders or product ops teams that already feel recurring coordination and strategy reconstruction drag."
        ),
        "expansion_path": (
            "Start with strategy-ready discovery and PM operating rhythm, then expand into richer validation, memory, and delivery planning."
        ),
        "key_risks": [
            "Buyers may still overweight visible output automation over strategy coherence.",
            "Broad suites may copy the visible packet without the same traceability depth.",
        ],
        "rejected_paths": [
            {
                "path_name": "Lead with broader autonomous drafting",
                "rejection_reason": "Broader drafting autonomy would increase visible output but weaken the evidence-backed mission and strategy posture ProductOS can defend today.",
            }
        ],
        "decision_readiness": "decision_ready",
        "claim_confidence": "high",
        "review_status": "commit_ready",
        "linked_artifact_ids": [mission_id, strategy_context_id, product_vision_id, strategy_option_set_id],
        "evidence_refs": [
            {
                "source_type": "other",
                "source_id": mission_id,
                "justification": "The mission keeps the market choice grounded in the accepted customer problem and business goal.",
            },
            {
                "source_type": "other",
                "source_id": product_vision_id,
                "justification": "The product vision defines the near-term goal, differentiation, and north-star logic that the challenger posture must support.",
            },
        ],
        "open_questions": [
            "Which part of the strategy wedge should be most visible in the first PM-facing packet?"
        ],
        "recommendation": "commit_posture",
        "created_at": generated_at,
    }

    problem_brief = {
        "schema_version": "1.1.0",
        "problem_brief_id": f"problem_brief_{mission_slug}_mission_discover",
        "workspace_id": workspace_id,
        "title": f"Problem Brief: {mission_title}",
        "problem_summary": customer_problem,
        "strategic_fit_summary": (
            "This mission fits the current ProductOS posture because the repo can turn a few high-signal PM answers "
            "into governed discovery artifacts before broader execution begins."
        ),
        "posture_alignment": "challenger",
        "why_this_problem_now": (
            f"ProductOS should prove the mission '{mission_title}' through a bounded discover loop before expanding into broader automation."
        ),
        "why_this_problem_for_this_segment": (
            f"{mission_target_user} benefits when ProductOS reduces reconstruction work and keeps execution grounded in one explicit mission."
        ),
        "problem_severity": {
            "customer_pain": "high",
            "workflow_frequency": "high",
            "evidence_strength": "moderate",
            "severity_rationale": (
                "The mission captures an immediate customer problem and business goal, so the bounded discover packet should treat this as a high-severity execution problem."
            ),
        },
        "target_segment_refs": segment_refs,
        "target_persona_refs": persona_refs,
        "linked_entity_refs": linked_entity_refs,
        "evidence_refs": evidence_refs,
        "upstream_artifact_ids": [mission_id, strategy_context_id, product_vision_id, strategy_option_set_id, market_strategy_id],
        "canonical_persona_archetype_pack_id": persona_archetype_pack_id,
        "artifact_trace_map_id": f"artifact_trace_map_problem_brief_{mission_slug}_mission_discover",
        "ralph_status": "decision_ready",
        "prioritization": _priority_profile(
            lane="must_now",
            priority_score=92,
            confidence="high",
            agentic_delivery_burden="medium",
            rationale="This problem is the accepted mission anchor, and solving it is the fastest path to proving ProductOS value without widening the claim boundary.",
            reviewer_handoff="PM should confirm the problem framing is strong enough to unlock PRD and story work without reopening mission intake.",
        ),
        "handoff_readiness_summary": "The problem is grounded in explicit mission intent, segment refs, persona refs, and evidence-backed posture fit.",
        "recommended_next_step": "prd",
        "created_at": generated_at,
    }

    concept_brief = {
        "schema_version": "1.1.0",
        "concept_brief_id": f"concept_brief_{mission_slug}_mission_discover",
        "workspace_id": workspace_id,
        "title": mission_title,
        "hypothesis": (
            f"If ProductOS uses the mission brief as the canonical discover intake, {mission_target_user} can move "
            f"from a few explicit answers to a reviewable discovery package while improving {primary_metric}."
        ),
        "positioning_hypothesis": (
            "ProductOS should behave like a governed PM operating system rather than a generic artifact generator."
        ),
        "offering_hypothesis": (
            f"The first valuable slice for this mission is a repo-native discover loop that supports {business_goal.lower()}."
        ),
        "wedge_hypothesis": (
            f"Mission-first discover for the '{mission_brief['title']}' loop is a sharper wedge than asking the PM to reconstruct the same context across phases."
        ),
        "why_now": (
            "The PM-first mission surface now exists, so discover should inherit that intent directly instead of depending on implicit self-hosting context."
        ),
        "why_us": (
            "ProductOS already has schemas, workflows, validation, and phase surfaces that can turn one mission into bounded downstream work."
        ),
        "advantage_hypothesis": (
            "A mission-linked discover path can make ProductOS feel more autonomous to the PM without widening the external claim boundary."
        ),
        "status": "candidate",
        "idea_record_ids": [mission_id],
        "strategy_artifact_ids": [strategy_context_id, product_vision_id, strategy_option_set_id, market_strategy_id],
        "target_segment_refs": problem_brief["target_segment_refs"],
        "target_persona_refs": problem_brief["target_persona_refs"],
        "linked_entity_refs": problem_brief["linked_entity_refs"],
        "canonical_persona_archetype_pack_id": persona_archetype_pack_id,
        "artifact_trace_map_id": f"artifact_trace_map_concept_brief_{mission_slug}_mission_discover",
        "ralph_status": "review_needed",
        "prioritization": _priority_profile(
            lane="must_now",
            priority_score=88,
            confidence="moderate",
            agentic_delivery_burden="medium",
            rationale="The concept is the smallest coherent wedge that connects the mission problem to a bounded governed discover product surface.",
            reviewer_handoff="PM should review wedge sharpness and confirm that the concept preserves the accepted mission boundary before broadening execution.",
        ),
        "must_be_true_assumptions": [
            "The mission brief captures enough explicit truth to start a bounded discover loop.",
            "ProductOS can preserve PM review gates while generating first-pass discovery artifacts."
        ],
        "open_questions": [
            f"Which downstream phase should follow the current {mission_operating_mode} mission mode once discover outputs are accepted?"
        ],
        "uncertainty_map_refs": [mission_brief["mission_brief_id"]],
        "risk_summary": [
            "The concept becomes weak if the mission brief is too thin to support downstream prioritization and handoff.",
            "The wedge loses clarity if ProductOS overreaches beyond governed discover outputs in the first release slice.",
        ],
        "handoff_readiness_summary": "The concept is reviewable but still expects PM confirmation on wedge shape and downstream routing.",
        "created_at": generated_at,
    }

    prd = {
        "schema_version": "1.1.0",
        "prd_id": f"prd_{mission_slug}_mission_discover",
        "workspace_id": workspace_id,
        "title": f"PRD: {mission_title}",
        "problem_summary": problem_brief["problem_summary"],
        "outcome_summary": (
            f"Help {mission_target_user} achieve {business_goal.lower()} through a bounded ProductOS execution loop."
        ),
        "scope_summary": (
            f"Use mission-first discover generation to turn the mission '{mission_title}' into a strategy context brief, product vision brief, "
            f"market strategy brief, problem brief, concept brief, and PRD package that downstream ProductOS phases can reuse without reconstructing intent."
        ),
        "strategic_context_summary": (
            "The PRD should preserve the mission-first challenger posture: a governed discover spine that improves PM outcomes without claiming broader autonomous PM coverage."
        ),
        "value_hypothesis": (
            f"If ProductOS keeps mission, strategy, segment, and persona truth linked, {mission_target_user} should need materially less reconstruction work across discover and downstream handoff."
        ),
        "target_outcomes": [
            f"Improve {primary_metric} through a smaller amount of PM reconstruction work.",
            "Increase the reviewability of the first discovery-to-delivery packet.",
        ],
        "target_segment_refs": problem_brief["target_segment_refs"],
        "target_persona_refs": problem_brief["target_persona_refs"],
        "linked_entity_refs": concept_brief["linked_entity_refs"],
        "upstream_artifact_ids": [
            mission_id,
            strategy_context_id,
            product_vision_id,
            strategy_option_set_id,
            market_strategy_id,
            problem_brief["problem_brief_id"],
            concept_brief["concept_brief_id"],
        ],
        "canonical_persona_archetype_pack_id": persona_archetype_pack_id,
        "artifact_trace_map_id": f"artifact_trace_map_prd_{mission_slug}_mission_discover",
        "ralph_status": "review_needed",
        "prioritization": _priority_profile(
            lane="must_now",
            priority_score=84,
            confidence="moderate",
            agentic_delivery_burden="medium",
            rationale="The PRD packages the accepted mission into a bounded execution spine and should be prioritized immediately after the problem and concept are judged reviewable.",
            reviewer_handoff="Design and engineering should review scope boundaries before any story or acceptance automation expands the slice.",
        ),
        "scope_boundaries": [
            "Stay within the mission-first discover packet and its direct downstream reuse.",
            "Do not broaden the slice into later lifecycle automation until PM review explicitly approves the move.",
        ],
        "out_of_scope": [
            "Broad autonomous PM claims beyond the evidence-backed discover and handoff packet.",
            "Replacing incumbent PM or execution systems as part of this bounded slice.",
        ],
        "open_questions": [
            f"What is the minimum handoff package needed after discover for the current {mission_operating_mode} mission mode?",
        ],
        "handoff_risks": [
            "Downstream teams may infer broader autonomy than the release boundary supports if scope boundaries are not explicit.",
            "Story generation will become noisy if the mission-linked prioritization and persona truth are dropped.",
        ],
        "generated_at": generated_at,
    }

    return {
        "strategy_context_brief": strategy_context,
        "product_vision_brief": product_vision,
        "strategy_option_set": strategy_option_set,
        "market_strategy_brief": market_strategy,
        "problem_brief": problem_brief,
        "concept_brief": concept_brief,
        "prd": prd,
    }


def format_mission_brief_markdown(mission_brief: dict[str, Any]) -> str:
    lines = [
        f"Status: active",
        f"Audience: {', '.join(mission_brief['audience'])}",
        f"Owner: {mission_brief.get('review_gate_owner', 'ProductOS PM')}",
        f"Updated At: {mission_brief['updated_at'][:10]}",
        "",
        "## Mission",
        "",
        f"- Title: `{mission_brief['title']}`",
        f"- Portfolio: `{mission_brief.get('portfolio_id', mission_brief['workspace_id'])}`",
        f"- Target user: `{mission_brief['target_user']}`",
        f"- Maturity band: `{mission_brief.get('maturity_band', 'zero_to_one')}`",
        f"- Operating mode: `{mission_brief['operating_mode']}`",
        f"- Entry phase: `{mission_brief['mission_router']['entry_phase']}`",
        f"- Phase sequence: {', '.join(f'`{item}`' for item in mission_brief['mission_router']['phase_sequence'])}",
        f"- Reviewer lane: `{mission_brief['mission_router']['primary_reviewer_lane']}`",
        "",
        mission_brief["mission_summary"],
        "",
        "## Core Questions",
        "",
        f"- Customer problem: {mission_brief['customer_problem']}",
        f"- Business goal: {mission_brief['business_goal']}",
        "",
        "## Success Metrics",
        "",
    ]
    for item in mission_brief["success_metrics"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Constraints", ""])
    for item in mission_brief["constraints"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Primary Outcomes", ""])
    for item in mission_brief.get("primary_outcomes", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Primary KPIs", ""])
    for item in mission_brief.get("primary_kpis", []):
        lines.append(f"- {item}")
    if mission_brief.get("known_risks"):
        lines.extend(["", "## Known Risks", ""])
        for item in mission_brief["known_risks"]:
            lines.append(f"- {item}")
    if mission_brief.get("stage_goals"):
        lines.extend(["", "## Stage Goals", ""])
        for phase, goal in mission_brief["stage_goals"].items():
            lines.append(f"- `{phase}`: {goal}")
    lines.extend(["", "## Steering Norms", ""])
    for item in mission_brief["steering_context"]["operating_norms"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Memory Priority Order", ""])
    for item in mission_brief["steering_context"]["memory_priority_order"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Primary Workflow Path", ""])
    for item in mission_brief["primary_workflow_refs"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Steering References", ""])
    for item in mission_brief["steering_context"]["steering_refs"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Next Action", "", mission_brief["next_action"], ""])
    return render_governed_markdown(
        title="Mission Brief",
        body_lines=lines,
        version_number=1,
        status="review_needed",
        updated_at=mission_brief["updated_at"],
        updated_by="ProductOS PM",
        change_summary="Created or refreshed the canonical mission brief for the bounded execution slice.",
        source_artifact_ids=[mission_brief["mission_brief_id"]],
    )


def _refresh_delivery_and_launch_artifacts(
    workspace_path: Path,
    *,
    mission_brief: dict[str, Any],
) -> None:
    artifacts_dir = workspace_path / "artifacts"
    mission_title = mission_brief["title"]
    mission_problem = mission_brief["customer_problem"]
    mission_goal = mission_brief["business_goal"]
    mission_id = mission_brief["mission_brief_id"]
    mission_doc_path = "docs/planning/mission-brief.md"
    mission_slug = _slug(mission_title)
    mission_prd_id = f"prd_{mission_slug}_mission_discover"
    mission_persona_archetype_pack_id = f"persona_archetype_pack_{mission_slug}_mission_strategy"

    story_pack_path = artifacts_dir / "story_pack.json"
    if story_pack_path.exists():
        story_pack = _load_json(story_pack_path)
        story_pack["source_prd_id"] = mission_prd_id
        story_pack["canonical_persona_archetype_pack_id"] = mission_persona_archetype_pack_id
        for story in story_pack.get("stories", []):
            story["title"] = _append_once(story["title"], f"for {mission_title}")
            story["narrative"] = _append_once(
                story["narrative"],
                f"This delivery path should stay tied to the mission '{mission_title}' and the customer problem: {mission_problem}",
            )
            context_refs = list(story.get("implementation_context_refs", []))
            if not any(ref.get("path") == mission_doc_path for ref in context_refs):
                context_refs.append(
                    {
                        "context_type": "markdown",
                        "title": "Mission Brief",
                        "path": mission_doc_path,
                        "summary": f"Canonical PM-first mission for '{mission_title}'.",
                    }
                )
            story["implementation_context_refs"] = context_refs
        _write_json(story_pack_path, story_pack)

    acceptance_path = artifacts_dir / "acceptance_criteria_set.json"
    if acceptance_path.exists():
        acceptance = _load_json(acceptance_path)
        acceptance["source_prd_id"] = mission_prd_id
        acceptance["canonical_persona_archetype_pack_id"] = mission_persona_archetype_pack_id
        for criterion in acceptance.get("criteria", []):
            criterion["statement"] = _append_once(
                criterion["statement"],
                f"This should remain explicitly aligned with the mission '{mission_title}'.",
            )
        _write_json(acceptance_path, acceptance)

    release_readiness_path = artifacts_dir / "release_readiness.json"
    if release_readiness_path.exists():
        release_readiness = _load_json(release_readiness_path)
        for role in release_readiness.get("launch_roles", []):
            role["responsibility"] = _append_once(
                role["responsibility"],
                f"Keep the mission '{mission_title}' visible in release decisions.",
            )
        for check in release_readiness.get("checks", []):
            notes = check.get("notes", "")
            check["notes"] = _append_once(
                notes,
                f"Mission traceability for '{mission_title}' remains explicit through delivery and launch readiness.",
            )
        _write_json(release_readiness_path, release_readiness)

    release_note_path = artifacts_dir / "release_note.json"
    if release_note_path.exists():
        release_note = _load_json(release_note_path)
        release_note["title"] = _append_once(release_note["title"], f"for {mission_title}")
        release_note["summary"] = _append_once(
            release_note["summary"],
            f"This release also advances the mission '{mission_title}'.",
        )
        if "classification_rationale" in release_note:
            release_note["classification_rationale"] = _append_once(
                release_note["classification_rationale"],
                f"The release should stay tied to the business goal: {mission_goal}",
            )
        _write_json(release_note_path, release_note)

    outcome_review_path = artifacts_dir / "outcome_review.json"
    if outcome_review_path.exists():
        outcome_review = _load_json(outcome_review_path)
        outcome_review["review_scope"] = _append_once(
            outcome_review["review_scope"],
            f"Check whether it still advances the mission '{mission_title}'.",
        )
        outcome_review["evidence_refs"] = list(dict.fromkeys([*outcome_review.get("evidence_refs", []), mission_id]))
        outcome_review["adoption_notes"] = list(
            dict.fromkeys(
                [
                    *outcome_review.get("adoption_notes", []),
                    f"The workspace should keep the mission '{mission_title}' visible through delivery, launch, and review.",
                ]
            )
        )
        outcome_review["next_action"] = _append_once(
            outcome_review["next_action"],
            f"Reconfirm the mission problem remains explicit: {mission_problem}",
        )
        outcome_names = {item.get("outcome_name") for item in outcome_review.get("target_outcomes", [])}
        mission_outcome_name = "Mission traceability stays explicit"
        if mission_outcome_name not in outcome_names:
            outcome_review["target_outcomes"].append(
                {
                    "outcome_name": mission_outcome_name,
                    "expected_signal": f"Delivery, launch, and review outputs should keep the mission '{mission_title}' explicit.",
                    "observed_signal": f"The workspace now carries the mission '{mission_title}' through its seeded delivery and launch artifacts.",
                    "status": "met",
                }
            )
        _write_json(outcome_review_path, outcome_review)


def _append_manifest_artifact_path(workspace_path: Path, relative_path: str) -> None:
    manifest_path = workspace_path / "workspace_manifest.yaml"
    if not manifest_path.exists():
        return
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    artifact_paths = manifest.setdefault("artifact_paths", [])
    if relative_path not in artifact_paths:
        artifact_paths.append(relative_path)
        manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")


def sync_canonical_discover_artifacts(
    workspace_dir: Path | str,
    *,
    mission_brief: dict[str, Any],
    generated_at: str,
    strategy_context_brief: dict[str, Any] | None = None,
    product_vision_brief: dict[str, Any] | None = None,
    strategy_option_set: dict[str, Any] | None = None,
    market_strategy_brief: dict[str, Any] | None = None,
    problem_brief: dict[str, Any] | None = None,
    concept_brief: dict[str, Any] | None = None,
    prd: dict[str, Any] | None = None,
) -> list[str]:
    workspace_path = Path(workspace_dir).resolve()
    artifacts_dir = workspace_path / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    workspace_id = mission_brief["workspace_id"]
    discover_bundle = {
        "strategy_context_brief": strategy_context_brief,
        "product_vision_brief": product_vision_brief,
        "strategy_option_set": strategy_option_set,
        "market_strategy_brief": market_strategy_brief,
        "problem_brief": problem_brief,
        "concept_brief": concept_brief,
        "prd": prd,
    }
    if any(payload is None for payload in discover_bundle.values()):
        discover_bundle = build_strategy_discover_bundle_from_mission(
            workspace_id=workspace_id,
            generated_at=generated_at,
            mission_brief=mission_brief,
        )

    synced_files: list[str] = []
    for filename, payload in {
        "strategy_context_brief.json": discover_bundle["strategy_context_brief"],
        "product_vision_brief.json": discover_bundle["product_vision_brief"],
        "strategy_option_set.json": discover_bundle["strategy_option_set"],
        "market_strategy_brief.json": discover_bundle["market_strategy_brief"],
        "problem_brief.json": discover_bundle["problem_brief"],
        "concept_brief.json": discover_bundle["concept_brief"],
        "prd.json": discover_bundle["prd"],
    }.items():
        target_path = artifacts_dir / filename
        if not _can_replace_discover_artifact(target_path):
            continue
        _write_json(target_path, payload)
        synced_files.append(filename)
        _append_manifest_artifact_path(workspace_path, f"artifacts/{filename}")
    return synced_files


def init_mission_in_workspace(
    workspace_dir: Path | str,
    *,
    title: str,
    target_user: str,
    customer_problem: str,
    business_goal: str,
    success_metrics: list[str],
    constraints: list[str] | None,
    audience: list[str] | None,
    operating_mode: str,
    generated_at: str,
    maturity_band: str = "zero_to_one",
    primary_outcomes: list[str] | None = None,
    primary_kpis: list[str] | None = None,
    review_gate_owner: str = "ProductOS PM",
    portfolio_id: str | None = None,
    stage_goals: dict[str, str] | None = None,
    known_risks: list[str] | None = None,
) -> dict[str, Any]:
    workspace_path = Path(workspace_dir).resolve()
    mission_brief = build_mission_brief(
        workspace_path,
        title=title,
        target_user=target_user,
        customer_problem=customer_problem,
        business_goal=business_goal,
        success_metrics=success_metrics,
        constraints=constraints,
        audience=audience,
        operating_mode=operating_mode,
        generated_at=generated_at,
        maturity_band=maturity_band,
        primary_outcomes=primary_outcomes,
        primary_kpis=primary_kpis,
        review_gate_owner=review_gate_owner,
        portfolio_id=portfolio_id,
        stage_goals=stage_goals,
        known_risks=known_risks,
    )
    artifacts_dir = workspace_path / "artifacts"
    docs_dir = workspace_path / "docs" / "planning"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)
    (artifacts_dir / "mission_brief.json").write_text(
        json.dumps(mission_brief, indent=2) + "\n",
        encoding="utf-8",
    )
    (docs_dir / "mission-brief.md").write_text(
        format_mission_brief_markdown(mission_brief) + "\n",
        encoding="utf-8",
    )
    (docs_dir / "steering-context.md").write_text(
        format_steering_context_markdown(mission_brief) + "\n",
        encoding="utf-8",
    )
    sync_canonical_discover_artifacts(
        workspace_path,
        mission_brief=mission_brief,
        generated_at=generated_at,
    )
    _refresh_delivery_and_launch_artifacts(
        workspace_path,
        mission_brief=mission_brief,
    )
    _rebase_safe_lifecycle_trace(
        workspace_path,
        mission_brief=mission_brief,
        generated_at=generated_at,
    )
    seed_pm_superpower_artifacts(
        workspace_path,
        mission_brief=mission_brief,
        generated_at=generated_at,
    )
    return mission_brief


def load_mission_brief_from_workspace(workspace_dir: Path | str) -> dict[str, Any] | None:
    path = Path(workspace_dir).resolve() / "artifacts" / "mission_brief.json"
    if not path.exists():
        return None
    return _load_json(path)
