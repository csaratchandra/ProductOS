# ProductOS V11.0.0 Candidate — Bounded Claim

**Status:** Candidate  
**Stable Line:** V10.0.0 remains current  
**Scope Boundary:** Living Product System infrastructure  

---

## What V11 Claims

This V11 candidate delivers the **Living Product System** — four integrated capabilities that transform static artifact generation into auto-propagating, self-rendering, delta-reviewed product management:

1. **Auto-Propagation Engine**: When source artifacts change, mechanical updates auto-execute and content-deep changes queue for PM review with human-readable delta previews.
2. **Living Markdown Renderer**: Readable documents are render targets from structured artifacts + Jinja2 templates, with evidence traceability and PM annotation preservation.
3. **PM Delta Review Lane**: Cockpit shows all pending artifact updates with approve/reject/modify actions, impact classification, and dependency ordering.
4. **Export Pipeline**: Same artifact exports to markdown, deck, agent brief, stakeholder update, battle card, or one pager without copy-paste drift.

---

## What V11 Does NOT Claim

The following are **explicitly out of scope** for V11.0.0:

1. **Real-time collaborative editing**: Multiple PMs editing the same artifact simultaneously is not supported.
2. **Voice memo transcription**: PM note ingestion supports text transcripts; voice-to-text transcription is a future integration.
3. **Slack/email ingestion**: Automated ingestion from external communication tools is not included.
4. **ML-based impact classification**: Impact classification (mechanical vs. content_deep) uses rule-based heuristics, not learned models.
5. **Automated research source discovery**: The research auto-cascade system defines the architecture but does not include live web scraping or API integrations.
6. **Production hosting**: ProductOS remains a CLI-first local runtime; cloud hosting is not included.

---

## Evidence of Claim

| Claim | Evidence Location |
|---|---|
| Auto-propagation works | `tests/test_v11_living_system.py::TestRegenerationQueue` |
| Living docs render | `tests/test_v11_living_system.py::TestMarkdownRenderer` |
| Export pipeline works | `tests/test_v11_living_system.py::TestExportPipeline` |
| Schemas validate | `tests/test_v11_living_system.py::TestSchemas` |
| CLI commands exist | `python3 scripts/productos.py queue build --help` |
| Dogfood workspace | Private local dogfood workspace not included in the shared repo |
| Templates render | `core/templates/living_docs/*.md.jinja2` |
| Skills documented | `core/skills/*/SKILL.md` (12-element standard) |

---

## Risk & Mitigation

| Risk | Mitigation |
|---|---|
| Auto-propagation creates noise | Rule-based classification is conservative; PM can tune sensitivity |
| Template rendering loses PM voice | Templates are narrative-first; PM edits structured artifacts with voice |
| Circular dependencies | Detected and blocked with PM escalation |
| Over-automation | Design principle: AI handles reconstruction, PM handles decisions |

---

## Release Operator

- `./productos release --slice-label "v11-living-system" --push`
- Tag: `v11.0.0`
- Branch: `main`

---

*Bounded claim status: candidate only until public release metadata is aligned*  
*Date: 2026-05-06*
