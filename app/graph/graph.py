from __future__ import annotations

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from app.graph.nodes import document_producer, router, supervisor, synthesizer
from app.graph.state import FinancialAnalysisState
from app.graph.teams.analysis import AGENT_REGISTRY


def _route_decision(state: FinancialAnalysisState) -> str:
    return state["route"]


def _supervisor_dispatch(state: FinancialAnalysisState) -> list[Send] | str:
    """Fan out to pending agents via Send, or advance to document_producer when all done."""
    pending = set(state["active_agents"]) - set(state["completed_agents"])
    if pending:
        return [Send(name, state) for name in pending]
    return "document_producer"


def build_graph():
    builder = StateGraph(FinancialAnalysisState)

    # Core nodes
    builder.add_node("router", router.run)
    builder.add_node("supervisor", supervisor.run)
    builder.add_node("document_producer", document_producer.run)
    builder.add_node("synthesizer", synthesizer.run)

    # Register all analysis agents dynamically from the registry
    for name, agent in AGENT_REGISTRY.items():
        builder.add_node(name, agent)

    # Entry point
    builder.add_edge(START, "router")

    # Router → full analysis pipeline OR fast-path to synthesizer
    builder.add_conditional_edges(
        "router",
        _route_decision,
        {
            "analysis": "supervisor",
            "simple_query": "synthesizer",
            "unknown": "synthesizer",
        },
    )

    # Supervisor: fan-out to pending agents (via Send) or advance to document_producer
    all_targets = ["document_producer"] + list(AGENT_REGISTRY.keys())
    builder.add_conditional_edges("supervisor", _supervisor_dispatch, all_targets)

    # All agents fan back to supervisor
    for name in AGENT_REGISTRY:
        builder.add_edge(name, "supervisor")

    builder.add_edge("document_producer", "synthesizer")
    builder.add_edge("synthesizer", END)

    return builder.compile()
