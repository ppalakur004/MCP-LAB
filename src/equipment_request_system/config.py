from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    data_dir: Path = PROJECT_ROOT / "data"
    ollama_base_url: str = os.getenv(
        "OLLAMA_BASE_URL", "http://host.docker.internal:11434/v1"
    )
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen3:8b")
    ollama_api_key: str = os.getenv("OLLAMA_API_KEY", "ollama")
    agent_max_steps: int = int(os.getenv("AGENT_MAX_STEPS", "8"))
    model_max_retries: int = int(os.getenv("MODEL_MAX_RETRIES", "3"))
    mcp_max_retries: int = int(os.getenv("MCP_MAX_RETRIES", "3"))
    mcp_call_timeout_seconds: float = float(os.getenv("MCP_CALL_TIMEOUT_SECONDS", "20"))

    @property
    def employees_path(self) -> Path:
        return self.data_dir / "employees.json"

    @property
    def policies_path(self) -> Path:
        return self.data_dir / "policies.json"

    @property
    def review_queue_path(self) -> Path:
        return self.data_dir / "review_queue.json"


settings = Settings()
