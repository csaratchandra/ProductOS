# Evidence Extraction

## Purpose

Pull the most relevant supporting excerpts or claims from source material for a bounded question.

## Trigger / When To Use

Use when ProductOS needs reusable evidence, not just full-source retention or generic summaries.

## Inputs

- research question or decision question
- normalized source content
- fallback snippet or summary

## Outputs

- evidence excerpts
- supporting claim summaries
- source-linked note-card inputs

## Guardrails

- do not quote or summarize large bodies without relevance filtering
- do not treat question-echo text as strong evidence
- do not detach evidence from the source that supports it

## Execution Pattern

- score candidate sentences or excerpts for question overlap
- prefer non-echo evidence
- clip to reusable evidence spans
- preserve source linkage

## Validation Expectations

- extracted evidence should answer the triggering question materially better than the fallback snippet
- evidence should remain source-linked
- low-signal extraction should stay visible as weak evidence, not strong proof
