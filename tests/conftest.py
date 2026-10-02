from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
def mock_data_dir(tmp_path: Path) -> Path:
    employees = {
        "employees": [
            {
                "employee_id": "E100",
                "name": "Test Engineer",
                "role": "software_engineer",
                "hire_date": "2020-01-01",
                "equipment": [
                    {
                        "asset_id": "MN-1",
                        "item": "monitor",
                        "issued_date": "2025-01-01",
                        "status": "active",
                    }
                ],
            },
            {
                "employee_id": "E200",
                "name": "Test Employee",
                "role": "standard_employee",
                "hire_date": "2024-01-01",
                "equipment": [
                    {
                        "asset_id": "LT-2",
                        "item": "laptop",
                        "issued_date": "2025-01-01",
                        "status": "active",
                    }
                ],
            },
            {
                "employee_id": "E300",
                "name": "Test Contractor",
                "role": "contractor",
                "hire_date": "2025-01-01",
                "equipment": [],
            },
        ]
    }
    policies = {
        "roles": {
            "software_engineer": {
                "equipment": {
                    "monitor": {"maximum_quantity": 2, "replacement_years": 3}
                }
            },
            "standard_employee": {
                "equipment": {
                    "laptop": {"maximum_quantity": 1, "replacement_years": 4}
                }
            },
        }
    }
    (tmp_path / "employees.json").write_text(json.dumps(employees), encoding="utf-8")
    (tmp_path / "policies.json").write_text(json.dumps(policies), encoding="utf-8")
    (tmp_path / "review_queue.json").write_text('{"requests": []}', encoding="utf-8")
    return tmp_path
