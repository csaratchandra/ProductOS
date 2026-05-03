from conftest import assert_v10_skill_contract


def test_v10_user_journey_screen_flow_contract(root_dir):
    assert_v10_skill_contract(root_dir, "user_journey_screen_flow", "tests/test_v10_user_journey.py")
