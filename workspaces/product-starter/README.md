# ProductOS Starter Workspace

This workspace is the clean non-self-hosting starter for using ProductOS on another product.

This is the workspace PMs should copy or initialize from when using ProductOS for a new product or feature.

Use this when:

- you want to operate a normal product with ProductOS
- you do not need ProductOS-improvement records as the main product backlog
- you want a seeded lifecycle bundle that demonstrates traceability from intake through release readiness

Use `workspaces/productos-v2/` only when ProductOS itself is the product being operated.

The starter now includes:

- a seeded discovery-plus-delivery bundle
- one canonical `item_lifecycle_state`
- lifecycle stage snapshots for `discovery`, `delivery`, `launch`, `outcomes`, and `full_lifecycle`
- one bounded `story_pack`
- one bounded `acceptance_criteria_set`
- one bounded `release_readiness`
- starter docs showing how to review the item end to end

Recommended start path:

1. initialize a new workspace with `./productos init-workspace --template product-starter ...`
2. replace the seeded artifacts with product-specific evidence
3. keep `workspaces/productos-v2/` untouched unless ProductOS itself is the product
