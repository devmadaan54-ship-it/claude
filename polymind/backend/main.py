"""
PolyMind - LLM Orchestration Platform
FastAPI Backend Entry Point
"""

import asyncio
import json
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from config import settings, update_api_keys, get_settings
from models.schemas import (
    QueryRequest,
    QueryMode,
    HealthResponse,
    SettingsUpdate,
)
from routers import (
    router_router,
    synthesis_router,
    debate_router,
    hub_router,
    vote_router,
)
from utils.llm_client import get_llm_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📡 Mock Mode: {'Enabled' if settings.MOCK_MODE else 'Disabled'}")
    print(f"🌐 CORS Origins: {settings.CORS_ORIGINS}")

    yield

    # Shutdown
    print(f"👋 Shutting down {settings.APP_NAME}")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Production-grade LLM Orchestration Platform with multi-model routing, synthesis, debate, and consensus voting.",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router_router)
app.include_router(synthesis_router)
app.include_router(debate_router)
app.include_router(hub_router)
app.include_router(vote_router)


# ============== Unified Query Endpoint ==============

@app.post("/query")
async def unified_query(request: QueryRequest):
    """
    Unified query endpoint that routes to the appropriate mode.

    Modes:
    - router: Auto-classify intent and route to best model
    - synthesizer: Query multiple models and merge responses
    - debate: Multi-step debate with verdict
    - hub: Parallel streaming to multiple models
    - vote: Consensus voting with structured output
    """
    # Route based on mode
    if request.mode == QueryMode.ROUTER:
        from routers.router import router_stream, router_query
        if request.stream:
            return await router_stream(request)
        return await router_query(request)

    elif request.mode == QueryMode.SYNTHESIZER:
        from routers.synthesis import synthesizer_stream, synthesizer_query
        if request.stream:
            return await synthesizer_stream(request)
        return await synthesizer_query(request)

    elif request.mode == QueryMode.DEBATE:
        from routers.debate import debate_stream, debate_query
        if request.stream:
            return await debate_stream(request)
        return await debate_query(request)

    elif request.mode == QueryMode.HUB:
        from routers.hub import hub_stream, hub_query
        if request.stream:
            return await hub_stream(request)
        return await hub_query(request)

    elif request.mode == QueryMode.VOTE:
        from routers.vote import vote_stream, vote_query
        if request.stream:
            return await vote_stream(request)
        return await vote_query(request)

    else:
        raise HTTPException(status_code=400, detail=f"Unknown mode: {request.mode}")


# ============== Settings Endpoints ==============

@app.post("/settings")
async def update_settings(update: SettingsUpdate):
    """Update API keys and settings."""
    update_api_keys(
        openai_key=update.openai_api_key,
        anthropic_key=update.anthropic_api_key,
        google_key=update.google_api_key,
        groq_key=update.groq_api_key,
    )

    if update.mock_mode is not None:
        settings.MOCK_MODE = update.mock_mode

    return {"status": "updated", "mock_mode": settings.MOCK_MODE}


@app.get("/settings")
async def get_current_settings():
    """Get current settings (API keys are masked)."""
    return {
        "mock_mode": settings.MOCK_MODE,
        "has_openai_key": bool(settings.OPENAI_API_KEY),
        "has_anthropic_key": bool(settings.ANTHROPIC_API_KEY),
        "has_google_key": bool(settings.GOOGLE_API_KEY),
        "has_groq_key": bool(settings.GROQ_API_KEY),
        "available_models": {
            "hub": settings.HUB_MODELS,
            "voting": settings.VOTING_MODELS,
            "synthesizer": settings.SYNTHESIZER_MODELS,
        }
    }


# ============== Health Endpoints ==============

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        mock_mode=settings.MOCK_MODE
    )


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "LLM Orchestration Platform",
        "docs": "/docs",
        "modes": {
            "router": "Auto-classify and route to optimal model",
            "synthesizer": "Parallel query and merge responses",
            "debate": "Multi-step debate with final verdict",
            "hub": "6-grid parallel streaming matrix",
            "vote": "Consensus voting with structured output"
        },
        "endpoints": {
            "unified": "POST /query",
            "router": "POST /router/stream, POST /router/query",
            "synthesizer": "POST /synthesizer/stream, POST /synthesizer/query",
            "debate": "POST /debate/stream, POST /debate/query",
            "hub": "POST /hub/stream, POST /hub/query",
            "vote": "POST /vote/stream, POST /vote/query",
            "settings": "GET/POST /settings",
            "health": "GET /health"
        }
    }


# ============== Run with Uvicorn ==============

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
