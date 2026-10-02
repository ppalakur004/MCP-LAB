from __future__ import annotations

import json
import re
import uuid
from typing import Any

import anyio
from openai import AsyncOpenAI

from equipment_request_system.agent.client import EquipmentMCPClient
from equipment_request_system.agent.prompts import SYSTEM_PROMPT, build_request_prompt
from equipment_request_system.agent.reflection import reflect_draft
from equipment_request_system.config import settings
from equipment_request_system.domain.models import AgentResult, Decision, TraceStep

FINAL_PATTERN = re.compile(
    r"DECISION:\s*(approved|denied|escalated)\s*\nRESPONSE:\s*(.+)",
    re.IGNORECASE | re.DOTALL,
)


class AgentRunError(RuntimeError):
    pass


def _openai_tools(mcp_tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["input_schema"],
            "strict": False,
        }
        for tool in mcp_tools
    ]


async def _create_response_with_retry(client: AsyncOpenAI, **kwargs: Any) -> Any:
    last_error: Exception | None = None
    for attempt in range(1, settings.model_max_retries + 1):
        try:
            return await client.responses.create(**kwargs)
        except Exception as exc:
            last_error = exc
            if attempt == settings.model_max_retries:
                break
            await anyio.sleep(0.5 * (2 ** (attempt - 1)))
    raise AgentRunError("The model request failed after the configured retries") from last_error


def _parse_final(text: str) -> tuple[Decision, str]:
    match = FINAL_PATTERN.search(text.strip())
    if not match:
        raise AgentRunError("The model did not return the required final format")
    return Decision(match.group(1).lower()), match.group(2).strip()


async def run_agent(
    employee_id: str,
    request: str,
    *,
    mcp_client: EquipmentMCPClient,
    openai_client: AsyncOpenAI | None = None,
) -> AgentResult:
    model_client = openai_client or AsyncOpenAI(
        base_url=settings.ollama_base_url,
        api_key=settings.ollama_api_key,
    )
    request_id = f"REQ-{uuid.uuid4().hex[:10].upper()}"
    available_tools = await mcp_client.list_tools()
    tools = _openai_tools(available_tools)
    trace: list[TraceStep] = []
    input_items: list[Any] = [
        {
            "role": "user",
            "content": build_request_prompt(employee_id, request, request_id),
        }
    ]

    response = await _create_response_with_retry(
        model_client,
        model=settings.ollama_model,
        instructions=SYSTEM_PROMPT,
        input=input_items,
        tools=tools,
        extra_body={"think": False},
    )

    for _step_number in range(1, settings.agent_max_steps + 1):
        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            decision, draft = _parse_final(response.output_text)
            decision, draft, reflection = reflect_draft(decision, draft, trace)
            return AgentResult(
                decision=decision,
                response=draft,
                trace=trace,
                reflection=reflection,
            )

        input_items.extend(item.model_dump(exclude_none=True) for item in response.output)
        outputs: list[dict[str, str]] = []
        for call in calls:
            arguments = json.loads(call.arguments)
            observation = await mcp_client.call_tool(call.name, arguments)
            trace.append(
                TraceStep(
                    step=len(trace) + 1,
                    reason=f"The agent selected {call.name} to gather or act on request evidence.",
                    tool=call.name,
                    arguments=arguments,
                    observation=observation,
                )
            )
            outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": json.dumps(observation),
                }
            )

        input_items.extend(outputs)
        response = await _create_response_with_retry(
            model_client,
            model=settings.ollama_model,
            instructions=SYSTEM_PROMPT,
            input=input_items,
            tools=tools,
            extra_body={"think": False},
        )

    escalation = await mcp_client.call_tool(
        "flag_for_human_review",
        {
            "employee_id": employee_id,
            "request": request,
            "reason": f"The agent exceeded its {settings.agent_max_steps}-step limit.",
            "request_id": request_id,
        },
    )
    trace.append(
        TraceStep(
            step=len(trace) + 1,
            reason="Safety limit reached; the request must be reviewed by a human.",
            tool="flag_for_human_review",
            arguments={"employee_id": employee_id, "request_id": request_id},
            observation=escalation,
        )
    )
    return AgentResult(
        decision=Decision.ESCALATED,
        response=(
            "Your request was sent for human review because the automated review reached "
            "its step limit."
        ),
        trace=trace,
        reflection="Confirmed: the step-limit fallback created a human-review record.",
    )
