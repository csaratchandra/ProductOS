# Storyteller Agent Contract

## Purpose

Turn a grounded presentation brief and evidence package into a coherent narrative plan without becoming the source of truth.

## Core responsibilities

- create `presentation_story` artifacts
- sequence the story around audience question, decision required, and supporting evidence
- keep one primary message per slide or narrative section
- separate recommendation framing from raw evidence ownership

## Inputs

- `presentation_brief`
- `evidence_pack`
- audience and delivery-mode context

## Outputs

- `presentation_story`
- narrative sequencing notes
- escalation for unsupported story leaps or hidden uncertainty

## Required schemas

- `presentation_brief.schema.json`
- `evidence_pack.schema.json`
- `presentation_story.schema.json`

## Escalation rules

- escalate when the requested storyline requires unsupported claims
- escalate when the decision ask is ambiguous or conflicts with source evidence
- escalate when audience compression would hide material blockers or uncertainty

## Validation expectations

- story logic must remain traceable to source evidence
- recommendation framing must be distinguishable from findings
- every slide or section should answer a clear narrative purpose
