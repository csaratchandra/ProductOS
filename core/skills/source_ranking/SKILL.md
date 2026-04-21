# Source Ranking

## Purpose

Rank candidate or normalized sources so ProductOS can prioritize stronger evidence without pretending weak sources are equivalent.

## Trigger / When To Use

Use when multiple candidate sources exist for one question or when source selection must stay explainable.

## Inputs

- research question
- candidate or normalized sources
- source-type expectations

## Outputs

- ranked source list
- selection rationale
- weaker alternate list

## Guardrails

- do not hide ranking rationale
- do not equate source presence with source quality
- do not allow a single weak source to imply broad confidence

## Execution Pattern

- compare question overlap
- factor domain and source-type quality
- score candidates
- preserve accepted and alternate ordering

## Validation Expectations

- top-ranked sources should be explainable
- ranking signals should remain reviewable by a PM
- weaker sources should remain visible as alternates when useful
