# Market Trend Extrapolation

## 1. Purpose

Project current market trends forward with confidence bands and scenario modeling — enabling PMs to make timing-sensitive decisions by understanding not just what is happening now, but where the market is heading in 6, 12, and 24 months with explicit uncertainty quantification.

## 2. Trigger / When To Use

- Market data refresh detected (new market report, updated analyst estimates, regulatory change)
- PESTLE factor shows significant movement (inflation shift, technology adoption inflection, new regulation)
- PM requests forward-looking analysis before strategy review or roadmap planning
- `market_sizing_brief` or `market_analysis_brief` staleness exceeds TTL
- Competitive shift detected that may indicate broader market movement, not just single-competitor action

## 3. Prerequisites

- Current `market_analysis_brief` or `market_sizing_brief` with historical data points
- Current `pestle_analysis` for environmental factors affecting market trajectory
- Source note cards with market data (analyst reports, industry data, economic indicators)
- `competitive_feature_matrix` for understanding competitive shifts that may signal market changes
- (Recommended) At least 3 time-series data points for meaningful extrapolation

## 4. Input Specification

| Field | Type | Source Artifact/Schema | Required | Example Value | Notes |
|---|---|---|---|---|---|
| `market_data` | `object` | `market_sizing_brief.schema.json`, `market_analysis_brief.schema.json` | Yes | Current market artifacts with historical data | Must have temporal dimension |
| `pestle_context` | `object` | `pestle_analysis.schema.json` | Yes | Current PESTLE with trend directions | Environmental factors constrain extrapolation |
| `competitive_context` | `object` | `competitive_feature_matrix.schema.json` | No | Current competitive landscape | Competitive shifts may accelerate/decelerate trends |
| `regulatory_context` | `object` | `regulatory_change_tracker.schema.json` | No | Pending regulations | Regulatory changes can abruptly alter trajectories |

## 5. Execution Steps

1. **Extract baseline data**: From market artifacts, collect all time-series data points. Identify trend direction, growth rate, acceleration/deceleration. Note data gaps and interpolation assumptions.
2. **Decompose trend into drivers**: Identify underlying forces driving the trend: Technology adoption rate? Regulatory tailwinds? Customer behavior shift? Economic conditions? Competitive dynamics? For each driver, assess current state and likely trajectory.
3. **Build trend projection models**: Apply appropriate method: Linear extrapolation (steady growth, high confidence in past pattern continuing), Exponential (compound growth, network effects, viral adoption), S-curve (technology adoption lifecycle, approach to saturation), Regression (multi-factor correlation with driver variables).
4. **Generate 3 scenarios**: Optimistic (all drivers accelerate — compound tailwinds), Expected (baseline extrapolation from current trend line), Pessimistic (key drivers stall or reverse, regulatory headwinds materialize, competitor captures disproportionate share). Each scenario includes: quantitative projection, qualitative narrative, driver assumptions, confidence band.
5. **Calculate confidence bands**: Per scenario: what is the range of likely outcomes? Confidence intervals: 80% (likely range), 50% (central estimate), 20% (tail risk). Document: "We are 80% confident the market will be between $X and $Y in 2026."
6. **Identify inflection points**: What could change the trajectory? Technology breakthrough, regulatory cliff, competitor acquisition, platform shift, economic shock. Per inflection point: trigger condition, probability within timeframe, impact on projection if triggered.
7. **Map to product implications**: If trend projections hold: what features become more/less important? Which segments grow/shrink? Does our beachhead remain the right beachhead? Timing: are we too early, on time, or too late for this market wave?
8. **Generate scenario comparison**: Visual: 3 lines on shared chart with confidence bands shaded. Table: per scenario, what changes for our product strategy? Key differences between scenarios that PM should action on.
9. **Recommend market posture**: Based on projections: invest heavily (strong tailwinds, we lead), invest selectively (moderate growth, specific niches), maintain (steady state), harvest (market plateauing, shift resources), divest (declining, our position weak).
10. **Set review triggers**: "Revisit this projection: if actual market growth deviates >20% from expected scenario, or if inflection point X triggers." Set artefact staleness TTL based on market volatility — high volatility = shorter TTL.

