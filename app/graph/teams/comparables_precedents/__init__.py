from __future__ import annotations

import asyncio

import structlog

from app.graph.state import FinancialAnalysisState
from app.graph.teams.comparables_precedents.multiple_normalizer import MultipleNormalizerAgent
from app.graph.teams.comparables_precedents.precedent_transactions import PrecedentTransactionsAgent
from app.graph.teams.comparables_precedents.trading_comps import TradingCompsAgent

log = structlog.get_logger()

_agents = [TradingCompsAgent(), PrecedentTransactionsAgent(), MultipleNormalizerAgent()]

TEAM_NAME = "comparables_precedents"


async def run(state: FinancialAnalysisState) -> dict:
    log.info(f"{TEAM_NAME}.run", query=state["query"][:80])
    results = await asyncio.gather(*[agent(state) for agent in _agents], return_exceptions=True)

    outputs, errors = [], []
    for r in results:
        if isinstance(r, Exception):
            errors.append(f"{TEAM_NAME}: {r}")
        else:
            outputs.extend(r.get("agent_outputs", []))

    return {"agent_outputs": outputs, "completed_teams": [TEAM_NAME], "errors": errors}
