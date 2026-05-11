from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

from core.python.productos_runtime import build_workspace_adoption_bundle_from_source


def _run_cli(root_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/productos.py", *args],
        cwd=root_dir,
        capture_output=True,
        text=True,
        check=False,
    )


def test_workspace_adoption_builds_note_cards_from_code_first_repo(root_dir: Path, tmp_path: Path):
    source_dir = tmp_path / "adoption_workspace-code-first"
    repo_dir = source_dir / "workflow-control-repo-main"
    repo_dir.mkdir(parents=True)
    (repo_dir / "README.md").write_text(
        "# Workflow Control Repo\n\nAdoption Workspace centralizes workflow-control operations across apps, packages, and services.\n",
        encoding="utf-8",
    )
    (repo_dir / "AGENTS.md").write_text(
        "# Repository Guidelines\n\nKeep observed claims separate from inferred positioning.\n",
        encoding="utf-8",
    )
    (repo_dir / "package.json").write_text(
        json.dumps({"name": "workflow-control-repo", "private": True, "engines": {"node": "22.x"}}, indent=2) + "\n",
        encoding="utf-8",
    )
    (repo_dir / "NODEJS_UPGRADE_PLAN.md").write_text(
        "# Upgrade Plan\n\nPin Node.js to a safe version and verify deployment runtime settings.\n",
        encoding="utf-8",
    )

    bundle = build_workspace_adoption_bundle_from_source(
        root_dir,
        source_dir=source_dir,
        workspace_id="ws_adoption_workspace_code_first",
        name="Adoption Workspace Code First",
        generated_at="2026-04-29T00:00:00Z",
    )

    assert bundle["source_note_card_executive_brief"]["source_ref"] == "workflow-control-repo-main/README.md"
    assert bundle["source_note_card_self_analysis"]["source_ref"] == "workflow-control-repo-main/AGENTS.md"
    assert bundle["source_note_card_segment_map"]["source_ref"] == "workflow-control-repo-main/README.md"
    assert bundle["source_note_card_persona_pack"]["source_ref"] == "workflow-control-repo-main/AGENTS.md"
    assert bundle["source_note_card_pilot_proposal"]["source_ref"] == "workflow-control-repo-main/NODEJS_UPGRADE_PLAN.md"
    assert bundle["research_brief"]["source_note_card_ids"] == [
        bundle["source_note_card_executive_brief"]["source_note_card_id"],
        bundle["source_note_card_self_analysis"]["source_note_card_id"],
    ]


def test_adopt_workspace_dry_run_exports_adoption_workspace_bundle(root_dir: Path, adoption_workspace_dir: Path, tmp_path: Path):
    output_dir = tmp_path / "adoption-bundle"
    destination = tmp_path / "adoption_workspace-adopted"
    result = _run_cli(
        root_dir,
        "adopt-workspace",
        "--source",
        str(adoption_workspace_dir),
        "--dest",
        str(destination),
        "--workspace-id",
        "ws_adoption_workspace",
        "--name",
        "Adoption Workspace",
        "--mode",
        "research",
        "--dry-run",
        "--output-dir",
        str(output_dir),
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Source Workspace Mode: notes_first" in result.stdout
    assert "Adoption Status: dry-run" in result.stdout
    assert "Dry Run: no workspace files were written." in result.stdout
    assert not destination.exists()

    report = json.loads((output_dir / "workspace_adoption_report.json").read_text(encoding="utf-8"))
    review_queue = json.loads((output_dir / "adoption_review_queue.json").read_text(encoding="utf-8"))
    lifecycle_state = json.loads((output_dir / "item_lifecycle_state.json").read_text(encoding="utf-8"))
    thread_review_bundle = json.loads((output_dir / "thread_review_bundle.json").read_text(encoding="utf-8"))
    note_card = json.loads((output_dir / "source_note_card_executive_brief.json").read_text(encoding="utf-8"))
    research_brief = json.loads((output_dir / "research_brief.json").read_text(encoding="utf-8"))

    assert report["source_workspace_mode"] == "notes_first"
    assert report["source_file_count"] > 0
    assert "prd_adoption_workspace" in " ".join(report["generated_artifact_ids"])
    assert len(review_queue["review_items"]) >= 4
    assert lifecycle_state["current_stage"] == "prd_handoff"
    assert lifecycle_state["overall_status"] == "active_discovery"
    assert thread_review_bundle["item_ref"]["entity_id"] == lifecycle_state["item_ref"]["entity_id"]
    assert any(section["section_id"] == "market_context" for section in thread_review_bundle["sections"])
    assert any(section["section_id"] == "prd" for section in thread_review_bundle["sections"])
    assert note_card["source_ref"] == "Notes/research/01-executive-brief.md"
    assert len(research_brief["known_gaps"]) >= 2
    assert len(research_brief["external_research_questions"]) >= 2
    assert {item["claim_mode"] for item in research_brief["insights"]} >= {"observed", "inferred"}


def test_import_command_alias_persists_traceable_workspace(root_dir: Path, adoption_workspace_dir: Path, tmp_path: Path):
    destination = tmp_path / "adoption_workspace-imported"
    result = _run_cli(
        root_dir,
        "import",
        "--source",
        str(adoption_workspace_dir),
        "--dest",
        str(destination),
        "--workspace-id",
        "ws_adoption_workspace_import",
        "--name",
        "Adoption Workspace Import",
        "--mode",
        "research",
        "--emit-report",
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Adoption Status: completed" in result.stdout
    assert destination.exists()
    assert (destination / "artifacts" / "workspace_adoption_report.json").exists()


def test_adopt_workspace_persists_traceable_workspace(root_dir: Path, adoption_workspace_dir: Path, tmp_path: Path):
    destination = tmp_path / "adoption_workspace-adopted"
    result = _run_cli(
        root_dir,
        "adopt-workspace",
        "--source",
        str(adoption_workspace_dir),
        "--dest",
        str(destination),
        "--workspace-id",
        "ws_adoption_workspace",
        "--name",
        "Adoption Workspace",
        "--mode",
        "research",
        "--emit-report",
        "--emit-thread-page",
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Adoption Status: completed" in result.stdout
    assert destination.exists()

    with (destination / "workspace_manifest.yaml").open("r", encoding="utf-8") as handle:
        manifest = yaml.safe_load(handle)

    assert "artifacts/research_brief.json" in manifest["artifact_paths"]
    assert "artifacts/workspace_adoption_report.json" in manifest["artifact_paths"]
    assert "artifacts/adoption_review_queue.json" in manifest["artifact_paths"]
    assert "artifacts/thread_review_bundle.json" in manifest["artifact_paths"]

    prd = json.loads((destination / "artifacts" / "prd.json").read_text(encoding="utf-8"))
    report = json.loads((destination / "artifacts" / "workspace_adoption_report.json").read_text(encoding="utf-8"))
    snapshot = json.loads((destination / "artifacts" / "lifecycle_stage_snapshot.json").read_text(encoding="utf-8"))
    thread_review_bundle = json.loads((destination / "artifacts" / "thread_review_bundle.json").read_text(encoding="utf-8"))
    product_overview = (destination / "docs" / "product" / "product-overview.md").read_text(encoding="utf-8")
    discovery_review = (destination / "docs" / "discovery" / "discovery-review.md").read_text(encoding="utf-8")
    thread_review_page = (destination / "docs" / "review" / "thread-review.html").read_text(encoding="utf-8")

    assert prd["title"] == "PRD: Adoption Workspace workspace adoption launch lane"
    assert report["destination_workspace_path"] == destination.as_posix()
    assert snapshot["focus_area"] == "discovery"
    assert snapshot["gate_counts"]["pending"] >= 1
    assert thread_review_bundle["current_stage"] == "prd_handoff"
    assert thread_review_bundle["review_status"] == "pm_review_required"
    assert thread_review_bundle["action_items"]
    assert any(section["section_id"] == "prototype" for section in thread_review_bundle["sections"])
    assert "governed workflow-control product" in product_overview
    assert "Version: `v1`" in product_overview
    assert "## Modification Log" in product_overview
    assert "## Known Gaps" in product_overview
    assert "## Conflicted Evidence" in product_overview
    assert "## Next External Research" in product_overview
    assert "evidence-governed product definition flow" in discovery_review
    assert "Version: `v1`" in discovery_review
    assert "## Modification Log" in discovery_review
    assert "## Evidence Status" in discovery_review
    assert "## Conflicted External Evidence" in discovery_review
    assert "Thread Review: Adoption Workspace workflow control adoption path" in thread_review_page
    assert "Market and competitor context" in thread_review_page
    assert "What the PM should do next" in thread_review_page
    assert "PM review required" in thread_review_page
    assert "Decision now" in thread_review_page
    assert "Summary mode" in thread_review_page

    assert (destination / "docs" / "planning" / "workspace-adoption-report.md").exists()
    assert (destination / "docs" / "review" / "thread-review.html").exists()
    assert not (destination / "inbox" / "raw-notes" / "2026-03-22-next-version-superpowers.md").exists()
    assert not (destination / "inbox" / "transcripts" / "2026-03-22-dogfood-next-version-session.txt").exists()


def test_adopted_workspace_supports_trace_command(root_dir: Path, adoption_workspace_dir: Path, tmp_path: Path):
    destination = tmp_path / "adoption_workspace-adopted"
    adopt_result = _run_cli(
        root_dir,
        "adopt-workspace",
        "--source",
        str(adoption_workspace_dir),
        "--dest",
        str(destination),
        "--workspace-id",
        "ws_adoption_workspace",
        "--name",
        "Adoption Workspace",
        "--mode",
        "research",
    )
    assert adopt_result.returncode == 0, adopt_result.stderr or adopt_result.stdout

    trace_result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "trace",
        "--stage",
        "discovery",
    )

    assert trace_result.returncode == 0, trace_result.stderr or trace_result.stdout
    assert "Focus Area: discovery" in trace_result.stdout
    assert "- prd_handoff: items=1, gate_passed=0, gate_pending=1" in trace_result.stdout


def test_adopted_workspace_supports_ingest_discover_and_validate(root_dir: Path, adoption_workspace_dir: Path, tmp_path: Path):
    destination = tmp_path / "adoption_workspace-adopted"
    adopt_result = _run_cli(
        root_dir,
        "adopt-workspace",
        "--source",
        str(adoption_workspace_dir),
        "--dest",
        str(destination),
        "--workspace-id",
        "ws_adoption_workspace",
        "--name",
        "Adoption Workspace",
        "--mode",
        "research",
        "--include-runtime-support-assets",
    )
    assert adopt_result.returncode == 0, adopt_result.stderr or adopt_result.stdout

    ingest_result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "ingest",
    )
    assert ingest_result.returncode == 0, ingest_result.stderr or ingest_result.stdout
    assert "Ingestion Mode: manual" in ingest_result.stdout
    assert "Intake Items:" in ingest_result.stdout

    discover_output = tmp_path / "discover-output"
    discover_result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "run",
        "discover",
        "--output-dir",
        str(discover_output),
    )
    assert discover_result.returncode == 0, discover_result.stderr or discover_result.stdout
    assert "Phase: discover" in discover_result.stdout
    assert "Context Pack: context_pack_ws_adoption_workspace_bounded_baseline" in discover_result.stdout
    assert (discover_output / "discover_problem_brief.json").exists()
    assert (discover_output / "discover_concept_brief.json").exists()
    assert (discover_output / "discover_prd.json").exists()

    align_output = tmp_path / "align-output"
    align_result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "run",
        "align",
        "--output-dir",
        str(align_output),
    )
    assert align_result.returncode == 0, align_result.stderr or align_result.stdout
    presentation_brief = json.loads((align_output / "presentation_brief.json").read_text(encoding="utf-8"))
    assert presentation_brief["known_gaps"]
    assert presentation_brief["external_research_questions"]
    assert presentation_brief["contradiction_summaries"]
    assert any(
        snapshot["artifact_id"] == "research_brief_adoption_workspace"
        for snapshot in presentation_brief["source_material_snapshots"]
    )
    presentation_story = json.loads((align_output / "presentation_story.json").read_text(encoding="utf-8"))
    corridor_spec = json.loads((align_output / "workflow_corridor_spec.json").read_text(encoding="utf-8"))
    corridor_publish_check = json.loads((align_output / "corridor_publish_check.json").read_text(encoding="utf-8"))
    assert any(slide["slide_id"] == "slide_conflicted_evidence" for slide in presentation_story["slides"])
    assert corridor_spec["publication_mode"] == "publishable_external"
    assert corridor_spec["customer_safe"] is True
    assert corridor_publish_check["corridor_publish_check_id"].startswith("corridor_publish_check_")

    validate_result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "validate-workspace",
    )
    assert validate_result.returncode == 0, validate_result.stderr or validate_result.stdout
    assert "Workspace validation passed:" in validate_result.stdout
    assert "source note cards indexed." in validate_result.stdout


