# PESTLE Synthesis

## 1. Purpose

Synthesize political, economic, social, technological, legal, and environmental factors into a scored PESTLE analysis with per-factor impact assessment, trend projections across 6/12/24-month horizons, factor interconnections map, geographic variations, scenario projections, and strategy implications — all evidence-backed with source references.

## 2. Trigger / When To Use

- Discovery phase begins for a new product or market entry
- PESTLE analysis freshness exceeds TTL (default: 90 days)
- PM requests environmental analysis: `./productos run analyze-pestle --market "X"`
- Significant macroeconomic event detected (inflation shift, regulatory change, trade policy update, technology breakthrough)
- Competitive intelligence or regulatory tracker detects material change that may have PESTLE-wide implications

## 3. Prerequisites

- Market definition (`market_definition` or `market_name` from `market_analysis_brief`)
- Geographic scope defined (at minimum: home market)
- Source note cards covering at least 3 of the 6 PESTLE factors
- `competitor_dossier` for competitive context informing technological and economic factors
- `regulatory_change_tracker` (if available) for legal/political factor completeness
- (Recommended) `market_sizing_brief` for economic factor depth
- (Recommended) `customer_pulse` for social factor depth

## 4. Input Specification

| Field | Type | Source Artifact/Schema | Required | Example Value | Notes |
|---|---|---|---|---|---|
| `market_name` | `string` | market_analysis_brief, mission_brief | Yes | `"AI-Powered PM Tooling"` | Scope of PESTLE analysis |
| `geographic_scope` | `array[string]` | Market strategy brief, PM input | Yes | `["Global", "US", "EU"]` | Regions to analyze |
| `source_note_cards` | `array[object]` | `source_note_card.schema.json` | Yes | Research, reports, regulatory docs | Min 3 factors covered |
| `research_context` | `object` | `research_brief.schema.json`, `research_notebook.schema.json` | No | Contextual framing | Research questions and hypotheses |
| `competitive_context` | `object` | `competitor_dossier.schema.json` | No | Competitive landscape | Informs tech and market dynamics |

## 5. Execution Steps

1. **Scope the analysis**: Confirm market boundaries and geographic scope. Identify which regions require separate variation analysis (different regulatory, economic, or social conditions). Flag any region where data is insufficient for meaningful analysis.
2. **Gather factor evidence**: For each of the 6 factors, collect all relevant source note cards, market reports, regulatory documents, and research findings. Tag each source with the factor(s) it informs. Identify evidence gaps.
3. **Synthesize per-factor findings**: For each factor, extract 2-4 key observations. Each observation must be: specific (references concrete data, regulation, or event), significant (classified as critical/major/moderate/minor), and sourced (references a specific source_note_card or artifact).
4. **Score impact**: Per factor, assign impact_score (1-10) based on: magnitude of effect on the product/market, irreversibility, and cascading potential. Document rationale.
5. **Assess trends**: Per factor: trend_direction (improving/stable/deteriorating/volatile), trend_velocity (accelerating/steady/decelerating/uncertain), confidence (high/moderate/low). Ground in evidence trajectory, not speculation.
6. **Generate timeline projections**: Per factor, write 6-month, 12-month, and 24-month projections. Extrapolate from current trends. Acknowledge uncertainty increasing with horizon. Do not present projections as predictions — frame as "most likely trajectory given current evidence."
7. **Map factor interconnections**: Identify pairs of factors that interact. Classify relationship: mutually_reinforcing (both move in same direction, amplifying effect), counterbalancing (one offsets the other), causally_linked (factor A drives factor B), correlated (move together but causation unclear). Minimum 4 interconnections. Rate strength: strong/moderate/weak.
8. **Identify risks and opportunities**: Per factor, extract specific risks (threats to product strategy) and opportunities (favorable conditions to exploit). Each item must link to at least one finding.
9. **Model geographic variations**: For each region beyond home market, identify which factors differ materially. Assess whether the region is higher_risk, similar_risk, or lower_risk than the baseline. Justify with evidence.
10. **Build scenario projections**: Generate 2-3 distinct future scenarios based on different factor trajectories. Each scenario: name, likelihood (likely/possible/unlikely), trigger conditions, pestle_impact description, strategic_implication. Scenarios must be materially different outcomes, not variations on the same theme.
11. **Calculate composite risk score**: Weighted average of factor impact scores, adjusted for interconnection amplification and confidence. Scale: 1-100. Justify weighting.
12. **Surface key strategic implications**: 5-7 actionable implications a PM can directly use. Each must reference specific factors or interconnections. "The EU AI Act deadline means X. LLM cost decline enables Y. PM career trends suggest Z."
13. **Assemble PESTLE artifact**: Combine all sections into `pestle_analysis` artifact. Validate against gold standard checklist. Mark ralph_status: blocked (major gaps or contradictions) or decision_ready (all checks pass).

## 6. Output Specification

| Field | Type | Schema Reference | Required | Description |
|---|---|---|---|---|
| `pestle_analysis` | `object` | `pestle_analysis.schema.json` | Yes | Complete 6-factor analysis with projections and implications |

Primary output artifact: `pestle_analysis` → maps to `core/schemas/artifacts/pestle_analysis.schema.json`

## 7. Guardrails