## 6. Output Specification

| Field | Type | Schema Reference | Required | Description |
|---|---|---|---|---|
| `market_trend_projection` | `object` | Custom — trend extrapolation artifact | Yes | 3 scenarios with quantitative data, narratives, confidence bands |
| `inflection_point_analysis` | `array[object]` | Custom | Yes | Potential trajectory-changing events with probabilities |
| `product_implication_map` | `object` | Custom | Yes | How each scenario affects product strategy, features, segments |
| `recommended_market_posture` | `object` | Custom | Yes | Invest/maintain/harvest/divest recommendation with rationale |
| `updated_market_sizing` | `object` | `market_sizing_brief.schema.json` | No | Updated TAM/SAM/SOM with projection-informed estimates |

## 7. Guardrails

- **Failure condition: Extrapolating from insufficient data points**: Detection criteria: fewer than 3 time-series data points for the trend being projected → response: mark projection as "speculative" with explicit warning. Do not present as predictive analysis. Recommend gathering more data before trusting projections.
- **Failure condition: Recent anomaly distorting trend**: Detection criteria: last data point is >2 standard deviations from trend line. Is this a new trajectory or a one-off? → response: generate two projections — one including the anomaly (new trajectory hypothesis) and one excluding it (noise hypothesis). Let PM decide which to trust.
- **Failure condition: Extrapolation horizon too aggressive**: Detection criteria: projection period > 3× the historical data period → response: widen confidence bands significantly. Mark long-horizon projections as "speculative" with increasing uncertainty language ("beyond 12 months, confidence decreases materially").
- **When to stop and escalate to PM**: All three scenarios point to negative outcome (market decline, regulatory block, competitive capture). Data is too sparse for any meaningful projection — PM needs to invest in gathering more data before extrapolation can be useful.
- **When output should be marked low-confidence**: Historical data has high variance (R² < 0.5). Key drivers are themselves uncertain (pending regulation with unknown outcome, technology at early adoption curve). Single-source market data without analyst corroboration.
- **When skill should refuse to generate**: No market data available at all. PESTLE analysis is >180 days stale — environmental context too outdated. PM has explicitly marked market analysis as "parked" for this workspace.

## 8. Gold Standard Checklist

- [ ] All 3 scenarios have quantitative projections, not just qualitative "optimistic/pessimistic" labels
- [ ] Confidence bands are explicit and grounded in data variance, not gut feel
- [ ] Historical data sources are cited for every data point used in projections
- [ ] Inflection points are specific and actionable ("if regulation X passes" not "if something changes")
- [ ] Product implications are mapped to specific features, segments, and roadmap items
- [ ] Review triggers are set with concrete numerical thresholds
- [ ] Extrapolation methodology is transparent (linear, exponential, S-curve, etc.) with justification for choice
- [ ] External framework alignment: validates against scenario planning (Shell methodology), technology adoption lifecycle (Geoffrey Moore), Porter's industry analysis, McKinsey horizon planning
- [ ] "Unknown unknowns" are acknowledged — "events not captured in any scenario remain a possibility"

## 9. Examples

### Excellent Output (5/5)

