from __future__ import annotations

import json
import os
import tempfile
import uuid
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from equipment_request_system.config import settings
from equipment_request_system.domain.models import Decision, Employee, ItemPolicy, ReviewRecord


class DataError(RuntimeError):
    """Raised when a mock data source is missing or invalid."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as source:
            return json.load(source)
    except (OSError, json.JSONDecodeError) as exc:
        raise DataError(f"Unable to read valid JSON from {path}") from exc


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as target:
            json.dump(payload, target, indent=2)
            target.write("\n")
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def get_employee_info(employee_id: str, employees_path: Path | None = None) -> dict[str, Any]:
    path = employees_path or settings.employees_path
    normalized_id = employee_id.strip().upper()
    records = _load_json(path).get("employees", [])
    for raw_employee in records:
        employee = Employee.model_validate(raw_employee)
        if employee.employee_id.upper() == normalized_id:
            today = date.today()
            tenure_years = today.year - employee.hire_date.year - (
                (today.month, today.day) < (employee.hire_date.month, employee.hire_date.day)
            )
            result = employee.model_dump(mode="json")
            result["tenure_years"] = tenure_years
            return {"found": True, "employee": result}
    return {"found": False, "employee_id": normalized_id, "reason": "Employee not found."}


def get_policy_limits(role: str, policies_path: Path | None = None) -> dict[str, Any]:
    path = policies_path or settings.policies_path
    normalized_role = role.strip().lower()
    raw_policy = _load_json(path).get("roles", {}).get(normalized_role)
    if raw_policy is None:
        return {"found": False, "role": normalized_role, "reason": "Role policy not found."}
    equipment = {
        item.lower(): ItemPolicy.model_validate(limits).model_dump()
        for item, limits in raw_policy.get("equipment", {}).items()
    }
    return {"found": True, "role": normalized_role, "equipment": equipment}


def check_request_eligibility(
    employee_id: str,
    item: str,
    employees_path: Path | None = None,
    policies_path: Path | None = None,
    as_of: date | None = None,
) -> dict[str, Any]:
    normalized_item = item.strip().lower()
    employee_result = get_employee_info(employee_id, employees_path)
    if not employee_result["found"]:
        return {
            "decision": Decision.ESCALATED.value,
            "employee_id": employee_id.strip().upper(),
            "item": normalized_item,
            "reason": "Employee record was not found; a human must verify identity.",
        }

    employee = employee_result["employee"]
    policy_result = get_policy_limits(employee["role"], policies_path)
    if not policy_result["found"]:
        return {
            "decision": Decision.ESCALATED.value,
            "employee_id": employee["employee_id"],
            "item": normalized_item,
            "reason": f"No equipment policy exists for role '{employee['role']}'.",
        }

    item_policy = policy_result["equipment"].get(normalized_item)
    if item_policy is None:
        return {
            "decision": Decision.ESCALATED.value,
            "employee_id": employee["employee_id"],
            "item": normalized_item,
            "reason": f"The policy does not cover item '{normalized_item}'.",
        }

    active_items = [
        record
        for record in employee["equipment"]
        if record["item"].lower() == normalized_item and record["status"] == "active"
    ]
    maximum = item_policy["maximum_quantity"]
    source = f"{employee['role']}.{normalized_item}"
    if len(active_items) < maximum:
        return {
            "decision": Decision.APPROVED.value,
            "employee_id": employee["employee_id"],
            "item": normalized_item,
            "reason": (
                f"Employee has {len(active_items)} active {normalized_item}(s); "
                f"policy permits {maximum}."
            ),
            "policy_source": source,
        }

    if not active_items:
        return {
            "decision": Decision.DENIED.value,
            "employee_id": employee["employee_id"],
            "item": normalized_item,
            "reason": f"Policy permits no active {normalized_item}s for this role.",
            "policy_source": source,
        }

    reference_date = as_of or date.today()
    oldest_issue_date = min(date.fromisoformat(record["issued_date"]) for record in active_items)
    replacement_date = oldest_issue_date.replace(
        year=oldest_issue_date.year + item_policy["replacement_years"]
    )
    if reference_date >= replacement_date:
        return {
            "decision": Decision.APPROVED.value,
            "employee_id": employee["employee_id"],
            "item": normalized_item,
            "reason": (
                f"The oldest active {normalized_item} reached its "
                f"{item_policy['replacement_years']}-year refresh period."
            ),
            "policy_source": source,
        }
    return {
        "decision": Decision.DENIED.value,
        "employee_id": employee["employee_id"],
        "item": normalized_item,
        "reason": (
            f"The employee is at the limit of {maximum}; the next replacement date is "
            f"{replacement_date.isoformat()}."
        ),
        "policy_source": source,
    }


def flag_for_human_review(
    employee_id: str,
    request: str,
    reason: str,
    request_id: str,
    review_queue_path: Path | None = None,
) -> dict[str, Any]:
    path = review_queue_path or settings.review_queue_path
    queue = _load_json(path)
    records = queue.setdefault("requests", [])
    for record in records:
        if record.get("request_id") == request_id:
            return {"status": "already_queued", "review": record}

    record = ReviewRecord(
        review_id=f"REV-{uuid.uuid4().hex[:8].upper()}",
        request_id=request_id,
        employee_id=employee_id.strip().upper(),
        request=request.strip(),
        reason=reason.strip(),
        created_at=datetime.now(UTC),
    )
    serialized = record.model_dump(mode="json")
    records.append(serialized)
    _write_json_atomic(path, queue)
    return {"status": "queued", "review": serialized}
