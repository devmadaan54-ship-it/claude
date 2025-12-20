"""
Mode C: The Council (Debate System)
Multi-step agent flow with debate, critique, and final verdict.
"""

import asyncio
import json
from typing import AsyncGenerator
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from config import settings
from models.schemas import QueryRequest, DebateResponse, DebateStep
from utils.llm_client import get_llm_client

router = APIRouter(prefix="/debate", tags=["Debate"])


ADVOCATE_A_PROMPT = """You are Advocate A in an intellectual debate. Your role is to provide a thoughtful, well-reasoned initial perspective on the following question. Be comprehensive but concise.

Question: {query}

Present your argument:"""

ADVOCATE_B_PROMPT = """You are Advocate B in an intellectual debate. You've seen Advocate A's perspective below. Your role is to provide an alternative or complementary viewpoint. Focus on aspects that A may have overlooked or approach the question differently.

Question: {query}

Advocate A's Argument:
{advocate_a_response}

Present your alternative perspective:"""

CRITIQUE_PROMPT = """You are a Critical Analyst. Review both arguments presented below and identify:
1. Strengths in each argument
2. Gaps or weaknesses in each argument
3. Points of agreement between the arguments
4. Unresolved tensions or contradictions

Question: {query}

Advocate A's Argument:
{advocate_a_response}

Advocate B's Argument:
{advocate_b_response}

Provide your critical analysis:"""

CHAIRMAN_PROMPT = """You are the Chairman of this debate council. You have heard all perspectives and the critical analysis. Your role is to deliver a final, balanced verdict that:
1. Acknowledges the valid points from all sides
2. Resolves any contradictions fairly
3. Provides a clear, actionable conclusion
4. Synthesizes the best insights into a coherent answer

Question: {query}

Advocate A's Argument:
{advocate_a_response}

Advocate B's Argument:
{advocate_b_response}

Critical Analysis:
{critique_response}

Deliver your final verdict:"""


async def stream_debate(
    client,
    query: str,
    advocate_a_model: str,
    advocate_b_model: str,
    chairman_model: str
) -> AsyncGenerator[str, None]:
    """Stream the entire debate process with step-by-step updates."""

    # Step 1: Advocate A's Initial Argument
    yield f"data: {json.dumps({'event': 'step_start', 'step': 1, 'name': 'Initial Arguments', 'role': 'Advocate A', 'model': advocate_a_model})}\n\n"

    advocate_a_prompt = ADVOCATE_A_PROMPT.format(query=query)
    advocate_a_response = ""

    async for chunk in client.stream(advocate_a_model, [{"role": "user", "content": advocate_a_prompt}]):
        advocate_a_response += chunk
        yield f"data: {json.dumps({'event': 'chunk', 'step': 1, 'data': chunk})}\n\n"

    yield f"data: {json.dumps({'event': 'step_end', 'step': 1})}\n\n"

    # Step 2: Advocate B's Counter Argument
    yield f"data: {json.dumps({'event': 'step_start', 'step': 2, 'name': 'Alternative Perspective', 'role': 'Advocate B', 'model': advocate_b_model})}\n\n"

    advocate_b_prompt = ADVOCATE_B_PROMPT.format(
        query=query,
        advocate_a_response=advocate_a_response
    )
    advocate_b_response = ""

    async for chunk in client.stream(advocate_b_model, [{"role": "user", "content": advocate_b_prompt}]):
        advocate_b_response += chunk
        yield f"data: {json.dumps({'event': 'chunk', 'step': 2, 'data': chunk})}\n\n"

    yield f"data: {json.dumps({'event': 'step_end', 'step': 2})}\n\n"

    # Step 3: Critical Analysis
    yield f"data: {json.dumps({'event': 'step_start', 'step': 3, 'name': 'Critical Analysis', 'role': 'Critic', 'model': advocate_a_model})}\n\n"

    critique_prompt = CRITIQUE_PROMPT.format(
        query=query,
        advocate_a_response=advocate_a_response,
        advocate_b_response=advocate_b_response
    )
    critique_response = ""

    async for chunk in client.stream(advocate_a_model, [{"role": "user", "content": critique_prompt}]):
        critique_response += chunk
        yield f"data: {json.dumps({'event': 'chunk', 'step': 3, 'data': chunk})}\n\n"

    yield f"data: {json.dumps({'event': 'step_end', 'step': 3})}\n\n"

    # Step 4: Chairman's Final Verdict
    yield f"data: {json.dumps({'event': 'step_start', 'step': 4, 'name': 'Final Verdict', 'role': 'Chairman', 'model': chairman_model})}\n\n"

    chairman_prompt = CHAIRMAN_PROMPT.format(
        query=query,
        advocate_a_response=advocate_a_response,
        advocate_b_response=advocate_b_response,
        critique_response=critique_response
    )

    async for chunk in client.stream(chairman_model, [{"role": "user", "content": chairman_prompt}]):
        yield f"data: {json.dumps({'event': 'chunk', 'step': 4, 'data': chunk})}\n\n"

    yield f"data: {json.dumps({'event': 'step_end', 'step': 4})}\n\n"
    yield f"data: {json.dumps({'event': 'done'})}\n\n"


