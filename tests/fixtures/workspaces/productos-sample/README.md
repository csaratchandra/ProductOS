# ProductOS Reference Workspace

This workspace is the private reference ProductOS loop used to build the next ProductOS version.

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
- mission-first PM control-plane artifacts: `product_record`, `phase_packet`, `workspace_tree_state`, `portfolio_state`, `cross_product_insight_index`, and `cockpit_bundle`
- live-intake and baseline-memory artifacts: `intake_routing_state` and `memory_retrieval_state`
- mission-boundary and reviewer-lane visibility inside the runtime control plane so the PM can see the active stage, current route, and next review gate
- a named steering-context layer so mission routing, operating norms, and memory priority order stay repo-visible and reusable
- internal learning-loop artifacts: `feedback_cluster_state` and `release_scope_recommendation`
- runtime proof and release-decision artifacts: `pm_benchmark`, `release_readiness`, `release_note`, `runtime_scenario_report`, and `release_gate_decision`
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

The PM-first mission surface is now the mission brief at `artifacts/mission_brief.json`, which can be refreshed with `./productos init-mission`.

The newer cockpit and portfolio surfaces should still be treated as bounded internal control-plane helpers. They make phase, approval, and context state more legible, but they are not standalone proof of broader autonomy or a larger public release promise.

The current public stable line is ProductOS `V8.4.0`.

The active reference program is now lifecycle-enrichment reconciliation across three bounded tracks:

- `P0` runtime, starter-workspace, and governed-doc coherence
- `P1` discovery, research, and prioritization enrichment
- `P2` downstream learning, traceability, and explicit reopen recommendations

The visual operating system work remains valuable, but it should be treated as a dependent aligned-output slice inside that broader lifecycle program rather than the primary next release claim.

The canonical current-plan entry point is [current-plan.md](/Users/sarat/Documents/code/ProductOS/tests/fixtures/workspaces/productos-sample/docs/planning/current-plan.md).

Useful commands:

- `./productos status`
- `./productos init-mission --title "Mission" --target-user "PM" --customer-problem "Problem" --business-goal "Goal" --success-metric "time to reviewable PRD" --maturity-band one_to_ten --primary-kpi "time to reviewable PRD" --primary-outcome "Create one reviewable PM package" --review-gate-owner "ProductOS PM"`
- `./productos phase plan validation`
- `./productos cockpit build`
- `./productos portfolio build --workspace tests/fixtures/workspaces/productos-sample --suite-id suite_productos`
- `./productos ingest`
- `./productos run discover`
- `./productos run align`
- `./productos run operate`
- `./productos run improve`
- `./productos v5 --output-dir /tmp/productos-v5-lifecycle`
- `./productos v6 --output-dir /tmp/productos-v6-lifecycle`
- `./productos v7 --output-dir /tmp/productos-v7-lifecycle`
- `./productos review`
- `./productos export --output-dir /tmp/productos-next-version`
- `./productos doctor`
- `./productos cutover --output-path tests/fixtures/workspaces/productos-sample/docs/planning/v7-cutover-plan.md`

This workspace is intentionally separate from PM product workspaces and should stay out of `workspaces/`.
