from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

BACKEND_DIR = Path(__file__).resolve().parents[2]
ROOT_DIR = BACKEND_DIR.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "GeoGround API"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Google Earth Engine
    GEE_PROJECT_ID: str
    GEE_SERVICE_ACCOUNT_KEY_PATH: str | None = None

    # CORS React
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Database (PostgreSQL + PostGIS)
    DATABASE_URL: str = Field(
        default="postgresql+psycopg2://geoground:geoground@localhost:5432/geoground",
        description="PostgreSQL + PostGIS connection string",
    )
    DB_ECHO: bool = Field(default=False)

    # LLM Integration (Google Gemini via google-genai)
    GEMINI_API_KEY: str | None = None
    LLM_MODEL_GEMINI: str = "gemini-2.5-flash"
    LLM_TIMEOUT_SECONDS: float = 15.0

    model_config = SettingsConfigDict(
        env_file=(BACKEND_DIR / ".env", ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()