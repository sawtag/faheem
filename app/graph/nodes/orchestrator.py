from __future__ import annotations

import structlog
from langchain_core.messages import HumanMessage, SystemMessage

from app.api.schemas import OrchestratorDecision
from app.core.llm import get_llm
from app.graph.state import FinancialAnalysisState
from app.prompts.orchestrator_prompts import ORCHESTRATOR_SYSTEM_PROMPT

log = structlog.get_logger()


async def run(state: FinancialAnalysisState) -> dict:
    log.info("orchestrator.run", query=state["query"][:80])

    # If teams were explicitly provided by the caller, skip LLM routing
    if state["active_teams"]:
        log.info("orchestrator.explicit_teams", teams=state["active_teams"])
        return {"active_teams": state["active_teams"]}

    # On re-route after rejection, prepend revision context
    query = state["query"]
    if state.get("revision_notes"):
        query = f"[REVISION REQUESTED: {state['revision_notes']}]\n\n{query}"

    llm = get_llm().with_structured_output(OrchestratorDecision)
    try:
        decision: OrchestratorDecision = await llm.ainvoke([
            SystemMessage(content=ORCHESTRATOR_SYSTEM_PROMPT),
            HumanMessage(content=query),
        ])
        log.info("orchestrator.decision", teams=decision.active_teams)
        return {
            "active_teams": decision.active_teams,
            "completed_teams": [],  # reset on re-route
        }
    except Exception as exc:
        log.error("orchestrator.error", error=str(exc))
        return {
            "active_teams": ["researching_sourcing", "document_intelligence"],
            "errors": [f"Orchestrator failed, defaulting to research teams: {exc}"],
        }
