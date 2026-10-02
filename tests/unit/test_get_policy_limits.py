from equipment_request_system.domain.services import get_policy_limits


def test_returns_policy_for_known_role(mock_data_dir):
    result = get_policy_limits("Software_Engineer", mock_data_dir / "policies.json")

    assert result["found"] is True
    assert result["equipment"]["monitor"]["maximum_quantity"] == 2


def test_unknown_role_returns_not_found(mock_data_dir):
    result = get_policy_limits("contractor", mock_data_dir / "policies.json")

    assert result["found"] is False
    assert result["reason"] == "Role policy not found."
