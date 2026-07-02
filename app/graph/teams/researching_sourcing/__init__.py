from __future__ import annotations

import asyncio

import structlog

from app.graph.state import FinancialAnalysisState
from app.graph.teams.researching_sourcing.market_data_news import MarketDataNewsAgent
from app.graph.teams.researching_sourcing.screen_universe import ScreenUniverseAgent
from app.graph.teams.researching_sourcing.transcript_earnings_parser import TranscriptEarningsParserAgent

log = structlog.get_logger()

_agents = [ScreenUniverseAgent(), MarketDataNewsAgent(), TranscriptEarningsParserAgent()]

TEAM_NAME = "researching_sourcing"


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
