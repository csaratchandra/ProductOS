# Help Manual Generation

## 1. Purpose

Auto-generate structured help manuals from PRD scope, user stories, and prototype specifications — including getting-started guides, feature guides, troubleshooting flows, FAQ, security documentation, and video walkthrough scripts.

## 2. Trigger / When To Use

PRD and stories complete. Launch planning. Support team needs documentation. Customer onboarding requires help content.

## 3. Prerequisites

- Relevant upstream artifacts for the skill domain
- Evidence sources (source note cards, research artifacts, competitive data)
- Defined scope from PM or mission context

## 4. Input Specification

| Field | Type | Source | Required | Notes |
|---|---|---|---|---|
| `primary_input` | `object` | Upstream artifact schemas | Yes | Core input for the skill |
| `context` | `array[object]` | Supporting artifacts | No | Additional context |

## 5. Execution Steps

1. Extract features from PRD: Identify every feature, capability, and workflow described in the PRD.
2. Structure help manual: Getting Started (workspace setup, first run), Core Features (per feature, ordered by user journey), Advanced Usage (power user features), Troubleshooting (common issues + resolution), FAQ, Security & Privacy, Glossary, Release Notes History.
3. Write per-article: Audience (who needs this), Difficulty (beginner/intermediate/advanced), Prerequisites (what you need before this article), Step-by-step instructions (numbered, with screenshot references), Common mistakes, What-next link.
4. Generate FAQ from support patterns: Analyze issue_log for recurring issues. Auto-generate FAQ entry for issues appearing >3 times.
5. Write video walkthrough scripts: Feature-specific scripts with screen-by-screen narration and timing.

## 6. Output Specification

Primary output: `help_manual_pack, prd, issue_log` artifact

## 7. Guardrails

- Article assumes knowledge user doesn't have: Step references a concept not explained earlier → flag. Prerequisites section must cover everything needed.
- Resolution steps are vague: "Check your settings" without saying which settings → fix. Every step must be executable.
- When to escalate: Feature behavior is still unstable — documenting it would be misleading. Flag feature as 'not ready for documentation.'

## 8. Gold Standard Checklist

- [ ] Every article has specified audience and difficulty level
- [ ] Step-by-step instructions are executable (not "do the thing")
- [ ] Prerequisites per article are complete
- [ ] FAQ entries are auto-generated from actual support data
- [ ] Framework: Microsoft Style Guide, Intercom/Stripe documentation standards
- [ ] Framework alignment: Microsoft Style Guide, Intercom/Stripe documentation, technical writing best practices
- [ ] All outputs have explicit evidence traceability

## 9. Examples

See `core/examples/artifacts/` for canonical example artifacts.

## 10. Cross-References

- **Upstream skills**: prd_scope_boundary_check, story_pack, issue_log, prototype_html_generation
- **Downstream skills**: support content, customer onboarding, launch communication
- **Schemas**: help_manual_pack.schema.json, prd.schema.json, issue_log.schema.json

## 11. Maturity Band Variations

| Band | Depth |
|---|---|
| 0→1 | Exhaustive: full depth with qualitative exploration |
| 1→10 | Deep: comprehensive coverage |
| 10→100 | Standard: focused on highest-impact outputs |
| 100→10K+ | Focused: data-driven, portfolio-level |

## 12. Validation Criteria

- **Schema conformance**: validates against associated artifact schemas
- **Test file**: TBD in validation sprint
- **Example fixture**: associated `.example.json` files
