import pytest
from mcp import Client

from equipment_request_system.server.app import mcp


@pytest.mark.integration
@pytest.mark.anyio
async def test_client_lists_and_calls_employee_tool():
    async with Client(mcp) as client:
        listed = await client.list_tools()
        names = {tool.name for tool in listed.tools}
        result = await client.call_tool("get_employee_info", {"employee_id": "E001"})

    assert {
        "get_employee_info",
        "get_policy_limits",
        "check_request_eligibility",
        "flag_for_human_review",
    } <= names
    assert result.is_error is False
    assert result.structured_content["found"] is True
