from __future__ import annotations

from uuid import uuid4

from app.api.schemas import AgentOutput, AnalyzeRequest, AnalyzeResponse, MonitorRequest, MonitorResponse
from app.graph.state import FinancialAnalysisState


async def analyze_controller(req: AnalyzeRequest, graph) -> AnalyzeResponse:
    initial_state: FinancialAnalysisState = {
        "query": req.query,
        "context": req.context,
        "active_teams": req.teams or [],
        "agent_outputs": [],
        "completed_teams": [],
        "compliance_result": None,
        "human_decision": "pending",
        "revision_notes": "",
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
        compliance_result=result.get("compliance_result"),
        human_decision=result.get("human_decision", "pending"),
        errors=result.get("errors", []),
    )


async def monitor_controller(req: MonitorRequest, monitor_graph) -> MonitorResponse:
    initial_state: FinancialAnalysisState = {
        "query": req.query,
        "context": req.context,
        "active_teams": ["monitoring_portfolio"],
        "agent_outputs": [],
        "completed_teams": [],
        "compliance_result": None,
        "human_decision": "pending",
        "revision_notes": "",
        "report": None,
        "final_output": "",
        "request_id": str(uuid4()),
        "errors": [],
    }

    result = await monitor_graph.ainvoke(initial_state)

    agent_results = [
        AgentOutput(**o) if isinstance(o, dict) else o
        for o in result.get("agent_outputs", [])
    ]

    return MonitorResponse(
        request_id=result["request_id"],
        agent_results=agent_results,
        errors=result.get("errors", []),
    )
