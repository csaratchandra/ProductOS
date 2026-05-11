# Mission Brief

Status: active
Audience: PM, engineering, design, leadership
Owner: ProductOS PM
Updated At: 2026-04-27

## Mission

- Title: `PM superpower recovery mission`
- Target user: `Product manager using ProductOS with Codex, Claude, Windsurf, or Antigravity style agents`
- Operating mode: `full_loop`
- Entry phase: `discover`
- Phase sequence: `discover`, `align`, `operate`, `improve`
- Reviewer lane: `pm_builder`

ProductOS Reference Workspace should help Product manager using ProductOS with Codex, Claude, Windsurf, or Antigravity style agents solve PMs still need one repo-native way to carry mission, research, prioritization, delivery, and review context through the full lifecycle without rebuilding the decision chain by hand.

## Core Questions

- Customer problem: PMs still need a single repo-native way to move from mission and evidence through prioritization, delivery, review, and bounded communication outputs without rebuilding the story or losing provenance by hand.
- Business goal: Make ProductOS credible for the first impatient customer by proving a coherent lifecycle-enrichment spine with governed research, prioritization, delivery traceability, and bounded visual outputs.

## Success Metrics

- time from intake to reviewable PRD
- time from PRD to aligned docs and deck
- weekly PM autopilot quality
- time from aligned artifact set to publish-ready deck or corridor

## Constraints

- Keep PM approval explicit for decision-driving scope and release movement.
- Preserve observed versus inferred claims when evidence is incomplete.
- Do not broaden autonomous PM claims past the current evidence-backed release boundary.

## Steering Norms

- Treat the repository as the system of record.
- Keep PM approval explicit for decision-driving scope, stakeholder-facing output, and release movement.
- Preserve observed versus inferred claims when evidence is incomplete.
- Prefer the smallest coherent slice that can be reviewed and validated end to end.

## Memory Priority Order

- `decisions`
- `evidence`
- `prior_artifacts`
- `repeated_issues`
- `strategic_memory`

## Primary Workflow Path

- `../../core/workflows/workspace-ingestion/inbox-to-normalized-evidence-workflow.md`
- `../../core/workflows/discovery/idea-to-concept-workflow.md`
- `../../core/workflows/research/research-command-center-workflow.md`
- `../../core/workflows/delivery/problem-brief-to-prd-workflow.md`
- `../../core/workflows/delivery/prd-to-stories-workflow.md`
- `../../core/workflows/delivery/stories-to-acceptance-workflow.md`
- `../../core/workflows/launch/release-readiness-workflow.md`
- `../../core/workflows/mastery/post-release-outcome-review-workflow.md`
- `../../core/workflows/mastery/bounded-improvement-workflow.md`
- `../../core/workflows/visual-operating-system/artifact-to-visual-rendering-workflow.md`

## Steering References

- `tests/fixtures/workspaces/productos-sample/docs/planning/steering-context.md`
- `core/docs/vendor-neutral-agent-harness-standard.md`
- `core/docs/ralph-loop-model.md`

## Next Action

Keep the mission routed through the strategy spine and complete `P0/P1/P2` lifecycle-enrichment reconciliation before broadening any release claim; treat visual surfaces as one aligned output lane inside that governed lifecycle.
