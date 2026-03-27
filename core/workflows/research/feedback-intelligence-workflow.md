# Feedback Intelligence Workflow

Purpose: Produce a `feedback_intelligence_brief` that synthesizes feedback across customers, prospects, analysts, vendors, partners, supply chain, and internal teams.

## Inputs

- PM feedback question
- user feedback, customer feedback, analyst notes, vendor notes, partner notes, supply-chain inputs, and internal observations

## Outputs

- `feedback_intelligence_brief`

## Rules

- keep feedback source class explicit instead of collapsing all feedback into customer voice
- preserve sentiment, theme, and action implication separately
- do not over-weight analyst or vendor feedback without corresponding field evidence
- preserve evidence references for each feedback theme