```json
{
  "trend": "AI Agent Tooling Market Growth",
  "baseline": {
    "historical_cagr": "41% (2023-2025)",
    "current_market_size": "$2.8B",
    "data_points": 12
  },
  "scenarios": {
    "optimistic": {
      "projection_12m": "$4.8B",
      "projection_24m": "$7.6B",
      "cagr": "48%",
      "drivers": "Enterprise adoption accelerates. LLM costs continue declining. AI agent orchestration becomes standard PM practice.",
      "confidence_80pct_range": "$4.2B - $5.4B"
    },
    "expected": {
      "projection_12m": "$4.0B",
      "projection_24m": "$5.5B",
      "cagr": "35%",
      "drivers": "Steady adoption. PMs adopt AI-assisted workflows. Some enterprise resistance to autonomous features.",
      "confidence_80pct_range": "$3.6B - $4.4B"
    },
    "pessimistic": {
      "projection_12m": "$3.2B",
      "projection_24m": "$3.8B",
      "cagr": "15%",
      "drivers": "Regulation restricts autonomous AI features. LLM cost increases. Incumbent PM tools add basic AI without switching cost for users.",
      "confidence_80pct_range": "$2.9B - $3.5B"
    }
  },
  "methodology": "Exponential extrapolation with S-curve saturation factor applied at 24-month horizon. Regression against LLM API cost trends and enterprise PM tooling spend data.",
  "review_trigger": "Revisit projections if: actual market growth deviates >25% from expected scenario for 2 consecutive quarters, or if EU AI Act restricts autonomous decision intelligence features materially."
}
```

### Poor Output (2/5) — What to Avoid

```json
{
  "projection": "Market will grow a lot. AI is transformative.",
  "confidence": "high confidence",
  "recommendation": "Invest more."
}
```

**Why this fails:**
- No quantitative projections — "grow a lot" is not a number a PM can plan against
- "High confidence" with no methodology or data basis is unjustified
- No confidence bands — PM can't assess risk
- No scenarios — single-point prediction ignores uncertainty
- No product implications — "invest more" in what? which features? which segments?
- No review triggers — projection becomes stale immediately

## 10. Cross-References

- **Upstream skills**: `market_sizing_reasoning_check`, `market_framework_synthesis`, `pestle_synthesis` (new), `competitive_shift_analysis` (new)
- **Downstream skills**: `strategy_refresh`, `roadmap_scenario_generation` (new), `pricing_model_design` (new), `investor_content_generation` (new)
- **Related entity schemas**: `core/schemas/entities/market.schema.json`, `core/schemas/entities/metric.schema.json`
- **Related artifact schemas**: `core/schemas/artifacts/market_sizing_brief.schema.json`, `core/schemas/artifacts/market_analysis_brief.schema.json`, `core/schemas/artifacts/pestle_analysis.schema.json`, `core/schemas/artifacts/regulatory_change_tracker.schema.json`
- **Related workflows**: `core/workflows/research/research-command-center-workflow.md`, `core/workflows/decision-intelligence/market-strategy-definition-workflow.md`

## 11. Maturity Band Variations

| Band | Depth Adjustment | Evidence Requirements | Output Expectations |
|---|---|---|---|
| 0→1 | Exhaustive: full 3-scenario model with inflections. Heavy qualitative narrative — early market has less data, more uncertainty. | Minimum 3 data points. Allow analyst estimates when historical data is thin. Qualitative driver analysis required. | Full projection with explicit "we have limited data" caveat. Recommended posture: invest selectively, gather data. |
| 1→10 | Deep: 3-scenario model. Quantitative projections with confidence bands. Inflection point analysis. | Minimum 5 data points. Mix of historical data + analyst estimates. | Projections feed directly into roadmap timing and feature prioritization. |
| 10→100 | Standard: 3-scenario model. Quantitative focus. Inflection points at macro level. | Minimum 8 data points. Historical data + market reports. Statistical rigor increased. | Projections inform capacity planning and investment allocation across features. |
| 100→10K+ | Focused: 2-scenario model (expected + pessimistic). Quantitative with statistical rigor. Portfolio-level trends. | Minimum 12 data points. Historical data only. No speculative estimates. Statistical models (ARIMA, regression). | Projections feed portfolio investment decisions. Individual product trends consolidated. |

## 12. Validation Criteria

- **Schema conformance**: validates against `core/schemas/artifacts/market_sizing_brief.schema.json`, `core/schemas/artifacts/pestle_analysis.schema.json`
- **Test file**: `tests/test_v10_market_trend_extrapolation.py`
- **Example fixture**: `core/examples/artifacts/market_sizing_brief.example.json`, `core/examples/artifacts/pestle_analysis.schema.json`
- **Skill consistency test**: included in `tests/test_skill_consistency.py` — all 12 elements present and non-empty
