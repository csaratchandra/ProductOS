from conftest import assert_v10_skill_contract


def test_v10_trade_off_analysis_contract(root_dir):
    assert_v10_skill_contract(root_dir, "trade_off_analysis", "tests/test_v10_trade_off_analysis.py")
