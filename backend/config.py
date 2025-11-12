from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # API Keys
    groq_api_key: str

    # Database
    database_url: str = "sqlite:///./backend/data/app.db"

    # Vector Store
    chroma_persist_directory: str = "backend/data/chroma_db"

    # LLM Settings
    llm_model: str = "llama-3.3-70b-versatile"
    llm_temperature: float = 0.7
    embedding_model: str = "text-embedding-3-small"

    # Application
    app_name: str = "AI Interview Platform"
    debug: bool = False

    # Rate Limiting
    rate_limit_per_minute: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = False


# Singleton instance
settings = Settings()
