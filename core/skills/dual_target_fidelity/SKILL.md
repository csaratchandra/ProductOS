# Dual Target Fidelity

## Purpose

Keep ProductOS visual outputs coherent across HTML and PPT targets without pretending that every composition can map perfectly.

## Trigger / When To Use

- when a visual surface targets both HTML and PPT
- when a design uses richer HTML behavior that might need a PPT-safe fallback
- when fidelity tradeoffs could affect meaning or reading path

## Inputs

- visual direction plan
- render model or render spec
- target formats
- known renderer constraints

## Outputs

- fidelity assessment
- fallback recommendation
- blocker or warning when a composition cannot hold meaning across targets

## Guardrails

- fidelity tradeoffs must stay explicit
- do not silently degrade meaning in PPT export
- prefer a simpler accurate fallback over a flashy misleading translation

## Execution Pattern

1. identify the target formats and required parity level
2. inspect the planned composition for target-specific risk
3. define fallback behavior where needed
4. mark aligned, partial, or at-risk fidelity explicitly
5. block export when the reading path would materially degrade

## Validation Expectations

- fidelity status is explicit
- fallbacks preserve meaning
- blocked cases are recorded instead of silently shipped
