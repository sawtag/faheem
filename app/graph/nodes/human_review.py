from __future__ import annotations

import structlog

from app.graph.state import FinancialAnalysisState

log = structlog.get_logger()

# To enable real human-in-the-loop interrupts, uncomment the import below
# and replace the auto-approve logic with: decision = interrupt({...})
# The caller then resumes via graph.ainvoke(Command(resume={"decision": "approved"}))
# Requires a checkpointer: builder.compile(checkpointer=MemorySaver())
#
# from langgraph.types import interrupt


async def run(state: FinancialAnalysisState) -> dict:
    """Human review checkpoint.

    Current behaviour: auto-approves unless the caller set
    context["human_decision"] = "rejected" (useful for testing the re-route path).

    Production upgrade: replace with langgraph.types.interrupt() + MemorySaver checkpointer
    to pause the graph and wait for a real human decision via the /resume endpoint.
    """
    log.info(
        "human_review.checkpoint",
        n_outputs=len(state.get("agent_outputs", [])),
        compliance_passed=state.get("compliance_result", {}).get("passed"),
    )

    # Allow caller to inject a decision override via context (for testing)
    override = state.get("context", {}).get("human_decision")
    if override in ("approved", "rejected"):
        return {
            "human_decision": override,
            "revision_notes": state.get("context", {}).get("revision_notes", ""),
        }

    # Default: auto-approve
    return {"human_decision": "approved", "revision_notes": ""}
