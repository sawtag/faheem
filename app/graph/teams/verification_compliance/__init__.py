from __future__ import annotations

import asyncio

import structlog

from app.graph.state import FinancialAnalysisState
from app.graph.teams.verification_compliance.confidence_flags import ConfidenceFlagsAgent
from app.graph.teams.verification_compliance.fact_check_visual import FactCheckVisualAgent
from app.graph.teams.verification_compliance.sanctions_conflicts import SanctionsConflictsAgent
from app.graph.teams.verification_compliance.shariah_screening import ShariahScreeningAgent

log = structlog.get_logger()

_agents = [
    ShariahScreeningAgent(),
    FactCheckVisualAgent(),
    SanctionsConflictsAgent(),
    ConfidenceFlagsAgent(),
]

TEAM_NAME = "verification_compliance"


async def run(state: FinancialAnalysisState) -> dict:
    """Mandatory post-processing. All 4 checks run in parallel."""
    log.info(f"{TEAM_NAME}.run", n_outputs_to_check=len(state.get("agent_outputs", [])))
    results = await asyncio.gather(*[agent(state) for agent in _agents], return_exceptions=True)

    outputs, errors = [], []
    for r in results:
        if isinstance(r, Exception):
            errors.append(f"{TEAM_NAME}: {r}")
        else:
            outputs.extend(r.get("agent_outputs", []))

    compliance_result = {
        "checks": {o["agent_name"]: o["analysis"] for o in outputs if not o.get("error")},
        "passed": not any(o.get("error") for o in outputs),
        "failed_checks": [o["agent_name"] for o in outputs if o.get("error")],
    }

    return {
        "agent_outputs": outputs,
        "completed_teams": [TEAM_NAME],
        "compliance_result": compliance_result,
        "errors": errors,
    }
