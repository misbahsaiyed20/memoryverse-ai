"""
Application configuration.

All environment-dependent values are loaded here via Pydantic Settings.
Nothing else in the codebase should call os.environ directly — import
`settings` from this module instead.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # General
    app_name: str = "MemoryVerse AI"
    environment: str = "development"

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/memoryverse"

    # CORS
    allowed_origins: str = "http://localhost:3000"

    # Firebase Admin SDK — path to the service account JSON downloaded from
    # Firebase Console. Not loaded until the first request that needs auth,
    # so the app still boots fine without it (e.g. for /health).
    firebase_credentials_path: str = "./firebase-service-account.json"

    # Local document storage — see app/services/storage/local.py
    upload_dir: str = "./uploads"

    # Gemini extraction (Sprint 6). Model name is configurable so a
    # future model rename/deprecation is a one-line env var change,
    # not a code change.
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash"

    # Vector storage (Sprint 7) — persistent local ChromaDB path.
    chroma_db_path: str = "./chromadb"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]


settings = Settings()
print("Gemini model =", settings.gemini_model)
