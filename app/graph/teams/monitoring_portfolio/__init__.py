from __future__ import annotations

import asyncio

import structlog

from app.graph.state import FinancialAnalysisState
from app.graph.teams.monitoring_portfolio.alerts import AlertsAgent
from app.graph.teams.monitoring_portfolio.crm_pipeline_syncer import CRMPipelineSyncerAgent
from app.graph.teams.monitoring_portfolio.holdings_monitor import HoldingsMonitorAgent
from app.graph.teams.monitoring_portfolio.periodic_reports import PeriodicReportsAgent

log = structlog.get_logger()

_agents = [HoldingsMonitorAgent(), AlertsAgent(), PeriodicReportsAgent(), CRMPipelineSyncerAgent()]

TEAM_NAME = "monitoring_portfolio"


async def run(state: FinancialAnalysisState) -> dict:
    """Invoked by the /monitor endpoint, not the main analysis graph."""
    log.info(f"{TEAM_NAME}.run", query=state["query"][:80])
    results = await asyncio.gather(*[agent(state) for agent in _agents], return_exceptions=True)

    outputs, errors = [], []
    for r in results:
        if isinstance(r, Exception):
            errors.append(f"{TEAM_NAME}: {r}")
        else:
            outputs.extend(r.get("agent_outputs", []))

    return {"agent_outputs": outputs, "completed_teams": [TEAM_NAME], "errors": errors}
