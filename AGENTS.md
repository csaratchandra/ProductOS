# ProductOS Agent Map

ProductOS is a repo-first operating system for PM work and AI-assisted execution.

## Canonical Surfaces

- `README.md`: repo entrypoint and stable-line posture
- `core/docs/`: operating models, guardrails, and release-scope boundaries
- `core/schemas/`: artifact and entity contracts
- `core/examples/`: valid example payloads for schema-backed work
- `scripts/productos.py`: canonical CLI surface
- `internal/ProductOS-Next/`: self-hosting workspace for dogfooding the next bounded slice

## Expected Flow

1. inspect the current repo and workspace reality
2. create or update the bounded mission or plan artifact
3. implement the smallest coherent slice
4. run the Ralph loop: inspect, implement, refine, validate, fix, revalidate
5. keep release claims aligned with actual proof in the repo

## Core Commands

- `./productos status`
- `./productos start --dest ... --workspace-id ... --name ... --mode ... --title ... --customer-problem ... --business-goal ...`
- `./productos import --source ... --dest ... --workspace-id ... --name ... --mode ...`
- `./productos run discover`
- `./productos run align`
- `./productos run operate`
- `./productos run improve`
- `./productos review`
- `./productos doctor`
- `pytest`

## Guardrails

- the repository is the system of record
- `workspaces/` is for product-specific workspaces, not core ProductOS logic
- keep PM approval explicit for decision-driving scope and release movement
- do not broaden autonomous PM claims past the evidence-backed release boundary
