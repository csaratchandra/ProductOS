from conftest import assert_v10_skill_contract


def test_v10_customer_journey_synthesis_contract(root_dir):
    assert_v10_skill_contract(root_dir, "customer_journey_synthesis", "tests/test_v10_customer_journey.py")
