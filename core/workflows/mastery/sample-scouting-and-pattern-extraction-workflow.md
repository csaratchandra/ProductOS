# Sample Scouting And Pattern Extraction Workflow

Purpose: Capture strong presentation examples, review their patterns, and decide whether ProductOS may adopt them under governed controls.

## Inputs

- candidate internal or external presentation sample
- [presentation-audience-policy.md](/Users/sarat/Documents/code/ProductOS/core/docs/presentation-audience-policy.md)
- [presentation-narrative-quality-checks.md](/Users/sarat/Documents/code/ProductOS/core/docs/presentation-narrative-quality-checks.md)
- current regression fixture set

## Outputs

- `presentation_sample_record`
- `presentation_pattern_review`
- approve / trial / revise / reject recommendation

## Operating Sequence

1. Capture the sample with source provenance, audience context, and why it appears strong.
2. Extract narrative and visual patterns into `presentation_sample_record`.
3. Review the candidate pattern for traceability, licensing, audience fit, and governance risk.
4. Record the decision, extracted rules, regression fixtures, and publish constraints in `presentation_pattern_review`.
5. Require Tier 3 manual validation before wider adoption.

## Rules

- inspiration does not equal approval
- do not import external assets, rhetoric, or layout rules without recording provenance and constraints
- any adopted pattern must have regression fixtures and an explicit publish boundary
