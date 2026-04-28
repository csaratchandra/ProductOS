# Market Sizing Reasoning Check

## Purpose

Stress-test TAM, SAM, and SOM reasoning so sizing is explicit, reviewable, and bounded.

## Trigger / When To Use

Use when `market_sizing_brief` claims could materially influence prioritization or release posture.

## Inputs

- market sizing draft
- formulas, assumptions, and source refs
- current segment and wedge definition

## Outputs

- tightened formula path
- clearer confidence and sensitivity notes
- identified assumption risks

## Guardrails

- do not present proxy math as observed truth
- separate bottom-up from top-down reasoning
- flag any sizing logic that assumes future adoption without evidence

## Execution Pattern

1. inspect each estimate and formula path
2. test whether the assumptions match the current wedge
3. identify the assumptions that move the result most
4. rewrite confidence and sensitivity notes accordingly

## Validation Expectations

- each estimate should have a readable formula
- the key assumptions should be obvious
- confidence should match the evidence quality
