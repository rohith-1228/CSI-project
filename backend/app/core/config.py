"""Configuration settings for CyberSaathi backend."""

import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENVIRONMENT: str = Field(default="development", description="Environment mode: development or production")
    PORT: int = Field(default=8000, description="Server port")
    HOST: str = Field(default="0.0.0.0", description="Server host")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # Security & CORS
    CORS_ORIGINS: str = Field(
        default="http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173",
        description="Comma-separated allowed origins"
    )

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="Allowed analyze requests per IP per minute")

    # Request validation
    MAX_MESSAGE_LENGTH: int = Field(default=5000, description="Maximum characters allowed in submitted message")
    MIN_MESSAGE_LENGTH: int = Field(default=2, description="Minimum characters required for analysis")

    # Model paths
    MODEL_PATH: str = Field(
        default="models/cybersaathi_text_classifier_v1.joblib",
        description="Path to serialized joblib model"
    )
    MODEL_METADATA_PATH: str = Field(
        default="models/model_metadata.json",
        description="Path to model metadata JSON"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        if not self.CORS_ORIGINS:
            return ["*"]
        if self.CORS_ORIGINS.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()
