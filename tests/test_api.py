import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch

from app.api.routes import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.mark.asyncio
async def test_health(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_analyze_missing_query_returns_422(app):
    """FastAPI Pydantic validation: missing required 'query' field."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/analyze", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_analyze_response_shape(app):
    """End-to-end: response must match AnalyzeResponse schema."""
    mock_result = {
        "request_id": "test-uuid",
        "final_output": "Based on the analysis...",
        "agent_outputs": [
            {
                "agent_name": "market",
                "analysis": "Bullish trend.",
                "confidence": 0.85,
                "metadata": {},
                "error": None,
            }
        ],
        "report": {
            "sections": {"Market Analysis": "Bullish trend."},
            "summary_bullets": ["Strong uptrend"],
            "raw_agent_outputs": [],
        },
        "errors": [],
    }

    with patch("app.api.routes.build_graph") as mock_build:
        mock_graph = MagicMock()
        mock_graph.ainvoke = AsyncMock(return_value=mock_result)
        mock_build.return_value = mock_graph

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/analyze",
                json={"query": "Analyze AAPL", "context": {}, "agents": ["market"]},
            )

    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    assert "final_output" in data
    assert "agent_results" in data
    assert "report_sections" in data
    assert "summary_bullets" in data
    assert "errors" in data
