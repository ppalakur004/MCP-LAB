# MCP Equipment Request Lab

Mock IT equipment request MCP server and ReAct agent.

The project now includes a working MCP server, MCP client, ReAct agent, mock data, tests, CLI,
demonstration script, bounded retries, and CI configuration.

## Setup

Open the repository in its development container, then create a local environment file:

```bash
cp .env.example .env
```

Install Ollama on the host and download the local Qwen model:

```bash
ollama pull qwen3:8b
```

The default development-container URL is `http://host.docker.internal:11434/v1`. If the Python
application runs directly on the host instead, set `OLLAMA_BASE_URL=http://localhost:11434/v1`.
Ollama's `think` option is disabled by the agent on every request.

Verify the MCP connection without calling the model:

```bash
python scripts/verify_connection.py
```

Run one request:

```bash
python -m equipment_request_system.cli \
  --employee-id E001 \
  --request "I need a second monitor"
```

Run the four rubric demonstrations and the tests:

```bash
python scripts/run_demo.py
pytest
```

## Project structure

```text
.
├── .devcontainer/
│   └── devcontainer.json
├── .github/
│   └── workflows/
│       └── ci.yml
├── artifacts/
│   ├── generated/
│   │   └── .gitkeep
│   └── screenshots/
│       └── .gitkeep
├── data/
│   ├── employees.json
│   ├── policies.json
│   └── review_queue.json
├── docs/
│   ├── architecture.md
│   ├── demo-plan.md
│   ├── requirements.md
│   └── submission-checklist.md
├── scripts/
│   ├── run_demo.py
│   └── verify_connection.py
├── src/
│   └── equipment_request_system/
│       ├── __init__.py
│       ├── agent/
│       │   ├── __init__.py
│       │   ├── client.py
│       │   ├── prompts.py
│       │   ├── react_agent.py
│       │   └── reflection.py
│       ├── cli.py
│       ├── config.py
│       ├── domain/
│       │   ├── __init__.py
│       │   ├── models.py
│       │   └── services.py
│       └── server/
│           ├── __init__.py
│           ├── app.py
│           └── tools.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── fixtures/
│   │   └── .gitkeep
│   ├── integration/
│   │   ├── __init__.py
│   │   └── test_mcp_connection.py
│   └── unit/
│       ├── __init__.py
│       ├── test_check_request_eligibility.py
│       ├── test_flag_for_human_review.py
│       ├── test_get_employee_info.py
│       ├── test_get_policy_limits.py
│       └── test_reflection.py
├── .env.example
├── .gitignore
├── LICENSE
├── pyproject.toml
├── requirements-dev.txt
└── requirements.txt
```
