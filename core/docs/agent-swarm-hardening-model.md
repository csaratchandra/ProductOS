# Agent Swarm Hardening Model

Purpose: Define hardening requirements for the V10 agent swarm to graduate from internal-governed capability to production-grade autonomous coordination.

## Current Swarm State (V10)

- Autonomous PM swarm is internal/dogfood only
- Specialist persona contracts defined (orchestrator, discoverer, reviewer, etc.)
- Review gates composite f(confidence, impact, maturity)
- Ralph loop mandatory for all major changes
- Anti-loop controls defined but not hardened under load

## Hardening Requirements

| Requirement | Current State | Target | Evidence Needed |
|---|---|---|---|
| Parallel agent reliability | Not tested under real workload | 3 parallel agents produce consistent, non-contradictory output in >90% of runs | 10 dogfood runs with 3+ parallel agents |
| Contradiction recovery | Detection exists, resolution is manual | Automatic conflict resolution for 80% of contradictions; escalate 20% to PM | Contradiction log with resolution rates |
| PM rewrite rate | ~40% (V9 baseline) | <10% for high-confidence outputs, <25% overall | Feature scorecard evidence across 5 capabilities |
| Unblock rate | Not measured | PM unblocks within 1 review cycle for 90% of blocked items | Block log with resolution timestamps |
| Post-release accounting | Not implemented | Every swarm-driven change has post-release outcome traceability | Outcome reviews linked to swarm change records |
| Anti-loop enforcement | Defined in contract, not enforced in runtime | Max parallel routes, max retries, stale-loop threshold enforced mechanically | Runtime guard violation logs |
| Cross-loop learning | Ad-hoc | Learning patterns from one loop feed into improvement of other loops | Learning transfer records |
| Confidence calibration | Not calibrated | System's stated confidence matches its actual accuracy within 15% | Confidence vs accuracy calibration chart |

## Swarm Promotion Gates

1. 10 consecutive dogfood runs with no contradiction escalation to PM
2. Feature scorecard average >=4.0 across all swarm-driven capabilities
3. PM override rate <5% of total outputs
4. Post-release accounting complete for 100% of swarm changes
5. Anti-loop controls mechanically enforced with zero runtime violations

## Current Posture

Keep swarm internal. Route through same scoring and review surfaces. Only broaden claim set after repeated Ralph-complete proof.

## Next Action

Run 10 dogfood cycles in one explicit workspace with 3+ parallel agents. Collect evidence per hardening requirement. Rescore after evidence.
