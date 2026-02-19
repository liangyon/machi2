from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    APP_ENV: str = "development"
    SECRET_KEY: str = "change-me-in-production"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./arcane_depths.db"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    OAUTH_REDIRECT_BASE: str = "http://localhost:8000"

    # LLM
    LLM_PROVIDER: str = "groq"  # groq | gemini | ollama
    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"

    # Session
    # Defaults to False so local dev (HTTP) works without a .env override.
    # Must be set to True in production where HTTPS is enforced.
    SESSION_COOKIE_SECURE: bool = False

    # Rate limiting
    FORGE_RATE_LIMIT: int = 20  # max new spell discoveries per user per hour

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
