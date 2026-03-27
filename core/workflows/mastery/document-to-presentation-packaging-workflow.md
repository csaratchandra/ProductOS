# Document To Presentation Packaging Workflow

Purpose: Convert approved readable docs and structured artifacts into a governed presentation package for leadership, roadmap, release, or strategy communication.

## Inputs

- approved readable doc or readable-doc bundle
- source artifacts such as `pm_superpower_benchmark`, `document_sync_state`, `outcome_review`, or `release_gate_decision`
- [presentation-audience-policy.md](/Users/sarat/Documents/code/ProductOS/core/docs/presentation-audience-policy.md)
- [presentation-narrative-quality-checks.md](/Users/sarat/Documents/code/ProductOS/core/docs/presentation-narrative-quality-checks.md)
- component presentation runtime and schemas

## Outputs

- `presentation_brief`
- `evidence_pack`
- `presentation_story`
- `render_spec`
- `slide_spec`
- `publish_check`
- `ppt_export_plan`

## Operating Sequence

1. Confirm the target audience, communication mode, and decision stakes.
2. Build `presentation_brief` from the approved docs and source artifacts without inventing unsupported claims.
3. Generate `evidence_pack`, `presentation_story`, `render_spec`, `slide_spec`, `publish_check`, and `ppt_export_plan`.
4. Run Tier 3 validation with `AI Reviewer`, `AI Tester`, and mandatory manual validation.
5. Block publication if publish checks, audience safety, or fidelity controls fail.

## Rules

- do not generate a presentation when a readable doc already solves the communication problem
- keep the presentation package traceable to the same source-of-truth artifacts as the readable docs
- treat audience safety and claim support as blocking controls, not editorial cleanup
