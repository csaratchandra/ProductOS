from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VAGUE_PATTERNS = (
    r"\betc\.?\b",
    r"\bother features\b",
    r"\btbd\b",
    r"\bmaybe\b",
    r"\bshould\b",
    r"\bconsider\b",
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _contains_vague_language(text: str) -> bool:
    lowered = text.lower()
    return any(re.search(pattern, lowered) for pattern in VAGUE_PATTERNS)


def _required_boundary_count(maturity_band: str) -> int:
    if maturity_band == "zero_to_one":
        return 8
    if maturity_band == "one_to_ten":
        return 5
    return 3


def build_prd_boundary_report(
    workspace_dir: Path,
    *,
    prd_path: Path | None = None,
    problem_brief_path: Path | None = None,
    strategy_context_path: Path | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    generated_at = generated_at or _now_iso()
    prd_path = prd_path or (workspace_dir / "artifacts" / "prd.json")
    problem_brief_path = problem_brief_path or (workspace_dir / "artifacts" / "problem_brief.json")
    strategy_context_path = strategy_context_path or (workspace_dir / "artifacts" / "strategy_context_brief.json")

    prd = _load_json(prd_path)
    problem_brief = _load_json(problem_brief_path) if problem_brief_path.exists() else {}
    strategy_context = _load_json(strategy_context_path) if strategy_context_path.exists() else {}
    out_of_scope = list(prd.get("out_of_scope") or [])
    maturity_band = str(prd.get("maturity_band") or "zero_to_one")

    flagged_boundaries: list[dict[str, str]] = []
    suggested_fixes: list[str] = []

    for boundary in out_of_scope:
        if _contains_vague_language(boundary):
            flagged_boundaries.append(
                {
                    "boundary": boundary,
                    "issue": "vague_language",
                    "suggested_fix": "Replace generic or hedged language with a concrete exclusion and rationale.",
                }
            )
            suggested_fixes.append(
                f"Rewrite '{boundary}' as a concrete exclusion with a user, platform, or capability boundary."
            )

    required_count = _required_boundary_count(maturity_band)
    if len(out_of_scope) < required_count:
        flagged_boundaries.append(
            {
                "boundary": "out_of_scope",
                "issue": "insufficient_coverage",
                "suggested_fix": f"Add at least {required_count - len(out_of_scope)} more explicit exclusions.",
            }
        )
        suggested_fixes.append(
            f"Add explicit exclusions to reach at least {required_count} out-of-scope items for {maturity_band} work."
        )

    problem_statement = str(problem_brief.get("problem_statement") or prd.get("problem_statement") or "")
    strategy_summary = " ".join(
        str(value)
        for value in (
            strategy_context.get("summary"),
            strategy_context.get("positioning"),
            strategy_context.get("strategy_statement"),
        )
        if value
    ).lower()
    for boundary in out_of_scope:
        lower = boundary.lower()
        if problem_statement and any(token in lower for token in problem_statement.lower().split()[:4]):
            flagged_boundaries.append(
                {
                    "boundary": boundary,
                    "issue": "problem_alignment_risk",
                    "suggested_fix": "Clarify whether the exclusion contradicts the core customer problem being solved.",
                }
            )
            suggested_fixes.append(
                f"Clarify how '{boundary}' stays out of scope without undermining the primary customer problem."
            )
        if strategy_summary and any(token in lower for token in strategy_summary.split()[:4]):
            flagged_boundaries.append(
                {
                    "boundary": boundary,
                    "issue": "strategy_alignment_risk",
                    "suggested_fix": "Explain why this exclusion still aligns with the current strategy wedge.",
                }
            )

    specificity_score = max(0, 10 - (len([f for f in flagged_boundaries if f["issue"] == "vague_language"]) * 2))
    coverage_score = min(10, int((len(out_of_scope) / max(required_count, 1)) * 10))
    alignment_penalty = len(
        [
            f
            for f in flagged_boundaries
            if f["issue"] in {"problem_alignment_risk", "strategy_alignment_risk"}
        ]
    )
    alignment_score = max(0, 10 - (alignment_penalty * 2))
    overall_score = round((specificity_score * 0.4) + (coverage_score * 0.4) + (alignment_score * 0.2), 1)

    has_vague_language = any(item["issue"] == "vague_language" for item in flagged_boundaries)
    if not out_of_scope:
        approval_status = "blocked"
    elif has_vague_language:
        approval_status = "blocked"
    elif overall_score < 5:
        approval_status = "blocked"
    elif overall_score < 7 or flagged_boundaries:
        approval_status = "needs_revision"
    else:
        approval_status = "approved"

    return {
        "schema_version": "1.0.0",
        "prd_boundary_report_id": f"prd_boundary_report_{prd.get('prd_id', workspace_dir.name)}",
        "workspace_id": prd.get("workspace_id", workspace_dir.name),
        "prd_ref": f"artifacts/{prd_path.name}",
        "score": overall_score,
        "score_breakdown": {
            "specificity": specificity_score,
            "coverage": coverage_score,
            "alignment": alignment_score,
        },
        "flagged_boundaries": flagged_boundaries,
        "suggested_fixes": sorted(set(suggested_fixes)),
        "approval_status": approval_status,
        "generated_at": generated_at,
    }


def write_prd_boundary_report(
    workspace_dir: Path,
    *,
    output_path: Path | None = None,
    generated_at: str | None = None,
) -> Path:
    report = build_prd_boundary_report(workspace_dir, generated_at=generated_at)
    output_path = output_path or (workspace_dir / "outputs" / "improve" / "prd_boundary_report.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return output_path
