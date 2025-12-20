"""
PolyMind Configuration Module
Handles environment variables, API keys, and mock mode settings.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # App Configuration
    APP_NAME: str = "PolyMind"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=True)

    # Mock Mode - Set to True for UI testing without API costs
    MOCK_MODE: bool = Field(default=True)
    MOCK_STREAM_DELAY: float = Field(default=0.02)  # Delay between characters in mock streaming

    # API Keys (loaded from environment or set via frontend)
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None)
    GOOGLE_API_KEY: Optional[str] = Field(default=None)
    GROQ_API_KEY: Optional[str] = Field(default=None)

    # Model Defaults
    DEFAULT_ROUTER_MODEL: str = "gpt-4o-mini"
    DEFAULT_CODING_MODEL: str = "claude-3-5-sonnet-20241022"
    DEFAULT_CREATIVE_MODEL: str = "gpt-4o"
    DEFAULT_REASONING_MODEL: str = "claude-3-5-sonnet-20241022"
    DEFAULT_FACTUAL_MODEL: str = "gemini-1.5-pro"
    DEFAULT_SYNTHESIS_MODEL: str = "claude-3-5-sonnet-20241022"
    DEFAULT_CHAIRMAN_MODEL: str = "claude-3-5-sonnet-20241022"

    # Hub Mode Models (6 models for parallel execution)
    HUB_MODELS: list[str] = [
        "gpt-4o",
        "claude-3-5-sonnet-20241022",
        "gemini-1.5-pro",
        "gpt-4o-mini",
        "claude-3-haiku-20240307",
        "gemini-1.5-flash"
    ]

    # Voting Mode Models (5 models)
    VOTING_MODELS: list[str] = [
        "gpt-4o",
        "claude-3-5-sonnet-20241022",
        "gemini-1.5-pro",
        "gpt-4o-mini",
        "claude-3-haiku-20240307"
    ]

    # Synthesizer Models (3 models)
    SYNTHESIZER_MODELS: list[str] = [
        "gpt-4o",
        "claude-3-5-sonnet-20241022",
        "gemini-1.5-pro"
    ]

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000"
    ]

    # Request Configuration
    REQUEST_TIMEOUT: int = 120  # seconds
    MAX_TOKENS: int = 4096
    TEMPERATURE: float = 0.7

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings


def update_api_keys(
    openai_key: Optional[str] = None,
    anthropic_key: Optional[str] = None,
    google_key: Optional[str] = None,
    groq_key: Optional[str] = None
) -> None:
    """Update API keys at runtime (called from frontend settings)."""
    global settings
    if openai_key:
        settings.OPENAI_API_KEY = openai_key
        os.environ["OPENAI_API_KEY"] = openai_key
    if anthropic_key:
        settings.ANTHROPIC_API_KEY = anthropic_key
        os.environ["ANTHROPIC_API_KEY"] = anthropic_key
    if google_key:
        settings.GOOGLE_API_KEY = google_key
        os.environ["GOOGLE_API_KEY"] = google_key
    if groq_key:
        settings.GROQ_API_KEY = groq_key
        os.environ["GROQ_API_KEY"] = groq_key
