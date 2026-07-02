from __future__ import annotations

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from app.graph.nodes import document_producer, human_review, orchestrator, synthesizer
from app.graph.state import FinancialAnalysisState
from app.graph.teams import (
    comparables_precedents,
    deliverable_writing,
    document_intelligence,
    modeling_valuation,
    researching_sourcing,
    verification_compliance,
)

# Phase definitions — drives which teams run in which phase
PHASE_1_TEAMS = {"researching_sourcing", "document_intelligence"}
PHASE_2_TEAMS = {"modeling_valuation", "comparables_precedents"}


# --- Conditional edge functions ---

def _phase_1_dispatch(state: FinancialAnalysisState) -> list[Send] | str:
    """Fan out to Phase 1 teams in parallel, or skip to Phase 2 if none needed."""
    needed = PHASE_1_TEAMS & set(state["active_teams"])
    if needed:
        return [Send(team, state) for team in needed]
    return "phase_2_transition"


def _phase_2_dispatch(state: FinancialAnalysisState) -> list[Send] | str:
    """Fan out to Phase 2 teams in parallel, or skip to writing if none needed."""
    needed = PHASE_2_TEAMS & set(state["active_teams"])
    if needed:
        return [Send(team, state) for team in needed]
    return "deliverable_writing"


def _human_review_routing(state: FinancialAnalysisState) -> str:
    if state.get("human_decision") == "rejected":
        return "orchestrator"
    return "document_producer"


# --- No-op join node ---

async def _phase_2_transition(state: FinancialAnalysisState) -> dict:
    """Join point: receives combined Phase 1 outputs, triggers Phase 2 dispatch."""
    return {}


def build_graph():
    builder = StateGraph(FinancialAnalysisState)

    # Core nodes
    builder.add_node("orchestrator", orchestrator.run)
    builder.add_node("phase_2_transition", _phase_2_transition)
    builder.add_node("document_producer", document_producer.run)
    builder.add_node("synthesizer", synthesizer.run)
    builder.add_node("human_review", human_review.run)

    # Team nodes
    builder.add_node("researching_sourcing", researching_sourcing.run)
    builder.add_node("document_intelligence", document_intelligence.run)
    builder.add_node("modeling_valuation", modeling_valuation.run)
    builder.add_node("comparables_precedents", comparables_precedents.run)
    builder.add_node("deliverable_writing", deliverable_writing.run)
    builder.add_node("verification_compliance", verification_compliance.run)

    # Entry
    builder.add_edge(START, "orchestrator")

    # Phase 1: orchestrator → [researching_sourcing, document_intelligence] in parallel
    builder.add_conditional_edges(
        "orchestrator",
        _phase_1_dispatch,
        ["researching_sourcing", "document_intelligence", "phase_2_transition"],
    )

    # Phase 1 fan-in → phase_2_transition
    builder.add_edge("researching_sourcing", "phase_2_transition")
    builder.add_edge("document_intelligence", "phase_2_transition")

    # Phase 2: phase_2_transition → [modeling_valuation, comparables_precedents] in parallel
    builder.add_conditional_edges(
        "phase_2_transition",
        _phase_2_dispatch,
        ["modeling_valuation", "comparables_precedents", "deliverable_writing"],
    )

    # Phase 2 fan-in → deliverable_writing
    builder.add_edge("modeling_valuation", "deliverable_writing")
    builder.add_edge("comparables_precedents", "deliverable_writing")

    # Phase 3: writing → compliance (mandatory) → human review
    builder.add_edge("deliverable_writing", "verification_compliance")
    builder.add_edge("verification_compliance", "human_review")

    # Human review: approved → document_producer; rejected → re-route to orchestrator
    builder.add_conditional_edges(
        "human_review",
        _human_review_routing,
        {"document_producer": "document_producer", "orchestrator": "orchestrator"},
    )

    builder.add_edge("document_producer", "synthesizer")
    builder.add_edge("synthesizer", END)

    return builder.compile()
