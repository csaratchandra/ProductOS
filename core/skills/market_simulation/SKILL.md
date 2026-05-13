# Skill Contract: Market Simulation

## 1. Purpose
Extend predictive simulation with external market forces using the static competitive knowledge base — competitive response modeling, regulatory timing awareness, market saturation analysis, economic sensitivity, and risk-adjusted roadmap generation.

## 2. Trigger / When To Use
- After predictive simulation completes with baseline forecast
- When generating comprehensive product architecture for a competitive domain
- As part of the full `productos architect` pipeline (always included in auto mode)

## 3. Prerequisites
- Completed `ProductArchitecture` with workflow orchestration map
- Completed `SimulationForecast` from `predictive_simulation`
- `MarketContext` loaded from static knowledge base (`core/market_intelligence/`)

## 4. Input Specification

| Field | Type | Source Artifact/Schema | Required | Description |
|---|---|---|---|---|
| `architecture` | `object` | `product_architecture.schema.json` | Yes | Full product architecture |
| `market_context` | `object` | Market intelligence JSON files | Yes | Competitive landscape, regulatory timeline, economic indicators |

## 5. Execution Steps
1. **Load market context**: Read competitive landscape, regulatory timeline, and economic indicators from static knowledge base.
2. **Model competitive response**: For each known competitor in the domain, simulate adoption impact of competitive feature launches.
3. **Assess regulatory timing**: Overlay expected regulation changes on the architecture timeline.
4. **Analyze market saturation**: Compare product positioning against known products in the domain.
5. **Evaluate economic sensitivity**: Map macro-economic factors to domain-specific user acquisition and retention impacts.
6. **Generate risk-adjusted roadmap**: Order feature delivery based on competitive pressure, regulatory timing, and technical risk.
7. **Emit MarketSimulationResult**: Return structured result with competitive scenarios, regulatory timing, and roadmap recommendations.

## 6. Output Specification

| Field | Type | Schema Reference | Required | Description |
|---|---|---|---|---|
| `competitive_response[]` | `array` | `market_simulation_result.schema.json` | Yes | Scenarios with adoption impact and confidence |
| `regulatory_timing[]` | `array` | `market_simulation_result.schema.json` | Yes | Expected regulation changes with impact |
| `risk_adjusted_roadmap[]` | `array` | `market_simulation_result.schema.json` | Yes | Prioritized recommendations with rationale |

Primary output artifact: `market_simulation_result` → maps to `core/schemas/artifacts/market_simulation_result.schema.json`

## 7. Guardrails
- **No knowledge base data**: If knowledge base is empty for the domain, return result with empty arrays and note "No competitive data available"
- **Static data only**: All market data is static knowledge; never make live API calls
- **Confidence bounded**: Competitive response confidence should never exceed 0.7 without external data sources
- **When to stop and escalate to PM**: If competitive adoption impact > 30%, flag as critical risk requiring PM review

## 8. Gold Standard Checklist
- [ ] Competitive response includes at least one relevant competitor scenario
- [ ] Regulatory timing references actual known regulations from the knowledge base
- [ ] Risk-adjusted roadmap provides concrete sequencing recommendations
- [ ] Each recommendation has an explicit rationale
- [ ] Confidence scores are calibrated (not all 1.0, not all 0.1)

## 9. Examples

### Excellent Output (5/5)
```json
{
  "competitive_response": [
    {"scenario": "Competitor launches similar feature in 3 months", "adoption_impact": "-22%", "confidence": 0.6}
  ],
  "regulatory_timing": [
    {"regulation": "EU AI Act", "expected_date": "2026-03-01", "impact": "AI features may need compliance update"}
  ],
  "risk_adjusted_roadmap": [
    {"recommendation": "Launch core in Q1, AI features in Q3 after regulatory clarity", "rationale": "Regulatory timing suggests delaying AI features until EU AI Act clarity"}
  ]
}
```

## 10. Cross-References
- **Upstream skills**: `predictive_simulation`, `domain_intelligence`
- **Related artifact schemas**: `core/schemas/artifacts/market_simulation_result.schema.json`, `core/schemas/artifacts/simulation_forecast.schema.json`
- **Related knowledge base**: `core/market_intelligence/competitive_landscape.json`, `core/market_intelligence/regulatory_timeline.json`, `core/market_intelligence/economic_indicators.json`
- **Test file**: `tests/test_v14_market_simulation.py`

## 11. Maturity Band Variations

| Band | Depth Adjustment | Evidence Requirements | Output Expectations |
|---|---|---|---|
| 0→1 | Rule-based competitive scenario matching | Static knowledge base with competitors | 1 competitive scenario |
| 1→10 | Enhanced scenario generation | KB + regulatory timeline | 3 competitive scenarios + regulatory timing |
| 10→100 | LLM-assisted market narrative generation | Full KB + domain context | Competitive + regulatory + economic + roadmap |
| 100→10K+ | Live market data integration (backlog) | API-connected data sources | Real-time competitive intelligence |

## 12. Validation Criteria
- **Schema conformance**: validates against `core/schemas/artifacts/market_simulation_result.schema.json`
- **Test file**: `tests/test_v14_market_simulation.py`
- **Skill consistency test**: included in `tests/test_skill_consistency.py` with all 12 elements present
