from __future__ import annotations

import operator
from typing import Annotated, Any, Literal

from typing_extensions import TypedDict


class FinancialAnalysisState(TypedDict):
    # ---- Input ----
    query: str
    context: dict[str, Any]

    # ---- Routing ----
    active_teams: list[str]  # teams to invoke, set by orchestrator or caller

    # ---- Outputs — reducers make parallel team writes safe ----
    agent_outputs: Annotated[list[dict], operator.add]
    completed_teams: Annotated[list[str], operator.add]

    # ---- Compliance ----
    compliance_result: dict | None  # populated by verification_compliance team

    # ---- Human review ----
    human_decision: Literal["approved", "rejected", "pending"]
    revision_notes: str

    # ---- Document / final ----
    report: dict | None       # structured report from document_producer
    final_output: str         # human-readable answer from synthesizer

    # ---- Metadata ----
    request_id: str
    errors: Annotated[list[str], operator.add]
