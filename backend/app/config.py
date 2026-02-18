"""
Application configuration using Pydantic Settings
"""
import json
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 0
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "IncluTalk"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = '["http://localhost:3000","http://localhost:5173"]'
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        # si viene ya como lista (por default), ok
        if isinstance(v, list):
            return v

        # si viene como string desde .env
        if isinstance(v, str):
            v = v.strip()
            # JSON string: ["http://...","http://..."]
            if v.startswith("["):
                return json.loads(v)
            # CSV: http://a,http://b
            return [x.strip() for x in v.split(",") if x.strip()]

        return v
    
    # Redis
    REDIS_URL: Optional[str] = None
    REDIS_ENABLED: bool = False
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # ML
    ML_MODEL_PATH: str = "app/ml/models/lsp_model.h5"
    ML_DEMO_MODE: bool = False
    ML_CONFIDENCE_THRESHOLD: float = 0.30
    ML_SEQUENCE_LENGTH: int = 30
    ML_FEATURE_DIM: int = 126
    
    # STT
    WHISPER_MODEL_SIZE: str = "base"
    WHISPER_ENABLED: bool = False
    STT_DEMO_MODE: bool = True
    
    # Session
    SESSION_TIMEOUT_MINUTES: int = 30
    MAX_SESSION_TURNS: int = 100
    
    # Privacy
    SAVE_CONVERSATION_TEXT: bool = False
    SAVE_AUDIO_VIDEO: bool = False
    COLLECT_METRICS: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"
    
    # Superadmin
    SUPERADMIN_EMAIL: str = "admin@inclutalk.com"
    SUPERADMIN_PASSWORD: str = "ChangeThisPassword123!"


settings = Settings()
