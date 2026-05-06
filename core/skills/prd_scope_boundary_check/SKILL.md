# PRD Scope Boundary Check Skill

## 1. Purpose
Validate that PRD scope boundaries are specific enough to prevent agent/execution scope creep and ensure builders know exactly what NOT to build.

## 2. Trigger / When To Use
- PRD created or updated
- Prototype generation plan requested
- Agent brief export requested
- Before any downstream execution from PRD

## 3. Prerequisites
- PRD artifact exists with `out_of_scope` field populated
- Linked artifacts available (problem_brief, strategy_context_brief)
- Workspace has active mission brief

## 4. Input Specification
- `prd.json`: Product Requirements Document artifact
- `problem_brief.json`: Problem framing context
- `strategy_context_brief.json`: Strategic direction context

## 5. Execution Steps
1. Load PRD artifact from workspace
2. Check `out_of_scope` field exists and has >= 3 items
3. Validate each boundary item is specific (no vague terms like "etc.", "other features", "TBD")
4. Check upstream alignment: boundaries don't contradict problem brief or strategy
5. Check downstream impact: boundaries cover all non-core use
6. Flag ambiguous boundaries with suggested specific language
7. Compute boundary score (1-10) based on specificity, coverage, and alignment
8. Emit `prd_boundary_report` artifact with score, flagged items, and approval status

## 6. Output Specification
- `prd_boundary_report.json`: {score, flagged_boundaries, suggested_fixes, approval_status}
- Score breakdown: specificity (40%), coverage (40%), alignment (20%)
- Approval status: approved | needs_revision | blocked

## 7. Guardrails
- Boundary too vague ("etc.", "other features", "TBD") → reject with specific feedback
- Missing out_of_scope field → block, require PRD update
- Boundary contradicts upstream strategy → escalate to PM with rationale
- < 3 out_of_scope items for 0→1 maturity → flag as insufficient
- Score < 5 → block downstream execution until revised

## 8. Gold Standard Checklist
- [ ] Every boundary is specific enough that a builder/agent would know what NOT to build
- [ ] No vague language in out_of_scope items (per McKinsey scope definition standards)
- [ ] Boundaries align with problem brief scope and strategy wedge
- [ ] Coverage includes: feature exclusions, segment exclusions, platform exclusions, timeline exclusions
- [ ] Score >= 8 for production PRDs

## 9. Examples
- Excellent (5/5): "Out of scope: iOS native app (web-only for v1), enterprise SSO integration (phase 2), real-time collaboration (evaluated, rejected for v1), admin dashboard (separate product), API rate limiting (handled by platform team)"
- Poor (2/5): "Other features not in scope", "Future enhancements TBD", "Additional platforms etc."

## 10. Cross-References
- Upstream: `concept_risk_surfacing`, `problem_brief`
- Downstream: `prototype_html_generation`, `export_pipeline` (agent_brief), `living_document_rendering`
- Related: `prd.schema.json`, `regeneration_queue`

## 11. Maturity Band Variations
| Band | Depth |
|---|---|
| 0→1 | Exhaustive boundaries required (8+ items), score >= 7 to pass |
| 1→10 | Deep boundaries with competitive context (5+ items), score >= 6 to pass |
| 10→100 | Standard with API contract linkage (3+ items), score >= 5 to pass |
| 100→10K+ | Automated boundary validation with historical pattern matching |

## 12. Validation Criteria
- `tests/test_v10_prd_scope_boundary_check.py`
- Report validates against `prd_boundary_report` schema (new)
- Score computation is deterministic and reproducible
- All vague language patterns are caught
