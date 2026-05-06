# ProductOS Starter Template

This template is the clean starter for using ProductOS on another product.

This is the starter PMs should copy or initialize from when using ProductOS for a new product or feature.

Use this when:

- you want to operate a normal product with ProductOS
- you do not need ProductOS-improvement records as the main product backlog
- you want a seeded lifecycle bundle that demonstrates traceability from intake through post-release learning

Do not mix ProductOS sample-fixture artifacts into a product workspace created from this template.

The starter now includes:

- a seeded discovery-plus-delivery bundle
- one canonical `item_lifecycle_state`
- lifecycle stage snapshots for `discovery`, `delivery`, `launch`, `outcomes`, and `full_lifecycle`
- one prototype-validation pass with an interactive-prototype record and UX review
- one bounded `story_pack`
- one bounded `acceptance_criteria_set`
- one bounded `release_readiness`
- one governed `release_note`
- one explicit `outcome_review`
- starter docs showing how to review the item end to end

Recommended start path:

1. run `./productos start`
2. choose `Start a new workspace` or `Bring existing work into ProductOS`
3. if you start a new workspace, choose `Startup` or `Enterprise`, then choose what you want ProductOS to help you create first
4. replace the seeded artifacts with product-specific evidence
5. keep ProductOS sample fixtures and release records outside your product workspace

Advanced path:

- `./productos init-workspace ...`
- `./productos --workspace-dir /path/to/workspace init-mission ...`
