# AI Review Lane Workflow

Purpose: Run the V4 `AI Reviewer` lane with structured logic, traceability, and audience-fit findings.

## Inputs

- candidate artifact, readable doc, or presentation package
- upstream source refs and workflow context
- applicable benchmark and policy context

## Outputs

- reviewer findings
- proceed / revise / block recommendation
- unresolved questions for downstream lanes

## Operating Sequence

1. Check whether the output makes claims that are traceable to approved evidence.
2. Review framing quality, audience fit, hidden assumptions, and conflicts with prior decisions.
3. Record blocking findings separately from non-blocking findings.
4. State unresolved questions that a tester, manual validator, or PM must answer.
5. Hand the result to `validation-tier-and-lane-review` for inclusion in `validation_lane_report`.

## Rules

- do not merge structural defects into stylistic feedback
- do not approve an output that breaks traceability or hides contradictory evidence
- if the issue is policy or commitment risk rather than editorial quality, name that explicitly for downstream routing
