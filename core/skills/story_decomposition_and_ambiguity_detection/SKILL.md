# Story Decomposition And Ambiguity Detection

## Purpose

Break a bounded PRD slice into implementable stories while surfacing ambiguity before engineering or QA inherit it.

## Trigger / When To Use

Use when converting a `prd` into a `story_pack` or when story drafts feel broad, merged, or hard to test.

## Inputs

- `prd`
- linked persona and segment context
- existing delivery constraints or implementation notes

## Outputs

- decomposed stories
- ambiguity notes
- delivery burden summary

## Guardrails

- do not merge unrelated work into one story
- keep each story inside PRD scope
- preserve the blocked versus review-needed distinction when ambiguity remains

## Execution Pattern

1. identify the smallest coherent delivery slices in the PRD
2. split user-facing, enabling, and risk-reduction work where needed
3. write explicit ambiguity notes for missing decisions or vague language
4. summarize the delivery burden that the story pack now creates

## Validation Expectations

- stories should be smaller and clearer than the source PRD
- ambiguity should be explicit and actionable
- downstream teams should know what still requires review
