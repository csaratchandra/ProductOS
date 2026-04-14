# ProductOS Continuous Intake And Memory Model

Purpose: Define the minimum V3 baseline for always-on intake and memory retrieval without claiming a fully autonomous background system.

## Steering Layer

Intake and memory should not operate without reusable steering.

ProductOS should keep a named steering context that declares:

- stable operating norms
- default artifact focus for the current mission
- memory retrieval priority order
- reusable steering references that live in the repository

This steering layer should stay inspectable and repo-backed rather than hidden in host prompts or side-channel notes.

## Internal Boundary

The continuous-intake and memory baseline is an internal runtime capability for ProductOS V3 development and proof.

It should improve PM leverage, but the self-improvement loop that uses it remains internal-only.

## Runtime Artifacts

### `intake_routing_state`

Use this state to show:

- which inbox paths are actively monitored
- which items were captured
- whether provenance is complete
- whether each item is normalized, routed, or blocked
- which downstream workflows should consume each item

### `memory_retrieval_state`

Use this state to show:

- what prior context was requested
- which records were retrieved
- why each record was retrieved
- freshness and confidence of the retrieved context
- provenance warnings and unresolved retrieval gaps

## Intake Rule

The V3 baseline does not require autonomous background processing everywhere.

It requires that ProductOS can represent continuous intake as explicit state and route inbox items forward without losing provenance.

## Memory Rule

The V3 baseline does not require perfect long-term memory.

It requires that ProductOS can retrieve prior decisions, evidence, artifacts, repeated issues, and strategic memory with enough provenance that the PM can decide whether to trust or review the context.

## Interaction Model

1. `intake_routing_state` captures what just entered the workspace and where it should go
2. downstream workflows normalize or route the item into canonical artifacts
3. steering context declares which artifacts and memory types matter most for the current mission
4. `memory_retrieval_state` pulls back the most relevant prior context for the current task
5. `cockpit_state` and `orchestration_state` use that intake and memory context to reduce PM reconstruction work

## Provenance Rule

If intake provenance is partial or missing:

- the item may still be tracked
- the item should not become a publish-driving source without review
- the warning should remain visible in `intake_routing_state` or `memory_retrieval_state`
