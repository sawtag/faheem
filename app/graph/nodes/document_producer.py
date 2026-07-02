from __future__ import annotations

import structlog
from langchain_core.messages import HumanMessage, SystemMessage

from app.api.schemas import ReportSchema
from app.core.llm import get_llm
from app.graph.state import FinancialAnalysisState
from app.prompts.document_prompts import DOCUMENT_PRODUCER_SYSTEM_PROMPT

log = structlog.get_logger()


async def run(state: FinancialAnalysisState) -> dict:
    agent_outputs = state.get("agent_outputs", [])
    log.info("document_producer.run", n_outputs=len(agent_outputs))

    successful = [o for o in agent_outputs if not o.get("error")]

    if not successful:
        log.warning("document_producer.no_successful_outputs")
        return {
            "report": {
                "sections": {},
                "summary_bullets": [],
                "raw_agent_outputs": agent_outputs,
            }
        }

    outputs_text = "\n\n".join(
        f"## {o['agent_name'].upper()} ANALYSIS\n{o['analysis']}"
        for o in successful
    )

    llm = get_llm().with_structured_output(ReportSchema)
    try:
        schema: ReportSchema = await llm.ainvoke([
            SystemMessage(content=DOCUMENT_PRODUCER_SYSTEM_PROMPT),
            HumanMessage(content=outputs_text),
        ])
        report = {
            "sections": schema.sections,
            "summary_bullets": schema.summary_bullets,
            "raw_agent_outputs": agent_outputs,
        }
    except Exception as exc:
        log.error("document_producer.error", error=str(exc))
        report = {
            "sections": {"combined_analysis": outputs_text},
            "summary_bullets": [],
            "raw_agent_outputs": agent_outputs,
        }

    return {"report": report}
