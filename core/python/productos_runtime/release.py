from __future__ import annotations

import json
import re
import subprocess
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

PUBLIC_RELEASE_BLOCKED_PREFIXES = ("workspaces/",)


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def parse_semver(version: str) -> tuple[int, int, int]:
    major, minor, patch = version.split(".")
    return int(major), int(minor), int(patch)


def infer_next_version(current_version: str, bump: str) -> str:
    major, minor, patch = parse_semver(current_version)
    if bump == "major":
        return f"{major + 1}.0.0"
    if bump == "minor":
        return f"{major}.{minor + 1}.0"
    if bump == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise ValueError(f"Unsupported bump type: {bump}")


def release_tag_to_version(tag: str) -> str:
    match = re.fullmatch(r"v(\d+)_(\d+)_(\d+)", tag)
    if not match:
        raise ValueError(f"Unsupported release tag: {tag}")
    return ".".join(match.groups())


def version_to_release_id(version: str) -> str:
    return f"release_{version.replace('.', '_')}"


def latest_release_path(root_dir: Path) -> Path:
    release_dir = root_dir / "registry" / "releases"
    release_paths = sorted(release_dir.glob("release_*.json"))
    if not release_paths:
        raise FileNotFoundError(f"No release metadata found under {release_dir}")
    return max(release_paths, key=lambda path: parse_semver(_load_json(path)["core_version"]))


