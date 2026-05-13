# ProductOS V13.0.0 Release Note

**Release Tag:** `v13.0.0`  
**Previous Stable:** V12.0.0

---

## Executive Summary

ProductOS V13 turns repo-native product inheritance into a first-class PM flow. Instead of manually reconstructing a product from scattered code, docs, screenshots, and transcripts, the PM can synthesize a visual atlas and use that shared understanding as the basis for downstream agent-native specification work.

V13 is the bridge between:

- inheriting an existing product,
- understanding what already exists,
- and exporting structured build context for human or AI execution.

---

## What Ships in V13

### 1. Takeover and Visual Atlas

- Multi-modal ingestion runtimes for code, docs, and screenshots
- Atlas synthesis and takeover briefing surfaces
- Rendered takeover atlas outputs and related living-system wiring

### 2. Agent-Native Spec Pipeline

- Multi-journey synthesis and full spec-chain generation
- Export formats for agent-native JSON, tool definitions, and GitHub planning outputs

### 3. Portfolio and Ecosystem Intelligence

- Cross-workspace portfolio atlas aggregation
- Portfolio gap analysis
- Ecosystem rendering surfaces

### 4. Test-Backed Proof

- Dedicated `tests/test_v13_*` coverage for the V13 feature set
- Repo-backed artifacts and renderers that keep the release boundary explicit

---

## Validation

```bash
pytest tests/test_v13_*.py
pytest -q
```

---

## Upgrade Notes

1. V12 stable surfaces remain the baseline until V13 release metadata is promoted.
2. V13 expands the repo with inheritance and atlas capabilities without removing V12 living-system or agent-native execution features.
3. Product work remains repo-first: stable-line truth is defined by release metadata, bounded claims, and passing tests.

---

*ProductOS V13 is release-ready when its public release metadata and README stable-line surfaces are aligned.*
