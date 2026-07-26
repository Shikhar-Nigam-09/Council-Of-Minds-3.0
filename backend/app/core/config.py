from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Council of Minds"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""
    UPSTASH_REDIS_REST_URL: str = ""
    UPSTASH_REDIS_REST_TOKEN: str = ""
    MAX_UPLOAD_SIZE_MB: int = 25
    MAX_DOCUMENTS_PER_USER: int = 20
    
    HUGGINGFACE_API_KEY: str = ""
    HUGGINGFACE_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    QDRANT_URL: str = ""
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION_NAME: str = "council_of_minds_chunks"
    TESSERACT_CMD_PATH: str = ""
    OCR_ENABLED: bool = True

    # Phase 4
    GROQ_API_KEY: str | None = None
    GROQ_PLANNER_MODEL: str = "llama-3.1-8b-instant"
    GROQ_COUNCIL_MODEL: str = "llama-3.3-70b-versatile"
    PLANNER_MAX_RETRIES: int = 3

    # Phase 6
    GROQ_JUDGE_MODEL: str = "llama-3.3-70b-versatile"
    PRICING_TABLE_PATH: str = ""

    # Phase 7
    LANGSMITH_API_KEY: str = ""
    LANGSMITH_PROJECT: str = "council-of-minds"
    RATE_LIMIT_GENERAL_PER_MINUTE: int = 60
    RATE_LIMIT_UPLOAD_PER_HOUR: int = 10
    RATE_LIMIT_LLM_PER_HOUR: int = 20
    DAILY_COST_CAP_USD: float = 5.00
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5
    CIRCUIT_BREAKER_COOLDOWN_SECONDS: int = 30
    ALLOWED_CORS_ORIGINS: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    @property
    def is_mock_mode(self) -> bool:
        # Computed property for later phases to detect mock mode
        return self.ENVIRONMENT == "mock"

    def get_cors_origins(self) -> List[str]:
        if not self.ALLOWED_CORS_ORIGINS:
            return []
        return [origin.strip() for origin in self.ALLOWED_CORS_ORIGINS.split(",")]

settings = Settings()
