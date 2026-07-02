from __future__ import annotations

import structlog
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage

from app.api.schemas import AgentOutput
from app.core.llm import get_llm
from app.core.vectorstore import get_vectorstore
from app.graph.state import FinancialAnalysisState
from app.graph.teams.base_agent import BaseAnalysisAgent
from app.prompts.document_intelligence_prompts import DOCUMENT_EXTRACTOR_PROMPT

log = structlog.get_logger()


class DocumentExtractorAgent(BaseAnalysisAgent):
    name = "document_extractor"

    async def analyze(self, state: FinancialAnalysisState) -> AgentOutput:
        vs = get_vectorstore()

        # Retrieve relevant documents from Qdrant
        retrieved_context = ""
        try:
            docs = vs.similarity_search(state["query"], k=5)
            if docs:
                retrieved_context = "\n\n".join(
                    f"[Source: {d.metadata.get('source', 'unknown')}]\n{d.page_content}"
                    for d in docs
                )
                log.info("document_extractor.retrieved", n_docs=len(docs))
        except Exception as exc:
            log.warning("document_extractor.retrieval_skipped", error=str(exc))

        prompt_input = f"Query: {state['query']}\nContext: {state['context']}"
        if retrieved_context:
            prompt_input += f"\n\nRetrieved Documents:\n{retrieved_context}"

        llm = get_llm()
        response = await llm.ainvoke([
            SystemMessage(content=DOCUMENT_EXTRACTOR_PROMPT),
            HumanMessage(content=prompt_input),
        ])

        # Store the analysis result back into Qdrant for future retrieval
        try:
            vs.add_documents([
                Document(
                    page_content=response.content,
                    metadata={
                        "source": "document_extractor",
                        "query": state["query"][:200],
                        "team": "document_intelligence",
                    },
                )
            ])
        except Exception as exc:
            log.warning("document_extractor.store_skipped", error=str(exc))

        return AgentOutput(
            agent_name=self.name,
            analysis=response.content,
            confidence=0.88,
            metadata={
                "team": "document_intelligence",
                "retrieved_docs": len(docs) if retrieved_context else 0,
            },
        )
