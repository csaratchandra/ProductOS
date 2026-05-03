from conftest import assert_v10_skill_contract


def test_v10_sensitivity_analysis_contract(root_dir):
    assert_v10_skill_contract(root_dir, "sensitivity_analysis", "tests/test_v10_sensitivity_analysis.py")
