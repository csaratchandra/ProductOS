from conftest import assert_v10_skill_contract


def test_v10_competitive_radar_scan_contract(root_dir):
    assert_v10_skill_contract(root_dir, "competitive_radar_scan", "tests/test_v10_competitive_radar.py")
