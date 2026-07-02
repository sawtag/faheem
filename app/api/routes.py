from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, Request
from fastapi.routing import APIRouter

from app.api.controller import analyze_controller, monitor_controller
from app.api.schemas import AnalyzeRequest, AnalyzeResponse, MonitorRequest, MonitorResponse
from app.graph.graph import build_graph
from app.graph.teams import monitoring_portfolio

router = APIRouter()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Compile the main analysis graph once at startup
    app.state.graph = build_graph()

    # Monitor graph: a minimal single-team graph for portfolio monitoring
    from langgraph.graph import END, START, StateGraph
    from app.graph.state import FinancialAnalysisState

    builder = StateGraph(FinancialAnalysisState)
    builder.add_node("monitoring_portfolio", monitoring_portfolio.run)
    builder.add_edge(START, "monitoring_portfolio")
    builder.add_edge("monitoring_portfolio", END)
    app.state.monitor_graph = builder.compile()

    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Faheem Financial Analysis API",
        description="Enterprise multi-agent fintech analysis system powered by LangGraph",
        version="0.2.0",
        lifespan=lifespan,
    )
    app.include_router(router)
    return app


@router.get("/health")
async def health() -> dict[str, Any]:
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest, request: Request) -> AnalyzeResponse:
    return await analyze_controller(req, graph=request.app.state.graph)


@router.post("/monitor", response_model=MonitorResponse)
async def monitor(req: MonitorRequest, request: Request) -> MonitorResponse:
    return await monitor_controller(req, monitor_graph=request.app.state.monitor_graph)
