# Weak Signal Detection

## 1. Purpose

Identify emerging patterns from thin, early-stage evidence before they become obvious trends — enabling proactive strategy by detecting nascent customer needs, competitive moves, market shifts, and technology changes while they are still weak signals, not established facts.

## 2. Trigger / When To Use

- New data arrives in any intelligence feed (customer interviews, support tickets, competitor radar, market reports)
- Scheduled signal landscape scan fires (weekly by default)
- `signal_landscape` artifact staleness exceeds TTL
- PM requests forward-looking signal analysis: `./productos run detect-weak-signals`
- Two or more unrelated sources independently surface the same theme — potential emerging signal

## 3. Prerequisites

- `signal_landscape` artifact with current signal clusters
- Source note cards from at least 3 different signal classes (customer, market, competitor, product, support)
- `research_notebook` or `inbox/` with recent raw inputs
- `freshness_scoring` results to distinguish fresh signals from stale noise

## 4. Input Specification

| Field | Type | Source Artifact/Schema | Required | Example Value | Notes |
|---|---|---|---|---|---|
| `signal_landscape` | `object` | `signal_landscape.schema.json` | Yes | Current signal clusters and watch list | Baseline for detecting new patterns |
| `source_inputs` | `array[object]` | `source_note_card.schema.json` | Yes | Recent source cards from all channels | Min 10 source cards for meaningful analysis |
| `recent_alerts` | `array[object]` | `competitive_intelligence_alert.schema.json`, `radar_alert.schema.json` | No | Alerts from the last 30 days | Cross-reference with existing known signals |

## 5. Execution Steps

1. **Ingest new evidence**: Load all source note cards from inbox created since last signal landscape scan. Group by signal class: customer, market, competitor, product, support, delivery, stakeholder, ecosystem.
2. **Extract thematic fragments**: From each source, extract atomic observations: "3 enterprise prospects independently asked for SSO integration in the last 2 weeks." "Blog post comments show recurring complaint about onboarding complexity." "Hiring data shows 2 adjacent companies posting for roles in our space." Each fragment is a single claim with source ref.
3. **Cluster by theme**: Group thematic fragments by shared topic, need, or concern. Use semantic similarity — fragments don't need identical wording, just shared underlying theme. Minimum cluster size: 2 fragments. Maximum: no limit.
4. **Score signal strength**: Per cluster: occurrence_count (how many sources?), source_diversity (how many different signal classes?), temporal_density (how concentrated in time?), source_quality (expert vs anecdotal), corroboration (independent vs linked sources). Composite: `signal_strength = f(occurrence, diversity, density, quality, corroboration)`.
5. **Classify signal maturity**: Nascent (1-2 mentions, low confidence, first appearance), Emerging (3-4 mentions from 2+ source types, moderate confidence, appears in multiple time windows), Strengthening (5+ mentions from 3+ source types, moderate-high confidence, accelerating frequency), Established (now a trend, should graduate to full research/signal cluster in signal_landscape).
6. **Assess potential impact**: If signal proves true, what changes? Segment affected, strategy options triggered, competitive implications, product roadmap impact. Impact score: 1-5.
7. **Surface as watch-listed signals**: Signals meeting minimum threshold (occurrence >=2, source quality != anecdotal-only) are added to `decision_watchlist` in signal_landscape with: signal description, strength score, maturity classification, potential impact, suggested monitoring frequency, trigger for escalation ("escalate if 2 more independent mentions in 14 days").
8. **Filter noise**: Suppress: one-off mentions (single source, no corroboration within 30 days), contradictory signals (one source says X, another says not-X — surface the contradiction for PM), duplicate signals (already captured in existing signal cluster), seasonal/cyclical patterns (expected, not signals).
9. **Link to hypotheses**: Check if any weak signal aligns with existing untested hypotheses in the `hypothesis_portfolio`. A weak signal that supports a high-impact hypothesis → escalate priority.
10. **Emit signal landscape update**: Updated `signal_landscape` with new weak signal entries, updated watchlist, noise suppression log, escalation recommendations.

## 6. Output Specification

| Field | Type | Schema Reference | Required | Description |
|---|---|---|---|---|
| `signal_landscape` (updated) | `object` | `signal_landscape.schema.json` | Yes | Updated clusters, watchlist, and weak signal entries |
| `weak_signal_report` | `object` | Custom — PM brief | Yes | Top 5 weak signals with strength, impact, and escalation triggers |
| `noise_suppression_log` | `array[object]` | Custom | Yes | Signals suppressed and why |
| `hypothesis_linkages` | `array[object]` | Custom | No | Weak signals linking to existing hypotheses |

## 7. Guardrails

- **Failure condition: Signal is fabricated from thin evidence**: Detection criteria: single source, anecdotal, no corroboration in 14 days → response: suppress as noise. Do not surface. Log suppression reason.
- **Failure condition: Signal is a known pattern (not emerging)**: Detection criteria: matches existing signal cluster or established trend → response: route to existing signal cluster as reinforcement data. Do not create new watch item for known pattern.
- **Failure condition: Confirmation bias — pattern fitting**: Detection criteria: PM has expressed desire for a specific signal to exist; evidence is being stretched to fit that desire → response: flag potential confirmation bias. Require independent corroboration from different source type before surfacing.
- **When to stop and escalate to PM**: A weak signal has high potential impact (score 4-5) but low confidence — potential big opportunity or threat, but thin evidence. PM should decide: invest in gathering more evidence, or dismiss.
- **When output should be marked low-confidence**: All weak signals by definition have lower confidence than established trends. Acceptable — weak signal report carries inherent uncertainty language. Mark specific signals as "very low confidence" if single-source only.
- **When skill should refuse to generate**: No new sources since last scan (nothing to detect). All source note cards are older than 30 days (stale inputs produce stale signals). PM has paused signal detection for this workspace.

