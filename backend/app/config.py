import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "DecisionLens"
    PROJECT_NAME: str = "DecisionLens"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./decisionai.db"
    
    # Vector DB
    CHROMA_PERSIST_DIR: str = "./data/chroma_db"
    
    # LLM Settings
    LLM_PROVIDER: str = "mock"  # "mock", "gemini", "openai", "nvidia"
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    NVIDIA_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None
    DEFAULT_MODEL: str = "gpt-4o-mini"
    
    # Tool Settings
    TAVILY_API_KEY: Optional[str] = None
    SERPER_API_KEY: Optional[str] = None
    MAX_WEB_RESULTS: int = 5
    MAX_SEARCH_LOOPS: int = 2
    
    # Benchmark / Sample Data
    BENCHMARK_DB_PATH: str = "./data/sample_benchmark.db"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
