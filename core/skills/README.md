# Core Skills

Purpose: Define reusable capability building blocks that ProductOS personas, agents, and workflows can compose instead of re-describing the same behavior in many places.

## Why This Exists

ProductOS already has a broad contract catalog in `core/agents/`.

That catalog is useful for authority boundaries and review posture.

It is not sufficient as the main source of task quality.

The shared skill layer exists so important capabilities are:

- defined once
- reviewed once
- improved once
- reused by many personas and workflows

## Structure

Each skill lives at:

- `core/skills/<skill_name>/SKILL.md`

Each skill document should use this section order:

1. `Purpose`
2. `Trigger / When To Use`
3. `Inputs`
4. `Outputs`
5. `Guardrails`
6. `Execution Pattern`
7. `Validation Expectations`

## Initial Skill Set

- `source_discovery`
- `source_normalization`
- `source_ranking`
- `freshness_scoring`
- `contradiction_detection`
- `evidence_extraction`
- `retrieval_selection`
- `strategy_refresh`
- `decision_packet_synthesis`
- `publish_safe_summarization`

## Rules

- skills should be capability-oriented, not persona-oriented
- skills should stay reusable across multiple workflows where practical
- skills should preserve evidence, review, and claim-boundary discipline
- if a behavior is only implied by a persona contract and is reused elsewhere, promote it into a skill
