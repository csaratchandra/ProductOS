# Agentic Delivery Burden Estimation

## Purpose

Estimate how much coordination, ambiguity handling, and review overhead a proposed slice creates for agents and humans downstream.

## Trigger / When To Use

Use when prioritization or handoff decisions need to account for delivery burden instead of only customer value.

## Inputs

- problem, concept, PRD, or story artifacts
- implementation context
- known compliance, ambiguity, or integration constraints

## Outputs

- delivery burden classification
- rationale for the burden estimate
- prioritization implications

## Guardrails

- do not hide complexity behind optimistic automation assumptions
- account for review and ambiguity costs, not just build effort
- keep burden estimates comparative and decision-useful

## Execution Pattern

1. inspect the slice for ambiguity, integration work, and review overhead
2. classify the burden as low, medium, or high
3. explain how the burden should affect priority or sequencing
4. flag where burden should block automation until upstream artifacts improve

## Validation Expectations

- burden estimates should reference concrete drivers
- prioritization should change when burden is materially different
- blocked work should explain what must improve upstream
