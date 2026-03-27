# Orchestrator Agent Contract

## Purpose

Coordinate multiple specialist agents and workflows so ProductOS behaves like a coherent operating system rather than disconnected single-step tools.

## Core responsibilities

- choose and sequence specialist agents for a workflow
- manage handoffs between discovery, delivery, communication, and governance paths
- prevent duplicate or conflicting downstream execution
- emit explicit route rationale and queue impacts when runtime state requires PM review or escalation
- route blocked or contradictory states to the correct escalation path

## Inputs

- PM request framing from `cockpit`
- `orchestration_state`
- `workflow_state`
- `handoff_contract`
- `reliability_state`
- `integration_state`
- `execution_session_state` where bounded work is already in flight
- `intake_routing_state` where new inbox items should trigger workflow routing
- `memory_retrieval_state` where prior context changes the recommended route
- `runtime_adapter_registry` where host capability affects routing
- workspace policies where relevant

## Outputs

- `orchestration_state`
- specialist routing decisions
- handoff sequencing decisions
- `execution_session_state` creation or update recommendations where runtime adapters exist
- intake-routing recommendations when new inbox items should trigger downstream workflows
- queue impact recommendations when blocked or review-needed routes should surface through cockpit queues
- escalation recommendations when execution should pause or reroute

## Required schemas

- `orchestration_state.schema.json`
- `workflow_state.schema.json`
- `handoff_contract.schema.json`
- `reliability_state.schema.json`
- `integration_state.schema.json`
- `execution_session_state.schema.json`
- `intake_routing_state.schema.json`
- `memory_retrieval_state.schema.json`
- `runtime_adapter_registry.schema.json`

## Escalation rules

- escalate when multiple specialist paths would create conflicting outputs
- escalate when blocked, stale, or contradictory inputs affect the next planned step
- escalate when a requested workflow would bypass a required validation or approval gate

## Validation expectations

- orchestration decisions must be explainable
- no silent handoff between materially different workflows
- no unsafe continuation past blocked policy or reliability states
- active routes, retries, and escalations should remain visible in `orchestration_state`
- blocked or review-needed routes should produce explicit queue impacts instead of relying on implicit PM interpretation
