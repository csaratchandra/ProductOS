# Workflow Corridor Design

## Purpose

Design customer-safe workflow corridors that explain ownership, handoffs, proof posture, and scenario deltas on one HTML-native page.

## Trigger / When To Use

- when a PM needs to explain a workflow externally without relying on slides
- when workflow publication needs stage, ownership, and proof grammar rather than deck storytelling
- when corridor output must stay customer-safe and publication-gated

## Inputs

- `workflow_corridor_spec`
- workflow stages, lanes, transitions, overlays, personas, and proof items
- audience and publication context

## Outputs

- corridor composition guidance
- corridor narrative and section priorities
- escalation when the workflow is too ambiguous to publish safely

## Guardrails

- stage cards are the primary structural primitive
- ownership transitions must read as explicit handoffs
- proof rails must distinguish observed, inferred, and hypothesis-level claims
- scenario deltas must stay secondary to the canonical baseline

## Execution Pattern

1. confirm the canonical workflow baseline and publication mode
2. map stages, owners, and handoffs into one corridor reading path
3. keep proof posture visible beside the claims it supports
4. place persona and scenario variation as secondary overlays
5. fail or bound the output when ownership or proof ambiguity is still material

## Validation Expectations

- the corridor explains one workflow clearly without presenter narration
- ownership and blocked/watch states remain visible
- customer-safe publication never depends on post-render cleanup
