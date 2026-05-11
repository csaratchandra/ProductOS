"""ProductOS V11 Living System: Auto-propagation engine for artifact regeneration."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _load_json_if_exists(path: Path) -> dict | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _default_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _artifact_path(workspace_dir: Path, artifact_ref: str) -> Path:
    if artifact_ref.startswith("artifacts/"):
        return workspace_dir / artifact_ref
    return workspace_dir / artifact_ref


def _backup_path(path: Path) -> Path:
    return path.with_suffix(".prev.json")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def classify_impact(source_change: dict[str, Any], target_artifact: dict[str, Any]) -> str:
    """Classify the impact of a source change on a target artifact.
    
    Returns one of: mechanical, content_deep, structural
    """
    source_type = source_change.get("event_type", "")
    target_type = target_artifact.get("schema_version", "")
    
    # Structural changes: schema changes, new required fields
    if source_type == "artifact_updated":
        source_keys = set(source_change.get("changed_keys", []))
        target_keys = set(target_artifact.keys())
        new_keys = source_keys - target_keys
        if any("schema" in key.lower() or "required" in key.lower() for key in new_keys):
            return "structural"
    
    # Content-deep changes: strategy, positioning, scope, competitive claims
    content_deep_indicators = [
        "strategy", "positioning", "scope", "claim", "pricing",
        "competitive", "persona", "journey", "problem", "solution",
        "hypothesis", "risk", "market"
    ]
    
    change_summary = source_change.get("change_summary", "").lower()
    if any(indicator in change_summary for indicator in content_deep_indicators):
        return "content_deep"
    
    # Mechanical changes: reference updates, date stamps, version bumps
    mechanical_indicators = [
        "version", "date", "timestamp", "reference", "link",
        "updated_at", "generated_at", "count", "status"
    ]
    
    if any(indicator in change_summary for indicator in mechanical_indicators):
        return "mechanical"
    
    # Default to content_deep for safety
    return "content_deep"


def generate_delta_preview(source_change: dict[str, Any], target_artifact: dict[str, Any]) -> str:
    """Generate a human-readable description of what would change."""
    impact = classify_impact(source_change, target_artifact)
    source_type = source_change.get("event_type", "unknown")
    change_summary = source_change.get("change_summary", "unspecified change")
    
    target_id = target_artifact.get("artifact_id", target_artifact.get("title", "unknown artifact"))
    
    if impact == "mechanical":
        return f"Mechanical update: {change_summary} → {target_id} (auto-executable)"
    elif impact == "content_deep":
        return f"Content-deep change: {change_summary} → {target_id} (requires PM review)"
    else:
        return f"Structural change: {change_summary} → {target_id} (requires PM review and schema validation)"


def build_regeneration_queue(
    trigger_event: dict[str, Any],
    workspace_dir: Path,
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build a regeneration queue from a trigger event.
    
    Analyzes the trigger event, identifies affected downstream artifacts,
    classifies impact, and creates queued items with delta previews.
    """
    if generated_at is None:
        generated_at = _default_timestamp()
    
    source_ref = trigger_event.get("source_artifact_ref", "")
    change_summary = trigger_event.get("change_summary", "")
    
    # Load impact propagation map if it exists
    impact_map_path = workspace_dir / "artifacts" / "impact_propagation_map.json"
    downstream_refs = []
    if impact_map_path.exists():
        impact_map = _load_json_if_exists(impact_map_path) or {}
        downstream_refs = impact_map.get("dependencies", {}).get(source_ref, [])
    
    # Build queued items for each downstream artifact
    queued_items = []
    dependency_sequence = []
    auto_executed_count = 0
    pm_review_count = 0
    
    for idx, target_ref in enumerate(downstream_refs):
        target_path = _artifact_path(workspace_dir, target_ref)
        if not target_path.exists():
            continue
        
        target_artifact = _load_json_if_exists(target_path) or {}
        impact = classify_impact(trigger_event, target_artifact)
        delta_preview = generate_delta_preview(trigger_event, target_artifact)
        
        if impact == "mechanical":
            mode = "auto"
            status = "pending"
            auto_executed_count += 1
        elif impact == "structural":
            mode = "pm_review"
            status = "pending"
            pm_review_count += 1
        else:
            mode = "pm_review"
            status = "pending"
            pm_review_count += 1
        
        item_id = f"rq_item_{idx + 1:03d}"
        queued_items.append({
            "item_id": item_id,
            "target_artifact_ref": target_ref,
            "impact_classification": impact,
            "regeneration_mode": mode,
            "status": status,
            "delta_preview": delta_preview,
            "pm_note": "",
            "execution_log": []
        })
        dependency_sequence.append(target_ref)
    
    queue_id = f"rq_{workspace_dir.name}_{generated_at[:10].replace('-', '')}"
    
    return {
        "schema_version": "1.0.0",
        "regeneration_queue_id": queue_id,
        "workspace_id": workspace_dir.name,
        "trigger_event": trigger_event,
        "queued_items": queued_items,
        "dependency_sequence": dependency_sequence,
        "status": "active" if queued_items else "completed",
        "pm_review_required": pm_review_count > 0,
        "auto_executed_count": auto_executed_count,
        "pm_review_count": pm_review_count,
        "generated_at": generated_at
    }


