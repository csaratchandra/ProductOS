# Research Command Center Workflow

Purpose: Give a new PM a single Day-1 entry point for common research asks such as competitive scans, review mining, consultant report synthesis, market analysis, and market sizing.

## Inputs

- PM research objective
- inbox items and normalized evidence
- optional existing `research_brief`, `research_notebook`, or `competitor_dossier`

## Outputs

- routed handoff to the correct research workflow
- explicit research starter pack recommendation
- decision-ready research pack for the PM
- recommendation to run `mission-to-strategy-spine-workflow` when the ask is about corporate linkage, value proposition, vision, product goal, or north-star logic
- recommendation to run `market-strategy-definition-workflow` when the ask is about posture, offering, or positioning rather than raw research alone

## Rules

- route competitive requests to `competitive-landscape-scan-workflow`
- route app reviews and social inputs to `app-review-and-social-mining-workflow`
- route long-form reports to `consultant-report-to-digest-workflow`
- route market sizing questions to `market-sizing-workflow`
- route market share questions to `market-share-estimation-workflow`
- route segmentation questions to `segmentation-mapping-workflow`
- route persona archetype questions to `persona-archetype-mapping-workflow`
- route market analysis questions to `market-analysis-workflow`
- route mixed competitor, market, and agentic-tool questions to `agentic-market-intelligence-workflow`
- route signal questions to `signal-landscape-workflow`
- route feedback source questions to `feedback-intelligence-workflow`
- route mixed-source discovery questions to `research-notebook-to-synthesis-workflow`
- route corporate-strategy linkage, value-proposition, product-vision, product-goal, or north-star questions to `mission-to-strategy-spine-workflow` after the relevant research artifacts exist
- route posture, offering, positioning, or beachhead-market questions to `market-strategy-definition-workflow` after the relevant research artifacts exist and the strategy spine is present when available
- for a PM starting from zero context, recommend one `research_brief`, one `competitor_dossier`, one `customer_pulse`, and one `visual_map_spec`
- the decision pack should pull from competitor, market share, segment, persona archetype, signal, and feedback intelligence outputs when relevant
- preserve any existing `strategy_context_brief` and `product_vision_brief` when routing posture or positioning work downstream
- do not let a positioning or strategic-posture question collapse into a raw research summary without an explicit market-role recommendation
- do not let strategy, vision, or value-proposition questions collapse into a raw research summary without an explicit strategy-spine recommendation
