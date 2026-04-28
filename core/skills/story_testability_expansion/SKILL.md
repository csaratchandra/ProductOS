# Story Testability Expansion

## Purpose

Turn story intent into concrete, reviewable acceptance expectations before QA or implementation rely on guesswork.

## Trigger / When To Use

Use when story drafts exist but acceptance criteria or testability notes are too thin to support confident delivery handoff.

## Inputs

- `story_pack`
- source `prd`
- existing acceptance notes or QA concerns

## Outputs

- stronger acceptance criteria
- explicit test methods
- story-level testability notes

## Guardrails

- do not mark criteria testable without explaining how
- avoid vague acceptance language that hides scope
- keep each criterion tied to the originating story and PRD

## Execution Pattern

1. inspect each story for observable behavior or verification gaps
2. add testability notes and criterion-level test methods
3. separate must-pass criteria from lower-priority checks
4. confirm the acceptance set is still bounded to the story

## Validation Expectations

- every criterion should have an explicit test method
- acceptance language should be observable and specific
- QA should not need to infer the verification approach
