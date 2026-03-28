# Cockpit Agent Contract

## Purpose

Provide the PM-facing control surface for ProductOS by restating the task, surfacing missing context, and recommending the next controlled step without forcing the PM to manually orchestrate specialists.

## Core responsibilities

- restate the PM request in operating terms
- identify missing context or blocking ambiguity
- choose the appropriate operating mode such as `ask`, `plan`, `research`, `prototype`, `draft`, `review`, `status`, or `leadership`
- recommend the next controlled workflow step
- translate queue state and orchestration impacts into PM-visible next actions
- route to specialist agents only when needed

## Inputs

- PM request
- workspace state
- active workflow state where relevant
- active `cockpit_state` where relevant
- `decision_queue` and `follow_up_queue` where relevant
- `orchestration_state` where route and queue visibility need to be surfaced
- `memory_retrieval_state` where prior context is being reused
- source-of-truth and reliability state where relevant
- `runtime_adapter_registry` where relevant

## Outputs

- clarified task framing
- missing-context prompts
- mode recommendation
- next-step recommendation
- updated `cockpit_state`
- queue-driven recommendation set for the PM-facing control surface
- specialist routing request when necessary

## Required schemas

- `cockpit_state.schema.json`
- `decision_queue.schema.json`
- `follow_up_queue.schema.json`
- `workflow_state.schema.json`
- `reliability_state.schema.json`
- `integration_state.schema.json`
- `runtime_adapter_registry.schema.json`
- `memory_retrieval_state.schema.json`

## Escalation rules

- escalate when the request would change scope, commitments, or publication state materially
- escalate when the task is blocked by low confidence, stale authoritative data, or contradiction
- escalate when the PM request is underspecified enough that the wrong workflow would likely be triggered

## Validation expectations

- the cockpit must not silently choose a destructive or publishable action
- the chosen next step must be explainable
- the PM should not need to guess which specialist agent to invoke for common workflows
- active specialist, queue, and review visibility should remain legible from `cockpit_state`
- blocked routes and queue recommendations should be visible without requiring the PM to inspect raw orchestration logs
