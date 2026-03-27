# Manual Validation Lane Workflow

Purpose: Run targeted or mandatory human validation for Tier 2 and Tier 3 outputs so ProductOS adopts only work that is actually usable.

## Inputs

- candidate artifact, readable doc, or presentation package
- `validation_lane_report`
- audience and adoption context for the output
- benchmark context when the output claims improvement

## Outputs

- `manual_validation_record`
- accept / revise / defer / reject decision
- practical fit notes for the next fix loop

## Operating Sequence

1. Confirm the validator role that owns adoption for the output class.
2. Review the output for usefulness, decision quality, communication quality, and practical fit.
3. Record the decision and fit notes in `manual_validation_record`.
4. Name any required follow-ups that must happen before broader adoption or publication.
5. If the manual decision conflicts with AI review or AI test, route the disagreement to referee.

## Rules

- manual validation should speak to real adoption, not just personal taste
- do not convert a manual reject into a soft pass inside summary language
- if the validator approves only for internal use, keep higher-stakes publication blocked until the narrower approval is expanded
