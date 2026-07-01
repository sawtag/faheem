from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, Request
from fastapi.routing import APIRouter

from app.api.controller import analyze_controller
from app.api.schemas import AnalyzeRequest, AnalyzeResponse
from app.graph.graph import build_graph

router = APIRouter()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Compile the graph once at startup; reuse the compiled instance per request
    app.state.graph = build_graph()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Faheem Financial Analysis API",
        description="Multi-agent fintech analysis system powered by LangGraph",
        version="0.1.0",
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
