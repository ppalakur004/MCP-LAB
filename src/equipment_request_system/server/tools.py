from __future__ import annotations

from mcp.server import MCPServer

from equipment_request_system.domain import services


def register_tools(mcp: MCPServer) -> None:
    @mcp.tool(name="get_employee_info")
    def employee_info(employee_id: str) -> dict[str, object]:
        """Return an employee's role, tenure, and active equipment."""
        return services.get_employee_info(employee_id)

    @mcp.tool(name="get_policy_limits")
    def policy_limits(role: str) -> dict[str, object]:
        """Return the equipment limits and refresh periods for a role."""
        return services.get_policy_limits(role)

    @mcp.tool(name="check_request_eligibility")
    def request_eligibility(employee_id: str, item: str) -> dict[str, object]:
        """Return whether a standard equipment request is approved, denied, or ambiguous."""
        return services.check_request_eligibility(employee_id, item)

    @mcp.tool(name="flag_for_human_review")
    def human_review(
        employee_id: str,
        request: str,
        reason: str,
        request_id: str,
    ) -> dict[str, object]:
        """Queue an ambiguous or exceptional request for human review.

        Reusing request_id is safe and returns the existing review instead of duplicating it.
        """
        return services.flag_for_human_review(employee_id, request, reason, request_id)
