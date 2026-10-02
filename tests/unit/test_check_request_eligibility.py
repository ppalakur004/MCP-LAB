from datetime import date

from equipment_request_system.domain.services import check_request_eligibility


def test_approves_when_employee_is_below_quantity_limit(mock_data_dir):
    result = check_request_eligibility(
        "E100",
        "monitor",
        mock_data_dir / "employees.json",
        mock_data_dir / "policies.json",
        as_of=date(2026, 1, 1),
    )

    assert result["decision"] == "approved"


def test_denies_when_at_limit_and_refresh_is_not_due(mock_data_dir):
    result = check_request_eligibility(
        "E200",
        "laptop",
        mock_data_dir / "employees.json",
        mock_data_dir / "policies.json",
        as_of=date(2026, 1, 1),
    )

    assert result["decision"] == "denied"
    assert "2029-01-01" in result["reason"]


def test_escalates_unknown_employee(mock_data_dir):
    result = check_request_eligibility(
        "E999",
        "monitor",
        mock_data_dir / "employees.json",
        mock_data_dir / "policies.json",
    )

    assert result["decision"] == "escalated"


def test_escalates_when_role_has_no_policy(mock_data_dir):
    result = check_request_eligibility(
        "E300",
        "monitor",
        mock_data_dir / "employees.json",
        mock_data_dir / "policies.json",
    )

    assert result["decision"] == "escalated"


def test_escalates_when_item_not_in_policy(mock_data_dir):
    result = check_request_eligibility(
        "E100",
        "medical-grade monitor",
        mock_data_dir / "employees.json",
        mock_data_dir / "policies.json",
    )

    assert result["decision"] == "escalated"
    assert "does not cover" in result["reason"]


def test_approves_when_refresh_period_reached(mock_data_dir):
    result = check_request_eligibility(
        "E200",
        "laptop",
        mock_data_dir / "employees.json",
        mock_data_dir / "policies.json",
        as_of=date(2029, 1, 1),
    )

    assert result["decision"] == "approved"
