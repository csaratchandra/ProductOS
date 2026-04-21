# Persona Operating Profile Definition Workflow

Purpose: Define and refresh `persona_operating_profile` so ProductOS has explicit authority boundaries, handoff rules, review paths, shared skill composition, and success measures for both PM and AI personas.

## Inputs

- [v4-execution-plan.md](/Users/sarat/Documents/code/ProductOS/core/docs/archive/version-history/v4-execution-plan.md)
- [ai-agent-persona-operating-model.md](/Users/sarat/Documents/code/ProductOS/core/docs/ai-agent-persona-operating-model.md)
- relevant agent contracts and PM operating policies
- `pm_superpower_benchmark`
- validation-tier policy and current workflow matrix

## Outputs

- `persona_operating_profile`
- persona review summary
- recommended contract or policy updates where a persona is underspecified

## Operating Sequence

1. Lock the required PM and AI personas for the current V4 stage.
2. Define each persona's purpose, inputs, outputs, authority boundaries, approval authority, handoff protocol, escalation rules, memory scope, benchmark measures, failure modes, and shared skill refs.
3. Map each persona to the default review path required by validation tier and output class.
4. Link each persona back to its governing contract or policy source and the reusable core skills it should compose.
5. Validate that no AI persona can silently bypass PM approval or mandatory manual validation.
6. Validate that each PM persona owns a distinct approval surface rather than a vague generic PM role.
7. Publish the profile only after AI review, AI test checks, and targeted manual validation confirm the policy is usable in practice.

## Rules

- do not define a generic "AI Agent" persona in place of the specialist stack
- do not treat role count as capability depth; shared skills should carry reusable quality where practical
- keep authority boundaries explicit enough to prevent silent scope or release decisions
- if a role lacks a stable contract, mark the gap and route it into the next bounded slice instead of hiding it
- if a role depends on a reusable capability, point to the relevant `core/skills/*/SKILL.md` rather than relying on implied prompt behavior
- tie benchmark measures to actual golden-loop leverage, not activity volume
- if two personas appear to own the same final approval, escalate and resolve the overlap before adoption
