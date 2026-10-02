from __future__ import annotations

import json

import anyio

from equipment_request_system.agent.client import EquipmentMCPClient


async def verify() -> None:
    async with EquipmentMCPClient() as client:
        tools = await client.list_tools()
        result = await client.call_tool("get_employee_info", {"employee_id": "E001"})
    print("Registered tools:", ", ".join(tool["name"] for tool in tools))
    print("get_employee_info response:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    anyio.run(verify)
