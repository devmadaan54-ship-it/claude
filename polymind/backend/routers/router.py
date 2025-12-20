"""
Mode A: The Auto-Router (Intelligent Switch)
Classifies user intent and routes to the optimal model.
"""

import json
from typing import AsyncGenerator
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from config import settings
from models.schemas import QueryRequest, RouterResponse, IntentCategory
from utils.llm_client import get_llm_client

router = APIRouter(prefix="/router", tags=["Router"])


# Intent to model mapping
INTENT_MODEL_MAP = {
    IntentCategory.CODING: settings.DEFAULT_CODING_MODEL,
    IntentCategory.CREATIVE: settings.DEFAULT_CREATIVE_MODEL,
    IntentCategory.REASONING: settings.DEFAULT_REASONING_MODEL,
    IntentCategory.FACTUAL: settings.DEFAULT_FACTUAL_MODEL,
}

INTENT_REASONING = {
    IntentCategory.CODING: "Routed to Claude 3.5 Sonnet for superior code generation and debugging capabilities.",
    IntentCategory.CREATIVE: "Routed to GPT-4o for creative writing with natural, engaging prose.",
    IntentCategory.REASONING: "Routed to Claude 3.5 Sonnet for step-by-step logical analysis.",
    IntentCategory.FACTUAL: "Routed to Gemini 1.5 Pro for comprehensive factual knowledge.",
}


async def stream_routed_response(
    client,
    query: str,
    intent: IntentCategory,
    model: str
) -> AsyncGenerator[str, None]:
    """Stream the routed response with metadata."""
    # Send routing info first
    routing_info = {
        "event": "routing",
        "intent": intent.value,
        "model": model,
        "reasoning": INTENT_REASONING[intent]
    }
    yield f"data: {json.dumps(routing_info)}\n\n"

    # Stream the actual response
    messages = [{"role": "user", "content": query}]

    yield f"data: {json.dumps({'event': 'start', 'model': model})}\n\n"

    async for chunk in client.stream(model, messages):
        yield f"data: {json.dumps({'event': 'chunk', 'data': chunk})}\n\n"

    yield f"data: {json.dumps({'event': 'end'})}\n\n"


@router.post("/stream")
async def router_stream(request: QueryRequest):
    """
    Stream a response after automatically routing to the best model.
    First classifies intent, then streams from the selected model.
    """
    client = get_llm_client()

    # Classify intent
    intent_str = await client.classify_intent(request.query)
    intent = IntentCategory(intent_str)

    # Get the appropriate model
    model = request.models[0] if request.models else INTENT_MODEL_MAP[intent]

    return EventSourceResponse(
        stream_routed_response(client, request.query, intent, model),
        media_type="text/event-stream"
    )


@router.post("/query")
async def router_query(request: QueryRequest) -> RouterResponse:
    """
    Non-streaming auto-router query.
    Classifies intent and returns the complete response.
    """
    client = get_llm_client()

    # Classify intent
    intent_str = await client.classify_intent(request.query)
    intent = IntentCategory(intent_str)

    # Get the appropriate model
    model = request.models[0] if request.models else INTENT_MODEL_MAP[intent]

    # Get response
    messages = [{"role": "user", "content": request.query}]
    response = await client.complete(
        model=model,
        messages=messages,
        max_tokens=request.max_tokens,
        temperature=request.temperature
    )

    return RouterResponse(
        query=request.query,
        detected_intent=intent,
        selected_model=model,
        content=response.content,
        reasoning=INTENT_REASONING[intent]
    )


@router.post("/classify")
async def classify_only(request: QueryRequest):
    """
    Only classify the intent without generating a response.
    Useful for debugging routing logic.
    """
    client = get_llm_client()
    intent_str = await client.classify_intent(request.query)
    intent = IntentCategory(intent_str)

    return {
        "query": request.query,
        "intent": intent.value,
        "recommended_model": INTENT_MODEL_MAP[intent],
        "reasoning": INTENT_REASONING[intent]
    }
