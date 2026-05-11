from __future__ import annotations

import json
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from core.python.productos_runtime.user_journey_screen_flow import (
    generate_screen_flow_svg,
    generate_screen_flow_from_journey_stages,
    link_journey_to_screens,
    generate_prototype_screen_variants,
)
from core.python.productos_runtime.journey_synthesis import synthesize_customer_journey_map


def test_screen_flow_svg_contains_nodes_from_user_journey_map(bundled_workspace_dir: Path):
    # Load user journey map example if available; skip if not
    ujm_path = bundled_workspace_dir / "artifacts" / "user_journey_map.json"
    if not ujm_path.exists():
        pytest.skip("No user_journey_map.json in fixture")
    with ujm_path.open("r", encoding="utf-8") as f:
        ujm = json.load(f)

    svg = generate_screen_flow_svg(ujm)
    assert svg.startswith("<svg")
    # Should contain rect nodes
    assert "<rect" in svg
    # Should contain step names
    for step in ujm.get("steps", [])[:2]:
        assert step["step_name"] in svg or step["step_name"][:10] in svg


def test_screen_flow_from_journey_stages_contains_all_11_stages(bundled_workspace_dir: Path):
    cjm = synthesize_customer_journey_map(bundled_workspace_dir)
    svg = generate_screen_flow_from_journey_stages(cjm)
    assert svg.startswith("<svg")
    # All 11 stage names should appear (possibly truncated)
    for stage in cjm["journey_stages"]:
        name = stage["stage_name"].replace("_", " ").title()
        assert name in svg or name[:8] in svg


def test_link_journey_to_screens_maps_stages_to_variants(bundled_workspace_dir: Path):
    cjm = synthesize_customer_journey_map(bundled_workspace_dir)
    mapping = link_journey_to_screens(cjm, prototype_record=None)
    assert len(mapping) == len(cjm["journey_stages"])
    for stage in cjm["journey_stages"]:
        assert stage["stage_id"] in mapping
        assert len(mapping[stage["stage_id"]]) > 0


def test_generate_prototype_screen_variants_creates_6_variants_per_stage(bundled_workspace_dir: Path):
    cjm = synthesize_customer_journey_map(bundled_workspace_dir)
    screens = generate_prototype_screen_variants(cjm)
    expected_count = len(cjm["journey_stages"]) * 6
    assert len(screens) == expected_count
    states = {s["state_variant"] for s in screens}
    assert states == {"loading", "empty", "normal", "error", "edge", "onboarding"}


def test_screen_flow_html_wrapper_valid(bundled_workspace_dir: Path):
    ujm_path = bundled_workspace_dir / "artifacts" / "user_journey_map.json"
    if not ujm_path.exists():
        pytest.skip("No user_journey_map.json in fixture")
    with ujm_path.open("r", encoding="utf-8") as f:
        ujm = json.load(f)
    svg = generate_screen_flow_svg(ujm)
    from core.python.productos_runtime.user_journey_screen_flow import _wrap_svg_in_html
    html = _wrap_svg_in_html(svg, ujm.get("title", "Flow"))
    soup = BeautifulSoup(html, "html.parser")
    assert soup.find("svg") is not None
    assert soup.title.string == ujm.get("title", "Flow")
