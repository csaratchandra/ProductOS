from conftest import assert_v10_skill_contract


def test_v10_competitive_shift_analysis_contract(root_dir):
    assert_v10_skill_contract(root_dir, "competitive_shift_analysis", "tests/test_v10_competitive_shift_analysis.py")
