# Auto-Research Refresh Workflow

Purpose: Continuously refresh discovery context from new workspace signals so research framing stays current without forcing the PM to restart discovery manually.

## Inputs

- normalized workspace evidence bundle
- change events
- current `idea_record`, `concept_brief`, or `research_brief`
- issue and meeting signals

## Outputs

- refreshed evidence summary
- recommendation to update research, prototype, or status workflows
- contradiction and freshness warnings

## Rules

- separate genuinely new evidence from previously summarized context
- call out materially changed assumptions, risks, and contradictions
- do not auto-advance to new commitments from weak signals alone
- preserve traceability back to the refreshed evidence sources
