import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from conftest import latest_release


def _run_cli(root_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/productos.py", *args],
        cwd=root_dir,
        capture_output=True,
        text=True,
        check=False,
    )


def _run_self_hosting_cli(root_dir: Path, workspace_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return _run_cli(root_dir, "--workspace-dir", str(workspace_dir), *args)


def test_productos_status_command(root_dir: Path, self_hosting_workspace_dir: Path):
    result = _run_self_hosting_cli(root_dir, self_hosting_workspace_dir, "status")

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Mode: status" in result.stdout
    assert "Mission: PM superpower recovery mission" in result.stdout
    assert "Top Priority Feature: v5_bundle_selection" in result.stdout
    assert "Truthfulness Status: healthy" in result.stdout
    assert "Eval Status: passed (0 regressions)" in result.stdout
    assert "Stable Promotion: ready" in result.stdout


def test_productos_doctor_command(root_dir: Path, self_hosting_workspace_dir: Path):
    result = _run_self_hosting_cli(root_dir, self_hosting_workspace_dir, "doctor")

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Bundle Status: healthy" in result.stdout
    assert "Mission: PM superpower recovery mission" in result.stdout
    assert "Stable Promotion: ready" in result.stdout
    assert "Intake Items: 2" in result.stdout
    assert "Top Priority Feature: v5_bundle_selection" in result.stdout


def test_productos_init_mission_command(root_dir: Path, self_hosting_workspace_dir: Path, tmp_path: Path):
    workspace_copy = tmp_path / "workspace-copy"
    shutil.copytree(self_hosting_workspace_dir, workspace_copy)
    for relative_path in [
        "artifacts/problem_brief.json",
        "artifacts/concept_brief.json",
        "artifacts/prd.json",
    ]:
        path = workspace_copy / relative_path
        if path.exists():
            path.unlink()

    result = _run_self_hosting_cli(
        root_dir,
        workspace_copy,
        "init-mission",
        "--title",
        "Customer recovery mission",
        "--target-user",
        "Product manager",
        "--customer-problem",
        "The PM needs ProductOS to turn messy inputs into reviewable artifacts faster.",
        "--business-goal",
        "Recover customer confidence with a clear PM-first operating surface.",
        "--success-metric",
        "time to reviewable PRD",
        "--success-metric",
        "time to aligned docs and deck",
        "--operating-mode",
        "full_loop",
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Mission Brief: mission_brief_ws_productos_v2_customer_recovery_mission" in result.stdout
    mission_brief = json.loads((workspace_copy / "artifacts" / "mission_brief.json").read_text(encoding="utf-8"))
    canonical_problem = json.loads((workspace_copy / "artifacts" / "problem_brief.json").read_text(encoding="utf-8"))
    canonical_concept = json.loads((workspace_copy / "artifacts" / "concept_brief.json").read_text(encoding="utf-8"))
    canonical_prd = json.loads((workspace_copy / "artifacts" / "prd.json").read_text(encoding="utf-8"))
    assert mission_brief["title"] == "Customer recovery mission"
    assert mission_brief["operating_mode"] == "full_loop"
    assert canonical_problem["title"] == "Problem Brief: Customer recovery mission"
    assert canonical_concept["title"] == "Customer recovery mission"
    assert canonical_prd["title"] == "PRD: Customer recovery mission"
    assert (workspace_copy / "docs" / "planning" / "mission-brief.md").exists()

    status_result = _run_self_hosting_cli(root_dir, workspace_copy, "status")
    assert status_result.returncode == 0, status_result.stderr or status_result.stdout
    assert "Mission: Customer recovery mission" in status_result.stdout


def test_productos_run_discover_can_fall_back_to_mission_brief(root_dir: Path, self_hosting_workspace_dir: Path, tmp_path: Path):
    workspace_copy = tmp_path / "workspace-copy"
    output_dir = tmp_path / "discover-output"
    shutil.copytree(self_hosting_workspace_dir, workspace_copy)

    for relative_path in [
        "artifacts/problem_brief.json",
        "artifacts/concept_brief.json",
        "artifacts/prd.json",
        "outputs/discover/discover_problem_brief.json",
        "outputs/discover/discover_concept_brief.json",
        "outputs/discover/discover_prd.json",
        "inbox/raw-notes/2026-03-22-next-version-superpowers.md",
        "inbox/transcripts/2026-03-22-dogfood-next-version-session.txt",
    ]:
        path = workspace_copy / relative_path
        if path.exists():
            path.unlink()

    result = _run_self_hosting_cli(
        root_dir,
        workspace_copy,
        "run",
        "discover",
        "--output-dir",
        str(output_dir),
    )

    assert result.returncode == 0, result.stderr or result.stdout
    generated_problem = json.loads((output_dir / "discover_problem_brief.json").read_text(encoding="utf-8"))
    generated_concept = json.loads((output_dir / "discover_concept_brief.json").read_text(encoding="utf-8"))
    generated_prd = json.loads((output_dir / "discover_prd.json").read_text(encoding="utf-8"))
    assert generated_problem["title"] == "Problem Brief: PM superpower recovery mission"
    assert "single repo-native way to declare the mission" in generated_problem["problem_summary"]
    assert generated_concept["title"] == "PM superpower recovery mission"
    assert generated_prd["title"] == "PRD: PM superpower recovery mission"


def test_productos_run_discover_persist_syncs_canonical_discover_artifacts_from_mission(
    root_dir: Path, self_hosting_workspace_dir: Path, tmp_path: Path
):
    workspace_copy = tmp_path / "workspace-copy"
    shutil.copytree(self_hosting_workspace_dir, workspace_copy)

    for relative_path in [
        "artifacts/problem_brief.json",
        "artifacts/concept_brief.json",
        "artifacts/prd.json",
        "outputs/discover/discover_problem_brief.json",
        "outputs/discover/discover_concept_brief.json",
        "outputs/discover/discover_prd.json",
        "inbox/raw-notes/2026-03-22-next-version-superpowers.md",
        "inbox/transcripts/2026-03-22-dogfood-next-version-session.txt",
    ]:
        path = workspace_copy / relative_path
        if path.exists():
            path.unlink()

    result = _run_self_hosting_cli(
        root_dir,
        workspace_copy,
        "run",
        "discover",
        "--persist",
    )

    assert result.returncode == 0, result.stderr or result.stdout
    canonical_problem = json.loads((workspace_copy / "artifacts" / "problem_brief.json").read_text(encoding="utf-8"))
    canonical_concept = json.loads((workspace_copy / "artifacts" / "concept_brief.json").read_text(encoding="utf-8"))
    canonical_prd = json.loads((workspace_copy / "artifacts" / "prd.json").read_text(encoding="utf-8"))
    persisted_problem = json.loads((workspace_copy / "outputs" / "discover" / "discover_problem_brief.json").read_text(encoding="utf-8"))
    assert canonical_problem["problem_brief_id"] == persisted_problem["problem_brief_id"]
    assert canonical_problem["title"] == "Problem Brief: PM superpower recovery mission"
    assert canonical_concept["title"] == "PM superpower recovery mission"
    assert canonical_prd["title"] == "PRD: PM superpower recovery mission"


def test_productos_init_mission_does_not_overwrite_mature_lifecycle_examples(
    root_dir: Path, self_hosting_workspace_dir: Path, tmp_path: Path
):
    workspace_copy = tmp_path / "workspace-copy"
    shutil.copytree(self_hosting_workspace_dir, workspace_copy)

    original_item = json.loads(
        (workspace_copy / "artifacts" / "item_lifecycle_state_pm_lifecycle_visibility.example.json").read_text(
            encoding="utf-8"
        )
    )

    result = _run_self_hosting_cli(
        root_dir,
        workspace_copy,
        "init-mission",
        "--title",
        "Customer trust recovery mission",
        "--target-user",
        "Product manager",
        "--customer-problem",
        "The PM needs ProductOS outputs to stay tied to the real customer problem instead of generic operating language.",
        "--business-goal",
        "Recover customer trust with explicit mission traceability across every PM phase.",
        "--success-metric",
        "time to reviewable PRD",
    )

    assert result.returncode == 0, result.stderr or result.stdout
    preserved_item = json.loads(
        (workspace_copy / "artifacts" / "item_lifecycle_state_pm_lifecycle_visibility.example.json").read_text(
            encoding="utf-8"
        )
    )
    assert preserved_item["item_lifecycle_state_id"] == original_item["item_lifecycle_state_id"]
    assert preserved_item["title"] == original_item["title"]
    assert not (workspace_copy / "artifacts" / "item_lifecycle_state.json").exists()
    assert not (workspace_copy / "artifacts" / "lifecycle_stage_snapshot.json").exists()


def test_productos_align_and_operate_outputs_include_custom_mission_context(
    root_dir: Path, self_hosting_workspace_dir: Path, tmp_path: Path
):
    workspace_copy = tmp_path / "workspace-copy"
    align_output_dir = tmp_path / "align-output"
    operate_output_dir = tmp_path / "operate-output"
    shutil.copytree(self_hosting_workspace_dir, workspace_copy)

    mission_result = _run_self_hosting_cli(
        root_dir,
        workspace_copy,
        "init-mission",
        "--title",
        "Customer trust recovery mission",
        "--target-user",
        "Product manager",
        "--customer-problem",
        "The PM needs ProductOS outputs to stay tied to the real customer problem instead of generic operating language.",
        "--business-goal",
        "Recover customer trust with explicit mission traceability across every PM phase.",
        "--success-metric",
        "time to reviewable PRD",
        "--success-metric",
        "time to aligned docs and deck",
    )
    assert mission_result.returncode == 0, mission_result.stderr or mission_result.stdout

    align_result = _run_self_hosting_cli(
        root_dir,
        workspace_copy,
        "run",
        "align",
        "--output-dir",
        str(align_output_dir),
    )
    operate_result = _run_self_hosting_cli(
        root_dir,
        workspace_copy,
        "run",
        "operate",
        "--output-dir",
        str(operate_output_dir),
    )

    assert align_result.returncode == 0, align_result.stderr or align_result.stdout
    assert operate_result.returncode == 0, operate_result.stderr or operate_result.stdout

    presentation_brief = json.loads((align_output_dir / "presentation_brief.json").read_text(encoding="utf-8"))
    document_sync_state = json.loads((align_output_dir / "align_document_sync_state.json").read_text(encoding="utf-8"))
    status_mail = json.loads((operate_output_dir / "operate_status_mail.json").read_text(encoding="utf-8"))
    issue_log = json.loads((operate_output_dir / "operate_issue_log.json").read_text(encoding="utf-8"))

    assert "Customer trust recovery mission" in presentation_brief["objective"]
    assert "mission_brief_ws_productos_v2_customer_trust_recovery_mission" in presentation_brief["source_artifact_ids"]
    assert any(
        snapshot["artifact_type"] == "mission_brief" for snapshot in presentation_brief["source_material_snapshots"]
    )
    assert "Customer trust recovery mission" in document_sync_state["next_action"]
    assert "mission_brief_ws_productos_v2_customer_trust_recovery_mission" in document_sync_state["source_artifact_refs"]
    assert "Customer trust recovery mission" in status_mail["summary"]
    assert "mission_brief_ws_productos_v2_customer_trust_recovery_mission" in status_mail["generated_from_artifact_ids"]
    assert any(
        "Customer trust recovery mission" in issue["title"] for issue in issue_log["issues"]
    )


def test_productos_status_review_and_doctor_surface_feed_governance(
    root_dir: Path, self_hosting_workspace_dir: Path, tmp_path: Path
):
    workspace_copy = tmp_path / "workspace-copy"
    shutil.copytree(self_hosting_workspace_dir, workspace_copy)

    feed_registry = {
        "schema_version": "1.0.0",
        "external_research_feed_registry_id": "external_research_feed_registry_ws_productos_v2_bounded_baseline",
        "workspace_id": "ws_productos_v2_bounded_baseline",
        "title": "External research feed registry: ws_productos_v2_bounded_baseline",
        "created_at": "2026-04-09T08:00:00Z",
        "feeds": [
            {
                "feed_id": "feed_market_validation",
                "title": "Market validation feed",
                "source_type": "market_validation",
                "uri": "https://example.com/feed/market.xml",
                "trust_tier": "primary",
                "refresh_cadence": "weekly",
                "health_status": "healthy",
                "health_reason": "Feed produced recent candidate results.",
                "last_checked_at": "2026-04-09T08:00:00Z",
                "last_success_at": "2026-04-09T08:00:00Z",
                "last_item_count": 3,
                "cadence_status": "current",
                "cadence_reason": "Feed refreshed within its weekly cadence window.",
            },
            {
                "feed_id": "feed_competitor_research",
                "title": "Competitor feed",
                "source_type": "competitor_research",
                "uri": "",
                "trust_tier": "secondary",
                "refresh_cadence": "weekly",
                "health_status": "unconfigured",
                "health_reason": "Feed URI is empty; add a trusted source before relying on this slot.",
                "last_checked_at": "2026-04-09T08:00:00Z",
                "last_item_count": 0,
                "cadence_status": "due",
                "cadence_reason": "No successful refresh has been recorded for this feed yet.",
            },
            {
                "feed_id": "feed_customer_evidence",
                "title": "Customer evidence feed",
                "source_type": "customer_evidence",
                "uri": "https://example.com/feed/customer.xml",
                "trust_tier": "primary",
                "refresh_cadence": "daily",
                "health_status": "healthy",
                "health_reason": "Feed produced recent candidate results.",
                "last_checked_at": "2026-04-09T08:00:00Z",
                "last_success_at": "2026-04-05T08:00:00Z",
                "last_item_count": 2,
                "cadence_status": "stale",
                "cadence_reason": "Feed is materially past its daily cadence and should not be trusted without refresh.",
            },
        ],
    }
    artifacts_dir = workspace_copy / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    (artifacts_dir / "external_research_feed_registry.json").write_text(
        json.dumps(feed_registry, indent=2) + "\n",
        encoding="utf-8",
    )

    status_result = _run_self_hosting_cli(root_dir, workspace_copy, "status")
    review_result = _run_self_hosting_cli(root_dir, workspace_copy, "review")
    doctor_result = _run_self_hosting_cli(root_dir, workspace_copy, "doctor")

    assert status_result.returncode == 0, status_result.stderr or status_result.stdout
    assert "Feed Governance: degraded (1 unconfigured, 1 stale, 1 due)" in status_result.stdout
    assert "Promotion Blockers:" in status_result.stdout
    assert "- Feed Governance:" in status_result.stdout
    assert "- Governed Research:" in status_result.stdout
    assert "Feed Governance Alerts:" in status_result.stdout
    assert "feed_competitor_research: unconfigured" in status_result.stdout
    assert "feed_customer_evidence: cadence stale" in status_result.stdout

    assert review_result.returncode == 0, review_result.stderr or review_result.stdout
    assert "Feed Governance: degraded (1 unconfigured, 1 stale, 1 due)" in review_result.stdout
    assert "Promotion Blockers:" in review_result.stdout
    assert "- Feed Governance:" in review_result.stdout
    assert "- Governed Research:" in review_result.stdout
    assert "Feed Governance Alerts:" in review_result.stdout

    assert doctor_result.returncode == 0, doctor_result.stderr or doctor_result.stdout
    assert "Feed Governance: degraded (1 unconfigured, 1 stale, 1 due)" in doctor_result.stdout
    assert "Promotion Blockers:" in doctor_result.stdout
    assert "- Feed Governance:" in doctor_result.stdout
    assert "- Governed Research:" in doctor_result.stdout
    assert "Feed Governance Alerts:" in doctor_result.stdout


def test_productos_cutover_command(root_dir: Path, self_hosting_workspace_dir: Path, tmp_path: Path):
    output_path = tmp_path / "v7-cutover-plan.md"
    result = _run_self_hosting_cli(root_dir, self_hosting_workspace_dir, "cutover", "--output-path", str(output_path))
    stable_release_version = latest_release(root_dir)["core_version"]

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Target Version: 7.0.0" in result.stdout
    assert "Selection Status: stable_active" in result.stdout
    assert "Promotion Gate: ready" in result.stdout
    assert f"Stable Release: V{stable_release_version}" in result.stdout
    assert "Build Strategy: stabilize_then_externalize" in result.stdout
    assert "Selected Bundle: Lifecycle traceability through outcome review" in result.stdout
    assert output_path.exists()
    markdown = output_path.read_text(encoding="utf-8")
    assert "# V7 Cutover Plan" in markdown
    assert "## Selected Bundle" in markdown
    assert "Lifecycle traceability through outcome review" in markdown
    assert "external_publication_adapters" in markdown
    assert f"keep V{stable_release_version} as the stable line" in markdown
    assert "extend beyond the current PM superpower core only through a later bounded release with explicit proof" in markdown


def test_productos_v5_cutover_markdown_groups_feed_governance_blockers(
    root_dir: Path, self_hosting_workspace_dir: Path, tmp_path: Path
):
    workspace_copy = tmp_path / "workspace-copy"
    shutil.copytree(self_hosting_workspace_dir, workspace_copy)

    (workspace_copy / "artifacts" / "research_brief.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "research_brief_id": "research_brief_ws_productos_v2",
                "workspace_id": "ws_productos_v2",
                "title": "Research Brief: ProductOS proof posture",
                "summary": "Validate the external proof posture before promotion.",
                "target_segment_refs": [],
                "insights": [],
                "known_gaps": ["Need governed market validation."],
                "external_research_questions": [
                    {
                        "question_id": "research_q_productos_proof_posture",
                        "question": "Do buyers expect measurable governance proof before adopting ProductOS-like systems?",
                        "recommended_source_type": "market_validation",
                        "why_it_matters": "The release claim should not overstate validated proof posture.",
                    }
                ],
                "created_at": "2026-04-09T10:00:00Z",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (workspace_copy / "artifacts" / "external_research_plan.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "external_research_plan_id": "external_research_plan_ws_productos_v2",
                "workspace_id": "ws_productos_v2",
                "title": "External research plan",
                "generated_from_artifact_id": "research_brief_ws_productos_v2",
                "research_objective": "Validate the external proof posture before promotion.",
                "prioritized_questions": [
                    {
                        "question_id": "research_q_productos_proof_posture",
                        "question": "Do buyers expect measurable governance proof before adopting ProductOS-like systems?",
                        "why_it_matters": "The release claim should not overstate validated proof posture.",
                        "recommended_source_type": "market_validation",
                        "priority": "high",
                        "search_queries": ["product operations governance proof measurable rollout"],
                        "source_requirements": ["Fresh operator or market validation evidence"],
                    }
                ],
                "coverage_summary": {
                    "known_gaps": ["Need governed market validation."],
                    "claims_needing_validation": ["Governance proof posture is customer-safe to claim."],
                    "recommended_next_step": "Refresh governed feed coverage and rerun the research loop.",
                },
                "created_at": "2026-04-09T10:00:00Z",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (workspace_copy / "artifacts" / "external_research_source_discovery.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "external_research_source_discovery_id": "external_research_source_discovery_ws_productos_v2",
                "workspace_id": "ws_productos_v2",
                "generated_from_plan_id": "external_research_plan_ws_productos_v2",
                "search_provider": "feed_registry,duckduckgo",
                "search_status": "completed",
                "discovered_questions": [
                    {
                        "question_id": "research_q_productos_proof_posture",
                        "query": "product operations governance proof measurable rollout",
                        "source_type": "market_validation",
                        "candidate_count": 1,
                        "queries_attempted": 1,
                        "providers_attempted": ["feed_registry", "duckduckgo"],
                    }
                ],
                "candidate_sources": [
                    {
                        "source_id": "research_q_productos_proof_posture_candidate_1",
                        "question_id": "research_q_productos_proof_posture",
                        "source_type": "market_validation",
                        "title": "Market validation source",
                        "uri": "https://example.com/market-proof",
                        "snippet": "Buyer proof posture note.",
                        "search_query": "product operations governance proof measurable rollout",
                        "selection_status": "suggested",
                        "provider": "feed_registry",
                        "domain": "example.com",
                        "quality_score": 9,
                        "selection_reason": "official docs or trust domain",
                        "freshness_expectation": "fresh",
                    }
                ],
                "created_at": "2026-04-09T10:00:00Z",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (workspace_copy / "artifacts" / "external_research_feed_registry.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "external_research_feed_registry_id": "external_research_feed_registry_ws_productos_v2",
                "workspace_id": "ws_productos_v2",
                "title": "External research feed registry: ws_productos_v2",
                "created_at": "2026-04-09T10:00:00Z",
                "feeds": [
                    {
                        "feed_id": "feed_market_validation",
                        "title": "Market validation feed",
                        "source_type": "market_validation",
                        "uri": "https://example.com/feed.xml",
                        "trust_tier": "primary",
                        "refresh_cadence": "weekly",
                        "health_status": "healthy",
                        "health_reason": "Feed produced candidate results.",
                        "last_checked_at": "2026-04-09T10:00:00Z",
                        "last_success_at": "2026-03-25T10:00:00Z",
                        "last_item_count": 1,
                        "cadence_status": "stale",
                        "cadence_reason": "Feed is materially past its weekly cadence and should not be trusted without refresh.",
                    }
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (workspace_copy / "outputs" / "research").mkdir(parents=True, exist_ok=True)
    (workspace_copy / "outputs" / "research" / "external-research-manifest.selected.json").write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "source_id": "src_market",
                        "question_id": "research_q_productos_proof_posture",
                        "uri": "https://example.com/market-proof",
                    }
                ]
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (workspace_copy / "artifacts" / "external_research_review.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "external_research_review_id": "external_research_review_ws_productos_v2",
                "workspace_id": "ws_productos_v2",
                "review_status": "clear",
                "accepted_source_ids": ["src_market"],
                "contradiction_items": [],
                "review_items": [],
                "recommendation": "continue_with_refresh",
                "created_at": "2026-04-09T10:00:00Z",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    output_path = tmp_path / "v5-cutover-plan.md"
    result = _run_self_hosting_cli(
        root_dir,
        workspace_copy,
        "cutover",
        "--target-version",
        "5.0.0",
        "--output-path",
        str(output_path),
    )

    assert result.returncode == 0, result.stderr or result.stdout
    markdown = output_path.read_text(encoding="utf-8")
    assert "## Feed Governance Blockers" in markdown
    assert "feed registry has materially degraded feeds" in markdown
    assert "## Governed Research Blockers" not in markdown


def test_productos_v5_command(root_dir: Path, self_hosting_workspace_dir: Path, tmp_path: Path):
    archived_v5_dir = self_hosting_workspace_dir / "archive" / "historical-artifacts" / "v5_lifecycle_traceability"
    release_5_path = root_dir / "registry" / "releases" / "release_5_0_0.json"
    if not archived_v5_dir.exists() or not release_5_path.exists():
        pytest.skip("Historical V5 validation surface is not included in this repo boundary.")

    result = _run_self_hosting_cli(root_dir, self_hosting_workspace_dir, "v5", "--output-dir", str(tmp_path))

    assert result.returncode == 0, result.stderr or result.stdout
    assert "V5 Bundle: Lifecycle traceability through PRD handoff" in result.stdout
    assert "Target Release: 5.0.0" in result.stdout
    assert "Scenario Status: passed" in result.stdout
    assert "Release Decision: go" in result.stdout
    assert (tmp_path / "runtime_scenario_report_v5_lifecycle_traceability.json").exists()
    assert (tmp_path / "release_gate_decision_v5_lifecycle_traceability.json").exists()
    assert (tmp_path / "ralph_loop_state_v5_lifecycle_traceability.json").exists()


def test_productos_v6_command(root_dir: Path, self_hosting_workspace_dir: Path, tmp_path: Path):
    result = _run_self_hosting_cli(root_dir, self_hosting_workspace_dir, "v6", "--output-dir", str(tmp_path))

    assert result.returncode == 0, result.stderr or result.stdout
    assert "V6 Bundle: Lifecycle traceability through release readiness" in result.stdout
    assert "Target Release: 6.0.0" in result.stdout
    assert "Scenario Status: passed" in result.stdout
    assert "Release Decision: go" in result.stdout
    assert (tmp_path / "runtime_scenario_report_v6_lifecycle_traceability.json").exists()
    assert (tmp_path / "release_gate_decision_v6_lifecycle_traceability.json").exists()
    assert (tmp_path / "ralph_loop_state_v6_lifecycle_traceability.json").exists()


def test_productos_v7_command(root_dir: Path, self_hosting_workspace_dir: Path, tmp_path: Path):
    result = _run_self_hosting_cli(root_dir, self_hosting_workspace_dir, "v7", "--output-dir", str(tmp_path))

    assert result.returncode == 0, result.stderr or result.stdout
    assert "V7 Bundle: Lifecycle traceability through outcome review" in result.stdout
    assert "Target Release: 7.0.0" in result.stdout
    assert "Scenario Status: passed" in result.stdout
    assert "Release Decision: go" in result.stdout
    assert (tmp_path / "runtime_scenario_report_v7_lifecycle_traceability.json").exists()
    assert (tmp_path / "release_gate_decision_v7_lifecycle_traceability.json").exists()
    assert (tmp_path / "ralph_loop_state_v7_lifecycle_traceability.json").exists()


def test_productos_run_discover_command_exports_phase_artifacts(root_dir: Path, self_hosting_workspace_dir: Path, tmp_path: Path):
    result = _run_self_hosting_cli(root_dir, self_hosting_workspace_dir, "run", "discover", "--output-dir", str(tmp_path))

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Phase: discover" in result.stdout
    assert "Session Status: completed" in result.stdout
    assert "Context Pack: context_pack_ws_productos_v2_bounded_baseline" in result.stdout
    assert (tmp_path / "context_pack.json").exists()
    assert (tmp_path / "discover_problem_brief.json").exists()
    assert (tmp_path / "discover_concept_brief.json").exists()
    assert (tmp_path / "discover_prd.json").exists()
    assert (tmp_path / "discover_execution_session_state.json").exists()
    assert (tmp_path / "discover_feature_scorecard.json").exists()


def test_productos_run_discover_persist_uses_persisted_outputs_for_scoring(root_dir: Path, self_hosting_workspace_dir: Path, tmp_path: Path):
    workspace_copy = tmp_path / "workspace-copy"
    shutil.copytree(self_hosting_workspace_dir, workspace_copy)

    persist_result = _run_self_hosting_cli(root_dir, workspace_copy, "run", "discover", "--persist")
    assert persist_result.returncode == 0, persist_result.stderr or persist_result.stdout

    persisted_dir = workspace_copy / "outputs" / "discover"
    assert (persisted_dir / "discover_problem_brief.json").exists()
    assert (persisted_dir / "discover_concept_brief.json").exists()
    assert (persisted_dir / "discover_prd.json").exists()

    export_dir = tmp_path / "persisted-discover-export"
    rerun_result = _run_self_hosting_cli(root_dir, workspace_copy, "run", "discover", "--output-dir", str(export_dir))
    assert rerun_result.returncode == 0, rerun_result.stderr or rerun_result.stdout

    scorecard = json.loads((export_dir / "discover_feature_scorecard.json").read_text(encoding="utf-8"))
    assert scorecard["overall_score"] == 5
    assert scorecard["provenance_classification"] == "real"
    assert scorecard["adoption_recommendation"] == "promote_as_standard"
    assert scorecard["blocked_by"] == []


def test_productos_run_align_command_exports_phase_artifacts(root_dir: Path, self_hosting_workspace_dir: Path, tmp_path: Path):
    result = _run_self_hosting_cli(root_dir, self_hosting_workspace_dir, "run", "align", "--output-dir", str(tmp_path))

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Phase: align" in result.stdout
    assert "Session Status: completed" in result.stdout
    assert (tmp_path / "context_pack.json").exists()
    assert (tmp_path / "align_execution_session_state.json").exists()
    assert (tmp_path / "align_document_sync_state.json").exists()
    assert (tmp_path / "market_distribution_report.json").exists()
    assert (tmp_path / "presentation_brief.json").exists()
    assert (tmp_path / "presentation_story.json").exists()
    assert (tmp_path / "presentation_render_spec.json").exists()
    assert (tmp_path / "presentation_publish_check.json").exists()
    assert (tmp_path / "docs_alignment_feature_scorecard.json").exists()
    assert (tmp_path / "presentation_feature_scorecard.json").exists()


def test_productos_run_align_persist_uses_persisted_outputs_for_presentation_scoring(root_dir: Path, self_hosting_workspace_dir: Path, tmp_path: Path):
    workspace_copy = tmp_path / "workspace-copy"
    shutil.copytree(self_hosting_workspace_dir, workspace_copy)

    persist_result = _run_self_hosting_cli(root_dir, workspace_copy, "run", "align", "--persist")
    assert persist_result.returncode == 0, persist_result.stderr or persist_result.stdout

    persisted_dir = workspace_copy / "outputs" / "align"
    assert (persisted_dir / "presentation_brief.json").exists()
    assert (persisted_dir / "presentation_story.json").exists()
    assert (persisted_dir / "presentation_render_spec.json").exists()
    assert (persisted_dir / "presentation_publish_check.json").exists()

    export_dir = tmp_path / "persisted-align-export"
    rerun_result = _run_self_hosting_cli(root_dir, workspace_copy, "run", "align", "--output-dir", str(export_dir))
    assert rerun_result.returncode == 0, rerun_result.stderr or rerun_result.stdout

    scorecard = json.loads((export_dir / "presentation_feature_scorecard.json").read_text(encoding="utf-8"))
    assert scorecard["overall_score"] == 5
    assert scorecard["provenance_classification"] == "real"
    assert scorecard["adoption_recommendation"] == "promote_as_standard"
    assert scorecard["blocked_by"] == []


def test_productos_run_operate_command_exports_phase_artifacts(root_dir: Path, self_hosting_workspace_dir: Path, tmp_path: Path):
    result = _run_self_hosting_cli(root_dir, self_hosting_workspace_dir, "run", "operate", "--output-dir", str(tmp_path))

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Phase: operate" in result.stdout
    assert "Session Status: completed" in result.stdout
    assert (tmp_path / "context_pack.json").exists()
    assert (tmp_path / "operate_execution_session_state.json").exists()
    assert (tmp_path / "operate_status_mail.json").exists()
    assert (tmp_path / "operate_issue_log.json").exists()
    assert (tmp_path / "weekly_pm_autopilot_feature_scorecard.json").exists()


def test_productos_run_operate_persist_uses_persisted_outputs_for_scoring(root_dir: Path, self_hosting_workspace_dir: Path, tmp_path: Path):
    workspace_copy = tmp_path / "workspace-copy"
    shutil.copytree(self_hosting_workspace_dir, workspace_copy)

    persist_result = _run_self_hosting_cli(root_dir, workspace_copy, "run", "operate", "--persist")
    assert persist_result.returncode == 0, persist_result.stderr or persist_result.stdout

    persisted_dir = workspace_copy / "outputs" / "operate"
    assert (persisted_dir / "operate_status_mail.json").exists()
    assert (persisted_dir / "operate_issue_log.json").exists()

    export_dir = tmp_path / "persisted-operate-export"
    rerun_result = _run_self_hosting_cli(root_dir, workspace_copy, "run", "operate", "--output-dir", str(export_dir))
    assert rerun_result.returncode == 0, rerun_result.stderr or rerun_result.stdout

    scorecard = json.loads((export_dir / "weekly_pm_autopilot_feature_scorecard.json").read_text(encoding="utf-8"))
    assert scorecard["overall_score"] == 5
    assert scorecard["provenance_classification"] == "real"
    assert scorecard["adoption_recommendation"] == "promote_as_standard"
    assert scorecard["blocked_by"] == []


def test_productos_plan_research_builds_plan_from_fallback_problem_brief(
    root_dir: Path, self_hosting_workspace_dir: Path, tmp_path: Path
):
    workspace_copy = tmp_path / "workspace-copy"
    shutil.copytree(self_hosting_workspace_dir, workspace_copy)

    result = _run_self_hosting_cli(root_dir, workspace_copy, "plan-research", "--output-dir", str(tmp_path))

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Research Plan:" in result.stdout
    assert "Planned Questions:" in result.stdout
    assert (tmp_path / "external_research_plan.json").exists()
    assert (workspace_copy / "artifacts" / "external_research_plan.json").exists()
    assert (workspace_copy / "outputs" / "research" / "external-research-manifest.template.json").exists()

    plan = json.loads((workspace_copy / "artifacts" / "external_research_plan.json").read_text(encoding="utf-8"))
    assert len(plan["prioritized_questions"]) >= 1
    assert plan["coverage_summary"]["recommended_next_step"].startswith("Fill the source manifest template")


def test_productos_run_improve_command_exports_phase_artifacts(root_dir: Path, self_hosting_workspace_dir: Path, tmp_path: Path):
    result = _run_self_hosting_cli(root_dir, self_hosting_workspace_dir, "run", "improve", "--output-dir", str(tmp_path))

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Phase: improve" in result.stdout
    assert "Session Status: completed" in result.stdout
    assert (tmp_path / "context_pack.json").exists()
    assert (tmp_path / "eval_suite_manifest.json").exists()
    assert (tmp_path / "eval_run_report.json").exists()
    assert (tmp_path / "next_version_release_gate_decision.json").exists()
    assert (tmp_path / "improve_execution_session_state.json").exists()
    assert (tmp_path / "improve_improvement_loop_state.json").exists()
    assert (tmp_path / "adapter_parity_report.json").exists()
    assert (tmp_path / "market_refresh_report.json").exists()
    assert (tmp_path / "self_improvement_feature_scorecard.json").exists()
    assert (tmp_path / "feature_portfolio_review.json").exists()
    assert (tmp_path / "next_version_release_review.md").exists()


def test_productos_run_improve_persist_uses_persisted_review_for_scoring(root_dir: Path, self_hosting_workspace_dir: Path, tmp_path: Path):
    workspace_copy = tmp_path / "workspace-copy"
    shutil.copytree(self_hosting_workspace_dir, workspace_copy)

    persist_result = _run_self_hosting_cli(root_dir, workspace_copy, "run", "improve", "--persist")
    assert persist_result.returncode == 0, persist_result.stderr or persist_result.stdout

    persisted_dir = workspace_copy / "outputs" / "improve"
    assert (persisted_dir / "eval_run_report.json").exists()
    assert (persisted_dir / "feature_portfolio_review.json").exists()
    assert (persisted_dir / "next_version_release_gate_decision.json").exists()
    assert (persisted_dir / "next_version_release_review.md").exists()
    assert (workspace_copy / "docs" / "planning" / "next-version-release-review.md").exists()

    export_dir = tmp_path / "persisted-improve-export"
    rerun_result = _run_self_hosting_cli(root_dir, workspace_copy, "run", "improve", "--output-dir", str(export_dir))
    assert rerun_result.returncode == 0, rerun_result.stderr or rerun_result.stdout

    scorecard = json.loads((export_dir / "self_improvement_feature_scorecard.json").read_text(encoding="utf-8"))
    assert scorecard["overall_score"] == 5
    assert scorecard["adoption_recommendation"] == "promote_as_standard"
    assert scorecard["blocked_by"] == []
    workspace_review_md = (workspace_copy / "docs" / "planning" / "next-version-release-review.md").read_text(
        encoding="utf-8"
    )
    assert "# Next-Version Release Review" in workspace_review_md


def test_productos_run_improve_blocks_promotion_when_external_research_review_requires_pm_review(
    root_dir: Path, self_hosting_workspace_dir: Path, tmp_path: Path
):
    workspace_copy = tmp_path / "workspace-copy"
    shutil.copytree(self_hosting_workspace_dir, workspace_copy)

    (workspace_copy / "artifacts" / "external_research_review.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "external_research_review_id": "external_research_review_ws_productos_v2",
                "workspace_id": "ws_productos_v2",
                "review_status": "review_required",
                "accepted_source_ids": ["src_proof", "src_competitor"],
                "contradiction_items": [
                    {
                        "contradiction_id": "external_contradiction_proof_posture",
                        "topic": "proof_posture",
                        "severity": "moderate",
                        "statement": "External sources disagree on whether buyers already require measurable governance proof.",
                        "question_ids": ["research_q_codesync_outcomes_proof"],
                        "source_ids": ["src_proof", "src_competitor"],
                    }
                ],
                "review_items": [
                    "External sources disagree on whether buyers already require measurable governance proof."
                ],
                "recommendation": "pm_review_required",
                "created_at": "2026-04-08T10:00:00Z",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    export_dir = tmp_path / "research-gated-improve-export"
    result = _run_self_hosting_cli(root_dir, workspace_copy, "run", "improve", "--output-dir", str(export_dir))

    assert result.returncode == 0, result.stderr or result.stdout
    portfolio = json.loads((export_dir / "feature_portfolio_review.json").read_text(encoding="utf-8"))
    release_gate = json.loads((export_dir / "next_version_release_gate_decision.json").read_text(encoding="utf-8"))

    assert portfolio["truthfulness_status"] == "blocked"
    assert portfolio["top_priority_feature_id"] == "market_intelligence"
    assert any("external research" in item.lower() for item in portfolio["highlighted_risks"])
    assert release_gate["decision"] == "no_go"
    assert any("external research" in item.lower() for item in release_gate["known_gaps"])
    review_md = (export_dir / "next_version_release_review.md").read_text(encoding="utf-8")
    assert "## Governed Research Blockers" in review_md


def test_productos_run_improve_blocks_promotion_when_research_discovery_finds_no_sources(
    root_dir: Path, self_hosting_workspace_dir: Path, tmp_path: Path
):
    workspace_copy = tmp_path / "workspace-copy"
    shutil.copytree(self_hosting_workspace_dir, workspace_copy)

    (workspace_copy / "artifacts" / "research_brief.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "research_brief_id": "research_brief_ws_productos_v2",
                "workspace_id": "ws_productos_v2",
                "title": "Research Brief: ProductOS proof posture",
                "summary": "Validate the external proof posture before promotion.",
                "target_segment_refs": [],
                "insights": [],
                "known_gaps": ["Need external validation on governance proof posture."],
                "external_research_questions": [
                    {
                        "question_id": "research_q_productos_proof_posture",
                        "question": "Do buyers expect measurable governance proof before adopting ProductOS-like systems?",
                        "recommended_source_type": "market_validation",
                        "why_it_matters": "The release claim should not overstate validated proof posture.",
                    }
                ],
                "created_at": "2026-04-08T10:00:00Z",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (workspace_copy / "artifacts" / "external_research_plan.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "external_research_plan_id": "external_research_plan_ws_productos_v2",
                "workspace_id": "ws_productos_v2",
                "title": "External research plan",
                "generated_from_artifact_id": "research_brief_ws_productos_v2",
                "research_objective": "Validate the external proof posture before promotion.",
                "prioritized_questions": [
                    {
                        "question_id": "research_q_productos_proof_posture",
                        "question": "Do buyers expect measurable governance proof before adopting ProductOS-like systems?",
                        "why_it_matters": "The release claim should not overstate validated proof posture.",
                        "recommended_source_type": "market_validation",
                        "priority": "high",
                        "search_queries": ["product operations governance proof measurable rollout"],
                        "source_requirements": ["Fresh operator or market validation evidence"],
                    }
                ],
                "coverage_summary": {
                    "known_gaps": ["Need external validation on governance proof posture."],
                    "claims_needing_validation": ["Governance proof posture is customer-safe to claim."],
                    "recommended_next_step": "Run source discovery and refresh research artifacts.",
                },
                "created_at": "2026-04-08T10:00:00Z",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (workspace_copy / "artifacts" / "external_research_source_discovery.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "external_research_source_discovery_id": "external_research_source_discovery_ws_productos_v2",
                "workspace_id": "ws_productos_v2",
                "generated_from_plan_id": "external_research_plan_ws_productos_v2",
                "search_provider": "duckduckgo",
                "search_status": "no_results",
                "discovered_questions": [
                    {
                        "question_id": "research_q_productos_proof_posture",
                        "query": "product operations governance proof measurable rollout",
                        "source_type": "market_validation",
                        "candidate_count": 0,
                        "queries_attempted": 1,
                        "providers_attempted": ["duckduckgo"],
                    }
                ],
                "candidate_sources": [],
                "created_at": "2026-04-08T10:00:00Z",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    export_dir = tmp_path / "research-discovery-blocked-improve-export"
    result = _run_self_hosting_cli(root_dir, workspace_copy, "run", "improve", "--output-dir", str(export_dir))

    assert result.returncode == 0, result.stderr or result.stdout
    portfolio = json.loads((export_dir / "feature_portfolio_review.json").read_text(encoding="utf-8"))
    release_gate = json.loads((export_dir / "next_version_release_gate_decision.json").read_text(encoding="utf-8"))

    assert portfolio["truthfulness_status"] == "blocked"
    assert portfolio["top_priority_feature_id"] == "market_intelligence"
    assert any("no usable candidate sources" in item.lower() for item in portfolio["highlighted_risks"])
    assert release_gate["decision"] == "no_go"
    assert any("no usable candidate sources" in item.lower() for item in release_gate["known_gaps"])
    review_md = (export_dir / "next_version_release_review.md").read_text(encoding="utf-8")
    assert "## Governed Research Blockers" in review_md


def test_productos_run_improve_carries_feed_governance_blockers_into_release_gate_artifact(
    root_dir: Path, self_hosting_workspace_dir: Path, tmp_path: Path
):
    workspace_copy = tmp_path / "workspace-copy"
    shutil.copytree(self_hosting_workspace_dir, workspace_copy)

    (workspace_copy / "artifacts" / "research_brief.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "research_brief_id": "research_brief_ws_productos_v2",
                "workspace_id": "ws_productos_v2",
                "title": "Research Brief: ProductOS proof posture",
                "summary": "Validate the external proof posture before promotion.",
                "target_segment_refs": [],
                "insights": [],
                "known_gaps": ["Need governed market validation."],
                "external_research_questions": [
                    {
                        "question_id": "research_q_productos_proof_posture",
                        "question": "Do buyers expect measurable governance proof before adopting ProductOS-like systems?",
                        "recommended_source_type": "market_validation",
                        "why_it_matters": "The release claim should not overstate validated proof posture.",
                    }
                ],
                "created_at": "2026-04-09T10:00:00Z",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (workspace_copy / "artifacts" / "external_research_plan.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "external_research_plan_id": "external_research_plan_ws_productos_v2",
                "workspace_id": "ws_productos_v2",
                "title": "External research plan",
                "generated_from_artifact_id": "research_brief_ws_productos_v2",
                "research_objective": "Validate the external proof posture before promotion.",
                "prioritized_questions": [
                    {
                        "question_id": "research_q_productos_proof_posture",
                        "question": "Do buyers expect measurable governance proof before adopting ProductOS-like systems?",
                        "why_it_matters": "The release claim should not overstate validated proof posture.",
                        "recommended_source_type": "market_validation",
                        "priority": "high",
                        "search_queries": ["product operations governance proof measurable rollout"],
                        "source_requirements": ["Fresh operator or market validation evidence"],
                    }
                ],
                "coverage_summary": {
                    "known_gaps": ["Need governed market validation."],
                    "claims_needing_validation": ["Governance proof posture is customer-safe to claim."],
                    "recommended_next_step": "Refresh governed feed coverage and rerun the research loop.",
                },
                "created_at": "2026-04-09T10:00:00Z",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (workspace_copy / "artifacts" / "external_research_source_discovery.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "external_research_source_discovery_id": "external_research_source_discovery_ws_productos_v2",
                "workspace_id": "ws_productos_v2",
                "generated_from_plan_id": "external_research_plan_ws_productos_v2",
                "search_provider": "feed_registry,duckduckgo",
                "search_status": "completed",
                "discovered_questions": [
                    {
                        "question_id": "research_q_productos_proof_posture",
                        "query": "product operations governance proof measurable rollout",
                        "source_type": "market_validation",
                        "candidate_count": 1,
                        "queries_attempted": 1,
                        "providers_attempted": ["feed_registry", "duckduckgo"],
                    }
                ],
                "candidate_sources": [
                    {
                        "source_id": "research_q_productos_proof_posture_candidate_1",
                        "question_id": "research_q_productos_proof_posture",
                        "source_type": "market_validation",
                        "title": "Market validation source",
                        "uri": "https://example.com/market-proof",
                        "snippet": "Buyer proof posture note.",
                        "search_query": "product operations governance proof measurable rollout",
                        "selection_status": "suggested",
                        "provider": "feed_registry",
                        "domain": "example.com",
                        "quality_score": 9,
                        "selection_reason": "official docs or trust domain",
                        "freshness_expectation": "fresh",
                    }
                ],
                "created_at": "2026-04-09T10:00:00Z",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (workspace_copy / "artifacts" / "external_research_feed_registry.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "external_research_feed_registry_id": "external_research_feed_registry_ws_productos_v2",
                "workspace_id": "ws_productos_v2",
                "title": "External research feed registry: ws_productos_v2",
                "created_at": "2026-04-09T10:00:00Z",
                "feeds": [
                    {
                        "feed_id": "feed_market_validation",
                        "title": "Market validation feed",
                        "source_type": "market_validation",
                        "uri": "https://example.com/feed.xml",
                        "trust_tier": "primary",
                        "refresh_cadence": "weekly",
                        "health_status": "healthy",
                        "health_reason": "Feed produced candidate results.",
                        "last_checked_at": "2026-04-09T10:00:00Z",
                        "last_success_at": "2026-03-25T10:00:00Z",
                        "last_item_count": 1,
                        "cadence_status": "stale",
                        "cadence_reason": "Feed is materially past its weekly cadence and should not be trusted without refresh.",
                    }
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (workspace_copy / "outputs" / "research").mkdir(parents=True, exist_ok=True)
    (workspace_copy / "outputs" / "research" / "external-research-manifest.selected.json").write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "source_id": "src_market",
                        "question_id": "research_q_productos_proof_posture",
                        "uri": "https://example.com/market-proof",
                    }
                ]
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (workspace_copy / "artifacts" / "external_research_review.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "external_research_review_id": "external_research_review_ws_productos_v2",
                "workspace_id": "ws_productos_v2",
                "review_status": "clear",
                "accepted_source_ids": ["src_market"],
                "contradiction_items": [],
                "review_items": [],
                "recommendation": "continue_with_refresh",
                "created_at": "2026-04-09T10:00:00Z",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    export_dir = tmp_path / "feed-governance-improve-export"
    result = _run_self_hosting_cli(root_dir, workspace_copy, "run", "improve", "--output-dir", str(export_dir))

    assert result.returncode == 0, result.stderr or result.stdout
    portfolio = json.loads((export_dir / "feature_portfolio_review.json").read_text(encoding="utf-8"))
    release_gate = json.loads((export_dir / "next_version_release_gate_decision.json").read_text(encoding="utf-8"))

    assert portfolio["truthfulness_status"] == "blocked"
    assert portfolio["top_priority_feature_id"] == "market_intelligence"
    assert any("feed registry" in item.lower() for item in portfolio["highlighted_risks"])
    assert release_gate["decision"] == "no_go"
    assert any("feed registry" in item.lower() for item in release_gate["known_gaps"])
    assert release_gate["blocker_categories"]["feed_governance_blockers"]
    assert any("feed registry" in item.lower() for item in release_gate["blocker_categories"]["feed_governance_blockers"])
    assert release_gate["blocker_categories"]["governed_research_blockers"] == []
    review_md = (export_dir / "next_version_release_review.md").read_text(encoding="utf-8")
    assert "## Feed Governance Blockers" in review_md


def test_productos_export_command_writes_bundle(root_dir: Path, self_hosting_workspace_dir: Path, tmp_path: Path):
    output_dir = tmp_path / "bundle"
    result = _run_self_hosting_cli(root_dir, self_hosting_workspace_dir, "export", "--output-dir", str(output_dir))

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Exported 40 artifacts" in result.stdout

    portfolio_path = output_dir / "feature_portfolio_review.json"
    assert portfolio_path.exists()
    payload = json.loads(portfolio_path.read_text(encoding="utf-8"))
    assert payload["top_priority_feature_id"] == "v5_bundle_selection"


def test_productos_trace_item_command(root_dir: Path, self_hosting_workspace_dir: Path):
    result = _run_self_hosting_cli(root_dir, self_hosting_workspace_dir, "trace", "--item-id", "opp_pm_lifecycle_traceability")

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Item: Lifecycle traceability and stage visibility for PM work" in result.stdout
    assert "Current Stage: outcome_review" in result.stdout
    assert "- problem_framing: completed" in result.stdout


def test_productos_trace_stage_command(root_dir: Path, self_hosting_workspace_dir: Path):
    result = _run_self_hosting_cli(root_dir, self_hosting_workspace_dir, "trace", "--stage", "delivery")

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Focus Area: delivery" in result.stdout
    assert "Items: 1" in result.stdout
    assert "- story_planning: items=1, gate_passed=1" in result.stdout
    assert "- release_readiness: items=1, gate_passed=1" in result.stdout


def test_productos_thread_review_command(root_dir: Path, self_hosting_workspace_dir: Path, tmp_path: Path):
    output_path = tmp_path / "thread-review.html"
    markdown_path = tmp_path / "thread-review.md"
    package_dir = tmp_path / "thread-package"
    result = _run_self_hosting_cli(
        root_dir,
        self_hosting_workspace_dir,
        "thread-review",
        "--item-id",
        "opp_pm_lifecycle_traceability",
        "--output-path",
        str(output_path),
        "--markdown-path",
        str(markdown_path),
        "--package-dir",
        str(package_dir),
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Thread Review: Thread Review: Lifecycle traceability and stage visibility for PM work" in result.stdout
    assert "Current Stage: outcome_review" in result.stdout
    assert "Package:" in result.stdout
    assert "Slides: 4" in result.stdout
    assert output_path.exists()
    assert markdown_path.exists()
    assert (package_dir / "presentation" / "thread-review-deck.html").exists()

    html = output_path.read_text(encoding="utf-8")
    assert "Market and competitor context" in html
    assert "Release readiness" in html
    assert "Outcome review" in html
    assert "artifact-backed" in html
    assert "Decision now" in html
    assert "What the PM should do next" in html
    assert "Stable full lifecycle" in html
    assert "Summary mode" in html
    assert "opp_pm_lifecycle_traceability" in html
    markdown = markdown_path.read_text(encoding="utf-8")
    assert "## Review Actions" in markdown
    assert "## Stage Rail" in markdown


def test_productos_thread_review_index_command(root_dir: Path, self_hosting_workspace_dir: Path, tmp_path: Path):
    workspace_copy = tmp_path / "workspace-copy"
    shutil.copytree(self_hosting_workspace_dir, workspace_copy)
    artifacts_dir = workspace_copy / "artifacts"
    source_path = artifacts_dir / "item_lifecycle_state_pm_lifecycle_visibility.example.json"
    payload = json.loads(source_path.read_text(encoding="utf-8"))
    payload["item_lifecycle_state_id"] = "item_lifecycle_state_pm_release_lane"
    payload["item_ref"]["entity_id"] = "opp_pm_release_lane"
    payload["title"] = "Release lane and launch alignment"
    payload["current_stage"] = "launch_preparation"
    payload["overall_status"] = "active_delivery"
    (artifacts_dir / "item_lifecycle_state_pm_release_lane.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    output_dir = tmp_path / "thread-index"
    result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(workspace_copy),
        "thread-review-index",
        "--output-dir",
        str(output_dir),
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Thread Review Index:" in result.stdout
    assert "Threads: 2" in result.stdout
    assert (output_dir / "index.html").exists()
    assert (output_dir / "threads" / "opp_pm_lifecycle_traceability" / "thread-review.html").exists()
    assert (output_dir / "threads" / "opp_pm_release_lane" / "presentation" / "thread-review-deck.html").exists()
    index_html = (output_dir / "index.html").read_text(encoding="utf-8")
    assert "Release lane and launch alignment" in index_html
    assert "Lifecycle traceability and stage visibility for PM work" in index_html


def test_productos_thread_review_release_check_command(root_dir: Path, self_hosting_workspace_dir: Path, tmp_path: Path):
    output_dir = tmp_path / "thread-release-check"
    result = _run_self_hosting_cli(
        root_dir,
        self_hosting_workspace_dir,
        "thread-review-release-check",
        "--item-id",
        "opp_pm_lifecycle_traceability",
        "--output-dir",
        str(output_dir),
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Thread Review Release Check:" in result.stdout
    assert "Validation: ready_for_manual_validation" in result.stdout
    assert "Decision: conditional_go" in result.stdout
    assert "Target Release: v8_0_0" in result.stdout
    assert (output_dir / "release" / "validation_lane_report_thread_review_release.json").exists()
    assert (output_dir / "release" / "release_gate_decision_thread_review_release.json").exists()
    release_gate = json.loads((output_dir / "release" / "release_gate_decision_thread_review_release.json").read_text(encoding="utf-8"))
    assert release_gate["decision"] == "conditional_go"


def test_productos_init_workspace_command(root_dir: Path, tmp_path: Path):
    destination = tmp_path / "acme-workspace"
    result = _run_cli(
        root_dir,
        "init-workspace",
        "--dest",
        str(destination),
        "--workspace-id",
        "ws_acme",
        "--name",
        "Acme Product Workspace",
        "--mode",
        "enterprise",
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert destination.exists()
    assert "Initialized workspace from templates" in result.stdout

    with (destination / "workspace_manifest.yaml").open("r", encoding="utf-8") as handle:
        manifest = yaml.safe_load(handle)
    lifecycle_state = json.loads((destination / "artifacts" / "item_lifecycle_state.json").read_text(encoding="utf-8"))

    assert manifest["workspace_id"] == "ws_acme"
    assert manifest["name"] == "Acme Product Workspace"
    assert manifest["mode"] == "enterprise"
    assert manifest["active_increment_id"] == "pi_initial_01"
    assert lifecycle_state["workspace_id"] == "ws_acme"
    assert "artifacts/story_pack.json" in manifest["artifact_paths"]
    assert "artifacts/release_readiness.json" in manifest["artifact_paths"]


def test_productos_init_mission_updates_delivery_and_launch_artifacts_in_initialized_workspace(
    root_dir: Path, tmp_path: Path
):
    destination = tmp_path / "acme-workspace"
    init_result = _run_cli(
        root_dir,
        "init-workspace",
        "--dest",
        str(destination),
        "--workspace-id",
        "ws_acme",
        "--name",
        "Acme Product Workspace",
        "--mode",
        "enterprise",
    )
    assert init_result.returncode == 0, init_result.stderr or init_result.stdout

    mission_result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "init-mission",
        "--title",
        "Activation recovery mission",
        "--target-user",
        "Product manager",
        "--customer-problem",
        "Customers are not reaching activation fast enough and the PM needs one canonical mission across delivery and launch artifacts.",
        "--business-goal",
        "Increase activation while keeping execution artifacts and launch messaging aligned.",
        "--success-metric",
        "activation rate uplift",
    )
    assert mission_result.returncode == 0, mission_result.stderr or mission_result.stdout

    story_pack = json.loads((destination / "artifacts" / "story_pack.json").read_text(encoding="utf-8"))
    acceptance = json.loads((destination / "artifacts" / "acceptance_criteria_set.json").read_text(encoding="utf-8"))
    release_readiness = json.loads((destination / "artifacts" / "release_readiness.json").read_text(encoding="utf-8"))
    release_note = json.loads((destination / "artifacts" / "release_note.json").read_text(encoding="utf-8"))
    outcome_review = json.loads((destination / "artifacts" / "outcome_review.json").read_text(encoding="utf-8"))
    item_lifecycle_state = json.loads((destination / "artifacts" / "item_lifecycle_state.json").read_text(encoding="utf-8"))
    discovery_snapshot = json.loads((destination / "artifacts" / "lifecycle_stage_snapshot.json").read_text(encoding="utf-8"))
    delivery_snapshot = json.loads(
        (destination / "artifacts" / "lifecycle_stage_snapshot_delivery.json").read_text(encoding="utf-8")
    )
    launch_snapshot = json.loads(
        (destination / "artifacts" / "lifecycle_stage_snapshot_launch.json").read_text(encoding="utf-8")
    )
    outcomes_snapshot = json.loads(
        (destination / "artifacts" / "lifecycle_stage_snapshot_outcomes.json").read_text(encoding="utf-8")
    )
    full_snapshot = json.loads(
        (destination / "artifacts" / "lifecycle_stage_snapshot_full_lifecycle.json").read_text(encoding="utf-8")
    )

    assert "Activation recovery mission" in story_pack["stories"][0]["title"]
    assert any(
        ref["path"] == "docs/planning/mission-brief.md" for ref in story_pack["stories"][0]["implementation_context_refs"]
    )
    assert story_pack["feature_id"] == "feature_activation_recovery_mission_discover_loop"
    assert any(
        ref["entity_type"] == "opportunity" and ref["entity_id"] == "opportunity_activation_recovery_mission"
        for ref in story_pack["stories"][0]["linked_entity_refs"]
    )
    assert any("Activation recovery mission" in criterion["statement"] for criterion in acceptance["criteria"])
    assert release_readiness["feature_id"] == "feature_activation_recovery_mission_discover_loop"
    assert all("Activation recovery mission" in role["responsibility"] for role in release_readiness["launch_roles"])
    assert "Activation recovery mission" in release_note["summary"]
    assert release_note["feature_ids"] == ["feature_activation_recovery_mission_discover_loop"]
    assert "mission_brief_ws_acme_activation_recovery_mission" in outcome_review["evidence_refs"]
    assert "item_lifecycle_state_activation_recovery_mission_mission_trace" in outcome_review["evidence_refs"]
    assert "Activation recovery mission" in outcome_review["review_scope"]
    assert item_lifecycle_state["item_lifecycle_state_id"] == "item_lifecycle_state_activation_recovery_mission_mission_trace"
    assert item_lifecycle_state["item_ref"]["entity_id"] == "opportunity_activation_recovery_mission"
    assert item_lifecycle_state["title"] == "Mission lifecycle trace for Activation recovery mission"
    assert item_lifecycle_state["lifecycle_stages"][0]["artifact_ids"] == ["mission_brief_ws_acme_activation_recovery_mission"]
    assert item_lifecycle_state["lifecycle_stages"][3]["artifact_ids"] == [
        "problem_brief_activation_recovery_mission_mission_discover"
    ]
    assert item_lifecycle_state["lifecycle_stages"][4]["artifact_ids"] == [
        "concept_brief_activation_recovery_mission_mission_discover"
    ]
    assert item_lifecycle_state["lifecycle_stages"][6]["artifact_ids"][0] == "prd_activation_recovery_mission_mission_discover"
    assert discovery_snapshot["lifecycle_stage_snapshot_id"] == (
        "lifecycle_stage_snapshot_discovery_activation_recovery_mission_mission_trace"
    )
    assert delivery_snapshot["lifecycle_stage_snapshot_id"] == (
        "lifecycle_stage_snapshot_delivery_activation_recovery_mission_mission_trace"
    )
    assert launch_snapshot["lifecycle_stage_snapshot_id"] == (
        "lifecycle_stage_snapshot_launch_activation_recovery_mission_mission_trace"
    )
    assert outcomes_snapshot["lifecycle_stage_snapshot_id"] == (
        "lifecycle_stage_snapshot_outcomes_activation_recovery_mission_mission_trace"
    )
    assert full_snapshot["lifecycle_stage_snapshot_id"] == (
        "lifecycle_stage_snapshot_full_lifecycle_activation_recovery_mission_mission_trace"
    )
    assert discovery_snapshot["active_item_ids"] == ["opportunity_activation_recovery_mission"]
    assert delivery_snapshot["active_item_ids"] == ["opportunity_activation_recovery_mission"]
    assert launch_snapshot["active_item_ids"] == ["opportunity_activation_recovery_mission"]
    assert outcomes_snapshot["active_item_ids"] == ["opportunity_activation_recovery_mission"]
    assert full_snapshot["active_item_ids"] == ["opportunity_activation_recovery_mission"]
    assert discovery_snapshot["stage_summaries"][0]["artifact_ids"] == ["mission_brief_ws_acme_activation_recovery_mission"]
    assert any(
        summary["stage_key"] == "problem_framing"
        and summary["artifact_ids"] == ["problem_brief_activation_recovery_mission_mission_discover"]
        for summary in discovery_snapshot["stage_summaries"]
    )
    assert any(
        summary["stage_key"] == "release_readiness"
        and summary["artifact_ids"] == ["release_readiness_starter_trace_demo"]
        for summary in delivery_snapshot["stage_summaries"]
    )


def test_productos_validate_workspace_command(root_dir: Path):
    workspace_dir = root_dir / "workspaces" / "contract-intelligence-platform"
    result = _run_cli(root_dir, "--workspace-dir", str(workspace_dir), "validate-workspace")

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Workspace validation passed:" in result.stdout
    assert "3 source note cards indexed." in result.stdout


def test_productos_validate_workspace_command_reports_missing_source_note_cards(root_dir: Path, tmp_path: Path):
    workspace_dir = tmp_path / "broken-workspace"
    artifacts_dir = workspace_dir / "artifacts"
    artifacts_dir.mkdir(parents=True)
    (artifacts_dir / "research_notebook.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "research_notebook_id": "research_notebook_demo",
                "workspace_id": "ws_demo",
                "title": "Broken notebook",
                "research_question": "What is missing from this workspace evidence chain?",
                "source_note_card_ids": ["source_note_card_missing_demo"],
                "synthesis_hypothesis": "Missing evidence references should fail validation.",
                "created_at": "2026-03-29T00:00:00Z",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    result = _run_cli(root_dir, "--workspace-dir", str(workspace_dir), "validate-workspace")

    assert result.returncode == 1
    assert "references missing source note card 'source_note_card_missing_demo'" in result.stdout
