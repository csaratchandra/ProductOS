# Steering Context

Mission: `PM superpower recovery mission`
Operating Mode: `full_loop`

## Mission Router

- Entry phase: `discover`
- Phase sequence: `discover`, `align`, `operate`, `improve`
- Primary reviewer lane: `pm_builder`

Run the full PM loop from a mission-first discover start while keeping PM approval explicit at every decision-driving boundary.

## Stop Conditions

- Stop if any phase loses provenance, reviewability, or PM approval visibility.
- Stop if downstream phases outrun the accepted mission package.
- Stop if release-facing claims exceed the current evidence-backed boundary.

## Operating Norms

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

## Default Artifact Focus

- `mission_brief`
- `problem_brief`
- `concept_brief`
- `prd`
- `document_sync_state`
- `presentation_brief`
- `status_mail`
- `feature_portfolio_review`

## Steering References

- `tests/fixtures/workspaces/productos-sample/docs/planning/steering-context.md`
- `core/docs/vendor-neutral-agent-harness-standard.md`
- `core/docs/ralph-loop-model.md`