def test_adopt_workspace_runtime_support_assets_are_opt_in(root_dir: Path, adoption_workspace_dir: Path, tmp_path: Path):
    destination = tmp_path / "adoption_workspace-adopted-with-runtime"
    result = _run_cli(
        root_dir,
        "adopt-workspace",
        "--source",
        str(adoption_workspace_dir),
        "--dest",
        str(destination),
        "--workspace-id",
        "ws_adoption_workspace",
        "--name",
        "Adoption Workspace",
        "--mode",
        "research",
        "--include-runtime-support-assets",
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert (destination / "artifacts" / "decision_queue.example.json").exists()
    assert (destination / "artifacts" / "runtime_adapter_registry.example.json").exists()
    assert (destination / "inbox" / "raw-notes" / "2026-03-22-next-version-superpowers.md").exists()
    assert (destination / "inbox" / "transcripts" / "2026-03-22-dogfood-next-version-session.txt").exists()


def test_research_workspace_refreshes_external_research_artifacts(root_dir: Path, adoption_workspace_dir: Path, tmp_path: Path):
    destination = tmp_path / "adoption_workspace-adopted"
    adopt_result = _run_cli(
        root_dir,
        "adopt-workspace",
        "--source",
        str(adoption_workspace_dir),
        "--dest",
        str(destination),
        "--workspace-id",
        "ws_adoption_workspace",
        "--name",
        "Adoption Workspace",
        "--mode",
        "research",
    )
    assert adopt_result.returncode == 0, adopt_result.stderr or adopt_result.stdout

    competitor_source = tmp_path / "competitor.html"
    competitor_source.write_text(
        "<html><head><title>RivalFlow Competitor Overview</title></head><body>"
        "<p>RivalFlow positions itself as an all-in-one operations workflow suite.</p>"
        "<p>Its story emphasizes automation breadth, but proof boundaries and workflow control detail remain thin.</p>"
        "</body></html>",
        encoding="utf-8",
    )
    customer_source = tmp_path / "customer.txt"
    customer_source.write_text(
        "Operators still spend hours every week reconciling intake and exception handoffs. "
        "They want clearer queue control and fewer manual follow-up loops.",
        encoding="utf-8",
    )
    market_source = tmp_path / "market.html"
    market_source.write_text(
        "<html><head><title>Workflow Control Market Note</title></head><body>"
        "<p>Buyers increasingly expect workflow control, auditability, and measurable rollout proof.</p>"
        "<p>Vendor familiarity still creates real switching friction.</p>"
        "</body></html>",
        encoding="utf-8",
    )
    manifest_path = tmp_path / "external-research-manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "source_id": "src_competitor",
                        "uri": competitor_source.as_uri(),
                        "source_type": "competitor_research",
                        "published_at": "2026-04-01T00:00:00Z",
                    },
                    {
                        "source_id": "src_customer",
                        "uri": customer_source.as_uri(),
                        "source_type": "customer_evidence",
                        "published_at": "2026-04-02T00:00:00Z",
                    },
                    {
                        "source_id": "src_market",
                        "uri": market_source.as_uri(),
                        "source_type": "market_validation",
                        "published_at": "2026-04-03T00:00:00Z",
                    },
                ]
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    output_dir = tmp_path / "research-output"
    research_result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "research-workspace",
        "--input-manifest",
        str(manifest_path),
        "--output-dir",
        str(output_dir),
    )

    assert research_result.returncode == 0, research_result.stderr or research_result.stdout
    assert "Artifacts Refreshed: 13" in research_result.stdout
    assert (output_dir / "framework_registry.json").exists()
    assert (output_dir / "competitor_dossier.json").exists()
    assert (output_dir / "customer_pulse.json").exists()
    assert (output_dir / "market_analysis_brief.json").exists()
    assert (output_dir / "landscape_matrix.json").exists()
    assert (output_dir / "market_sizing_brief.json").exists()
    assert (output_dir / "market_share_brief.json").exists()
    assert (output_dir / "opportunity_portfolio_view.json").exists()
    assert (output_dir / "prioritization_decision_record.json").exists()
    assert (output_dir / "feature_prioritization_brief.json").exists()
    assert (output_dir / "external_research_review.json").exists()
    assert (output_dir / "research_notebook.json").exists()

    refreshed_research_brief = json.loads((destination / "artifacts" / "research_brief.json").read_text(encoding="utf-8"))
    external_research_review = json.loads((destination / "artifacts" / "external_research_review.json").read_text(encoding="utf-8"))
    competitor_dossier = json.loads((destination / "artifacts" / "competitor_dossier.json").read_text(encoding="utf-8"))
    customer_pulse = json.loads((destination / "artifacts" / "customer_pulse.json").read_text(encoding="utf-8"))
    market_analysis = json.loads((destination / "artifacts" / "market_analysis_brief.json").read_text(encoding="utf-8"))
    research_notebook = json.loads((destination / "artifacts" / "research_notebook.json").read_text(encoding="utf-8"))

    assert any("Refined with 3 external sources" in item for item in refreshed_research_brief["synthesis_provenance"])
    assert external_research_review["recommendation"] in {"continue_with_refresh", "pm_review_required"}
    assert refreshed_research_brief["research_notebook_ids"] == [research_notebook["research_notebook_id"]]
    assert competitor_dossier["source_artifact_ids"][:2] == [
        research_notebook["research_notebook_id"],
        refreshed_research_brief["research_brief_id"],
    ]
    assert competitor_dossier["dossier_quality"] in {"reviewable", "decision_ready"}
    assert competitor_dossier["competitors"][0]["evidence_refs"]
    assert customer_pulse["top_pain_points"][0]["description"].startswith("Operators still spend hours every week")
    assert customer_pulse["support_signal_clusters"]
    assert customer_pulse["priority_recommendation"]["focus_area"]
    assert market_analysis["source_artifact_ids"][:2] == [
        research_notebook["research_notebook_id"],
        refreshed_research_brief["research_brief_id"],
    ]
    assert (destination / "docs" / "discovery" / "external-research-refresh.md").exists()


