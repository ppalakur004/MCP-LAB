# Architecture

```text
CLI -> ReAct agent -> MCP client -> MCP server -> tool wrapper -> domain service -> JSON data
                              result returns <-                 <-
```

- `cli.py` accepts a request and displays the result.
- `agent/react_agent.py` runs the bounded model/tool loop and records an operational trace.
- Local `qwen3:8b` runs through Ollama's OpenAI-compatible Responses endpoint with thinking off.
- `agent/client.py` discovers and calls tools over MCP stdio.
- `server/app.py` creates the MCP server.
- `server/tools.py` exposes four thin tool wrappers.
- `domain/services.py` owns the testable business rules and JSON access.
- `agent/reflection.py` compares the draft decision with recorded tool observations.

The scratchpad is the in-memory list of `TraceStep` records in `react_agent.py`. A trace contains the
tool selected, arguments, structured observation, and a concise operational reason. It does not
store hidden model reasoning.