- **Failure condition: Single-source factor**: A factor's findings rely on a single source with no corroboration → response: mark confidence as low. Flag factor for PM review. Do not block, but do not claim certainty.
- **Failure condition: Geographic scope exceeds evidence**: PM requests analysis for APAC but only US/EU data available → response: flag APAC region with "data insufficient — analysis deferred" message. Do not generate speculative analysis for data-less regions.
- **Failure condition: Contradictory evidence within a factor**: Two sources disagree on trend direction (one says improving, another says stable) → response: surface contradiction explicitly in findings. Mark confidence as low. Do not resolve silently.
- **When to stop and escalate to PM**: Composite risk score >80 — product faces high environmental risk and PM should review before proceeding. Two or more factors have impact_score >=8 with low confidence — high-stakes uncertainty. Scenario projections all point to negative outcomes.
- **When output should be marked low-confidence**: More than 2 factors rely on single-source evidence. Key findings are >90 days old (stale). Geographic variations are inferred from global data, not region-specific research.
- **When skill should refuse to generate**: No source evidence for any factor beyond one. Market is undefined. PM has marked PESTLE analysis as parked. Governance review blocks environmental data collection.

## 8. Gold Standard Checklist

- [ ] All 6 PESTLE factors are covered with specific, non-generic findings — not "Economic: GDP may fluctuate" but "Economic: PM tooling market growing at 35% CAGR per 2026 analyst reports"
- [ ] Every finding has a source_ref that resolves to a specific source_note_card, regulation, or artifact
- [ ] Trend projections exist for all three horizons (6m/12m/24m) for every factor with explicit reasoning
- [ ] Minimum 4 factor interconnections spanning at least 3 different relationship types
- [ ] Each factor has at least one risk AND one opportunity — PESTLE is not just description, it's strategic input
- [ ] Geographic variations are modeled for at least 2 regions beyond home market
- [ ] At least 2 distinct scenario projections that represent materially different futures
- [ ] Key implications are actionable — a PM should read them and know what to do next
- [ ] Confidence levels are honest — low confidence is stated explicitly, not obscured
- [ ] External framework alignment: validates against Francis Aguilar's original PESTLE framework (Harvard), Shell scenario planning methodology, and Porter's Five Forces contextual analysis

## 9. Examples

### Excellent Output (5/5)
See `core/examples/artifacts/pestle_analysis.example.json` for the canonical format. Key qualities:
- 17 specific findings across all 6 factors, each with source_ref
- All three timeline projections per factor with evidence-grounded reasoning
- 5 interconnections across 3 relationship types
- 2 distinct scenario projections (AI Regulation Overreach, LLM Commoditization)
- 3 geographic variations with risk adjustments
- 5 actionable strategic implications

### Poor Output (2/5) — What to Avoid

```json
{
  "factors": {
    "political": {
      "key_findings": [{"observation": "Regulations are changing", "significance": "major", "source_ref": "general_knowledge"}],
      "risks": ["Regulation could be bad"],
      "opportunities": ["Could be good"]
    }
  }
}
```

**Why this fails:**
- Vague findings with no specific data, regulation name, or jurisdiction reference
- Source "general_knowledge" is not a valid source_ref — every claim needs an evidence source
- Risks and opportunities are uselessly generic — "could be bad" gives PM zero actionable insight
- Single finding per factor — insufficient for strategic-quality analysis
- No timeline projections, interconnections, or scenarios

## 10. Cross-References

- **Upstream skills**: `source_discovery`, `source_normalization`, `evidence_extraction`, `market_definition_precision`, `freshness_scoring`, `competitive_entity_resolution`
- **Downstream skills**: `strategy_option_architecture`, `decision_packet_synthesis`, `market_trend_extrapolation`, `roadmap_scenario_generation`, `investor_content_generation`, `sensitivity_analysis`
- **Related entity schemas**: `core/schemas/entities/market.schema.json`, `core/schemas/entities/decision.schema.json`
- **Related artifact schemas**: `core/schemas/artifacts/pestle_analysis.schema.json`, `core/schemas/artifacts/strategy_option_set.schema.json`, `core/schemas/artifacts/market_strategy_brief.schema.json`, `core/schemas/artifacts/regulatory_change_tracker.schema.json`
- **Related workflows**: `core/workflows/discovery/pestle-to-strategy-bridge.md`

## 11. Maturity Band Variations

| Band | Depth Adjustment | Evidence Requirements | Output Expectations |
|---|---|---|---|
| 0→1 | Exhaustive: full 6-factor with all projections, 3+ scenarios, geographic variations for all target regions. Deep qualitative narrative — early market has less quantitative data. | Minimum 3 sources per factor. Allow analyst estimates when historical data thin. Qualitative driver analysis required. | Full PESTLE. Explicit "limited data" caveat. Scenario projections weighted toward exploration, not prediction. |
| 1→10 | Deep: full 6-factor with all projections. 2 scenarios minimum. Geographic variations for key regions. | Minimum 2 sources per factor. Mix of primary research + analyst data. | Strategic implications linked to specific features and roadmap items. |
| 10→100 | Standard: full 6-factor. 6m and 12m projections. 2 scenarios. Key region variations only. | Minimum 2 sources per factor. Quantitative data preferred. Statistical rigor. | Implications feed resource allocation and investment decisions. |
| 100→10K+ | Focused: 4-factor subset (highest impact factors). 12m projection only. 1 scenario (pessimistic). | Minimum 2 sources per factor. Market data + regulatory tracking. | Portfolio-level environmental view. Individual factor depth deprioritized for macro trends. |

## 12. Validation Criteria

- **Schema conformance**: validates against `core/schemas/artifacts/pestle_analysis.schema.json`
- **Test file**: `tests/test_v10_pestle_synthesis.py`
- **Example fixture**: `core/examples/artifacts/pestle_analysis.example.json`
- **Skill consistency test**: included in `tests/test_skill_consistency.py` — all 12 elements present and non-empty
