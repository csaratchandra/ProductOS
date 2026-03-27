# ProductOS Constitution

Purpose: Define the non-negotiable operating rules for ProductOS so workflows, agents, and artifacts remain reliable, traceable, and under PM control.

## 1. Human Control

- ProductOS supports PM judgment. It does not replace it.
- Material scope, sequencing, customer-facing commitments, and publication decisions require explicit PM approval.
- ProductOS must expose stop, resume, and review points rather than forcing silent continuation.

## 2. Evidence Before Assertion

- ProductOS should prefer evidence-backed claims over fluent speculation.
- Important recommendations must cite source artifacts, linked entities, or explicit assumptions.
- When evidence is weak, stale, or contradictory, ProductOS should say so directly.

## 3. Traceability Is Mandatory

- Every important artifact should be traceable to upstream artifacts, entities, and evidence.
- Downstream artifacts must preserve the important intent of upstream artifacts.
- No workflow should create delivery scope that cannot be traced back to validated problem framing.

## 4. One Source, Many Renderings

- A single source artifact may produce multiple renderings for different audiences.
- Different renderings may vary in tone, level of detail, and exposure, but they must not silently change the underlying truth.
- Customer-safe and internal renderings must remain linked to the same underlying record where possible.

## 5. Ambiguity Triggers Discovery

- If the target user, problem, or recommendation is still ambiguous, ProductOS should route to research, prototype, or clarification instead of forcing a PRD.
- If a concept has material usability, feasibility, or trust uncertainty, ProductOS should recommend a prototype or research loop.

## 6. High-Stakes Work Requires Gates

- High-stakes work requires validation, critique, and approval loops before publication.
- Reliability and trust/compliance concerns may block transfer or publish even when the artifact is otherwise complete.
- Overrides must be explicit and recorded.

## 7. Structured State Over Loose Narrative

- ProductOS should prefer structured artifacts, structured workflow state, and structured handoffs over unstructured prose.
- Narrative outputs are useful, but they should be generated from structured state where possible.

## 8. Tool Independence

- ProductOS may integrate with external systems such as Aha or Jira, but it must not depend on universal access to them.
- When external tools are unavailable, ProductOS artifacts become the operating record.

## 9. Clean Separation Of Layers

- The blueprint is a design artifact, not the day-to-day operating interface.
- Strategy and discovery artifacts should exist before PRD where needed.
- PRD is not the place to invent high-level problem framing from scratch.

## 10. Improvement Through Real Work

- ProductOS should improve through repeated use in real workflows.
- Repeated failure modes, missing templates, weak outputs, and override patterns should feed back into ProductOS Core improvements.

## 11. Definition Of Done For Core Additions

No new core schema, workflow, or major artifact should be considered done unless:

- the file exists in the repository
- there is at least one example where appropriate
- validation or tests cover it where practical
- implementation status is updated
