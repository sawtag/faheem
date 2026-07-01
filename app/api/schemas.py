from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class AgentOutput(BaseModel):
    agent_name: str
    analysis: str
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class RouterDecision(BaseModel):
    """LLM structured output schema for the router node."""

    route: Literal["analysis", "simple_query", "unknown"]
    active_agents: list[str]
    reasoning: str


class ReportSchema(BaseModel):
    """LLM structured output schema for the document_producer node."""

    sections: dict[str, str]
    summary_bullets: list[str]


class AnalyzeRequest(BaseModel):
    query: str
    context: dict[str, Any] = Field(default_factory=dict)
    agents: list[str] | None = Field(
        default=None,
        description="Optional: force specific agents (e.g. ['market', 'risk']). "
        "If omitted, the router decides.",
    )


class AnalyzeResponse(BaseModel):
    request_id: str
    final_output: str
    agent_results: list[AgentOutput]
    report_sections: dict[str, str]
    summary_bullets: list[str]
    errors: list[str]
