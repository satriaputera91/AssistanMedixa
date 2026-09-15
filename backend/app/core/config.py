import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        case_sensitive=True,
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
    GEMINI_MODEL_NAME: str = "gemini-2.5-flash"
    GEMINI_STT_MODEL_NAME: str = "gemini-2.5-flash"
    MAX_AUDIO_UPLOAD_BYTES: int = 25 * 1024 * 1024
    
    # LangGraph SQLite Checkpointer settings
    CHECKPOINT_DB_PATH: str = str(BACKEND_DIR / "checkpoints.db")

settings = Settings()
