from __future__ import annotations

import operator
from typing import Annotated, Any, Literal

from typing_extensions import TypedDict


class FinancialAnalysisState(TypedDict):
    # ---- Input ----
    query: str
    context: dict[str, Any]

    # ---- Routing ----
    route: Literal["analysis", "simple_query", "unknown"]
    active_agents: list[str]  # agents to invoke, set by router or caller

    # ---- Agent outputs — reducer makes parallel Send writes safe ----
    agent_outputs: Annotated[list[dict], operator.add]

    # ---- Supervisor bookkeeping ----
    completed_agents: list[str]
    supervisor_iterations: int

    # ---- Document / final ----
    report: dict | None  # structured report from document_producer
    final_output: str  # human-readable answer from synthesizer

    # ---- Metadata ----
    request_id: str
    errors: Annotated[list[str], operator.add]
