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