def test_plan_research_generates_bounded_research_plan_and_manifest_template(
    root_dir: Path, adoption_workspace_dir: Path, tmp_path: Path
):
    destination = tmp_path / "adoption_workspace-adopted"
    adopt_result = _run_cli(
        root_dir,
        "adopt-workspace",
        "--source",
        str(adoption_workspace_dir),
        "--dest",
        str(destination),
        "--workspace-id",
        "ws_adoption_workspace",
        "--name",
        "Adoption Workspace",
        "--mode",
        "research",
    )
    assert adopt_result.returncode == 0, adopt_result.stderr or adopt_result.stdout

    output_dir = tmp_path / "research-plan-output"
    plan_result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "plan-research",
        "--output-dir",
        str(output_dir),
    )

    assert plan_result.returncode == 0, plan_result.stderr or plan_result.stdout
    assert "Planned Questions:" in plan_result.stdout
    assert "Signal Lanes Planned: 3/3" in plan_result.stdout
    assert (output_dir / "external_research_plan.json").exists()
    assert (destination / "artifacts" / "external_research_plan.json").exists()
    assert (destination / "outputs" / "research" / "external-research-manifest.template.json").exists()
    assert (destination / "docs" / "discovery" / "external-research-plan.md").exists()

    research_plan = json.loads((destination / "artifacts" / "external_research_plan.json").read_text(encoding="utf-8"))
    manifest_template = json.loads(
        (destination / "outputs" / "research" / "external-research-manifest.template.json").read_text(encoding="utf-8")
    )

    assert len(research_plan["prioritized_questions"]) >= 2
    assert research_plan["coverage_summary"]["required_signal_lanes"] == ["market", "competitor", "customer"]
    assert research_plan["coverage_summary"]["planned_signal_lanes"] == ["market", "competitor", "customer"]
    assert research_plan["coverage_summary"]["missing_signal_lanes"] == []
    assert all(question["search_queries"] for question in research_plan["prioritized_questions"])
    assert all(question["source_requirements"] for question in research_plan["prioritized_questions"])
    assert research_plan["coverage_summary"]["claims_needing_validation"]
    assert len(manifest_template["sources"]) == len(research_plan["suggested_manifest_sources"])
    assert all("question_id" in item for item in manifest_template["sources"])


def test_init_feed_registry_scaffolds_workspace_feed_registry(
    root_dir: Path, adoption_workspace_dir: Path, tmp_path: Path
):
    destination = tmp_path / "adoption_workspace-adopted"
    adopt_result = _run_cli(
        root_dir,
        "adopt-workspace",
        "--source",
        str(adoption_workspace_dir),
        "--dest",
        str(destination),
        "--workspace-id",
        "ws_adoption_workspace",
        "--name",
        "Adoption Workspace",
        "--mode",
        "research",
    )
    assert adopt_result.returncode == 0, adopt_result.stderr or adopt_result.stdout

    result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "init-feed-registry",
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Feed Registry:" in result.stdout
    registry = json.loads((destination / "artifacts" / "external_research_feed_registry.json").read_text(encoding="utf-8"))
    assert registry["feeds"]
    assert (destination / "outputs" / "research" / "external-research-feed-registry.template.json").exists()
    assert (destination / "docs" / "discovery" / "external-research-feed-registry.md").exists()
    assert all("source_type" in item for item in registry["feeds"])


