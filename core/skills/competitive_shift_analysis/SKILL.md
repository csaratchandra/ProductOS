# Competitive Shift Analysis

## 1. Purpose

Analyze detected competitive changes against existing product strategy, surface strategic implications, update differentiation claims, and generate prioritized action recommendations — transforming raw intelligence alerts into decision-driving strategic insight.

## 2. Trigger / When To Use

- New `competitive_intelligence_alert` generated with severity >= medium
- Multiple alerts accumulate for the same competitor (3+ within 14 days) — pattern analysis triggered
- Competitive feature matrix staleness exceeds TTL
- PM requests strategic competitive review: `./productos run analyze-competitive-shift --alert-id X`
- Before any strategy refresh or leadership presentation — ensure competitive context is current

## 3. Prerequisites

- At least one `competitive_intelligence_alert` in `new` or `acknowledged` status
- Current `competitive_feature_matrix` artifact
- Current `competitor_dossier` artifact
- Current `strategy_option_set` and `market_strategy_brief` for strategy context
- (Optional) `battle_card` artifacts for affected competitors

## 4. Input Specification

| Field | Type | Source Artifact/Schema | Required | Example Value | Notes |
|---|---|---|---|---|---|
| `intelligence_alerts` | `array[object]` | `competitive_intelligence_alert.schema.json` | Yes | Array of alerts to analyze | Must be same competitor or related set |
| `competitive_feature_matrix` | `object` | `competitive_feature_matrix.schema.json` | Yes | Current feature comparison | Baseline for shift detection |
| `competitor_dossier` | `object` | `competitor_dossier.schema.json` | Yes | Deep competitor context | Provides where_we_win/where_we_lose baseline |
| `strategy_artifacts` | `array[object]` | strategy_option_set, market_strategy_brief | Yes | Current strategy state | Tests if strategy still holds after competitive shift |

## 5. Execution Steps

1. **Aggregate alerts**: Group all alerts by competitor and change type. Identify temporal patterns: single event? sustained activity? accelerating pace?
2. **Compare against baseline**: For each affected capability, compare alert content against current `competitive_feature_matrix` scores. Has the competitor's position changed? Does this flip a `where_we_lead` to `where_we_are_parity` or `where_we_lag`?
3. **Classify shift magnitude**: Minor shift (adequate→strong on non-differentiator), Moderate shift (absent→adequate on differentiator), Major shift (weak→strong on core differentiator), Existential shift (competitor leapfrogs on our primary differentiator with strong evidence).
4. **Test strategy assumptions**: For each assumption in the current strategy option set, check: does this competitive shift invalidate or weaken the assumption? Example: "We have a 12-month lead on PESTLE analysis" → competitor launched basic PESTLE → assumption weakens but holds (their PESTLE is shallow).
5. **Surface strategic implications**: Per shift: what does this mean for our positioning? For our wedge? For our right-to-win? For our roadmap priorities? Frame implications in terms PMs can act on: "Should we accelerate X, defend Y, or reposition Z?"
6. **Update differentiation claims**: Generate updated `differentiation_summary` for the competitive feature matrix. Re-score all affected capabilities. New leader per capability. Updated moat_strength assessment.
7. **Generate gap analysis updates**: New critical gaps, emerging threats, or opportunity windows. Each with: competitor_id, segment_impact, recommended_action, priority.
8. **Produce recommended strategic responses**: 3-5 concrete strategic options: Option A: [Response] with pros/cons/cost/timeline. Option B: [Counter-positioning]. Option C: [Accelerate differentiation]. Option D: [Accept the gap, invest elsewhere]. Option E: [Monitor and learn].
9. **Update downstream artifacts**: Trigger refreshes: `competitive_feature_matrix`, `battle_card` (affected competitors), `strategy_option_set` (if assumptions changed), `market_strategy_brief` (if positioning impacted).
10. **Emit PM decision brief**: Structured summary: what changed, why it matters, what we should do, what happens if we do nothing, recommended action with timeline.

## 6. Output Specification

| Field | Type | Schema Reference | Required | Description |
|---|---|---|---|---|
| `competitive_feature_matrix` (updated) | `object` | `competitive_feature_matrix.schema.json` | Yes | Updated scores, differentiation, gaps |
| `strategic_implication_brief` | `object` | Custom — PM decision brief | Yes | What shifted, implication, recommended actions |
| `refreshed_battle_cards` | `array[string]` | `battle_card.schema.json` | No | List of battle card IDs refreshed |
| `strategy_assumption_impact` | `object` | Custom | Yes | Which strategy assumptions are affected |

## 7. Guardrails

