from __future__ import annotations

import json

import anyio

from equipment_request_system.agent.client import EquipmentMCPClient
from equipment_request_system.agent.react_agent import run_agent

DEMO_REQUESTS = [
    ("approved", "E001", "I need a second monitor."),
    ("denied", "E002", "My current laptop is slow. Can I replace it?"),
    ("escalated_unknown_employee", "E999", "I need a monitor."),
    ("escalated_specialized_item", "E001", "I need a color-calibrated medical-grade monitor."),
]


async def main() -> None:
    async with EquipmentMCPClient() as client:
        for scenario, employee_id, request in DEMO_REQUESTS:
            result = await run_agent(employee_id, request, mcp_client=client)
            print(f"\n=== {scenario} ===")
            print(json.dumps(result.model_dump(mode="json"), indent=2))


if __name__ == "__main__":
    anyio.run(main)