def test_discover_research_sources_generates_autodiscovered_manifest(
    root_dir: Path, adoption_workspace_dir: Path, tmp_path: Path
):
    destination = tmp_path / "adoption_workspace-adopted"
    adopt_result = _run_cli(
        root_dir,
        "adopt-workspace",
        "--source",
        str(adoption_workspace_dir),
        "--dest",
        str(destination),
        "--workspace-id",
        "ws_adoption_workspace",
        "--name",
        "Adoption Workspace",
        "--mode",
        "research",
    )
    assert adopt_result.returncode == 0, adopt_result.stderr or adopt_result.stdout

    fixture_dir = tmp_path / "search-fixtures"
    fixture_dir.mkdir()
    (fixture_dir / "default.html").write_text(
        """
        <html><body>
        <a class="result__a" href="https://example.com/market-proof">Market Proof Note</a>
        <div class="result__snippet">Buyers increasingly expect measurable rollout proof and explicit workflow controls.</div>
        <a class="result__a" href="https://example.com/competitor-brief">Competitor Brief</a>
        <div class="result__snippet">A competing vendor emphasizes automation breadth but leaves proof boundaries vague.</div>
        <a class="result__a" href="https://example.com/customer-signal">Customer Signal</a>
        <div class="result__snippet">Operators still spend hours in manual follow-up loops and want clearer queue control.</div>
        </body></html>
        """,
        encoding="utf-8",
    )

    output_dir = tmp_path / "discovery-output"
    discover_result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "discover-research-sources",
        "--search-fixture-dir",
        str(fixture_dir),
        "--output-dir",
        str(output_dir),
    )

    assert discover_result.returncode == 0, discover_result.stderr or discover_result.stdout
    assert "Search Status: completed" in discover_result.stdout
    assert "Signal Lanes Discovered: 3/3" in discover_result.stdout
    assert (output_dir / "external_research_source_discovery.json").exists()
    assert (destination / "artifacts" / "external_research_source_discovery.json").exists()
    assert (destination / "outputs" / "research" / "external-research-manifest.autodiscovered.json").exists()
    assert (destination / "docs" / "discovery" / "external-research-source-discovery.md").exists()

    discovery = json.loads(
        (destination / "artifacts" / "external_research_source_discovery.json").read_text(encoding="utf-8")
    )
    autodiscovered_manifest = json.loads(
        (destination / "outputs" / "research" / "external-research-manifest.autodiscovered.json").read_text(encoding="utf-8")
    )

    assert discovery["search_provider"] == "duckduckgo_html"
    assert len(discovery["candidate_sources"]) >= 3
    assert {item["signal_lane_id"] for item in discovery["signal_lane_coverage"]} == {"market", "competitor", "customer"}
    assert all("quality_score" in item for item in discovery["candidate_sources"])
    assert all("provider" in item for item in discovery["candidate_sources"])
    assert autodiscovered_manifest["sources"]
    assert all(item["uri"].startswith("https://example.com/") for item in autodiscovered_manifest["sources"])


def test_discover_research_sources_uses_later_queries_when_first_query_has_no_results(
    root_dir: Path, adoption_workspace_dir: Path, tmp_path: Path
):
    def _slug(value: str) -> str:
        normalized = "".join(char.lower() if char.isalnum() else "_" for char in value)
        while "__" in normalized:
            normalized = normalized.replace("__", "_")
        return normalized.strip("_")

    destination = tmp_path / "adoption_workspace-adopted"
    adopt_result = _run_cli(
        root_dir,
        "adopt-workspace",
        "--source",
        str(adoption_workspace_dir),
        "--dest",
        str(destination),
        "--workspace-id",
        "ws_adoption_workspace",
        "--name",
        "Adoption Workspace",
        "--mode",
        "research",
    )
    assert adopt_result.returncode == 0, adopt_result.stderr or adopt_result.stdout

    plan_result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "plan-research",
    )
    assert plan_result.returncode == 0, plan_result.stderr or plan_result.stdout
    plan = json.loads((destination / "artifacts" / "external_research_plan.json").read_text(encoding="utf-8"))

    fixture_dir = tmp_path / "search-fixtures-fallback"
    fixture_dir.mkdir()
    for question in plan["prioritized_questions"]:
        fallback_query = question["search_queries"][1] if len(question["search_queries"]) > 1 else question["search_queries"][0]
        (fixture_dir / f"{_slug(fallback_query)}.html").write_text(
            (
                f'<html><body>'
                f'<a class="result__a" href="https://example.com/{question["question_id"]}">Fallback {question["question_id"]}</a>'
                f'<div class="result__snippet">Fallback result for {question["recommended_source_type"]} question coverage.</div>'
                f"</body></html>"
            ),
            encoding="utf-8",
        )

    output_dir = tmp_path / "discovery-fallback-output"
    discover_result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "discover-research-sources",
        "--search-fixture-dir",
        str(fixture_dir),
        "--output-dir",
        str(output_dir),
    )

    assert discover_result.returncode == 0, discover_result.stderr or discover_result.stdout
    assert "Search Status: completed" in discover_result.stdout

    discovery = json.loads((output_dir / "external_research_source_discovery.json").read_text(encoding="utf-8"))
    assert all(item["queries_attempted"] >= 2 for item in discovery["discovered_questions"] if item["candidate_count"] > 0)
    assert len(discovery["candidate_sources"]) == len(plan["prioritized_questions"])


def test_discover_research_sources_falls_back_to_second_provider(
    root_dir: Path, adoption_workspace_dir: Path, tmp_path: Path
):
    def _slug(value: str) -> str:
        normalized = "".join(char.lower() if char.isalnum() else "_" for char in value)
        while "__" in normalized:
            normalized = normalized.replace("__", "_")
        return normalized.strip("_")

    destination = tmp_path / "adoption_workspace-adopted"
    adopt_result = _run_cli(
        root_dir,
        "adopt-workspace",
        "--source",
        str(adoption_workspace_dir),
        "--dest",
        str(destination),
        "--workspace-id",
        "ws_adoption_workspace",
        "--name",
        "Adoption Workspace",
        "--mode",
        "research",
    )
    assert adopt_result.returncode == 0, adopt_result.stderr or adopt_result.stdout

    plan_result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "plan-research",
    )
    assert plan_result.returncode == 0, plan_result.stderr or plan_result.stdout
    plan = json.loads((destination / "artifacts" / "external_research_plan.json").read_text(encoding="utf-8"))

    fixture_dir = tmp_path / "provider-fixtures"
    (fixture_dir / "fixture_secondary").mkdir(parents=True)
    for question in plan["prioritized_questions"]:
        query = question["search_queries"][0]
        (fixture_dir / "fixture_secondary" / f"{_slug(query)}.html").write_text(
            (
                f'<html><body>'
                f'<a class="result__a" href="https://example.com/{question["question_id"]}">Provider fallback {question["question_id"]}</a>'
                f'<div class="result__snippet">Provider fallback result for {question["recommended_source_type"]}.</div>'
                f"</body></html>"
            ),
            encoding="utf-8",
        )

    output_dir = tmp_path / "provider-fallback-output"
    discover_result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "discover-research-sources",
        "--search-fixture-dir",
        str(fixture_dir),
        "--search-provider-chain",
        "fixture_primary,fixture_secondary",
        "--output-dir",
        str(output_dir),
    )

    assert discover_result.returncode == 0, discover_result.stderr or discover_result.stdout
    discovery = json.loads((output_dir / "external_research_source_discovery.json").read_text(encoding="utf-8"))
    assert discovery["search_provider"] == "fixture_primary,fixture_secondary"
    assert all("fixture_secondary" in item["providers_attempted"] for item in discovery["discovered_questions"])
    assert discovery["candidate_sources"]
    assert all(item["provider"] == "fixture_secondary" for item in discovery["candidate_sources"])


def test_discover_research_sources_parses_generic_result_blocks(
    root_dir: Path, adoption_workspace_dir: Path, tmp_path: Path
):
    def _slug(value: str) -> str:
        normalized = "".join(char.lower() if char.isalnum() else "_" for char in value)
        while "__" in normalized:
            normalized = normalized.replace("__", "_")
        return normalized.strip("_")

    destination = tmp_path / "adoption_workspace-adopted"
    adopt_result = _run_cli(
        root_dir,
        "adopt-workspace",
        "--source",
        str(adoption_workspace_dir),
        "--dest",
        str(destination),
        "--workspace-id",
        "ws_adoption_workspace",
        "--name",
        "Adoption Workspace",
        "--mode",
        "research",
    )
    assert adopt_result.returncode == 0, adopt_result.stderr or adopt_result.stdout

    plan_result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "plan-research",
    )
    assert plan_result.returncode == 0, plan_result.stderr or plan_result.stdout
    plan = json.loads((destination / "artifacts" / "external_research_plan.json").read_text(encoding="utf-8"))

    fixture_dir = tmp_path / "generic-block-fixtures"
    fixture_dir.mkdir()
    for question in plan["prioritized_questions"]:
        (fixture_dir / f"{_slug(question['search_queries'][0])}.html").write_text(
            (
                "<html><body>"
                '<div class="search-result">'
                f'<a href="https://example.com/{question["question_id"]}">{question["question_id"]} generic block</a>'
                f'<p>{question["question"]}</p>'
                "</div>"
                "</body></html>"
            ),
            encoding="utf-8",
        )

    result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "discover-research-sources",
        "--search-fixture-dir",
        str(fixture_dir),
    )

    assert result.returncode == 0, result.stderr or result.stdout
    discovery = json.loads((destination / "artifacts" / "external_research_source_discovery.json").read_text(encoding="utf-8"))
    assert discovery["candidate_sources"]
    assert all(item["uri"].startswith("https://example.com/") for item in discovery["candidate_sources"])


