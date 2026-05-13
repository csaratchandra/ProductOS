# ProductOS V13.0.0 Bounded Claim

**Status:** Release-ready  
**Previous Stable Line:** V12.0.0  
**Scope Boundary:** Visual atlas, takeover synthesis, agent-native spec pipeline, and portfolio intelligence

---

## What V13 Claims

ProductOS V13 makes the **inheritance problem** the primary PM surface. A PM can ingest code, docs, screenshots, and transcripts, synthesize a product understanding, and generate agent-native build specs from that understanding.

V13 claims the following shipped capabilities:

1. **AI-assisted takeover understanding**
   - Code, document, and screenshot ingestion runtimes exist in the repo
   - Takeover synthesis produces a repo-backed product understanding and visual atlas
   - Product understanding can be rendered as human-readable atlas surfaces

2. **Agent-native spec pipeline**
   - Multi-journey and spec-chain runtimes generate structured implementation artifacts
   - Export surfaces produce agent-native JSON, tool definitions, and GitHub issue plans

3. **Portfolio intelligence**
   - Cross-workspace atlas aggregation and portfolio gap analysis exist in the repo
   - Ecosystem and portfolio renderers provide cross-product visibility

4. **Repo-backed proof posture**
   - V13 features are backed by dedicated `tests/test_v13_*` coverage
   - The shared repo keeps stable-line and bounded-claim evidence explicit

---

## What V13 Does NOT Claim

1. **Promoted stable-line status before release metadata exists.** V13 is only current after `release_13_0_0.json` and tag `v13.0.0` are created.
2. **Live third-party API ingestion as a required path.** File and repo ingestion are supported; live vendor integrations remain optional or future-facing.
3. **Cloud-hosted multi-user product operation.** ProductOS remains a repo-first local/runtime-driven system.
4. **V14 intent-driven architecture.** `productos architect` belongs to the V14 line, not the V13 bounded claim.

---

## Evidence of Claim

| Claim | Evidence |
|---|---|
| Takeover synthesis and atlas rendering | `tests/test_v13_atlas_synthesis.py`, `tests/test_v13_takeover_atlas_rendering.py` |
| Code, vision, and doc understanding | `tests/test_v13_code_analysis.py`, `tests/test_v13_vision_analysis.py`, `tests/test_v13_doc_ingestion.py` |
| Takeover living-system integration | `tests/test_v13_takeover_living_system.py` |
| Agent-native spec chain and export | `tests/test_v13_spec_chain.py`, `tests/test_v13_spec_export.py` |
| Portfolio aggregation and gaps | `tests/test_v13_portfolio_atlas.py` |

---

## Release Operator

- `./productos release --slice-label "v13 visual atlas and agent-native spec pipeline" --target-version 13.0.0 --push`
- Tag: `v13.0.0`
- Branch: `main`

---

*Bounded claim is limited to behavior proven in the shared repo and its tests.*
