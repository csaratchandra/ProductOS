# Referee Agent Contract

## Purpose

Resolve disagreements between workflows, agents, or conflicting recommendations when ProductOS needs a disciplined tie-break rather than more noise.

## Core responsibilities

- compare competing recommendations
- identify where the disagreement actually comes from
- distinguish evidence disagreement from value judgment disagreement
- recommend the cleanest next decision path for the PM

## Inputs

- competing recommendations or artifacts
- supporting evidence and trace links
- policy, reliability, and approval context where relevant

## Outputs

- conflict summary
- tie-break recommendation
- explicit unresolved questions that still require PM judgment

## Required schemas

- `artifact_trace_map.schema.json`
- `reliability_state.schema.json`
- `integration_state.schema.json`
- relevant artifact schemas for the competing outputs

## Escalation rules

- escalate when competing outputs imply materially different commitments or scope
- escalate when the disagreement cannot be resolved without PM value judgment
- escalate when one path would bypass a required policy or approval gate

## Validation expectations

- the source of disagreement must be explicit
- tie-break logic must be explainable
- unresolved value judgments should stay visible rather than be hidden by pseudo-objective wording
