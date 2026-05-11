#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from components.presentation.python.productos_presentation import (
    build_evidence_pack,
    build_presentation_story,
    build_publish_check,
    build_ppt_export_plan,
    build_render_spec,
    build_slide_spec,
    build_visual_map_render_spec,
    build_visual_map_slide_spec,
    write_html_presentation,
    write_ppt_presentation,
)
from components.workflow_corridor.python.productos_workflow_corridor import (
    build_workflow_corridor_bundle,
    write_corridor_html,
    write_corridor_payload,
)
from components.journey_engine.python.journey_visual_renderer import (
    render_customer_journey_map_html,
)
from core.python.productos_runtime import (
    ADOPTION_ARTIFACT_SCHEMAS,
    RESEARCH_DISCOVERY_ARTIFACT_SCHEMAS,
    RESEARCH_FEED_REGISTRY_ARTIFACT_SCHEMAS,
    RESEARCH_PLANNING_ARTIFACT_SCHEMAS,
    RESEARCH_RUNTIME_ARTIFACT_SCHEMAS,
    THREAD_REVIEW_RELEASE_ARTIFACT_SCHEMAS,
    adopt_workspace_from_source,
    build_external_research_feed_registry_from_workspace,
    build_external_research_plan_from_workspace,
    build_next_version_bundle_from_workspace,
    build_cockpit_bundle_from_workspace,
    build_cross_product_insight_index,
    build_agent_context,
    build_prd_boundary_report,
    build_runtime_adapter_registry,
    build_portfolio_state_from_workspaces,
    build_thread_review_bundle_from_workspace,
    build_thread_review_presentation_package,
    build_thread_review_release_bundle_from_workspace,
    build_workspace_adoption_bundle_from_source,
    build_v5_lifecycle_bundle_from_workspace,
    build_v5_cutover_plan_from_workspace,
    build_v6_lifecycle_bundle_from_workspace,
    build_v6_cutover_plan_from_workspace,
    build_v7_lifecycle_bundle_from_workspace,
    build_v7_cutover_plan_from_workspace,
    build_v9_lifecycle_bundle_from_workspace,
    build_v9_cutover_plan_from_workspace,
    format_item_lifecycle_state,
    format_lifecycle_stage_snapshot,
    format_v5_cutover_plan_markdown,
    format_v6_cutover_plan_markdown,
    format_v7_cutover_plan_markdown,
    format_v9_cutover_plan_markdown,
    init_workspace_from_template,
    inspect_v9_lifecycle_enrichment_state,
    ingest_pm_note,
    load_item_lifecycle_state_from_workspace,
    load_lifecycle_stage_snapshot_from_workspace,
    discover_external_research_sources_from_workspace,
    collect_memory_review_items,
    load_phase_packet_from_workspace,
    load_competitor_registry,
    load_product_record_from_workspace,
    load_problem_register,
    research_workspace_from_manifest,
    render_cockpit_html,
    render_all_living_documents,
    run_external_research_loop_from_workspace,
    summarize_research_posture,
    summarize_strategy_refresh_posture,
    sync_canonical_discovery_operations_artifacts,
    summarize_v5_lifecycle_bundle,
    summarize_v6_lifecycle_bundle,
    summarize_v7_lifecycle_bundle,
    summarize_v9_lifecycle_bundle,
    init_mission_in_workspace,
    load_mission_brief_from_workspace,
    sync_memory_registers,
    sync_canonical_discover_artifacts,
    write_phase_packet_for_workspace,
    write_prd_boundary_report,
    write_pm_note_delta_proposal,
    write_thread_review_index_site,
    write_thread_review_markdown,
    write_thread_review_package,
    write_thread_review_page,
    synthesize_customer_journey_map,
    generate_screen_flow_svg,
    generate_screen_flow_from_journey_stages,
    write_screen_flow_html,
    generate_impact_propagation_map,
)
from core.python.productos_runtime.validation import inspect_workspace_source_note_card_refs
from core.python.productos_runtime.next_version import NEXT_VERSION_ARTIFACT_SCHEMAS
from core.python.productos_runtime.v5 import V5_ARTIFACT_SCHEMAS
from core.python.productos_runtime.v6 import V6_ARTIFACT_SCHEMAS
from core.python.productos_runtime.v7 import V7_ARTIFACT_SCHEMAS
from core.python.productos_runtime.v9 import V9_ARTIFACT_SCHEMAS
from core.python.productos_runtime.release import evaluate_promotion_gate, run_public_release
from core.python.productos_runtime.visual_os import (
    build_visual_direction_plan,
    build_visual_quality_review_for_corridor,
    build_visual_quality_review_for_deck,
    build_visual_quality_review_for_map,
    infer_visual_review_target,
)
from core.python.productos_runtime.living_system import (
    build_regeneration_queue,
    detect_circular_dependencies,
    process_regeneration_item,
)
from core.python.productos_runtime.markdown_renderer import render_living_document
from core.python.productos_runtime.takeover import (
    TAKEOVER_ARTIFACT_SCHEMAS,
    build_takeover_bundle,
    build_takeover_brief,
    build_problem_space_map,
    build_roadmap_recovery_brief,
    build_visual_product_atlas,
    build_takeover_feature_scorecard,
    render_takeover_atlas_html,
)
from core.python.productos_runtime.export_pipeline import export_artifact
from core.python.productos_runtime.llm import default_provider
from components.prototype.python.prototype_engine import write_prototype_bundle

