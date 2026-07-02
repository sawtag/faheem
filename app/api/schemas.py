from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AgentOutput(BaseModel):
    agent_name: str
    analysis: str
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class OrchestratorDecision(BaseModel):
    """LLM structured output schema for the orchestrator node."""

    active_teams: list[str]
    reasoning: str


class ReportSchema(BaseModel):
    """LLM structured output schema for the document_producer node."""

    sections: dict[str, str]
    summary_bullets: list[str]


class AnalyzeRequest(BaseModel):
    query: str
    context: dict[str, Any] = Field(default_factory=dict)
    teams: list[str] | None = Field(
        default=None,
        description="Optional: force specific teams (e.g. ['researching_sourcing', 'modeling_valuation']). "
        "If omitted, the orchestrator decides.",
    )


class AnalyzeResponse(BaseModel):
    request_id: str
    final_output: str
    agent_results: list[AgentOutput]
    report_sections: dict[str, str]
    summary_bullets: list[str]
    compliance_result: dict[str, Any] | None
    human_decision: str
    errors: list[str]


class MonitorRequest(BaseModel):
    query: str
    context: dict[str, Any] = Field(default_factory=dict)


class MonitorResponse(BaseModel):
    request_id: str
    agent_results: list[AgentOutput]
    errors: list[str]
