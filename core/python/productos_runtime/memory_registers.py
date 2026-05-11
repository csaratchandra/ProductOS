from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _append_manifest_artifact_path(workspace_path: Path, relative_path: str) -> None:
    manifest_path = workspace_path / "workspace_manifest.yaml"
    if not manifest_path.exists():
        return
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    artifact_paths = manifest.setdefault("artifact_paths", [])
    if relative_path in artifact_paths:
        return
    artifact_paths.append(relative_path)
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _parse_timestamp(raw: str | None) -> datetime | None:
    if not raw or not isinstance(raw, str):
        return None
    normalized = raw.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def _freshness_status(*timestamps: str | None) -> str:
    parsed = [item for item in (_parse_timestamp(raw) for raw in timestamps) if item is not None]
    current = max(parsed, default=None)
    if current is None:
        return "usable_with_review"
    age = datetime.now(timezone.utc) - current.astimezone(timezone.utc)
    if age.days <= 90:
        return "fresh"
    if age.days <= 180:
        return "usable_with_review"
    return "stale"


def _clean_strings(values: list[Any]) -> list[str]:
    cleaned: list[str] = []
    for value in values:
        if not isinstance(value, str):
            continue
        stripped = value.strip()
        if stripped and stripped not in cleaned:
            cleaned.append(stripped)
    return cleaned


def _is_starter_seed(*values: str) -> bool:
    return any("starter_trace_demo" in value or "ws_product_starter" in value for value in values if isinstance(value, str))


