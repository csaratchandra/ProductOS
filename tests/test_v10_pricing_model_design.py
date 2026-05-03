from conftest import assert_v10_skill_contract


def test_v10_pricing_model_design_contract(root_dir):
    assert_v10_skill_contract(root_dir, "pricing_model_design", "tests/test_v10_pricing_model_design.py")
