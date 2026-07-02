from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from app.api.schemas import AgentOutput
from app.core.llm import get_llm
from app.graph.state import FinancialAnalysisState
from app.graph.teams.base_agent import BaseAnalysisAgent
from app.prompts.verification_compliance_prompts import SHARIAH_SCREENING_PROMPT


class ShariahScreeningAgent(BaseAnalysisAgent):
    name = "shariah_screening"

    async def analyze(self, state: FinancialAnalysisState) -> AgentOutput:
        llm = get_llm()
        outputs_text = "\n\n".join(
            f"{o['agent_name']}: {o['analysis']}"
            for o in state.get("agent_outputs", [])
            if not o.get("error")
        )
        response = await llm.ainvoke([
            SystemMessage(content=SHARIAH_SCREENING_PROMPT),
            HumanMessage(content=f"Query: {state['query']}\n\nOutputs to screen:\n{outputs_text}"),
        ])
        return AgentOutput(
            agent_name=self.name,
            analysis=response.content,
            confidence=0.90,
            metadata={"team": "verification_compliance"},
        )
