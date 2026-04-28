# Persona Evidence Synthesis

## Purpose

Turn scattered persona observations into a canonical archetype packet that downstream artifacts can reuse without reinterpretation.

## Trigger / When To Use

Use when persona notes, interviews, or source artifacts exist but the persona truth is too loose for problem, concept, PRD, or story work.

## Inputs

- persona notes or `persona_pack`
- source evidence about goals, pains, blockers, and workflow traits
- linked segments and buying context

## Outputs

- `persona_archetype_pack`
- evidence-backed archetype priorities
- handoff preferences for downstream execution artifacts

## Guardrails

- keep one canonical upstream truth instead of duplicating conflicting persona summaries
- preserve evidence refs for each archetype
- do not invent buying influence or blockers without support

## Execution Pattern

1. group evidence by persona and archetype role
2. synthesize goals, pains, triggers, blockers, and workflow traits
3. prioritize the archetypes that matter most for the current wedge
4. record handoff preferences that downstream artifacts must preserve

## Validation Expectations

- each archetype should have clear evidence support
- priority differences should be explainable
- downstream teams should be able to reuse the pack without reopening raw notes