def test_discover_research_sources_parses_json_result_payload(
    root_dir: Path, adoption_workspace_dir: Path, tmp_path: Path
):
    def _slug(value: str) -> str:
        normalized = "".join(char.lower() if char.isalnum() else "_" for char in value)
        while "__" in normalized:
            normalized = normalized.replace("__", "_")
        return normalized.strip("_")

    destination = tmp_path / "adoption_workspace-adopted"
    adopt_result = _run_cli(
        root_dir,
        "adopt-workspace",
        "--source",
        str(adoption_workspace_dir),
        "--dest",
        str(destination),
        "--workspace-id",
        "ws_adoption_workspace",
        "--name",
        "Adoption Workspace",
        "--mode",
        "research",
    )
    assert adopt_result.returncode == 0, adopt_result.stderr or adopt_result.stdout

    plan_result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "plan-research",
    )
    assert plan_result.returncode == 0, plan_result.stderr or plan_result.stdout
    plan = json.loads((destination / "artifacts" / "external_research_plan.json").read_text(encoding="utf-8"))

    fixture_dir = tmp_path / "json-result-fixtures"
    fixture_dir.mkdir()
    for question in plan["prioritized_questions"]:
        payload = {
            "results": [
                {
                    "title": f"JSON {question['question_id']}",
                    "url": f"https://example.com/json/{question['question_id']}",
                    "snippet": question["why_it_matters"],
                }
            ]
        }
        (fixture_dir / f"{_slug(question['search_queries'][0])}.html").write_text(
            json.dumps(payload),
            encoding="utf-8",
        )

    result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "discover-research-sources",
        "--search-fixture-dir",
        str(fixture_dir),
    )

    assert result.returncode == 0, result.stderr or result.stdout
    discovery = json.loads((destination / "artifacts" / "external_research_source_discovery.json").read_text(encoding="utf-8"))
    assert discovery["candidate_sources"]
    assert all("/json/" in item["uri"] for item in discovery["candidate_sources"])


def test_discover_research_sources_parses_rss_feed_payload(
    root_dir: Path, adoption_workspace_dir: Path, tmp_path: Path
):
    def _slug(value: str) -> str:
        normalized = "".join(char.lower() if char.isalnum() else "_" for char in value)
        while "__" in normalized:
            normalized = normalized.replace("__", "_")
        return normalized.strip("_")

    destination = tmp_path / "adoption_workspace-adopted"
    adopt_result = _run_cli(
        root_dir,
        "adopt-workspace",
        "--source",
        str(adoption_workspace_dir),
        "--dest",
        str(destination),
        "--workspace-id",
        "ws_adoption_workspace",
        "--name",
        "Adoption Workspace",
        "--mode",
        "research",
    )
    assert adopt_result.returncode == 0, adopt_result.stderr or adopt_result.stdout

    plan_result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "plan-research",
    )
    assert plan_result.returncode == 0, plan_result.stderr or plan_result.stdout
    plan = json.loads((destination / "artifacts" / "external_research_plan.json").read_text(encoding="utf-8"))

    fixture_dir = tmp_path / "rss-result-fixtures"
    fixture_dir.mkdir()
    for question in plan["prioritized_questions"]:
        payload = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            "<rss><channel>"
            f"<item><title>RSS {question['question_id']}</title>"
            f"<link>https://example.com/rss/{question['question_id']}</link>"
            f"<description>{question['why_it_matters']}</description></item>"
            "</channel></rss>"
        )
        (fixture_dir / f"{_slug(question['search_queries'][0])}.html").write_text(
            payload,
            encoding="utf-8",
        )

    result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "discover-research-sources",
        "--search-fixture-dir",
        str(fixture_dir),
    )

    assert result.returncode == 0, result.stderr or result.stdout
    discovery = json.loads((destination / "artifacts" / "external_research_source_discovery.json").read_text(encoding="utf-8"))
    assert discovery["candidate_sources"]
    assert all("/rss/" in item["uri"] for item in discovery["candidate_sources"])


def test_discover_research_sources_uses_feed_registry_sources(
    root_dir: Path, adoption_workspace_dir: Path, tmp_path: Path
):
    destination = tmp_path / "adoption_workspace-adopted"
    adopt_result = _run_cli(
        root_dir,
        "adopt-workspace",
        "--source",
        str(adoption_workspace_dir),
        "--dest",
        str(destination),
        "--workspace-id",
        "ws_adoption_workspace",
        "--name",
        "Adoption Workspace",
        "--mode",
        "research",
    )
    assert adopt_result.returncode == 0, adopt_result.stderr or adopt_result.stdout

    plan_result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "plan-research",
    )
    assert plan_result.returncode == 0, plan_result.stderr or plan_result.stdout
    plan = json.loads((destination / "artifacts" / "external_research_plan.json").read_text(encoding="utf-8"))

    feed_registry_path = tmp_path / "external-research-feed-registry.json"
    feeds = []
    for question in plan["prioritized_questions"]:
        feed_path = tmp_path / f"{question['question_id']}-feed.xml"
        feed_path.write_text(
            (
                '<?xml version="1.0" encoding="UTF-8"?>'
                "<rss><channel>"
                f"<item><title>Feed {question['question_id']}</title>"
                f"<link>https://example.com/feed/{question['question_id']}</link>"
                f"<description>{question['why_it_matters']}</description></item>"
                "</channel></rss>"
            ),
            encoding="utf-8",
        )
        feeds.append(
            {
                "feed_id": f"feed_{question['question_id']}",
                "source_type": question["recommended_source_type"],
                "uri": feed_path.as_uri(),
                "title": f"Feed for {question['question_id']}",
            }
        )
    feed_registry_path.write_text(json.dumps({"feeds": feeds}, indent=2) + "\n", encoding="utf-8")

    result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "discover-research-sources",
        "--feed-registry-path",
        str(feed_registry_path),
        "--search-result-limit",
        "1",
    )

    assert result.returncode == 0, result.stderr or result.stdout
    discovery = json.loads((destination / "artifacts" / "external_research_source_discovery.json").read_text(encoding="utf-8"))
    assert discovery["candidate_sources"]
    assert discovery["search_provider"].startswith("feed_registry")
    assert all(item["provider"] == "feed_registry" for item in discovery["candidate_sources"])
    assert all("/feed/" in item["uri"] for item in discovery["candidate_sources"])


