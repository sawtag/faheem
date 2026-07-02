from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from app.api.schemas import AgentOutput
from app.core.llm import get_llm
from app.graph.state import FinancialAnalysisState
from app.graph.teams.base_agent import BaseAnalysisAgent
from app.prompts.verification_compliance_prompts import FACT_CHECK_VISUAL_PROMPT


class FactCheckVisualAgent(BaseAnalysisAgent):
    name = "fact_check_visual"

    async def analyze(self, state: FinancialAnalysisState) -> AgentOutput:
        llm = get_llm()
        outputs_text = "\n\n".join(
            f"{o['agent_name']}: {o['analysis']}"
            for o in state.get("agent_outputs", [])
            if not o.get("error")
        )
        response = await llm.ainvoke([
            SystemMessage(content=FACT_CHECK_VISUAL_PROMPT),
            HumanMessage(content=(
                f"Query: {state['query']}\n\n"
                f"Source context: {state.get('context', {})}\n\n"
                f"Outputs to fact-check:\n{outputs_text}"
            )),
        ])
        return AgentOutput(
            agent_name=self.name,
            analysis=response.content,
            confidence=0.88,
            metadata={"team": "verification_compliance"},
        )
