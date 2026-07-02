from app.graph.graph import build_graph
from app.graph.teams.analysis import AGENT_REGISTRY


def test_graph_compiles():
    """Graph must compile without errors."""
    graph = build_graph()
    assert graph is not None


def test_graph_has_expected_nodes():
    graph = build_graph()
    assert "router" in graph.nodes
    assert "supervisor" in graph.nodes
    assert "document_producer" in graph.nodes
    assert "synthesizer" in graph.nodes


def test_graph_includes_all_registry_agents():
    graph = build_graph()
    for name in AGENT_REGISTRY:
        assert name in graph.nodes, f"Agent '{name}' missing from compiled graph"
