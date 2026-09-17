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

    # API Keys
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    COHERE_API_KEY: str = ""

    # Model identifiers
    GEMINI_CHAT_MODEL: str = "gemini/gemini-1.5-flash"
    GEMINI_EMBEDDING_MODEL: str = "gemini/text-embedding-004"
    GROQ_MODEL: str = "groq/llama-3.1-8b-instant"
    COHERE_MODEL: str = "cohere/command-r"
    MAX_OUTPUT_TOKENS: int = 1024

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
