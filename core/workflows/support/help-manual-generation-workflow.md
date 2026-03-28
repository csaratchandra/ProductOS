# Help Manual Generation Workflow

Purpose: Convert recurring support issues, release changes, and product workflow knowledge into clear help-manual outputs for internal teams or customer-safe support use.

## Inputs

- `issue_log`
- optional `release_note`
- optional `meeting_notes`
- optional source screenshots or workflow explanations

## Outputs

- help manual draft
- internal or customer-safe rendering recommendation
- escalation notes for unsupported or risky guidance

## Rules

- help content should reflect approved product behavior rather than speculative fixes
- resolution steps must be concrete, ordered, and audience-appropriate
- customer-safe outputs must exclude internal-only detail
- if the issue is still unresolved or behavior is unstable, route to support escalation instead of pretending there is a stable manual