@router.post("/stream")
async def debate_stream(request: QueryRequest):
    """
    Stream the full debate process.
    Shows each step as it progresses through the debate.
    """
    client = get_llm_client()

    # Default models for debate
    advocate_a_model = "gpt-4o"
    advocate_b_model = "gemini-1.5-pro"
    chairman_model = settings.DEFAULT_CHAIRMAN_MODEL

    if request.models and len(request.models) >= 3:
        advocate_a_model = request.models[0]
        advocate_b_model = request.models[1]
        chairman_model = request.models[2]

    return EventSourceResponse(
        stream_debate(
            client,
            request.query,
            advocate_a_model,
            advocate_b_model,
            chairman_model
        ),
        media_type="text/event-stream"
    )


@router.post("/query")
async def debate_query(request: QueryRequest) -> DebateResponse:
    """
    Non-streaming debate query.
    Returns all steps and the final verdict.
    """
    client = get_llm_client()

    advocate_a_model = "gpt-4o"
    advocate_b_model = "gemini-1.5-pro"
    chairman_model = settings.DEFAULT_CHAIRMAN_MODEL

    if request.models and len(request.models) >= 3:
        advocate_a_model = request.models[0]
        advocate_b_model = request.models[1]
        chairman_model = request.models[2]

    steps = []

    # Step 1: Advocate A
    advocate_a_prompt = ADVOCATE_A_PROMPT.format(query=request.query)
    advocate_a_resp = await client.complete(
        advocate_a_model,
        [{"role": "user", "content": advocate_a_prompt}]
    )
    steps.append(DebateStep(
        step_number=1,
        step_name="Initial Arguments",
        model=advocate_a_model,
        content=advocate_a_resp.content,
        role="Advocate A"
    ))

    # Step 2: Advocate B
    advocate_b_prompt = ADVOCATE_B_PROMPT.format(
        query=request.query,
        advocate_a_response=advocate_a_resp.content
    )
    advocate_b_resp = await client.complete(
        advocate_b_model,
        [{"role": "user", "content": advocate_b_prompt}]
    )
    steps.append(DebateStep(
        step_number=2,
        step_name="Alternative Perspective",
        model=advocate_b_model,
        content=advocate_b_resp.content,
        role="Advocate B"
    ))

    # Step 3: Critique
    critique_prompt = CRITIQUE_PROMPT.format(
        query=request.query,
        advocate_a_response=advocate_a_resp.content,
        advocate_b_response=advocate_b_resp.content
    )
    critique_resp = await client.complete(
        advocate_a_model,
        [{"role": "user", "content": critique_prompt}]
    )
    steps.append(DebateStep(
        step_number=3,
        step_name="Critical Analysis",
        model=advocate_a_model,
        content=critique_resp.content,
        role="Critic"
    ))

    # Step 4: Chairman Verdict
    chairman_prompt = CHAIRMAN_PROMPT.format(
        query=request.query,
        advocate_a_response=advocate_a_resp.content,
        advocate_b_response=advocate_b_resp.content,
        critique_response=critique_resp.content
    )
    chairman_resp = await client.complete(
        chairman_model,
        [{"role": "user", "content": chairman_prompt}]
    )
    steps.append(DebateStep(
        step_number=4,
        step_name="Final Verdict",
        model=chairman_model,
        content=chairman_resp.content,
        role="Chairman"
    ))

    return DebateResponse(
        query=request.query,
        steps=steps,
        final_verdict=chairman_resp.content,
        chairman_model=chairman_model
    )
