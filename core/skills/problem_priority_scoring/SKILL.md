# Problem Priority Scoring

## Purpose

Rank problems so ProductOS can explain why one problem deserves the next bounded slice.

## Trigger / When To Use

Use when multiple candidate problems exist or when a problem brief needs explicit priority logic.

## Inputs

- problem briefs
- severity and evidence data
- market and customer context

## Outputs

- ranked problem set
- rationale and burden notes
- recommended next problem

## Guardrails

- do not rank by intuition alone
- keep severity and evidence separate
- preserve burden and ambiguity tradeoffs

## Execution Pattern

1. score pain, frequency, leverage, and proof fit
2. compare burden and ambiguity explicitly
3. choose the next problem with rationale
4. note what evidence could rerank the set

## Validation Expectations

- the ranking should be legible
- burden should affect the order
- rerank conditions should be explicit
