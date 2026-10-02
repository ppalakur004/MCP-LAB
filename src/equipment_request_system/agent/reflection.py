from __future__ import annotations

from equipment_request_system.domain.models import Decision, TraceStep


def _last_observation(trace: list[TraceStep], tool: str) -> dict[str, object] | None:
    return next((step.observation for step in reversed(trace) if step.tool == tool), None)


def should_queue_review(decision: Decision, trace: list[TraceStep]) -> bool:
    if _last_observation(trace, "flag_for_human_review") is not None:
        return False
    if decision == Decision.ESCALATED:
        return True
    eligibility = _last_observation(trace, "check_request_eligibility")
    return bool(eligibility and eligibility.get("decision") == Decision.ESCALATED.value)


def reflect_draft(
    decision: Decision,
    response: str,
    trace: list[TraceStep],
) -> tuple[Decision, str, str]:
    eligibility = _last_observation(trace, "check_request_eligibility")
    review = _last_observation(trace, "flag_for_human_review")

    if eligibility and eligibility.get("decision") == Decision.ESCALATED.value and not review:
        corrected = (
            "This request needs human review because the available records do not support "
            "an automatic decision."
        )
        return Decision.ESCALATED, corrected, "Corrected: ambiguous result had not been escalated."

    if review and decision != Decision.ESCALATED:
        reason = review.get("review", {}).get("reason", "the request requires human review")
        corrected = f"Your request was sent for human review because {reason}"
        return (
            Decision.ESCALATED,
            corrected,
            "Corrected: a queued review cannot be presented as approved or denied.",
        )

    if eligibility:
        expected = Decision(str(eligibility["decision"]))
        if expected != decision and expected != Decision.ESCALATED:
            corrected = str(eligibility.get("reason", response))
            return (
                expected,
                corrected,
                "Corrected: draft decision did not match the eligibility tool.",
            )

    return decision, response.strip(), "Confirmed: the draft matches the recorded tool results."
