# Market Share Estimation Workflow

Purpose: Produce a `market_share_brief` with explicit share scope, timeframe, denominator, basis, and confidence.

## Inputs

- PM market-share question
- competitor evidence, market notes, or analyst inputs
- optional prior `market_sizing_brief`

## Outputs

- `market_share_brief`

## Rules

- distinguish current share from reachable share and share-shift signals
- define the denominator explicitly before presenting any estimate
- every share estimate must record its basis and source references
- low-confidence share estimates should remain visibly tentative
