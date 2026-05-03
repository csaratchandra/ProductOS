from conftest import assert_v10_skill_contract


def test_v10_premortem_analysis_contract(root_dir):
    assert_v10_skill_contract(root_dir, "premortem_analysis", "tests/test_v10_premortem_analysis.py")