SCHEMA_DIR = ROOT / "core" / "schemas" / "artifacts"
PHASE_ARTIFACTS = {
    "discover": [
        "cockpit_state",
        "orchestration_state",
        "intake_routing_state",
        "memory_retrieval_state",
        "context_pack",
        "discover_strategy_context_brief",
        "discover_product_vision_brief",
        "discover_strategy_option_set",
        "discover_market_strategy_brief",
        "discover_problem_brief",
        "discover_research_handoff",
        "discover_research_notebook",
        "discover_research_brief",
        "discover_external_research_plan",
        "discover_external_research_source_discovery",
        "discover_external_research_review",
        "discover_framework_registry",
        "discover_competitor_dossier",
        "discover_customer_pulse",
        "discover_market_analysis_brief",
        "discover_landscape_matrix",
        "discover_market_sizing_brief",
        "discover_market_share_brief",
        "discover_opportunity_portfolio_view",
        "discover_prioritization_decision_record",
        "discover_feature_prioritization_brief",
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
        "presentation_visual_direction_plan",
        "presentation_visual_quality_review",
        "workflow_corridor_spec",
        "corridor_proof_pack",
        "corridor_narrative_plan",
        "corridor_render_model",
        "corridor_publish_check",
        "corridor_visual_direction_plan",
        "corridor_visual_quality_review",
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
MISSION_PHASE_ORDER = ["discover", "align", "operate", "improve"]
ADOPTION_ARTIFACTS = list(ADOPTION_ARTIFACT_SCHEMAS.keys())
RESEARCH_RUNTIME_ARTIFACTS = list(RESEARCH_RUNTIME_ARTIFACT_SCHEMAS.keys())
RESEARCH_PLANNING_ARTIFACTS = list(RESEARCH_PLANNING_ARTIFACT_SCHEMAS.keys())
RESEARCH_FEED_REGISTRY_ARTIFACTS = list(RESEARCH_FEED_REGISTRY_ARTIFACT_SCHEMAS.keys())
RESEARCH_DISCOVERY_ARTIFACTS = list(RESEARCH_DISCOVERY_ARTIFACT_SCHEMAS.keys())
START_MODE_TO_MATURITY_BAND = {
    "startup": "zero_to_one",
    "enterprise": "one_to_ten",
}
START_FIRST_WIN_CHOICES = [
    {
        "value": "strategy_brief",
        "label": "Strategy brief",
        "description": "Clarify product direction before downstream execution expands.",
        "success_metric": "time to reviewable strategy brief",
        "primary_outcome": "Create one reviewable strategy brief",
        "title": "Create the first reviewable strategy brief",
    },
    {
        "value": "problem_brief",
        "label": "Problem brief",
        "description": "Frame the customer problem clearly before solution work grows.",
        "success_metric": "time to reviewable problem brief",
        "primary_outcome": "Create one reviewable problem brief",
        "title": "Create the first reviewable problem brief",
    },
    {
        "value": "prd",
        "label": "PRD",
        "description": "Turn the first product slice into one reviewable spec quickly.",
        "success_metric": "time to reviewable PRD",
        "primary_outcome": "Create one reviewable PRD",
        "title": "Create the first reviewable PRD",
    },
    {
        "value": "research_pack",
        "label": "Research pack",
        "description": "Collect the first evidence-backed research package for the product.",
        "success_metric": "time to reviewable research pack",
        "primary_outcome": "Create one reviewable research pack",
        "title": "Create the first reviewable research pack",
    },
    {
        "value": "roadmap",
        "label": "Roadmap / plan",
        "description": "Shape the first reviewable plan for what the team should do next.",
        "success_metric": "time to reviewable roadmap",
        "primary_outcome": "Create one reviewable roadmap",
        "title": "Create the first reviewable roadmap",
    },
]
START_FIRST_WIN_BY_VALUE = {
    choice["value"]: choice for choice in START_FIRST_WIN_CHOICES
}


def _default_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _workspace_dir(args: argparse.Namespace) -> Path:
    if args.workspace_dir is not None:
        return args.workspace_dir

    raise SystemExit(
        "Workspace selection is explicit. Pass --workspace-dir to run this command against "
        "a specific workspace, or create one with `./productos start`."
    )


def _build_bundle(args: argparse.Namespace) -> dict[str, dict]:
    return build_next_version_bundle_from_workspace(
        _workspace_dir(args),
        generated_at=args.generated_at,
        adapter_name=args.adapter,
    )


def _try_build_bundle(args: argparse.Namespace) -> dict[str, dict] | None:
    try:
        return _build_bundle(args)
    except Exception:
        return None


def _build_v9_program_state(
    workspace_dir: Path,
    *,
    generated_at: str,
    adapter_name: str,
    bundle: dict[str, dict] | None,
) -> dict[str, object]:
    return inspect_v9_lifecycle_enrichment_state(
        workspace_dir,
        generated_at=generated_at,
        adapter_name=adapter_name,
        next_version_bundle=bundle,
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


def _write_source_note_cards(output_dir: Path, bundle: dict[str, dict]) -> None:
    source_note_cards = bundle.get("source_note_cards") or bundle.get("discover_source_note_cards") or {}
    if not isinstance(source_note_cards, dict):
        return
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, payload in source_note_cards.items():
        with (output_dir / filename).open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
            handle.write("\n")


def _write_json_payload(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def _iter_note_inputs(workspace_dir: Path) -> list[Path]:
    candidates: list[Path] = []
    for folder in (workspace_dir / "inbox" / "raw-notes", workspace_dir / "feedback"):
        if not folder.exists():
            continue
        for path in sorted(folder.iterdir()):
            if not path.is_file() or path.name.startswith(".") or path.name == "README.md":
                continue
            candidates.append(path)
    return candidates


def _memory_review_output_dir(workspace_dir: Path) -> Path:
    return workspace_dir / "outputs" / "operate"


def _collect_note_memory_proposals(workspace_dir: Path, generated_at: str) -> list[tuple[Path, dict[str, object]]]:
    proposals: list[tuple[Path, dict[str, object]]] = []
    for note_path in _iter_note_inputs(workspace_dir):
        proposal = ingest_pm_note(workspace_dir, note_path, generated_at=generated_at)
        if not proposal.get("proposed_deltas") and not proposal.get("memory_candidates"):
            continue
        proposals.append((note_path, proposal))
    return proposals


def _persist_note_memory_proposals(workspace_dir: Path, generated_at: str, output_dir: Path | None = None) -> list[Path]:
    proposals = _collect_note_memory_proposals(workspace_dir, generated_at)
    persisted_paths: list[Path] = []
    target_dir = output_dir or _memory_review_output_dir(workspace_dir)
    for note_path, proposal in proposals:
        proposal_path = target_dir / f"{note_path.stem}.pm_note_delta_proposal.json"
        _write_json_payload(proposal_path, proposal)
        persisted_paths.append(proposal_path)
    return persisted_paths


def _memory_freshness_label(register: dict[str, object] | None) -> str:
    if register is None:
        return "missing"
    timestamp = register.get("updated_at") if isinstance(register, dict) else None
    if not isinstance(timestamp, str):
        return "usable_with_review"
    normalized = timestamp.replace("Z", "+00:00")
    try:
        updated_at = datetime.fromisoformat(normalized)
    except ValueError:
        return "usable_with_review"
    if datetime.now(timezone.utc) - updated_at.astimezone(timezone.utc) <= timedelta(days=90):
        return "healthy"
    return "stale"


def _validate_payload_against_schema(payload: dict, schema_name: str) -> list[str]:
    validator = Draft202012Validator(_load_json(SCHEMA_DIR / schema_name))
    return [error.message for error in sorted(validator.iter_errors(payload), key=lambda item: list(item.path))]


def _entity_ref(entity_type: str, entity_id: str) -> dict[str, str]:
    return {"entity_type": entity_type, "entity_id": entity_id}


def _evidence_ref(source_type: str, source_id: str, justification: str) -> dict[str, str]:
    return {
        "source_type": source_type,
        "source_id": source_id,
        "justification": justification,
    }


def _prioritization_block(problem_statement: str) -> dict[str, object]:
    return {
        "lane": "must_now",
        "priority_score": 82,
        "confidence": "moderate",
        "agentic_delivery_burden": "medium",
        "priority_rationale": f"The problem is concrete enough to warrant an immediate discovery-to-PRD wedge for {problem_statement[:60]}.",
        "reviewer_handoff": "PM should verify the segment wedge and top unknowns before broadening scope.",
    }


def _build_new_workspace_artifacts(
    problem_statement: str,
    *,
    workspace_id: str,
    generated_at: str,
) -> dict[str, dict]:
    slug = _slugify_problem(problem_statement)
    segment_id = f"seg_{slug}"
    persona_id = f"pers_{slug}"
    trace_id = f"trace_{slug}"
    framework_id = "framework_registry_default"
    source_note_id = f"source_note_card_{slug}"
    provider = default_provider()
    provider.generate_structured(
        f"Generate a bounded PM starter set for: {problem_statement}",
        {"type": "object", "properties": {"summary": {"type": "string"}}, "required": ["summary"]},
    )

    problem_brief = {
        "schema_version": "1.1.0",
        "problem_brief_id": f"problem_brief_{slug}",
        "workspace_id": workspace_id,
        "title": f"Problem Brief: {problem_statement[:72]}",
        "problem_summary": problem_statement,
        "strategic_fit_summary": "A focused starter brief helps the PM turn raw demand into a repo-backed plan without spreadsheet drift.",
        "posture_alignment": "challenger",
        "why_this_problem_now": "Teams adopting AI-assisted PM workflows need a bounded starting point before execution expands.",
        "why_this_problem_for_this_segment": "The target segment feels the pain frequently and benefits from structured operating rhythm improvements.",
        "problem_severity": {
            "customer_pain": "high",
            "workflow_frequency": "high",
            "evidence_strength": "moderate",
            "severity_rationale": "The described problem blocks a recurring workflow and is concrete enough for immediate discovery.",
        },
        "target_segment_refs": [_entity_ref("segment", segment_id)],
        "target_persona_refs": [_entity_ref("persona", persona_id)],
        "linked_entity_refs": [_entity_ref("problem", f"prob_{slug}")],
        "evidence_refs": [_evidence_ref("other", source_note_id, "Seeded from the raw problem statement supplied at workspace creation.")],
        "upstream_artifact_ids": [f"mission_brief_{workspace_id}"],
        "canonical_persona_archetype_pack_id": f"persona_archetype_pack_{slug}",
        "artifact_trace_map_id": trace_id,
        "ralph_status": "review_needed",
        "prioritization": _prioritization_block(problem_statement),
        "handoff_readiness_summary": "Ready for guided discovery, initial competitor framing, and first-pass PRD drafting.",
        "recommended_next_step": "research",
        "created_at": generated_at,
    }
    concept_brief = {
        "schema_version": "1.1.0",
        "concept_brief_id": f"concept_brief_{slug}",
        "workspace_id": workspace_id,
        "title": f"Concept Brief: {problem_statement[:72]}",
        "hypothesis": f"If we solve '{problem_statement}', teams will reach a reviewable PM package faster with less manual reconciliation.",
        "positioning_hypothesis": "Position ProductOS as the repo-native control plane for this workflow instead of another document wrapper.",
        "offering_hypothesis": "Start with one narrow workflow slice that compounds into living docs, queue review, and execution context.",
        "wedge_hypothesis": "A tightly scoped starter workspace gives immediate value without requiring a full platform rollout.",
        "why_now": "AI-native product work is moving from drafting to managed execution, which raises the value of bounded repo truth.",
        "why_us": "The repo already contains structured artifacts, CLI surfaces, and validation loops that can express this concept cleanly.",
        "advantage_hypothesis": "Structured artifacts plus machine-readable CLI output create leverage that document-centric competitors cannot match.",
        "status": "candidate",
        "idea_record_ids": [f"idea_record_{slug}"],
        "strategy_artifact_ids": [f"problem_brief_{slug}"],
        "target_segment_refs": [_entity_ref("segment", segment_id)],
        "target_persona_refs": [_entity_ref("persona", persona_id)],
        "canonical_persona_archetype_pack_id": f"persona_archetype_pack_{slug}",
        "artifact_trace_map_id": trace_id,
        "ralph_status": "review_needed",
        "prioritization": _prioritization_block(problem_statement),
        "must_be_true_assumptions": [
            "The target PM workflow happens often enough to justify a dedicated operating system wedge.",
            "Structured artifact generation reduces review time more than ad hoc note-taking.",
        ],
        "risk_summary": [
            "The initial brief may overfit the first phrasing of the problem.",
            "Downstream artifacts need PM review before being treated as decision-ready.",
        ],
        "handoff_readiness_summary": "Ready for competitor framing, persona validation, and a bounded PRD draft.",
        "created_at": generated_at,
    }
    prd = {
        "schema_version": "1.1.0",
        "prd_id": f"prd_{slug}",
        "workspace_id": workspace_id,
        "title": f"PRD: {problem_statement[:72]}",
        "problem_summary": problem_statement,
        "outcome_summary": "Produce a reviewable first release slice that compresses PM synthesis and decision latency.",
        "scope_summary": "Cover the smallest coherent workflow wedge that makes the problem materially easier for the target PM.",
        "strategic_context_summary": "This PRD should stay bounded to a starter wedge and avoid broad platform claims.",
        "value_hypothesis": "A living, artifact-backed PM workflow will outperform static docs for this job to be done.",
        "target_outcomes": [
            "Generate a reviewable PM package in one session.",
            "Expose boundaries clearly enough that an agent or builder knows what not to build.",
        ],
        "target_segment_refs": [_entity_ref("segment", segment_id)],
        "target_persona_refs": [_entity_ref("persona", persona_id)],
        "linked_entity_refs": [_entity_ref("feature", f"feature_{slug}_starter")],
        "upstream_artifact_ids": [problem_brief["problem_brief_id"], concept_brief["concept_brief_id"]],
        "canonical_persona_archetype_pack_id": f"persona_archetype_pack_{slug}",
        "artifact_trace_map_id": trace_id,
        "ralph_status": "review_needed",
        "prioritization": _prioritization_block(problem_statement),
        "scope_boundaries": [
            "Web-first workflow only for the initial slice.",
            "Single PM persona and one high-value workflow.",
            "Repo-backed artifacts remain the only system of record.",
        ],
        "out_of_scope": [
            "Native iOS or Android applications in v1.",
            "Enterprise SSO and admin governance workflows in v1.",
            "General-purpose project management beyond the target PM wedge.",
        ],
        "open_questions": [
            "Which persona pain should be validated first?",
            "What proof most clearly differentiates this wedge from static docs?",
        ],
        "handoff_risks": [
            "Unchecked assumptions may create false confidence if discovery is skipped.",
            "Prototype screens can look complete before the underlying decision logic is proven.",
        ],
        "generated_at": generated_at,
    }
    competitor_dossier = {
        "schema_version": "1.1.0",
        "competitor_dossier_id": f"competitor_dossier_{slug}",
        "workspace_id": workspace_id,
        "title": f"Competitor Dossier: {problem_statement[:64]}",
        "competitive_frame": "Alternatives include static document stacks, project management suites, and AI drafting tools with weak system-of-record posture.",
        "comparison_basis": "Compare against tools used to capture PM context, route work, and hand off execution safely.",
        "framework_registry_ref": framework_id,
        "selected_framework_ids": ["competitive_frame", "wedge_comparison"],
        "target_segment_refs": [_entity_ref("segment", segment_id)],
        "target_persona_refs": [_entity_ref("persona", persona_id)],
        "source_artifact_ids": [problem_brief["problem_brief_id"], concept_brief["concept_brief_id"]],
        "status_quo_alternatives": ["Spreadsheets", "Notion or Confluence", "General AI chat tools"],
        "internal_build_risk": "medium",
        "competitive_landscape_status": "named_competitor_set",
        "evidence_coverage_status": "internal_only",
        "dossier_quality": "draft",
        "named_competitor_count": 2,
        "where_we_win": [
            "Repo-native truth instead of screenshot or copy-paste workflows.",
            "Machine-readable CLI surfaces for agent execution loops.",
        ],
        "where_we_lose": [
            "Category awareness compared with broader project tools.",
        ],
        "credible_wedge_for_posture": "Win by making one PM workflow fully living, reviewable, and exportable instead of broadly average.",
        "required_proof_to_displace": [
            "Show faster review cycles than static document workflows.",
            "Show cleaner agent handoff than generic AI drafting tools.",
        ],
        "prioritization_implications": [
            "Prioritize living-system proof and review-lane clarity before broadening packaging claims.",
        ],
        "competitors": [
            {
                "name": "Static Docs Stack",
                "competitor_type": "direct",
                "target_customer": "PM teams coordinating work across docs and tickets",
                "positioning_summary": "Flexible documentation but weak structured execution continuity.",
                "go_to_market_motion": "Bottom-up workspace adoption",
                "pricing_signal": "Seat-based SaaS plus wiki sprawl cost",
                "positioning_gap": "Weak machine-readable execution context and bounded review gates.",
                "strengths": ["Low friction collaboration", "Familiar workflows"],
                "weaknesses": ["Version drift", "Manual handoff overhead"],
                "where_they_win": ["Broad awareness", "Lightweight collaboration"],
                "where_they_lose": ["Structured execution continuity", "Living artifact propagation"],
                "displacement_barriers": ["Habit inertia", "Existing documentation volume"],
                "implications": ["Lead with proof of living-system leverage."],
                "evidence_refs": [source_note_id],
                "confidence": "medium",
                "last_checked_at": generated_at,
            }
        ],
        "created_at": generated_at,
    }
    persona_pack = {
        "schema_version": "1.0.0",
        "persona_pack_id": f"persona_pack_{slug}",
        "workspace_id": workspace_id,
        "title": f"Persona Pack: {problem_statement[:64]}",
        "segment_refs": [_entity_ref("segment", segment_id)],
        "personas": [
            {
                "persona_ref": _entity_ref("persona", persona_id),
                "role": "Product manager",
                "goals": [
                    "Get from raw signals to a reviewable brief quickly.",
                    "Keep downstream artifact drift visible and fixable.",
                ],
                "pains": [
                    "Manual synthesis across fragmented tools.",
                    "Weak scope boundaries that create execution sprawl.",
                ],
                "behavior_notes": [
                    "Prefers tools that produce reviewable artifacts and explicit next steps.",
                ],
            }
        ],
        "source_artifact_ids": [problem_brief["problem_brief_id"]],
        "created_at": generated_at,
    }
    market_analysis = {
        "schema_version": "1.1.0",
        "market_analysis_brief_id": f"market_analysis_brief_{slug}",
        "workspace_id": workspace_id,
        "title": f"Market Analysis Brief: {problem_statement[:60]}",
        "market_name": "AI-native PM tooling",
        "framework_registry_ref": framework_id,
        "selected_framework_ids": ["market_dynamics", "category_pressure"],
        "category_structure": [
            "Static document systems",
            "Task and workflow management tools",
            "AI drafting and agent execution surfaces",
        ],
        "category_summary": "The market is shifting from drafting assistance toward managed execution with traceable evidence and bounded automation.",
        "trend_summary": "Teams increasingly expect AI help, but trust and reviewability remain blockers for decision-driving work.",
        "market_dynamics": [
            "Execution tools are adding AI while AI tools are moving closer to system-of-record expectations.",
        ],
        "power_centers": [
            "Existing documentation suites and ticketing systems still own default workflow gravity.",
        ],
        "adoption_barriers": [
            "Teams do not trust generated output without validation and clear release boundaries.",
        ],
        "switching_costs": [
            "Process retraining and artifact migration make partial adoption easier than full rip-and-replace.",
        ],
        "market_role_implications": [
            "Lead with one narrow workflow that compounds into adjacent PM jobs.",
        ],
        "agentic_delivery_implications": [
            "Machine-readable CLI output is a prerequisite for agent-native operation.",
        ],
        "prioritization_implications": [
            "Prioritize proof of living execution over breadth of templates.",
        ],
        "source_artifact_ids": [problem_brief["problem_brief_id"], competitor_dossier["competitor_dossier_id"]],
        "created_at": generated_at,
    }
    return {
        "problem_brief": problem_brief,
        "concept_brief": concept_brief,
        "prd": prd,
        "competitor_dossier": competitor_dossier,
        "persona_pack": persona_pack,
        "market_analysis_brief": market_analysis,
    }


def _build_quality_snapshot(workspace_dir: Path, artifact_payloads: dict[str, dict]) -> dict[str, object]:
    schema_map = {
        "problem_brief": "problem_brief.schema.json",
        "concept_brief": "concept_brief.schema.json",
        "prd": "prd.schema.json",
        "competitor_dossier": "competitor_dossier.schema.json",
        "persona_pack": "persona_pack.schema.json",
        "market_analysis_brief": "market_analysis_brief.schema.json",
    }
    checks: dict[str, dict[str, object]] = {}
    validation_pass_count = 0
    for artifact_name, payload in artifact_payloads.items():
        schema_name = schema_map.get(artifact_name)
        errors = _validate_payload_against_schema(payload, schema_name) if schema_name else []
        populated_fields = [
            key
            for key, value in payload.items()
            if value not in (None, "", [], {})
        ]
        total_fields = max(len(payload), 1)
        if not errors:
            validation_pass_count += 1
        checks[artifact_name] = {
            "validation_status": "pass" if not errors else "fail",
            "error_count": len(errors),
            "errors": errors[:5],
            "completeness_score": round(len(populated_fields) / total_fields, 2),
        }
    contradiction_items = []
    prd = artifact_payloads.get("prd", {})
    competitor = artifact_payloads.get("competitor_dossier", {})
    if "repo-native" not in " ".join(competitor.get("where_we_win", [])).lower():
        contradiction_items.append("Competitor dossier does not reinforce the repo-native wedge used in the PRD.")
    return {
        "schema_version": "1.0.0",
        "quality_snapshot_id": f"quality_snapshot_{workspace_dir.name}",
        "workspace_id": workspace_dir.name,
        "validation_pass_count": validation_pass_count,
        "artifact_count": len(schema_map),
        "overall_status": "green" if validation_pass_count == len(schema_map) and not contradiction_items else "yellow",
        "artifact_checks": checks,
        "contradiction_items": contradiction_items,
        "generated_at": _default_timestamp(),
    }


def _queue_path(workspace_dir: Path) -> Path:
    return workspace_dir / "outputs" / "operate" / "regeneration_queue.json"


def _load_or_create_cockpit_bundle(workspace_dir: Path, generated_at: str, adapter: str = "codex") -> dict:
    cockpit_path = workspace_dir / "outputs" / "cockpit" / "cockpit_bundle.json"
    if cockpit_path.exists():
        return _load_json(cockpit_path)
    bundle = build_cockpit_bundle_from_workspace(workspace_dir, generated_at=generated_at, adapter_name=adapter)
    _write_json_payload(cockpit_path, bundle)
    return bundle


def _sync_cockpit_living_updates(workspace_dir: Path, queue: dict, *, generated_at: str) -> Path:
    cockpit_bundle = _load_or_create_cockpit_bundle(workspace_dir, generated_at)
    cockpit_state = cockpit_bundle.setdefault("cockpit_state", {})
    updates = []
    for item in queue.get("queued_items", []):
        updates.append(
            {
                "update_id": f"lu_{item['item_id']}",
                "regeneration_queue_item_ref": item["item_id"],
                "source_change": queue.get("trigger_event", {}).get("change_summary", "Artifact change"),
                "target_artifact": item["target_artifact_ref"],
                "delta_summary": item["delta_preview"],
                "impact_classification": item["impact_classification"],
                "pm_action": item.get("status", "pending"),
                "pm_note": item.get("pm_note", ""),
                "reviewed_at": generated_at if item.get("status") not in {"pending", "active"} else "",
            }
        )
    cockpit_state["living_updates_queue"] = updates
    cockpit_state["updated_at"] = generated_at
    cockpit_path = workspace_dir / "outputs" / "cockpit" / "cockpit_bundle.json"
    _write_json_payload(cockpit_path, cockpit_bundle)
    if {"mission_brief", "active_phase_packet", "product_record", "workspace_tree_state", "portfolio_state"} <= set(cockpit_bundle.keys()):
        html_path = workspace_dir / "outputs" / "cockpit" / "cockpit.html"
        html_path.write_text(render_cockpit_html(cockpit_bundle), encoding="utf-8")
    return cockpit_path


def _product_context_for_cli(
    workspace_dir: Path,
    bundle: dict[str, object],
) -> tuple[dict[str, object] | None, dict[str, object] | None]:
    product_record = load_product_record_from_workspace(workspace_dir)
    if product_record is None:
        candidate = bundle.get("product_record")
        product_record = candidate if isinstance(candidate, dict) else None

    phase_packet = load_phase_packet_from_workspace(workspace_dir)
    if phase_packet is None:
        candidate = bundle.get("phase_packet")
        phase_packet = candidate if isinstance(candidate, dict) else None

    return product_record, phase_packet


def _parse_phase_goals(raw_values: list[str] | None) -> dict[str, str]:
    goals: dict[str, str] = {}
    for raw_value in raw_values or []:
        if ":" not in raw_value:
            raise SystemExit(f"Invalid --stage-goal '{raw_value}'. Use lifecycle_phase:goal_text.")
        phase, goal = raw_value.split(":", 1)
        normalized_phase = phase.strip()
        normalized_goal = goal.strip()
        if normalized_phase not in {"discovery", "validation", "delivery", "launch", "support_learning", "improve"}:
            raise SystemExit(f"Unsupported lifecycle phase '{normalized_phase}' in --stage-goal.")
        if not normalized_goal:
            raise SystemExit(f"Stage goal for '{normalized_phase}' cannot be empty.")
        goals[normalized_phase] = normalized_goal
    return goals


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _normalized_text(value: object | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _start_kind_from_args(args: argparse.Namespace) -> str:
    if args.kind:
        return args.kind
    if args.source is not None:
        return "import"
    return "new"


def _start_mode_for_guided_flow(args: argparse.Namespace) -> str | None:
    mode = _normalized_text(args.mode)
    if mode is None:
        return None
    if mode not in START_MODE_TO_MATURITY_BAND:
        raise SystemExit("Guided start only supports --mode startup or --mode enterprise.")
    return mode


def _start_new_is_fully_specified(args: argparse.Namespace) -> bool:
    required_values = [
        args.dest,
        _normalized_text(args.workspace_id),
        _normalized_text(args.name),
        _normalized_text(args.mode),
        _normalized_text(args.title),
        _normalized_text(args.customer_problem),
        _normalized_text(args.business_goal),
    ]
    return all(value is not None for value in required_values)


def _start_import_is_fully_specified(args: argparse.Namespace) -> bool:
    required_values = [
        args.source,
        args.dest,
        _normalized_text(args.workspace_id),
        _normalized_text(args.name),
        _normalized_text(args.mode),
    ]
    return all(value is not None for value in required_values)


def _interactive_start_required(args: argparse.Namespace) -> bool:
    kind = _start_kind_from_args(args)
    if args.non_interactive:
        return False
    if kind == "import":
        return not _start_import_is_fully_specified(args)
    return not _start_new_is_fully_specified(args)


def _prompt_text(prompt: str, *, default: str | None = None) -> str:
    while True:
        suffix = f" [{default}]" if default else ""
        try:
            raw_value = input(f"{prompt}{suffix}: ")
        except EOFError as exc:
            raise SystemExit("Startup cancelled.") from exc
        normalized = raw_value.strip()
        if normalized:
            return normalized
        if default is not None:
            return default
        print("Please enter a value.")


def _prompt_choice(
    prompt: str,
    options: list[dict[str, str]],
    *,
    default_value: str | None = None,
) -> str:
    default_index = 1
    if default_value is not None:
        for index, option in enumerate(options, start=1):
            if option["value"] == default_value:
                default_index = index
                break
    while True:
        print(prompt)
        for index, option in enumerate(options, start=1):
            print(f"  {index}. {option['label']} - {option['description']}")
        selected = _prompt_text("Choose an option", default=str(default_index))
        if selected.isdigit():
            option_index = int(selected)
            if 1 <= option_index <= len(options):
                return options[option_index - 1]["value"]
        print("Enter one of the numbered options.")


def _prompt_path(
    prompt: str,
    *,
    default: Path | None = None,
    must_exist: bool = False,
    must_not_exist: bool = False,
) -> Path:
    default_value = default.as_posix() if default is not None else None
    while True:
        raw_value = _prompt_text(prompt, default=default_value)
        candidate = Path(raw_value).expanduser()
        if not candidate.is_absolute():
            candidate = (Path.cwd() / candidate).resolve()
        else:
            candidate = candidate.resolve()
        if must_exist and not candidate.exists():
            print("That path does not exist yet. Enter an existing path.")
            continue
        if must_not_exist and candidate.exists():
            print("That destination already exists. Choose a new path.")
            continue
        return candidate


def _default_start_destination(workspace_name: str) -> Path:
    return ROOT / "workspaces" / _slug(workspace_name)


def _guided_first_win_choice(args: argparse.Namespace) -> dict[str, str]:
    prompt = "What should ProductOS help you create first?"
    choice_value = _prompt_choice(prompt, START_FIRST_WIN_CHOICES)
    return START_FIRST_WIN_BY_VALUE[choice_value]


def _run_start_new(
    *,
    dest: Path,
    workspace_id: str,
    name: str,
    mode: str,
    title: str,
    customer_problem: str,
    business_goal: str,
    success_metrics: list[str],
    primary_kpis: list[str],
    primary_outcomes: list[str],
    target_user: str,
    operating_mode: str,
    generated_at: str,
    maturity_band: str,
    constraints: list[str] | None,
    audience: list[str] | None,
    review_gate_owner: str,
    portfolio_id: str | None,
    stage_goals: dict[str, str],
    known_risks: list[str] | None,
    template_name: str,
    guided: bool,
    first_win_label: str | None = None,
) -> int:
    init_workspace_from_template(
        ROOT,
        template_name=template_name,
        dest=dest,
        workspace_id=workspace_id,
        name=name,
        mode=mode,
    )
    mission_brief = init_mission_in_workspace(
        dest,
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
    print(f"Started workspace at {dest}")
    if guided:
        print(f"Mode: {mode}")
        if first_win_label is not None:
            print(f"First Win: {first_win_label}")
        print(f"Mission: {mission_brief['title']}")
        print(f"Next Command: ./productos --workspace-dir {dest} run discover")
        return 0
    print(f"Mission Brief: {mission_brief['mission_brief_id']}")
    print(f"Operating Mode: {mission_brief['operating_mode']}")
    print(f"Maturity Band: {mission_brief['maturity_band']}")
    print(f"Portfolio: {mission_brief['portfolio_id']}")
    print(f"Next Action: {mission_brief['next_action']}")
    return 0


def _run_workspace_adoption(
    *,
    source: Path,
    dest: Path,
    workspace_id: str,
    name: str,
    mode: str,
    generated_at: str,
    review_threshold: str,
    emit_report: bool = False,
    emit_thread_page: bool = False,
    include_runtime_support_assets: bool = False,
    dry_run: bool = False,
    output_dir: Path | None = None,
    guided: bool = False,
) -> int:
    bundle = build_workspace_adoption_bundle_from_source(
        ROOT,
        source_dir=source,
        workspace_id=workspace_id,
        name=name,
        generated_at=generated_at,
        review_threshold=review_threshold,
    )
    failures = _validate_named_bundle(bundle, ADOPTION_ARTIFACT_SCHEMAS)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    if output_dir:
        _write_artifacts(output_dir, bundle, ADOPTION_ARTIFACTS)
        if emit_thread_page:
            write_thread_review_page(bundle["thread_review_bundle"], output_dir / "thread-review.html")

    report = bundle["workspace_adoption_report"]
    review_queue = bundle["adoption_review_queue"]
    print(f"Source Workspace Mode: {report['source_workspace_mode']}")
    print(f"Source Files: {report['source_file_count']}")
    print(f"Generated Artifacts: {len(report['generated_artifact_ids'])}")
    print(f"Review Items: {review_queue['review_items'] and len(review_queue['review_items']) or 0}")

    if dry_run:
        print("Adoption Status: dry-run")
        print("Dry Run: no workspace files were written.")
        return 0

    destination, adopted_bundle = adopt_workspace_from_source(
        ROOT,
        source_dir=source,
        dest=dest,
        workspace_id=workspace_id,
        name=name,
        mode=mode,
        generated_at=generated_at,
        review_threshold=review_threshold,
        emit_report=emit_report,
        emit_thread_page=emit_thread_page,
        include_runtime_support_assets=include_runtime_support_assets,
    )
    print("Adoption Status: completed")
    print(f"Destination: {destination}")
    if guided:
        print(f"Mode: {mode}")
        print(f"Next Command: ./productos --workspace-dir {destination} review")
        return 0
    print(f"Lifecycle Item: {adopted_bundle['item_lifecycle_state']['item_ref']['entity_id']}")
    if emit_thread_page:
        print(f"Thread Review Page: {destination / 'docs' / 'review' / 'thread-review.html'}")
    return 0


def _run_guided_start(args: argparse.Namespace) -> int:
    kind = args.kind
    if kind is None:
        kind = _prompt_choice(
            "How do you want to get started?",
            [
                {
                    "value": "new",
                    "label": "Start a new workspace",
                    "description": "Create a fresh ProductOS workspace for a product or feature.",
                },
                {
                    "value": "import",
                    "label": "Bring existing work into ProductOS",
                    "description": "Adopt an existing folder of notes, docs, or product files.",
                },
            ],
            default_value=_start_kind_from_args(args),
        )
    if kind == "import":
        source = args.source or _prompt_path(
            "Where is the existing product folder?",
            must_exist=True,
        )
        name = _normalized_text(args.name) or _prompt_text("What should this workspace be called?")
        dest = args.dest or _prompt_path(
            "Where should ProductOS create the new workspace?",
            default=_default_start_destination(name),
            must_not_exist=True,
        )
        mode = _start_mode_for_guided_flow(args) or _prompt_choice(
            "Which mode fits this workspace best?",
            [
                {
                    "value": "startup",
                    "label": "Startup",
                    "description": "Simpler, faster default for a new or early-stage team.",
                },
                {
                    "value": "enterprise",
                    "label": "Enterprise",
                    "description": "More structured default for a governance-heavy product environment.",
                },
            ],
            default_value="startup",
        )
        workspace_id = _normalized_text(args.workspace_id) or f"ws_{_slug(name)}"
        return _run_workspace_adoption(
            source=source,
            dest=dest,
            workspace_id=workspace_id,
            name=name,
            mode=mode,
            generated_at=args.generated_at,
            review_threshold=args.review_threshold,
            guided=True,
        )

    name = _normalized_text(args.name) or _prompt_text("What should this workspace be called?")
    dest = args.dest or _prompt_path(
        "Where should ProductOS create the workspace?",
        default=_default_start_destination(name),
        must_not_exist=True,
    )
    mode = _start_mode_for_guided_flow(args) or _prompt_choice(
        "Which mode fits this workspace best?",
        [
            {
                "value": "startup",
                "label": "Startup",
                "description": "Simpler, faster default for a new or early-stage team.",
            },
            {
                "value": "enterprise",
                "label": "Enterprise",
                "description": "More structured default for a governance-heavy product environment.",
            },
        ],
        default_value="startup",
    )
    first_win = _guided_first_win_choice(args)
    workspace_id = _normalized_text(args.workspace_id) or f"ws_{_slug(name)}"
    title = _normalized_text(args.title) or first_win["title"]
    deliverable_name = first_win["label"].lower()
    customer_problem = _normalized_text(args.customer_problem) or (
        f"The PM needs a fast way to turn messy product context into a reviewable {deliverable_name}."
    )
    business_goal = _normalized_text(args.business_goal) or (
        f"Help {name} get to a clear product direction faster with less PM coordination overhead."
    )
    success_metrics = args.success_metric or [first_win["success_metric"]]
    primary_kpis = args.primary_kpi or success_metrics
    primary_outcomes = args.primary_outcome or [first_win["primary_outcome"]]
    maturity_band = START_MODE_TO_MATURITY_BAND[mode]
    return _run_start_new(
        dest=dest,
        workspace_id=workspace_id,
        name=name,
        mode=mode,
        title=title,
        customer_problem=customer_problem,
        business_goal=business_goal,
        success_metrics=success_metrics,
        primary_kpis=primary_kpis,
        primary_outcomes=primary_outcomes,
        target_user=args.target_user or "Product manager",
        operating_mode=args.operating_mode,
        generated_at=args.generated_at,
        maturity_band=maturity_band,
        constraints=args.constraint,
        audience=args.audience,
        review_gate_owner=args.review_gate_owner,
        portfolio_id=args.portfolio_id,
        stage_goals=_parse_phase_goals(args.stage_goal),
        known_risks=args.known_risk,
        template_name=args.template,
        guided=True,
        first_win_label=first_win["label"],
    )


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


def _load_stable_cutover_plan(workspace_dir: Path, generated_at: str) -> dict | None:
    cutover_plan = build_v6_cutover_plan_from_workspace(
        workspace_dir,
        generated_at=generated_at,
    )
    if cutover_plan["selection_status"] != "stable_active":
        return cutover_plan

    try:
        return build_v7_cutover_plan_from_workspace(
            workspace_dir,
            generated_at=generated_at,
        )
    except KeyError:
        # Product workspaces do not necessarily carry the reference lifecycle
        # item used by the ProductOS V7 publication cutover logic.
        return cutover_plan


def _phase_output_dir(workspace_dir: Path, phase: str) -> Path:
    return workspace_dir / "outputs" / phase


def _mission_phase_entry_classifier(workspace_dir: Path, requested_phase: str) -> dict[str, object] | None:
    if requested_phase == "all":
        return None

    mission_brief = load_mission_brief_from_workspace(workspace_dir)
    if mission_brief is None:
        return None

    router = mission_brief.get("mission_router") or {}
    entry_phase = str(router.get("entry_phase", "discover"))
    raw_phase_sequence = list(router.get("phase_sequence") or MISSION_PHASE_ORDER)
    phase_sequence = [phase for phase in MISSION_PHASE_ORDER if phase in raw_phase_sequence]
    if not phase_sequence:
        phase_sequence = [entry_phase] if entry_phase in MISSION_PHASE_ORDER else ["discover"]
    if entry_phase in phase_sequence:
        phase_sequence = phase_sequence[phase_sequence.index(entry_phase):]
    elif entry_phase in MISSION_PHASE_ORDER:
        phase_sequence.insert(0, entry_phase)

    return {
        "mission_title": mission_brief["title"],
        "operating_mode": mission_brief.get("operating_mode", "full_loop"),
        "entry_phase": entry_phase,
        "allowed_phases": phase_sequence,
        "requested_phase": requested_phase,
        "allowed": requested_phase in phase_sequence,
    }


def _validate_mission_phase_entry(workspace_dir: Path, requested_phase: str) -> bool:
    phase_entry = _mission_phase_entry_classifier(workspace_dir, requested_phase)
    if phase_entry is None or phase_entry["allowed"]:
        return True

    allowed_phases = ", ".join(phase_entry["allowed_phases"])
    print(
        "FAIL: "
        f"Mission '{phase_entry['mission_title']}' routes through [{allowed_phases}] in "
        f"'{phase_entry['operating_mode']}' mode, so '{requested_phase}' is not an allowed entry phase. "
        f"Start at '{phase_entry['entry_phase']}' and expand only after the routed prior phases are accepted.",
        file=sys.stderr,
    )
    return False


def _print_mission_summary(workspace_dir: Path) -> None:
    mission_brief = load_mission_brief_from_workspace(workspace_dir)
    if mission_brief is None:
        return
    print(f"Mission: {mission_brief['title']}")
    print(f"Mission Mode: {mission_brief['operating_mode']}")
    if "mission_router" in mission_brief:
        print(f"Mission Entry Phase: {mission_brief['mission_router']['entry_phase']}")
    if "steering_context" in mission_brief:
        print(f"Steering Refs: {len(mission_brief['steering_context']['steering_refs'])}")


def _print_mission_control(cockpit: dict[str, object]) -> None:
    mission_control = cockpit.get("mission_control")
    if not isinstance(mission_control, dict):
        return
    print(f"Mission Stage: {mission_control['active_stage']}")
    print(f"Mission Task: {mission_control['current_task_name']}")
    print(f"Mission Task Status: {mission_control['current_task_status']}")
    print(f"Reviewer Lane: {mission_control['reviewer_lane']}")


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


def _print_research_summary(bundle: dict[str, dict]) -> None:
    research_plan = bundle.get("external_research_plan") or bundle.get("discover_external_research_plan")
    source_discovery = bundle.get("external_research_source_discovery") or bundle.get("discover_external_research_source_discovery")
    selected_manifest = bundle.get("external_research_selected_manifest") or bundle.get("discover_selected_research_manifest")
    if research_plan is not None:
        required_signal_lane_count = 3
        planned_signal_lanes = research_plan.get("coverage_summary", {}).get("planned_signal_lanes")
        if not planned_signal_lanes:
            planned_signal_lanes = list(
                dict.fromkeys(
                    _signal_lane_id_for_source_type(item["recommended_source_type"])
                    for item in research_plan.get("prioritized_questions", [])
                    if isinstance(item, dict) and isinstance(item.get("recommended_source_type"), str)
                )
            )
        discovered_signal_lane_count = 0
        selected_signal_lane_count = 0
        if source_discovery is not None:
            signal_lane_coverage = source_discovery.get("signal_lane_coverage") or []
            if signal_lane_coverage:
                discovered_signal_lane_count = sum(
                    1 for item in signal_lane_coverage if item.get("candidate_source_count", 0) > 0
                )
            else:
                discovered_signal_lane_count = len(
                    {
                        _signal_lane_id_for_source_type(item["source_type"])
                        for item in source_discovery.get("candidate_sources", [])
                        if isinstance(item, dict) and isinstance(item.get("source_type"), str)
                    }
                )
        if selected_manifest is not None:
            selected_signal_lane_count = len(
                {
                    _signal_lane_id_for_source_type(item["source_type"])
                    for item in selected_manifest.get("sources", [])
                    if isinstance(item, dict) and isinstance(item.get("source_type"), str)
                }
            )
        if selected_manifest is not None:
            print(f"Research Coverage: selected {selected_signal_lane_count}/{required_signal_lane_count} signal lanes")
        elif source_discovery is not None:
            print(f"Research Coverage: discovered {discovered_signal_lane_count}/{required_signal_lane_count} signal lanes")
        else:
            print(f"Research Coverage: planned {len(planned_signal_lanes)}/{required_signal_lane_count} signal lanes")
    if research_plan is not None:
        print(f"Research Questions: {len(research_plan.get('prioritized_questions', []))}")
    if source_discovery is not None:
        print(f"Research Candidates: {len(source_discovery.get('candidate_sources', []))}")
    if selected_manifest is not None:
        print(f"Selected Research Sources: {len(selected_manifest.get('sources', []))}")


def _print_research_posture(bundle: dict[str, dict]) -> None:
    summary = summarize_research_posture(bundle)
    print(f"Research Review: {summary['review_status']}")
    print(f"Research Search: {summary['search_status']}")
    print(f"Research Contradictions: {summary['contradiction_count']}")
    print(f"Research Freshness: {summary['freshness_summary']}")
    print(f"Research Recommendation: {summary['recommendation']}")


def _print_strategy_refresh_posture(bundle: dict[str, dict]) -> None:
    summary = summarize_strategy_refresh_posture(bundle)
    evidence_types = ", ".join(summary["available_evidence_types"]) if summary["available_evidence_types"] else "none"
    missing_downstream = ", ".join(summary["missing_downstream_types"]) if summary["missing_downstream_types"] else "none"
    print(f"Strategy Refresh: {summary['status']}")
    print(f"Strategy Evidence: {summary['available_evidence_count']} ({evidence_types})")
    print(f"Downstream Packet: {summary['downstream_packet_status']}")
    print(f"Missing Downstream Artifacts: {missing_downstream}")
    print(f"Strategy Recommendation: {summary['recommendation']}")


def _signal_lane_id_for_source_type(source_type: str) -> str:
    if source_type in {"market_validation", "security_review"}:
        return "market"
    if source_type == "competitor_research":
        return "competitor"
    if source_type in {"customer_evidence", "operator_interview"}:
        return "customer"
    return source_type


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


def _print_v9_program_summary(program_state: dict[str, object]) -> None:
    track_states = program_state["track_states"]
    track_summary = ", ".join(
        f"{track_id}={track_state['status']}"
        for track_id, track_state in track_states.items()
    )
    research_packet = program_state["research_packet"]
    governed_docs = program_state["governed_docs"]
    downstream = program_state["downstream"]
    stale_inputs = program_state["stale_release_inputs"]
    print(f"Lifecycle Tracks: {track_summary}")
    print(f"Workspace Coherence: {program_state['workspace_coherence_mode']}")
    if program_state.get("fallback_reasons"):
        print(f"Fallback Reasons: {', '.join(program_state['fallback_reasons'])}")
    print(
        "Governed Docs: "
        f"{governed_docs['mode']} ({governed_docs['sync_mode']}, validation={governed_docs['validation_status']})"
    )
    print(
        "Research Packet: "
        f"{research_packet['present_count']}/{research_packet['required_count']} "
        f"({research_packet['mode']}, freshness={research_packet['freshness']}, "
        f"contradictions={research_packet['contradiction_count']})"
    )
    print(f"Research Downstream Readiness: {'ready' if research_packet['downstream_ready'] else 'pending'}")
    print(
        "Downstream Traceability: "
        f"{downstream['mode']} (reopen={'ready' if downstream['reopen_ready'] else 'pending'})"
    )
    print(f"V9 Stale Inputs: {stale_inputs['count']} ({stale_inputs['status']})")
    print(f"V9 Release Gate: {program_state['gate_status']}")


def cmd_status(args: argparse.Namespace) -> int:
    workspace_dir = _workspace_dir(args)
    bundle = _try_build_bundle(args)
    program_state = _build_v9_program_state(
        workspace_dir,
        generated_at=args.generated_at,
        adapter_name=args.adapter,
        bundle=bundle,
    )
    product_record, phase_packet = _product_context_for_cli(workspace_dir, bundle or {})
    if bundle is not None:
        cockpit = bundle["cockpit_state"]
        review = bundle["feature_portfolio_review"]
        eval_report = bundle["eval_run_report"]
        swarm_plan = bundle["autonomous_pm_swarm_plan"]
        swarm_scorecard = bundle["autonomous_pm_swarm_feature_scorecard"]
        focus = cockpit["current_focus"]
        cutover_plan = _load_stable_cutover_plan(workspace_dir, args.generated_at)
        top_priority_feature = review["top_priority_feature_id"]
        if cutover_plan and cutover_plan["selection_status"] == "stable_active" and cutover_plan["stable_release_version"] == "7.0.0":
            focus = "Keep ProductOS V7.0.0 stable for lifecycle traceability through outcome_review and prepare the next external publication slice."
            top_priority_feature = cutover_plan["top_priority_feature_id"]
        elif cutover_plan and cutover_plan["selection_status"] == "stable_active" and cutover_plan["stable_release_version"] == "6.0.0":
            focus = "Keep ProductOS V6.0.0 stable for lifecycle traceability through release_readiness and prepare the next bounded lifecycle expansion."
            top_priority_feature = cutover_plan["top_priority_feature_id"]
        print(f"Mode: {cockpit['mode']}")
        print(f"Status: {cockpit['status']}")
        print(f"Focus: {focus}")
    else:
        print("Mode: review")
        print("Status: watch")
        print("Focus: Keep the lifecycle-enrichment program coherent even when the full next-version runtime is unavailable for this workspace.")
    _print_mission_summary(workspace_dir)
    if bundle is not None:
        _print_mission_control(bundle["cockpit_state"])
    if product_record is not None:
        print(f"Maturity Band: {product_record['maturity_band']}")
        print(f"Lifecycle Phase: {product_record['lifecycle_stage']}")
    if phase_packet is not None:
        print(f"Active Phase Packet: {phase_packet['phase_packet_id']}")
    problem_register = load_problem_register(workspace_dir, generated_at=args.generated_at, persist=False)
    competitor_registry = load_competitor_registry(workspace_dir, generated_at=args.generated_at, persist=False)
    if problem_register is not None:
        active_problem_count = sum(1 for item in problem_register["problems"] if item.get("status") == "active")
        print(
            f"Problem Register: {active_problem_count} active / {len(problem_register['problems'])} total "
            f"({_memory_freshness_label(problem_register)})"
        )
    if competitor_registry is not None:
        tracked_competitor_count = sum(1 for item in competitor_registry["competitors"] if item.get("status") == "tracked")
        print(
            f"Competitor Registry: {tracked_competitor_count} tracked / {len(competitor_registry['competitors'])} total "
            f"({_memory_freshness_label(competitor_registry)})"
        )
    memory_review = collect_memory_review_items(workspace_dir)
    print(
        f"Pending Memory Review: {memory_review['pending_items']} "
        f"(problems: {memory_review['problem_candidates']}, competitors: {memory_review['competitor_candidates']})"
    )
    _print_v9_program_summary(program_state)
    if bundle is not None:
        gate = _promotion_gate(bundle)
        print(f"Top Priority Feature: {top_priority_feature}")
        print(f"Truthfulness Status: {review['truthfulness_status']}")
        print(f"Eval Status: {eval_report['status']} ({eval_report['regression_count']} regressions)")
        print(f"Governed Research: {_governed_research_status(bundle)}")
        print(f"Feed Governance: {_feed_governance_status(bundle)}")
        _print_research_summary(bundle)
        _print_research_posture(bundle)
        _print_strategy_refresh_posture(bundle)
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
    workspace_dir = _workspace_dir(args)
    bundle = _build_bundle(args)
    intake = bundle["intake_routing_state"]
    print(f"Ingestion Mode: {intake['ingestion_mode']}")
    print(f"Intake Items: {len(intake['intake_items'])}")
    for item in intake["intake_items"]:
        print(f"- {item['item_id']}: {item['input_type']} -> {', '.join(item['recommended_workflow_ids'])}")
    persisted_paths = _persist_note_memory_proposals(
        workspace_dir,
        args.generated_at,
        output_dir=args.output_dir,
    )
    persisted_proposals = [_load_json(path) for path in persisted_paths]
    memory_candidates = [
        candidate
        for proposal in persisted_proposals
        for candidate in proposal.get("memory_candidates", [])
    ]
    print(
        f"Memory Candidates: {len(memory_candidates)} "
        f"(problems: {sum(1 for item in memory_candidates if item.get('candidate_type') == 'problem')}, "
        f"competitors: {sum(1 for item in memory_candidates if item.get('candidate_type') == 'competitor')})"
    )
    for candidate in memory_candidates[:5]:
        print(f"- {candidate['candidate_type']}: {candidate['action']} -> {candidate['label']}")
    if args.output_dir:
        _write_artifacts(args.output_dir, bundle, ["intake_routing_state"])
    elif persisted_paths:
        print(f"Memory Proposal Files: {len(persisted_paths)}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    workspace_dir = _workspace_dir(args)
    if not _validate_mission_phase_entry(workspace_dir, args.phase):
        return 1
    bundle = _build_bundle(args)
    names = PHASE_ARTIFACTS[args.phase]
    if args.output_dir:
        _write_artifacts(args.output_dir, bundle, names)
        if args.phase in {"discover", "all"}:
            _write_source_note_cards(args.output_dir, bundle)
        if args.phase in {"improve", "all"}:
            _write_release_review_markdown(args.output_dir, bundle)
    if args.persist:
        output_dir = _phase_output_dir(workspace_dir, args.phase)
        _write_artifacts(output_dir, bundle, names)
        if args.phase in {"discover", "all"}:
            _write_source_note_cards(output_dir, bundle)
        if args.phase in {"discover", "all"}:
            mission_brief = load_mission_brief_from_workspace(workspace_dir)
            if mission_brief is not None:
                sync_canonical_discover_artifacts(
                    workspace_dir,
                    mission_brief=mission_brief,
                    generated_at=args.generated_at,
                    strategy_context_brief=bundle.get("discover_strategy_context_brief"),
                    product_vision_brief=bundle.get("discover_product_vision_brief"),
                    strategy_option_set=bundle.get("discover_strategy_option_set"),
                    market_strategy_brief=bundle.get("discover_market_strategy_brief"),
                    problem_brief=bundle.get("discover_problem_brief"),
                    concept_brief=bundle.get("discover_concept_brief"),
                    prd=bundle.get("discover_prd"),
                )
            sync_canonical_discovery_operations_artifacts(
                workspace_dir,
                bundle={
                    "research_handoff": bundle.get("discover_research_handoff"),
                    "research_notebook": bundle.get("discover_research_notebook"),
                    "research_brief": bundle.get("discover_research_brief"),
                    "external_research_plan": bundle.get("discover_external_research_plan"),
                    "external_research_source_discovery": bundle.get("discover_external_research_source_discovery"),
                    "external_research_review": bundle.get("discover_external_research_review"),
                    "framework_registry": bundle.get("discover_framework_registry"),
                    "competitor_dossier": bundle.get("discover_competitor_dossier"),
                    "customer_pulse": bundle.get("discover_customer_pulse"),
                    "market_analysis_brief": bundle.get("discover_market_analysis_brief"),
                    "landscape_matrix": bundle.get("discover_landscape_matrix"),
                    "market_sizing_brief": bundle.get("discover_market_sizing_brief"),
                    "market_share_brief": bundle.get("discover_market_share_brief"),
                    "opportunity_portfolio_view": bundle.get("discover_opportunity_portfolio_view"),
                    "prioritization_decision_record": bundle.get("discover_prioritization_decision_record"),
                    "feature_prioritization_brief": bundle.get("discover_feature_prioritization_brief"),
                    "source_note_cards": bundle.get("discover_source_note_cards"),
                    "selected_research_manifest": bundle.get("discover_selected_research_manifest"),
                },
            )
            sync_memory_registers(
                workspace_dir,
                generated_at=args.generated_at,
                problem_brief=bundle.get("discover_problem_brief"),
                competitor_dossier=bundle.get("discover_competitor_dossier"),
                feed_registry=bundle.get("external_research_feed_registry"),
            )
            # Slice 2: auto-synthesize customer journey map if persona/problem data exists
            cjm_path = workspace_dir / "artifacts" / "customer_journey_map.json"
            if not cjm_path.exists():
                try:
                    synthesized = synthesize_customer_journey_map(workspace_dir, generated_at=args.generated_at)
                    cjm_path.parent.mkdir(parents=True, exist_ok=True)
                    with cjm_path.open("w", encoding="utf-8") as f:
                        json.dump(synthesized, f, indent=2)
                        f.write("\n")
                    print(f"Synthesized: artifacts/customer_journey_map.json")
                except Exception as exc:
                    print(f"Synthesis skipped: {exc}")
            try:
                journey_args = argparse.Namespace(workspace_dir=workspace_dir, generated_at=args.generated_at)
                cmd_render_journey_map(journey_args)
                cmd_render_screen_flow(journey_args)
                bundle_paths = write_prototype_bundle(workspace_dir, generated_at=args.generated_at)
                print(f"Prototype generated: {bundle_paths['prototype_html']}")
            except Exception as exc:
                print(f"Prototype pipeline skipped: {exc}")
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
    workspace_dir = _workspace_dir(args)
    bundle = _try_build_bundle(args)
    program_state = _build_v9_program_state(
        workspace_dir,
        generated_at=args.generated_at,
        adapter_name=args.adapter,
        bundle=bundle,
    )
    product_record, phase_packet = _product_context_for_cli(workspace_dir, bundle or {})
    _print_mission_summary(workspace_dir)
    if bundle is not None:
        _print_mission_control(bundle["cockpit_state"])
    if product_record is not None:
        print(f"Maturity Band: {product_record['maturity_band']}")
        print(f"Lifecycle Phase: {product_record['lifecycle_stage']}")
    if phase_packet is not None:
        print(f"Active Phase Packet: {phase_packet['phase_packet_id']}")
    _print_v9_program_summary(program_state)
    if bundle is not None:
        cockpit = bundle["cockpit_state"]
        portfolio = bundle["feature_portfolio_review"]
        eval_report = bundle["eval_run_report"]
        swarm_plan = bundle["autonomous_pm_swarm_plan"]
        swarm_scorecard = bundle["autonomous_pm_swarm_feature_scorecard"]
        gate = _promotion_gate(bundle)
        print(f"Governed Research: {_governed_research_status(bundle)}")
        print(f"Feed Governance: {_feed_governance_status(bundle)}")
        _print_research_summary(bundle)
        _print_research_posture(bundle)
        _print_strategy_refresh_posture(bundle)
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
    if getattr(args, "export_command", None) == "artifact":
        workspace_dir = _workspace_dir(args)
        result = export_artifact(
            args.artifact,
            args.format,
            workspace_dir,
            generated_at=args.generated_at,
        )
        output_path = args.output_path or (workspace_dir / "outputs" / "export" / f"{Path(args.artifact).stem}.{args.format}.json")
        _write_json_payload(output_path, result)
        print(f"Export Artifact: {args.artifact}")
        print(f"Format: {args.format}")
        print(f"Output: {output_path}")
        return 0

    if args.output_dir is None:
        raise SystemExit("`productos export` requires --output-dir unless using `export artifact`.")
    bundle = _build_bundle(args)
    _write_artifacts(args.output_dir, bundle, list(bundle.keys()))
    _write_release_review_markdown(args.output_dir, bundle)
    print(f"Exported {len(bundle)} artifacts to {args.output_dir}")
    return 0


def _default_visual_plan_path(visual_surface: str, source_artifact_id: str) -> Path:
    return (ROOT / "tmp" / "visual-plans" / visual_surface / f"{source_artifact_id}.visual-direction-plan.json").resolve()


def _default_visual_output_dir(visual_surface: str, source_artifact_id: str) -> Path:
    if visual_surface == "deck":
        return (ROOT / "tmp" / "presentations" / source_artifact_id).resolve()
    if visual_surface == "corridor":
        return (ROOT / "tmp" / "workflow-corridor" / str(source_artifact_id).replace(" ", "-").lower()).resolve()
    if visual_surface == "map":
        return (ROOT / "tmp" / "visual-maps" / source_artifact_id).resolve()
    raise ValueError(f"Unsupported visual surface: {visual_surface}")


def _build_deck_outputs(
    presentation_brief: dict,
    direction_plan: dict,
    output_dir: Path,
    *,
    aspect_ratio: str,
) -> tuple[dict[str, dict], dict[str, Path]]:
    brief_id = presentation_brief["presentation_brief_id"]
    evidence_pack = build_evidence_pack(presentation_brief)
    presentation_story = build_presentation_story(presentation_brief, evidence_pack)
    render_spec = build_render_spec(
        presentation_brief,
        presentation_story,
        aspect_ratio=aspect_ratio,
    )
    slide_spec = build_slide_spec(
        presentation_brief,
        aspect_ratio=aspect_ratio,
    )
    publish_check = build_publish_check(presentation_brief, render_spec)
    export_plan = build_ppt_export_plan(render_spec)
    quality_review = build_visual_quality_review_for_deck(direction_plan, render_spec, publish_check)

    output_paths = {
        "visual_direction_plan": output_dir / f"{brief_id}.visual-direction-plan.json",
        "visual_quality_review": output_dir / f"{brief_id}.visual-quality-review.json",
        "evidence_pack": output_dir / f"{brief_id}.evidence-pack.json",
        "presentation_story": output_dir / f"{brief_id}.presentation-story.json",
        "render_spec": output_dir / f"{brief_id}.render-spec.json",
        "slide_spec": output_dir / f"{brief_id}.slide-spec.json",
        "publish_check": output_dir / f"{brief_id}.publish-check.json",
        "ppt_export_plan": output_dir / f"{brief_id}.ppt-export-plan.json",
        "html": output_dir / f"{brief_id}.html",
    }

    _write_json_payload(output_paths["visual_direction_plan"], direction_plan)
    _write_json_payload(output_paths["visual_quality_review"], quality_review)
    _write_json_payload(output_paths["evidence_pack"], evidence_pack)
    _write_json_payload(output_paths["presentation_story"], presentation_story)
    _write_json_payload(output_paths["render_spec"], render_spec)
    _write_json_payload(output_paths["slide_spec"], slide_spec)
    _write_json_payload(output_paths["publish_check"], publish_check)
    _write_json_payload(output_paths["ppt_export_plan"], export_plan)
    write_html_presentation(render_spec, output_paths["html"])

    return {
        "evidence_pack": evidence_pack,
        "presentation_story": presentation_story,
        "render_spec": render_spec,
        "slide_spec": slide_spec,
        "publish_check": publish_check,
        "ppt_export_plan": export_plan,
        "visual_quality_review": quality_review,
    }, output_paths


def _build_corridor_outputs(
    source_bundle: dict,
    direction_plan: dict,
    output_dir: Path,
    *,
    audience_mode: str,
    publication_mode: str,
) -> tuple[dict[str, dict], dict[str, Path]]:
    bundle = build_workflow_corridor_bundle(
        source_bundle,
        audience_mode=audience_mode,
        publication_mode=publication_mode,
    )
    quality_review = build_visual_quality_review_for_corridor(direction_plan, bundle)
    output_paths = {
        "visual_direction_plan": output_dir / "visual_direction_plan.json",
        "visual_quality_review": output_dir / "visual_quality_review.json",
        **{name: output_dir / f"{name}.json" for name in bundle},
        "html": output_dir / "workflow_corridor.html",
    }

    _write_json_payload(output_paths["visual_direction_plan"], direction_plan)
    _write_json_payload(output_paths["visual_quality_review"], quality_review)
    for name, payload in bundle.items():
        write_corridor_payload(payload, output_paths[name])
    write_corridor_html(bundle["corridor_render_model"], output_paths["html"])

    bundle["visual_quality_review"] = quality_review
    return bundle, output_paths


def _build_map_outputs(
    visual_map_spec: dict,
    direction_plan: dict,
    output_dir: Path,
    *,
    aspect_ratio: str,
    theme_name: str,
) -> tuple[dict[str, dict], dict[str, Path]]:
    visual_map_id = visual_map_spec["visual_map_spec_id"]
    render_spec = build_visual_map_render_spec(
        visual_map_spec,
        theme_name=theme_name,
        aspect_ratio=aspect_ratio,
    )
    slide_spec = build_visual_map_slide_spec(
        visual_map_spec,
        theme_name=theme_name,
        aspect_ratio=aspect_ratio,
    )
    quality_review = build_visual_quality_review_for_map(direction_plan, render_spec)
    output_paths = {
        "visual_direction_plan": output_dir / f"{visual_map_id}.visual-direction-plan.json",
        "visual_quality_review": output_dir / f"{visual_map_id}.visual-quality-review.json",
        "render_spec": output_dir / f"{visual_map_id}.render-spec.json",
        "slide_spec": output_dir / f"{visual_map_id}.slide-spec.json",
        "html": output_dir / f"{visual_map_id}.html",
    }

    _write_json_payload(output_paths["visual_direction_plan"], direction_plan)
    _write_json_payload(output_paths["visual_quality_review"], quality_review)
    _write_json_payload(output_paths["render_spec"], render_spec)
    _write_json_payload(output_paths["slide_spec"], slide_spec)
    write_html_presentation(render_spec, output_paths["html"])

    return {
        "render_spec": render_spec,
        "slide_spec": slide_spec,
        "visual_quality_review": quality_review,
    }, output_paths


def _maybe_write_native_ppt(render_spec: dict, ppt_path: Path) -> str | None:
    try:
        write_ppt_presentation(render_spec, ppt_path)
    except RuntimeError as error:
        return f"skipped ({error})"
    return None


def _maybe_write_node_ppt(render_spec_path: Path, node_output: Path, node_binary: str) -> tuple[int, str]:
    command = [
        node_binary,
        str(ROOT / "scripts" / "presentation_export_pptx.mjs"),
        str(render_spec_path),
        str(node_output),
    ]
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return 1, f"missing node binary: {node_binary}"
    if result.returncode != 0:
        return result.returncode or 1, result.stderr.strip() or result.stdout.strip() or "node PPT export failed"
    return 0, ""


def _load_visual_direction_plan(path: Path) -> dict:
    return _load_json(path.resolve())


def _find_single_path(output_dir: Path, pattern: str) -> Path:
    matches = sorted(output_dir.glob(pattern))
    if not matches:
        raise SystemExit(f"Expected to find {pattern} in {output_dir}")
    return matches[0]


def cmd_visual_plan_deck(args: argparse.Namespace) -> int:
    brief_path = args.presentation_brief.resolve()
    presentation_brief = _load_json(brief_path)
    direction_plan = build_visual_direction_plan(
        "deck",
        presentation_brief,
        input_ref=str(brief_path),
        aspect_ratio=args.aspect_ratio,
    )
    output_path = (args.output_path or _default_visual_plan_path("deck", presentation_brief["presentation_brief_id"])).resolve()
    _write_json_payload(output_path, direction_plan)
    print(f"Visual direction plan: {output_path}")
    return 0


def cmd_visual_plan_corridor(args: argparse.Namespace) -> int:
    source_path = args.source_bundle.resolve()
    source_bundle = _load_json(source_path)
    source_artifact_id = (
        source_bundle.get("workflow_corridor_spec_id")
        or source_bundle.get("corridor_id")
        or source_bundle.get("title")
        or source_bundle["workspace_id"]
    )
    direction_plan = build_visual_direction_plan(
        "corridor",
        source_bundle,
        input_ref=str(source_path),
        audience_mode=args.audience_mode,
        publication_mode=args.publication_mode,
    )
    output_path = (args.output_path or _default_visual_plan_path("corridor", source_artifact_id)).resolve()
    _write_json_payload(output_path, direction_plan)
    print(f"Visual direction plan: {output_path}")
    return 0


def cmd_visual_plan_map(args: argparse.Namespace) -> int:
    spec_path = args.visual_map_spec.resolve()
    visual_map_spec = _load_json(spec_path)
    direction_plan = build_visual_direction_plan(
        "map",
        visual_map_spec,
        input_ref=str(spec_path),
        aspect_ratio=args.aspect_ratio,
        theme_name=args.theme_preset,
    )
    output_path = (args.output_path or _default_visual_plan_path("map", visual_map_spec["visual_map_spec_id"])).resolve()
    _write_json_payload(output_path, direction_plan)
    print(f"Visual direction plan: {output_path}")
    return 0


def cmd_visual_build(args: argparse.Namespace) -> int:
    direction_plan = _load_visual_direction_plan(args.visual_direction_plan)
    input_payload = _load_json(Path(direction_plan["input_ref"]))
    output_dir = (args.output_dir or _default_visual_output_dir(direction_plan["visual_surface"], direction_plan["source_artifact_id"])).resolve()

    if direction_plan["visual_surface"] == "deck":
        _, output_paths = _build_deck_outputs(
            input_payload,
            direction_plan,
            output_dir,
            aspect_ratio=direction_plan["aspect_ratio"],
        )
        print(f"Built deck outputs for {direction_plan['source_artifact_id']}:")
        for label, path in output_paths.items():
            print(f"  - {label}: {path}")
        if not args.skip_ppt and "pptx" in direction_plan["output_targets"]:
            ppt_path = output_dir / f"{direction_plan['source_artifact_id']}.pptx"
            detail = _maybe_write_native_ppt(_load_json(output_paths["render_spec"]), ppt_path)
            if detail is None:
                print(f"  - pptx: {ppt_path}")
            else:
                print(f"  - pptx: {detail}")
        return 0

    if direction_plan["visual_surface"] == "corridor":
        plan_notes = direction_plan.get("notes", [])
        publication_mode = plan_notes[1] if len(plan_notes) > 1 else "publishable_external"
        _, output_paths = _build_corridor_outputs(
            input_payload,
            direction_plan,
            output_dir,
            audience_mode=direction_plan["audience"],
            publication_mode=publication_mode,
        )
        print(f"Built corridor outputs for {direction_plan['source_artifact_id']}:")
        print(f"  - output_dir: {output_dir}")
        for label, path in output_paths.items():
            if label == "html":
                continue
            print(f"  - {label}: {path}")
        print(f"  - html: {output_paths['html']}")
        return 0

    if direction_plan["visual_surface"] == "map":
        payloads, output_paths = _build_map_outputs(
            input_payload,
            direction_plan,
            output_dir,
            aspect_ratio=direction_plan["aspect_ratio"],
            theme_name=direction_plan["theme_preset"],
        )
        print(f"Built map outputs for {direction_plan['source_artifact_id']}:")
        for label, path in output_paths.items():
            print(f"  - {label}: {path}")
        if not args.skip_ppt and "pptx" in direction_plan["output_targets"]:
            ppt_path = output_dir / f"{direction_plan['source_artifact_id']}.pptx"
            detail = _maybe_write_native_ppt(payloads["render_spec"], ppt_path)
            if detail is None:
                print(f"  - pptx: {ppt_path}")
            else:
                print(f"  - pptx: {detail}")
        return 0

    raise AssertionError(f"Unsupported visual surface: {direction_plan['visual_surface']}")


def cmd_visual_review(args: argparse.Namespace) -> int:
    output_dir = infer_visual_review_target(args.target.resolve())

    corridor_plan_path = output_dir / "visual_direction_plan.json"
    corridor_publish_check_path = output_dir / "corridor_publish_check.json"
    if corridor_plan_path.exists() and corridor_publish_check_path.exists():
        direction_plan = _load_json(corridor_plan_path)
        corridor_bundle = {
            "corridor_render_model": _load_json(output_dir / "corridor_render_model.json"),
            "corridor_publish_check": _load_json(corridor_publish_check_path),
        }
        quality_review = build_visual_quality_review_for_corridor(direction_plan, corridor_bundle)
        output_path = (args.output_path or output_dir / "visual_quality_review.json").resolve()
        _write_json_payload(output_path, quality_review)
        print(f"Visual quality review: {output_path}")
        return 0

    direction_plan_path = _find_single_path(output_dir, "*.visual-direction-plan.json")
    direction_plan = _load_json(direction_plan_path)
    if direction_plan["visual_surface"] == "deck":
        render_spec = _load_json(_find_single_path(output_dir, "*.render-spec.json"))
        publish_check = _load_json(_find_single_path(output_dir, "*.publish-check.json"))
        quality_review = build_visual_quality_review_for_deck(direction_plan, render_spec, publish_check)
    elif direction_plan["visual_surface"] == "map":
        render_spec = _load_json(_find_single_path(output_dir, "*.render-spec.json"))
        quality_review = build_visual_quality_review_for_map(direction_plan, render_spec)
    else:
        raise SystemExit(f"Unsupported review surface in {direction_plan_path}")

    output_path = (
        args.output_path
        or output_dir / f"{direction_plan['source_artifact_id']}.visual-quality-review.json"
    ).resolve()
    _write_json_payload(output_path, quality_review)
    print(f"Visual quality review: {output_path}")
    return 0


def cmd_visual_export_deck(args: argparse.Namespace) -> int:
    brief_path = args.presentation_brief.resolve()
    presentation_brief = _load_json(brief_path)
    brief_id = presentation_brief["presentation_brief_id"]
    direction_plan = build_visual_direction_plan(
        "deck",
        presentation_brief,
        input_ref=str(brief_path),
        aspect_ratio=args.aspect_ratio,
    )
    output_dir = (args.output_dir or _default_visual_output_dir("deck", brief_id)).resolve()
    _, output_paths = _build_deck_outputs(
        presentation_brief,
        direction_plan,
        output_dir,
        aspect_ratio=args.aspect_ratio,
    )

    print(f"Generated deck outputs for {brief_id}:")
    for label, path in output_paths.items():
        print(f"  - {label}: {path}")

    if not args.skip_ppt:
        ppt_path = output_dir / f"{brief_id}.pptx"
        detail = _maybe_write_native_ppt(_load_json(output_paths["render_spec"]), ppt_path)
        if detail is None:
            print(f"  - pptx: {ppt_path}")
        else:
            print(f"  - pptx: {detail}")

    if args.node_ppt_output:
        node_output = args.node_ppt_output.resolve()
        status, detail = _maybe_write_node_ppt(output_paths["render_spec"], node_output, args.node_binary)
        if status != 0:
            print(f"  - node_pptx: failed ({detail})")
            return status
        print(f"  - node_pptx: {node_output}")

    return 0


def cmd_visual_export_corridor(args: argparse.Namespace) -> int:
    source_path = args.source_bundle.resolve()
    source_bundle = _load_json(source_path)
    slug = source_bundle.get("corridor_id") or source_bundle.get("title", "workflow-corridor")
    direction_plan = build_visual_direction_plan(
        "corridor",
        source_bundle,
        input_ref=str(source_path),
        audience_mode=args.audience_mode,
        publication_mode=args.publication_mode,
    )
    output_dir = (args.output_dir or _default_visual_output_dir("corridor", slug)).resolve()
    bundle, output_paths = _build_corridor_outputs(
        source_bundle,
        direction_plan,
        output_dir,
        audience_mode=args.audience_mode,
        publication_mode=args.publication_mode,
    )

    print(f"Generated corridor outputs for {slug}:")
    print(f"  - output_dir: {output_dir}")
    for name in bundle:
        if name == "visual_quality_review":
            continue
        print(f"  - {name}: {output_dir / f'{name}.json'}")
    print(f"  - visual_direction_plan: {output_paths['visual_direction_plan']}")
    print(f"  - visual_quality_review: {output_paths['visual_quality_review']}")
    print(f"  - html: {output_paths['html']}")
    return 0


def cmd_visual_export_map(args: argparse.Namespace) -> int:
    spec_path = args.visual_map_spec.resolve()
    visual_map_spec = _load_json(spec_path)
    visual_map_id = visual_map_spec["visual_map_spec_id"]
    direction_plan = build_visual_direction_plan(
        "map",
        visual_map_spec,
        input_ref=str(spec_path),
        aspect_ratio=args.aspect_ratio,
        theme_name=args.theme_preset,
    )
    output_dir = (args.output_dir or _default_visual_output_dir("map", visual_map_id)).resolve()
    payloads, output_paths = _build_map_outputs(
        visual_map_spec,
        direction_plan,
        output_dir,
        aspect_ratio=args.aspect_ratio,
        theme_name=args.theme_preset,
    )

    print(f"Generated map outputs for {visual_map_id}:")
    for label, path in output_paths.items():
        print(f"  - {label}: {path}")

    if not args.skip_ppt and "pptx" in direction_plan["output_targets"]:
        ppt_path = output_dir / f"{visual_map_id}.pptx"
        detail = _maybe_write_native_ppt(payloads["render_spec"], ppt_path)
        if detail is None:
            print(f"  - pptx: {ppt_path}")
        else:
            print(f"  - pptx: {detail}")

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
        "opencode": "adapter_opencode_thin",
        }[args.adapter]
    )
    review = bundle["feature_portfolio_review"]
    eval_report = bundle["eval_run_report"]
    swarm_plan = bundle["autonomous_pm_swarm_plan"]
    swarm_scorecard = bundle["autonomous_pm_swarm_feature_scorecard"]
    gate = _promotion_gate(bundle)
    cutover_plan = _load_stable_cutover_plan(workspace_dir, args.generated_at)
    top_priority_feature = (
        cutover_plan["top_priority_feature_id"]
        if cutover_plan and cutover_plan["selection_status"] == "stable_active" and cutover_plan["stable_release_version"] == "7.0.0"
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
    _print_research_summary(bundle)
    _print_research_posture(bundle)
    _print_strategy_refresh_posture(bundle)
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
    print(f"Default Adapter: {adapter_registry['default_adapter_id']}")
    _print_mission_control(bundle["cockpit_state"])
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
    elif args.target_version.startswith("9."):
        plan = build_v9_cutover_plan_from_workspace(
            _workspace_dir(args),
            generated_at=args.generated_at,
            adapter_name=args.adapter,
            target_version=args.target_version,
        )
        formatter = format_v9_cutover_plan_markdown
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


def cmd_release(args: argparse.Namespace) -> int:
    result = run_public_release(
        ROOT,
        slice_label=args.slice_label,
        released_at=args.released_at,
        approved_by=args.approved_by,
        target_version=args.target_version,
        bump=args.bump,
        commit_message=args.commit_message,
        tag_message=args.tag_message,
        remote=args.remote,
        branch=args.branch,
        push=args.push,
    )
    print(f"Release Version: {result['target_version']}")
    print(f"Release Tag: {result['tag_name']}")
    print(f"Release Branch: {result['branch']}")
    print(f"Release Commit: {result['commit_message']}")
    print(f"Release Metadata: {result['release_path'].relative_to(ROOT)}")
    print(f"Push Status: {'completed' if result['push'] else 'skipped'}")
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


def cmd_v9(args: argparse.Namespace) -> int:
    next_version_bundle = _try_build_bundle(args)
    bundle = build_v9_lifecycle_bundle_from_workspace(
        _workspace_dir(args),
        generated_at=args.generated_at,
        adapter_name=args.adapter,
        next_version_bundle=next_version_bundle,
    )
    print(summarize_v9_lifecycle_bundle(_workspace_dir(args), bundle))
    if args.output_dir:
        _write_artifacts(args.output_dir, bundle, list(V9_ARTIFACT_SCHEMAS.keys()))
    return 0


# V11 Living System Commands


def cmd_queue_build(args: argparse.Namespace) -> int:
    workspace_dir = _workspace_dir(args)
    trigger = {
        "event_type": args.event_type or "artifact_updated",
        "source_artifact_ref": args.source_artifact,
        "change_summary": args.change_summary or "Manual queue build via CLI",
    }

    # Auto-generate impact propagation map if missing
    impact_map_path = workspace_dir / "artifacts" / "impact_propagation_map.json"
    if not impact_map_path.exists():
        impact_map = generate_impact_propagation_map(workspace_dir)
        with impact_map_path.open("w", encoding="utf-8") as f:
            json.dump(impact_map, f, indent=2)
            f.write("\n")
        print(f"Auto-generated: artifacts/impact_propagation_map.json")

    queue = build_regeneration_queue(trigger, workspace_dir, generated_at=args.generated_at)
    
    # Check for circular dependencies
    circular = detect_circular_dependencies(queue["dependency_sequence"], workspace_dir)
    if circular:
        print("FAIL: Circular dependencies detected:")
        for ref in circular:
            print(f"  - {ref}")
        return 1
    
    queue_output_path = (args.output_dir / "regeneration_queue.json") if args.output_dir else _queue_path(workspace_dir)
    _write_json_payload(queue_output_path, queue)
    _sync_cockpit_living_updates(workspace_dir, queue, generated_at=args.generated_at)
    print(f"Regeneration Queue: {queue_output_path}")
    
    print(f"Queue ID: {queue['regeneration_queue_id']}")
    print(f"Status: {queue['status']}")
    print(f"Items: {len(queue['queued_items'])}")
    print(f"Auto-executable: {queue['auto_executed_count']}")
    print(f"PM Review Required: {queue['pm_review_count']}")
    
    for item in queue["queued_items"]:
        print(f"  - {item['item_id']}: {item['target_artifact_ref']} [{item['impact_classification']}] -> {item['status']}")
        print(f"    Delta: {item['delta_preview']}")
    
    return 0


def cmd_queue_review(args: argparse.Namespace) -> int:
    workspace_dir = _workspace_dir(args)
    
    # Load existing queue
    queue_path = args.queue_path or (workspace_dir / "outputs" / "operate" / "regeneration_queue.json")
    if not queue_path.exists():
        raise SystemExit(f"No regeneration queue found at {queue_path}")
    
    queue = _load_json(queue_path)
    
    # Find the item
    item = next((i for i in queue["queued_items"] if i["item_id"] == args.item_id), None)
    if item is None:
        raise SystemExit(f"Item {args.item_id} not found in queue")
    
    processed = process_regeneration_item(
        item,
        workspace_dir,
        action=args.action,
        pm_note=args.pm_note or "",
        generated_at=args.generated_at,
    )
    
    # Update queue
    for idx, q_item in enumerate(queue["queued_items"]):
        if q_item["item_id"] == args.item_id:
            queue["queued_items"][idx] = processed
            break
    
    # Write back
    _write_json_payload(queue_path, queue)
    _sync_cockpit_living_updates(workspace_dir, queue, generated_at=args.generated_at)
    
    print(f"Item {args.item_id}: {processed['status']}")
    print(f"Action: {args.action}")
    if args.pm_note:
        print(f"PM Note: {args.pm_note}")
    print(f"Log: {processed['execution_log'][-1] if processed['execution_log'] else 'No log'}")
    
    return 0


def cmd_render_doc(args: argparse.Namespace) -> int:
    workspace_dir = _workspace_dir(args)
    
    try:
        rendered = render_living_document(
            args.doc_key,
            workspace_dir,
            generated_at=args.generated_at,
        )
    except ValueError as exc:
        raise SystemExit(str(exc))
    except FileNotFoundError as exc:
        raise SystemExit(str(exc))
    
    output_path = args.output_path or (workspace_dir / "docs" / f"{args.doc_key}.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    
    print(f"Rendered: {output_path}")
    print(f"Doc Key: {args.doc_key}")
    print(f"Lines: {len(rendered.splitlines())}")
    
    return 0


def cmd_render_docs(args: argparse.Namespace) -> int:
    workspace_dir = _workspace_dir(args)
    rendered_docs = render_all_living_documents(
        workspace_dir,
        generated_at=args.generated_at,
    )
    if not rendered_docs:
        raise SystemExit("No renderable living documents found for the current workspace.")
    for doc_key, rendered in rendered_docs.items():
        output_path = workspace_dir / "docs" / f"{doc_key}.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
        print(f"Rendered: {output_path}")
    print(f"Rendered Documents: {len(rendered_docs)}")
    return 0


def cmd_render_journey_map(args: argparse.Namespace) -> int:
    workspace_dir = _workspace_dir(args)
    
    journey_map_path = workspace_dir / "artifacts" / "customer_journey_map.json"
    if not journey_map_path.exists():
        raise SystemExit(f"No customer_journey_map.json found in {journey_map_path}")
    
    with journey_map_path.open("r", encoding="utf-8") as handle:
        journey_map = json.load(handle)
    
    design_tokens = None
    design_tokens_path = workspace_dir / "artifacts" / "design_token_set.json"
    if design_tokens_path.exists():
        with design_tokens_path.open("r", encoding="utf-8") as handle:
            design_tokens = json.load(handle)
    
    html = render_customer_journey_map_html(journey_map, design_tokens)
    
    output_path = workspace_dir / "outputs" / "discover" / "customer_journey_map.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        handle.write(html)
    
    print(json.dumps({"status": "ok", "output_path": str(output_path)}))
    return 0


def cmd_render_screen_flow(args: argparse.Namespace) -> int:
    workspace_dir = _workspace_dir(args)

    # Prefer user_journey_map.json, fall back to customer_journey_map.json
    ujm_path = workspace_dir / "artifacts" / "user_journey_map.json"
    cjm_path = workspace_dir / "artifacts" / "customer_journey_map.json"

    design_tokens = None
    design_tokens_path = workspace_dir / "artifacts" / "design_token_set.json"
    if design_tokens_path.exists():
        with design_tokens_path.open("r", encoding="utf-8") as handle:
            design_tokens = json.load(handle)

    if ujm_path.exists():
        with ujm_path.open("r", encoding="utf-8") as handle:
            user_journey_map = json.load(handle)
        svg = generate_screen_flow_svg(user_journey_map, design_tokens)
    elif cjm_path.exists():
        with cjm_path.open("r", encoding="utf-8") as handle:
            journey_map = json.load(handle)
        svg = generate_screen_flow_from_journey_stages(journey_map, design_tokens)
    else:
        raise SystemExit(f"No user_journey_map.json or customer_journey_map.json found in {workspace_dir / 'artifacts'}")

    output_path = workspace_dir / "outputs" / "discover" / "screen_flow.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    html = _wrap_svg_in_html(svg, user_journey_map.get("title", "Screen Flow") if ujm_path.exists() else journey_map.get("title", "Screen Flow"))
    with output_path.open("w", encoding="utf-8") as handle:
        handle.write(html)

    print(json.dumps({"status": "ok", "output_path": str(output_path)}))
    return 0


def cmd_render_prototype(args: argparse.Namespace) -> int:
    workspace_dir = _workspace_dir(args)
    bundle_paths = write_prototype_bundle(workspace_dir, generated_at=args.generated_at)
    print(f"Prototype HTML: {bundle_paths['prototype_html']}")
    print(f"Story Map HTML: {bundle_paths['story_map_html']}")
    print(f"Prototype Quality Report: {bundle_paths['prototype_quality_report']}")
    return 0


def _wrap_svg_in_html(svg: str, title: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>body {{ margin: 0; padding: 24px; background: #F8FAFC; font-family: Inter, system-ui, sans-serif; }}</style>
</head>
<body>
  {svg}
</body>
</html>"""


def cmd_review_delta(args: argparse.Namespace) -> int:
    workspace_dir = _workspace_dir(args)
    
    # Load cockpit state to find the living updates queue
    cockpit_path = workspace_dir / "outputs" / "cockpit" / "cockpit_bundle.json"
    if cockpit_path.exists():
        cockpit = _load_json(cockpit_path)
        living_updates = cockpit.get("cockpit_state", {}).get("living_updates_queue", [])
    else:
        living_updates = []
    
    update = next((u for u in living_updates if u["update_id"] == args.update_id), None)
    if update is None:
        raise SystemExit(f"Update {args.update_id} not found in cockpit living updates queue")
    
    update["pm_action"] = args.action
    if args.pm_note:
        update["pm_note"] = args.pm_note
    update["reviewed_at"] = args.generated_at

    print(f"Update {args.update_id}: {args.action}")
    print(f"Target: {update['target_artifact']}")
    print(f"Classification: {update['impact_classification']}")
    if args.pm_note:
        print(f"PM Note: {args.pm_note}")

    queue_path = _queue_path(workspace_dir)
    if queue_path.exists():
        queue = _load_json(queue_path)
        queue_item = next(
            (item for item in queue.get("queued_items", []) if item["item_id"] == update["regeneration_queue_item_ref"]),
            None,
        )
        if queue_item is not None:
            processed = process_regeneration_item(
                queue_item,
                workspace_dir,
                action=args.action,
                pm_note=args.pm_note or "",
                generated_at=args.generated_at,
            )
            for index, item in enumerate(queue["queued_items"]):
                if item["item_id"] == processed["item_id"]:
                    queue["queued_items"][index] = processed
                    break
            _write_json_payload(queue_path, queue)
            update["pm_action"] = processed["status"]
            update["pm_note"] = processed.get("pm_note", update.get("pm_note", ""))
            if processed["execution_log"]:
                print(f"Log: {processed['execution_log'][-1]}")
        elif args.action == "approve":
            print(f"Approved. Downstream regeneration queued for {update['target_artifact']}")
    elif args.action == "approve":
        print(f"Approved. Downstream regeneration queued for {update['target_artifact']}")
    if args.action == "reject":
        feedback_path = workspace_dir / "outputs" / "operate" / "living_system_rejection_feedback.json"
        feedback = _load_json(feedback_path) if feedback_path.exists() else {"items": []}
        feedback["items"].append(
            {
                "update_id": args.update_id,
                "target_artifact": update["target_artifact"],
                "reason": args.pm_note or "No reason provided",
                "reviewed_at": args.generated_at,
            }
        )
        _write_json_payload(feedback_path, feedback)
        print(f"Rejected. Downstream propagation blocked for {update['target_artifact']}")

    if cockpit_path.exists():
        _write_json_payload(cockpit_path, cockpit)
        if {"mission_brief", "active_phase_packet", "product_record", "workspace_tree_state", "portfolio_state"} <= set(cockpit.keys()):
            (workspace_dir / "outputs" / "cockpit" / "cockpit.html").write_text(
                render_cockpit_html(cockpit),
                encoding="utf-8",
            )
    
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


def cmd_start(args: argparse.Namespace) -> int:
    if _interactive_start_required(args):
        return _run_guided_start(args)

    kind = _start_kind_from_args(args)
    if kind == "import":
        mode = _normalized_text(args.mode)
        if mode not in START_MODE_TO_MATURITY_BAND:
            raise SystemExit("`start --kind import` requires --mode startup or --mode enterprise.")
        if args.source is None or args.dest is None:
            raise SystemExit("`start --kind import --non-interactive` requires --source and --dest.")
        workspace_id = _normalized_text(args.workspace_id)
        name = _normalized_text(args.name)
        if workspace_id is None or name is None:
            raise SystemExit("`start --kind import --non-interactive` requires --workspace-id and --name.")
        return _run_workspace_adoption(
            source=args.source,
            dest=args.dest,
            workspace_id=workspace_id,
            name=name,
            mode=mode,
            generated_at=args.generated_at,
            review_threshold=args.review_threshold,
            guided=False,
        )

    if args.dest is None:
        raise SystemExit("`start --non-interactive` requires --dest.")
    workspace_id = _normalized_text(args.workspace_id)
    name = _normalized_text(args.name)
    mode = _normalized_text(args.mode)
    title = _normalized_text(args.title)
    customer_problem = _normalized_text(args.customer_problem)
    business_goal = _normalized_text(args.business_goal)
    if None in {workspace_id, name, mode, title, customer_problem, business_goal}:
        raise SystemExit(
            "`start --non-interactive` requires --workspace-id, --name, --mode, --title, --customer-problem, and --business-goal."
        )
    success_metrics = args.success_metric or ["time to reviewable PM package"]
    primary_kpis = args.primary_kpi or success_metrics
    primary_outcomes = args.primary_outcome or ["Create one reviewable PM package"]
    return _run_start_new(
        dest=args.dest,
        workspace_id=workspace_id,
        name=name,
        mode=mode,
        title=title,
        customer_problem=customer_problem,
        business_goal=business_goal,
        success_metrics=success_metrics,
        primary_kpis=primary_kpis,
        primary_outcomes=primary_outcomes,
        target_user=args.target_user or "Product manager",
        operating_mode=args.operating_mode,
        generated_at=args.generated_at,
        maturity_band=args.maturity_band,
        constraints=args.constraint,
        audience=args.audience,
        review_gate_owner=args.review_gate_owner,
        portfolio_id=args.portfolio_id,
        stage_goals=_parse_phase_goals(args.stage_goal),
        known_risks=args.known_risk,
        template_name=args.template,
        guided=False,
    )


def cmd_init_mission(args: argparse.Namespace) -> int:
    workspace_dir = _workspace_dir(args)
    primary_kpis = args.primary_kpi or args.success_metric
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
        maturity_band=args.maturity_band,
        primary_outcomes=args.primary_outcome,
        primary_kpis=primary_kpis,
        review_gate_owner=args.review_gate_owner,
        portfolio_id=args.portfolio_id,
        stage_goals=_parse_phase_goals(args.stage_goal),
        known_risks=args.known_risk,
    )
    print(f"Mission Brief: {mission_brief['mission_brief_id']}")
    print(f"Workspace: {workspace_dir}")
    print(f"Operating Mode: {mission_brief['operating_mode']}")
    print(f"Maturity Band: {mission_brief['maturity_band']}")
    print(f"Primary Workflows: {len(mission_brief['primary_workflow_refs'])}")
    print(f"Next Action: {mission_brief['next_action']}")
    return 0


def _slugify_problem(problem: str) -> str:
    """Convert a problem statement into a workspace-friendly slug."""
    cleaned = problem.lower().strip().rstrip(".")
    for char in " -/\\:":
        cleaned = cleaned.replace(char, "_")
    for char in "!?,'\"()":
        cleaned = cleaned.replace(char, "")
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    return cleaned[:60]


def cmd_new(args: argparse.Namespace) -> int:
    """V12: One-command workspace creation from a raw problem statement."""
    problem_statement = args.problem_statement
    if not problem_statement:
        raise SystemExit("Usage: productos new 'Problem statement here'")

    slug = _slugify_problem(problem_statement)
    workspace_id = f"ws_{slug}"
    name = problem_statement[:80]
    dest = Path(args.dest or workspace_id).resolve()

    if dest.exists():
        raise SystemExit(f"Destination already exists: {dest}")

    mode = args.mode or "startup"
    title = problem_statement[:120]
    customer_problem = problem_statement
    business_goal = f"Solve: {problem_statement}"
    success_metrics = [f"Ship MVP that addresses {slug}"]
    primary_kpis = success_metrics
    primary_outcomes = [f"Create reviewable PRD and prototype plan for {slug}"]

    init_workspace_from_template(
        ROOT,
        template_name="templates",
        dest=dest,
        workspace_id=workspace_id,
        name=name,
        mode=mode,
    )

    mission_brief = init_mission_in_workspace(
        dest,
        title=title,
        target_user="Product manager",
        customer_problem=customer_problem,
        business_goal=business_goal,
        success_metrics=success_metrics,
        constraints=[],
        audience=[],
        operating_mode="discover_to_align",
        generated_at=args.generated_at,
        maturity_band="zero_to_one",
        primary_outcomes=primary_outcomes,
        primary_kpis=primary_kpis,
        review_gate_owner="ProductOS PM",
        portfolio_id=None,
    )
    generated_artifacts = _build_new_workspace_artifacts(
        problem_statement,
        workspace_id=workspace_id,
        generated_at=args.generated_at,
    )
    for artifact_name, payload in generated_artifacts.items():
        _write_json_payload(dest / "artifacts" / f"{artifact_name}.json", payload)

    sync_canonical_discover_artifacts(
        dest,
        mission_brief=mission_brief,
        generated_at=args.generated_at,
        problem_brief=generated_artifacts["problem_brief"],
        concept_brief=generated_artifacts["concept_brief"],
        prd=generated_artifacts["prd"],
    )
    sync_memory_registers(
        dest,
        generated_at=args.generated_at,
        problem_brief=generated_artifacts["problem_brief"],
        competitor_dossier=generated_artifacts["competitor_dossier"],
    )

    runtime_adapter_registry = build_runtime_adapter_registry(dest, generated_at=args.generated_at)
    _write_json_payload(dest / "artifacts" / "runtime_adapter_registry.json", runtime_adapter_registry)

    cockpit_bundle = build_cockpit_bundle_from_workspace(dest, generated_at=args.generated_at, adapter_name=args.adapter)
    cockpit_bundle["cockpit_state"]["mode"] = "plan"
    cockpit_bundle["cockpit_state"]["status"] = "active"
    cockpit_bundle["cockpit_state"]["current_focus"] = "Discovery phase initialization"
    cockpit_bundle["cockpit_state"].setdefault("living_updates_queue", [])
    cockpit_bundle["cockpit_state"].setdefault("mission_control", {})
    cockpit_bundle["cockpit_state"]["mission_control"]["active_stage"] = "discover"
    cockpit_bundle["cockpit_state"]["recommended_next_step"] = {
        "action_summary": f"Run ./productos --workspace-dir {dest} run discover"
    }
    _write_json_payload(dest / "outputs" / "cockpit" / "cockpit_bundle.json", cockpit_bundle)
    (dest / "outputs" / "cockpit" / "cockpit.html").write_text(
        render_cockpit_html(cockpit_bundle),
        encoding="utf-8",
    )

    quality_snapshot = _build_quality_snapshot(dest, generated_artifacts)
    _write_json_payload(dest / "outputs" / "cockpit" / "quality_snapshot.json", quality_snapshot)

    print(f"Created workspace: {dest}")
    print(f"Workspace ID: {workspace_id}")
    print(f"Mission: {mission_brief['title']}")
    print("Artifacts: mission_brief, problem_brief, problem_register, concept_brief, prd, competitor_dossier, competitor_registry, persona_pack, market_analysis_brief, cockpit_state")
    print(f"Cockpit HTML: {dest / 'outputs' / 'cockpit' / 'cockpit.html'}")
    print(f"Quality Snapshot: {dest / 'outputs' / 'cockpit' / 'quality_snapshot.json'}")
    print(f"Next: ./productos --workspace-dir {dest} run discover")
    return 0


def cmd_agent_context(args: argparse.Namespace) -> int:
    workspace_dir = _workspace_dir(args)
    payload = build_agent_context(
        workspace_dir,
        target=args.target,
        generated_at=args.generated_at,
    )
    if args.output_path:
        _write_json_payload(args.output_path, payload)
        print(f"Agent Context: {args.output_path}")
    else:
        print(json.dumps(payload, indent=2))
    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    source_dir = ROOT / "tests" / "fixtures" / "workspaces" / "productos-sample"
    if not source_dir.exists():
        raise SystemExit("No bundled demo workspace available.")
    dest = (args.dest or (ROOT / "tmp" / "productos-demo")).resolve()
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(source_dir, dest)
    print(f"Demo Workspace: {dest}")
    print(f"Run: ./productos --workspace-dir {dest} status")
    cockpit_html = dest / "outputs" / "cockpit" / "cockpit.html"
    if not cockpit_html.exists():
        cockpit_bundle = build_cockpit_bundle_from_workspace(dest, generated_at=args.generated_at, adapter_name=args.adapter)
        _write_json_payload(dest / "outputs" / "cockpit" / "cockpit_bundle.json", cockpit_bundle)
        cockpit_html.write_text(render_cockpit_html(cockpit_bundle), encoding="utf-8")
    print(f"Cockpit HTML: {cockpit_html}")
    return 0


def cmd_phase_plan(args: argparse.Namespace) -> int:
    workspace_dir = _workspace_dir(args)
    mission_brief = load_mission_brief_from_workspace(workspace_dir)
    if mission_brief is None:
        raise SystemExit(f"No mission brief found in {workspace_dir}. Run `./productos init-mission` first.")
    phase_packet = write_phase_packet_for_workspace(
        workspace_dir,
        mission_brief=mission_brief,
        lifecycle_phase=args.phase,
        generated_at=args.generated_at,
    )
    if args.output_dir is not None:
        _write_json_payload(args.output_dir / f"phase_packet_{args.phase}.json", phase_packet)
    print(f"Phase Packet: {phase_packet['phase_packet_id']}")
    print(f"Lifecycle Phase: {phase_packet['lifecycle_phase']}")
    print(f"Tasks: {len(phase_packet['task_queue'])}")
    return 0


def cmd_cockpit_build(args: argparse.Namespace) -> int:
    workspace_dir = _workspace_dir(args)
    cockpit_bundle = build_cockpit_bundle_from_workspace(
        workspace_dir,
        generated_at=args.generated_at,
        adapter_name=args.adapter,
    )
    failures = _validate_named_bundle(
        {"cockpit_bundle": cockpit_bundle},
        {"cockpit_bundle": "cockpit_bundle.schema.json"},
    )
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    output_dir = args.output_dir or (workspace_dir / "outputs" / "cockpit")
    output_dir.mkdir(parents=True, exist_ok=True)
    bundle_path = output_dir / "cockpit_bundle.json"
    html_path = output_dir / "control-center.html"
    _write_json_payload(bundle_path, cockpit_bundle)
    html_path.write_text(render_cockpit_html(cockpit_bundle), encoding="utf-8")
    print(f"Cockpit Bundle: {bundle_path}")
    print(f"Cockpit HTML: {html_path}")
    print(f"Mission: {cockpit_bundle['mission_brief']['title']}")
    return 0


def cmd_portfolio_build(args: argparse.Namespace) -> int:
    workspace_dirs = args.workspace or [_workspace_dir(args)]
    portfolio_state = build_portfolio_state_from_workspaces(
        workspace_dirs,
        generated_at=args.generated_at,
        suite_id=args.suite_id,
    )
    cross_product_insight_index = build_cross_product_insight_index(
        workspace_dirs,
        generated_at=args.generated_at,
        portfolio_id=args.suite_id,
    )
    failures = _validate_named_bundle(
        {
            "portfolio_state": portfolio_state,
            "cross_product_insight_index": cross_product_insight_index,
        },
        {
            "portfolio_state": "portfolio_state.schema.json",
            "cross_product_insight_index": "cross_product_insight_index.schema.json",
        },
    )
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    output_dir = args.output_dir or ROOT / "outputs" / "portfolio"
    output_dir.mkdir(parents=True, exist_ok=True)
    portfolio_path = output_dir / "portfolio_state.json"
    insight_index_path = output_dir / "cross_product_insight_index.json"
    _write_json_payload(portfolio_path, portfolio_state)
    _write_json_payload(insight_index_path, cross_product_insight_index)
    print(f"Portfolio State: {portfolio_path}")
    print(f"Cross Product Insight Index: {insight_index_path}")
    print(f"Suite: {portfolio_state['suite_id']}")
    print(f"Products: {len(portfolio_state['product_summaries'])}")
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


def cmd_thread_review(args: argparse.Namespace) -> int:
    bundle = build_thread_review_bundle_from_workspace(
        _workspace_dir(args),
        item_id=args.item_id,
        generated_at=args.generated_at,
    )
    failures = _validate_named_bundle({"thread_review_bundle": bundle}, {"thread_review_bundle": "thread_review_bundle.schema.json"})
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    write_thread_review_page(bundle, args.output_path)
    if args.markdown_path:
        write_thread_review_markdown(bundle, args.markdown_path)
    if args.package_dir:
        package = build_thread_review_presentation_package(bundle, aspect_ratio=args.aspect_ratio)
        package_paths = write_thread_review_package(bundle, args.package_dir, aspect_ratio=args.aspect_ratio)
        print(f"Package: {args.package_dir}")
        print(f"Deck: {package_paths['presentation_html']}")
        print(f"Corridor: {package_paths['corridor_html']}")
        print(f"Slides: {len(package['presentation_story']['slides'])}")
    print(f"Thread Review: {bundle['title']}")
    print(f"Item: {bundle['item_ref']['entity_id']}")
    print(f"Current Stage: {bundle['current_stage']}")
    print(f"Output: {args.output_path}")
    return 0


def cmd_thread_review_index(args: argparse.Namespace) -> int:
    site = write_thread_review_index_site(
        _workspace_dir(args),
        args.output_dir,
        generated_at=args.generated_at,
        aspect_ratio=args.aspect_ratio,
    )
    print(f"Thread Review Index: {site['index_path']}")
    print(f"Threads: {site['thread_count']}")
    return 0


def cmd_thread_review_release_check(args: argparse.Namespace) -> int:
    result = build_thread_review_release_bundle_from_workspace(
        _workspace_dir(args),
        item_id=args.item_id,
        generated_at=args.generated_at,
        output_dir=args.output_dir,
        target_release=args.target_release,
    )
    failures = _validate_named_bundle(result["release_bundle"], THREAD_REVIEW_RELEASE_ARTIFACT_SCHEMAS)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    release_gate = result["release_bundle"]["release_gate_decision_thread_review_release"]
    validation = result["release_bundle"]["validation_lane_report_thread_review_release"]
    print(f"Thread Review Release Check: {args.output_dir}")
    print(f"Item: {result['thread_review_bundle']['item_ref']['entity_id']}")
    print(f"Validation: {validation['overall_status']}")
    print(f"Decision: {release_gate['decision']}")
    print(f"Target Release: {release_gate['target_release']}")
    print(f"Index Threads: {result['index_site']['thread_count']}")
    return 0


def cmd_adopt_workspace(args: argparse.Namespace) -> int:
    return _run_workspace_adoption(
        source=args.source,
        dest=args.dest,
        workspace_id=args.workspace_id,
        name=args.name,
        mode=args.mode,
        generated_at=args.generated_at,
        review_threshold=args.review_threshold,
        emit_report=args.emit_report,
        emit_thread_page=args.emit_thread_page,
        include_runtime_support_assets=args.include_runtime_support_assets,
        dry_run=args.dry_run,
        output_dir=args.output_dir,
        guided=False,
    )


def cmd_takeover(args: argparse.Namespace) -> int:
    workspace_id = args.workspace_id
    bundle = build_takeover_bundle(
        ROOT,
        source_dir=args.source,
        dest=args.dest,
        workspace_id=workspace_id,
        name=args.name,
        mode=args.mode,
        generated_at=args.generated_at,
    )

    failures = _validate_named_bundle(bundle, TAKEOVER_ARTIFACT_SCHEMAS)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    output_dir = args.output_dir or (Path(args.dest) / "outputs" / "takeover")
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_artifacts(output_dir, bundle, {"takeover_brief": "takeover_brief.json", "problem_space_map": "problem_space_map.json", "roadmap_recovery_brief": "roadmap_recovery_brief.json", "visual_product_atlas": "visual_product_atlas.json", "takeover_feature_scorecard": "takeover_feature_scorecard.json"})

    takeover_brief = bundle["takeover_brief"]
    print(f"Takeover Brief: {takeover_brief['takeover_brief_id']}")
    print(f"Problems: {len(bundle['problem_space_map']['problems'])}")
    print(f"Evidence Gaps: {len(takeover_brief['evidence_gaps'])}")
    print(f"Visual Records: {len(bundle['visual_product_atlas']['visual_evidence_records'])}")
    print(f"Scorecard: {bundle['takeover_feature_scorecard']['overall_score']}/5")
    print(f"Destination: {args.dest}")

    if args.live_research:
        print("Live research flag not yet implemented: use `run-research-loop` separately.")
    return 0


def cmd_render_takeover_atlas(args: argparse.Namespace) -> int:
    workspace_dir = args.workspace_dir.resolve() if args.workspace_dir else _workspace_dir(args)
    ws_id = workspace_dir.name
    with open(workspace_dir / "workspace_manifest.yaml", "r") as f:
        import yaml
        manifest = yaml.safe_load(f)
        ws_id = manifest.get("workspace_id", ws_id)

    takeover_brief = _load_json(workspace_dir / "artifacts" / f"takeover_brief_{ws_id}.json")
    problem_space_map = _load_json(workspace_dir / "artifacts" / f"problem_space_map_{ws_id}.json")
    roadmap_recovery = _load_json(workspace_dir / "artifacts" / f"roadmap_recovery_brief_{ws_id}.json")
    visual_atlas = _load_json(workspace_dir / "artifacts" / f"visual_product_atlas_{ws_id}.json")
    scorecard_path = workspace_dir / "artifacts" / f"takeover_feature_scorecard_{ws_id}.json"
    scorecard = _load_json(scorecard_path) if scorecard_path.exists() else None

    html = render_takeover_atlas_html(takeover_brief, problem_space_map, roadmap_recovery, visual_atlas, takeover_feature_scorecard=scorecard)
    output_path = args.output_path or (workspace_dir / "outputs" / "takeover" / "takeover_atlas.html")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    print(f"Takeover Atlas HTML: {output_path}")
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
        _write_source_note_cards(args.output_dir, bundle)
    print(f"Research Sources: {args.input_manifest}")
    print(f"Artifacts Refreshed: {len(RESEARCH_RUNTIME_ARTIFACTS)}")
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
    print(
        "Signal Lanes Planned: "
        f"{len(plan.get('coverage_summary', {}).get('planned_signal_lanes', []))}/"
        f"{len(plan.get('coverage_summary', {}).get('required_signal_lanes', ['market', 'competitor', 'customer']))}"
    )
    print(f"Suggested Sources: {len(plan['suggested_manifest_sources'])}")
    print(f"Next Step: {plan['coverage_summary']['recommended_next_step']}")
    return 0


def cmd_init_feed_registry(args: argparse.Namespace) -> int:
    workspace_dir = _workspace_dir(args)
    bundle = build_external_research_feed_registry_from_workspace(
        ROOT,
        workspace_dir=workspace_dir,
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
    competitor_dossier_path = workspace_dir / "artifacts" / "competitor_dossier.json"
    if competitor_dossier_path.exists() and not args.no_persist:
        sync_memory_registers(
            workspace_dir,
            generated_at=args.generated_at,
            competitor_dossier=_load_json(competitor_dossier_path),
            feed_registry=bundle["external_research_feed_registry"],
        )
    registry = bundle["external_research_feed_registry"]
    print(f"Feed Registry: {registry['external_research_feed_registry_id']}")
    print(f"Registered Feeds: {len(registry['feeds'])}")
    return 0


def cmd_discover_research_sources(args: argparse.Namespace) -> int:
    workspace_dir = _workspace_dir(args)
    bundle = discover_external_research_sources_from_workspace(
        ROOT,
        workspace_dir=workspace_dir,
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
    competitor_dossier_path = workspace_dir / "artifacts" / "competitor_dossier.json"
    registry_path = workspace_dir / "artifacts" / "external_research_feed_registry.json"
    if competitor_dossier_path.exists() and registry_path.exists() and not args.no_persist:
        sync_memory_registers(
            workspace_dir,
            generated_at=args.generated_at,
            competitor_dossier=_load_json(competitor_dossier_path),
            feed_registry=_load_json(registry_path),
        )
    if args.output_dir:
        _write_artifacts(args.output_dir, bundle, RESEARCH_DISCOVERY_ARTIFACTS)
    discovery = bundle["external_research_source_discovery"]
    print(f"Source Discovery: {discovery['external_research_source_discovery_id']}")
    print(f"Search Provider: {discovery['search_provider']}")
    print(f"Search Status: {discovery['search_status']}")
    print(
        "Signal Lanes Discovered: "
        f"{sum(1 for item in discovery.get('signal_lane_coverage', []) if item.get('candidate_source_count', 0) > 0)}/3"
    )
    print(f"Candidate Sources: {len(discovery['candidate_sources'])}")
    return 0


def cmd_run_research_loop(args: argparse.Namespace) -> int:
    workspace_dir = _workspace_dir(args)
    bundle, summary = run_external_research_loop_from_workspace(
        ROOT,
        workspace_dir=workspace_dir,
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
    if not args.no_persist and bundle.get("competitor_dossier") is not None:
        sync_memory_registers(
            workspace_dir,
            generated_at=args.generated_at,
            competitor_dossier=bundle.get("competitor_dossier"),
            feed_registry=bundle.get("external_research_feed_registry"),
        )
    if args.output_dir:
        _write_artifacts(args.output_dir, bundle, output_names)
        _write_source_note_cards(args.output_dir, bundle)
    print(f"Research Loop Coverage: {summary['coverage_status']}")
    print(f"Research Refresh: {summary['refresh_status']}")
    print(f"Planned Questions: {summary['planned_question_count']}")
    print(f"Candidate Sources: {summary['candidate_source_count']}")
    print(f"Selected Sources: {summary['selected_source_count']}")
    print(
        "Signal Lanes Selected: "
        f"{summary['selected_signal_lane_count']}/{summary['required_signal_lane_count']}"
    )
    print(f"Review Required: {len(summary['review_items'])}")
    for item in summary["review_items"]:
        print(f"- {item}")
    if summary["refresh_status"] == "completed":
        candidate_source = None
        for ref in (
            "artifacts/competitor_dossier.json",
            "artifacts/customer_pulse.json",
            "artifacts/market_analysis_brief.json",
        ):
            if (_workspace_dir(args) / ref).exists():
                candidate_source = ref
                break
        if candidate_source is not None:
            trigger = {
                "event_type": "research_fresh",
                "source_artifact_ref": candidate_source,
                "change_summary": "Research loop refreshed source artifacts and may require downstream living updates.",
            }
            impact_map_path = _workspace_dir(args) / "artifacts" / "impact_propagation_map.json"
            if not impact_map_path.exists():
                _write_json_payload(impact_map_path, generate_impact_propagation_map(_workspace_dir(args)))
            queue = build_regeneration_queue(trigger, _workspace_dir(args), generated_at=args.generated_at)
            _write_json_payload(_queue_path(_workspace_dir(args)), queue)
            _sync_cockpit_living_updates(_workspace_dir(args), queue, generated_at=args.generated_at)
            print(f"Auto-Cascade Queue Items: {len(queue['queued_items'])}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ProductOS next-version repo CLI.")
    parser.add_argument("--workspace-dir", type=Path)
    parser.add_argument("--generated-at", default="2026-03-22T08:00:00Z")
    parser.add_argument(
        "--adapter",
        default="codex",
        choices=["codex", "claude", "windsurf", "antigravity", "opencode"],
    )
    parser.add_argument(
        "--format",
        dest="output_format",
        default="text",
        choices=["text", "json"],
        help="Output format: text (human-readable) or json (machine-readable).",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status")
    subparsers.add_parser("review")
    agent_context_parser = subparsers.add_parser("agent-context")
    agent_context_parser.add_argument("--target", choices=["codex", "opencode"], required=True)
    agent_context_parser.add_argument("--output-path", type=Path)

    demo_parser = subparsers.add_parser("demo")
    demo_parser.add_argument("--dest", type=Path, help="Destination directory for the copied demo workspace")

    new_parser = subparsers.add_parser("new")
    new_parser.add_argument("problem_statement", nargs="?", default="", help="Problem statement for the new product")
    new_parser.add_argument("--dest", type=Path, help="Destination directory for the workspace")
    new_parser.add_argument("--mode", choices=["startup", "enterprise"], default="startup")

    ingest = subparsers.add_parser("ingest")
    ingest.add_argument("--output-dir", type=Path)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("phase", choices=["discover", "align", "operate", "improve", "all"])
    run_parser.add_argument("--output-dir", type=Path)
    run_parser.add_argument("--persist", action="store_true")

    export_parser = subparsers.add_parser("export")
    export_parser.add_argument("--output-dir", type=Path)
    export_subparsers = export_parser.add_subparsers(dest="export_command")
    export_artifact_parser = export_subparsers.add_parser("artifact")
    export_artifact_parser.add_argument("--artifact", required=True)
    export_artifact_parser.add_argument("--format", dest="format", choices=["markdown", "deck", "agent_brief", "stakeholder_update", "battle_card", "one_pager"], required=True)
    export_artifact_parser.add_argument("--output-path", type=Path)

    visual_parser = subparsers.add_parser("visual")
    visual_subparsers = visual_parser.add_subparsers(dest="visual_command", required=True)
    visual_plan_parser = visual_subparsers.add_parser("plan")
    visual_plan_subparsers = visual_plan_parser.add_subparsers(dest="visual_surface", required=True)
    visual_build_parser = visual_subparsers.add_parser("build")
    visual_build_parser.add_argument("visual_direction_plan", type=Path)
    visual_build_parser.add_argument("--output-dir", type=Path)
    visual_build_parser.add_argument("--skip-ppt", action="store_true")
    visual_review_parser = visual_subparsers.add_parser("review")
    visual_review_parser.add_argument("target", type=Path)
    visual_review_parser.add_argument("--output-path", type=Path)
    visual_export_parser = visual_subparsers.add_parser("export")
    visual_export_subparsers = visual_export_parser.add_subparsers(dest="visual_surface", required=True)

    visual_plan_deck_parser = visual_plan_subparsers.add_parser("deck")
    visual_plan_deck_parser.add_argument("presentation_brief", type=Path)
    visual_plan_deck_parser.add_argument("--output-path", type=Path)
    visual_plan_deck_parser.add_argument("--aspect-ratio", choices=["16:9", "4:3"], default="16:9")

    visual_plan_corridor_parser = visual_plan_subparsers.add_parser("corridor")
    visual_plan_corridor_parser.add_argument("source_bundle", type=Path)
    visual_plan_corridor_parser.add_argument("--output-path", type=Path)
    visual_plan_corridor_parser.add_argument(
        "--audience-mode",
        default="customer_safe_public",
        choices=["customer_safe_public", "buyer_exec", "operator_review", "product_browse"],
    )
    visual_plan_corridor_parser.add_argument(
        "--publication-mode",
        default="publishable_external",
        choices=["publishable_external", "product_browse", "internal_review"],
    )

    visual_plan_map_parser = visual_plan_subparsers.add_parser("map")
    visual_plan_map_parser.add_argument("visual_map_spec", type=Path)
    visual_plan_map_parser.add_argument("--output-path", type=Path)
    visual_plan_map_parser.add_argument("--aspect-ratio", choices=["16:9", "4:3"], default="16:9")
    visual_plan_map_parser.add_argument("--theme-preset", default="atlas")

    visual_deck_parser = visual_export_subparsers.add_parser("deck")
    visual_deck_parser.add_argument("presentation_brief", type=Path)
    visual_deck_parser.add_argument("--output-dir", type=Path)
    visual_deck_parser.add_argument("--aspect-ratio", choices=["16:9", "4:3"], default="16:9")
    visual_deck_parser.add_argument("--skip-ppt", action="store_true")
    visual_deck_parser.add_argument("--node-ppt-output", type=Path)
    visual_deck_parser.add_argument("--node-binary", default="node")

    visual_corridor_parser = visual_export_subparsers.add_parser("corridor")
    visual_corridor_parser.add_argument("source_bundle", type=Path)
    visual_corridor_parser.add_argument("--output-dir", type=Path)
    visual_corridor_parser.add_argument(
        "--audience-mode",
        default="customer_safe_public",
        choices=["customer_safe_public", "buyer_exec", "operator_review", "product_browse"],
    )
    visual_corridor_parser.add_argument(
        "--publication-mode",
        default="publishable_external",
        choices=["publishable_external", "product_browse", "internal_review"],
    )

    visual_map_parser = visual_export_subparsers.add_parser("map")
    visual_map_parser.add_argument("visual_map_spec", type=Path)
    visual_map_parser.add_argument("--output-dir", type=Path)
    visual_map_parser.add_argument("--aspect-ratio", choices=["16:9", "4:3"], default="16:9")
    visual_map_parser.add_argument("--theme-preset", default="atlas")
    visual_map_parser.add_argument("--skip-ppt", action="store_true")

    trace_parser = subparsers.add_parser("trace")
    trace_group = trace_parser.add_mutually_exclusive_group(required=True)
    trace_group.add_argument("--item-id")
    trace_group.add_argument("--stage", choices=["discovery", "delivery", "launch", "outcomes", "full_lifecycle"])

    thread_review_parser = subparsers.add_parser("thread-review")
    thread_review_parser.add_argument("--item-id")
    thread_review_parser.add_argument("--output-path", type=Path, required=True)
    thread_review_parser.add_argument("--markdown-path", type=Path)
    thread_review_parser.add_argument("--package-dir", type=Path)
    thread_review_parser.add_argument("--aspect-ratio", choices=["16:9", "4:3"], default="16:9")

    thread_review_index_parser = subparsers.add_parser("thread-review-index")
    thread_review_index_parser.add_argument("--output-dir", type=Path, required=True)
    thread_review_index_parser.add_argument("--aspect-ratio", choices=["16:9", "4:3"], default="16:9")

    thread_review_release_parser = subparsers.add_parser("thread-review-release-check")
    thread_review_release_parser.add_argument("--item-id")
    thread_review_release_parser.add_argument("--output-dir", type=Path, required=True)
    thread_review_release_parser.add_argument("--target-release", default="v8_0_0")

    start_parser = subparsers.add_parser("start")
    start_parser.add_argument("--template", choices=["templates"], default="templates")
    start_parser.add_argument("--kind", choices=["new", "import"])
    start_parser.add_argument("--non-interactive", action="store_true")
    start_parser.add_argument("--source", type=Path)
    start_parser.add_argument("--dest", type=Path)
    start_parser.add_argument("--workspace-id")
    start_parser.add_argument("--name")
    start_parser.add_argument("--mode")
    start_parser.add_argument("--title")
    start_parser.add_argument("--target-user", default="Product manager")
    start_parser.add_argument("--customer-problem")
    start_parser.add_argument("--business-goal")
    start_parser.add_argument("--success-metric", action="append")
    start_parser.add_argument("--primary-kpi", action="append")
    start_parser.add_argument("--primary-outcome", action="append")
    start_parser.add_argument("--constraint", action="append")
    start_parser.add_argument("--audience", action="append")
    start_parser.add_argument("--known-risk", action="append")
    start_parser.add_argument("--stage-goal", action="append")
    start_parser.add_argument("--portfolio-id")
    start_parser.add_argument("--review-gate-owner", default="ProductOS PM")
    start_parser.add_argument("--review-threshold", choices=["medium", "high"], default="medium")
    start_parser.add_argument(
        "--maturity-band",
        choices=["zero_to_one", "one_to_ten", "ten_to_hundred", "hundred_to_thousand_plus"],
        default="zero_to_one",
    )
    start_parser.add_argument(
        "--operating-mode",
        choices=["discover", "discover_to_align", "full_loop"],
        default="discover",
    )

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
    mission_parser.add_argument("--primary-kpi", action="append")
    mission_parser.add_argument("--primary-outcome", action="append")
    mission_parser.add_argument("--constraint", action="append")
    mission_parser.add_argument("--audience", action="append")
    mission_parser.add_argument("--known-risk", action="append")
    mission_parser.add_argument("--stage-goal", action="append")
    mission_parser.add_argument("--portfolio-id")
    mission_parser.add_argument("--review-gate-owner", default="ProductOS PM")
    mission_parser.add_argument(
        "--maturity-band",
        choices=["zero_to_one", "one_to_ten", "ten_to_hundred", "hundred_to_thousand_plus"],
        default="zero_to_one",
    )
    mission_parser.add_argument(
        "--operating-mode",
        choices=["discover", "discover_to_align", "full_loop"],
        default="discover_to_align",
    )

    phase_parser = subparsers.add_parser("phase")
    phase_subparsers = phase_parser.add_subparsers(dest="phase_command", required=True)
    phase_plan_parser = phase_subparsers.add_parser("plan")
    phase_plan_parser.add_argument("phase", choices=["discovery", "validation", "delivery", "launch", "support_learning", "improve"])
    phase_plan_parser.add_argument("--output-dir", type=Path)

    cockpit_parser = subparsers.add_parser("cockpit")
    cockpit_subparsers = cockpit_parser.add_subparsers(dest="cockpit_command", required=True)
    cockpit_build_parser = cockpit_subparsers.add_parser("build")
    cockpit_build_parser.add_argument("--output-dir", type=Path)
    cockpit_build_parser.add_argument("--adapter", choices=["codex", "claude", "windsurf", "antigravity", "opencode"], default="codex")

    portfolio_parser = subparsers.add_parser("portfolio")
    portfolio_subparsers = portfolio_parser.add_subparsers(dest="portfolio_command", required=True)
    portfolio_build_parser = portfolio_subparsers.add_parser("build")
    portfolio_build_parser.add_argument("--workspace", type=Path, action="append")
    portfolio_build_parser.add_argument("--suite-id")
    portfolio_build_parser.add_argument("--output-dir", type=Path)

    takeover_parser = subparsers.add_parser("takeover")
    takeover_parser.add_argument("--source", type=Path, required=True)
    takeover_parser.add_argument("--dest", type=Path, required=True)
    takeover_parser.add_argument("--workspace-id", required=True)
    takeover_parser.add_argument("--name", required=True)
    takeover_parser.add_argument("--mode", required=True)
    takeover_parser.add_argument("--live-research", action="store_true", help="Run live external research refresh as part of the takeover flow.")
    takeover_parser.add_argument("--output-dir", type=Path)

    adopt_parser = subparsers.add_parser("import", aliases=["adopt-workspace"])
    adopt_parser.add_argument("--source", type=Path, required=True)
    adopt_parser.add_argument("--dest", type=Path, required=True)
    adopt_parser.add_argument("--workspace-id", required=True)
    adopt_parser.add_argument("--name", required=True)
    adopt_parser.add_argument("--mode", required=True)
    adopt_parser.add_argument("--review-threshold", choices=["medium", "high"], default="medium")
    adopt_parser.add_argument("--output-dir", type=Path)
    adopt_parser.add_argument("--dry-run", action="store_true")
    adopt_parser.add_argument("--emit-report", action="store_true")
    adopt_parser.add_argument("--emit-thread-page", action="store_true")
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
    v9_parser = subparsers.add_parser("v9")
    v9_parser.add_argument("--output-dir", type=Path)
    cutover_parser = subparsers.add_parser("cutover")
    cutover_parser.add_argument("--target-version", default="7.0.0")
    cutover_parser.add_argument("--output-path", type=Path)
    release_parser = subparsers.add_parser("release")
    release_parser.add_argument("--slice-label", required=True)
    release_parser.add_argument("--released-at", default=_default_timestamp())
    release_parser.add_argument("--approved-by", default="ProductOS PM")
    release_parser.add_argument("--target-version")
    release_parser.add_argument("--bump", choices=["major", "minor", "patch"], default="minor")
    release_parser.add_argument("--commit-message")
    release_parser.add_argument("--tag-message")
    release_parser.add_argument("--remote", default="origin")
    release_parser.add_argument("--branch")
    release_parser.add_argument("--push", action="store_true")

    # V11 Living System CLI
    queue_parser = subparsers.add_parser("queue")
    queue_subparsers = queue_parser.add_subparsers(dest="queue_command", required=True)
    queue_build_parser = queue_subparsers.add_parser("build")
    queue_build_parser.add_argument("--source-artifact", required=True)
    queue_build_parser.add_argument("--event-type", choices=["artifact_updated", "competitive_alert", "pm_note_added", "research_fresh", "stakeholder_feedback"])
    queue_build_parser.add_argument("--change-summary")
    queue_build_parser.add_argument("--output-dir", type=Path)

    queue_review_parser = queue_subparsers.add_parser("review")
    queue_review_parser.add_argument("--queue-path", type=Path)
    queue_review_parser.add_argument("--item-id", required=True)
    queue_review_parser.add_argument("--action", choices=["approve", "reject", "modify"], required=True)
    queue_review_parser.add_argument("--pm-note")

    render_parser = subparsers.add_parser("render")
    render_subparsers = render_parser.add_subparsers(dest="render_command", required=True)
    render_doc_parser = render_subparsers.add_parser("doc")
    render_doc_parser.add_argument("--doc-key", choices=["prd", "problem-brief", "strategy-brief", "user-journey"], required=True)
    render_doc_parser.add_argument("--output-path", type=Path)
    render_docs_parser = render_subparsers.add_parser("docs")

    render_journey_parser = render_subparsers.add_parser("journey-map")
    render_journey_parser.add_argument("--workspace-dir", type=Path, required=True)

    render_screen_flow_parser = render_subparsers.add_parser("screen-flow")
    render_screen_flow_parser.add_argument("--workspace-dir", type=Path, required=True)

    render_prototype_parser = render_subparsers.add_parser("prototype")
    render_prototype_parser.add_argument("--workspace-dir", type=Path, required=True)

    render_takeover_atlas_parser = render_subparsers.add_parser("takeover-atlas")
    render_takeover_atlas_parser.add_argument("--workspace-dir", type=Path, required=True)
    render_takeover_atlas_parser.add_argument("--output-path", type=Path)

    review_parser = subparsers.add_parser("review-delta")
    review_parser.add_argument("--update-id", required=True)
    review_parser.add_argument("--action", choices=["approve", "reject", "modify"], required=True)
    review_parser.add_argument("--pm-note")

    return parser.parse_args()


def _dispatch_command(args: argparse.Namespace) -> int:
    """Dispatch to the concrete command handler."""
    if args.command == "status":
        return cmd_status(args)
    if args.command == "ingest":
        return cmd_ingest(args)
    if args.command == "run":
        return cmd_run(args)
    if args.command == "review":
        return cmd_review(args)
    if args.command == "agent-context":
        return cmd_agent_context(args)
    if args.command == "demo":
        return cmd_demo(args)
    if args.command == "export":
        return cmd_export(args)
    if args.command == "visual":
        if args.visual_command == "plan" and args.visual_surface == "deck":
            return cmd_visual_plan_deck(args)
        if args.visual_command == "plan" and args.visual_surface == "corridor":
            return cmd_visual_plan_corridor(args)
        if args.visual_command == "plan" and args.visual_surface == "map":
            return cmd_visual_plan_map(args)
        if args.visual_command == "build":
            return cmd_visual_build(args)
        if args.visual_command == "review":
            return cmd_visual_review(args)
        if args.visual_command == "export" and args.visual_surface == "deck":
            return cmd_visual_export_deck(args)
        if args.visual_command == "export" and args.visual_surface == "corridor":
            return cmd_visual_export_corridor(args)
        if args.visual_command == "export" and args.visual_surface == "map":
            return cmd_visual_export_map(args)
        raise AssertionError(f"Unsupported visual command: {args.visual_command}/{args.visual_surface}")
    if args.command == "trace":
        return cmd_trace(args)
    if args.command == "start":
        return cmd_start(args)
    if args.command == "phase":
        if args.phase_command == "plan":
            return cmd_phase_plan(args)
    if args.command == "cockpit":
        if args.cockpit_command == "build":
            return cmd_cockpit_build(args)
    if args.command == "portfolio":
        if args.portfolio_command == "build":
            return cmd_portfolio_build(args)
    if args.command == "init-workspace":
        return cmd_init_workspace(args)
    if args.command == "init-mission":
        return cmd_init_mission(args)
    if args.command == "doctor":
        return cmd_doctor(args)
    if args.command == "validate-workspace":
        return cmd_validate_workspace(args)
    if args.command in {"import", "adopt-workspace"}:
        return cmd_adopt_workspace(args)
    if args.command == "takeover":
        return cmd_takeover(args)
    if args.command == "thread-review":
        return cmd_thread_review(args)
    if args.command == "thread-review-index":
        return cmd_thread_review_index(args)
    if args.command == "thread-review-release-check":
        return cmd_thread_review_release_check(args)
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
    if args.command == "v9":
        return cmd_v9(args)
    if args.command == "cutover":
        return cmd_cutover(args)
    if args.command == "release":
        return cmd_release(args)
    if args.command == "queue":
        if args.queue_command == "build":
            return cmd_queue_build(args)
        if args.queue_command == "review":
            return cmd_queue_review(args)
    if args.command == "render":
        if args.render_command == "doc":
            return cmd_render_doc(args)
        if args.render_command == "docs":
            return cmd_render_docs(args)
        if args.render_command == "journey-map":
            return cmd_render_journey_map(args)
        if args.render_command == "screen-flow":
            return cmd_render_screen_flow(args)
        if args.render_command == "prototype":
            return cmd_render_prototype(args)
        if args.render_command == "takeover-atlas":
            return cmd_render_takeover_atlas(args)
    if args.command == "review-delta":
        return cmd_review_delta(args)
    if args.command == "new":
        return cmd_new(args)
    raise AssertionError(f"Unsupported command: {args.command}")


def main() -> int:
    args = parse_args()
    if args.output_format == "json":
        import io
        import sys
        old_stdout = sys.stdout
        sys.stdout = captured = io.StringIO()
        try:
            code = _dispatch_command(args)
        except SystemExit as exc:
            code = exc.code if isinstance(exc.code, int) else 1
        except Exception as exc:
            sys.stdout = old_stdout
            result = {
                "status": "error",
                "code": type(exc).__name__,
                "message": str(exc),
            }
            print(json.dumps(result, indent=2))
            return 1
        sys.stdout = old_stdout
        output = captured.getvalue()
        result = {
            "status": "ok" if code == 0 else "error",
            "returncode": code,
            "stdout": output,
        }
        print(json.dumps(result, indent=2))
        return code
    return _dispatch_command(args)


if __name__ == "__main__":
    raise SystemExit(main())