def test_discover_research_sources_uses_default_workspace_feed_registry(
    root_dir: Path, adoption_workspace_dir: Path, tmp_path: Path
):
    destination = tmp_path / "adoption_workspace-adopted"
    adopt_result = _run_cli(
        root_dir,
        "adopt-workspace",
        "--source",
        str(adoption_workspace_dir),
        "--dest",
        str(destination),
        "--workspace-id",
        "ws_adoption_workspace",
        "--name",
        "Adoption Workspace",
        "--mode",
        "research",
    )
    assert adopt_result.returncode == 0, adopt_result.stderr or adopt_result.stdout

    init_result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "init-feed-registry",
    )
    assert init_result.returncode == 0, init_result.stderr or init_result.stdout

    registry_path = destination / "artifacts" / "external_research_feed_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    for index, feed in enumerate(registry["feeds"], start=1):
        feed_path = tmp_path / f"default-feed-{index}.xml"
        feed_path.write_text(
            (
                '<?xml version="1.0" encoding="UTF-8"?>'
                "<rss><channel>"
                f"<item><title>Default Feed {index}</title>"
                f"<link>https://example.com/default-feed/{index}</link>"
                "<description>Trusted default feed result.</description></item>"
                "</channel></rss>"
            ),
            encoding="utf-8",
        )
        feed["uri"] = feed_path.as_uri()
    registry_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")

    result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "discover-research-sources",
        "--search-result-limit",
        "1",
    )

    assert result.returncode == 0, result.stderr or result.stdout
    discovery = json.loads((destination / "artifacts" / "external_research_source_discovery.json").read_text(encoding="utf-8"))
    assert discovery["candidate_sources"]
    assert discovery["search_provider"].startswith("feed_registry")


def test_discover_research_sources_updates_feed_registry_health(
    root_dir: Path, adoption_workspace_dir: Path, tmp_path: Path
):
    destination = tmp_path / "adoption_workspace-adopted"
    adopt_result = _run_cli(
        root_dir,
        "adopt-workspace",
        "--source",
        str(adoption_workspace_dir),
        "--dest",
        str(destination),
        "--workspace-id",
        "ws_adoption_workspace",
        "--name",
        "Adoption Workspace",
        "--mode",
        "research",
    )
    assert adopt_result.returncode == 0, adopt_result.stderr or adopt_result.stdout

    init_result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "init-feed-registry",
    )
    assert init_result.returncode == 0, init_result.stderr or init_result.stdout

    registry_path = destination / "artifacts" / "external_research_feed_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    assert len(registry["feeds"]) >= 2

    healthy_feed_path = tmp_path / "healthy-feed.xml"
    healthy_feed_path.write_text(
        (
            '<?xml version="1.0" encoding="UTF-8"?>'
            "<rss><channel>"
            "<item><title>Healthy Feed Source</title>"
            "<link>https://example.com/feed/healthy</link>"
            "<description>Trusted workflow evidence for governed research coverage.</description></item>"
            "</channel></rss>"
        ),
        encoding="utf-8",
    )

    registry["feeds"][0]["uri"] = healthy_feed_path.as_uri()
    registry["feeds"][1]["uri"] = (tmp_path / "missing-feed.xml").as_uri()
    if len(registry["feeds"]) > 2:
        registry["feeds"][2]["uri"] = ""
    registry_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")

    result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "discover-research-sources",
        "--search-result-limit",
        "1",
    )

    assert result.returncode == 0, result.stderr or result.stdout
    refreshed_registry = json.loads(registry_path.read_text(encoding="utf-8"))

    assert refreshed_registry["feeds"][0]["health_status"] == "healthy"
    assert refreshed_registry["feeds"][0]["last_item_count"] >= 1
    assert refreshed_registry["feeds"][0]["last_checked_at"]
    assert refreshed_registry["feeds"][0]["last_success_at"]
    assert refreshed_registry["feeds"][0]["cadence_status"]
    assert refreshed_registry["feeds"][0]["cadence_reason"]

    assert refreshed_registry["feeds"][1]["health_status"] == "error"
    assert refreshed_registry["feeds"][1]["last_checked_at"]
    assert refreshed_registry["feeds"][1]["last_error"]
    assert refreshed_registry["feeds"][1]["cadence_status"]

    if len(refreshed_registry["feeds"]) > 2:
        assert refreshed_registry["feeds"][2]["health_status"] == "unconfigured"
        assert refreshed_registry["feeds"][2]["last_item_count"] == 0
        assert refreshed_registry["feeds"][2]["cadence_status"]

    discovery_doc = (destination / "docs" / "discovery" / "external-research-source-discovery.md").read_text(
        encoding="utf-8"
    )
    registry_doc = (destination / "docs" / "discovery" / "external-research-feed-registry.md").read_text(
        encoding="utf-8"
    )
    assert "## Feed Health" in discovery_doc
    assert "healthy" in discovery_doc
    assert "Health: healthy" in registry_doc
    assert "Health: error" in registry_doc
    assert "Cadence:" in registry_doc


def test_run_research_loop_surfaces_feed_health_review_items(
    root_dir: Path, adoption_workspace_dir: Path, tmp_path: Path
):
    destination = tmp_path / "adoption_workspace-adopted"
    adopt_result = _run_cli(
        root_dir,
        "adopt-workspace",
        "--source",
        str(adoption_workspace_dir),
        "--dest",
        str(destination),
        "--workspace-id",
        "ws_adoption_workspace",
        "--name",
        "Adoption Workspace",
        "--mode",
        "research",
    )
    assert adopt_result.returncode == 0, adopt_result.stderr or adopt_result.stdout

    init_result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "init-feed-registry",
    )
    assert init_result.returncode == 0, init_result.stderr or init_result.stdout

    registry_path = destination / "artifacts" / "external_research_feed_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))

    healthy_feed_path = tmp_path / "loop-healthy-feed.xml"
    healthy_feed_path.write_text(
        (
            '<?xml version="1.0" encoding="UTF-8"?>'
            "<rss><channel>"
            "<item><title>Loop Healthy Feed Source</title>"
            "<link>https://example.com/feed/loop-healthy</link>"
            "<description>Trusted workflow evidence for governed research coverage.</description></item>"
            "</channel></rss>"
        ),
        encoding="utf-8",
    )

    registry["feeds"][0]["uri"] = healthy_feed_path.as_uri()
    unconfigured_feed_id = None
    if len(registry["feeds"]) > 1:
        registry["feeds"][1]["uri"] = ""
        unconfigured_feed_id = registry["feeds"][1]["feed_id"]
    registry_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")

    result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "run-research-loop",
        "--search-result-limit",
        "1",
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert unconfigured_feed_id is not None
    assert f"Feed `{unconfigured_feed_id}` is `unconfigured`" in result.stdout

    loop_doc = (destination / "docs" / "discovery" / "external-research-loop.md").read_text(encoding="utf-8")
    assert "## Feed Health" in loop_doc
    assert unconfigured_feed_id in loop_doc


