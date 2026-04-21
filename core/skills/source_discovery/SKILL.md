# Source Discovery

## Purpose

Find candidate sources across bounded external and internal surfaces for a research question or operating task.

## Trigger / When To Use

Use when ProductOS needs candidate market, competitor, customer, operator, or internal context sources before synthesis begins.

## Inputs

- research question or operating question
- source-type expectation
- bounded search scope or feed scope
- existing canonical source context when available

## Outputs

- candidate source list
- source coverage summary
- search-status summary

## Guardrails

- do not treat discovery as validation
- do not hide empty, partial, or no-result states
- do not broaden into unrestricted source intake without an explicit scope

## Execution Pattern

- generate bounded queries or feed matches
- collect candidate sources
- deduplicate obvious repeats
- record coverage and discovery status

## Validation Expectations

- the resulting candidate set should map back to the triggering questions
- no-results and partial-coverage states should remain explicit
- candidate source provenance should stay visible
