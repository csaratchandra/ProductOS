# Problem Severity Quantification

## Purpose

Make problem urgency explicit so downstream prioritization and gating decisions do not rely on vague qualitative language.

## Trigger / When To Use

Use when a `problem_brief` exists but severity, urgency, or evidence strength are not explicit enough to justify prioritization.

## Inputs

- draft `problem_brief`
- segment and persona context
- evidence about pain frequency, impact, and trust gaps

## Outputs

- quantified problem severity summary
- priority rationale for the problem
- explicit handoff readiness recommendation

## Guardrails

- do not convert weak evidence into false precision
- keep severity rationale grounded in actual workflow pain and evidence strength
- block downstream claims when severity is still speculative

## Execution Pattern

1. identify the pain frequency and user impact
2. classify evidence strength and current uncertainty
3. translate severity into a priority lane and downstream recommendation
4. state what would still block PRD or story work

## Validation Expectations

- severity should be traceable to evidence
- the priority lane should match the stated severity
- blocking gaps should remain visible
