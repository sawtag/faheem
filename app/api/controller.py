from __future__ import annotations

from uuid import uuid4

from app.api.schemas import AgentOutput, AnalyzeRequest, AnalyzeResponse
from app.graph.state import FinancialAnalysisState


async def analyze_controller(req: AnalyzeRequest, graph) -> AnalyzeResponse:
    initial_state: FinancialAnalysisState = {
        "query": req.query,
        "context": req.context,
        "route": "unknown",
        "active_agents": req.agents or [],
        "agent_outputs": [],
        "completed_agents": [],
        "supervisor_iterations": 0,
        "report": None,
        "final_output": "",
        "request_id": str(uuid4()),
        "errors": [],
    }

    result = await graph.ainvoke(initial_state)

    agent_results = [
        AgentOutput(**o) if isinstance(o, dict) else o
        for o in result.get("agent_outputs", [])
    ]

    report = result.get("report") or {}

    return AnalyzeResponse(
        request_id=result["request_id"],
        final_output=result.get("final_output", ""),
        agent_results=agent_results,
        report_sections=report.get("sections", {}),
        summary_bullets=report.get("summary_bullets", []),
        errors=result.get("errors", []),
    )
