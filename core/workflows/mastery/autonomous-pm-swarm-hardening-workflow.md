# Autonomous PM Swarm Hardening Workflow

Purpose: Define, harden, and score a governed autonomous PM swarm plan before ProductOS broadens its internal autonomous-PM coverage.

## Inputs

- [autonomous-pm-swarm-model.md](/Users/sarat/Documents/code/ProductOS/core/docs/autonomous-pm-swarm-model.md)
- [ai-agent-persona-operating-model.md](/Users/sarat/Documents/code/ProductOS/core/docs/ai-agent-persona-operating-model.md)
- [ralph-loop-model.md](/Users/sarat/Documents/code/ProductOS/core/docs/ralph-loop-model.md)
- current `cockpit_state`, `orchestration_state`, and `execution_session_state`
- current `feature_portfolio_review` and relevant `feature_scorecard` artifacts

## Outputs

- `autonomous_pm_swarm_plan`
- swarm readiness scorecard or review summary
- explicit proceed, revise, defer, or block next action

## Operating Sequence

1. Inspect the current runtime, persona stack, and review lanes that the swarm would rely on.
2. Define one bounded swarm mission with explicit personas, route ownership, success metrics, and PM decision gates.
3. Encode anti-loop controls before any broader autonomy claim is scored.
4. Run a Ralph refinement cycle over the plan until routes, reviewer triggers, and blocked-state behavior are legible.
5. Validate the plan against current runtime state, score-bearing outputs, and release-boundary rules.
6. Record blockers and rejected paths when the swarm would create hidden scope, duplicate work, or contradiction churn.
7. Revalidate and emit one explicit next action: proceed internally, revise, defer, or block.

## Rules

- keep the swarm internal until repeated real runs prove outcome movement
- do not let a swarm route bypass PM approval for scope or release movement
- every route must have one accountable owner persona and one exit condition
- if a route opens duplicate work, collapse it into the active route and preserve the rationale
- if reviewer or PM gates disagree, escalate instead of auto-selecting the most optimistic answer
