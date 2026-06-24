"""Application configuration loaded from environment variables."""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False
    )

    # Application
    ENVIRONMENT: Literal["development", "staging", "production", "test"] = "development"
    PROJECT_NAME: str = "Extract AI"
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: str = "http://localhost:5173"

    # Security
    SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14
    ALGORITHM: str = "HS256"

    # Database
    POSTGRES_USER: str = "extract"
    POSTGRES_PASSWORD: str = "extract"
    POSTGRES_DB: str = "extract_ai"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str | None = None

    # LLM provider selection
    # "openai" (GPT-4o) or "anthropic" (Claude). When LLM_MOCK is true (or no
    # key is configured for the selected provider) a deterministic stub is used.
    LLM_PROVIDER: Literal["openai", "anthropic"] = "openai"
    LLM_MOCK: bool = False
    # Prompt strategy for extraction: zero_shot | few_shot | cot (chain-of-thought)
    LLM_PROMPT_STRATEGY: Literal["zero_shot", "few_shot", "cot"] = "zero_shot"
    # Retries on transient LLM errors (rate limit / 5xx / connection).
    LLM_MAX_RETRIES: int = 2

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    # Back-compat alias: setting OPENAI_MOCK=true still forces the stub.
    OPENAI_MOCK: bool = False

    # Anthropic (Claude)
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-opus-4-8"

    # OCR
    OCR_ENGINE: Literal["easyocr", "tesseract"] = "easyocr"
    OCR_LANGUAGES: str = "en"
    OCR_CONFIDENCE_THRESHOLD: float = 0.45

    # Uploads / storage
    MAX_UPLOAD_SIZE_MB: int = 50
    STORAGE_BACKEND: Literal["local", "s3"] = "local"
    STORAGE_DIR: str = "storage"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def sqlalchemy_database_uri(self) -> str:
        if self.DATABASE_URL:
            return self._normalise_db_url(self.DATABASE_URL)
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @staticmethod
    def _normalise_db_url(url: str) -> str:
        """Force the psycopg (v3) driver for Postgres URLs.

        Managed hosts (Railway, Render, Heroku) inject `postgres://` or
        `postgresql://`, which SQLAlchemy would route to psycopg2 (not
        installed). Rewrite to `postgresql+psycopg://`. SQLite/other URLs pass
        through unchanged.
        """
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://") :]
        if url.startswith("postgresql://"):
            return "postgresql+psycopg://" + url[len("postgresql://") :]
        return url

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.BACKEND_CORS_ORIGINS.split(",") if o.strip()]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def max_upload_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @computed_field  # type: ignore[prop-decorator]
    @property
    def ocr_language_list(self) -> list[str]:
        return [lang.strip() for lang in self.OCR_LANGUAGES.split(",") if lang.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
