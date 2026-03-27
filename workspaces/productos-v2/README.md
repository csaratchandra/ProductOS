# ProductOS Self-Hosting Workspace

This workspace seeds the V2 repository with a concrete PM operating context derived from the V1 sample workspace.

Current bootstrap contents focus on:

- current-state assessment and release-candidate readiness
- inbox-driven raw-input intake
- idea capture and concept framing
- weak-signal triage and customer pulse synthesis
- research notebook and research brief generation
- competitive, segment, and persona context
- change handling
- incremental delivery planning
- meeting automation
- status communication
- decision queue and follow-up queue management
- decision traceability
- ProductOS feedback logging

The workspace now includes a discovery-to-research starter pack under `artifacts/` plus routed handoff examples under `handoffs/` so the V2 repository has concrete upstream context before delivery workflows begin.

The delivery handoff example `handoffs/story_generate_status_draft.md` shows how implementation context can be attached to a story without turning side-channel notes into hidden scope.

For the core discovery-to-delivery chain, the workspace should be treated as operating on real artifact documents rather than seed examples:

- `artifacts/idea_record.json`
- `artifacts/concept_brief.json`
- `artifacts/problem_brief.json`
- `artifacts/prototype_record.json`
- `artifacts/prd.json`
- `artifacts/increment_plan.json`
- `artifacts/program_increment_state.json`

The workspace also now includes:

- a scaffolded `inbox/` for raw notes, transcripts, screenshots, documents, spreadsheets, and support exports
- a `feedback/` folder plus `productos_feedback_log` artifact for ProductOS-as-a-product feedback
- runtime-state artifacts for queue steering, orchestration, execution sessions, and adapter visibility: `cockpit_state`, `orchestration_state`, `execution_session_state`, and `runtime_adapter_registry`
- live-intake and baseline-memory artifacts: `intake_routing_state` and `memory_retrieval_state`
- internal learning-loop artifacts: `feedback_cluster_state` and `release_scope_recommendation`
- runtime proof and release-decision artifacts: `pm_benchmark`, `release_readiness`, `runtime_scenario_report`, and `release_gate_decision`
- lifecycle design and reasoning artifacts: `ux_design_review`, `visual_reasoning_state`, and `superpower_benchmark`
- gap-clustering and improvement-loop artifacts: `gap_cluster_state` and `improvement_loop_state`
- benchmark, persona, and governance artifacts: `pm_superpower_benchmark`, `persona_operating_profile`, and `validation_lane_report`
- readable-doc governance artifacts: `document_sync_state`, `manual_validation_record`, and `referee_decision_record`
- loop-memory and review artifacts: `ai_agent_benchmark`, `rejected_path_record`, and `outcome_review`
- the first readable product-doc bundle under `docs/`
- the first live product-doc bundle under `docs/product/`
- the first governed messaging bundle under `docs/marketing/`
- communication entry artifacts: `presentation_brief`
- presentation-governance artifacts: `presentation_sample_record` and `presentation_pattern_review`
- market-intelligence artifacts: `research_feature_recommendation_brief`, `ralph_loop_state`, and the supporting agentic market-intelligence research pack
- live-doc governance artifacts: `document_sync_state_live_docs`, `validation_lane_report_live_docs`, `manual_validation_record_live_docs`, `rejected_path_record_live_docs`, and `ralph_loop_state_live_docs`
- archived historical completion bundles now live under `archive/historical-artifacts/`

The self-improvement loop in this workspace is internal-only.

It is used to dogfood ProductOS while building later versions, but it is not part of the external ProductOS product promise.

The current next-version control surface is the repo CLI at `./productos`.

The current stable V6.0 line is lifecycle traceability through `release_readiness`, using the starter workspace as the clean adoption surface.

The current follow-on work is extending lifecycle traceability beyond `release_readiness` without broadening the stable V6 claim prematurely.

The canonical current-plan entry point is [current-plan.md](/Users/sarat/Documents/code/ProductOS/workspaces/productos-v2/docs/planning/current-plan.md).

Useful commands:

- `./productos status`
- `./productos ingest`
- `./productos run discover`
- `./productos run align`
- `./productos run operate`
- `./productos run improve`
- `./productos v5 --output-dir /tmp/productos-v5-lifecycle`
- `./productos v6 --output-dir /tmp/productos-v6-lifecycle`
- `./productos review`
- `./productos export --output-dir /tmp/productos-next-version`
- `./productos doctor`
- `./productos cutover --output-path workspaces/productos-v2/docs/planning/v6-cutover-plan.md`

The path name `workspaces/productos-v2/` is legacy.

It remains the self-hosting workspace even as the core release line advances beyond `2.0.0`.
