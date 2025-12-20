"""
Mode D: The Hub (6-Grid Matrix)
Fan-out architecture with parallel streaming to 6 models simultaneously.
"""

import asyncio
import json
from typing import AsyncGenerator
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from config import settings
from models.schemas import QueryRequest, HubResponse, HubStreamConfig, ModelResponse
from utils.llm_client import get_llm_client

router = APIRouter(prefix="/hub", tags=["Hub"])


def get_model_display_name(model: str) -> str:
    """Convert model ID to display-friendly name."""
    display_names = {
        "gpt-4o": "GPT-4o",
        "gpt-4o-mini": "GPT-4o Mini",
        "claude-3-5-sonnet-20241022": "Claude 3.5 Sonnet",
        "claude-3-haiku-20240307": "Claude 3 Haiku",
        "gemini-1.5-pro": "Gemini 1.5 Pro",
        "gemini-1.5-flash": "Gemini 1.5 Flash",
    }
    return display_names.get(model, model)


async def stream_single_model(
    client,
    model: str,
    messages: list[dict],
    index: int
) -> AsyncGenerator[str, None]:
    """Stream responses from a single model with index identification."""
    try:
        # Send start event
        yield f"data: {json.dumps({'event': 'start', 'index': index, 'model': model})}\n\n"

        # Stream content
        async for chunk in client.stream(model, messages):
            yield f"data: {json.dumps({'event': 'chunk', 'index': index, 'model': model, 'data': chunk})}\n\n"

        # Send end event
        yield f"data: {json.dumps({'event': 'end', 'index': index, 'model': model})}\n\n"

    except Exception as e:
        # Send error event
        yield f"data: {json.dumps({'event': 'error', 'index': index, 'model': model, 'data': str(e)})}\n\n"


async def multiplex_streams(
    client,
    models: list[str],
    messages: list[dict]
) -> AsyncGenerator[str, None]:
    """
    Multiplex multiple model streams into a single SSE stream.
    Each event is tagged with its model index so the frontend can
    route it to the correct grid cell.
    """
    # Create queues for each model
    queues: list[asyncio.Queue] = [asyncio.Queue() for _ in models]
    done_count = [0]

    async def producer(model: str, index: int, queue: asyncio.Queue):
        """Produce events for a single model into its queue."""
        try:
            # Start event
            await queue.put({
                "event": "start",
                "index": index,
                "model": model,
                "display_name": get_model_display_name(model)
            })

            # Stream content
            async for chunk in client.stream(model, messages):
                await queue.put({
                    "event": "chunk",
                    "index": index,
                    "model": model,
                    "data": chunk
                })

            # End event
            await queue.put({
                "event": "end",
                "index": index,
                "model": model
            })

        except Exception as e:
            await queue.put({
                "event": "error",
                "index": index,
                "model": model,
                "data": str(e)
            })

        finally:
            await queue.put(None)  # Signal done

    async def consumer() -> AsyncGenerator[dict, None]:
        """Consume from all queues and yield events."""
        active_queues = len(queues)

        while active_queues > 0:
            # Create tasks to wait on all queues
            for i, queue in enumerate(queues):
                if queue is not None:
                    try:
                        event = queue.get_nowait()
                        if event is None:
                            queues[i] = None
                            active_queues -= 1
                        else:
                            yield event
                    except asyncio.QueueEmpty:
                        pass

            # Small delay to prevent busy waiting
            await asyncio.sleep(0.01)

    # Start all producers
    tasks = [
        asyncio.create_task(producer(model, i, queues[i]))
        for i, model in enumerate(models)
    ]

    # Yield the stream config first
    config = {
        "event": "config",
        "streams": [
            {"index": i, "model": m, "display_name": get_model_display_name(m)}
            for i, m in enumerate(models)
        ]
    }
    yield f"data: {json.dumps(config)}\n\n"

    # Use a more robust approach: poll all queues
    active = [True] * len(models)

    while any(active):
        for i, queue in enumerate(queues):
            if active[i]:
                try:
                    event = queue.get_nowait()
                    if event is None:
                        active[i] = False
                    else:
                        yield f"data: {json.dumps(event)}\n\n"
                except asyncio.QueueEmpty:
                    pass

        await asyncio.sleep(0.005)  # 5ms polling interval

    # Wait for all tasks to complete
    await asyncio.gather(*tasks, return_exceptions=True)

    # Send final done event
    yield f"data: {json.dumps({'event': 'done'})}\n\n"


@router.post("/stream")
async def hub_stream(request: QueryRequest):
    """
    Stream responses from multiple models simultaneously.
    Returns an SSE stream with events tagged by model index.
    """
    client = get_llm_client()
    models = request.models or settings.HUB_MODELS[:6]  # Limit to 6 models

    messages = [{"role": "user", "content": request.query}]

    return EventSourceResponse(
        multiplex_streams(client, models, messages),
        media_type="text/event-stream"
    )


@router.post("/query")
async def hub_query(request: QueryRequest) -> HubResponse:
    """
    Non-streaming hub query - returns all responses at once.
    Useful for testing or when streaming is not needed.
    """
    client = get_llm_client()
    models = request.models or settings.HUB_MODELS[:6]

    messages = [{"role": "user", "content": request.query}]

    # Execute all models in parallel
    responses = await client.parallel_complete(
        models=models,
        messages=messages,
        max_tokens=request.max_tokens,
        temperature=request.temperature
    )

    return HubResponse(
        query=request.query,
        responses=[
            ModelResponse(model=r.model, content=r.content)
            for r in responses
        ],
        stream_configs=[
            HubStreamConfig(
                index=i,
                model=m,
                display_name=get_model_display_name(m)
            )
            for i, m in enumerate(models)
        ]
    )


@router.get("/models")
async def get_hub_models():
    """Get available models for hub mode."""
    return {
        "models": [
            {"id": m, "display_name": get_model_display_name(m)}
            for m in settings.HUB_MODELS
        ]
    }
