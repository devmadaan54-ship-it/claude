"""
LLM Client Wrapper using LiteLLM
Provides a unified async interface for multiple LLM providers with mock mode support.
"""

import asyncio
import random
import string
from typing import AsyncGenerator, Optional, Any
from dataclasses import dataclass

import litellm
from litellm import acompletion

from config import settings


# Configure LiteLLM
litellm.set_verbose = settings.DEBUG


@dataclass
class LLMResponse:
    """Structured response from LLM."""
    model: str
    content: str
    finish_reason: str
    usage: dict


# Mock responses for different scenarios
MOCK_RESPONSES = {
    "default": """I understand your question. Let me provide a comprehensive answer.

Based on my analysis, here are the key points to consider:

1. **First Point**: This is an important consideration that affects the overall outcome.

2. **Second Point**: Building on the previous point, we should also examine this aspect carefully.

3. **Third Point**: Finally, this ties everything together and provides a complete picture.

In conclusion, the answer involves balancing multiple factors while keeping the end goal in mind. Would you like me to elaborate on any specific aspect?""",

    "coding": """Here's a solution for your coding question:

```python
def solution(data):
    '''
    A well-structured solution that handles the requirements.
    '''
    # Initialize the result
    result = []

    # Process the input data
    for item in data:
        processed = transform(item)
        if validate(processed):
            result.append(processed)

    return result


def transform(item):
    '''Transform a single item.'''
    return item.upper() if isinstance(item, str) else item * 2


def validate(item):
    '''Validate the transformed item.'''
    return item is not None
```

This solution follows best practices with clear separation of concerns and proper error handling.""",

    "creative": """*The morning sun painted golden streaks across the canvas of the sky...*

In the quiet village of Thornwood, where ancient oaks whispered secrets to those who listened, there lived a peculiar clockmaker named Elara. Her shop, nestled between a bakery that smelled of cinnamon dreams and a bookstore filled with forgotten tales, was known for creating timepieces that did more than tell time—they captured moments.

"Every tick," she would say to curious visitors, "is a heartbeat of the universe."

And perhaps, in her own magical way, she was right.""",

    "reasoning": """Let me work through this step by step:

**Step 1: Understanding the Problem**
First, we need to clearly define what we're trying to solve. The core question involves...

**Step 2: Breaking Down the Components**
- Component A: This affects X and Y
- Component B: This interacts with Component A through Z
- Component C: This is the outcome we're measuring

**Step 3: Analysis**
When we examine the relationship between these components, we find that...

**Step 4: Conclusion**
Based on this logical progression, the answer is that we should approach this by considering all factors systematically while prioritizing the most impactful elements.""",

    "factual": """Based on factual information:

**Key Facts:**
- Fact 1: This is verified by multiple reliable sources
- Fact 2: Historical data supports this conclusion
- Fact 3: Scientific consensus aligns with this understanding

**Context:**
This topic has been studied extensively since the early 2000s, with significant developments in 2015 and 2020.

**Current Status:**
As of the latest available information, the situation continues to evolve with new research being published regularly.

Note: For the most current information, I recommend consulting primary sources or recent publications."""
}


def get_mock_response(model: str, query: str) -> str:
    """Get an appropriate mock response based on model and query content."""
    query_lower = query.lower()

    # Determine response type based on query content
    if any(word in query_lower for word in ["code", "function", "program", "debug", "error", "python", "javascript"]):
        response_type = "coding"
    elif any(word in query_lower for word in ["write", "story", "creative", "poem", "imagine"]):
        response_type = "creative"
    elif any(word in query_lower for word in ["why", "how", "explain", "reason", "logic", "think"]):
        response_type = "reasoning"
    elif any(word in query_lower for word in ["what is", "when", "where", "who", "fact", "data"]):
        response_type = "factual"
    else:
        response_type = "default"

    # Add model identifier to response
    model_name = model.split("/")[-1] if "/" in model else model
    prefix = f"**[{model_name}]**\n\n"

    return prefix + MOCK_RESPONSES[response_type]


async def mock_stream_response(model: str, query: str) -> AsyncGenerator[str, None]:
    """Generate a mock streaming response character by character."""
    response = get_mock_response(model, query)

    for char in response:
        yield char
        await asyncio.sleep(settings.MOCK_STREAM_DELAY)


