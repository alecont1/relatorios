from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "SmartHand"
    app_version: str = "0.1.0"
    debug: bool = False

    # Database
    database_url: str = Field(..., description="PostgreSQL connection URL")

    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:5173"],
        description="Allowed CORS origins"
    )

    # Cloudflare R2 Storage
    r2_endpoint_url: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = "smarthand-photos"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT Authentication
    jwt_secret_key: str = Field(..., description="Secret key for JWT signing (required)")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()
