from __future__ import annotations

import structlog
from langchain_core.messages import HumanMessage, SystemMessage

from app.api.schemas import RouterDecision
from app.core.llm import get_llm
from app.graph.state import FinancialAnalysisState
from app.prompts.router_prompts import ROUTER_SYSTEM_PROMPT

log = structlog.get_logger()


async def run(state: FinancialAnalysisState) -> dict:
    log.info("router.run", query=state["query"][:80])

    # If the caller explicitly provided agents, skip LLM routing
    if state["active_agents"]:
        log.info("router.explicit_agents", active_agents=state["active_agents"])
        return {"route": "analysis", "active_agents": state["active_agents"]}

    llm = get_llm().with_structured_output(RouterDecision)
    try:
        decision: RouterDecision = await llm.ainvoke([
            SystemMessage(content=ROUTER_SYSTEM_PROMPT),
            HumanMessage(content=state["query"]),
        ])
        log.info("router.decision", route=decision.route, agents=decision.active_agents)
        return {
            "route": decision.route,
            "active_agents": decision.active_agents,
        }
    except Exception as exc:
        log.error("router.error", error=str(exc))
        return {
            "route": "unknown",
            "active_agents": [],
            "errors": [f"Router failed: {exc}"],
        }
