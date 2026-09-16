from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "AI Master Tutor API"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "chrome-extension://*",
    ]

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_master_tutor"

    # Semantic Cache
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_data"

    # LLM Keys
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    COHERE_API_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
