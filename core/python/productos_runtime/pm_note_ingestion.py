from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .memory_registers import load_competitor_registry, load_problem_register


NOTE_TARGET_RULES = [
    ("competitor", "artifacts/competitor_dossier.json", "high"),
    ("pricing", "artifacts/competitor_dossier.json", "medium"),
    ("problem", "artifacts/problem_brief.json", "medium"),
    ("issue", "artifacts/problem_brief.json", "medium"),
    ("friction", "artifacts/problem_brief.json", "medium"),
    ("persona", "artifacts/persona_narrative_card.json", "medium"),
    ("customer", "artifacts/persona_narrative_card.json", "medium"),
    ("journey", "artifacts/customer_journey_map.json", "medium"),
    ("pain point", "artifacts/customer_journey_map.json", "high"),
    ("scope", "artifacts/prd.json", "high"),
    ("mobile", "artifacts/prd.json", "high"),
    ("sso", "artifacts/prd.json", "high"),
    ("market", "artifacts/market_analysis_brief.json", "medium"),
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ingest_pm_note(
    workspace_dir: Path,
    note_path: Path,
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    generated_at = generated_at or _now_iso()
    relative_path = note_path.relative_to(workspace_dir).as_posix()
    note_text = note_path.read_text(encoding="utf-8").strip()
    lowered = note_text.lower()

    proposed_deltas: list[dict[str, str]] = []
    seen_targets: set[str] = set()
    for index, (keyword, target_ref, confidence) in enumerate(NOTE_TARGET_RULES, start=1):
        if keyword not in lowered or target_ref in seen_targets:
            continue
        seen_targets.add(target_ref)
        quote = _first_matching_sentence(note_text, keyword)
        proposed_deltas.append(
            {
                "delta_id": f"pd_{index:03d}",
                "target_artifact_ref": target_ref,
                "proposed_change": _proposed_change(keyword, target_ref, quote),
                "confidence": confidence,
                "evidence_quote": quote,
                "regeneration_queue_item_id": f"rq_item_{index:03d}",
            }
        )
    memory_candidates = _memory_candidates(
        workspace_dir,
        note_text,
        note_path=note_path,
        proposed_deltas=proposed_deltas,
    )

    proposal = {
        "schema_version": "1.0.0",
        "pm_note_delta_proposal_id": f"pndp_{workspace_dir.name}_{note_path.stem}",
        "workspace_id": workspace_dir.name,
        "source_note": {
            "note_path": relative_path,
            "note_type": _note_type(note_path.name, note_text),
            "summary": _summarize_note(note_text),
        },
        "proposed_deltas": proposed_deltas,
        "generated_at": generated_at,
    }
    if memory_candidates:
        proposal["memory_candidates"] = memory_candidates
    return proposal


def write_pm_note_delta_proposal(
    workspace_dir: Path,
    note_path: Path,
    *,
    output_path: Path | None = None,
    generated_at: str | None = None,
) -> Path:
    proposal = ingest_pm_note(workspace_dir, note_path, generated_at=generated_at)
    output_path = output_path or (workspace_dir / "outputs" / "operate" / f"{note_path.stem}.pm_note_delta_proposal.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(proposal, indent=2) + "\n", encoding="utf-8")
    return output_path


def _note_type(filename: str, note_text: str) -> str:
    lowered_name = filename.lower()
    lowered_text = note_text.lower()
    if "transcript" in lowered_text or "customer call" in lowered_text or "call" in lowered_name:
        return "transcript"
    if "voice" in lowered_name or "memo" in lowered_name:
        return "voice_memo"
    return "meeting_notes"


def _summarize_note(note_text: str) -> str:
    first_sentence = re.split(r"(?<=[.!?])\s+", note_text.strip())[0]
    return first_sentence[:160] if first_sentence else "PM note ingested"


def _first_matching_sentence(note_text: str, keyword: str) -> str:
    for sentence in re.split(r"(?<=[.!?])\s+", note_text.strip()):
        if keyword in sentence.lower():
            return sentence.strip()[:240]
    return note_text[:240]


def _proposed_change(keyword: str, target_ref: str, quote: str) -> str:
    if target_ref.endswith("competitor_dossier.json"):
        return f"Add or refresh competitive signal related to '{keyword}'."
    if target_ref.endswith("problem_brief.json"):
        return f"Update problem framing or supporting evidence to account for: {quote[:100]}"
    if target_ref.endswith("prd.json"):
        return f"Update PRD scope or requirements to account for: {quote[:100]}"
    if target_ref.endswith("customer_journey_map.json"):
        return f"Update journey pain points and touchpoints based on: {quote[:100]}"
    if target_ref.endswith("market_analysis_brief.json"):
        return f"Refresh market analysis signal for '{keyword}'."
    return f"Review note impact on {target_ref}."


def _memory_candidates(
    workspace_dir: Path,
    note_text: str,
    *,
    note_path: Path,
    proposed_deltas: list[dict[str, str]],
) -> list[dict[str, Any]]:
    lowered = note_text.lower()
    problem_register = load_problem_register(workspace_dir, persist=False) or {}
    competitor_registry = load_competitor_registry(workspace_dir, persist=False) or {}
    candidates: list[dict[str, Any]] = []

    competitor_entries = competitor_registry.get("competitors", []) if isinstance(competitor_registry.get("competitors"), list) else []
    matched_competitors = [
        entry
        for entry in competitor_entries
        if isinstance(entry.get("name"), str) and entry["name"].lower() in lowered
    ]
    if any(delta["target_artifact_ref"].endswith("competitor_dossier.json") for delta in proposed_deltas):
        action = "refresh_existing" if matched_competitors else "create_candidate"
        linked_ids = [entry["competitor_entry_id"] for entry in matched_competitors]
        label = matched_competitors[0]["name"] if matched_competitors else f"Competitor signal from {note_path.stem}"
        candidates.append(
            {
                "candidate_id": f"mc_competitor_{note_path.stem}",
                "candidate_type": "competitor",
                "action": action,
                "label": label,
                "summary": _summarize_note(note_text),
                "confidence": "high" if matched_competitors else "medium",
                "linked_entry_ids": linked_ids,
            }
        )

    problem_entries = problem_register.get("problems", []) if isinstance(problem_register.get("problems"), list) else []
    active_problem = next((item for item in problem_entries if item.get("problem_entry_id") == problem_register.get("current_problem_entry_id")), None)
    problem_signal = any(
        keyword in lowered for keyword in ("problem", "pain", "issue", "friction", "workflow", "needs")
    ) or any(delta["target_artifact_ref"].endswith("problem_brief.json") for delta in proposed_deltas)
    if problem_signal:
        candidates.append(
            {
                "candidate_id": f"mc_problem_{note_path.stem}",
                "candidate_type": "problem",
                "action": "attach_evidence" if active_problem else "create_candidate",
                "label": active_problem.get("title", f"Problem signal from {note_path.stem}") if active_problem else f"Problem signal from {note_path.stem}",
                "summary": _summarize_note(note_text),
                "confidence": "medium" if active_problem else "needs_pm_clarification",
                "linked_entry_ids": [active_problem["problem_entry_id"]] if active_problem else [],
            }
        )

    return candidates
