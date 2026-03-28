# Source Ingestion To Note Card Workflow

Purpose: Convert each relevant research source into reusable `source_note_card` artifacts before synthesis.

## Inputs

- normalized workspace evidence bundle
- PM question or tagging context

## Outputs

- one or more `source_note_card` artifacts

## Rules

- every serious research source should become a reusable note card before it becomes a synthesis claim
- preserve source references, claim, implication, confidence, and follow-up questions
- tag the note card with any linked segment, persona, problem, competitor, feature, metric, or decision
- avoid rereading raw files when a prior note card already covers the same source slice
