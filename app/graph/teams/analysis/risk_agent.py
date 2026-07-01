from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from app.api.schemas import AgentOutput
from app.core.llm import get_llm
from app.graph.state import FinancialAnalysisState
from app.graph.teams.analysis.base_agent import BaseAnalysisAgent
from app.prompts.agent_prompts import RISK_AGENT_SYSTEM_PROMPT


class RiskAgent(BaseAnalysisAgent):
    name = "risk"

    async def analyze(self, state: FinancialAnalysisState) -> AgentOutput:
        llm = get_llm()
        response = await llm.ainvoke([
            SystemMessage(content=RISK_AGENT_SYSTEM_PROMPT),
            HumanMessage(content=f"Query: {state['query']}\nContext: {state['context']}"),
        ])
        return AgentOutput(
            agent_name=self.name,
            analysis=response.content,
            confidence=0.80,
            metadata={"focus": "volatility, downside risk, risk metrics"},
        )