def _monitoring_summary(feed_registry: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(feed_registry, dict):
        return None
    competitor_feeds = [
        feed
        for feed in feed_registry.get("feeds", [])
        if isinstance(feed, dict) and feed.get("source_type") == "competitor_research"
    ]
    if not competitor_feeds:
        return None
    health_rank = {"healthy": 0, "empty": 1, "unconfigured": 2, "error": 3}
    cadence_rank = {"current": 0, "manual": 1, "due": 2, "unknown": 3, "stale": 4}
    health_status = max(
        (str(feed.get("health_status", "unconfigured")) for feed in competitor_feeds),
        key=lambda item: health_rank.get(item, 2),
        default="unconfigured",
    )
    cadence_status = max(
        (str(feed.get("cadence_status", "unknown")) for feed in competitor_feeds),
        key=lambda item: cadence_rank.get(item, 3),
        default="unknown",
    )
    checked_at = [str(feed.get("last_checked_at", "")) for feed in competitor_feeds if feed.get("last_checked_at")]
    success_at = [str(feed.get("last_success_at", "")) for feed in competitor_feeds if feed.get("last_success_at")]
    return {
        "feed_ids": _clean_strings([str(feed.get("feed_id", "")) for feed in competitor_feeds]),
        "health_status": health_status,
        "cadence_status": cadence_status,
        "last_checked_at": max(checked_at, default=""),
        "last_success_at": max(success_at, default=""),
    }


def _problem_entry_from_brief(
    problem_brief: dict[str, Any],
    *,
    existing_entry: dict[str, Any] | None = None,
    generated_at: str,
) -> dict[str, Any]:
    existing_entry = existing_entry or {}
    linked_problem_ids = [
        ref["entity_id"]
        for ref in problem_brief.get("linked_entity_refs", [])
        if ref.get("entity_type") == "problem" and isinstance(ref.get("entity_id"), str)
    ]
    problem_entry_id = existing_entry.get("problem_entry_id") or linked_problem_ids[:1] or [
        f"problem_entry_{_slug(problem_brief.get('title', 'problem'))}"
    ]
    title = problem_brief.get("title", "Problem")
    return {
        "problem_entry_id": problem_entry_id[0] if isinstance(problem_entry_id, list) else problem_entry_id,
        "title": title,
        "problem_summary": problem_brief.get("problem_summary", title),
        "status": existing_entry.get("status", "active"),
        "source_artifact_ids": _clean_strings(
            [
                *existing_entry.get("source_artifact_ids", []),
                problem_brief.get("problem_brief_id", ""),
                *problem_brief.get("upstream_artifact_ids", []),
            ]
        ),
        "evidence_refs": problem_brief.get("evidence_refs", []),
        "related_competitor_ids": _clean_strings(existing_entry.get("related_competitor_ids", [])),
        "current_problem_brief_id": problem_brief.get("problem_brief_id", ""),
        "current_derivative_artifact_ids": _clean_strings(
            [
                *existing_entry.get("current_derivative_artifact_ids", []),
                problem_brief.get("concept_brief_id", ""),
                problem_brief.get("prd_id", ""),
            ]
        ),
        "freshness_status": _freshness_status(problem_brief.get("created_at"), generated_at),
        "tags": _clean_strings(existing_entry.get("tags", [])),
        "last_updated_at": generated_at,
    }


def build_problem_register(
    workspace_id: str,
    problem_brief: dict[str, Any],
    *,
    generated_at: str | None = None,
    existing_register: dict[str, Any] | None = None,
) -> dict[str, Any]:
    generated_at = generated_at or _now_iso()
    existing_register = existing_register or {}
    incoming_problem_brief_id = str(problem_brief.get("problem_brief_id", ""))
    existing_problems_raw = existing_register.get("problems", []) if isinstance(existing_register.get("problems"), list) else []
    if existing_register.get("workspace_id") != workspace_id or (
        existing_problems_raw
        and all(
            _is_starter_seed(
                str(entry.get("current_problem_brief_id", "")),
                *[str(item) for item in entry.get("source_artifact_ids", [])],
            )
            for entry in existing_problems_raw
        )
        and not _is_starter_seed(incoming_problem_brief_id)
    ):
        existing_register = {}
    existing_problems = existing_register.get("problems", []) if isinstance(existing_register.get("problems"), list) else []
    active_entry = next((item for item in existing_problems if item.get("status") == "active"), None)
    if active_entry is None and len(existing_problems) == 1:
        active_entry = existing_problems[0]
    current_entry = _problem_entry_from_brief(problem_brief, existing_entry=active_entry, generated_at=generated_at)
    current_id = current_entry["problem_entry_id"]
    problems: list[dict[str, Any]] = [current_entry]
    for entry in existing_problems:
        if entry.get("problem_entry_id") == current_id:
            continue
        problems.append(entry)
    summary = current_entry["problem_summary"][:160]
    return {
        "schema_version": "1.0.0",
        "problem_register_id": existing_register.get("problem_register_id", f"problem_register_{workspace_id}"),
        "workspace_id": workspace_id,
        "current_problem_entry_id": current_id,
        "problem_summary": summary,
        "problems": problems,
        "created_at": existing_register.get("created_at", generated_at),
        "updated_at": generated_at,
    }


def _competitor_entry_from_item(
    competitor: dict[str, Any],
    *,
    competitor_dossier: dict[str, Any],
    related_problem_ids: list[str],
    existing_entry: dict[str, Any] | None = None,
    monitoring: dict[str, Any] | None = None,
    generated_at: str,
) -> dict[str, Any]:
    existing_entry = existing_entry or {}
    name = competitor.get("name", "Competitor")
    competitor_entry_id = existing_entry.get("competitor_entry_id") or f"competitor_entry_{_slug(name)}"
    summary = competitor.get("positioning_summary") or competitor.get("positioning_gap") or name
    source_artifact_ids = _clean_strings(
        [
            *existing_entry.get("source_artifact_ids", []),
            competitor_dossier.get("competitor_dossier_id", ""),
            *competitor_dossier.get("source_artifact_ids", []),
        ]
    )
    evidence_refs = _clean_strings(
        [
            *existing_entry.get("evidence_refs", []),
            *(competitor.get("evidence_refs") or []),
        ]
    )
    status = existing_entry.get("status", "tracked")
    if monitoring is not None and (
        monitoring.get("health_status") in {"empty", "unconfigured", "error"}
        or monitoring.get("cadence_status") in {"due", "stale", "unknown"}
    ):
        status = "watch"
    return {
        "competitor_entry_id": competitor_entry_id,
        "name": name,
        "status": status,
        "summary": summary,
        "source_artifact_ids": source_artifact_ids,
        "evidence_refs": evidence_refs,
        "related_problem_ids": _clean_strings(related_problem_ids or existing_entry.get("related_problem_ids", [])),
        "current_competitor_dossier_id": competitor_dossier.get("competitor_dossier_id", ""),
        "freshness_status": _freshness_status(
            competitor.get("last_checked_at"),
            competitor_dossier.get("last_refreshed_at"),
            competitor_dossier.get("created_at"),
            generated_at,
        ),
        "tags": _clean_strings(existing_entry.get("tags", [])),
        "last_updated_at": generated_at,
        **({"monitoring": monitoring} if monitoring is not None else {}),
    }


def build_competitor_registry(
    workspace_id: str,
    competitor_dossier: dict[str, Any],
    *,
    generated_at: str | None = None,
    existing_registry: dict[str, Any] | None = None,
    feed_registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    generated_at = generated_at or _now_iso()
    existing_registry = existing_registry or {}
    incoming_dossier_id = str(competitor_dossier.get("competitor_dossier_id", ""))
    existing_entries_raw = existing_registry.get("competitors", []) if isinstance(existing_registry.get("competitors"), list) else []
    if existing_registry.get("workspace_id") != workspace_id or (
        existing_entries_raw
        and all(
            _is_starter_seed(
                str(entry.get("current_competitor_dossier_id", "")),
                *[str(item) for item in entry.get("source_artifact_ids", [])],
            )
            for entry in existing_entries_raw
        )
        and not _is_starter_seed(incoming_dossier_id)
    ):
        existing_registry = {}
    existing_entries = existing_registry.get("competitors", []) if isinstance(existing_registry.get("competitors"), list) else []
    related_problem_ids = [
        ref["entity_id"]
        for ref in competitor_dossier.get("linked_entity_refs", [])
        if ref.get("entity_type") == "problem" and isinstance(ref.get("entity_id"), str)
    ]
    monitoring = _monitoring_summary(feed_registry)
    competitor_entries: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for competitor in competitor_dossier.get("competitors", []):
        name = competitor.get("name", "")
        existing_entry = next((item for item in existing_entries if item.get("name") == name), None)
        entry = _competitor_entry_from_item(
            competitor,
            competitor_dossier=competitor_dossier,
            related_problem_ids=related_problem_ids,
            existing_entry=existing_entry,
            monitoring=monitoring,
            generated_at=generated_at,
        )
        competitor_entries.append(entry)
        seen_ids.add(entry["competitor_entry_id"])
    for entry in existing_entries:
        if entry.get("competitor_entry_id") in seen_ids:
            continue
        competitor_entries.append(entry)
    summary = competitor_dossier.get("competitive_frame", "Competitor tracking state")
    if monitoring is not None:
        summary = (
            f"{summary} Monitoring: {monitoring['health_status']} / {monitoring['cadence_status']}."
        )[:160]
    return {
        "schema_version": "1.0.0",
        "competitor_registry_id": existing_registry.get("competitor_registry_id", f"competitor_registry_{workspace_id}"),
        "workspace_id": workspace_id,
        "registry_summary": summary[:160],
        "competitors": competitor_entries,
        "created_at": existing_registry.get("created_at", generated_at),
        "updated_at": generated_at,
    }


def load_problem_register(
    workspace_dir: Path | str,
    *,
    generated_at: str | None = None,
    persist: bool = False,
) -> dict[str, Any] | None:
    workspace_path = Path(workspace_dir).resolve()
    register_path = workspace_path / "artifacts" / "problem_register.json"
    if register_path.exists():
        return _load_json(register_path)
    problem_brief_path = workspace_path / "artifacts" / "problem_brief.json"
    if not problem_brief_path.exists():
        return None
    problem_brief = _load_json(problem_brief_path)
    payload = build_problem_register(
        problem_brief.get("workspace_id", workspace_path.name),
        problem_brief,
        generated_at=generated_at,
    )
    if persist:
        _write_json(register_path, payload)
        _append_manifest_artifact_path(workspace_path, "artifacts/problem_register.json")
    return payload


def load_competitor_registry(
    workspace_dir: Path | str,
    *,
    generated_at: str | None = None,
    persist: bool = False,
) -> dict[str, Any] | None:
    workspace_path = Path(workspace_dir).resolve()
    register_path = workspace_path / "artifacts" / "competitor_registry.json"
    dossier_path = workspace_path / "artifacts" / "competitor_dossier.json"
    feed_registry_path = workspace_path / "artifacts" / "external_research_feed_registry.json"
    if register_path.exists():
        existing = _load_json(register_path)
        if dossier_path.exists() and feed_registry_path.exists():
            payload = build_competitor_registry(
                existing.get("workspace_id", workspace_path.name),
                _load_json(dossier_path),
                generated_at=generated_at,
                existing_registry=existing,
                feed_registry=_load_json(feed_registry_path),
            )
            if persist:
                _write_json(register_path, payload)
                _append_manifest_artifact_path(workspace_path, "artifacts/competitor_registry.json")
            return payload
        return existing
    if not dossier_path.exists():
        return None
    dossier = _load_json(dossier_path)
    feed_registry = _load_json(feed_registry_path) if feed_registry_path.exists() else None
    payload = build_competitor_registry(
        dossier.get("workspace_id", workspace_path.name),
        dossier,
        generated_at=generated_at,
        feed_registry=feed_registry,
    )
    if persist:
        _write_json(register_path, payload)
        _append_manifest_artifact_path(workspace_path, "artifacts/competitor_registry.json")
    return payload


def sync_memory_registers(
    workspace_dir: Path | str,
    *,
    generated_at: str,
    problem_brief: dict[str, Any] | None = None,
    competitor_dossier: dict[str, Any] | None = None,
    feed_registry: dict[str, Any] | None = None,
) -> list[str]:
    workspace_path = Path(workspace_dir).resolve()
    artifacts_dir = workspace_path / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    synced_files: list[str] = []
    if problem_brief is not None:
        register_path = artifacts_dir / "problem_register.json"
        existing = _load_json(register_path) if register_path.exists() else None
        payload = build_problem_register(
            problem_brief.get("workspace_id", workspace_path.name),
            problem_brief,
            generated_at=generated_at,
            existing_register=existing,
        )
        _write_json(register_path, payload)
        _append_manifest_artifact_path(workspace_path, "artifacts/problem_register.json")
        synced_files.append("problem_register.json")
    if competitor_dossier is not None:
        register_path = artifacts_dir / "competitor_registry.json"
        existing = _load_json(register_path) if register_path.exists() else None
        payload = build_competitor_registry(
            competitor_dossier.get("workspace_id", workspace_path.name),
            competitor_dossier,
            generated_at=generated_at,
            existing_registry=existing,
            feed_registry=feed_registry,
        )
        _write_json(register_path, payload)
        _append_manifest_artifact_path(workspace_path, "artifacts/competitor_registry.json")
        synced_files.append("competitor_registry.json")
    return synced_files


def collect_memory_review_items(workspace_dir: Path | str) -> dict[str, int]:
    workspace_path = Path(workspace_dir).resolve()
    proposal_paths = sorted((workspace_path / "outputs" / "operate").glob("*.pm_note_delta_proposal.json"))
    pending_items = 0
    problem_candidates = 0
    competitor_candidates = 0
    for path in proposal_paths:
        payload = _load_json(path)
        candidates = payload.get("memory_candidates", [])
        pending_items += len(candidates)
        problem_candidates += sum(1 for item in candidates if item.get("candidate_type") == "problem")
        competitor_candidates += sum(1 for item in candidates if item.get("candidate_type") == "competitor")
    return {
        "proposal_file_count": len(proposal_paths),
        "pending_items": pending_items,
        "problem_candidates": problem_candidates,
        "competitor_candidates": competitor_candidates,
    }
