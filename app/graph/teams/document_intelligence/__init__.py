from __future__ import annotations

import structlog

from app.graph.state import FinancialAnalysisState
from app.graph.teams.document_intelligence.document_extractor import DocumentExtractorAgent

log = structlog.get_logger()

_agent = DocumentExtractorAgent()

TEAM_NAME = "document_intelligence"


async def run(state: FinancialAnalysisState) -> dict:
    log.info(f"{TEAM_NAME}.run", query=state["query"][:80])
    try:
        result = await _agent(state)
        return {"agent_outputs": result.get("agent_outputs", []), "completed_teams": [TEAM_NAME]}
    except Exception as exc:
        return {
            "agent_outputs": [],
            "completed_teams": [TEAM_NAME],
            "errors": [f"{TEAM_NAME}: {exc}"],
        }
