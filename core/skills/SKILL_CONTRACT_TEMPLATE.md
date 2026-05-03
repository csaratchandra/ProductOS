# Skill Contract Template (V10 Standard — 12 Elements)

This is the canonical skill contract format for all ProductOS V10 skills. Every skill (existing and new) must conform to this standard. Skills that do not meet this standard are scored <5 on `output_quality` in feature scorecards.

---

## 1. Purpose
One sentence: what this skill accomplishes and why it exists.

## 2. Trigger / When To Use
Specific conditions under which this skill should be invoked. Include explicit signals: what evidence, artifact state, or PM action triggers this skill.

## 3. Prerequisites
What must exist or be completed before this skill can execute. List upstream artifacts, evidence, decisions, or approvals required.

## 4. Input Specification

| Field | Type | Source Artifact/Schema | Required | Example Value | Notes |
|---|---|---|---|---|---|
| `field_name` | `type` | `schema_reference` | Yes/No | `"example"` | Constraints, format requirements |

## 5. Execution Steps
1. **[Step label]**: Specific action with explicit instructions. What to do. What to check. What to transform.
2. **[Step label]**: Specific action.
...
N. **[Step label]**: Final action and output emission.

## 6. Output Specification

| Field | Type | Schema Reference | Required | Description |
|---|---|---|---|---|
| `field_name` | `type` | `schema_file.schema.json#/$defs/...` | Yes/No | What this field represents |

Primary output artifact: `[schema_name]` → maps to `core/schemas/artifacts/[name].schema.json`

## 7. Guardrails
- **Failure condition 1**: [condition] → detection criteria: [how to detect] → response: [what to do]
- **Failure condition 2**: ...
- **When to stop and escalate to PM**: [conditions where AI should NOT continue]
- **When output should be marked low-confidence**: [specific criteria]
- **When skill should refuse to generate**: [hard blockers — no output produced]

## 8. Gold Standard Checklist
- [ ] Criterion 1: [specific, verifiable quality check]
- [ ] Criterion 2: ...
- [ ] External framework alignment: validate against [named framework] — see [reference]
- [ ] Evidence traceability: every claim traces to at least one source
- [ ] Contradiction check: no internal contradictions or conflicts with existing artifacts

## 9. Examples

### Excellent Output (5/5)
```json
{
  "embedded_example": "showing perfect output that passes all gold standard checks"
}
```

### Poor Output (2/5) — What to Avoid
```json
{
  "embedded_example": "showing common failure patterns and why they fail"
}
```

**Why this fails:** [explanation of what's wrong and how to fix it]

## 10. Cross-References
- **Upstream skills**: `[skill_name_1](./SKILL.md)`, `[skill_name_2](./SKILL.md)` — skills that feed input into this skill
- **Downstream skills**: `[skill_name_3](./SKILL.md)`, `[skill_name_4](./SKILL.md)` — skills that consume this skill's output
- **Related entity schemas**: `core/schemas/entities/[name].schema.json`
- **Related artifact schemas**: `core/schemas/artifacts/[name].schema.json`
- **Related workflows**: `core/workflows/[path/workflow].md`

## 11. Maturity Band Variations

| Band | Depth Adjustment | Evidence Requirements | Output Expectations |
|---|---|---|---|
| 0→1 | [how skill behaves differently] | [minimum evidence bar] | [what quality level is expected] |
| 1→10 | ... | ... | ... |
| 10→100 | ... | ... | ... |
| 100→10K+ | ... | ... | ... |

## 12. Validation Criteria
- **Schema conformance**: validates against `core/schemas/artifacts/[name].schema.json`
- **Test file**: `tests/test_v10_[name].py`
- **Example fixture**: `core/examples/artifacts/[name].example.json`
- **Skill consistency test**: included in `tests/test_skill_consistency.py` with all 12 elements present