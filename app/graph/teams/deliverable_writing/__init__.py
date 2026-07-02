from __future__ import annotations

import asyncio

import structlog

from app.graph.state import FinancialAnalysisState
from app.graph.teams.deliverable_writing.ic_credit_memos import ICCreditMemosAgent
from app.graph.teams.deliverable_writing.pitch_decks import PitchDecksAgent
from app.graph.teams.deliverable_writing.research_notes import ResearchNotesAgent
from app.graph.teams.deliverable_writing.sponsor_outreach import SponsorOutreachAgent

log = structlog.get_logger()

_agents = [ICCreditMemosAgent(), ResearchNotesAgent(), PitchDecksAgent(), SponsorOutreachAgent()]

TEAM_NAME = "deliverable_writing"


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