- **Failure condition: Insufficient evidence for shift classification**: Detection criteria: alert confidence is low and no corroborating source exists → response: classify shift as "unconfirmed" and mark for monitoring. Do not trigger downstream artifact updates on unconfirmed shifts.
- **Failure condition: Alert is stale (older than 7 days for high severity, 30 days for medium)**: Detection criteria: alert age exceeds maximum action window → response: skip analysis. Mark alert as `superseded`. Generate fresh radar scan if needed.
- **Failure condition: Shift nullifies a core differentiator but evidence is single-source**: Detection criteria: major/existential shift magnitude with single evidence source → response: flag as high priority for verification. Do not update moat_strength. Generate urgent verification action: "Confirm this by checking competitor documentation and changelog."
- **When to stop and escalate to PM**: Shift magnitude is existential (competitor leapfrogs primary differentiator with strong multi-source evidence). Two or more core differentiators shift from `where_we_lead` to `where_we_lag` simultaneously. Strategy assumptions that underpin the current wedge design are invalidated.
- **When output should be marked low-confidence**: Shift is inferred from hiring signals or patent filings (not confirmed shipped features). Only one surface shows the change, others remain unchanged. Competitor alpha/beta/early access features that may not ship.
- **When skill should refuse to generate**: No strategy artifacts exist (can't assess implications without strategy baseline). Alerts are all informational/low severity with no strategic impact. PM has dismissed all related alerts.

## 8. Gold Standard Checklist

- [ ] Every shift is classified on a concrete scale (minor/moderate/major/existential) with evidence justification
- [ ] Strategy assumption impact is explicit: "We assumed X. This shift changes X to Y. Therefore strategy option Z needs revision."
- [ ] Recommended responses include pros/cons and trade-off analysis, not just "do this"
- [ ] Differentiation claims are evidence-backed — "we lead" must cite what competitor lacks
- [ ] Downstream artifact updates are traceable — each update links back to the specific alert that triggered it
- [ ] External framework alignment: validates against Porter's Five Forces (competitive rivalry analysis), Blue Ocean Strategy (differentiation tracking)
- [ ] "Do nothing" scenario is analyzed: cost of inaction vs cost of response

## 9. Examples

### Excellent Output (5/5)
See `core/examples/artifacts/competitive_feature_matrix.example.json` for the canonical format. Key qualities:
- Specific capability scores with evidence refs
- Clear differentiation summary with leader assignment per feature
- Gap analysis with segment-level impact and priority
- Moat strength with honest assessment

### Poor Output (2/5) — What to Avoid

```json
{
  "shift_classification": "major",
  "implications": "Competitor got better. We need to improve.",
  "recommended_responses": [
    "Build better features",
    "Improve our product"
  ]
}
```

**Why this fails:**
- "Build better features" is a platitude, not a strategic response — which features? in what order? at what cost?
- No capability-level analysis — which specific capabilities shifted?
- No segment impact — which customers does this affect?
- No trade-off analysis — improving features means deprioritizing what?
- No cost of inaction — what happens if we do nothing?

## 10. Cross-References

- **Upstream skills**: `competitive_radar_scan`, `quantitative_competitive_comparison`, `competitive_capability_decomposition`, `right_to_win_assessment`
- **Downstream skills**: `strategy_refresh`, `battle_card_generation`, `roadmap_scenario_generation`, `drift_and_impact_propagation`
- **Related entity schemas**: `core/schemas/entities/feature.schema.json`, `core/schemas/entities/market.schema.json`, `core/schemas/entities/decision.schema.json`
- **Related artifact schemas**: `core/schemas/artifacts/competitive_feature_matrix.schema.json`, `core/schemas/artifacts/competitive_intelligence_alert.schema.json`, `core/schemas/artifacts/strategy_option_set.schema.json`, `core/schemas/artifacts/market_strategy_brief.schema.json`
- **Related workflows**: `core/workflows/decision-intelligence/market-strategy-definition-workflow.md`

## 11. Maturity Band Variations

| Band | Depth Adjustment | Evidence Requirements | Output Expectations |
|---|---|---|---|
| 0→1 | Exhaustive: every shift analyzed for strategy impact. Every alert triggers full shift analysis. | Multi-source evidence required. Strategy assumption testing mandatory for all shifts >= moderate. | Full strategic implication brief with 5 option responses. Premortem on each recommended option. |
| 1→10 | Deep: moderate+ shifts analyzed. Low/informational aggregated for weekly review. | Multi-source for major/existential. Single source OK for moderate with confidence flag. | 3 option responses for major shifts. Battle card auto-updated for all shifts. |
| 10→100 | Standard: major+ shifts analyzed. Moderate aggregated monthly. | Quantitative competitive data prioritized. Automated scoring. | Strategic implications focused on roadmap impact. Feature matrix auto-updated. |
| 100→10K+ | Focused: existential shifts only for deep analysis. Others monitored at portfolio level. | Market data-driven. Competitor moves assessed against market share impact. | Portfolio-level competitive view. Individual competitor shifts de-prioritized below portfolio threats. |

## 12. Validation Criteria

- **Schema conformance**: validates against `core/schemas/artifacts/competitive_feature_matrix.schema.json`, `core/schemas/artifacts/competitive_intelligence_alert.schema.json`
- **Test file**: `tests/test_v10_competitive_shift_analysis.py`
- **Example fixture**: `core/examples/artifacts/competitive_feature_matrix.example.json`
- **Skill consistency test**: included in `tests/test_skill_consistency.py` — all 12 elements present and non-empty
