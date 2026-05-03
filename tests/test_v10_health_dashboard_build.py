from conftest import assert_v10_skill_contract


def test_v10_health_dashboard_build_contract(root_dir):
    assert_v10_skill_contract(root_dir, "health_dashboard_build", "tests/test_v10_health_dashboard_build.py")