## 8. Gold Standard Checklist

- [ ] Every surfaced weak signal has at least 2 independent source refs from different source note cards
- [ ] Signal strength assessment uses objective criteria (occurrence, diversity, density) not subjective judgment
- [ ] For each surfaced signal, the "what would make this stronger" escalation trigger is defined
- [ ] Noise suppression is documented — every suppressed signal has a logged reason
- [ ] Weak signals are linked to existing hypotheses where relevant
- [ ] Signal maturity classification is conservative — default to "nascent" when evidence is thin
- [ ] External framework alignment: validates against Ansoff's weak signal methodology, Igor Ansoff Strategic Management, and Day & Schoemaker peripheral vision framework
- [ ] PM is protected from false positives: weak signal reports explicitly state "these are early-stage patterns, not validated findings"

## 9. Examples

### Excellent Output (5/5)

```json
{
  "weak_signal": {
    "signal_id": "ws_20260503_003",
    "description": "Multiple enterprise PM prospects independently mention need for automated competitive pricing tracking",
    "strength_score": 58,
    "maturity": "emerging",
    "occurrences": 4,
    "source_types": ["customer_interview", "support_ticket", "sales_call"],
    "temporal_density": "3 mentions in last 10 days",
    "potential_impact": 4,
    "impact_description": "If true, validates pricing intelligence as a must-now feature for enterprise segment. Currently scheduled Sprint 7-8 — would confirm priority.",
    "escalation_trigger": "Escalate if 2 more independent mentions within 14 days. Reclassify as established if pattern continues for 30 days.",
    "hypothesis_link": "Links to hypothesis H016: 'Enterprise PMs value pricing intelligence more than startup PMs' — this signal supports the hypothesis."
  }
}
```

### Poor Output (2/5) — What to Avoid

```json
{
  "weak_signal": {
    "description": "AI is getting more popular",
    "strength_score": 90,
    "occurrences": 1,
    "source_types": ["news_article"],
    "potential_impact": 5
  }
}
```

**Why this fails:**
- Single-source signal with a strength score of 90 — impossible; strength requires multiple independent sources
- Signal is too broad to be actionable ("AI is getting more popular")
- No escalation trigger defined
- No link to specific product capabilities or segments
- Inflated potential impact score without segment-level justification

## 10. Cross-References

- **Upstream skills**: `source_discovery`, `source_normalization`, `customer_signal_clustering`, `freshness_scoring`, `signal_priority_scoring`
- **Downstream skills**: `decision_packet_synthesis`, `hypothesis_portfolio_management` (new), `strategy_refresh`, `concept_risk_surfacing`
- **Related entity schemas**: `core/schemas/entities/hypothesis.schema.json`, `core/schemas/entities/opportunity.schema.json`, `core/schemas/entities/problem.schema.json`
- **Related artifact schemas**: `core/schemas/artifacts/signal_landscape.schema.json`, `core/schemas/artifacts/source_note_card.schema.json`, `core/schemas/artifacts/customer_pulse.schema.json`
- **Related workflows**: `core/workflows/research/research-command-center-workflow.md`

## 11. Maturity Band Variations

| Band | Depth Adjustment | Evidence Requirements | Output Expectations |
|---|---|---|---|
| 0→1 | Exhaustive: surface all signals >= 2 mentions. Heavy exploration mode — early product needs to find its signal. | Minimum 2 mentions from different sources. Interview + observation data preferred. | Full weak signal report with impact assessment. New signals auto-routed to hypothesis portfolio. PM reviews all surfaced signals. |
| 1→10 | Deep: surface signals >= 3 mentions or from 2+ source types. | Minimum 3 mentions. Customer + market sources required. | Top 10 weak signals reported. Auto-linked to existing feature prioritization. |
| 10→100 | Standard: surface signals >= 4 mentions. Focus on product + support + competitor classes. | Minimum 4 mentions. Quantitative data preferred over anecdotal. | Top 5 weak signals. Linked to roadmap impact. Noise suppression more aggressive. |
| 100→10K+ | Focused: surface signals >= 5 mentions with clear product impact. Ecosystem + competitor classes prioritized. | Minimum 5 mentions. Data-driven. Market share / revenue impact framing. | Portfolio-level signal view. Individual signal noise suppressed unless linked to measurable metric impact. |

## 12. Validation Criteria

- **Schema conformance**: validates against `core/schemas/artifacts/signal_landscape.schema.json`
- **Test file**: `tests/test_v10_weak_signal_detection.py`
- **Example fixture**: `core/examples/artifacts/signal_landscape.example.json`
- **Skill consistency test**: included in `tests/test_skill_consistency.py` — all 12 elements present and non-empty
