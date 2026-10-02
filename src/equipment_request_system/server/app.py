from mcp.server import MCPServer

from equipment_request_system.server.tools import register_tools

mcp = MCPServer(
    "IT Equipment Request System",
    instructions=(
        "Use these tools to inspect employee equipment and policy. "
        "Escalate missing, uncovered, or exceptional requests rather than guessing."
    ),
)
register_tools(mcp)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
