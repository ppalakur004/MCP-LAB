# MCP Equipment Request Lab

Starter project structure for the mock IT equipment request MCP server and ReAct agent.

Application code has intentionally not been implemented yet.

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
│       └── test_get_policy_limits.py
├── .env.example
├── .gitignore
├── LICENSE
├── pyproject.toml
├── requirements-dev.txt
└── requirements.txt
```
