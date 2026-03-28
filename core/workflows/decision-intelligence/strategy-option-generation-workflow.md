# Strategy Option Generation Workflow

Purpose: Turn a strategic question into a `strategy_option_set` with materially different choices rather than superficial variants of one path.

## Inputs

- `problem_brief` or `signal_hypothesis_brief`
- `portfolio_state`
- `stakeholder_incentive_map`
- optional `opportunity_advantage_brief`

## Outputs

- `strategy_option_set`
- strategic recommendation
- decision-needed framing for the queue

## Rules

- generate at least three materially different options including a conservative path where relevant
- make tradeoffs explicit across upside, failure mode, dependency burden, reversibility, portfolio interaction, and org capability requirement
- reject cosmetic variants that only rename the same bet
- call out when missing evidence prevents a credible recommendation
