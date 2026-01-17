# app/core/config.py
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr, SecretStr

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
        case_sensitive=True,
    )

    # --- Supabase ---
    SUPABASE_URL: str
    SUPABASE_JWT_SECRET: str
    SUPABASE_SERVICE_ROLE_KEY: str | None = None
    SUPABASE_ANON_KEY: str | None = None
    SUPABASE_KEY: str

    # --- Database / App ---
    DATABASE_URL: str | None = None
    LOG_LEVEL: str = "INFO"
    JWT_SECRET_KEY: str | None = None

    # # --- Firebase ---kanchitk-2025-08-12
    # FIREBASE_CREDENTIALS_PATH: str | None = None
    # FIREBASE_EMAIL: EmailStr | None = None
    # FIREBASE_PASSWORD: SecretStr | None = None
    # FIREBASE_WEB_API_KEY: str | None = None

@lru_cache()   # ✅ ต้องมีวงเล็บ
def get_settings() -> Settings:
    return Settings()
