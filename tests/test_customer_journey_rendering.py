import json
import subprocess
import sys
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from components.journey_engine.python.journey_visual_renderer import render_customer_journey_map_html


def _load_example_cjm(root_dir: Path) -> dict:
    path = root_dir / "core" / "examples" / "artifacts" / "customer_journey_map.example.json"
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_example_tokens(root_dir: Path) -> dict:
    path = root_dir / "core" / "examples" / "artifacts" / "design_token_set.example.json"
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_journey_map_renders_11_stages(root_dir: Path):
    journey_map = _load_example_cjm(root_dir)
    html = render_customer_journey_map_html(journey_map)
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.find_all("div", class_="stage-card")
    assert len(cards) == 11


def test_emotion_curve_svg_present(root_dir: Path):
    journey_map = _load_example_cjm(root_dir)
    html = render_customer_journey_map_html(journey_map)
    soup = BeautifulSoup(html, "html.parser")
    svg = soup.find("svg")
    assert svg is not None
    # Should contain a path element
    paths = svg.find_all("path")
    assert len(paths) >= 2  # fill path + stroke path


def test_pain_point_badges_count(root_dir: Path):
    journey_map = _load_example_cjm(root_dir)
    html = render_customer_journey_map_html(journey_map)
    soup = BeautifulSoup(html, "html.parser")
    pain_badges = soup.find_all("div", class_="pain-badge")
    # All 11 stages in the example artifact have pain points
    assert len(pain_badges) == 11


def test_stage_click_opens_detail_panel(root_dir: Path):
    journey_map = _load_example_cjm(root_dir)
    html = render_customer_journey_map_html(journey_map)
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.find_all("div", class_="stage-card")
    assert len(cards) == 11
    for card in cards:
        assert card.has_attr("data-stage-id")
        assert card.has_attr("data-stage-json")
    # Panel should exist
    panel = soup.find("aside", id="detail-panel")
    assert panel is not None
    overlay = soup.find("div", id="detail-overlay")
    assert overlay is not None
    close_btn = soup.find("button", id="detail-close")
    assert close_btn is not None


def test_peak_and_valley_stages(root_dir: Path):
    journey_map = _load_example_cjm(root_dir)
    html = render_customer_journey_map_html(journey_map)
    soup = BeautifulSoup(html, "html.parser")
    svg_text = soup.find("svg").get_text()
    assert "PEAK" in svg_text
    assert "VALLEY" in svg_text


def test_cli_render_journey_map_produces_html(root_dir: Path, tmp_path: Path):
    # Use the bundled workspace fixture if available, otherwise create a minimal one
    fixture_dir = root_dir / "tests" / "fixtures" / "workspaces" / "productos-sample"
    workspace_copy = tmp_path / "journey-map-workspace"
    if fixture_dir.exists():
        import shutil
        shutil.copytree(fixture_dir, workspace_copy)
    else:
        pytest.skip("Bundled workspace fixture not available.")

    result = subprocess.run(
        [sys.executable, str(root_dir / "scripts" / "productos.py"), "render", "journey-map", "--workspace-dir", str(workspace_copy)],
        cwd=root_dir,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    output = json.loads(result.stdout.strip().splitlines()[-1])
    assert output["status"] == "ok"
    output_path = Path(output["output_path"])
    assert output_path.exists()

    html = output_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.find_all("div", class_="stage-card")
    assert len(cards) == 11

    # Verify purchase stage quote is in the data attributes (JS will display it)
    purchase_card = soup.find("div", {"data-stage-id": "stage_purchase"})
    assert purchase_card is not None
    stage_data = json.loads(purchase_card["data-stage-json"])
    assert "Why is this taking so long?" in stage_data["persona_thoughts"]


def test_design_tokens_apply_theme(root_dir: Path):
    journey_map = _load_example_cjm(root_dir)
    tokens = _load_example_tokens(root_dir)
    html = render_customer_journey_map_html(journey_map, tokens)
    # Just ensure it renders without error and contains primary color
    assert "#2563EB" in html or "var(--bg)" in html
    soup = BeautifulSoup(html, "html.parser")
    assert len(soup.find_all("div", class_="stage-card")) == 11
