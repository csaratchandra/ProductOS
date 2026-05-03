from conftest import assert_v10_skill_contract


def test_v10_pricing_analysis_synthesis_contract(root_dir):
    assert_v10_skill_contract(root_dir, "pricing_analysis_synthesis", "tests/test_v10_pricing_analysis_synthesis.py")
