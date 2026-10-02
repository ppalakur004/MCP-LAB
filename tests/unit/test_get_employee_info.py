from equipment_request_system.domain.services import get_employee_info


def test_returns_employee_role_and_equipment(mock_data_dir):
    result = get_employee_info("e100", mock_data_dir / "employees.json")

    assert result["found"] is True
    assert result["employee"]["role"] == "software_engineer"
    assert result["employee"]["equipment"][0]["item"] == "monitor"
    assert result["employee"]["tenure_years"] >= 0


def test_unknown_employee_returns_not_found(mock_data_dir):
    result = get_employee_info("E999", mock_data_dir / "employees.json")

    assert result == {
        "found": False,
        "employee_id": "E999",
        "reason": "Employee not found.",
    }
