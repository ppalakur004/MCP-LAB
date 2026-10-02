from __future__ import annotations

import sys
from types import TracebackType
from typing import Any

import anyio
from mcp import Client, StdioServerParameters

from equipment_request_system.config import PROJECT_ROOT, settings

READ_ONLY_TOOLS = {
    "get_employee_info",
    "get_policy_limits",
    "check_request_eligibility",
}


class MCPToolCallError(RuntimeError):
    pass


class EquipmentMCPClient:
    def __init__(self, target: Any | None = None) -> None:
        if target is None:
            source_path = str(PROJECT_ROOT / "src")
            target = StdioServerParameters(
                command=sys.executable,
                args=["-m", "equipment_request_system.server.app"],
                env={"PYTHONPATH": source_path},
            )
        self._client = Client(target)

    async def __aenter__(self) -> EquipmentMCPClient:
        await self._client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        return await self._client.__aexit__(exc_type, exc, traceback)

    async def list_tools(self) -> list[dict[str, Any]]:
        result = await self._client.list_tools()
        return [
            {
                "name": tool.name,
                "description": tool.description or "",
                "input_schema": tool.input_schema,
            }
            for tool in result.tools
        ]

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        attempts = settings.mcp_max_retries if name in READ_ONLY_TOOLS else 1
        last_error: Exception | None = None
        for attempt in range(1, attempts + 1):
            try:
                with anyio.fail_after(settings.mcp_call_timeout_seconds):
                    result = await self._client.call_tool(name, arguments)
                if result.is_error:
                    message = " ".join(
                        getattr(block, "text", "") for block in result.content
                    ).strip()
                    raise MCPToolCallError(message or f"Tool {name} failed")
                if result.structured_content is not None:
                    return dict(result.structured_content)
                raise MCPToolCallError(f"Tool {name} returned no structured content")
            except Exception as exc:
                last_error = exc
                if attempt == attempts:
                    break
                await anyio.sleep(0.25 * (2 ** (attempt - 1)))
        raise MCPToolCallError(f"Tool {name} failed after {attempts} attempt(s)") from last_error