def process_regeneration_item(
    item: dict[str, Any],
    workspace_dir: Path,
    *,
    action: str = "approve",
    pm_note: str = "",
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Process a single regeneration queue item.
    
    Actions: approve, reject, modify
    For mechanical items with approve action, auto-execute the change.
    For content-deep items, update status based on PM action.
    """
    if generated_at is None:
        generated_at = _default_timestamp()
    
    target_ref = item.get("target_artifact_ref", "")
    impact = item.get("impact_classification", "content_deep")
    target_path = _artifact_path(workspace_dir, target_ref)
    
    updated_item = dict(item)
    updated_item["executed_at"] = generated_at
    updated_item["pm_note"] = pm_note
    
    if action == "reject":
        updated_item["status"] = "rejected"
        updated_item["execution_log"].append(
            f"[{generated_at}] Rejected by PM: {pm_note or 'No reason provided'}"
        )
        return updated_item
    
    if impact == "mechanical" and action == "approve":
        # Auto-execute mechanical changes
        if target_path.exists():
            target_artifact = _load_json_if_exists(target_path) or {}
            _write_json(_backup_path(target_path), target_artifact)
            # Update timestamp and version
            target_artifact["updated_at"] = generated_at
            target_artifact["version"] = target_artifact.get("version", 1) + 1
            _write_json(target_path, target_artifact)
        
        updated_item["status"] = "auto_executed"
        updated_item["execution_log"].append(
            f"[{generated_at}] Auto-executed mechanical update"
        )
        return updated_item
    
    if action in ("approve", "modify"):
        updated_item["status"] = "approved"
        updated_item["execution_log"].append(
            f"[{generated_at}] Approved by PM: {pm_note or 'No additional notes'}"
        )
        return updated_item
    
    return updated_item


def detect_circular_dependencies(
    dependency_sequence: list[str],
    workspace_dir: Path,
) -> list[str] | None:
    """Detect circular dependencies in the artifact graph.
    
    Returns list of artifact refs involved in circular dependency, or None if clean.
    """
    graph = {}
    for ref in dependency_sequence:
        target_path = _artifact_path(workspace_dir, ref)
        if target_path.exists():
            artifact = _load_json_if_exists(target_path) or {}
            graph[ref] = artifact.get("dependencies", [])
    
    visited = set()
    rec_stack = set()
    circular = []
    
    def dfs(node: str, path: list[str]) -> bool:
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor, path):
                    return True
            elif neighbor in rec_stack:
                cycle_start = path.index(neighbor)
                circular.extend(path[cycle_start:])
                return True
        
        path.pop()
        rec_stack.discard(node)
        return False
    
    for node in graph:
        if node not in visited:
            if dfs(node, []):
                return circular
    
    return None


def generate_impact_propagation_map(workspace_dir: Path) -> dict[str, Any]:
    """Auto-generate an impact_propagation_map.json by scanning artifact cross-references.

    Inspects all JSON artifacts in artifacts/ for fields that reference other
    artifacts (source_artifact_ids, upstream_artifact_ids, target_persona_refs,
    source_evidence_refs, etc.) and builds a dependency DAG.
    """
    artifact_dir = workspace_dir / "artifacts"
    dependencies: dict[str, list[str]] = {}
    artifact_ids: set[str] = set()

    for path in artifact_dir.glob("*.json"):
        data = _load_json_if_exists(path)
        if not isinstance(data, dict):
            continue
        aid = data.get("artifact_id") or data.get("problem_brief_id") or data.get("persona_pack_id")
        if aid:
            artifact_ids.add(aid)
        # Normalize artifact ref to relative path under artifacts/
        ref = "artifacts/" + path.name

    for path in artifact_dir.glob("*.json"):
        data = _load_json_if_exists(path)
        if not isinstance(data, dict):
            continue
        ref = "artifacts/" + path.name
        deps: list[str] = []
        # Common reference fields
        for key in ("source_artifact_ids", "upstream_artifact_ids", "source_evidence_refs"):
            for dref in data.get(key, []):
                if isinstance(dref, str):
                    candidate = _resolve_ref(dref, artifact_dir)
                    if candidate:
                        deps.append(candidate)
        # Nested refs (e.g., persona_pack segment_refs)
        for nested in ("segment_refs", "target_persona_refs", "linked_entity_refs", "evidence_refs"):
            for item in data.get(nested, []):
                if isinstance(item, dict):
                    eid = item.get("entity_id", "")
                    candidate = _resolve_ref(eid, artifact_dir)
                    if candidate:
                        deps.append(candidate)
                elif isinstance(item, str):
                    candidate = _resolve_ref(item, artifact_dir)
                    if candidate:
                        deps.append(candidate)
        # Deduplicate and store reverse mapping (who depends on whom)
        unique_deps = sorted(set(deps))
        for dep in unique_deps:
            dependencies.setdefault(dep, []).append(ref)

    # Add explicit high-priority edge: persona -> customer_journey_map
    persona_refs = ["artifacts/persona_pack.json", "artifacts/persona_pack.example.json"]
    cjm_refs = ["artifacts/customer_journey_map.json"]
    for pref in persona_refs:
        p = workspace_dir / pref
        if p.exists():
            for cjm in cjm_refs:
                dependencies.setdefault(pref, []).append(cjm)

    # Deduplicate
    for k, v in dependencies.items():
        dependencies[k] = sorted(set(v))

    return {
        "schema_version": "1.0.0",
        "propagation_map_id": f"ipm_{workspace_dir.name}_{_default_timestamp()[:10].replace('-', '')}",
        "workspace_id": workspace_dir.name,
        "dependencies": dependencies,
        "generated_at": _default_timestamp(),
    }


def _resolve_ref(ref: str, artifact_dir: Path) -> str | None:
    """Try to map a loose ref string to a known artifact file name."""
    # Strip artifacts/ prefix if present for filesystem lookup
    bare_ref = ref
    if bare_ref.startswith("artifacts/"):
        bare_ref = bare_ref[len("artifacts/"):]
    # Direct file name match
    if (artifact_dir / bare_ref).exists():
        return "artifacts/" + bare_ref
    # Try common patterns
    candidates = [
        bare_ref + ".json",
        bare_ref.replace("_", "-") + ".json",
        bare_ref.replace("-", "_") + ".json",
    ]
    for c in candidates:
        if (artifact_dir / c).exists():
            return "artifacts/" + c
    # Fuzzy: any file containing the ref as substring
    for path in artifact_dir.glob("*.json"):
        if bare_ref in path.name:
            return "artifacts/" + path.name
    return None


def process_regeneration_item(
    item: dict[str, Any],
    workspace_dir: Path,
    *,
    action: str = "approve",
    pm_note: str = "",
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Process a single regeneration queue item.
    
    Actions: approve, reject, modify
    For mechanical items with approve action, auto-execute the change.
    For content_deep items, update status based on PM action and
    actually mutate target artifact content when approved.
    """
    if generated_at is None:
        generated_at = _default_timestamp()
    
    target_ref = item.get("target_artifact_ref", "")
    impact = item.get("impact_classification", "content_deep")
    target_path = _artifact_path(workspace_dir, target_ref)
    
    updated_item = dict(item)
    updated_item["executed_at"] = generated_at
    updated_item["pm_note"] = pm_note
    
    if action == "reject":
        updated_item["status"] = "rejected"
        updated_item["execution_log"].append(
            f"[{generated_at}] Rejected by PM: {pm_note or 'No reason provided'}"
        )
        return updated_item
    
    if impact == "mechanical" and action == "approve":
        # Auto-execute mechanical changes
        if target_path.exists():
            target_artifact = _load_json_if_exists(target_path) or {}
            # Update timestamp and version
            target_artifact["updated_at"] = generated_at
            target_artifact["version"] = target_artifact.get("version", 1) + 1
            
            with target_path.open("w", encoding="utf-8") as f:
                json.dump(target_artifact, f, indent=2)
                f.write("\n")
        
        updated_item["status"] = "auto_executed"
        updated_item["execution_log"].append(
            f"[{generated_at}] Auto-executed mechanical update"
        )
        return updated_item
    
    if impact in ("content_deep", "structural") and action == "approve":
        # Actually mutate content for content-deep changes
        if "customer_journey_map" in target_ref and target_path.exists():
            try:
                from .journey_synthesis import synthesize_customer_journey_map
                old_map = _load_json_if_exists(target_path) or {}
                new_map = synthesize_customer_journey_map(
                    workspace_dir,
                    generated_at=generated_at,
                )
                _write_json(_backup_path(target_path), old_map)
                _write_json(target_path, new_map)
                updated_item["status"] = "content_regenerated"
                updated_item["execution_log"].append(
                    f"[{generated_at}] Content-deep regeneration executed: customer_journey_map.json mutated"
                )
                return updated_item
            except Exception as exc:
                updated_item["status"] = "approved"
                updated_item["execution_log"].append(
                    f"[{generated_at}] Approved by PM but regeneration failed: {exc}"
                )
                return updated_item
        # Generic content-deep: bump version and timestamp as placeholder for future runtimes
        if target_path.exists():
            target_artifact = _load_json_if_exists(target_path) or {}
            _write_json(_backup_path(target_path), target_artifact)
            target_artifact["updated_at"] = generated_at
            target_artifact["version"] = target_artifact.get("version", 1) + 1
            _write_json(target_path, target_artifact)
        updated_item["status"] = "approved"
        updated_item["execution_log"].append(
            f"[{generated_at}] Approved by PM: {pm_note or 'Content-deep change acknowledged, awaiting dedicated runtime'}"
        )
        return updated_item
    
    if action in ("approve", "modify"):
        updated_item["status"] = "approved"
        updated_item["execution_log"].append(
            f"[{generated_at}] Approved by PM: {pm_note or 'No additional notes'}"
        )
        return updated_item
    
    return updated_item
