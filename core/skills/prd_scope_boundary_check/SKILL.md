# PRD Scope Boundary Check

## Purpose

Keep PRD scope bounded to the validated problem and concept so delivery handoff does not quietly expand.

## Trigger / When To Use

Use when drafting or reviewing a `prd`, especially before story generation or release-facing reuse.

## Inputs

- `problem_brief`
- `concept_brief`
- draft `prd`
- linked evidence and target persona context

## Outputs

- scope boundary review
- out-of-scope clarification
- handoff risks for story and acceptance work

## Guardrails

- do not allow hidden feature expansion
- keep out-of-scope items explicit
- preserve the validated persona and prioritization spine

## Execution Pattern

1. compare PRD scope against the problem and concept
2. identify additions that are not justified upstream
3. sharpen scope boundaries and out-of-scope language
4. record the downstream risks if the PRD stays ambiguous

## Validation Expectations

- scope should be traceable upstream
- out-of-scope items should be concrete
- downstream teams should be able to tell what is intentionally excluded
