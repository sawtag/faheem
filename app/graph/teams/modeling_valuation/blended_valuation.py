from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from app.api.schemas import AgentOutput
from app.core.llm import get_llm
from app.graph.state import FinancialAnalysisState
from app.graph.teams.base_agent import BaseAnalysisAgent
from app.prompts.modeling_valuation_prompts import BLENDED_VALUATION_PROMPT


class BlendedValuationAgent(BaseAnalysisAgent):
    name = "blended_valuation"

    async def analyze(self, state: FinancialAnalysisState) -> AgentOutput:
        llm = get_llm()
        # valuation_inputs is injected by the team run() after DCF/LBO/Credit complete
        valuation_inputs = state.get("context", {}).get("valuation_inputs", "No prior valuation inputs available.")
        response = await llm.ainvoke([
            SystemMessage(content=BLENDED_VALUATION_PROMPT),
            HumanMessage(content=(
                f"Query: {state['query']}\n\n"
                f"Valuation method outputs to synthesize:\n{valuation_inputs}"
            )),
        ])
        return AgentOutput(
            agent_name=self.name,
            analysis=response.content,
            confidence=0.85,
            metadata={"team": "modeling_valuation", "model_type": "blended"},
        )
