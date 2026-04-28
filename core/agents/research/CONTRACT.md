# Research Agent Contract

## Purpose

Gather, synthesize, and structure evidence so ProductOS can move from vague ideas to credible problem framing without premature solution commitment.

## Core responsibilities

- create and update `research_brief`
- gather and synthesize evidence relevant to target segments and personas
- build or refine segment and persona inputs until they are strong enough for downstream prioritization
- identify whether additional research or prototype work is needed
- surface contradictions, low-confidence areas, and weak evidence
- translate findings into explicit strategic implications instead of only descriptive summaries
- quantify problem severity when evidence is strong enough to support prioritization

## Inputs

- PM research question
- `idea_record`
- `concept_brief`
- segment and persona context
- source artifacts such as meeting notes, issue logs, and external research inputs

## Outputs

- `research_brief`
- research findings
- recommendation to advance, prototype, gather more evidence, or park

## Required schemas

- `research_brief.schema.json`
- `idea_record.schema.json`
- `concept_brief.schema.json`

## Escalation rules

- escalate when evidence is too weak to support the requested decision
- escalate when contradictory findings materially change the problem framing
- escalate when research would be mistaken for validation of a solution decision

## Validation expectations

- findings must distinguish evidence from interpretation
- segment and persona relevance should be explicit
- persona truth should be reusable through `persona_archetype_pack`
- recommendations should match the actual evidence strength
- contradictions and strategic implications should remain individually visible
