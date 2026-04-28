# Launch Priority Reasoning

## Purpose

Turn launch-readiness findings into explicit go, watch, and block decisions.

## Trigger / When To Use

Use when `release_readiness` needs more than a checklist and must explain why the launch posture is what it is.

## Inputs

- readiness checks
- release claims
- support and validation evidence

## Outputs

- decision summary
- claim-readiness posture
- blocking evidence refs

## Guardrails

- do not treat passed checks as proof of safe claims automatically
- keep bounded claims separate from verified claims
- surface blockers directly

## Execution Pattern

1. inspect the claims being made
2. classify each as verified, bounded, or blocked
3. summarize the decision in one release-ready paragraph
4. attach the evidence refs behind the decision

## Validation Expectations

- the decision summary should be readable quickly
- claim-readiness should match the evidence
- blockers should be concrete
