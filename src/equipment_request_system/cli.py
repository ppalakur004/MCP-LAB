from __future__ import annotations

import argparse
import json

import anyio

from equipment_request_system.agent.client import EquipmentMCPClient
from equipment_request_system.agent.react_agent import run_agent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Process an IT equipment request.")
    parser.add_argument("--employee-id", required=True)
    parser.add_argument("--request", required=True)
    return parser


async def _run(employee_id: str, request: str) -> None:
    async with EquipmentMCPClient() as client:
        result = await run_agent(employee_id, request, mcp_client=client)
    print(json.dumps(result.model_dump(mode="json"), indent=2))


def main() -> None:
    arguments = build_parser().parse_args()
    anyio.run(_run, arguments.employee_id, arguments.request)


if __name__ == "__main__":
    main()
