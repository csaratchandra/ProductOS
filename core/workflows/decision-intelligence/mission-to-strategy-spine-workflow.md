# Mission To Strategy Spine Workflow

Purpose: Convert a bounded `mission_brief` and supporting discovery evidence into explicit strategy context and product vision artifacts before market posture, concept, or PRD work continues.

## Inputs

- `mission_brief`
- `market_analysis_brief`
- `segment_map`
- `persona_pack` or `persona_archetype_pack`
- `research_brief`
- optional `strategy_option_set`

## Outputs

- `strategy_context_brief`
- `product_vision_brief`
- recommendation to proceed to `market_strategy_brief` or gather more evidence

## Rules

- make enterprise-goal linkage, portfolio-bet fit, and business-model outcomes explicit rather than implied
- define the durable product vision and the nearer-term product goal in separate fields
- state customer value, business value, differentiation, and the north-star metric explicitly
- preserve references to the mission, market, segment, persona, and research artifacts used to form the recommendation
- route to `market-strategy-definition-workflow` only after the strategy context and product vision are explicit enough to constrain posture and positioning
- route to `strategy-option-generation-workflow` before committed market posture when more than one credible wedge or posture remains
- recommend more evidence when the team cannot justify `why this market`, `why this bet`, `why now`, or `what metric matters most`
- do not let strategy, vision, or value-proposition questions collapse into a generic research summary

## Failure Rules

Do not produce a committed strategy spine if:

- there is no current `mission_brief`
- enterprise-goal linkage is missing
- customer value, business value, or differentiation remains materially ambiguous
- the north-star metric is missing or disconnected from the stated product goal
- evidence cannot explain the recommendation
- the likely posture depends on unresolved option tradeoffs that have not been made explicit

In these cases, route back to research or mission refinement instead of forcing a weak strategy packet.
