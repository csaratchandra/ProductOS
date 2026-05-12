# ProductOS Validation Tier Policy

Purpose: Define how ProductOS chooses validation depth for V4 outputs so review cost scales with risk instead of defaulting to either no gate or one universal heavy gate.

Date baseline: March 21, 2026

Dependencies:

- [v4-artifact-workflow-matrix.md](/Users/sarat/Documents/code/ProductOS/core/docs/archive/version-history/v4-artifact-workflow-matrix.md)
- [governance-review-model.md](/Users/sarat/Documents/code/ProductOS/core/docs/governance-review-model.md)
- [testing-strategy.md](/Users/sarat/Documents/code/ProductOS/core/docs/testing-strategy.md)

## Rule

No V4 artifact, readable doc, or presentation should advance based only on existence or schema validity.

Every gated output should:

- declare a validation tier
- run the required lanes for that tier
- emit a `validation_lane_report`
- route disagreement to referee rather than silently merging conclusions

## Tier Definitions

### Tier 0

Use for:

- low-risk internal drafts
- disposable summaries
- preparatory notes that do not drive commitment

Required lanes:

- `AI Reviewer` or lightweight automation

Manual validation:

- not required by default

### Tier 1

Use for:

- normal operating artifacts
- routed internal state
- structured outputs that affect downstream work but do not themselves create a major commitment

Required lanes:

- `AI Reviewer`
- `AI Tester`

Manual validation:

- optional by exception when the workflow matrix says PM sampling is needed

### Tier 2

Use for:

- decision-driving outputs
- stakeholder-facing readable docs
- artifacts that shape scope, roadmap direction, or major operating choices

Required lanes:

- `AI Reviewer`
- `AI Tester`
- targeted or sampled manual validation

Manual validation:

- required unless the workflow matrix explicitly narrows the case to sampled review

### Tier 3

Use for:

- release-driving outputs
- customer-facing communication
- adopted external patterns or presentation grammar
- any output where failure would create trust, policy, or commitment risk

Required lanes:

- full tri-gate

Manual validation:

- always mandatory

## Selection Policy

Choose the tier by asking:

1. does this output change a real decision or commitment
2. could a bad output create customer, launch, policy, or trust damage
3. will a human rely on this output directly rather than only as intermediate machine state
4. is the output adopting a new pattern or new external influence that needs explicit supervision

If the answer is unclear, choose the stricter tier until the ambiguity is resolved.

## Lane Outputs

`AI Reviewer` should emit:

- logic and traceability findings
- proceed / revise / block guidance
- unresolved questions

`AI Tester` should emit:

- structural and regression findings
- pass / revise / fail guidance
- automation gaps that still need manual confirmation

Manual validation should emit:

- accept / revise / defer / reject
- practical fit notes
- final approval where the workflow requires it

Referee should emit:

- the source of disagreement
- tie-break recommendation
- explicit next action

## Escalation Policy

Route to referee when:

- reviewer and tester disagree on proceed versus block
- manual validation rejects an output the AI lanes pass
- the disagreement changes scope, commitment, or publish safety
- one lane claims the issue is structural while another claims it is only editorial

Do not suppress the disagreement inside a vague summary.

## Output Rule

`validation_lane_report` is the stage-level control artifact for V4 lanes.

It should record:

- the artifact under review
- the chosen tier
- lane findings and status
- whether manual validation is required
- whether referee routing is required
- the next action before the artifact may advance
