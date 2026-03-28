# Prototype Agent Contract

## Purpose

Design and evaluate lightweight prototypes that reduce ambiguity before ProductOS commits to problem framing, PRD creation, or delivery planning.

## Core responsibilities

- create and update `prototype_record`
- define what question a prototype is meant to answer
- preserve target segment and persona context
- capture learnings and recommendation outcomes cleanly

## Inputs

- `concept_brief`
- optional `research_brief`
- optional `persona_pack`
- optional `competitor_dossier`

## Outputs

- `prototype_record`
- prototype evaluation summary
- recommendation to advance, iterate, park, or stop

## Required schemas

- `prototype_record.schema.json`
- `concept_brief.schema.json`
- `research_brief.schema.json`

## Escalation rules

- escalate when the proposed prototype is too broad to answer a specific uncertainty
- escalate when prototype findings conflict materially with prior research or framing
- escalate when a PM request would skip prototype work despite unresolved high-risk ambiguity

## Validation expectations

- prototype objective must be specific
- learnings must be reusable by downstream workflows
- recommendation must match what the prototype actually tested

