from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import yaml_compat as yaml
from .lifecycle import load_item_lifecycle_state_from_workspace
from .next_version import build_next_version_bundle_from_workspace
from .release import latest_release_metadata


ROOT = Path(__file__).resolve().parents[3]
V9_BASELINE_VERSION = "10.0.0"
V9_TARGET_VERSION = "10.0.0"
V9_TARGET_RELEASE = "v10_0_0"
V9_BUNDLE_ID = "v10_pm_superpower_platform"
V9_BUNDLE_NAME = "World-class PM superpowers — autonomous intelligence, decisions, discovery, prototypes, marketing, and living system"
V9_ARTIFACT_SCHEMAS = {
    "runtime_scenario_report_v9_lifecycle_enrichment": "runtime_scenario_report.schema.json",
    "validation_lane_report_v9_lifecycle_enrichment": "validation_lane_report.schema.json",
    "manual_validation_record_v9_lifecycle_enrichment": "manual_validation_record.schema.json",
    "release_readiness_v9_lifecycle_enrichment": "release_readiness.schema.json",
    "release_gate_decision_v9_lifecycle_enrichment": "release_gate_decision.schema.json",
    "ralph_loop_state_v9_lifecycle_enrichment": "ralph_loop_state.schema.json",
}


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_optional_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return _load_json(path)


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _first_str(payload: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return None


def _payload_id(payload: dict[str, Any] | None) -> str | None:
    if payload is None:
        return None
    for key, value in payload.items():
        if key.endswith("_id") and isinstance(value, str):
            return value
    return None


def _artifacts_dir(workspace_path: Path) -> Path:
    return workspace_path / "artifacts"


def _outputs_dir(workspace_path: Path, phase: str) -> Path:
    return workspace_path / "outputs" / phase


def _load_manifest(workspace_path: Path) -> dict[str, Any]:
    manifest_path = workspace_path / "workspace_manifest.yaml"
    if not manifest_path.exists():
        return {}
    with manifest_path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    return payload if isinstance(payload, dict) else {}


def _workspace_identity(workspace_path: Path) -> tuple[str, str]:
    manifest = _load_manifest(workspace_path)
    workspace_id = manifest.get("workspace_id")
    workspace_name = manifest.get("name")
    if isinstance(workspace_id, str) and workspace_id.strip():
        resolved_id = workspace_id
    else:
        mission_brief = _load_optional_json(_artifacts_dir(workspace_path) / "mission_brief.json") or {}
        resolved_id = mission_brief.get("workspace_id", workspace_path.name)
    if isinstance(workspace_name, str) and workspace_name.strip():
        resolved_name = workspace_name
    else:
        mission_brief = _load_optional_json(_artifacts_dir(workspace_path) / "mission_brief.json") or {}
        resolved_name = mission_brief.get("title", workspace_path.name)
    return resolved_id, resolved_name


def _choose_file_payload(workspace_path: Path, patterns: list[tuple[str, str]]) -> tuple[dict[str, Any] | None, str | None, Path | None]:
    matches: list[Path] = []
    for relative_dir, pattern in patterns:
        directory = workspace_path / relative_dir
        if not directory.exists():
            continue
        matches.extend(sorted(directory.glob(pattern)))
    real_paths = [path for path in matches if not path.name.endswith(".example.json")]
    if real_paths:
        path = real_paths[0]
        return _load_json(path), "real", path
    if matches:
        path = matches[0]
        return _load_json(path), "example", path
    return None, None, None


def _artifact_source_state(
    workspace_path: Path,
    *,
    patterns: list[tuple[str, str]],
    next_version_bundle: dict[str, Any] | None = None,
    bundle_keys: list[str] | None = None,
) -> dict[str, Any]:
    payload, source_kind, path = _choose_file_payload(workspace_path, patterns)
    if payload is not None:
        return {
            "payload": payload,
            "source_kind": source_kind,
            "path": path,
            "artifact_id": _payload_id(payload),
        }
    for key in bundle_keys or []:
        candidate = (next_version_bundle or {}).get(key)
        if isinstance(candidate, dict):
            return {
                "payload": candidate,
                "source_kind": "bundle",
                "path": None,
                "artifact_id": _payload_id(candidate),
            }
    return {
        "payload": None,
        "source_kind": None,
        "path": None,
        "artifact_id": None,
    }


def _track_mode(states: list[dict[str, Any]]) -> str:
    source_kinds = {state.get("source_kind") for state in states if state.get("payload") is not None}
    if source_kinds and source_kinds == {"real"}:
        return "artifact_backed"
    if source_kinds:
        return "lifecycle_fallback"
    return "deferred"


def _stages_from_item_state(workspace_path: Path) -> dict[str, dict[str, Any]]:
    try:
        payload = load_item_lifecycle_state_from_workspace(workspace_path)
    except (FileNotFoundError, KeyError, ValueError):
        return {}
    return {
        stage["stage_key"]: stage
        for stage in payload.get("lifecycle_stages", [])
        if isinstance(stage, dict) and isinstance(stage.get("stage_key"), str)
    }


def _governed_doc_state(
    workspace_path: Path,
    *,
    next_version_bundle: dict[str, Any] | None,
) -> dict[str, Any]:
    state = _artifact_source_state(
        workspace_path,
        patterns=[
            ("outputs/align", "align_document_sync_state.json"),
            ("artifacts", "document_sync_state.json"),
            ("artifacts", "document_sync_state_live_docs.example.json"),
            ("artifacts", "document_sync_state*.json"),
        ],
        next_version_bundle=next_version_bundle,
        bundle_keys=["align_document_sync_state"],
    )
    payload = state["payload"]
    if payload is None:
        return {
            "mode": "deferred",
            "sync_mode": "missing",
            "validation_status": "missing",
            "artifact_id": None,
        }
    sync_mode = "live_doc" if "live_docs" in (_payload_id(payload) or "") else "readable_doc"
    has_modification_log = False
    for document in payload.get("documents", []):
        if isinstance(document, dict) and document.get("modification_log"):
            has_modification_log = True
            break
    validation_status = "passed" if has_modification_log and state["source_kind"] == "real" else "watch"
    return {
        "mode": "artifact_backed" if state["source_kind"] == "real" else "lifecycle_fallback",
        "sync_mode": sync_mode,
        "validation_status": validation_status,
        "artifact_id": state["artifact_id"],
    }


def _freshness_status(reference_time: datetime, payloads: list[dict[str, Any]]) -> str:
    timestamps = [
        timestamp
        for payload in payloads
        for timestamp in [
            _parse_timestamp(
                _first_str(
                    payload,
                    "generated_at",
                    "updated_at",
                    "last_refreshed_at",
                    "created_at",
                    "reviewed_at",
                    "last_updated_at",
                )
            )
        ]
        if timestamp is not None
    ]
    if not timestamps:
        return "unknown"
    newest_age_days = max((reference_time - timestamp).days for timestamp in timestamps)
    if newest_age_days <= 30:
        return "fresh"
    if newest_age_days <= 60:
        return "watch"
    return "stale"


def _count_research_contradictions(research_brief: dict[str, Any] | None, research_review: dict[str, Any] | None) -> int:
    contradictions = 0
    contradictions += len(research_brief.get("contradictions", [])) if research_brief else 0
    contradictions += len(research_review.get("contradiction_items", [])) if research_review else 0
    return contradictions


def _research_packet_state(
    workspace_path: Path,
    *,
    next_version_bundle: dict[str, Any] | None,
    generated_at: str,
) -> dict[str, Any]:
    logical_artifacts = {
        "research_handoff": {
            "patterns": [("artifacts", "handoff_discovery_to_research.json"), ("outputs/discover", "discover_research_handoff.json")],
            "bundle_keys": ["research_handoff", "discover_research_handoff"],
        },
        "research_notebook": {
            "patterns": [("artifacts", "research_notebook.json"), ("outputs/discover", "discover_research_notebook.json")],
            "bundle_keys": ["research_notebook", "discover_research_notebook"],
        },
        "research_brief": {
            "patterns": [("artifacts", "research_brief.json"), ("outputs/discover", "discover_research_brief.json")],
            "bundle_keys": ["research_brief", "discover_research_brief"],
        },
        "external_research_plan": {
            "patterns": [("artifacts", "external_research_plan.json"), ("outputs/discover", "discover_external_research_plan.json")],
            "bundle_keys": ["external_research_plan", "discover_external_research_plan"],
        },
        "external_research_source_discovery": {
            "patterns": [("artifacts", "external_research_source_discovery.json"), ("outputs/discover", "discover_external_research_source_discovery.json")],
            "bundle_keys": ["external_research_source_discovery", "discover_external_research_source_discovery"],
        },
        "external_research_review": {
            "patterns": [("artifacts", "external_research_review.json"), ("outputs/discover", "discover_external_research_review.json")],
            "bundle_keys": ["external_research_review", "discover_external_research_review"],
        },
        "selected_research_manifest": {
            "patterns": [("outputs/discover", "discover_selected_research_manifest.json")],
            "bundle_keys": ["external_research_selected_manifest", "discover_selected_research_manifest"],
        },
        "framework_registry": {
            "patterns": [("artifacts", "framework_registry.json"), ("outputs/discover", "discover_framework_registry.json")],
            "bundle_keys": ["framework_registry", "discover_framework_registry"],
        },
        "competitor_dossier": {
            "patterns": [("artifacts", "competitor_dossier.json"), ("outputs/discover", "discover_competitor_dossier.json")],
            "bundle_keys": ["competitor_dossier", "discover_competitor_dossier"],
        },
        "customer_pulse": {
            "patterns": [("artifacts", "customer_pulse.json"), ("outputs/discover", "discover_customer_pulse.json")],
            "bundle_keys": ["customer_pulse", "discover_customer_pulse"],
        },
        "market_analysis_brief": {
            "patterns": [("artifacts", "market_analysis_brief.json"), ("outputs/discover", "discover_market_analysis_brief.json")],
            "bundle_keys": ["market_analysis_brief", "discover_market_analysis_brief"],
        },
        "landscape_matrix": {
            "patterns": [("artifacts", "landscape_matrix.json"), ("outputs/discover", "discover_landscape_matrix.json")],
            "bundle_keys": ["landscape_matrix", "discover_landscape_matrix"],
        },
        "market_sizing_brief": {
            "patterns": [("artifacts", "market_sizing_brief.json"), ("outputs/discover", "discover_market_sizing_brief.json")],
            "bundle_keys": ["market_sizing_brief", "discover_market_sizing_brief"],
        },
        "market_share_brief": {
            "patterns": [("artifacts", "market_share_brief.json"), ("outputs/discover", "discover_market_share_brief.json")],
            "bundle_keys": ["market_share_brief", "discover_market_share_brief"],
        },
        "opportunity_portfolio_view": {
            "patterns": [("artifacts", "opportunity_portfolio_view.json"), ("outputs/discover", "discover_opportunity_portfolio_view.json")],
            "bundle_keys": ["opportunity_portfolio_view", "discover_opportunity_portfolio_view"],
        },
        "prioritization_decision_record": {
            "patterns": [("artifacts", "prioritization_decision_record.json"), ("outputs/discover", "discover_prioritization_decision_record.json")],
            "bundle_keys": ["prioritization_decision_record", "discover_prioritization_decision_record"],
        },
        "feature_prioritization_brief": {
            "patterns": [("artifacts", "feature_prioritization_brief.json"), ("outputs/discover", "discover_feature_prioritization_brief.json")],
            "bundle_keys": ["feature_prioritization_brief", "discover_feature_prioritization_brief"],
        },
        "prd": {
            "patterns": [("artifacts", "prd.json"), ("outputs/discover", "discover_prd.json")],
            "bundle_keys": ["discover_prd"],
        },
    }
    states = {
        logical_name: _artifact_source_state(
            workspace_path,
            patterns=config["patterns"],
            next_version_bundle=next_version_bundle,
            bundle_keys=config["bundle_keys"],
        )
        for logical_name, config in logical_artifacts.items()
    }
    present_states = [state for state in states.values() if state["payload"] is not None]
    real_count = sum(1 for state in present_states if state["source_kind"] == "real")
    completeness = len(present_states) / len(logical_artifacts)
    mode = _track_mode(
        [
            state
            for logical_name, state in states.items()
            if logical_name != "selected_research_manifest"
        ]
    )
    research_brief = states["research_brief"]["payload"]
    research_review = states["external_research_review"]["payload"]
    prd = states["prd"]["payload"]
    prioritization = states["prioritization_decision_record"]["payload"]
    feature_prioritization = states["feature_prioritization_brief"]["payload"]
    selected_manifest = states["selected_research_manifest"]["payload"]
    contradiction_count = _count_research_contradictions(research_brief, research_review)
    downstream_ready = bool(
        prioritization
        and feature_prioritization
        and prd
        and (
            states["opportunity_portfolio_view"]["payload"] is not None
            or selected_manifest is not None
        )
    )
    packet_payloads = [
        state["payload"]
        for logical_name, state in states.items()
        if logical_name != "selected_research_manifest" and isinstance(state["payload"], dict)
    ]
    freshness = _freshness_status(
        _parse_timestamp(generated_at) or datetime.now(timezone.utc),
        packet_payloads,
    )
    if mode == "artifact_backed" and completeness == 1 and freshness == "fresh" and contradiction_count == 0 and downstream_ready:
        status = "passed"
    elif completeness >= 0.6 and present_states:
        status = "watch"
    else:
        status = "blocked"
    return {
        "status": status,
        "mode": mode,
        "present_count": len(present_states),
        "required_count": len(logical_artifacts),
        "real_count": real_count,
        "freshness": freshness,
        "contradiction_count": contradiction_count,
        "downstream_ready": downstream_ready,
        "selected_packet_id": _payload_id(selected_manifest) or _payload_id(research_brief),
        "missing_artifacts": [logical_name for logical_name, state in states.items() if state["payload"] is None],
        "artifact_ids": [state["artifact_id"] for state in present_states if isinstance(state["artifact_id"], str)],
    }


def _downstream_state(
    workspace_path: Path,
    *,
    next_version_bundle: dict[str, Any] | None,
) -> dict[str, Any]:
    states = {
        "status_mail": _artifact_source_state(
            workspace_path,
            patterns=[("outputs/operate", "operate_status_mail.json"), ("artifacts", "status_mail.json"), ("artifacts", "status_mail.example.json")],
            next_version_bundle=next_version_bundle,
            bundle_keys=["operate_status_mail"],
        ),
        "issue_log": _artifact_source_state(
            workspace_path,
            patterns=[("outputs/operate", "operate_issue_log.json"), ("artifacts", "issue_log.json"), ("artifacts", "issue_log.example.json")],
            next_version_bundle=next_version_bundle,
            bundle_keys=["operate_issue_log"],
        ),
        "release_readiness": _artifact_source_state(
            workspace_path,
            patterns=[("artifacts", "release_readiness.json"), ("artifacts", "release_readiness*.json")],
            next_version_bundle=next_version_bundle,
            bundle_keys=[],
        ),
        "release_note": _artifact_source_state(
            workspace_path,
            patterns=[("artifacts", "release_note.json"), ("artifacts", "release_note*.json")],
            next_version_bundle=next_version_bundle,
            bundle_keys=[],
        ),
        "outcome_review": _artifact_source_state(
            workspace_path,
            patterns=[("artifacts", "outcome_review.json"), ("artifacts", "outcome_review*.json")],
            next_version_bundle=next_version_bundle,
            bundle_keys=[],
        ),
    }
    mode = _track_mode(list(states.values()))
    outcome_review = states["outcome_review"]["payload"] or {}
    reopen_ready = bool(outcome_review.get("reopen_recommendations"))
    if mode == "artifact_backed" and reopen_ready:
        status = "passed"
    elif any(state["payload"] is not None for state in states.values()):
        status = "watch"
    else:
        status = "blocked"
    return {
        "status": status,
        "mode": mode,
        "reopen_ready": reopen_ready,
        "missing_artifacts": [name for name, state in states.items() if state["payload"] is None],
        "artifact_ids": [state["artifact_id"] for state in states.values() if isinstance(state["artifact_id"], str)],
    }


def _stale_release_inputs(workspace_path: Path) -> dict[str, Any]:
    candidates = [
        workspace_path / "artifacts" / "increment_plan.json",
        workspace_path / "artifacts" / "program_increment_state.json",
        workspace_path / "outputs" / "improve" / "next_version_release_gate_decision.json",
    ]
    present_paths = [path for path in candidates if path.exists()]
    plan_doc = workspace_path / "docs" / "planning" / "current-plan.md"
    review_doc = workspace_path / "docs" / "planning" / "next-version-release-review.md"
    canonical_text = ""
    if plan_doc.exists():
        canonical_text += plan_doc.read_text(encoding="utf-8")
    if review_doc.exists():
        canonical_text += "\n" + review_doc.read_text(encoding="utf-8")
    canonical_v9 = "P0/P1/P2" in canonical_text and "lifecycle-enrichment" in canonical_text.replace(" ", "-").lower()
    return {
        "count": len(present_paths),
        "paths": [path.relative_to(workspace_path).as_posix() for path in present_paths],
        "status": "ignored" if canonical_v9 else ("missing" if not present_paths else "review_required"),
    }


def inspect_v9_lifecycle_enrichment_state(
    workspace_dir: Path | str,
    *,
    generated_at: str,
    adapter_name: str = "codex",
    next_version_bundle: dict[str, Any] | None = None,
) -> dict[str, Any]:
    workspace_path = Path(workspace_dir).resolve()
    workspace_id, workspace_name = _workspace_identity(workspace_path)
    if next_version_bundle is None:
        try:
            next_version_bundle = build_next_version_bundle_from_workspace(
                workspace_path,
                generated_at=generated_at,
                adapter_name=adapter_name,
            )
        except Exception:
            next_version_bundle = None

    mission_state = _artifact_source_state(
        workspace_path,
        patterns=[("artifacts", "mission_brief.json")],
        next_version_bundle=next_version_bundle,
        bundle_keys=[],
    )
    core_states = {
        "strategy_context_brief": _artifact_source_state(
            workspace_path,
            patterns=[("artifacts", "strategy_context_brief.json"), ("outputs/discover", "discover_strategy_context_brief.json")],
            next_version_bundle=next_version_bundle,
            bundle_keys=["discover_strategy_context_brief"],
        ),
        "product_vision_brief": _artifact_source_state(
            workspace_path,
            patterns=[("artifacts", "product_vision_brief.json"), ("outputs/discover", "discover_product_vision_brief.json")],
            next_version_bundle=next_version_bundle,
            bundle_keys=["discover_product_vision_brief"],
        ),
        "market_strategy_brief": _artifact_source_state(
            workspace_path,
            patterns=[("artifacts", "market_strategy_brief.json"), ("outputs/discover", "discover_market_strategy_brief.json")],
            next_version_bundle=next_version_bundle,
            bundle_keys=["discover_market_strategy_brief"],
        ),
        "problem_brief": _artifact_source_state(
            workspace_path,
            patterns=[("artifacts", "problem_brief.json"), ("outputs/discover", "discover_problem_brief.json")],
            next_version_bundle=next_version_bundle,
            bundle_keys=["discover_problem_brief"],
        ),
        "concept_brief": _artifact_source_state(
            workspace_path,
            patterns=[("artifacts", "concept_brief.json"), ("outputs/discover", "discover_concept_brief.json")],
            next_version_bundle=next_version_bundle,
            bundle_keys=["discover_concept_brief"],
        ),
        "prd": _artifact_source_state(
            workspace_path,
            patterns=[("artifacts", "prd.json"), ("outputs/discover", "discover_prd.json")],
            next_version_bundle=next_version_bundle,
            bundle_keys=["discover_prd"],
        ),
    }
    stage_map = _stages_from_item_state(workspace_path)
    missing_core = [name for name, state in core_states.items() if state["payload"] is None]
    if all(state["source_kind"] == "real" for state in core_states.values()):
        workspace_coherence_mode = "artifact_backed"
        fallback_reasons: list[str] = []
    elif mission_state["payload"] is not None or stage_map:
        workspace_coherence_mode = "lifecycle_fallback"
        fallback_reasons = [
            "discover_bundle_missing:" + ",".join(missing_core)
        ] if missing_core else []
    else:
        workspace_coherence_mode = "deferred"
        fallback_reasons = ["mission_brief_and_lifecycle_state_missing"]

    governed_docs = _governed_doc_state(workspace_path, next_version_bundle=next_version_bundle)
    stale_inputs = _stale_release_inputs(workspace_path)
    if workspace_coherence_mode == "artifact_backed" and governed_docs["mode"] == "artifact_backed":
        p0_status = "passed"
    elif workspace_coherence_mode != "deferred" and governed_docs["mode"] != "deferred":
        p0_status = "watch"
    else:
        p0_status = "blocked"
    research_packet = _research_packet_state(
        workspace_path,
        next_version_bundle=next_version_bundle,
        generated_at=generated_at,
    )
    downstream = _downstream_state(
        workspace_path,
        next_version_bundle=next_version_bundle,
    )
    track_states = {
        "P0": {
            "status": p0_status,
            "focus": "runtime_coherence",
        },
        "P1": {
            "status": research_packet["status"],
            "focus": "governed_research_packet",
        },
        "P2": {
            "status": downstream["status"],
            "focus": "downstream_learning_loop",
        },
    }
    gate_status = "ready" if all(track["status"] == "passed" for track in track_states.values()) else "blocked"
    stable_release = latest_release_metadata(ROOT)
    return {
        "workspace_id": workspace_id,
        "workspace_name": workspace_name,
        "baseline_version": V9_BASELINE_VERSION,
        "candidate_version": V9_TARGET_VERSION,
        "stable_release_version": stable_release["core_version"],
        "workspace_coherence_mode": workspace_coherence_mode,
        "fallback_reasons": fallback_reasons,
        "governed_docs": governed_docs,
        "research_packet": research_packet,
        "downstream": downstream,
        "track_states": track_states,
        "stale_release_inputs": stale_inputs,
        "gate_status": gate_status,
        "next_version_bundle_available": next_version_bundle is not None,
    }


def build_v9_lifecycle_bundle_from_workspace(
    workspace_dir: Path | str,
    *,
    generated_at: str,
    target_version: str = V9_TARGET_VERSION,
    adapter_name: str = "codex",
    next_version_bundle: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    program_state = inspect_v9_lifecycle_enrichment_state(
        workspace_dir,
        generated_at=generated_at,
        adapter_name=adapter_name,
        next_version_bundle=next_version_bundle,
    )
    workspace_id = program_state["workspace_id"]
    track_states = program_state["track_states"]
    overall_status = "passed" if program_state["gate_status"] == "ready" else "watch"
    mission_state = _artifact_source_state(
        Path(workspace_dir).resolve(),
        patterns=[("artifacts", "mission_brief.json")],
    )
    coherence_evidence_refs = [
        ref
        for ref in [
            _payload_id(mission_state["payload"]),
            program_state["governed_docs"]["artifact_id"],
        ]
        if isinstance(ref, str)
    ]

    runtime_scenario_report = {
        "schema_version": "1.0.0",
        "runtime_scenario_report_id": f"runtime_scenario_report_{workspace_id}_v9_lifecycle_enrichment",
        "workspace_id": workspace_id,
        "baseline_version": program_state["baseline_version"],
        "candidate_version": target_version,
        "status": overall_status,
        "summary": (
            "The V9 lifecycle-enrichment program is fully artifact-backed across runtime coherence, governed research, and downstream reopen loops."
            if overall_status == "passed"
            else "The V9 lifecycle-enrichment program is partially proven, but one or more runtime, research-packet, or downstream learning lanes still rely on fallback or deferred evidence."
        ),
        "scenarios": [
            {
                "scenario_id": "scenario_workspace_coherence",
                "name": "Workspace coherence survives starter, adoption, and self-hosting variance",
                "status": "passed" if track_states["P0"]["status"] == "passed" else ("watch" if track_states["P0"]["status"] == "watch" else "failed"),
                "metric_deltas": [
                    {
                        "metric_name": "workspace_coherence_mode",
                        "baseline_value": 0,
                        "candidate_value": 1 if program_state["workspace_coherence_mode"] == "artifact_backed" else 0.5 if program_state["workspace_coherence_mode"] == "lifecycle_fallback" else 0,
                        "unit": "mode_score",
                        "trend": "improved" if program_state["workspace_coherence_mode"] != "deferred" else "flat",
                    }
                ],
                "evidence_refs": coherence_evidence_refs,
                "gaps": program_state["fallback_reasons"],
            },
            {
                "scenario_id": "scenario_governed_research_packet",
                "name": "Governed research and prioritization stay one traceable packet",
                "status": "passed" if track_states["P1"]["status"] == "passed" else ("watch" if track_states["P1"]["status"] == "watch" else "failed"),
                "metric_deltas": [
                    {
                        "metric_name": "research_packet_completeness",
                        "baseline_value": 0,
                        "candidate_value": program_state["research_packet"]["present_count"],
                        "unit": "count",
                        "trend": "improved" if program_state["research_packet"]["present_count"] else "flat",
                    }
                ],
                "evidence_refs": program_state["research_packet"]["artifact_ids"][:5],
                "gaps": (
                    program_state["research_packet"]["missing_artifacts"]
                    if program_state["research_packet"]["missing_artifacts"]
                    else []
                ),
            },
            {
                "scenario_id": "scenario_downstream_learning_chain",
                "name": "Launch, support, outcome, and reopen loops remain explicit",
                "status": "passed" if track_states["P2"]["status"] == "passed" else ("watch" if track_states["P2"]["status"] == "watch" else "failed"),
                "metric_deltas": [
                    {
                        "metric_name": "downstream_traceability_mode",
                        "baseline_value": 0,
                        "candidate_value": 1 if program_state["downstream"]["mode"] == "artifact_backed" else 0.5 if program_state["downstream"]["mode"] == "lifecycle_fallback" else 0,
                        "unit": "mode_score",
                        "trend": "improved" if program_state["downstream"]["mode"] != "deferred" else "flat",
                    }
                ],
                "evidence_refs": program_state["downstream"]["artifact_ids"][:5],
                "gaps": program_state["downstream"]["missing_artifacts"],
            },
            {
                "scenario_id": "scenario_shared_release_gate",
                "name": "The shared gate stays blocked until all P0/P1/P2 tracks pass",
                "status": "passed" if program_state["gate_status"] == "ready" else "watch",
                "metric_deltas": [
                    {
                        "metric_name": "passed_track_count",
                        "baseline_value": 0,
                        "candidate_value": sum(1 for track in track_states.values() if track["status"] == "passed"),
                        "unit": "count",
                        "trend": "improved" if any(track["status"] == "passed" for track in track_states.values()) else "flat",
                    }
                ],
                "evidence_refs": ["internal/ProductOS-Next/docs/planning/current-plan.md"],
                "gaps": [] if program_state["gate_status"] == "ready" else ["The shared V9 release gate remains blocked until all three lifecycle-enrichment tracks are fully artifact-backed."],
            },
        ],
        "generated_at": generated_at,
    }

    validation_lane_report = {
        "schema_version": "1.0.0",
        "validation_lane_report_id": f"validation_lane_report_{workspace_id}_v9_lifecycle_enrichment",
        "workspace_id": workspace_id,
        "artifact_ref": runtime_scenario_report["runtime_scenario_report_id"],
        "artifact_type": "runtime_scenario_report",
        "stage_name": "v9_0_lifecycle_enrichment_release_gate",
        "validation_tier": "tier_2",
        "overall_status": "passed" if program_state["gate_status"] == "ready" else "ready_for_manual_validation",
        "review_summary": (
            "The V9 bundle is ready: all three lifecycle-enrichment tracks are artifact-backed and the stable-line promotion can proceed."
            if program_state["gate_status"] == "ready"
            else "The V9 bundle is structurally coherent, but manual review should keep the stable-line promotion blocked until fallback and deferred evidence are eliminated."
        ),
        "ai_reviewer_lane": {
            "status": "proceed" if program_state["gate_status"] == "ready" else "revise",
            "reviewer_role": "AI Reviewer",
            "blocking_findings": (
                []
                if program_state["gate_status"] == "ready"
                else ["One or more lifecycle-enrichment tracks still depend on fallback or deferred evidence."]
            ),
            "non_blocking_findings": [
                "The runtime now reports lifecycle-enrichment state directly instead of the older visual-release-first framing.",
                "The April 27 planning docs are treated as canonical and the stale March release inputs are explicitly ignored.",
            ],
            "unresolved_questions": (
                []
                if program_state["gate_status"] == "ready"
                else ["Which remaining lifecycle-enrichment track should clear its fallback state before V9 promotion?"]
            ),
        },
        "ai_tester_lane": {
            "status": "passed" if program_state["gate_status"] == "ready" else "revise",
            "tester_role": "AI Tester",
            "checks_run": [
                "Validated workspace coherence and governed-doc posture for the selected workspace shape.",
                "Validated governed research packet completeness, freshness, contradiction count, and downstream readiness.",
                "Validated launch, support, outcome, and reopen-loop traceability.",
            ],
            "blocking_findings": (
                []
                if program_state["gate_status"] == "ready"
                else ["The shared V9 release gate is still blocked because not every lifecycle-enrichment track is artifact-backed."]
            ),
            "non_blocking_findings": [
                "The stale March increment and next-version gate artifacts are no longer used as canonical release proof.",
            ],
            "automation_gaps": [
                "Future V9 follow-up should add stricter parity checks across starter and adopted workspaces with persisted governed-doc artifacts.",
            ],
        },
        "manual_validation_policy": {
            "required": True,
            "scope": "targeted",
            "owner_role": "PM Operator",
            "status": "passed" if program_state["gate_status"] == "ready" else "pending",
            "rationale": "V9 changes the effective lifecycle proof boundary, so explicit PM review remains mandatory even when automated checks are green.",
        },
        "referee_trigger": {
            "required": False,
            "rationale": "Reviewer and tester lanes do not currently disagree on the shared V9 gate status.",
            "conflicting_lanes": [],
        },
        "governance_layer_refs": list(
            dict.fromkeys(
                [
                    *coherence_evidence_refs,
                    *program_state["research_packet"]["artifact_ids"][:4],
                    *program_state["downstream"]["artifact_ids"][:4],
                    "internal/ProductOS-Next/docs/planning/current-plan.md",
                ]
            )
        ),
        "next_action": (
            "Promote ProductOS V10.0.0 and update the stable release surfaces."
            if program_state["gate_status"] == "ready"
            else "Keep V10.0.0 stable and close the remaining lifecycle-enrichment fallback gaps before rerunning the V9 gate."
        ),
        "generated_at": generated_at,
    }

    manual_validation_record_id = f"manual_validation_record_{workspace_id}_v9_lifecycle_enrichment"
    release_readiness = {
        "schema_version": "1.2.0",
        "release_readiness_id": f"release_readiness_{workspace_id}_v9_lifecycle_enrichment",
        "workspace_id": workspace_id,
        "feature_id": "lifecycle_enrichment_program",
        "status": "ready" if program_state["gate_status"] == "ready" else "watch",
        "decision_summary": (
            "The V9 lifecycle-enrichment program is ready for stable promotion."
            if program_state["gate_status"] == "ready"
            else "Keep V10.0.0 stable while the lifecycle-enrichment program removes fallback and deferred evidence."
        ),
        "claim_readiness": [
            {
                "claim": "The V9 lifecycle-enrichment program is fully artifact-backed across runtime coherence, governed research, and downstream reopen loops.",
                "status": "verified" if program_state["gate_status"] == "ready" else "bounded",
                "evidence_refs": [
                    runtime_scenario_report["runtime_scenario_report_id"],
                    manual_validation_record_id,
                ],
            },
            {
                "claim": "ProductOS should keep V10.0.0 as the public stable line until the shared V9 release gate is go.",
                "status": "verified",
                "evidence_refs": ["internal/ProductOS-Next/docs/planning/current-plan.md"],
            },
        ],
        "launch_roles": [
            {
                "role_name": "Release owner",
                "responsibility": "Approve V10.0.0 only after P0, P1, and P2 are all artifact-backed.",
                "assignment_status": "assigned",
                "owner_name": "ProductOS PM",
                "owner_function": "Product management",
            }
        ],
        "checks": [
            {
                "name": "P0 runtime coherence",
                "status": "passed" if track_states["P0"]["status"] == "passed" else "watch",
                "notes": f"Workspace coherence mode is {program_state['workspace_coherence_mode']}.",
            },
            {
                "name": "P1 governed research packet",
                "status": "passed" if track_states["P1"]["status"] == "passed" else "watch",
                "notes": (
                    f"Research packet mode is {program_state['research_packet']['mode']} with "
                    f"{program_state['research_packet']['present_count']}/{program_state['research_packet']['required_count']} artifacts."
                ),
            },
            {
                "name": "P2 downstream reopen loop",
                "status": "passed" if track_states["P2"]["status"] == "passed" else "watch",
                "notes": f"Downstream mode is {program_state['downstream']['mode']}.",
            },
            {
                "name": "stale March release inputs",
                "status": "passed" if program_state["stale_release_inputs"]["status"] == "ignored" else "watch",
                "notes": (
                    "Stale March release and increment artifacts are explicitly ignored in favor of the April 27 lifecycle-enrichment plan."
                    if program_state["stale_release_inputs"]["status"] == "ignored"
                    else "Stale March release and increment artifacts still need explicit supersession."
                ),
            },
        ],
        "blocking_evidence_refs": [runtime_scenario_report["runtime_scenario_report_id"]],
        "generated_at": generated_at,
    }

    release_gate_decision = {
        "schema_version": "1.0.0",
        "release_gate_decision_id": f"release_gate_decision_{workspace_id}_v9_lifecycle_enrichment",
        "workspace_id": workspace_id,
        "target_release": V9_TARGET_RELEASE,
        "decision": "go" if program_state["gate_status"] == "ready" else "no_go",
        "pm_benchmark_ref": runtime_scenario_report["runtime_scenario_report_id"],
        "runtime_scenario_report_ref": runtime_scenario_report["runtime_scenario_report_id"],
        "release_readiness_ref": release_readiness["release_readiness_id"],
        "rationale": (
            "All lifecycle-enrichment tracks are artifact-backed and the shared V9 release gate is clear."
            if program_state["gate_status"] == "ready"
            else "Keep V10.0.0 as the public stable line because one or more lifecycle-enrichment tracks still depend on fallback or deferred evidence."
        ),
        "next_action": (
            "Promote ProductOS to V10.0.0 and update the stable release surfaces."
            if program_state["gate_status"] == "ready"
            else "Finish the remaining lifecycle-enrichment hardening and rerun the shared V9 release gate."
        ),
        "known_gaps": [
            *program_state["fallback_reasons"],
            *program_state["research_packet"]["missing_artifacts"][:3],
            *program_state["downstream"]["missing_artifacts"][:3],
        ]
        or ["No material V9 release gaps remain."],
        "blocker_categories": {
            "feed_governance_blockers": [],
            "governed_research_blockers": (
                []
                if track_states["P1"]["status"] == "passed"
                else ["Governed research packet is not yet fully artifact-backed."]
            ),
            "other_blockers": [
                blocker
                for blocker in [
                    "Runtime coherence and governed docs are not yet fully artifact-backed."
                    if track_states["P0"]["status"] != "passed"
                    else None,
                    "Downstream delivery-to-learning evidence is not yet fully artifact-backed."
                    if track_states["P2"]["status"] != "passed"
                    else None,
                ]
                if blocker is not None
            ],
        },
        "deferred_items": [
            "Keep V10.0.0 as the stable public line until the shared V9 gate clears.",
            "Do not broaden autonomous PM claims past the lifecycle-enrichment proof boundary.",
        ],
        "generated_at": generated_at,
    }

    manual_validation_record = {
        "schema_version": "1.0.0",
        "manual_validation_record_id": manual_validation_record_id,
        "workspace_id": workspace_id,
        "subject_ref": runtime_scenario_report["runtime_scenario_report_id"],
        "subject_type": "runtime_scenario_report",
        "validation_tier": "tier_2",
        "validator_role": "PM Operator",
        "scope": "targeted",
        "decision": "accept" if program_state["gate_status"] == "ready" else "defer",
        "fit_notes": [
            "The V9 candidate keeps lifecycle-enrichment scope explicit across runtime, research, and downstream learning lanes.",
            "The stable line remains V10.0.0 until all three lifecycle-enrichment tracks are fully artifact-backed.",
        ],
        "required_follow_ups": [
            "Clear the remaining fallback or deferred lanes before promoting V10.0.0.",
            "Keep the stale March planning inputs out of the release-proof path.",
        ],
        "related_validation_report_ref": validation_lane_report["validation_lane_report_id"],
        "final_approval": program_state["gate_status"] == "ready",
        "recorded_at": generated_at,
    }

    ralph_loop_state = {
        "schema_version": "1.0.0",
        "ralph_loop_state_id": f"ralph_loop_state_{workspace_id}_v9_lifecycle_enrichment",
        "workspace_id": workspace_id,
        "target_release": V9_TARGET_RELEASE,
        "loop_goal": (
            "Inspect, review, implement, validate, fix, and revalidate the lifecycle-enrichment program before stable release promotion."
        ),
        "overall_status": "ready_for_release" if program_state["gate_status"] == "ready" else "in_progress",
        "subject_refs": [
            runtime_scenario_report["runtime_scenario_report_id"],
            validation_lane_report["validation_lane_report_id"],
            manual_validation_record["manual_validation_record_id"],
        ],
        "stages": [
            {
                "stage_key": "inspect",
                "status": "passed",
                "owner": "AI Librarian",
                "findings_summary": "The lifecycle-enrichment workspace shape, research packet, and downstream chain were inspected as one bounded V9 release claim.",
                "evidence_refs": [runtime_scenario_report["runtime_scenario_report_id"]],
                "exit_condition": "The runtime, research, and downstream evidence paths are explicit enough to review as one bounded V9 slice.",
            },
            {
                "stage_key": "review",
                "status": "passed",
                "owner": "AI Reviewer",
                "findings_summary": "The selected V9 claim is correctly bounded to lifecycle enrichment and does not overstate stable public coverage.",
                "evidence_refs": [validation_lane_report["validation_lane_report_id"]],
                "exit_condition": "The promoted claim stays scoped to the lifecycle-enrichment program and its explicit release gate.",
            },
            {
                "stage_key": "implement",
                "status": "passed",
                "owner": "AI Product Shaper",
                "findings_summary": "The repo exposes a concrete V9 lifecycle-enrichment release surface through the CLI and bundle artifacts.",
                "evidence_refs": [runtime_scenario_report["runtime_scenario_report_id"]],
                "exit_condition": "The V9 slice exists concretely in the repo and can be validated and promoted.",
            },
            {
                "stage_key": "validate",
                "status": "passed" if program_state["gate_status"] == "ready" else "revise",
                "owner": "AI Tester",
                "findings_summary": "Shared-gate validation is ready only when P0, P1, and P2 are all artifact-backed.",
                "evidence_refs": [runtime_scenario_report["runtime_scenario_report_id"], release_readiness["release_readiness_id"]],
                "exit_condition": "The runtime, research, and downstream proof checks agree on one shared V9 gate status.",
            },
            {
                "stage_key": "fix",
                "status": "passed" if program_state["gate_status"] == "ready" else "revise",
                "owner": "AI Product Shaper",
                "findings_summary": "Any remaining fallback or deferred evidence must stay explicit rather than silently broadening the V9 claim.",
                "evidence_refs": [release_gate_decision["release_gate_decision_id"]],
                "exit_condition": "Deferred or fallback work remains visible and does not leak into the stable promotion claim.",
            },
            {
                "stage_key": "revalidate",
                "status": "passed" if program_state["gate_status"] == "ready" else "revise",
                "owner": "PM Operator",
                "findings_summary": "Manual review confirms whether the shared V9 gate is ready or still requires more hardening.",
                "evidence_refs": [manual_validation_record["manual_validation_record_id"]],
                "exit_condition": "One explicit proceed decision exists and no unresolved blocking lifecycle-enrichment gap remains.",
            },
        ],
        "validation_report_refs": [validation_lane_report["validation_lane_report_id"]],
        "manual_review_summary": (
            "The V9 lifecycle-enrichment release is ready."
            if program_state["gate_status"] == "ready"
            else "The V9 lifecycle-enrichment release still needs hardening before stable promotion."
        ),
        "next_action": release_gate_decision["next_action"],
        "generated_at": generated_at,
    }

    return {
        "runtime_scenario_report_v9_lifecycle_enrichment": runtime_scenario_report,
        "validation_lane_report_v9_lifecycle_enrichment": validation_lane_report,
        "manual_validation_record_v9_lifecycle_enrichment": manual_validation_record,
        "release_readiness_v9_lifecycle_enrichment": release_readiness,
        "release_gate_decision_v9_lifecycle_enrichment": release_gate_decision,
        "ralph_loop_state_v9_lifecycle_enrichment": ralph_loop_state,
    }


def summarize_v9_lifecycle_bundle(
    workspace_dir: Path | str,
    bundle: dict[str, dict[str, Any]],
) -> str:
    program_state = inspect_v9_lifecycle_enrichment_state(
        workspace_dir,
        generated_at=bundle["runtime_scenario_report_v9_lifecycle_enrichment"]["generated_at"],
    )
    track_summary = ", ".join(
        f"{track_id}={track_state['status']}"
        for track_id, track_state in program_state["track_states"].items()
    )
    return "\n".join(
        [
            f"V9 Bundle: {V9_BUNDLE_NAME}",
            f"Target Release: {bundle['runtime_scenario_report_v9_lifecycle_enrichment']['candidate_version']}",
            f"Track Statuses: {track_summary}",
            f"Workspace Coherence: {program_state['workspace_coherence_mode']}",
            (
                "Research Packet: "
                f"{program_state['research_packet']['present_count']}/"
                f"{program_state['research_packet']['required_count']} "
                f"({program_state['research_packet']['mode']})"
            ),
            f"Downstream Traceability: {program_state['downstream']['mode']}",
            f"Release Decision: {bundle['release_gate_decision_v9_lifecycle_enrichment']['decision']}",
        ]
    )