class LLMClient:
    """
    Unified LLM Client using LiteLLM.
    Supports both real API calls and mock mode for testing.
    """

    def __init__(self, mock_mode: Optional[bool] = None):
        """Initialize the LLM client."""
        self.mock_mode = mock_mode if mock_mode is not None else settings.MOCK_MODE
        self._configure_api_keys()

    def _configure_api_keys(self) -> None:
        """Configure API keys for LiteLLM."""
        import os
        if settings.OPENAI_API_KEY:
            os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
        if settings.ANTHROPIC_API_KEY:
            os.environ["ANTHROPIC_API_KEY"] = settings.ANTHROPIC_API_KEY
        if settings.GOOGLE_API_KEY:
            os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY
        if settings.GROQ_API_KEY:
            os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY

    async def complete(
        self,
        model: str,
        messages: list[dict],
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """
        Get a complete (non-streaming) response from the LLM.

        Args:
            model: The model identifier (e.g., 'gpt-4o', 'claude-3-5-sonnet-20241022')
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature

        Returns:
            LLMResponse with the complete response
        """
        if self.mock_mode:
            # Extract query from messages
            query = messages[-1].get("content", "") if messages else ""
            content = get_mock_response(model, query)
            return LLMResponse(
                model=model,
                content=content,
                finish_reason="stop",
                usage={"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300}
            )

        # Real API call using LiteLLM
        response = await acompletion(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )

        return LLMResponse(
            model=model,
            content=response.choices[0].message.content,
            finish_reason=response.choices[0].finish_reason,
            usage=dict(response.usage) if response.usage else {}
        )

    async def complete_json(
        self,
        model: str,
        messages: list[dict],
        response_format: Optional[dict] = None,
        max_tokens: int = 4096,
        temperature: float = 0.3,
        **kwargs
    ) -> LLMResponse:
        """
        Get a JSON-formatted response from the LLM.

        Args:
            model: The model identifier
            messages: List of message dicts
            response_format: Optional JSON schema for structured output
            max_tokens: Maximum tokens in response
            temperature: Lower temperature for more deterministic JSON

        Returns:
            LLMResponse with JSON content
        """
        if self.mock_mode:
            # Return mock JSON response for voting
            import json
            mock_json = {
                "vote": random.choice(["Yes", "No"]),
                "confidence": round(random.uniform(0.6, 0.95), 2),
                "reasoning": "Based on careful analysis of the available information, this conclusion follows logically from the premises presented."
            }
            return LLMResponse(
                model=model,
                content=json.dumps(mock_json),
                finish_reason="stop",
                usage={"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}
            )

        # Real API call with JSON mode
        response = await acompletion(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            response_format=response_format or {"type": "json_object"},
            **kwargs
        )

        return LLMResponse(
            model=model,
            content=response.choices[0].message.content,
            finish_reason=response.choices[0].finish_reason,
            usage=dict(response.usage) if response.usage else {}
        )

    async def stream(
        self,
        model: str,
        messages: list[dict],
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Stream a response from the LLM character by character.

        Args:
            model: The model identifier
            messages: List of message dicts
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature

        Yields:
            Individual characters/chunks from the response
        """
        if self.mock_mode:
            query = messages[-1].get("content", "") if messages else ""
            async for char in mock_stream_response(model, query):
                yield char
            return

        # Real streaming API call using LiteLLM
        response = await acompletion(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
            **kwargs
        )

        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def parallel_complete(
        self,
        models: list[str],
        messages: list[dict],
        max_tokens: int = 4096,
        temperature: float = 0.7
    ) -> list[LLMResponse]:
        """
        Execute multiple LLM completions in parallel using asyncio.gather.

        Args:
            models: List of model identifiers
            messages: Common messages for all models
            max_tokens: Maximum tokens per response
            temperature: Sampling temperature

        Returns:
            List of LLMResponse objects from all models
        """
        tasks = [
            self.complete(model, messages, max_tokens, temperature)
            for model in models
        ]
        return await asyncio.gather(*tasks)

    async def classify_intent(self, query: str) -> str:
        """
        Classify the intent of a user query for routing.

        Args:
            query: The user's query text

        Returns:
            Intent category: 'coding', 'creative', 'reasoning', or 'factual'
        """
        if self.mock_mode:
            # Simple keyword-based classification for mock mode
            query_lower = query.lower()
            if any(word in query_lower for word in ["code", "function", "program", "debug", "error", "python", "javascript", "api"]):
                return "coding"
            elif any(word in query_lower for word in ["write", "story", "creative", "poem", "imagine", "describe"]):
                return "creative"
            elif any(word in query_lower for word in ["why", "how does", "explain", "reason", "logic", "analyze"]):
                return "reasoning"
            else:
                return "factual"

        # Real classification using a lightweight model
        classification_prompt = f"""Classify the following user query into exactly one category.
Categories:
- coding: Programming, debugging, code review, technical implementation
- creative: Writing, storytelling, creative content, artistic expression
- reasoning: Logic problems, analysis, step-by-step thinking, explanations
- factual: Facts, data, information lookup, definitions, history

Query: {query}

Respond with only the category name in lowercase."""

        response = await self.complete(
            model=settings.DEFAULT_ROUTER_MODEL,
            messages=[{"role": "user", "content": classification_prompt}],
            max_tokens=20,
            temperature=0.1
        )

        intent = response.content.strip().lower()
        valid_intents = ["coding", "creative", "reasoning", "factual"]
        return intent if intent in valid_intents else "factual"


# Global client instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create the global LLM client instance."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
