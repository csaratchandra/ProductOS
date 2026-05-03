# Stakeholder Management

## 1. Purpose

Turn stakeholder evidence into an actionable alignment operating package that maps influence, captures objections, prepares decision meetings, and keeps follow-up visible.

## 2. Trigger / When To Use

Use when a PM needs to understand decision power, unblock alignment, prepare for a review, or route stakeholder objections into explicit next actions. Typical triggers:
- `stakeholder_map` does not yet exist for a release-driving initiative
- `alignment_dashboard_state` is stale or missing before a decision meeting
- `objection_playbook` needs to be grounded in fresh stakeholder evidence
- PM requests a structured meeting brief ahead of a launch, roadmap, or release review

## 3. Prerequisites

- Source evidence about stakeholders, decision dynamics, or prior meeting outcomes
- Current strategy, roadmap, or release context for the initiative being aligned
- Named stakeholder scope approved by PM or present in mission context

## 4. Input Specification

| Field | Type | Source | Required | Notes |
|---|---|---|---|---|
| `primary_input` | `object` | Strategy, release, or initiative artifacts | Yes | The decision-driving context being aligned |
| `context` | `array[object]` | Notes, prior artifacts, stakeholder evidence | No | Supporting context for influence and objection analysis |

## 5. Execution Steps

1. Inventory stakeholders: Identify all named decision participants, influencers, blockers, and informed parties for the scoped initiative.
2. Map power and interest: Score each stakeholder on power, interest, and decision influence using direct evidence from prior reviews, ownership, and operating context.
3. Classify alignment posture: Mark each stakeholder as supporter, neutral, detractor, or unknown, and record the reasons with source-backed concerns.
4. Capture relationship dynamics: Note who influences whom, known dependencies, likely veto paths, and sequencing risks for the decision.
5. Build objection inventory: Extract recurring objections, unanswered questions, and approval conditions from notes, review history, and live evidence.
6. Draft the meeting brief: Summarize the decision, meeting objective, required attendees, agenda, likely objections, and decision-ready evidence.
7. Assemble the playbook: For each major objection, define response path, evidence to cite, owner, and unresolved gaps requiring PM judgment.
8. Update alignment state: Produce a current alignment dashboard with stakeholder status, recent contact, open actions, and follow-up priorities.

## 6. Output Specification

- `stakeholder_map` → `core/schemas/artifacts/stakeholder_map.schema.json`
- `meeting_brief` → `core/schemas/artifacts/meeting_brief.schema.json`
- `objection_playbook` → `core/schemas/artifacts/objection_playbook.schema.json`
- `alignment_dashboard_state` → `core/schemas/artifacts/alignment_dashboard_state.schema.json`

## 7. Guardrails

- Do not invent stakeholder influence or support levels without evidence; mark unknown when proof is thin.
- Do not collapse materially different objections into one generic concern; keep the source stakeholder and decision impact visible.
- Escalate to PM when a veto holder is unknown, relationship dynamics are contradictory, or the evidence cannot support a meeting recommendation.

## 8. Gold Standard Checklist

- [ ] Every stakeholder has a named role, power/interest posture, and evidence-backed alignment status
- [ ] Key objections are attributable to a specific stakeholder or stakeholder class
- [ ] Meeting brief states the decision needed, the blockers, and the evidence required to clear them
- [ ] Alignment dashboard makes open actions and last-contact status visible
- [ ] Framework alignment: stakeholder mapping, influence analysis, objection handling, and explicit decision routing

## 9. Examples

See `stakeholder_map.example.json`, `meeting_brief.example.json`, `objection_playbook.example.json`, and `alignment_dashboard_state.example.json` in `core/examples/artifacts/`.

## 10. Cross-References

- **Upstream skills**: `trade_off_analysis`, `decision_tree_construction`, `pricing_analysis_synthesis`
- **Downstream skills**: `health_dashboard_build`, `release_claim_traceability`, `publish_safe_summarization`
- **Schemas**: `stakeholder_map.schema.json`, `meeting_brief.schema.json`, `objection_playbook.schema.json`, `alignment_dashboard_state.schema.json`

## 11. Maturity Band Variations

| Band | Depth |
|---|---|
| 0→1 | Exhaustive: map every active stakeholder and document detailed objection pathways |
| 1→10 | Deep: cover all decision-makers plus primary cross-functional influencers |
| 10→100 | Standard: focus on approval roles, decision bottlenecks, and unresolved objections |
| 100→10K+ | Focused: portfolio-level alignment state with exception-based follow-up |

## 12. Validation Criteria

- **Schema conformance**: stakeholder outputs validate against associated artifact schemas
- **Test file**: `tests/test_v10_stakeholder_management.py`
- **Example fixture**: `stakeholder_map.example.json`, `meeting_brief.example.json`, `objection_playbook.example.json`, `alignment_dashboard_state.example.json`
