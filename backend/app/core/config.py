"""Application configuration settings."""

import os
from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "postgresql://secre:secre@localhost:5432/secre_db"
    database_url_test: str = "postgresql://secre:secre@localhost:5433/secre_db_test"
    
    # API
    api_v1_prefix: str = "/v1"
    project_name: str = "Secre API"
    version: str = "1.0.0"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Logging
    log_level: str = "INFO"
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
