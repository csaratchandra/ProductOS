from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

from .release import latest_release_metadata
from typing import Any

from components.presentation.python.productos_presentation import (
    build_evidence_pack,
    build_ppt_export_plan,
    build_presentation_story,
    build_publish_check,
    build_render_spec,
    build_slide_spec,
)
from .governed_docs import default_modification_log
from .mission import build_discover_artifacts_from_mission


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _date_from_timestamp(timestamp: str) -> datetime:
    return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")


def build_v4_foundation_bundle_from_workspace(
    workspace_dir: Path | str,
    *,
    generated_at: str,
) -> dict[str, dict[str, Any]]:
    workspace_path = Path(workspace_dir).resolve()
    artifacts_dir = workspace_path / "artifacts"
    docs_dir = workspace_path / "docs"
    workspace_name = workspace_path.name

    mission_brief_path = artifacts_dir / "mission_brief.json"
    mission_brief = _load_json(mission_brief_path) if mission_brief_path.exists() else None
    problem_brief_path = artifacts_dir / "problem_brief.json"
    concept_brief_path = artifacts_dir / "concept_brief.json"
    prd_path = artifacts_dir / "prd.json"
    if problem_brief_path.exists() and concept_brief_path.exists() and prd_path.exists():
        problem_brief = _load_json(problem_brief_path)
        concept_brief = _load_json(concept_brief_path)
        prd = _load_json(prd_path)
    elif mission_brief is not None:
        problem_brief, concept_brief, prd = build_discover_artifacts_from_mission(
            workspace_id=mission_brief["workspace_id"],
            generated_at=generated_at,
            mission_brief=mission_brief,
        )
    else:
        problem_brief = _load_json(problem_brief_path)
        concept_brief = _load_json(concept_brief_path)
        prd = _load_json(prd_path)
    prototype_record = _load_json(artifacts_dir / "prototype_record.json")
    increment_plan = _load_json(artifacts_dir / "increment_plan.json")
    release_readiness = _load_json(artifacts_dir / "release_readiness.example.json")
    release_gate_decision = _load_json(artifacts_dir / "release_gate_decision.example.json")
    runtime_adapter_registry = _load_json(artifacts_dir / "runtime_adapter_registry.example.json")
    execution_session_state = _load_json(artifacts_dir / "execution_session_state.example.json")
    productos_feedback_log = _load_json(artifacts_dir / "productos_feedback_log.example.json")
    presentation_brief = _load_json(artifacts_dir / "presentation_brief.example.json")
    presentation_sample_record = _load_json(artifacts_dir / "presentation_sample_record.example.json")
    presentation_pattern_review = _load_json(artifacts_dir / "presentation_pattern_review.example.json")
    feedback_cluster_state = _load_json(artifacts_dir / "feedback_cluster_state.example.json")
    gap_cluster_state = _load_json(artifacts_dir / "gap_cluster_state.example.json")
    improvement_loop_state = _load_json(artifacts_dir / "improvement_loop_state.example.json")
    pm_benchmark = _load_json(artifacts_dir / "pm_benchmark.example.json")
    superpower_benchmark = _load_json(artifacts_dir / "superpower_benchmark.example.json")

    generated_dt = _date_from_timestamp(generated_at)
    review_dt = generated_dt + timedelta(days=28)
    workspace_id = problem_brief["workspace_id"]

    pm_superpower_benchmark = {
        "schema_version": "1.0.0",
        "pm_superpower_benchmark_id": f"pm_superpower_benchmark_{workspace_id}_v4_0",
        "workspace_id": workspace_id,
        "baseline_version": "3.1.0",
        "candidate_version": "4.0.0",
        "status": "defined",
        "comparison_window": {
            "baseline_cutoff_date": generated_dt.date().isoformat(),
            "target_review_date": review_dt.date().isoformat(),
        },
        "validation_tier": "tier_2",
        "baseline_benchmark_refs": [
            pm_benchmark["pm_benchmark_id"],
            superpower_benchmark["superpower_benchmark_id"],
        ],
        "golden_loop_scores": [
            {
                "loop_id": "signal_to_product_decision",
                "name": "Signal to product decision",
                "benchmark_question": "Does V4 reduce the PM work required to reach a decision-ready package from noisy evidence?",
                "status": "baseline_defined",
                "primary_metrics": [
                    {
                        "metric_name": "time_to_decision_ready_package_hours",
                        "baseline_value": 18,
                        "target_value": 6,
                        "unit": "hours",
                        "target_comparison": "lte",
                        "rationale": "Readable decision packages should remove manual reconstruction across problem, concept, and PRD work.",
                    },
                    {
                        "metric_name": "rewrite_rounds_before_pm_acceptance",
                        "baseline_value": 3,
                        "target_value": 1,
                        "unit": "rounds",
                        "target_comparison": "lte",
                        "rationale": "Approved source artifacts should translate into decision-ready docs with minimal rewrite.",
                    },
                ],
                "success_thresholds": [
                    "At least one end-to-end problem-to-PRD package reaches PM review in the same working day.",
                    "The PM should not need more than one material rewrite before approving the package for downstream use.",
                ],
                "evidence_refs": [
                    problem_brief["problem_brief_id"],
                    concept_brief["concept_brief_id"],
                    prd["prd_id"],
                ],
                "current_pain_points": [
                    "Key PM reasoning still has to be manually reconstructed across structured artifacts.",
                    "The transition from evidence to PRD-ready framing is still slower than the target operating rhythm.",
                ],
            },
            {
                "loop_id": "decision_to_stakeholder_alignment",
                "name": "Decision to stakeholder alignment",
                "benchmark_question": "Does V4 turn approved product direction into reviewable communication fast enough for real stakeholder alignment?",
                "status": "baseline_defined",
                "primary_metrics": [
                    {
                        "metric_name": "time_to_first_reviewable_doc_hours",
                        "baseline_value": 12,
                        "target_value": 3,
                        "unit": "hours",
                        "target_comparison": "lte",
                        "rationale": "Readable docs should be generated quickly from approved artifacts once the direction is stable.",
                    },
                    {
                        "metric_name": "stakeholder_alignment_cycles_before_acceptance",
                        "baseline_value": 4,
                        "target_value": 2,
                        "unit": "cycles",
                        "target_comparison": "lte",
                        "rationale": "Better narrative packaging should reduce the number of clarification loops required for alignment.",
                    },
                ],
                "success_thresholds": [
                    "A PM-facing readable document should be available within the same business day after artifact approval.",
                    "Stakeholder review should usually converge within two cycles when the source artifacts are approved.",
                ],
                "evidence_refs": [
                    prd["prd_id"],
                    increment_plan["increment_plan_id"],
                    release_readiness["release_readiness_id"],
                ],
                "current_pain_points": [
                    "Stakeholder-safe communication still depends on manual narrative rebuilding.",
                    "Release and roadmap context are not yet packaged into one governed communication path.",
                ],
            },
            {
                "loop_id": "feedback_to_accepted_improvement",
                "name": "Feedback to accepted improvement",
                "benchmark_question": "Does V4 convert repeated feedback into a bounded improvement decision without waiting for a manual planning reset?",
                "status": "baseline_defined",
                "primary_metrics": [
                    {
                        "metric_name": "time_from_clustered_feedback_to_pm_ready_improvement_days",
                        "baseline_value": 21,
                        "target_value": 7,
                        "unit": "days",
                        "target_comparison": "lte",
                        "rationale": "The improvement loop should turn repeated pain into a decision-ready bounded slice in under one week.",
                    },
                    {
                        "metric_name": "repeated_unresolved_pain_items_per_cycle",
                        "baseline_value": 2,
                        "target_value": 0,
                        "unit": "items",
                        "target_comparison": "lte",
                        "rationale": "Once a repeated pain point is accepted into the loop, it should not keep resurfacing unchanged.",
                    },
                ],
                "success_thresholds": [
                    "Repeated high-impact feedback should produce a PM-ready bounded improvement proposal inside one weekly planning cycle.",
                    "Accepted fixes should reduce the recurrence of the same unresolved pain in the next observed cycle.",
                ],
                "evidence_refs": [
                    feedback_cluster_state["feedback_cluster_state_id"],
                    gap_cluster_state["gap_cluster_state_id"],
                    improvement_loop_state["improvement_loop_state_id"],
                ],
                "current_pain_points": [
                    "Feedback-to-fix loops still depend on manual release planning translation.",
                    "Repeated communication pain can be identified, but not yet closed through a governed V4 loop.",
                ],
            },
        ],
        "overall_summary": "The first V4.0 slice locks the PM superpower scoreboard before broader document-system implementation continues.",
        "recommended_next_action": "Use this benchmark as the acceptance bar for the next V4.0 document-system and validation-tier slices.",
        "generated_at": generated_at,
    }

    persona_operating_profile = {
        "schema_version": "1.0.0",
        "persona_operating_profile_id": f"persona_operating_profile_{workspace_id}_v4_0",
        "workspace_id": workspace_id,
        "status": "defined",
        "profile_scope": "v4_0_foundation",
        "validation_tier": "tier_2",
        "benchmark_ref": pm_superpower_benchmark["pm_superpower_benchmark_id"],
        "governance_refs": [
            "core/docs/v4-execution-plan.md",
            "core/docs/v4-artifact-workflow-matrix.md",
            "core/docs/ai-agent-persona-operating-model.md",
        ],
        "review_policy_summary": "AI personas may route, draft, critique, test, retrieve, and package within explicit boundaries, but PM personas remain the human approval owners for decision-driving and stakeholder-facing outputs.",
        "profiles": [
            {
                "persona_key": "ai_orchestrator",
                "display_name": "AI Orchestrator",
                "persona_class": "ai",
                "purpose": "Route work across specialist loops so ProductOS behaves like a governed operating system rather than a pile of disconnected agents.",
                "allowed_inputs": [
                    "PM request framing from cockpit",
                    "orchestration_state and execution_session_state",
                    "memory retrieval and runtime adapter context",
                ],
                "required_outputs": [
                    "orchestration_state updates",
                    "specialist routing decisions",
                    "escalation recommendations",
                ],
                "authority_boundaries": [
                    "May route and sequence specialist work.",
                    "May not approve Tier 2 or Tier 3 outputs.",
                    "May not bypass required validation or PM gates.",
                ],
                "approval_authority": [
                    "No final approval authority beyond proposing route changes."
                ],
                "handoff_protocol": [
                    "Hands off work with explicit objective, source refs, and exit condition.",
                    "Returns blocked or contradictory states to PM-visible queues.",
                ],
                "escalation_rules": [
                    "Escalate when multiple specialist paths would create conflicting outputs.",
                    "Escalate when policy, reliability, or validation gates block the next step.",
                ],
                "memory_scope": [
                    "Active orchestration state",
                    "bounded execution session context",
                    "retrieval summaries required for route selection",
                ],
                "benchmark_measures": [
                    "time_to_route_bounded_slice_minutes",
                    "duplicate_route_prevention_rate",
                ],
                "failure_modes": [
                    "Conflicting downstream workstreams",
                    "silent workflow hops",
                    "unsafe continuation past blocked state",
                ],
                "review_path": [
                    "AI Reviewer for major route rationale changes.",
                    "AI Tester for orchestration-state schema and regression checks.",
                    "PM Builder or PM Operator when route changes scope or commitment.",
                ],
                "skill_refs": [
                    "core/skills/retrieval_selection/SKILL.md",
                    "core/skills/decision_packet_synthesis/SKILL.md",
                ],
                "source_refs": [
                    "core/agents/orchestrator/CONTRACT.md",
                    "core/docs/v4-execution-plan.md",
                ],
            },
            {
                "persona_key": "ai_discoverer",
                "display_name": "AI Discoverer",
                "persona_class": "ai",
                "purpose": "Capture and route meaningful new signals without letting noise overwhelm the active PM workflow.",
                "allowed_inputs": [
                    "feedback logs, issue logs, meeting inputs, and workspace changes",
                    "change_event and signal-hypothesis context",
                ],
                "required_outputs": [
                    "change_event candidates",
                    "ranked signal summaries",
                    "trigger recommendations for downstream workflows",
                ],
                "authority_boundaries": [
                    "May classify and rank signals.",
                    "May not convert a signal into product commitment without downstream review.",
                    "May not interrupt active execution with low-signal churn.",
                ],
                "approval_authority": [
                    "No approval authority; recommend only."
                ],
                "handoff_protocol": [
                    "Hands high-signal items to research, product shaping, or operator lanes with explainable basis.",
                    "Suppresses low-signal churn until recurrence or impact increases.",
                ],
                "escalation_rules": [
                    "Escalate when contradictions affect customer-facing or release-driving outputs.",
                    "Escalate when strong signals broaden beyond one workflow.",
                ],
                "memory_scope": [
                    "Recent signal history",
                    "change-event log",
                    "weak-signal clusters awaiting stronger evidence",
                ],
                "benchmark_measures": [
                    "time_from_raw_signal_to_routed_state",
                    "signal_noise_suppression_rate",
                ],
                "failure_modes": [
                    "Alert spam",
                    "duplicate signal routing",
                    "missed high-impact change",
                ],
                "review_path": [
                    "AI Reviewer for signal framing quality on major routed items.",
                    "AI Tester for change-event and routing-state checks.",
                    "PM Operator when a signal changes release or communication significance.",
                ],
                "skill_refs": [
                    "core/skills/source_discovery/SKILL.md",
                    "core/skills/source_ranking/SKILL.md",
                    "core/skills/freshness_scoring/SKILL.md",
                ],
                "source_refs": [
                    "core/agents/radar/CONTRACT.md",
                    "core/docs/ai-agent-persona-operating-model.md",
                ],
            },
            {
                "persona_key": "ai_researcher",
                "display_name": "AI Researcher",
                "persona_class": "ai",
                "purpose": "Turn vague questions and noisy evidence into credible research framing without pretending weak evidence is decision-grade.",
                "allowed_inputs": [
                    "PM research question",
                    "idea, concept, segment, and persona context",
                    "source artifacts and external research inputs",
                ],
                "required_outputs": [
                    "research_brief",
                    "research findings",
                    "advance, prototype, or gather-more-evidence recommendation",
                ],
                "authority_boundaries": [
                    "May synthesize and interpret evidence.",
                    "May not validate a solution decision on weak evidence.",
                    "May not hide contradictory findings.",
                ],
                "approval_authority": [
                    "No final approval authority; evidence and implications only."
                ],
                "handoff_protocol": [
                    "Hands validated research framing to problem or concept workflows.",
                    "Routes weak-evidence states back for more research instead of forced progression.",
                ],
                "escalation_rules": [
                    "Escalate when evidence is too weak for the requested decision.",
                    "Escalate when contradictions materially change problem framing.",
                ],
                "memory_scope": [
                    "research briefs",
                    "segment and persona context",
                    "relevant prior evidence summaries",
                ],
                "benchmark_measures": [
                    "context_retrieval_precision",
                    "reviewer_rejection_rate_for_weak_evidence",
                ],
                "failure_modes": [
                    "Premature solution commitment",
                    "hidden contradictions",
                    "descriptive summary without strategic implication",
                ],
                "review_path": [
                    "AI Reviewer for evidence-versus-inference discipline.",
                    "AI Tester for research artifact completeness and traceability.",
                    "PM Builder when research is used to justify a decision-driving change.",
                ],
                "skill_refs": [
                    "core/skills/source_discovery/SKILL.md",
                    "core/skills/source_normalization/SKILL.md",
                    "core/skills/evidence_extraction/SKILL.md",
                    "core/skills/contradiction_detection/SKILL.md",
                ],
                "source_refs": [
                    "core/agents/research/CONTRACT.md",
                    "core/workflows/research/research-command-center-workflow.md",
                ],
            },
            {
                "persona_key": "ai_product_shaper",
                "display_name": "AI Product Shaper",
                "persona_class": "ai",
                "purpose": "Translate validated problem framing into ideas, concepts, prototypes, and PRD-ready structure without expanding scope invisibly.",
                "allowed_inputs": [
                    "problem_brief and research_brief",
                    "prototype evidence where relevant",
                    "linked entities and upstream artifacts",
                ],
                "required_outputs": [
                    "idea, concept, or PRD-ready structure",
                    "scope notes",
                    "unresolved questions",
                ],
                "authority_boundaries": [
                    "May draft and revise product-shaping artifacts.",
                    "May not commit customer-facing scope without PM approval.",
                    "May not hide unresolved questions behind polished structure.",
                ],
                "approval_authority": [
                    "No final approval authority; recommend and draft only."
                ],
                "handoff_protocol": [
                    "Hands decision-ready packages to PM Builder with explicit upstream traceability.",
                    "Routes unresolved evidence gaps back to research or prototype validation.",
                ],
                "escalation_rules": [
                    "Escalate when the problem is not strong enough for PRD commitment.",
                    "Escalate when prototype or research evidence conflicts with requested scope.",
                ],
                "memory_scope": [
                    "problem and concept history",
                    "PRD scope boundaries",
                    "open product questions",
                ],
                "benchmark_measures": [
                    "time_to_first_reviewable_prd",
                    "rewrite_rounds_before_pm_acceptance",
                ],
                "failure_modes": [
                    "Hidden scope expansion",
                    "requirements without validated problem context",
                    "dropped upstream evidence",
                ],
                "review_path": [
                    "AI Reviewer for framing, alternatives, and traceability.",
                    "AI Tester for schema and cross-artifact checks.",
                    "PM Builder for final product-shaping approval.",
                ],
                "skill_refs": [
                    "core/skills/strategy_refresh/SKILL.md",
                    "core/skills/decision_packet_synthesis/SKILL.md",
                    "core/skills/evidence_extraction/SKILL.md",
                ],
                "source_refs": [
                    "core/agents/prd/CONTRACT.md",
                    "core/workflows/discovery/idea-to-concept-workflow.md",
                ],
            },
            {
                "persona_key": "ai_reviewer",
                "display_name": "AI Reviewer",
                "persona_class": "ai",
                "purpose": "Challenge logic, assumptions, traceability, and audience fit before weak work becomes a PM or stakeholder commitment.",
                "allowed_inputs": [
                    "candidate artifacts or recommendations",
                    "upstream evidence and trace links",
                    "workflow and risk context",
                ],
                "required_outputs": [
                    "findings",
                    "revise or proceed recommendation",
                    "explicit unresolved questions",
                ],
                "authority_boundaries": [
                    "May block or challenge weak logic through findings.",
                    "May not invent unsupported counterclaims.",
                    "May not silently replace PM value judgment.",
                ],
                "approval_authority": [
                    "May recommend proceed or revise, but not final approval."
                ],
                "handoff_protocol": [
                    "Returns findings to the producing lane with concrete weaknesses.",
                    "Routes unresolved value judgment conflicts to referee or PM gate.",
                ],
                "escalation_rules": [
                    "Escalate when a candidate overstates certainty.",
                    "Escalate when hidden tradeoffs or missing alternatives would affect the decision.",
                ],
                "memory_scope": [
                    "current artifact under review",
                    "traceability links",
                    "relevant prior decisions",
                ],
                "benchmark_measures": [
                    "reviewer_rejection_precision",
                    "weak_artifact_catch_rate_before_pm_review",
                ],
                "failure_modes": [
                    "Style critique without substance",
                    "invented counterclaims",
                    "blocking without actionable explanation",
                ],
                "review_path": [
                    "AI Tester checks reviewer outputs where structured reports are generated.",
                    "Referee resolves lane disagreement.",
                    "PM gate decides unresolved value tradeoffs.",
                ],
                "skill_refs": [
                    "core/skills/contradiction_detection/SKILL.md",
                    "core/skills/evidence_extraction/SKILL.md",
                    "core/skills/retrieval_selection/SKILL.md",
                ],
                "source_refs": [
                    "core/agents/critic/CONTRACT.md",
                    "core/docs/v4-execution-plan.md",
                ],
            },
            {
                "persona_key": "ai_tester",
                "display_name": "AI Tester",
                "persona_class": "ai",
                "purpose": "Validate structure, traceability, regressions, and benchmark movement so ProductOS does not confuse artifact existence with readiness.",
                "allowed_inputs": [
                    "candidate artifacts and workflow outputs",
                    "schema, fixture, and regression context",
                    "benchmark definitions",
                ],
                "required_outputs": [
                    "validation findings",
                    "pass or revise recommendation",
                    "missing-information prompts",
                ],
                "authority_boundaries": [
                    "May block structurally unsafe outputs.",
                    "May not rewrite source truth.",
                    "May not approve adoption without the required manual or PM lane.",
                ],
                "approval_authority": [
                    "May approve test lane passage only, not downstream adoption."
                ],
                "handoff_protocol": [
                    "Returns blocking defects to the producing lane with exact missing evidence or fields.",
                    "Routes cross-lane disagreement to referee when review and test conclusions conflict.",
                ],
                "escalation_rules": [
                    "Escalate when customer-facing or high-stakes outputs fail validation.",
                    "Escalate when important claims cannot be traced or benchmark checks regress.",
                ],
                "memory_scope": [
                    "schema catalog",
                    "fixture and regression history",
                    "benchmark expectations",
                ],
                "benchmark_measures": [
                    "schema_pass_rate",
                    "regression_catch_rate",
                ],
                "failure_modes": [
                    "False pass on broken traceability",
                    "non-actionable blocking feedback",
                    "structural approval of strategically weak output",
                ],
                "review_path": [
                    "AI Reviewer checks logic where test findings imply strategic impact.",
                    "Referee resolves disagreement with reviewer or manual validation.",
                    "PM gate required for adoption beyond lane pass.",
                ],
                "skill_refs": [
                    "core/skills/freshness_scoring/SKILL.md",
                    "core/skills/contradiction_detection/SKILL.md",
                    "core/skills/retrieval_selection/SKILL.md",
                ],
                "source_refs": [
                    "core/agents/validation/CONTRACT.md",
                    "core/docs/testing-strategy.md",
                ],
            },
            {
                "persona_key": "ai_librarian",
                "display_name": "AI Librarian",
                "persona_class": "ai",
                "purpose": "Maintain retrievability, provenance, and duplicate-work prevention so downstream loops start from the right context.",
                "allowed_inputs": [
                    "retrieval requests from PM or agents",
                    "workspace manifest and registry context",
                    "artifact paths and trace maps",
                ],
                "required_outputs": [
                    "artifact retrieval bundle",
                    "canonical source references",
                    "deduplication and traceability recommendations",
                ],
                "authority_boundaries": [
                    "May identify canonical sources and stale context.",
                    "May not silently substitute one source for another.",
                    "May not override approved state.",
                ],
                "approval_authority": [
                    "No approval authority; retrieval and provenance only."
                ],
                "handoff_protocol": [
                    "Supplies canonical context before downstream work starts.",
                    "Returns stale or conflicting source states to orchestrator or PM review.",
                ],
                "escalation_rules": [
                    "Escalate when current approved state cannot be traced cleanly.",
                    "Escalate when multiple candidate artifacts conflict on canonical status.",
                ],
                "memory_scope": [
                    "artifact registry and trace maps",
                    "current canonical references",
                    "stale or conflicting context warnings",
                ],
                "benchmark_measures": [
                    "time_to_find_relevant_prior_context",
                    "duplicate_artifact_prevention_rate",
                ],
                "failure_modes": [
                    "Stale source substitution",
                    "duplicate artifact creation",
                    "hidden traceability gaps",
                ],
                "review_path": [
                    "AI Tester checks retrieval bundles and traceability outputs where structured.",
                    "AI Reviewer checks high-impact canonical-source recommendations.",
                    "PM Operator resolves disputed current-state references.",
                ],
                "skill_refs": [
                    "core/skills/retrieval_selection/SKILL.md",
                    "core/skills/source_normalization/SKILL.md",
                ],
                "source_refs": [
                    "core/agents/librarian/CONTRACT.md",
                    "core/docs/continuous-intake-and-memory-model.md",
                ],
            },
            {
                "persona_key": "ai_presenter",
                "display_name": "AI Presenter",
                "persona_class": "ai",
                "purpose": "Turn approved artifacts into readable narratives and presentations without making the deck the source of product truth.",
                "allowed_inputs": [
                    "presentation_brief and source artifacts",
                    "status, leadership, and portfolio communication context",
                    "approved evidence pack inputs",
                ],
                "required_outputs": [
                    "evidence_pack and presentation_story",
                    "render_spec or presentation export plan",
                    "communication-safe narrative packaging",
                ],
                "authority_boundaries": [
                    "May package and compress approved facts for audience fit.",
                    "May not hide material risk or overstate certainty.",
                    "May not replace source-of-truth artifacts.",
                ],
                "approval_authority": [
                    "No final approval authority; packaging only."
                ],
                "handoff_protocol": [
                    "Hands packaged narrative to PM Leader or PM Operator for manual review where required.",
                    "Returns risky compression or audience-fit conflicts for revision.",
                ],
                "escalation_rules": [
                    "Escalate when executive compression would hide a required blocker, dependency, or decision.",
                    "Escalate when a requested layout or narrative would distort source truth.",
                ],
                "memory_scope": [
                    "approved source artifacts",
                    "presentation patterns and evidence packs",
                    "audience-specific narrative constraints",
                ],
                "benchmark_measures": [
                    "time_to_executive_briefing",
                    "presentation_review_score",
                ],
                "failure_modes": [
                    "Presentation as source-of-truth",
                    "audience-safe distortion of facts",
                    "traceability loss in narrative compression",
                ],
                "review_path": [
                    "AI Reviewer checks audience fit and certainty discipline.",
                    "AI Tester checks traceability and presentation regression fixtures.",
                    "PM Leader approves strategy and executive-facing packages.",
                ],
                "skill_refs": [
                    "core/skills/decision_packet_synthesis/SKILL.md",
                    "core/skills/publish_safe_summarization/SKILL.md",
                ],
                "source_refs": [
                    "components/presentation/contracts/presentation/CONTRACT.md",
                    "core/agents/status-communications/CONTRACT.md",
                ],
            },
            {
                "persona_key": "pm_builder",
                "display_name": "PM Builder",
                "persona_class": "pm",
                "purpose": "Use ProductOS to turn evidence into shaped product decisions, validated concepts, and ship-ready plans.",
                "allowed_inputs": [
                    "research, problem, concept, prototype, and PRD artifacts",
                    "review and test lane findings",
                ],
                "required_outputs": [
                    "approval or revision decisions on product-shaping artifacts",
                    "bounded product direction and scope commitments",
                ],
                "authority_boundaries": [
                    "Owns product-shaping approval for decision-driving artifacts.",
                    "Should not silently waive reliability, compliance, or manual validation gates owned elsewhere.",
                    "Should not accept scope that lacks evidence or explicit tradeoffs.",
                ],
                "approval_authority": [
                    "May approve problem, concept, prototype, and PRD packages after required lanes pass."
                ],
                "handoff_protocol": [
                    "Hands approved direction to delivery, operator, or leadership packaging paths.",
                    "Routes evidence or usability gaps back to research, prototype, or product-shaping lanes.",
                ],
                "escalation_rules": [
                    "Escalate when product value judgment conflicts with reviewer or tester findings.",
                    "Escalate when approval would imply a release or stakeholder promise beyond current evidence.",
                ],
                "memory_scope": [
                    "decision history",
                    "product framing artifacts",
                    "open product tradeoffs",
                ],
                "benchmark_measures": [
                    "time_to_decision_ready_problem_framing",
                    "rewrite_rate_before_pm_acceptance",
                ],
                "failure_modes": [
                    "Approval of polished but weak framing",
                    "hidden tradeoff acceptance",
                    "scope commitment without evidence",
                ],
                "review_path": [
                    "Uses AI Reviewer and AI Tester for Tier 2 decision artifacts.",
                    "Routes unresolved conflicts to referee or PM Leader when commitment broadens.",
                ],
                "skill_refs": [
                    "core/skills/strategy_refresh/SKILL.md",
                    "core/skills/decision_packet_synthesis/SKILL.md",
                ],
                "source_refs": [
                    "core/docs/v4-execution-plan.md",
                    "core/docs/v4-artifact-workflow-matrix.md",
                ],
            },
            {
                "persona_key": "pm_operator",
                "display_name": "PM Operator",
                "persona_class": "pm",
                "purpose": "Use ProductOS to manage status, follow-through, release readiness, and the ongoing operating cadence around shipped work.",
                "allowed_inputs": [
                    "status, queue, release, issue, and runtime artifacts",
                    "validation lane findings and readiness signals",
                ],
                "required_outputs": [
                    "status and follow-through decisions",
                    "release readiness and communication approvals",
                    "operating cadence updates",
                ],
                "authority_boundaries": [
                    "Owns operating clarity, release-readiness review, and follow-through quality.",
                    "Should not hide critical blockers in a communication-safe summary.",
                    "Should not waive mandatory Tier 3 manual validation.",
                ],
                "approval_authority": [
                    "May approve status, follow-through, and release-operating outputs after required lanes pass."
                ],
                "handoff_protocol": [
                    "Hands high-stakes communication to PM Leader when narrative stakes exceed routine operation.",
                    "Routes unresolved release risk back to delivery, reliability, or referee lanes.",
                ],
                "escalation_rules": [
                    "Escalate when release risk, support readiness, or evidence conflicts remain unresolved.",
                    "Escalate when stakeholder-safe phrasing would conflict with source truth.",
                ],
                "memory_scope": [
                    "issue and follow-up queues",
                    "release and runtime state",
                    "communication commitments already made",
                ],
                "benchmark_measures": [
                    "stakeholder_alignment_speed",
                    "blocked_release_detection_rate",
                ],
                "failure_modes": [
                    "Status theater instead of operating truth",
                    "hidden blocker in summary language",
                    "release decision without explicit ownership",
                ],
                "review_path": [
                    "Uses AI Reviewer and AI Tester on Tier 2 and Tier 3 operating outputs.",
                    "Runs mandatory manual validation on release-driving packages.",
                ],
                "skill_refs": [
                    "core/skills/freshness_scoring/SKILL.md",
                    "core/skills/decision_packet_synthesis/SKILL.md",
                    "core/skills/publish_safe_summarization/SKILL.md",
                ],
                "source_refs": [
                    "core/workflows/launch/release-readiness-workflow.md",
                    "core/docs/v4-artifact-workflow-matrix.md",
                ],
            },
            {
                "persona_key": "pm_leader_communicator",
                "display_name": "PM Leader / Communicator",
                "persona_class": "pm",
                "purpose": "Use ProductOS to align stakeholders, defend tradeoffs, and package decisions into readable docs and presentations that change real outcomes.",
                "allowed_inputs": [
                    "approved strategy, roadmap, release, and presentation source artifacts",
                    "review and manual validation findings",
                ],
                "required_outputs": [
                    "approval on stakeholder-facing docs and presentations",
                    "narrative framing for leadership and cross-functional alignment",
                ],
                "authority_boundaries": [
                    "Owns stakeholder-facing narrative quality and final alignment quality.",
                    "Should not let audience polish override product truth.",
                    "Should not approve borrowed patterns or external exemplars without the required review path.",
                ],
                "approval_authority": [
                    "May approve leadership-facing docs, strategy narratives, and executive presentations after required tri-gate review."
                ],
                "handoff_protocol": [
                    "Hands final aligned narrative into meeting, release, or portfolio review contexts.",
                    "Routes weak narrative logic or missing proof back to PM Builder, PM Operator, or AI Presenter.",
                ],
                "escalation_rules": [
                    "Escalate when material commitment would change because of narrative packaging choices.",
                    "Escalate when presentation quality depends on an unreviewed external pattern.",
                ],
                "memory_scope": [
                    "leadership narrative history",
                    "decision rationale and tradeoff memory",
                    "presentation review outcomes",
                ],
                "benchmark_measures": [
                    "time_to_executive_or_cross_functional_briefing",
                    "quality_of_narrative_score",
                ],
                "failure_modes": [
                    "Narrative polish masking unresolved risk",
                    "presentation drift from source artifacts",
                    "alignment claim without real adoption",
                ],
                "review_path": [
                    "Uses AI Reviewer and AI Tester for stakeholder-facing drafts.",
                    "Requires targeted or mandatory manual validation for Tier 2 and Tier 3 communication outputs.",
                ],
                "skill_refs": [
                    "core/skills/strategy_refresh/SKILL.md",
                    "core/skills/decision_packet_synthesis/SKILL.md",
                    "core/skills/publish_safe_summarization/SKILL.md",
                ],
                "source_refs": [
                    "core/docs/v4-execution-plan.md",
                    "components/presentation/docs/presentation-system.md",
                ],
            },
        ],
        "generated_at": generated_at,
    }

    validation_lane_report = {
        "schema_version": "1.0.0",
        "validation_lane_report_id": f"validation_lane_report_{workspace_id}_persona_profile_v4_0",
        "workspace_id": workspace_id,
        "artifact_ref": persona_operating_profile["persona_operating_profile_id"],
        "artifact_type": "persona_operating_profile",
        "stage_name": "v4_0_foundation_governance_definition",
        "validation_tier": "tier_2",
        "overall_status": "ready_for_manual_validation",
        "review_summary": "AI review and AI test checks say the persona operating profile is structurally sound and governance-ready, but Tier 2 adoption still requires targeted PM manual validation.",
        "ai_reviewer_lane": {
            "status": "proceed",
            "reviewer_role": "AI Reviewer",
            "blocking_findings": [],
            "non_blocking_findings": [
                "Authority boundaries are explicit enough to prevent silent scope, publish, or release approval by AI personas."
            ],
            "unresolved_questions": [
                "Which PM persona should own sampled manual validation when an artifact spans builder and operator concerns?"
            ],
        },
        "ai_tester_lane": {
            "status": "passed",
            "tester_role": "AI Tester",
            "checks_run": [
                "schema validation",
                "bundle generation",
                "cross-reference tests",
            ],
            "blocking_findings": [],
            "non_blocking_findings": [
                "The persona profile example and generated bundle output match exactly."
            ],
            "automation_gaps": [
                "Manual usefulness validation for real PM adoption is still outside automated coverage."
            ],
        },
        "manual_validation_policy": {
            "required": True,
            "scope": "targeted",
            "owner_role": "PM Builder",
            "status": "pending",
            "rationale": "Tier 2 governance artifacts require targeted human confirmation that approval boundaries and review paths are usable in real work.",
        },
        "referee_trigger": {
            "required": False,
            "rationale": "AI Reviewer and AI Tester agree on proceed versus revise, so there is no lane disagreement to resolve.",
            "conflicting_lanes": [],
        },
        "governance_layer_refs": [
            "core/docs/validation-tier-policy.md",
            "core/docs/v4-execution-plan.md",
            "core/docs/governance-review-model.md",
        ],
        "next_action": "Run targeted PM manual validation on the persona operating profile before adopting it as the default Tier 2 governance control.",
        "generated_at": generated_at,
    }

    doc_specs = [
        {
            "doc_key": "discovery_summary",
            "title": "Discovery Summary",
            "relative_path": Path("discovery/discovery-summary.md"),
            "source_artifact_refs": [
                productos_feedback_log["feedback_log_id"],
                problem_brief["problem_brief_id"],
            ],
            "audience": [
                "PM",
                "leadership",
                "design",
                "engineering",
            ],
            "status": "review_pending",
            "last_sync_status": "Readable draft exists and remains traceable to the current discovery and feedback evidence.",
        },
        {
            "doc_key": "problem_brief",
            "title": "Problem Brief",
            "relative_path": Path("discovery/problem-brief.md"),
            "source_artifact_refs": [problem_brief["problem_brief_id"]],
            "audience": [
                "PM",
                "design",
                "engineering",
                "leadership",
            ],
            "status": "synced",
            "last_sync_status": "Problem framing and recommendation match the current structured artifact.",
        },
        {
            "doc_key": "concept_brief",
            "title": "Concept Brief",
            "relative_path": Path("strategy/concept-brief.md"),
            "source_artifact_refs": [concept_brief["concept_brief_id"]],
            "audience": [
                "PM",
                "design",
                "research",
                "leadership",
            ],
            "status": "synced",
            "last_sync_status": "Concept narrative remains aligned with the validated concept artifact.",
        },
        {
            "doc_key": "prototype_review",
            "title": "Prototype Review",
            "relative_path": Path("prototype/prototype-review.md"),
            "source_artifact_refs": [prototype_record["prototype_record_id"]],
            "audience": [
                "PM",
                "design",
                "engineering",
                "leadership",
            ],
            "status": "synced",
            "last_sync_status": "Prototype learnings and decision state reflect the current structured prototype record.",
        },
        {
            "doc_key": "roadmap",
            "title": "Product Roadmap",
            "relative_path": Path("planning/roadmap.md"),
            "source_artifact_refs": [
                increment_plan["increment_plan_id"],
                release_gate_decision["release_gate_decision_id"],
            ],
            "audience": [
                "leadership",
                "design",
                "engineering",
                "go-to-market",
            ],
            "status": "review_pending",
            "last_sync_status": "Roadmap document is current enough for targeted PM review but still needs confirmation on publishing metadata.",
        },
        {
            "doc_key": "prd",
            "title": "Product Requirements Document",
            "relative_path": Path("planning/prd.md"),
            "source_artifact_refs": [prd["prd_id"]],
            "audience": [
                "PM",
                "design",
                "engineering",
                "data or AI implementation",
            ],
            "status": "review_pending",
            "last_sync_status": "PRD narrative is grounded in the current artifact and is waiting on targeted manual validation for adoptability.",
        },
    ]
    documents: list[dict[str, Any]] = []
    missing_doc_paths: list[str] = []
    for spec in doc_specs:
        readable_path = Path("workspaces") / workspace_name / "docs" / spec["relative_path"]
        absolute_path = docs_dir / spec["relative_path"]
        doc_exists = absolute_path.exists()
        if not doc_exists:
            missing_doc_paths.append(readable_path.as_posix())
        documents.append(
            {
                "doc_key": spec["doc_key"],
                "title": spec["title"],
                "readable_path": readable_path.as_posix(),
                "source_artifact_refs": spec["source_artifact_refs"],
                "audience": spec["audience"],
                "status": spec["status"] if doc_exists else "drifted",
                "version_number": 1,
                "modification_log": default_modification_log(
                    version_number=1,
                    updated_at=generated_at,
                    updated_by="ProductOS PM",
                    summary=(
                        f"Synced governed readable doc metadata for {spec['title']}."
                        if doc_exists
                        else f"Recorded that the governed readable doc for {spec['title']} is currently missing."
                    ),
                ),
                "last_sync_status": (
                    spec["last_sync_status"]
                    if doc_exists
                    else f"Expected readable doc is missing at {readable_path.as_posix()} and must be regenerated before sync can continue."
                ),
            }
        )

    document_sync_state = {
        "schema_version": "1.1.0",
        "document_sync_state_id": f"document_sync_state_{workspace_id}_v4_readable_docs",
        "workspace_id": workspace_id,
        "sync_scope": "v4_0_readable_doc_bundle",
        "validation_tier": "tier_2",
        "status": "review_pending" if not missing_doc_paths else "blocked",
        "source_artifact_refs": [
            productos_feedback_log["feedback_log_id"],
            problem_brief["problem_brief_id"],
            concept_brief["concept_brief_id"],
            prototype_record["prototype_record_id"],
            prd["prd_id"],
            increment_plan["increment_plan_id"],
            release_gate_decision["release_gate_decision_id"],
        ],
        "documents": documents,
        "drift_summary": (
            "The current readable docs are traceable and mostly aligned, but the discovery summary, roadmap, and PRD still require targeted review before they can be treated as fully synced Tier 2 documents."
            if not missing_doc_paths
            else f"Readable-doc generation is blocked because required workspace docs are missing: {', '.join(missing_doc_paths)}."
        ),
        "review_requirements": (
            [
                "Run AI review on narrative clarity and traceability for the document bundle.",
                "Run AI test checks for required metadata and source-artifact coverage.",
                "Complete targeted PM manual validation for roadmap and PRD adoption.",
            ]
            if not missing_doc_paths
            else [
                f"Regenerate missing readable docs before any validation pass: {', '.join(missing_doc_paths)}.",
                "Re-run AI review and AI test once the missing docs exist.",
                "Do not start manual validation until the readable doc bundle is complete.",
            ]
        ),
        "next_action": (
            "Advance the readable doc bundle through validation-tier review and targeted PM validation before external publishing rules are locked."
            if not missing_doc_paths
            else "Regenerate the missing readable docs, then rerun the validation-tier review before claiming the V4 readable-doc slice is ready."
        ),
        "generated_at": generated_at,
    }

    readable_doc_validation_lane_report = {
        "schema_version": "1.0.0",
        "validation_lane_report_id": f"validation_lane_report_{workspace_id}_doc_bundle_v4_0",
        "workspace_id": workspace_id,
        "artifact_ref": document_sync_state["document_sync_state_id"],
        "artifact_type": "document_sync_state",
        "stage_name": "v4_0_readable_doc_generation_and_sync",
        "validation_tier": "tier_2",
        "overall_status": "blocked" if not missing_doc_paths else "blocked",
        "review_summary": "AI review says the readable-doc bundle is traceable and internally usable, while AI test still wants metadata hardening before broader publishing.",
        "ai_reviewer_lane": {
            "status": "proceed",
            "reviewer_role": "AI Reviewer",
            "blocking_findings": [],
            "non_blocking_findings": [
                "The readable docs preserve source linkage and cover the intended PM-facing sections."
            ],
            "unresolved_questions": [
                "Which external publishing metadata fields should be mandatory before broader sync is allowed?"
            ],
        },
        "ai_tester_lane": {
            "status": "revise",
            "tester_role": "AI Tester",
            "checks_run": [
                "schema validation",
                "document path existence check",
                "source-artifact coverage check",
            ],
            "blocking_findings": [],
            "non_blocking_findings": (
                ["All required readable-doc paths exist in the workspace docs tree."]
                if not missing_doc_paths
                else []
            ),
            "automation_gaps": [
                "External publishing metadata rules still require targeted manual confirmation."
            ],
        },
        "manual_validation_policy": {
            "required": True,
            "scope": "targeted",
            "owner_role": "PM Operator",
            "status": "pending",
            "rationale": "Tier 2 readable documents require a PM usefulness review before broader adoption.",
        },
        "referee_trigger": {
            "required": True,
            "rationale": "AI Reviewer allows internal proceed while AI Tester still requires revise for publishing-metadata hardening, so the disagreement needs an explicit tie-break.",
            "conflicting_lanes": [
                "AI Reviewer",
                "AI Tester",
            ],
        },
        "governance_layer_refs": [
            "core/docs/validation-tier-policy.md",
            "core/docs/product-document-system.md",
            "core/docs/v4-artifact-workflow-matrix.md",
        ],
        "next_action": "Run targeted PM manual validation on the roadmap and PRD docs, then use referee routing to decide whether internal adoption may proceed before external sync is enabled.",
        "generated_at": generated_at,
    }

    manual_validation_record = {
        "schema_version": "1.0.0",
        "manual_validation_record_id": f"manual_validation_record_{workspace_id}_doc_bundle_v4_0",
        "workspace_id": workspace_id,
        "subject_ref": document_sync_state["document_sync_state_id"],
        "subject_type": "readable_doc_bundle",
        "validation_tier": "tier_2",
        "validator_role": "PM Operator",
        "scope": "targeted",
        "decision": "accept",
        "fit_notes": [
            "The roadmap and PRD are readable enough to review with stakeholders without requiring raw JSON inspection.",
            "Source linkage remains visible enough for the PM to defend where each claim came from.",
        ],
        "required_follow_ups": [
            "Add publishing metadata guidance for external SharePoint and Confluence sync.",
            "Keep discovery-summary wording under review while the wider document taxonomy stabilizes.",
        ],
        "related_validation_report_ref": readable_doc_validation_lane_report["validation_lane_report_id"],
        "final_approval": True,
        "recorded_at": generated_at,
    }

    referee_decision_record = {
        "schema_version": "1.0.0",
        "referee_decision_record_id": f"referee_decision_record_{workspace_id}_doc_bundle_v4_0",
        "workspace_id": workspace_id,
        "subject_ref": document_sync_state["document_sync_state_id"],
        "subject_type": "readable_doc_bundle",
        "related_validation_report_ref": readable_doc_validation_lane_report["validation_lane_report_id"],
        "disagreement_summary": "AI review judged the roadmap and PRD narrative ready for PM use, while AI test requested a revise pass for missing external-publishing metadata guidance.",
        "lane_positions": [
            {
                "lane_name": "AI Reviewer",
                "position": "proceed",
                "rationale": "Traceability and audience fit are strong enough for internal stakeholder review.",
            },
            {
                "lane_name": "AI Tester",
                "position": "revise",
                "rationale": "The document bundle does not yet encode every publishing metadata rule needed for a broader sync target.",
            },
            {
                "lane_name": "Manual Validation",
                "position": "accept",
                "rationale": "The PM can already use the docs internally while metadata hardening continues.",
            },
        ],
        "referee_role": "Referee",
        "resolution": "proceed",
        "next_action": "Allow internal adoption of the readable-doc bundle while keeping external publishing blocked until metadata guidance is complete.",
        "unresolved_questions": [
            "Which metadata fields must be mandatory before SharePoint sync is allowed?"
        ],
        "recorded_at": generated_at,
    }

    ai_agent_benchmark = {
        "schema_version": "1.0.0",
        "ai_agent_benchmark_id": f"ai_agent_benchmark_{workspace_id}_v4_0",
        "workspace_id": workspace_id,
        "status": "defined",
        "benchmark_scope": "Measure whether the V4 persona stack and validation lanes reduce coordination and fix-loop overhead without replacing the PM benchmark.",
        "benchmark_window": {
            "baseline_cutoff_date": generated_dt.date().isoformat(),
            "target_review_date": review_dt.date().isoformat(),
        },
        "pm_guardrail_ref": pm_superpower_benchmark["pm_superpower_benchmark_id"],
        "persona_refs": [
            persona_operating_profile["persona_operating_profile_id"],
            runtime_adapter_registry["runtime_adapter_registry_id"],
            execution_session_state["execution_session_state_id"],
        ],
        "loop_efficiency_scores": [
            {
                "loop_id": "doc_generation_and_review",
                "benchmark_question": "Do the AI personas generate and review a readable document bundle with fewer handoff delays and fewer duplicate passes?",
                "primary_metrics": [
                    {
                        "metric_name": "handoff_cycles_before_review_ready",
                        "baseline_value": 5,
                        "target_value": 2,
                        "unit": "cycles",
                        "target_comparison": "lte",
                        "rationale": "Explicit persona ownership should reduce repeated route churn.",
                    },
                    {
                        "metric_name": "duplicate_fix_loops_per_bundle",
                        "baseline_value": 3,
                        "target_value": 1,
                        "unit": "loops",
                        "target_comparison": "lte",
                        "rationale": "Reviewer, tester, and manual lanes should stop the same fix from being rediscovered repeatedly.",
                    },
                ],
                "evidence_refs": [
                    persona_operating_profile["persona_operating_profile_id"],
                    validation_lane_report["validation_lane_report_id"],
                    execution_session_state["execution_session_state_id"],
                ],
                "guardrail": "Do not treat better agent throughput as success if the PM benchmark does not also improve.",
            },
            {
                "loop_id": "feedback_to_bounded_fix",
                "benchmark_question": "Do the improvement-loop personas reduce the time from repeated pain to a bounded next slice with explicit validation?",
                "primary_metrics": [
                    {
                        "metric_name": "time_from_feedback_cluster_to_next_slice_days",
                        "baseline_value": 14,
                        "target_value": 5,
                        "unit": "days",
                        "target_comparison": "lte",
                        "rationale": "The auto-improvement loop should route repeated pain faster without waiting for a planning reset.",
                    }
                ],
                "evidence_refs": [
                    feedback_cluster_state["feedback_cluster_state_id"],
                    improvement_loop_state["improvement_loop_state_id"],
                    runtime_adapter_registry["runtime_adapter_registry_id"],
                ],
                "guardrail": "Do not optimize for faster routing if the resulting slice still fails PM acceptance.",
            },
        ],
        "overall_summary": "The AI-agent benchmark defines efficiency measures for the V4 persona stack, but it remains explicitly subordinate to the PM superpower benchmark.",
        "generated_at": generated_at,
    }

    rejected_path_record = {
        "schema_version": "1.0.0",
        "rejected_path_record_id": f"rejected_path_record_{workspace_id}_json_only_docs",
        "workspace_id": workspace_id,
        "path_type": "workflow_route",
        "title": "Reject JSON-only stakeholder communication path",
        "related_refs": [
            productos_feedback_log["feedback_log_id"],
            document_sync_state["document_sync_state_id"],
            pm_superpower_benchmark["pm_superpower_benchmark_id"],
        ],
        "rejection_stage": "decision_to_stakeholder_alignment",
        "decision": "rejected",
        "rejection_reason": "Stakeholder-facing communication that depends on raw JSON inspection does not satisfy the V4 document-system objective or the PM leverage benchmark.",
        "failure_signals": [
            "Readable stakeholder review still required manual PM translation.",
            "The same communication pain reappeared in feedback after runtime gains were already proven.",
        ],
        "retry_conditions": [
            "Only revisit this path if a readable doc layer becomes unnecessary for the target audience, which is unlikely for PM communication work."
        ],
        "retained_lessons": [
            "Structured artifacts remain the system of record, but they are not sufficient as the human-facing communication surface.",
            "Anti-loop memory must record rejected workflow routes so the team does not keep relitigating them.",
        ],
        "benchmark_guardrail_refs": [
            pm_superpower_benchmark["pm_superpower_benchmark_id"],
            ai_agent_benchmark["ai_agent_benchmark_id"],
        ],
        "recorded_at": generated_at,
    }

    outcome_review = {
        "schema_version": "1.1.0",
        "outcome_review_id": f"outcome_review_{workspace_id}_v4_readable_docs",
        "workspace_id": workspace_id,
        "reviewed_change_ref": document_sync_state["document_sync_state_id"],
        "review_scope": "Review whether the first readable-doc bundle materially improved PM and stakeholder communication readiness.",
        "status": "iterate",
        "pm_benchmark_ref": pm_superpower_benchmark["pm_superpower_benchmark_id"],
        "ai_agent_benchmark_ref": ai_agent_benchmark["ai_agent_benchmark_id"],
        "evidence_refs": [
            document_sync_state["document_sync_state_id"],
            manual_validation_record["manual_validation_record_id"],
            release_gate_decision["release_gate_decision_id"],
            productos_feedback_log["feedback_log_id"],
        ],
        "target_outcomes": [
            {
                "outcome_name": "Same-day reviewable document package",
                "expected_signal": "A PM-facing readable bundle should be available on the same working day after source-artifact approval.",
                "observed_signal": "The first discovery, roadmap, and PRD docs now exist and are traceable, but external-publishing metadata is still incomplete.",
                "status": "partial",
            },
            {
                "outcome_name": "Lower stakeholder translation overhead",
                "expected_signal": "Stakeholders should not need the PM to narrate raw JSON into a reviewable document.",
                "observed_signal": "Manual validation says the new docs are internally usable, but the discovery summary and publishing rules still need another iteration.",
                "status": "partial",
            },
        ],
        "claim_verification_summary": "The readable-doc slice improved internal review readiness, but external publishing and sync claims still need tighter proof and clearer release boundaries.",
        "adoption_notes": [
            "The readable-doc bundle is good enough for internal PM and leadership review.",
            "The document-system slice should continue until publishing metadata and sync rules are fully stable.",
        ],
        "unresolved_pain_points": [
            "External SharePoint and Confluence sync rules are not yet encoded in the generated control artifacts."
        ],
        "support_signals": [
            {
                "signal_name": "Publishing adapter questions",
                "summary": "Support-style feedback still clusters around missing external publishing and sync details.",
                "direction": "stable",
                "evidence_refs": [productos_feedback_log["feedback_log_id"]],
            }
        ],
        "adoption_signals": [
            {
                "signal_name": "Readable docs adopted for internal review",
                "summary": "PM and leadership review can now happen from governed readable docs instead of raw JSON alone.",
                "direction": "improving",
                "evidence_refs": [manual_validation_record["manual_validation_record_id"]],
            }
        ],
        "reopen_recommendations": [
            {
                "artifact_id": f"prd_{workspace_id}_v4_readable_docs",
                "artifact_type": "prd",
                "recommended_action": "refresh",
                "rationale": "Publishing and sync details should feed back into the readable-doc PRD and release-boundary scope.",
                "evidence_refs": [productos_feedback_log["feedback_log_id"], release_gate_decision["release_gate_decision_id"]],
            }
        ],
        "rejected_path_updates": [
            rejected_path_record["rejected_path_record_id"]
        ],
        "next_action": "Keep the readable-doc system active, close the metadata and sync-rule gaps, and refresh the outcome review at the next benchmark window.",
        "reviewed_at": generated_at,
    }

    feature_scorecard = {
        "schema_version": "1.0.0",
        "feature_scorecard_id": f"feature_scorecard_{workspace_id}_readable_doc_bundle_v4_0",
        "workspace_id": workspace_id,
        "feature_id": "readable_doc_bundle",
        "feature_name": "Readable doc bundle and stakeholder alignment slice",
        "loop_id": "decision_to_stakeholder_alignment",
        "status": "reviewed",
        "benchmark_ref": pm_superpower_benchmark["pm_superpower_benchmark_id"],
        "validation_tier": "tier_2",
        "scenarios": [
            {
                "scenario_id": "scn_readable_docs_self_hosted_bundle",
                "title": "Self-hosted readable doc bundle generation",
                "scenario_type": "dogfood_run",
                "result": "partial",
                "summary": "ProductOS can generate and review a same-day readable doc bundle from current artifacts, but publishing metadata and broader sync rules still need another pass.",
                "evidence_refs": [
                    document_sync_state["document_sync_state_id"],
                    readable_doc_validation_lane_report["validation_lane_report_id"],
                ],
            },
            {
                "scenario_id": "scn_readable_docs_pm_internal_review",
                "title": "PM internal review of readable docs",
                "scenario_type": "manual_review",
                "result": "passed",
                "summary": "PM manual validation confirms the roadmap and PRD are usable internally without forcing stakeholders to inspect raw JSON artifacts.",
                "evidence_refs": [
                    manual_validation_record["manual_validation_record_id"],
                    outcome_review["outcome_review_id"],
                ],
            },
        ],
        "evidence_refs": [
            pm_superpower_benchmark["pm_superpower_benchmark_id"],
            document_sync_state["document_sync_state_id"],
            readable_doc_validation_lane_report["validation_lane_report_id"],
            manual_validation_record["manual_validation_record_id"],
            outcome_review["outcome_review_id"],
        ],
        "provenance_classification": "mixed",
        "score_basis": [
            "validation_lane_report",
            "manual_validation_record",
            "outcome_review",
        ],
        "truthfulness_summary": "The readable-doc slice is grounded in validated evidence, but the final promotion claim still depends on incomplete publishing metadata and broader sync assumptions.",
        "dimension_scores": [
            {
                "dimension_key": "pm_leverage",
                "score": 4,
                "rationale": "Readable docs remove most raw-JSON translation work, but the PM still has to close metadata and freshness gaps before the slice feels fully automatic.",
                "evidence_refs": [
                    document_sync_state["document_sync_state_id"],
                    outcome_review["outcome_review_id"],
                ],
            },
            {
                "dimension_key": "output_quality",
                "score": 4,
                "rationale": "The generated roadmap and PRD are audience-fit and traceable, but the bundle still needs one more quality pass before it reaches a true superpower bar.",
                "evidence_refs": [
                    manual_validation_record["manual_validation_record_id"],
                    outcome_review["outcome_review_id"],
                ],
            },
            {
                "dimension_key": "reliability",
                "score": 4,
                "rationale": "Internal use is safe, but external publishing metadata and sync controls are still incomplete enough to block broader promotion.",
                "evidence_refs": [
                    readable_doc_validation_lane_report["validation_lane_report_id"],
                    document_sync_state["document_sync_state_id"],
                ],
            },
            {
                "dimension_key": "autonomy_quality",
                "score": 4,
                "rationale": "The draft-then-review behavior is correct and useful, but the PM still needs targeted intervention for doc freshness and publishing decisions.",
                "evidence_refs": [
                    document_sync_state["document_sync_state_id"],
                    manual_validation_record["manual_validation_record_id"],
                ],
            },
            {
                "dimension_key": "repeatability",
                "score": 4,
                "rationale": "The workspace bundle and validation lane are stable across repeat runs, but wider sync and adapter parity are not yet proven for this slice.",
                "evidence_refs": [
                    readable_doc_validation_lane_report["validation_lane_report_id"],
                    outcome_review["outcome_review_id"],
                ],
            },
        ],
        "overall_score": 4,
        "adoption_recommendation": "keep_in_internal_use",
        "reviewer_verdict": {
            "status": "pass",
            "summary": "The readable-doc slice is traceable and audience-fit enough for internal stakeholder use.",
            "evidence_refs": [
                readable_doc_validation_lane_report["validation_lane_report_id"],
                document_sync_state["document_sync_state_id"],
            ],
        },
        "tester_verdict": {
            "status": "revise",
            "summary": "Schema, path, and bundle checks pass, but publishing metadata coverage is not complete enough for broader promotion.",
            "evidence_refs": [
                readable_doc_validation_lane_report["validation_lane_report_id"],
                document_sync_state["document_sync_state_id"],
            ],
        },
        "manual_verdict": {
            "status": "accept",
            "summary": "The PM can use the bundle internally while metadata hardening and doc freshness automation continue.",
            "evidence_refs": [
                manual_validation_record["manual_validation_record_id"],
                outcome_review["outcome_review_id"],
            ],
        },
        "blocked_by": [
            "External publishing metadata rules are not yet encoded in the readable-doc control artifacts.",
            "Broader SharePoint and Confluence sync behavior is still undefined for this slice.",
        ],
        "feedback_items": [
            {
                "feedback_id": "score_feedback_publish_metadata",
                "summary": "Encode mandatory SharePoint and Confluence publishing metadata before the readable-doc bundle is promoted beyond internal use.",
                "impact_level": "high",
                "recommended_action": "Add publishing metadata rules to the doc-sync controls and rescore the feature after another dogfood run.",
                "route_targets": [
                    "productos_feedback_log",
                    "improvement_loop_state",
                ],
                "linked_dimension_keys": [
                    "reliability",
                    "repeatability",
                ],
                "linked_artifact_refs": [
                    document_sync_state["document_sync_state_id"],
                    readable_doc_validation_lane_report["validation_lane_report_id"],
                ],
            },
            {
                "feedback_id": "score_feedback_doc_freshness",
                "summary": "Automate doc freshness refresh so the PM does not need targeted follow-up to keep discovery, roadmap, and PRD docs current.",
                "impact_level": "medium",
                "recommended_action": "Add doc-freshness checks and rescore once the next self-hosted bundle proves lower PM intervention.",
                "route_targets": [
                    "productos_feedback_log",
                    "feedback_cluster_state",
                ],
                "linked_dimension_keys": [
                    "pm_leverage",
                    "autonomy_quality",
                ],
                "linked_artifact_refs": [
                    document_sync_state["document_sync_state_id"],
                    outcome_review["outcome_review_id"],
                ],
            },
        ],
        "next_action": "Keep the readable-doc bundle active internally, route the metadata and freshness gaps into the next bounded improvement slice, and rescore after the next dogfood run.",
        "generated_at": generated_at,
    }

    presentation_brief["created_at"] = generated_at
    presentation_evidence_pack = build_evidence_pack(presentation_brief)
    presentation_story = build_presentation_story(presentation_brief, presentation_evidence_pack)
    presentation_render_spec = build_render_spec(presentation_brief, presentation_story)
    presentation_slide_spec = build_slide_spec(presentation_brief)
    presentation_publish_check = build_publish_check(presentation_brief, presentation_render_spec, target_format="html")
    presentation_ppt_export_plan = build_ppt_export_plan(presentation_render_spec)

    presentation_evidence_pack["generated_at"] = generated_at
    presentation_story["generated_at"] = generated_at
    presentation_render_spec["generated_at"] = generated_at
    presentation_slide_spec["generated_at"] = generated_at
    presentation_publish_check["generated_at"] = generated_at
    presentation_ppt_export_plan["generated_at"] = generated_at

    presentation_validation_lane_report = {
        "schema_version": "1.0.0",
        "validation_lane_report_id": f"validation_lane_report_{workspace_id}_presentation_packaging_v4_1",
        "workspace_id": workspace_id,
        "artifact_ref": presentation_brief["presentation_brief_id"],
        "artifact_type": "presentation_package",
        "stage_name": "v4_1_document_to_presentation_packaging",
        "validation_tier": "tier_3",
        "overall_status": "ready_for_manual_validation",
        "review_summary": "The generated presentation package is traceable, publish-check clean for the HTML path, and ready for mandatory manual leadership validation before broader use.",
        "ai_reviewer_lane": {
            "status": "proceed",
            "reviewer_role": "AI Reviewer",
            "blocking_findings": [],
            "non_blocking_findings": [
                "The deck leads with the decision and keeps evidence-linked narrative structure visible.",
                "The risk slide keeps governance and pattern-approval controls explicit instead of implying silent safety."
            ],
            "unresolved_questions": [
                "Should the first slide surface the recommendation even more aggressively for the live presentation mode?"
            ],
        },
        "ai_tester_lane": {
            "status": "passed",
            "tester_role": "AI Tester",
            "checks_run": [
                "presentation brief schema validation",
                "presentation runtime bundle generation",
                "render spec and slide spec schema validation",
                "publish check and ppt export plan validation"
            ],
            "blocking_findings": [],
            "non_blocking_findings": [
                "The workspace presentation brief generates evidence, story, render, slide, publish, and PPT-plan outputs without runtime errors."
            ],
            "automation_gaps": [
                "Leadership usefulness validation for the communication pattern still requires mandatory manual review."
            ],
        },
        "manual_validation_policy": {
            "required": True,
            "scope": "mandatory",
            "owner_role": "PM Leader / Communicator",
            "status": "pending",
            "rationale": "Tier 3 leadership-facing presentation outputs require mandatory manual validation before adoption or publication."
        },
        "referee_trigger": {
            "required": False,
            "rationale": "AI Reviewer and AI Tester agree that the package may advance to manual validation.",
            "conflicting_lanes": []
        },
        "governance_layer_refs": [
            "core/docs/presentation-audience-policy.md",
            "core/docs/presentation-narrative-quality-checks.md",
            "core/docs/presentation-regression-fixtures.md"
        ],
        "next_action": "Run mandatory PM Leader manual validation on the leadership presentation package before adopting it as the default V4 communication path.",
        "generated_at": generated_at,
    }

    presentation_sample_record["captured_at"] = generated_at
    presentation_pattern_review["reviewed_at"] = generated_at

    return {
        "pm_superpower_benchmark": pm_superpower_benchmark,
        "persona_operating_profile": persona_operating_profile,
        "validation_lane_report": validation_lane_report,
        "document_sync_state": document_sync_state,
        "readable_doc_validation_lane_report": readable_doc_validation_lane_report,
        "manual_validation_record": manual_validation_record,
        "referee_decision_record": referee_decision_record,
        "ai_agent_benchmark": ai_agent_benchmark,
        "rejected_path_record": rejected_path_record,
        "outcome_review": outcome_review,
        "feature_scorecard": feature_scorecard,
        "presentation_brief": presentation_brief,
        "presentation_evidence_pack": presentation_evidence_pack,
        "presentation_story": presentation_story,
        "presentation_render_spec": presentation_render_spec,
        "presentation_slide_spec": presentation_slide_spec,
        "presentation_publish_check": presentation_publish_check,
        "presentation_ppt_export_plan": presentation_ppt_export_plan,
        "presentation_validation_lane_report": presentation_validation_lane_report,
        "presentation_sample_record": presentation_sample_record,
        "presentation_pattern_review": presentation_pattern_review,
    }


