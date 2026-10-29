import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "AssistantMedixa - Agentic AI Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # JWT Auth settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "AssistantMedixa_super_secret_jwt_key_2026_agentic_ai_medical")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Generative AI API settings
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL_NAME: str = "gemini-3.8-flash"
    GEMINI_STT_MODEL_NAME: str = "gemini-3.8-flash"
    GEMINI_FALLBACK_MODELS: str = "gemini-3.5-flash-lite,gemini-3.7-flash,gemini-3.6-flash,gemini-3.5-flash,gemini-3.1-flash-lite,gemini-flash-latest,gemini-flash-lite-latest"
    MAX_AUDIO_UPLOAD_BYTES: int = 25 * 1024 * 1024
    
    # SatuSehat Integration settings
    SS_ENVIRONMENT: str = "sandbox"
    SS_ORGANIZATION_ID: str = ""
    SS_CLIENT_ID: str = ""
    SS_ClIENT_ID: str = ""
    SS_CLIENT_SECRET: str = ""

    # MongoDB Persistence settings
    MONGODB_HOST: str = "localhost"
    MONGODB_PORT: int = 27017
    MONGODB_USER: str = "medixa"
    MONGODB_PASSWORD: str = "admin2026"
    MONGODB_DATABASE: str = "assistant_medixa"
    MONGODB_AUTH_SOURCE: str = "assistant_medixa"
    MONGODB_URL: str = "mongodb://medixa:admin2026@localhost:27017/assistant_medixa?authSource=assistant_medixa"

    # LangGraph SQLite Checkpointer settings
    CHECKPOINT_DB_PATH: str = str(BACKEND_DIR / "checkpoints.db")

settings = Settings()
