# ProductOS Presentation Regression Fixtures

Purpose: Define the minimum fixture set that should stay stable as V4 presentation packaging evolves.

## Required Fixture Classes

- leadership decision deck fixture
- roadmap or strategy packaging fixture
- risk-heavy review fixture
- customer-safe redacted fixture
- PPT fallback fidelity fixture

## Current Fixture Set

- `components/presentation/examples/artifacts/presentation_brief.example.json`
- `components/presentation/examples/artifacts/evidence_pack.example.json`
- `components/presentation/examples/artifacts/presentation_story.example.json`
- `components/presentation/examples/artifacts/render_spec.example.json`
- `components/presentation/examples/artifacts/publish_check.example.json`
- `components/presentation/examples/artifacts/ppt_export_plan.example.json`

Private local fixtures may supplement these, but the public regression baseline should not depend on a private workspace checkout.

## Regression Rules

- do not remove source labels from decision-driving slides
- do not let HTML and PPT exports diverge without an explicit fidelity note
- do not regress answer-first leadership storytelling into setup-heavy narrative
- do not let new visual patterns bypass sample review and manual validation
