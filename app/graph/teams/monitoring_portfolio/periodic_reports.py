from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from app.api.schemas import AgentOutput
from app.core.llm import get_llm
from app.graph.state import FinancialAnalysisState
from app.graph.teams.base_agent import BaseAnalysisAgent
from app.prompts.monitoring_portfolio_prompts import PERIODIC_REPORTS_PROMPT


class PeriodicReportsAgent(BaseAnalysisAgent):
    name = "periodic_reports"

    async def analyze(self, state: FinancialAnalysisState) -> AgentOutput:
        llm = get_llm()
        response = await llm.ainvoke([
            SystemMessage(content=PERIODIC_REPORTS_PROMPT),
            HumanMessage(content=f"Query: {state['query']}\nContext: {state['context']}"),
        ])
        return AgentOutput(
            agent_name=self.name,
            analysis=response.content,
            confidence=0.85,
            metadata={"team": "monitoring_portfolio"},
        )
