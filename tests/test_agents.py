import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.graph.teams.analysis.market_agent import MarketAgent
from app.graph.teams.analysis.risk_agent import RiskAgent


def _make_state(**overrides):
    base = {
        "query": "What is the outlook for AAPL?",
        "context": {},
        "route": "analysis",
        "active_agents": ["market"],
        "agent_outputs": [],
        "completed_agents": [],
        "supervisor_iterations": 0,
        "report": None,
        "final_output": "",
        "request_id": "test-123",
        "errors": [],
    }
    return {**base, **overrides}


@pytest.mark.asyncio
async def test_agent_returns_correct_shape():
    """Agent __call__ must return dict with agent_outputs list."""
    agent = MarketAgent()
    state = _make_state()

    mock_response = MagicMock()
    mock_response.content = "Market looks bullish."

    with patch("app.graph.teams.analysis.market_agent.get_llm") as mock_get_llm:
        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        mock_get_llm.return_value = mock_llm

        result = await agent(state)

    assert "agent_outputs" in result
    assert len(result["agent_outputs"]) == 1
    output = result["agent_outputs"][0]
    assert output["agent_name"] == "market"
    assert output["analysis"] == "Market looks bullish."
    assert output["error"] is None


@pytest.mark.asyncio
async def test_agent_catches_llm_error():
    """A failing LLM call must not crash the graph — error is captured in output."""
    agent = RiskAgent()
    state = _make_state(active_agents=["risk"])

    with patch("app.graph.teams.analysis.risk_agent.get_llm") as mock_get_llm:
        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(side_effect=Exception("LLM timeout"))
        mock_get_llm.return_value = mock_llm

        result = await agent(state)

    output = result["agent_outputs"][0]
    assert output["agent_name"] == "risk"
    assert output["error"] == "LLM timeout"
    assert output["confidence"] == 0.0