def test_run_research_loop_chains_plan_discovery_and_refresh(
    root_dir: Path, adoption_workspace_dir: Path, tmp_path: Path
):
    def _slug(value: str) -> str:
        normalized = "".join(char.lower() if char.isalnum() else "_" for char in value)
        while "__" in normalized:
            normalized = normalized.replace("__", "_")
        return normalized.strip("_")

    destination = tmp_path / "adoption_workspace-adopted"
    adopt_result = _run_cli(
        root_dir,
        "adopt-workspace",
        "--source",
        str(adoption_workspace_dir),
        "--dest",
        str(destination),
        "--workspace-id",
        "ws_adoption_workspace",
        "--name",
        "Adoption Workspace",
        "--mode",
        "research",
    )
    assert adopt_result.returncode == 0, adopt_result.stderr or adopt_result.stdout

    plan_result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "plan-research",
    )
    assert plan_result.returncode == 0, plan_result.stderr or plan_result.stdout
    plan = json.loads((destination / "artifacts" / "external_research_plan.json").read_text(encoding="utf-8"))

    fixture_dir = tmp_path / "research-loop-fixtures"
    fixture_dir.mkdir()
    query_to_source_templates = {
        "market_validation": (
            "Workflow Proof Market Note",
            "Buyers increasingly expect measurable rollout proof and explicit workflow controls.",
        ),
        "competitor_research": (
            "RivalFlow Loop Overview",
            "A competing vendor emphasizes automation breadth but leaves proof boundaries vague.",
        ),
        "customer_evidence": (
            "Operator Loop Signal",
            "Operators still spend hours in manual follow-up loops and want clearer queue ownership.",
        ),
        "security_review": (
            "Workflow Governance Security Note",
            "Buyers expect auditability, approval boundaries, and visible governance controls before rollout.",
        ),
    }
    for question in plan["prioritized_questions"]:
        title, snippet = query_to_source_templates[question["recommended_source_type"]]
        source_path = tmp_path / f"{question['question_id']}.html"
        source_path.write_text(
            (
                f"<html><head><title>{title}</title></head><body>"
                f"<p>{snippet}</p>"
                f"<p>{question['question']}</p>"
                f"<p>{question['why_it_matters']}</p>"
                f"</body></html>"
            ),
            encoding="utf-8",
        )
        (fixture_dir / f"{_slug(question['search_queries'][0])}.html").write_text(
            (
                f'<html><body>'
                f'<a class="result__a" href="{source_path.as_uri()}">{title}</a>'
                f'<div class="result__snippet">{snippet}</div>'
                f"</body></html>"
            ),
            encoding="utf-8",
        )

    output_dir = tmp_path / "research-loop-output"
    result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "run-research-loop",
        "--search-fixture-dir",
        str(fixture_dir),
        "--output-dir",
        str(output_dir),
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Research Loop Coverage: completed" in result.stdout
    assert "Research Refresh: completed" in result.stdout
    assert f"Selected Sources: {len(plan['prioritized_questions'])}" in result.stdout
    assert "Signal Lanes Selected: 3/3" in result.stdout
    assert (output_dir / "external_research_plan.json").exists()
    assert (output_dir / "external_research_source_discovery.json").exists()
    assert (output_dir / "competitor_dossier.json").exists()
    assert (destination / "outputs" / "research" / "external-research-manifest.selected.json").exists()
    assert (destination / "docs" / "discovery" / "external-research-loop.md").exists()

    competitor_dossier = json.loads((destination / "artifacts" / "competitor_dossier.json").read_text(encoding="utf-8"))
    customer_pulse = json.loads((destination / "artifacts" / "customer_pulse.json").read_text(encoding="utf-8"))
    market_analysis = json.loads((destination / "artifacts" / "market_analysis_brief.json").read_text(encoding="utf-8"))
    discovery = json.loads((destination / "artifacts" / "external_research_source_discovery.json").read_text(encoding="utf-8"))

    assert competitor_dossier["source_artifact_ids"][:2] == [
        "research_notebook_ws_adoption_workspace",
        "research_brief_adoption_workspace",
    ]
    assert competitor_dossier["competitors"][0]["name"] == "RivalFlow Loop Overview"
    assert competitor_dossier["competitive_landscape_status"] == "named_competitor_set"
    assert competitor_dossier["dossier_quality"] in {"reviewable", "decision_ready"}
    assert "Operators still spend hours" in customer_pulse["top_pain_points"][0]["description"]
    assert any(
        phrase in market_analysis["category_summary"]
        for phrase in [
            "measurable rollout proof",
            "manual follow-up loops",
            "auditability",
        ]
    )
    assert sum(1 for item in discovery["signal_lane_coverage"] if item["selected_source_count"] > 0) == 3
    assert any(item.get("content_quality_status") == "accepted" for item in discovery["candidate_sources"])


def test_run_research_loop_filters_thin_sources_out_of_selected_manifest(
    root_dir: Path, adoption_workspace_dir: Path, tmp_path: Path
):
    def _slug(value: str) -> str:
        normalized = "".join(char.lower() if char.isalnum() else "_" for char in value)
        while "__" in normalized:
            normalized = normalized.replace("__", "_")
        return normalized.strip("_")

    destination = tmp_path / "adoption_workspace-adopted"
    adopt_result = _run_cli(
        root_dir,
        "adopt-workspace",
        "--source",
        str(adoption_workspace_dir),
        "--dest",
        str(destination),
        "--workspace-id",
        "ws_adoption_workspace",
        "--name",
        "Adoption Workspace",
        "--mode",
        "research",
    )
    assert adopt_result.returncode == 0, adopt_result.stderr or adopt_result.stdout

    plan_result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "plan-research",
    )
    assert plan_result.returncode == 0, plan_result.stderr or plan_result.stdout
    plan = json.loads((destination / "artifacts" / "external_research_plan.json").read_text(encoding="utf-8"))

    thin_source = tmp_path / "thin-source.txt"
    thin_source.write_text("workflow note", encoding="utf-8")

    fixture_dir = tmp_path / "thin-filter-fixtures"
    fixture_dir.mkdir()
    for question in plan["prioritized_questions"]:
        (fixture_dir / f"{_slug(question['search_queries'][0])}.html").write_text(
            (
                f'<html><body>'
                f'<a class="result__a" href="{thin_source.as_uri()}">Thin {question["question_id"]}</a>'
                f'<div class="result__snippet">Thin result for {question["recommended_source_type"]}.</div>'
                f"</body></html>"
            ),
            encoding="utf-8",
        )

    output_dir = tmp_path / "thin-filter-output"
    result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "run-research-loop",
        "--search-fixture-dir",
        str(fixture_dir),
        "--output-dir",
        str(output_dir),
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Research Loop Coverage: blocked" in result.stdout
    assert "Research Refresh: skipped" in result.stdout
    discovery = json.loads((destination / "artifacts" / "external_research_source_discovery.json").read_text(encoding="utf-8"))
    selected_manifest = json.loads(
        (destination / "outputs" / "research" / "external-research-manifest.selected.json").read_text(encoding="utf-8")
    )
    assert selected_manifest["sources"] == []
    assert all(item.get("content_quality_status") == "rejected" for item in discovery["candidate_sources"])


def test_discover_research_sources_prefers_domain_relevant_candidate(
    root_dir: Path, adoption_workspace_dir: Path, tmp_path: Path
):
    def _slug(value: str) -> str:
        normalized = "".join(char.lower() if char.isalnum() else "_" for char in value)
        while "__" in normalized:
            normalized = normalized.replace("__", "_")
        return normalized.strip("_")

    destination = tmp_path / "adoption_workspace-adopted"
    adopt_result = _run_cli(
        root_dir,
        "adopt-workspace",
        "--source",
        str(adoption_workspace_dir),
        "--dest",
        str(destination),
        "--workspace-id",
        "ws_adoption_workspace",
        "--name",
        "Adoption Workspace",
        "--mode",
        "research",
    )
    assert adopt_result.returncode == 0, adopt_result.stderr or adopt_result.stdout

    plan_result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "plan-research",
    )
    assert plan_result.returncode == 0, plan_result.stderr or plan_result.stdout
    plan = json.loads((destination / "artifacts" / "external_research_plan.json").read_text(encoding="utf-8"))

    fixture_dir = tmp_path / "discovery-ranking-fixtures"
    fixture_dir.mkdir()
    for question in plan["prioritized_questions"]:
        if question["recommended_source_type"] == "competitor_research":
            fixture_html = (
                '<html><body>'
                '<a class="result__a" href="https://community.example.com/rivalflow-workflow-post">Community workflow post</a>'
                '<div class="result__snippet">RivalFlow workflow overview with community comments and broad competitor observations.</div>'
                '<a class="result__a" href="https://docs.rivalflow.com/pricing">RivalFlow pricing and product docs</a>'
                '<div class="result__snippet">Official pricing, workflow automation details, and product proof boundaries.</div>'
                "</body></html>"
            )
        else:
            fixture_html = (
                '<html><body>'
                f'<a class="result__a" href="https://research.example.com/{question["question_id"]}">Research result</a>'
                f'<div class="result__snippet">{question["question"]}</div>'
                "</body></html>"
            )
        (fixture_dir / f"{_slug(question['search_queries'][0])}.html").write_text(
            fixture_html,
            encoding="utf-8",
        )

    result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "discover-research-sources",
        "--search-fixture-dir",
        str(fixture_dir),
    )

    assert result.returncode == 0, result.stderr or result.stdout
    discovery = json.loads((destination / "artifacts" / "external_research_source_discovery.json").read_text(encoding="utf-8"))
    competitor_candidates = [
        item for item in discovery["candidate_sources"]
        if item["source_type"] == "competitor_research"
    ]
    assert competitor_candidates
    suggested = next(item for item in competitor_candidates if item["selection_status"] == "suggested")
    assert suggested["uri"] == "https://docs.rivalflow.com/pricing"
    assert "official docs or trust domain" in suggested["selection_reason"] or "competitor-style product page" in suggested["selection_reason"]


