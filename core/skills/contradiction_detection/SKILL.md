# Contradiction Detection

## Purpose

Detect materially conflicting evidence so ProductOS does not flatten disagreement into false certainty.

## Trigger / When To Use

Use when multiple sources or recommendations bear on the same question and could support conflicting conclusions.

## Inputs

- normalized sources
- question or topic grouping
- extracted evidence statements

## Outputs

- contradiction items
- review-required summary
- supporting source references

## Guardrails

- do not suppress contradictions for narrative neatness
- do not invent contradictions where sources simply differ in detail
- do not let contradiction handling replace PM judgment

## Execution Pattern

- group evidence by topic
- compare directional claims
- record material conflicts
- route unresolved contradiction states into review

## Validation Expectations

- contradiction items should cite the specific supporting sources
- review-required states should stay explicit
- downstream summaries should preserve contradiction visibility
