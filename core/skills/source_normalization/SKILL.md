# Source Normalization

## Purpose

Turn raw source payloads into comparable, reusable normalized records.

## Trigger / When To Use

Use after source discovery or manifest selection when raw source content must become structured evidence.

## Inputs

- selected source URIs or files
- source metadata
- generated-at timestamp

## Outputs

- normalized source records
- extracted titles, summaries, and freshness metadata
- reusable sentence or excerpt structure

## Guardrails

- do not collapse raw content into one opaque summary
- do not lose source type, publication timing, or source identity
- do not merge internal and external evidence into one trust label

## Execution Pattern

- fetch or load source content
- extract metadata and text
- create normalized source entries
- preserve freshness and source-type fields

## Validation Expectations

- normalized records should retain source identity and timing
- summaries should remain traceable to the original source
- malformed or unreadable inputs should surface as explicit failures or review-needed states
