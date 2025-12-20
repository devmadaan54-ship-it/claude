"""
Pydantic Schemas for PolyMind API
Strict validation for all request/response types.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum


class QueryMode(str, Enum):
    """Available query modes for the unified endpoint."""
    ROUTER = "router"        # Mode A: Auto-Router
    SYNTHESIZER = "synthesizer"  # Mode B: Parallel Merge
    DEBATE = "debate"        # Mode C: Council/Debate
    HUB = "hub"              # Mode D: 6-Grid Matrix
    VOTE = "vote"            # Mode E: Consensus Voting


class IntentCategory(str, Enum):
    """Intent categories for routing."""
    CODING = "coding"
    CREATIVE = "creative"
    REASONING = "reasoning"
    FACTUAL = "factual"


# ============== Base Request/Response ==============

class QueryRequest(BaseModel):
    """Unified query request for all modes."""
    query: str = Field(..., min_length=1, max_length=10000, description="The user's query")
    mode: QueryMode = Field(default=QueryMode.ROUTER, description="Query processing mode")
    models: Optional[list[str]] = Field(default=None, description="Override default models")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=1, le=32000)
    stream: bool = Field(default=True, description="Enable streaming response")


class QueryResponse(BaseModel):
    """Standard query response."""
    mode: QueryMode
    model: str
    content: str
    finish_reason: str = "stop"
    usage: Optional[dict] = None


class StreamEvent(BaseModel):
    """SSE stream event format."""
    event: Literal["start", "chunk", "end", "error"]
    model: str
    data: str
    index: Optional[int] = None  # For hub mode - identifies which stream


# ============== Mode A: Router Response ==============

class RouterResponse(BaseModel):
    """Response from the auto-router mode."""
    query: str
    detected_intent: IntentCategory
    selected_model: str
    content: str
    reasoning: str = Field(default="", description="Why this model was selected")


# ============== Mode B: Synthesizer Response ==============

class ModelResponse(BaseModel):
    """Individual model response for synthesis."""
    model: str
    content: str


class SynthesisResponse(BaseModel):
    """Response from the synthesizer mode."""
    query: str
    individual_responses: list[ModelResponse]
    synthesized_response: str
    models_used: list[str]


# ============== Mode C: Debate Response ==============

class DebateStep(BaseModel):
    """A single step in the debate process."""
    step_number: int
    step_name: str  # e.g., "Initial Arguments", "Critique", "Final Verdict"
    model: str
    content: str
    role: str  # e.g., "Advocate A", "Advocate B", "Critic", "Chairman"


class DebateResponse(BaseModel):
    """Complete debate response with all steps."""
    query: str
    steps: list[DebateStep]
    final_verdict: str
    chairman_model: str


# ============== Mode D: Hub Response ==============

class HubStreamConfig(BaseModel):
    """Configuration for a single hub stream."""
    index: int
    model: str
    display_name: str


class HubResponse(BaseModel):
    """Response from the hub mode (for non-streaming)."""
    query: str
    responses: list[ModelResponse]
    stream_configs: list[HubStreamConfig]


# ============== Mode E: Voting Response ==============

class VoteResult(BaseModel):
    """Structured vote result from a single model."""
    vote: Literal["Yes", "No"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str


class ModelVote(BaseModel):
    """Vote with model identifier."""
    model: str
    vote: VoteResult


class VotingResponse(BaseModel):
    """Complete voting response with consensus."""
    query: str
    votes: list[ModelVote]
    yes_count: int
    no_count: int
    consensus: Literal["Yes", "No", "Tie"]
    average_confidence: float
    winner_reasoning: str


# ============== Settings ==============

class SettingsUpdate(BaseModel):
    """Request to update API keys and settings."""
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    mock_mode: Optional[bool] = None


class SettingsResponse(BaseModel):
    """Current settings response (keys masked)."""
    mock_mode: bool
    has_openai_key: bool
    has_anthropic_key: bool
    has_google_key: bool
    has_groq_key: bool
    available_models: list[str]


# ============== Health ==============

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str
    mock_mode: bool
