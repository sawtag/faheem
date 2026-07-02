# AGENT_REGISTRY is the single place to add/remove agents.
# Each key is the agent identifier used in routing and state.
# To add a new agent:
#   1. Create app/graph/teams/analysis/my_agent.py extending BaseAnalysisAgent
#   2. Import and add it here — nothing else needs to change.

from app.graph.teams.analysis.market_agent import MarketAgent
from app.graph.teams.analysis.portfolio_agent import PortfolioAgent
from app.graph.teams.analysis.risk_agent import RiskAgent
from app.graph.teams.analysis.sentiment_agent import SentimentAgent

AGENT_REGISTRY: dict[str, object] = {
    "market": MarketAgent(),
    "risk": RiskAgent(),
    "sentiment": SentimentAgent(),
    "portfolio": PortfolioAgent(),
}

__all__ = ["AGENT_REGISTRY"]
