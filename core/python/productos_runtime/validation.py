from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SOURCE_NOTE_CARD_PREFIX = "source_note_card_"
SOURCE_NOTE_CARD_REFERENCE_FIELDS = {
    "source_note_card_ids",
    "supporting_source_note_card_ids",
}


def _load_workspace_artifacts(workspace_dir: Path) -> tuple[list[tuple[Path, dict[str, Any]]], list[str]]:
    artifacts_dir = workspace_dir / "artifacts"
    if not artifacts_dir.exists():
        return [], [f"Missing artifacts directory: {artifacts_dir}"]

    artifacts: list[tuple[Path, dict[str, Any]]] = []
    failures: list[str] = []

    for artifact_path in sorted(artifacts_dir.glob("*.json")):
        try:
            with artifact_path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except json.JSONDecodeError as exc:
            failures.append(f"{artifact_path.relative_to(workspace_dir).as_posix()}: invalid JSON ({exc.msg})")
            continue

        if not isinstance(payload, dict):
            failures.append(f"{artifact_path.relative_to(workspace_dir).as_posix()}: top-level JSON payload must be an object")
            continue

        artifacts.append((artifact_path, payload))

    return artifacts, failures


def _collect_source_note_card_ids(
    workspace_dir: Path,
    artifacts: list[tuple[Path, dict[str, Any]]],
) -> tuple[set[str], list[str]]:
    indexed_ids: set[str] = set()
    failures: list[str] = []

    for artifact_path, payload in artifacts:
        source_note_card_id = payload.get("source_note_card_id")
        if not isinstance(source_note_card_id, str):
            continue
        if source_note_card_id in indexed_ids:
            failures.append(
                f"{artifact_path.relative_to(workspace_dir).as_posix()}: duplicate source_note_card_id '{source_note_card_id}'"
            )
            continue
        indexed_ids.add(source_note_card_id)

    return indexed_ids, failures


def _format_json_path(path_parts: tuple[Any, ...]) -> str:
    return ".".join(str(part) for part in path_parts) or "<root>"


def _iter_source_note_card_refs(payload: Any, path_parts: tuple[Any, ...] = ()) -> Any:
    if isinstance(payload, dict):
        for key, value in payload.items():
            next_path = (*path_parts, key)
            if key in SOURCE_NOTE_CARD_REFERENCE_FIELDS and isinstance(value, list):
                for index, item in enumerate(value):
                    if isinstance(item, str):
                        yield (*next_path, index), item
                continue

            if key == "evidence_refs" and isinstance(value, list):
                for index, item in enumerate(value):
                    if isinstance(item, str) and item.startswith(SOURCE_NOTE_CARD_PREFIX):
                        yield (*next_path, index), item

            yield from _iter_source_note_card_refs(value, next_path)
        return

    if isinstance(payload, list):
        for index, item in enumerate(payload):
            yield from _iter_source_note_card_refs(item, (*path_parts, index))


def inspect_workspace_source_note_card_refs(workspace_dir: Path) -> tuple[dict[str, int], list[str]]:
    artifacts, failures = _load_workspace_artifacts(workspace_dir)
    indexed_ids, id_failures = _collect_source_note_card_ids(workspace_dir, artifacts)
    failures.extend(id_failures)

    for artifact_path, payload in artifacts:
        for ref_path, source_note_card_id in _iter_source_note_card_refs(payload):
            if source_note_card_id not in indexed_ids:
                failures.append(
                    f"{artifact_path.relative_to(workspace_dir).as_posix()}:{_format_json_path(ref_path)} "
                    f"references missing source note card '{source_note_card_id}'"
                )

    summary = {
        "artifact_count": len(artifacts),
        "source_note_card_count": len(indexed_ids),
    }
    return summary, failures
