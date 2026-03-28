# Release Readiness Workflow

Purpose: Convert delivery artifacts and validation signals into release readiness and release communication outputs.

## Inputs

- `feature_record`
- `acceptance_criteria_set`
- `test_case_set`
- test execution and defect summary
- `reliability_state`
- `integration_state`
- optional `pm_benchmark`
- optional `runtime_scenario_report`
- issue log and dependency state
- support readiness artifacts
- launch constraints and customer commitments

## Outputs

- `release_readiness`
- optional `release_gate_decision`
- `release_note`
- rollout recommendation
- go, conditional-go, or no-go rationale

## Operating Sequence

1. Confirm release scope, intended audience, and feature traceability.
2. Classify release scope by product impact: major product change, feature enhancement, minor improvement, bug fix, or internal-only maintenance.
3. Confirm launch owner and reviewer coverage for the actual workspace context.
4. Evaluate acceptance, test, reliability, integration, and support readiness gates.
5. Classify unresolved items as blocker, conditional risk, or watch item.
6. Produce a release decision with rollout, rollback, owner expectations, and recommended version increment.
7. Generate internal readiness output and customer-facing release communication from the same validated evidence set.

## Readiness Gates

- feature scope is traceable to validated acceptance criteria
- critical test coverage is executed for the committed release path
- reliability, trust, privacy, and compliance blockers are resolved or explicitly waived
- open dependencies and operational support gaps have named owners and dates
- launch ownership and reviewer coverage are explicit for go-to-market, customer communication, and support readiness where relevant
- release communication reflects only validated and approved claims
- release classification is explicit and defensible

## Rules

- do not mark ready when critical checks fail or blocker defects remain unresolved
- do not assume a fixed org chart such as a mandatory "marketing head"; require explicit role coverage instead
- conditional-go decisions must name the exact risk, owner, and rollback trigger
- preserve traceability from release-note claims back to validated feature evidence
- keep internal readiness notes and customer-facing release notes distinct even when they share source facts
- never hide compliance, privacy, integration, or support gaps inside a generic risk summary
- rollout recommendation must state whether release should be immediate, phased, guarded, or blocked
- if change classification and release type disagree materially, escalate before publish
