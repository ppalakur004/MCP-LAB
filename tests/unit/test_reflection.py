from equipment_request_system.agent.reflection import reflect_draft
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
