# Visual Publish Safety

## Purpose

Keep ProductOS visuals publish-safe by enforcing claim boundaries, audience safety, redaction posture, and visible proof treatment before distribution.

## Trigger / When To Use

- when a visual may be shared outside the immediate working team
- when customer-safe and internal-only material risk being mixed
- when publish readiness depends on proof posture or redaction quality

## Inputs

- render contract or output draft
- audience mode and publication mode
- proof items, risk notes, and source visibility rules

## Outputs

- publish-safety assessment
- required redactions or blockers
- explicit recommendation to publish, hold, or bound the claim

## Guardrails

- unsupported certainty must fail publish
- internal-only content must not leak into customer-safe output
- proof gaps must remain visible when they change interpretation

## Execution Pattern

1. confirm target audience and sharing mode
2. check claim posture against visible proof
3. verify redaction and visibility rules
4. confirm the output does not hide material blockers or caveats
5. record publish blockers or bounded-release guidance explicitly

## Validation Expectations

- publish readiness is explicit, not implied
- customer-safe outputs exclude internal-only detail
- proof, risk, and certainty treatment remain visible after adaptation
