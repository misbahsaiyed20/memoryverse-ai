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

    # Database (connection config only — no models/migrations this sprint)
    database_url: str = "postgresql://postgres:postgres@localhost:5432/memoryverse"

    # CORS
    allowed_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]


settings = Settings()
