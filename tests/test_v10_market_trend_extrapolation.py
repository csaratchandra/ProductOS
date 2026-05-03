from conftest import assert_v10_skill_contract


def test_v10_market_trend_extrapolation_contract(root_dir):
    assert_v10_skill_contract(root_dir, "market_trend_extrapolation", "tests/test_v10_market_trend_extrapolation.py")
