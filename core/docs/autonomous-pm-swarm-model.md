# Autonomous PM Swarm Model

Purpose: Define the internal-only governed model for broader autonomous PM/swarm work inside ProductOS without changing the current external release claim.

## Boundary

This model is for ProductOS self-hosting and internal dogfooding.

It is not permission to market ProductOS as a full autonomous PM replacement.

External claims remain bounded by the current release scope until the swarm proves outcome movement, reviewer discipline, and Ralph-loop completion on repeated real runs.

## Why This Exists

ProductOS already has:

- a PM-visible cockpit
- orchestration and execution state
- specialist persona contracts
- a Ralph loop for quality
- feature scoring and release-gate accounting

What it does not yet have is one explicit internal operating plan for using those pieces as a supervised PM swarm.

Without that plan, the system risks:

- parallel routes opening without clear ownership
- reviewer lanes being treated as optional
- contradictory recommendations arriving without one escalation path
- output volume increasing faster than PM leverage

## Swarm Definition

A ProductOS PM swarm is a bounded specialist set working under PM supervision.

It should behave like:

1. one mission queue
2. one visible orchestration surface
3. one reviewer stack
4. one Ralph-governed quality loop
5. one explicit next action

It should not behave like an open-ended background mesh of agents creating work without an accountable gate.

## Required Operating Rules

### 1. PM supervision stays explicit

- AI routes, drafts, critiques, and validates
- PM approves decision-driving scope, stakeholder-facing outputs, and release movement
- no swarm route may silently convert a recommendation into commitment

### 2. One bounded mission at a time

- every active route must belong to a named mission
- every mission must define success, exit condition, and review triggers
- duplicate missions should collapse into the active route instead of branching

### 3. Ralph is mandatory

Every broader autonomous PM/swarm slice must pass:

1. inspect
2. implement
3. refine
4. validate
5. fix
6. revalidate

The shorthand is practical, but the fix and revalidate stages may not be skipped when weaknesses are found.

### 4. Reviewer stack is fixed by route type

Default stack:

- `AI Reviewer` for logic, traceability, and contradiction handling
- `AI Tester` for schemas, workflow wiring, and regression checks
- `PM Builder` or relevant PM owner for final scope and approval decisions

Optional specialist reviewers should be added only when the route truly changes their domain.

### 5. Anti-loop controls are first-class

Every swarm mission must encode:

- max parallel routes
- max retries per stage
- stale-loop threshold
- duplicate-route handling
- contradiction escalation
- blocked-state behavior

If these controls are not visible in state, the swarm is still too implicit to trust.

## Stage Gates

The broader swarm should move through these gates:

1. signal accepted for tracking
2. mission accepted for bounded execution
3. reviewer-clean recommendation package ready
4. validation-clean package ready
5. PM decision taken
6. outcome movement reviewed

No gate should be inferred from agent optimism alone.

## Artifact Contract

Use `autonomous_pm_swarm_plan` as the system-of-record artifact for:

- mission summary
- active persona stack
- route plan
- review stack
- anti-loop controls
- Ralph iteration target
- next action

This artifact is intentionally planning-heavy.

Execution should stay visible through existing runtime artifacts such as:

- `cockpit_state`
- `orchestration_state`
- `execution_session_state`
- `feature_scorecard`
- `feature_portfolio_review`

## Current ProductOS Posture

Current ProductOS can support an internal governed swarm candidate because it already has:

- explicit runtime control surfaces
- specialist persona contracts
- bounded CLI-driven loops
- eval and release-gate logic

Current ProductOS cannot yet claim a general autonomous PM swarm externally because it still needs stronger proof of:

- repeated loop-level outcome movement
- lower PM rewrite and unblock rates
- contradiction recovery under real workload
- durable post-release accounting for swarm-driven changes

## Next Action

Keep the swarm internal, route it through the same scoring and review surfaces as other ProductOS capabilities, and only broaden the claim set after repeated Ralph-complete proof exists.