def test_run_research_loop_uses_fetched_evidence_excerpt_for_selected_rationale(
    root_dir: Path, adoption_workspace_dir: Path, tmp_path: Path
):
    def _slug(value: str) -> str:
        normalized = "".join(char.lower() if char.isalnum() else "_" for char in value)
        while "__" in normalized:
            normalized = normalized.replace("__", "_")
        return normalized.strip("_")

    destination = tmp_path / "adoption_workspace-adopted"
    adopt_result = _run_cli(
        root_dir,
        "adopt-workspace",
        "--source",
        str(adoption_workspace_dir),
        "--dest",
        str(destination),
        "--workspace-id",
        "ws_adoption_workspace",
        "--name",
        "Adoption Workspace",
        "--mode",
        "research",
    )
    assert adopt_result.returncode == 0, adopt_result.stderr or adopt_result.stdout

    plan_result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "plan-research",
    )
    assert plan_result.returncode == 0, plan_result.stderr or plan_result.stdout
    plan = json.loads((destination / "artifacts" / "external_research_plan.json").read_text(encoding="utf-8"))

    fixture_dir = tmp_path / "evidence-excerpt-fixtures"
    fixture_dir.mkdir()
    expected_excerpt = "Buyers increasingly expect measurable rollout proof and explicit workflow controls before adoption."
    for question in plan["prioritized_questions"]:
        source_path = tmp_path / f"{question['question_id']}.html"
        source_path.write_text(
            (
                "<html><head><title>Evidence-rich source</title></head><body>"
                "<p>Generic search snippet should not become the final rationale.</p>"
                f"<p>{expected_excerpt}</p>"
                f"<p>{question['question']}</p>"
                "</body></html>"
            ),
            encoding="utf-8",
        )
        (fixture_dir / f"{_slug(question['search_queries'][0])}.html").write_text(
            (
                f'<html><body>'
                f'<a class="result__a" href="{source_path.as_uri()}">Evidence-rich source</a>'
                f'<div class="result__snippet">Generic result summary without the strongest proof sentence.</div>'
                f"</body></html>"
            ),
            encoding="utf-8",
        )

    result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "run-research-loop",
        "--search-fixture-dir",
        str(fixture_dir),
    )

    assert result.returncode == 0, result.stderr or result.stdout
    selected_manifest = json.loads(
        (destination / "outputs" / "research" / "external-research-manifest.selected.json").read_text(encoding="utf-8")
    )
    discovery = json.loads((destination / "artifacts" / "external_research_source_discovery.json").read_text(encoding="utf-8"))
    assert any(expected_excerpt in item["rationale"] for item in selected_manifest["sources"])
    assert any(expected_excerpt in item.get("content_quality_reason", "") for item in discovery["candidate_sources"])


def test_research_workspace_detects_html_metadata_for_summary_and_freshness(
    root_dir: Path, adoption_workspace_dir: Path, tmp_path: Path
):
    destination = tmp_path / "adoption_workspace-adopted"
    adopt_result = _run_cli(
        root_dir,
        "adopt-workspace",
        "--source",
        str(adoption_workspace_dir),
        "--dest",
        str(destination),
        "--workspace-id",
        "ws_adoption_workspace",
        "--name",
        "Adoption Workspace",
        "--mode",
        "research",
    )
    assert adopt_result.returncode == 0, adopt_result.stderr or adopt_result.stdout

    html_source = tmp_path / "metadata-source.html"
    html_source.write_text(
        (
            "<html><head>"
            '<title>Workflow Governance Market Note</title>'
            '<meta name="description" content="Fresh market validation shows buyers expect visible workflow controls and measurable rollout proof.">'
            '<meta property="article:published_time" content="2026-04-01T09:00:00Z">'
            "</head><body>"
            "<p>Body copy is less concise than the metadata description but still relevant.</p>"
            "</body></html>"
        ),
        encoding="utf-8",
    )
    manifest_path = tmp_path / "metadata-manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "source_id": "src_metadata_market",
                        "uri": html_source.as_uri(),
                        "source_type": "market_validation",
                        "question_id": "research_q_adoption_workspace_outcomes_proof",
                    }
                ]
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    result = _run_cli(
        root_dir,
        "--generated-at",
        "2026-04-08T10:00:00Z",
        "--workspace-dir",
        str(destination),
        "research-workspace",
        "--input-manifest",
        str(manifest_path),
    )

    assert result.returncode == 0, result.stderr or result.stdout
    market_analysis = json.loads((destination / "artifacts" / "market_analysis_brief.json").read_text(encoding="utf-8"))
    refresh_doc = (destination / "docs" / "discovery" / "external-research-refresh.md").read_text(encoding="utf-8")
    assert "Fresh market validation shows buyers expect visible workflow controls" in market_analysis["category_summary"]
    assert "`market_validation` `fresh`: Workflow Governance Market Note (2026-04-01T09:00:00Z)" in refresh_doc


def test_research_workspace_detects_external_contradictions(
    root_dir: Path, adoption_workspace_dir: Path, tmp_path: Path
):
    destination = tmp_path / "adoption_workspace-adopted"
    adopt_result = _run_cli(
        root_dir,
        "adopt-workspace",
        "--source",
        str(adoption_workspace_dir),
        "--dest",
        str(destination),
        "--workspace-id",
        "ws_adoption_workspace",
        "--name",
        "Adoption Workspace",
        "--mode",
        "research",
    )
    assert adopt_result.returncode == 0, adopt_result.stderr or adopt_result.stdout

    proof_source = tmp_path / "proof-source.html"
    proof_source.write_text(
        "<html><head><title>Governance Proof Note</title></head><body>"
        "<p>Buyers increasingly expect measurable rollout proof, auditability, and explicit workflow controls.</p>"
        "</body></html>",
        encoding="utf-8",
    )
    weak_source = tmp_path / "weak-source.html"
    weak_source.write_text(
        "<html><head><title>Thin Proof Note</title></head><body>"
        "<p>Proof boundaries remain thin and vague across current workflow offerings.</p>"
        "</body></html>",
        encoding="utf-8",
    )
    manifest_path = tmp_path / "contradiction-manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "source_id": "src_proof",
                        "uri": proof_source.as_uri(),
                        "source_type": "market_validation",
                        "question_id": "research_q_adoption_workspace_outcomes_proof"
                    },
                    {
                        "source_id": "src_weak",
                        "uri": weak_source.as_uri(),
                        "source_type": "competitor_research",
                        "question_id": "research_q_adoption_workspace_competitive_wedge"
                    }
                ]
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    result = _run_cli(
        root_dir,
        "--workspace-dir",
        str(destination),
        "research-workspace",
        "--input-manifest",
        str(manifest_path),
    )

    assert result.returncode == 0, result.stderr or result.stdout
    review = json.loads((destination / "artifacts" / "external_research_review.json").read_text(encoding="utf-8"))
    refreshed_research_brief = json.loads((destination / "artifacts" / "research_brief.json").read_text(encoding="utf-8"))
    assert review["review_status"] == "review_required"
    assert review["contradiction_items"]
    assert any(item["topic"] == "proof_posture" for item in review["contradiction_items"])
    assert any("proof" in item["statement"].lower() for item in refreshed_research_brief["contradictions"])
