from equipment_request_system.agent.reflection import reflect_draft, should_queue_review
from equipment_request_system.domain.models import Decision, TraceStep


def test_reflection_corrects_decision_that_conflicts_with_tool_result():
    trace = [
        TraceStep(
            step=1,
            reason="Check policy",
            tool="check_request_eligibility",
            arguments={"employee_id": "E200", "item": "laptop"},
            observation={"decision": "denied", "reason": "Refresh is not due."},
        )
    ]

    decision, response, reflection = reflect_draft(
        Decision.APPROVED,
        "Your request is approved.",
        trace,
    )

    assert decision == Decision.DENIED
    assert response == "Refresh is not due."
    assert reflection.startswith("Corrected:")


def test_reflection_confirms_matching_decision():
    trace = [
        TraceStep(
            step=1,
            reason="Check policy",
            tool="check_request_eligibility",
            arguments={"employee_id": "E100", "item": "monitor"},
            observation={"decision": "approved", "reason": "Below limit."},
        )
    ]

    decision, _, reflection = reflect_draft(
        Decision.APPROVED,
        "Your request is approved.",
        trace,
    )

    assert decision == Decision.APPROVED
    assert reflection.startswith("Confirmed:")


def test_should_queue_review_when_escalated_without_flag():
    trace = [
        TraceStep(
            step=1,
            reason="Lookup",
            tool="get_employee_info",
            arguments={"employee_id": "E999"},
            observation={"found": False, "reason": "Employee not found."},
        )
    ]

    assert should_queue_review(Decision.ESCALATED, trace) is True


def test_should_not_queue_review_when_already_flagged():
    trace = [
        TraceStep(
            step=1,
            reason="Flag",
            tool="flag_for_human_review",
            arguments={"employee_id": "E999"},
            observation={"status": "queued"},
        )
    ]

    assert should_queue_review(Decision.ESCALATED, trace) is False
