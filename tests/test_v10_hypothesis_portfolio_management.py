from conftest import assert_v10_skill_contract


def test_v10_hypothesis_portfolio_management_contract(root_dir):
    assert_v10_skill_contract(root_dir, "hypothesis_portfolio_management", "tests/test_v10_hypothesis_portfolio_management.py")
