from __future__ import annotations

import structlog

from app.core.config import get_settings
from app.graph.state import FinancialAnalysisState

log = structlog.get_logger()


async def run(state: FinancialAnalysisState) -> dict:
    iterations = state["supervisor_iterations"] + 1
    settings = get_settings()

    # Derive completed agents from whoever has written to agent_outputs
    reported = {o["agent_name"] for o in state.get("agent_outputs", [])}
    completed = list(reported)

    log.info(
        "supervisor.run",
        iterations=iterations,
        completed=completed,
        active=state["active_agents"],
    )

    if iterations > settings.MAX_SUPERVISOR_ITERATIONS:
        log.warning("supervisor.max_iterations", limit=settings.MAX_SUPERVISOR_ITERATIONS)
        return {
            "completed_agents": state["active_agents"],  # force completion
            "supervisor_iterations": iterations,
            "errors": [f"Supervisor hit max iterations ({settings.MAX_SUPERVISOR_ITERATIONS})"],
        }

    return {
        "completed_agents": completed,
        "supervisor_iterations": iterations,
    }
