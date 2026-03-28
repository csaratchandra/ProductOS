# App Review And Social Mining Workflow

Purpose: Turn app reviews and social commentary into structured note cards and customer signal summaries without overstating confidence.

## Inputs

- app store reviews
- social commentary summaries
- optional customer interview artifacts

## Outputs

- `source_note_card`
- optional `customer_pulse` input package
- recommendation to update `research_brief` or `customer_pulse`

## Rules

- distinguish raw single-source complaints from cross-source supported pain points
- preserve representative customer language where it clarifies the real problem
- separate sentiment, request, and underlying pain where possible
- do not promote review mining into a broad market claim without corroboration
