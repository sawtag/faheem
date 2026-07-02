from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from app.api.schemas import AgentOutput
from app.core.llm import get_llm
from app.graph.state import FinancialAnalysisState
from app.graph.teams.base_agent import BaseAnalysisAgent
from app.prompts.verification_compliance_prompts import CONFIDENCE_FLAGS_PROMPT


class ConfidenceFlagsAgent(BaseAnalysisAgent):
    name = "confidence_flags"

    async def analyze(self, state: FinancialAnalysisState) -> AgentOutput:
        llm = get_llm()
        outputs_text = "\n\n".join(
            f"{o['agent_name']} (confidence={o.get('confidence', '?')}): {o['analysis'][:300]}"
            for o in state.get("agent_outputs", [])
        )
        response = await llm.ainvoke([
            SystemMessage(content=CONFIDENCE_FLAGS_PROMPT),
            HumanMessage(content=(
                f"Query: {state['query']}\n\n"
                f"Request ID: {state.get('request_id', 'N/A')}\n\n"
                f"Agent outputs summary:\n{outputs_text}"
            )),
        ])
        return AgentOutput(
            agent_name=self.name,
            analysis=response.content,
            confidence=0.90,
            metadata={"team": "verification_compliance", "request_id": state.get("request_id")},
        )
