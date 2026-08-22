import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        case_sensitive=True,
    )

    PROJECT_NAME: str = "AIMedical - Agentic AI Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # JWT Auth settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "aimedical_super_secret_jwt_key_2026_agentic_ai_medical")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Gemini API settings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL_NAME: str = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash")
    GEMINI_STT_MODEL_NAME: str = os.getenv("GEMINI_STT_MODEL_NAME", "gemini-2.0-flash")
    MAX_AUDIO_UPLOAD_BYTES: int = int(os.getenv("MAX_AUDIO_UPLOAD_BYTES", str(25 * 1024 * 1024)))
    
    # LangGraph SQLite Checkpointer settings
    CHECKPOINT_DB_PATH: str = os.getenv("CHECKPOINT_DB_PATH", str(BACKEND_DIR / "checkpoints.db"))

settings = Settings()
