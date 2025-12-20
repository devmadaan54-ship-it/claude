"""
Mode E: Consensus Voting (Metric-Based)
Query multiple models with structured JSON output for voting.
"""

import asyncio
import json
from typing import AsyncGenerator
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from config import settings
from models.schemas import (
    QueryRequest, VotingResponse, VoteResult, ModelVote
)
from utils.llm_client import get_llm_client

router = APIRouter(prefix="/vote", tags=["Vote"])


VOTING_PROMPT = """You are participating in a consensus vote. Analyze the following question/statement and provide your vote.

Question/Statement: {query}

You MUST respond with valid JSON in exactly this format:
{{
    "vote": "Yes" or "No",
    "confidence": 0.0 to 1.0 (how confident are you in your vote),
    "reasoning": "Brief explanation for your vote (1-2 sentences)"
}}

Important:
- "Yes" means you agree with the statement or believe the answer is affirmative
- "No" means you disagree or believe the answer is negative
- Confidence should reflect how certain you are (0.5 = uncertain, 1.0 = very confident)

Respond ONLY with the JSON object, no additional text:"""


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


async def stream_voting(
    client,
    query: str,
    models: list[str]
) -> AsyncGenerator[str, None]:
    """Stream the voting process with live updates."""

    yield f"data: {json.dumps({'event': 'start', 'message': f'Collecting votes from {len(models)} models...', 'models': models})}\n\n"

    votes: list[ModelVote] = []

    # Collect votes in parallel but report as they come
    async def get_vote(model: str) -> tuple[str, dict]:
        prompt = VOTING_PROMPT.format(query=query)
        response = await client.complete_json(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        try:
            vote_data = json.loads(response.content)
            return model, vote_data
        except json.JSONDecodeError:
            return model, {"vote": "No", "confidence": 0.5, "reasoning": "Failed to parse response"}

    # Create tasks for all models
    tasks = [get_vote(model) for model in models]

    # Gather results (they complete in parallel)
    results = await asyncio.gather(*tasks)

    # Stream each vote as it's processed
    for model, vote_data in results:
        vote = VoteResult(
            vote=vote_data.get("vote", "No"),
            confidence=float(vote_data.get("confidence", 0.5)),
            reasoning=vote_data.get("reasoning", "No reasoning provided")
        )
        model_vote = ModelVote(model=model, vote=vote)
        votes.append(model_vote)

        # Stream this vote
        yield f"data: {json.dumps({'event': 'vote', 'model': model, 'display_name': get_model_display_name(model), 'vote': vote.vote, 'confidence': vote.confidence, 'reasoning': vote.reasoning})}\n\n"

    # Calculate consensus
    yes_count = sum(1 for v in votes if v.vote.vote == "Yes")
    no_count = sum(1 for v in votes if v.vote.vote == "No")

    if yes_count > no_count:
        consensus = "Yes"
    elif no_count > yes_count:
        consensus = "No"
    else:
        consensus = "Tie"

    avg_confidence = sum(v.vote.confidence for v in votes) / len(votes) if votes else 0

    # Get reasoning from the winning side's most confident voter
    winning_votes = [v for v in votes if v.vote.vote == consensus]
    if winning_votes:
        most_confident = max(winning_votes, key=lambda v: v.vote.confidence)
        winner_reasoning = most_confident.vote.reasoning
    else:
        winner_reasoning = "No clear winner"

    # Stream final result
    yield f"data: {json.dumps({'event': 'result', 'yes_count': yes_count, 'no_count': no_count, 'consensus': consensus, 'average_confidence': round(avg_confidence, 2), 'winner_reasoning': winner_reasoning})}\n\n"

    yield f"data: {json.dumps({'event': 'done'})}\n\n"


@router.post("/stream")
async def vote_stream(request: QueryRequest):
    """
    Stream the voting process with live vote updates.
    """
    client = get_llm_client()
    models = request.models or settings.VOTING_MODELS

    return EventSourceResponse(
        stream_voting(client, request.query, models),
        media_type="text/event-stream"
    )


@router.post("/query")
async def vote_query(request: QueryRequest) -> VotingResponse:
    """
    Non-streaming vote query.
    Returns all votes and the consensus result.
    """
    client = get_llm_client()
    models = request.models or settings.VOTING_MODELS

    votes: list[ModelVote] = []

    async def get_vote(model: str) -> ModelVote:
        prompt = VOTING_PROMPT.format(query=request.query)
        response = await client.complete_json(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        try:
            vote_data = json.loads(response.content)
            vote = VoteResult(
                vote=vote_data.get("vote", "No"),
                confidence=float(vote_data.get("confidence", 0.5)),
                reasoning=vote_data.get("reasoning", "No reasoning provided")
            )
        except (json.JSONDecodeError, KeyError):
            vote = VoteResult(
                vote="No",
                confidence=0.5,
                reasoning="Failed to parse response"
            )
        return ModelVote(model=model, vote=vote)

    # Collect all votes in parallel
    tasks = [get_vote(model) for model in models]
    votes = await asyncio.gather(*tasks)

    # Calculate consensus
    yes_count = sum(1 for v in votes if v.vote.vote == "Yes")
    no_count = sum(1 for v in votes if v.vote.vote == "No")

    if yes_count > no_count:
        consensus = "Yes"
    elif no_count > yes_count:
        consensus = "No"
    else:
        consensus = "Tie"

    avg_confidence = sum(v.vote.confidence for v in votes) / len(votes) if votes else 0

    # Get reasoning from the winning side
    winning_votes = [v for v in votes if v.vote.vote == consensus]
    if winning_votes:
        most_confident = max(winning_votes, key=lambda v: v.vote.confidence)
        winner_reasoning = most_confident.vote.reasoning
    else:
        winner_reasoning = "No clear winner"

    return VotingResponse(
        query=request.query,
        votes=list(votes),
        yes_count=yes_count,
        no_count=no_count,
        consensus=consensus,
        average_confidence=round(avg_confidence, 2),
        winner_reasoning=winner_reasoning
    )
