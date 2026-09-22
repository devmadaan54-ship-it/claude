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

    # Tracxn API (company/investor intelligence data)
    # Tracxn is a REST API, not a SQL database: generate an access token at
    # https://platform.tracxn.com/a/api/apitoken and set TRACXN_ACCESS_TOKEN.
    TRACXN_ACCESS_TOKEN: Optional[str] = Field(default=None)
    TRACXN_BASE_URL: str = Field(default="https://platform.tracxn.com/api/2.2")
    # Header name carrying the token. Confirm against your account's API docs;
    # override here if your plan expects a different header.
    TRACXN_AUTH_HEADER: str = Field(default="accessToken")
    TRACXN_TIMEOUT: int = Field(default=30)  # seconds
    TRACXN_MAX_RETRIES: int = Field(default=3)  # retries on 429/5xx
    TRACXN_MOCK_MODE: bool = Field(default=True)  # serve mock rows, spend no credits

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


def update_tracxn_config(
    access_token: Optional[str] = None,
    base_url: Optional[str] = None,
    auth_header: Optional[str] = None,
    mock_mode: Optional[bool] = None,
) -> None:
    """Update Tracxn API settings at runtime (called from frontend settings)."""
    global settings
    if access_token:
        settings.TRACXN_ACCESS_TOKEN = access_token
        os.environ["TRACXN_ACCESS_TOKEN"] = access_token
    if base_url:
        settings.TRACXN_BASE_URL = base_url
    if auth_header:
        settings.TRACXN_AUTH_HEADER = auth_header
    if mock_mode is not None:
        settings.TRACXN_MOCK_MODE = mock_mode
