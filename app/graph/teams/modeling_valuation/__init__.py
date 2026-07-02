from __future__ import annotations

import asyncio

import structlog

from app.graph.state import FinancialAnalysisState
from app.graph.teams.modeling_valuation.blended_valuation import BlendedValuationAgent
from app.graph.teams.modeling_valuation.credit_fixed_income import CreditFixedIncomeAgent
from app.graph.teams.modeling_valuation.dcf import DCFAgent
from app.graph.teams.modeling_valuation.lbo import LBOAgent

log = structlog.get_logger()

TEAM_NAME = "modeling_valuation"


async def run(state: FinancialAnalysisState) -> dict:
    """Two-phase execution:
    Phase A — DCF, LBO, Credit run in parallel.
    Phase B — Blended Valuation synthesizes Phase A outputs (runs sequentially after).
    """
    log.info(f"{TEAM_NAME}.run", query=state["query"][:80])

    # Phase A: independent models run in parallel
    phase_a_results = await asyncio.gather(
        DCFAgent()(state), LBOAgent()(state), CreditFixedIncomeAgent()(state),
        return_exceptions=True,
    )

    phase_a_outputs, errors = [], []
    for r in phase_a_results:
        if isinstance(r, Exception):
            errors.append(f"{TEAM_NAME}.phase_a: {r}")
        else:
            phase_a_outputs.extend(r.get("agent_outputs", []))

    # Phase B: blended valuation reads Phase A outputs via enriched context
    valuation_inputs = "\n\n".join(
        f"**{o['agent_name'].upper()}**:\n{o['analysis']}"
        for o in phase_a_outputs
        if not o.get("error")
    )
    blended_state = {
        **state,
        "context": {**state.get("context", {}), "valuation_inputs": valuation_inputs},
    }
    try:
        blended_result = await BlendedValuationAgent()(blended_state)
        phase_b_outputs = blended_result.get("agent_outputs", [])
    except Exception as exc:
        errors.append(f"{TEAM_NAME}.blended_valuation: {exc}")
        phase_b_outputs = []

    all_outputs = phase_a_outputs + phase_b_outputs
    return {"agent_outputs": all_outputs, "completed_teams": [TEAM_NAME], "errors": errors}
