# Visual Regression Review

## Purpose

Review generated visual outputs against prior approved patterns and quality expectations so ProductOS does not drift back into weaker design or weaker truthfulness.

## Trigger / When To Use

- when a visual system change could alter hierarchy, fidelity, or publish posture
- when a new pattern is being promoted from trial to standard
- when generated outputs should be compared against approved fixtures or dogfood artifacts

## Inputs

- generated visual output
- prior approved example or review artifact
- quality rubric or review expectations

## Outputs

- regression review summary
- blockers, warnings, and strengths
- recommendation to proceed, revise, defer, or block

## Guardrails

- regression review must check both aesthetics and truthfulness
- do not approve visual polish that weakens evidence visibility
- compare against approved repo fixtures where available

## Execution Pattern

1. identify the baseline fixture or approved sample
2. compare hierarchy, evidence treatment, fidelity, and reading path
3. separate real regressions from neutral stylistic change
4. record blockers and warnings explicitly
5. recommend the next action clearly

## Validation Expectations

- real regressions are named explicitly
- review outcome is decision-ready
- approval is not granted without comparing against a real baseline
