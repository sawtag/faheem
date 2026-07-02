from __future__ import annotations

from abc import ABC, abstractmethod

import structlog

from app.api.schemas import AgentOutput
from app.graph.state import FinancialAnalysisState
from data.synthetic.factory import DataFactory

log = structlog.get_logger()

# Singleton factory — shared across all agents; swap for real adapters per-agent later
_factory = DataFactory()


class BaseAnalysisAgent(ABC):
    name: str  # Must be overridden by each subclass

    @property
    def data(self) -> DataFactory:
        """Access to synthetic (or real, once swapped) data sources."""
        return _factory

    @abstractmethod
    async def analyze(self, state: FinancialAnalysisState) -> AgentOutput:
        """Perform domain-specific financial analysis and return a structured result."""
        ...

    async def __call__(self, state: FinancialAnalysisState) -> dict:
        """LangGraph-compatible node callable.
        Wraps analyze() so a single agent failure never crashes the full graph.
        """
        log.info(f"{self.name}.analyze", query=state["query"][:80])
        try:
            output = await self.analyze(state)
            result = output.model_dump()
        except Exception as exc:
            log.error(f"{self.name}.error", error=str(exc))
            result = AgentOutput(
                agent_name=self.name,
                analysis="",
                confidence=0.0,
                metadata={},
                error=str(exc),
            ).model_dump()
        return {"agent_outputs": [result]}