def build_v4_market_intelligence_bundle_from_workspace(
    workspace_dir: Path | str,
    *,
    generated_at: str,
) -> dict[str, Any]:
    workspace_path = Path(workspace_dir).resolve()
    artifacts_dir = workspace_path / "artifacts"
    root_dir = Path(__file__).resolve().parents[3]

    source_note_card_files = [
        "source_note_card_productboard_spark_official_2026.example.json",
        "source_note_card_jpd_ai_official_2026.example.json",
        "source_note_card_aha_knowledge_ai_official_2026.example.json",
        "source_note_card_linear_asks_official_2026.example.json",
        "source_note_card_notion_mcp_official_2026.example.json",
        "source_note_card_coda_ai_official_2026.example.json",
        "source_note_card_asana_ai_teammates_official_2026.example.json",
        "source_note_card_openai_deep_research_official_2026.example.json",
        "source_note_card_gemini_deep_research_official_2026.example.json",
        "source_note_card_perplexity_deep_research_official_2026.example.json",
        "source_note_card_glean_agentic_engine_official_2026.example.json",
        "source_note_card_crayon_ci_official_2026.example.json",
        "source_note_card_klue_compete_agent_official_2026.example.json",
        "source_note_card_semrush_eyeon_official_2026.example.json",
    ]

    source_note_cards = [
        _load_json(artifacts_dir / filename)
        for filename in source_note_card_files
    ]
    research_notebook = _load_json(artifacts_dir / "research_notebook_agentic_market_intelligence.example.json")
    landscape_matrix = _load_json(artifacts_dir / "landscape_matrix_agentic_market_intelligence.example.json")
    competitor_dossier = _load_json(artifacts_dir / "competitor_dossier_agentic_market_intelligence.example.json")
    market_analysis_brief = _load_json(artifacts_dir / "market_analysis_brief_agentic_market_intelligence.example.json")
    research_feature_recommendation_brief = _load_json(
        artifacts_dir / "research_feature_recommendation_brief.example.json"
    )
    ralph_loop_state = _load_json(artifacts_dir / "ralph_loop_state.example.json")
    validation_lane_report = _load_json(
        artifacts_dir / "validation_lane_report_market_intelligence.example.json"
    )
    manual_validation_record = _load_json(
        artifacts_dir / "manual_validation_record_market_intelligence.example.json"
    )
    rejected_path_record = _load_json(
        artifacts_dir / "rejected_path_record_market_intelligence.example.json"
    )
    leadership_review = _load_json(
        artifacts_dir / "leadership_review_market_intelligence_distribution.example.json"
    )
    portfolio_update = _load_json(
        artifacts_dir / "portfolio_update_market_intelligence_distribution.example.json"
    )
    market_distribution_report = _load_json(
        artifacts_dir / "runtime_scenario_report_market_distribution.example.json"
    )
    stable_release_metadata = latest_release_metadata(root_dir)

    research_feature_recommendation_brief["created_at"] = generated_at
    ralph_loop_state["generated_at"] = generated_at
    validation_lane_report["generated_at"] = generated_at
    manual_validation_record["recorded_at"] = generated_at
    leadership_review["generated_at"] = generated_at
    portfolio_update["generated_at"] = generated_at
    market_distribution_report["generated_at"] = generated_at

    return {
        "source_note_cards": source_note_cards,
        "research_notebook": research_notebook,
        "landscape_matrix": landscape_matrix,
        "competitor_dossier": competitor_dossier,
        "market_analysis_brief": market_analysis_brief,
        "research_feature_recommendation_brief": research_feature_recommendation_brief,
        "ralph_loop_state": ralph_loop_state,
        "validation_lane_report": validation_lane_report,
        "manual_validation_record": manual_validation_record,
        "rejected_path_record": rejected_path_record,
        "leadership_review": leadership_review,
        "portfolio_update": portfolio_update,
        "market_distribution_report": market_distribution_report,
        "stable_release_metadata": stable_release_metadata,
    }