def latest_release_metadata(root_dir: Path) -> dict[str, Any]:
    return _load_json(latest_release_path(root_dir))


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _format_datetime(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _latest_release_before(root_dir: Path, target_version: str) -> dict[str, Any]:
    release_dir = root_dir / "registry" / "releases"
    release_payloads = [
        _load_json(path)
        for path in sorted(release_dir.glob("release_*.json"))
        if _load_json(path)["core_version"] != target_version
    ]
    if not release_payloads:
        existing_target = root_dir / "registry" / "releases" / f"{version_to_release_id(target_version)}.json"
        if existing_target.exists():
            return _load_json(existing_target)
        raise FileNotFoundError(f"No release metadata found before {target_version}")
    return max(release_payloads, key=lambda payload: parse_semver(payload["core_version"]))


def _normalize_released_at(released_at: str, previous_release: dict[str, Any]) -> str:
    candidate = _parse_datetime(released_at)
    previous = _parse_datetime(previous_release["released_at"])
    if candidate <= previous:
        candidate = previous + timedelta(seconds=1)
    return _format_datetime(candidate)


def _extract_slice_label(loop_goal: str) -> str:
    text = loop_goal.strip()
    prefix = "Inspect, review, implement, validate, fix, and revalidate "
    if text.startswith(prefix):
        text = text[len(prefix):]
    suffixes = [
        " before next-version promotion.",
        " before stable promotion.",
        " before stable release promotion.",
        " before release promotion.",
    ]
    for suffix in suffixes:
        if text.endswith(suffix):
            text = text[: -len(suffix)]
            break
    if text.startswith("the "):
        text = text[4:]
    return text


def _infer_release_type(previous_version: str, target_version: str) -> str:
    previous = parse_semver(previous_version)
    target = parse_semver(target_version)
    if target[0] != previous[0]:
        return "major"
    if target[1] != previous[1]:
        return "minor"
    return "patch"


def _infer_change_classification(release_type: str) -> str:
    if release_type == "major":
        return "major_product_change"
    if release_type == "minor":
        return "feature_enhancement"
    return "minor_improvement"


def _build_release_metadata(
    previous_release: dict[str, Any],
    ralph_state: dict[str, Any],
    target_version: str,
    released_at: str,
) -> dict[str, Any]:
    release_type = _infer_release_type(previous_release["core_version"], target_version)
    slice_label = _extract_slice_label(ralph_state["loop_goal"])
    pretty_slice_label = slice_label[0].upper() + slice_label[1:] if slice_label else "Bounded Ralph slice"

    return {
        "schema_version": "1.0.0",
        "release_id": version_to_release_id(target_version),
        "core_version": target_version,
        "released_at": released_at,
        "release_type": release_type,
        "change_classification": _infer_change_classification(release_type),
        "customer_visible": True,
        "classification_rationale": (
            f"This release promotes ProductOS to V{target_version} after the {slice_label} "
            "passed Ralph-loop inspection, validation, fix, and revalidation."
        ),
        "summary": (
            f"ProductOS V{target_version} is the stable release for {slice_label}."
        ),
        "breaking_changes": [],
        "upgrade_actions": [
            f"Adopt the promoted {pretty_slice_label} in the current ProductOS operating flow.",
            "Use the automatic Ralph-gated release promotion command for future successful slices.",
            "Keep product-specific work outside shared repo surfaces and promote only reusable repo assets.",
        ],
    }


def _assert_ralph_ready(ralph_state: dict[str, Any]) -> None:
    if ralph_state.get("overall_status") != "ready_for_release":
        raise ValueError(
            f"Ralph loop is not ready for release: overall_status={ralph_state.get('overall_status')}"
        )
    failed_stages = [
        stage["stage_key"]
        for stage in ralph_state.get("stages", [])
        if stage.get("status") != "passed"
    ]
    if failed_stages:
        raise ValueError(f"Ralph loop has non-passed stages: {failed_stages}")
    if not ralph_state.get("validation_report_refs"):
        raise ValueError("Ralph loop is missing validation_report_refs")


def _update_registration(
    payload: dict[str, Any],
    target_version: str,
    released_at: str,
    approved_by: str,
    change_note: str,
) -> dict[str, Any]:
    updated = deepcopy(payload)
    updated["current_core_version"] = target_version
    history = list(updated.get("upgrade_history", []))
    if history and history[-1]["core_version"] == target_version:
        history[-1] = {
            "core_version": target_version,
            "adopted_at": released_at,
            "approved_by": approved_by,
            "change_note": change_note,
        }
    else:
        history.append(
            {
                "core_version": target_version,
                "adopted_at": released_at,
                "approved_by": approved_by,
                "change_note": change_note,
            }
        )
    updated["upgrade_history"] = history
    return updated


def _update_readme(text: str, target_version: str) -> str:
    text = re.sub(
        r"ProductOS V\d+\.\d+\.\d+ is the current stable ProductOS Core line\.",
        f"ProductOS V{target_version} is the current stable ProductOS Core line.",
        text,
        count=1,
    )
    text = re.sub(
        r"ProductOS V\d+\.\d+\.\d+ is organized around the PM lifecycle plus governed research and improvement loops:",
        f"ProductOS V{target_version} is organized around the PM lifecycle plus governed research and improvement loops:",
        text,
        count=1,
    )
    text = re.sub(
        r"the active core line is now `\d+\.\d+\.\d+`\.",
        f"the active core line is now `{target_version}`.",
        text,
        count=1,
    )
    text = re.sub(
        r"- V\d+\.\d+ market-intelligence, Ralph-loop, readable-doc, and communication assets remain present",
        "- latest stable release assets remain present",
        text,
        count=1,
    )
    return text


def _update_product_overview(text: str, target_version: str) -> str:
    return re.sub(
        r"The current stable line is ProductOS `V\d+\.\d+\.\d+`\.",
        f"The current stable line is ProductOS `V{target_version}`.",
        text,
        count=1,
    )


def _build_public_release_ralph_state(slice_label: str) -> dict[str, Any]:
    normalized = " ".join(slice_label.split()).strip()
    if not normalized:
        raise ValueError("slice_label must not be empty")
    return {
        "loop_goal": (
            f"Inspect, review, implement, validate, fix, and revalidate the {normalized} "
            "before stable release promotion."
        )
    }


def _run_git(root_dir: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root_dir,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        command_text = " ".join(["git", *args])
        detail = (completed.stderr or completed.stdout).strip()
        raise RuntimeError(f"{command_text} failed: {detail}")
    return completed.stdout.strip()


def _blocked_public_release_paths(paths: list[str]) -> list[str]:
    return [
        path
        for path in paths
        if any(path == prefix[:-1] or path.startswith(prefix) for prefix in PUBLIC_RELEASE_BLOCKED_PREFIXES)
    ]


def verify_public_release_alignment(
    root_dir: Path,
    *,
    target_version: str,
    tag_name: str | None = None,
    workspace_registration_path: Path | None = None,
    suite_registration_path: Path | None = None,
    readme_path: Path | None = None,
) -> dict[str, Any]:
    root_dir = root_dir.resolve()
    workspace_registration_path = workspace_registration_path or root_dir / "registry" / "workspaces" / "ws_productos_v2.registration.json"
    suite_registration_path = suite_registration_path or root_dir / "registry" / "suites" / "suite_productos.registration.json"
    readme_path = readme_path or root_dir / "README.md"

    mismatches: list[str] = []
    latest_release = latest_release_metadata(root_dir)
    if latest_release["core_version"] != target_version:
        mismatches.append(
            f"Latest release metadata is {latest_release['core_version']} instead of {target_version}."
        )

    workspace_payload = _load_json(workspace_registration_path)
    if workspace_payload["current_core_version"] != target_version:
        mismatches.append(
            f"Workspace registration is {workspace_payload['current_core_version']} instead of {target_version}."
        )

    suite_payload = _load_json(suite_registration_path)
    if suite_payload["current_core_version"] != target_version:
        mismatches.append(
            f"Suite registration is {suite_payload['current_core_version']} instead of {target_version}."
        )

    readme_text = readme_path.read_text(encoding="utf-8")
    stable_line = f"ProductOS V{target_version} is the current stable ProductOS Core line."
    if stable_line not in readme_text:
        mismatches.append(f"README does not contain the stable-line marker for {target_version}.")

    if tag_name is not None:
        head_commit = _run_git(root_dir, "rev-parse", "HEAD")
        tag_commit = _run_git(root_dir, "rev-parse", f"{tag_name}^{{commit}}")
        if head_commit != tag_commit:
            mismatches.append(f"Git tag {tag_name} does not point to HEAD.")

    return {
        "status": "aligned" if not mismatches else "mismatched",
        "mismatches": mismatches,
    }


def promote_public_release(
    root_dir: Path,
    *,
    slice_label: str,
    released_at: str,
    approved_by: str = "ProductOS PM",
    target_version: str | None = None,
    bump: str = "minor",
    workspace_registration_path: Path | None = None,
    suite_registration_path: Path | None = None,
    readme_path: Path | None = None,
) -> dict[str, Any]:
    root_dir = root_dir.resolve()
    previous_release = latest_release_metadata(root_dir)
    target_version = target_version or infer_next_version(previous_release["core_version"], bump)
    if parse_semver(target_version) <= parse_semver(previous_release["core_version"]):
        raise ValueError(
            f"Target version {target_version} must be newer than current stable {previous_release['core_version']}."
        )

    normalized_released_at = _normalize_released_at(released_at, previous_release)
    release_payload = _build_release_metadata(
        previous_release,
        _build_public_release_ralph_state(slice_label),
        target_version,
        normalized_released_at,
    )
    release_path = root_dir / "registry" / "releases" / f"{release_payload['release_id']}.json"
    _write_json(release_path, release_payload)

    workspace_registration_path = workspace_registration_path or root_dir / "registry" / "workspaces" / "ws_productos_v2.registration.json"
    suite_registration_path = suite_registration_path or root_dir / "registry" / "suites" / "suite_productos.registration.json"
    readme_path = readme_path or root_dir / "README.md"

    workspace_note = (
        f"Adopted ProductOS V{target_version} after promoting the {slice_label} through the public release operator."
    )
    suite_note = (
        f"Promoted the suite to ProductOS V{target_version} after the {slice_label} passed the public release operator."
    )
    workspace_payload = _update_registration(
        _load_json(workspace_registration_path),
        target_version,
        normalized_released_at,
        approved_by,
        workspace_note,
    )
    suite_payload = _update_registration(
        _load_json(suite_registration_path),
        target_version,
        normalized_released_at,
        approved_by,
        suite_note,
    )
    _write_json(workspace_registration_path, workspace_payload)
    _write_json(suite_registration_path, suite_payload)

    updated_readme = _update_readme(readme_path.read_text(encoding="utf-8"), target_version)
    readme_path.write_text(updated_readme, encoding="utf-8")

    return {
        "target_version": target_version,
        "tag_name": f"v{target_version}",
        "release_path": release_path,
        "workspace_registration_path": workspace_registration_path,
        "suite_registration_path": suite_registration_path,
        "readme_path": readme_path,
        "changed_paths": [
            readme_path.relative_to(root_dir).as_posix(),
            release_path.relative_to(root_dir).as_posix(),
            workspace_registration_path.relative_to(root_dir).as_posix(),
            suite_registration_path.relative_to(root_dir).as_posix(),
        ],
    }


def run_public_release(
    root_dir: Path,
    *,
    slice_label: str,
    released_at: str,
    approved_by: str = "ProductOS PM",
    target_version: str | None = None,
    bump: str = "minor",
    commit_message: str | None = None,
    tag_message: str | None = None,
    remote: str = "origin",
    branch: str | None = None,
    push: bool = False,
) -> dict[str, Any]:
    root_dir = root_dir.resolve()
    promotion = promote_public_release(
        root_dir,
        slice_label=slice_label,
        released_at=released_at,
        approved_by=approved_by,
        target_version=target_version,
        bump=bump,
    )

    _run_git(root_dir, "add", "--all", ".")
    staged_paths = [
        line.strip()
        for line in _run_git(root_dir, "diff", "--cached", "--name-only").splitlines()
        if line.strip()
    ]
    if not staged_paths:
        raise ValueError("Public release found no staged changes to commit.")

    blocked_paths = _blocked_public_release_paths(staged_paths)
    if blocked_paths:
        raise ValueError(
            "Public release attempted to stage blocked paths: " + ", ".join(sorted(blocked_paths))
        )

    target_version = promotion["target_version"]
    commit_message = commit_message or f"Release ProductOS v{target_version}"
    _run_git(root_dir, "commit", "-m", commit_message)

    tag_name = promotion["tag_name"]
    tag_message = tag_message or f"ProductOS v{target_version} stable release"
    _run_git(root_dir, "tag", "-a", tag_name, "-m", tag_message)

    branch = branch or _run_git(root_dir, "branch", "--show-current")
    if push:
        _run_git(root_dir, "push", remote, branch)
        _run_git(root_dir, "push", remote, tag_name)

    alignment = verify_public_release_alignment(
        root_dir,
        target_version=target_version,
        tag_name=tag_name,
    )
    if alignment["status"] != "aligned":
        raise ValueError("Public release alignment failed: " + "; ".join(alignment["mismatches"]))

    return {
        **promotion,
        "branch": branch,
        "commit_message": commit_message,
        "staged_paths": staged_paths,
        "push": push,
    }


def external_research_gate_blockers(
    research_brief: dict[str, Any] | None = None,
    external_research_plan: dict[str, Any] | None = None,
    external_research_source_discovery: dict[str, Any] | None = None,
    external_research_feed_registry: dict[str, Any] | None = None,
    selected_manifest: dict[str, Any] | None = None,
    external_research_review: dict[str, Any] | None = None,
) -> list[str]:
    needs_governed_research = False
    if research_brief is not None:
        needs_governed_research = bool(
            research_brief.get("external_research_questions") or research_brief.get("known_gaps")
        )
    if (
        external_research_source_discovery is not None
        or external_research_feed_registry is not None
        or selected_manifest is not None
        or external_research_review is not None
    ):
        needs_governed_research = True

    if not needs_governed_research and external_research_review is None and selected_manifest is None:
        return []

    blockers: list[str] = []
    if needs_governed_research and external_research_plan is None:
        blockers.append(
            "Governed external research is required for this workspace, but no persisted external research plan exists."
        )

    if external_research_plan is not None and external_research_source_discovery is None:
        blockers.append(
            "Governed external research is planned, but source discovery has not been persisted yet."
        )

    if external_research_source_discovery is not None:
        search_status = external_research_source_discovery.get("search_status")
        if search_status == "no_results":
            blockers.append(
                "Governed external research source discovery found no usable candidate sources for the bounded questions."
            )
        elif search_status == "partial":
            blockers.append(
                "Governed external research source discovery only has partial question coverage, so broad release claims remain blocked."
            )
        elif selected_manifest is None:
            blockers.append(
                "Governed external research discovery completed, but no selected manifest has been persisted yet."
            )

    if external_research_feed_registry is not None:
        degraded_feeds: list[str] = []
        for feed in external_research_feed_registry.get("feeds", []):
            health_status = feed.get("health_status")
            cadence_status = feed.get("cadence_status")
            feed_id = feed.get("feed_id", feed.get("title", "unknown"))
            if health_status in {"error", "unconfigured"}:
                degraded_feeds.append(f"{feed_id} ({health_status})")
            elif cadence_status == "stale":
                degraded_feeds.append(f"{feed_id} (stale)")
        if degraded_feeds:
            blockers.append(
                "Governed external research feed registry has materially degraded feeds: "
                + ", ".join(degraded_feeds[:5])
                + ("." if len(degraded_feeds) <= 5 else ", ...")
            )

    if selected_manifest is not None and not list(selected_manifest.get("sources", [])):
        blockers.append(
            "Governed external research selected zero accepted sources, so the research refresh has not cleared the bounded plan."
        )

    if (
        selected_manifest is not None
        and list(selected_manifest.get("sources", []))
        and external_research_review is None
    ):
        blockers.append(
            "Governed external research selected sources, but the refreshed research review has not been persisted yet."
        )

    if external_research_review is None:
        return blockers

    accepted_source_ids = list(external_research_review.get("accepted_source_ids", []))
    contradiction_items = list(external_research_review.get("contradiction_items", []))
    review_required = (
        external_research_review.get("review_status") == "review_required"
        or external_research_review.get("recommendation") == "pm_review_required"
    )

    if review_required:
        if contradiction_items:
            topics = ", ".join(
                sorted({item.get("topic", "evidence_conflict").replace("_", " ") for item in contradiction_items})
            )
            blockers.append(
                "Governed external research still requires PM review due to contradictory evidence"
                f" on {topics}."
            )
        else:
            blockers.append("Governed external research still requires PM review.")

    if not accepted_source_ids:
        blockers.append(
            "Governed external research has zero accepted sources, so research-backed release claims remain unsupported."
        )

    return blockers


def categorize_promotion_blockers(blockers: list[str]) -> dict[str, list[str]]:
    categories = {
        "feed_governance_blockers": [],
        "governed_research_blockers": [],
        "other_blockers": [],
    }
    for blocker in blockers:
        lower = blocker.lower()
        if "feed registry" in lower or ("feed " in lower and any(term in lower for term in ["stale", "unconfigured", "error"])):
            categories["feed_governance_blockers"].append(blocker)
        elif "external research" in lower or "research " in lower:
            categories["governed_research_blockers"].append(blocker)
        else:
            categories["other_blockers"].append(blocker)
    return categories


def evaluate_promotion_gate(
    *,
    eval_run_report: dict[str, Any] | None = None,
    feature_portfolio_review: dict[str, Any] | None = None,
    research_brief: dict[str, Any] | None = None,
    external_research_plan: dict[str, Any] | None = None,
    external_research_source_discovery: dict[str, Any] | None = None,
    external_research_feed_registry: dict[str, Any] | None = None,
    selected_manifest: dict[str, Any] | None = None,
    external_research_review: dict[str, Any] | None = None,
) -> dict[str, Any]:
    blockers: list[str] = []
    status = "ready"
    top_priority_feature_id: str | None = None

    if eval_run_report is not None:
        eval_status = eval_run_report.get("status")
        regression_count = int(eval_run_report.get("regression_count", 0))
        truthfulness_status = eval_run_report.get("truthfulness_status")
        if eval_status != "passed":
            blockers.append(
                f"Frozen eval suite is `{eval_status}` with {regression_count} regressions."
            )
        elif regression_count:
            blockers.append(f"Frozen eval suite still reports {regression_count} regressions.")
        if truthfulness_status and truthfulness_status != "healthy":
            blockers.append(f"Eval truthfulness status is `{truthfulness_status}`.")

    if feature_portfolio_review is not None:
        portfolio_truthfulness = feature_portfolio_review.get("truthfulness_status")
        top_priority_feature_id = feature_portfolio_review.get("top_priority_feature_id")
        if portfolio_truthfulness and portfolio_truthfulness != "healthy":
            blockers.append(f"Feature portfolio truthfulness is `{portfolio_truthfulness}`.")

    blockers.extend(
        external_research_gate_blockers(
            research_brief=research_brief,
            external_research_plan=external_research_plan,
            external_research_source_discovery=external_research_source_discovery,
            external_research_feed_registry=external_research_feed_registry,
            selected_manifest=selected_manifest,
            external_research_review=external_research_review,
        )
    )

    if blockers:
        status = "blocked"

    return {
        "status": status,
        "blockers": blockers,
        "blocker_categories": categorize_promotion_blockers(blockers),
        "top_priority_feature_id": top_priority_feature_id,
    }


def _assert_promotion_gate_ready(
    *,
    eval_run_report: dict[str, Any] | None = None,
    feature_portfolio_review: dict[str, Any] | None = None,
    research_brief: dict[str, Any] | None = None,
    external_research_plan: dict[str, Any] | None = None,
    external_research_source_discovery: dict[str, Any] | None = None,
    external_research_feed_registry: dict[str, Any] | None = None,
    selected_manifest: dict[str, Any] | None = None,
    external_research_review: dict[str, Any] | None = None,
) -> None:
    gate = evaluate_promotion_gate(
        eval_run_report=eval_run_report,
        feature_portfolio_review=feature_portfolio_review,
        research_brief=research_brief,
        external_research_plan=external_research_plan,
        external_research_source_discovery=external_research_source_discovery,
        external_research_feed_registry=external_research_feed_registry,
        selected_manifest=selected_manifest,
        external_research_review=external_research_review,
    )
    if gate["status"] != "ready":
        blocker_text = "; ".join(gate["blockers"])
        raise ValueError(f"Promotion gate is blocked: {blocker_text}")


def promote_release_from_ralph(
    root_dir: Path,
    ralph_path: Path,
    *,
    released_at: str,
    approved_by: str = "ProductOS PM",
    eval_run_report_path: Path | None = None,
    feature_portfolio_review_path: Path | None = None,
    research_brief_path: Path | None = None,
    external_research_plan_path: Path | None = None,
    external_research_source_discovery_path: Path | None = None,
    external_research_feed_registry_path: Path | None = None,
    selected_manifest_path: Path | None = None,
    external_research_review_path: Path | None = None,
    workspace_registration_path: Path | None = None,
    suite_registration_path: Path | None = None,
    readme_path: Path | None = None,
    product_overview_path: Path | None = None,
) -> dict[str, Any]:
    root_dir = root_dir.resolve()
    ralph_payload = _load_json(ralph_path if ralph_path.is_absolute() else root_dir / ralph_path)
    _assert_ralph_ready(ralph_payload)
    eval_payload = None
    if eval_run_report_path is not None:
        eval_payload = _load_json(
            eval_run_report_path if eval_run_report_path.is_absolute() else root_dir / eval_run_report_path
        )
    portfolio_payload = None
    if feature_portfolio_review_path is not None:
        portfolio_payload = _load_json(
            feature_portfolio_review_path
            if feature_portfolio_review_path.is_absolute()
            else root_dir / feature_portfolio_review_path
        )
    research_brief_payload = None
    if research_brief_path is not None:
        research_brief_payload = _load_json(
            research_brief_path if research_brief_path.is_absolute() else root_dir / research_brief_path
        )
    external_research_plan_payload = None
    if external_research_plan_path is not None:
        external_research_plan_payload = _load_json(
            external_research_plan_path
            if external_research_plan_path.is_absolute()
            else root_dir / external_research_plan_path
        )
    external_research_source_discovery_payload = None
    if external_research_source_discovery_path is not None:
        external_research_source_discovery_payload = _load_json(
            external_research_source_discovery_path
            if external_research_source_discovery_path.is_absolute()
            else root_dir / external_research_source_discovery_path
        )
    external_research_feed_registry_payload = None
    if external_research_feed_registry_path is not None:
        external_research_feed_registry_payload = _load_json(
            external_research_feed_registry_path
            if external_research_feed_registry_path.is_absolute()
            else root_dir / external_research_feed_registry_path
        )
    selected_manifest_payload = None
    if selected_manifest_path is not None:
        selected_manifest_payload = _load_json(
            selected_manifest_path if selected_manifest_path.is_absolute() else root_dir / selected_manifest_path
        )
    external_research_review_payload = None
    if external_research_review_path is not None:
        external_research_review_payload = _load_json(
            external_research_review_path
            if external_research_review_path.is_absolute()
            else root_dir / external_research_review_path
        )
    _assert_promotion_gate_ready(
        eval_run_report=eval_payload,
        feature_portfolio_review=portfolio_payload,
        research_brief=research_brief_payload,
        external_research_plan=external_research_plan_payload,
        external_research_source_discovery=external_research_source_discovery_payload,
        external_research_feed_registry=external_research_feed_registry_payload,
        selected_manifest=selected_manifest_payload,
        external_research_review=external_research_review_payload,
    )

    target_version = release_tag_to_version(ralph_payload["target_release"])
    previous_release = _latest_release_before(root_dir, target_version)
    previous_version = previous_release["core_version"]
    if parse_semver(target_version) < parse_semver(previous_version):
        raise ValueError(
            f"Target version {target_version} is older than current stable {previous_version}"
        )

    normalized_released_at = _normalize_released_at(released_at, previous_release)
    release_payload = _build_release_metadata(previous_release, ralph_payload, target_version, normalized_released_at)
    release_path = root_dir / "registry" / "releases" / f"{release_payload['release_id']}.json"
    _write_json(release_path, release_payload)

    slice_label = _extract_slice_label(ralph_payload["loop_goal"])
    workspace_note = (
        f"Adopted ProductOS V{target_version} after promoting the {slice_label} through a successful Ralph loop."
    )
    suite_note = (
        f"Promoted the suite to ProductOS V{target_version} after the {slice_label} passed automatic Ralph-gated release promotion."
    )

    workspace_registration_path = workspace_registration_path or root_dir / "registry" / "workspaces" / "ws_productos_v2.registration.json"
    suite_registration_path = suite_registration_path or root_dir / "registry" / "suites" / "suite_productos.registration.json"
    readme_path = readme_path or root_dir / "README.md"
    workspace_payload = _update_registration(
        _load_json(workspace_registration_path),
        target_version,
        normalized_released_at,
        approved_by,
        workspace_note,
    )
    suite_payload = _update_registration(
        _load_json(suite_registration_path),
        target_version,
        normalized_released_at,
        approved_by,
        suite_note,
    )
    _write_json(workspace_registration_path, workspace_payload)
    _write_json(suite_registration_path, suite_payload)

    updated_readme = _update_readme(readme_path.read_text(encoding="utf-8"), target_version)
    readme_path.write_text(updated_readme, encoding="utf-8")

    if product_overview_path is not None and product_overview_path.exists():
        updated_overview = _update_product_overview(
            product_overview_path.read_text(encoding="utf-8"),
            target_version,
        )
        product_overview_path.write_text(updated_overview, encoding="utf-8")

    return {
        "target_version": target_version,
        "release_path": release_path,
        "workspace_registration_path": workspace_registration_path,
        "suite_registration_path": suite_registration_path,
    }
