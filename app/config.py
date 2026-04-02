"""
Application configuration.

Loads and validates environment variables at startup using Pydantic Settings.
Fail-fast approach: if required config is missing, the app won't start.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    # ── App ──────────────────────────────────────────────
    APP_NAME: str = "Finance Dashboard API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ── Database ─────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./finance.db"

    # ── JWT ──────────────────────────────────────────────
    JWT_SECRET_KEY: str = Field(
        ..., description="Secret key for JWT signing. Must be set."
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ── Rate Limiting ────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 60

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


# Singleton — imported everywhere as `from app.config import settings`
settings = Settings()
