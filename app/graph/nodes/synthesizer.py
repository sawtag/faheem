from __future__ import annotations

import structlog
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.llm import get_llm
from app.graph.state import FinancialAnalysisState
from app.prompts.synthesizer_prompts import SYNTHESIZER_SYSTEM_PROMPT

log = structlog.get_logger()


async def run(state: FinancialAnalysisState) -> dict:
    report = state.get("report")
    log.info("synthesizer.run", has_report=report is not None)

    if report:
        bullets = "\n".join(f"- {b}" for b in report.get("summary_bullets", []))
        context = (
            f"Report sections:\n{report.get('sections', {})}\n\n"
            f"Key findings:\n{bullets}"
        )
    else:
        # Fast path: no analysis ran (simple_query or unknown route)
        context = f"User query: {state['query']}"

    llm = get_llm()
    try:
        response = await llm.ainvoke([
            SystemMessage(content=SYNTHESIZER_SYSTEM_PROMPT),
            HumanMessage(content=context),
        ])
        final_output = response.content
    except Exception as exc:
        log.error("synthesizer.error", error=str(exc))
        final_output = "Analysis could not be completed. Please try again."

    return {"final_output": final_output}
