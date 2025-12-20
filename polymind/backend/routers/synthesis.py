"""
Mode B: The Synthesizer (Parallel Merge)
Queries multiple models in parallel and synthesizes a unified response.
"""

import asyncio
import json
from typing import AsyncGenerator
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from config import settings
from models.schemas import QueryRequest, SynthesisResponse, ModelResponse
from utils.llm_client import get_llm_client

router = APIRouter(prefix="/synthesizer", tags=["Synthesizer"])


SYNTHESIS_PROMPT = """You are a master synthesizer. You have received responses from multiple AI models to the same question. Your job is to:

1. Identify the unique insights and valuable points from each response
2. Merge them into a single, coherent, high-quality answer
3. Remove any redundancy while preserving all valuable information
4. Ensure the final response is well-structured and comprehensive
5. If there are conflicting viewpoints, acknowledge them fairly

Here are the responses to synthesize:

{responses}

Now provide the synthesized master response:"""


def format_responses_for_synthesis(responses: list) -> str:
    """Format multiple responses for the synthesis prompt."""
    formatted = []
    for i, resp in enumerate(responses, 1):
        formatted.append(f"=== Response {i} from {resp.model} ===\n{resp.content}\n")
    return "\n".join(formatted)


async def stream_synthesis(
    client,
    query: str,
    models: list[str],
    synthesis_model: str
) -> AsyncGenerator[str, None]:
    """Stream the synthesis process with progress updates."""
    messages = [{"role": "user", "content": query}]

    # Phase 1: Signal start of parallel queries
    yield f"data: {json.dumps({'event': 'phase', 'phase': 'querying', 'message': f'Querying {len(models)} models in parallel...'})}\n\n"

    # Execute all models in parallel
    responses = await client.parallel_complete(models=models, messages=messages)

    # Phase 2: Signal completion of queries
    yield f"data: {json.dumps({'event': 'phase', 'phase': 'collected', 'message': 'All responses collected. Beginning synthesis...'})}\n\n"

    # Send individual responses summary
    for i, resp in enumerate(responses):
        summary = resp.content[:200] + "..." if len(resp.content) > 200 else resp.content
        yield f"data: {json.dumps({'event': 'response', 'index': i, 'model': resp.model, 'preview': summary})}\n\n"

    # Phase 3: Synthesize
    yield f"data: {json.dumps({'event': 'phase', 'phase': 'synthesizing', 'message': 'Synthesizing unified response...'})}\n\n"

    synthesis_prompt = SYNTHESIS_PROMPT.format(
        responses=format_responses_for_synthesis(responses)
    )

    yield f"data: {json.dumps({'event': 'start', 'model': synthesis_model})}\n\n"

    async for chunk in client.stream(
        synthesis_model,
        [{"role": "user", "content": synthesis_prompt}]
    ):
        yield f"data: {json.dumps({'event': 'chunk', 'data': chunk})}\n\n"

    yield f"data: {json.dumps({'event': 'end'})}\n\n"
    yield f"data: {json.dumps({'event': 'done'})}\n\n"


@router.post("/stream")
async def synthesizer_stream(request: QueryRequest):
    """
    Stream the synthesis process.
    Shows progress through query, collection, and synthesis phases.
    """
    client = get_llm_client()
    models = request.models or settings.SYNTHESIZER_MODELS
    synthesis_model = settings.DEFAULT_SYNTHESIS_MODEL

    return EventSourceResponse(
        stream_synthesis(client, request.query, models, synthesis_model),
        media_type="text/event-stream"
    )


@router.post("/query")
async def synthesizer_query(request: QueryRequest) -> SynthesisResponse:
    """
    Non-streaming synthesis query.
    Returns all individual responses plus the synthesized result.
    """
    client = get_llm_client()
    models = request.models or settings.SYNTHESIZER_MODELS
    synthesis_model = settings.DEFAULT_SYNTHESIS_MODEL

    messages = [{"role": "user", "content": request.query}]

    # Get all responses in parallel
    responses = await client.parallel_complete(
        models=models,
        messages=messages,
        max_tokens=request.max_tokens,
        temperature=request.temperature
    )

    # Create synthesis prompt
    synthesis_prompt = SYNTHESIS_PROMPT.format(
        responses=format_responses_for_synthesis(responses)
    )

    # Get synthesized response
    synthesized = await client.complete(
        model=synthesis_model,
        messages=[{"role": "user", "content": synthesis_prompt}],
        max_tokens=request.max_tokens,
        temperature=0.5  # Lower temperature for synthesis
    )

    return SynthesisResponse(
        query=request.query,
        individual_responses=[
            ModelResponse(model=r.model, content=r.content)
            for r in responses
        ],
        synthesized_response=synthesized.content,
        models_used=models + [synthesis_model]
    )
