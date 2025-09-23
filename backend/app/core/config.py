"""Application configuration settings."""

import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "postgresql://secre:secre@localhost:5432/secre_db"
    database_url_test: str = "postgresql://secre:secre@localhost:5433/secre_db_test"
    
    # Railway will provide DATABASE_URL environment variable
    @property
    def effective_database_url(self) -> str:
        """Get the effective database URL, preferring Railway's DATABASE_URL."""
        return os.getenv("DATABASE_URL", self.database_url)
    
    # API
    api_v1_prefix: str = "/v1"
    project_name: str = "Secre API"
    version: str = "1.0.0"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    master_api_key: str = "hPoRkL0mz91Ui3sPTsFflbBUPvpHC67TdNC4ytGw19evzSRRlfn9To8LmL89b5wP"
    
    # Logging
    log_level: str = "INFO"
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # Railway port configuration
    @property
    def port(self) -> int:
        """Get the port from Railway's PORT environment variable."""
        return int(os.getenv("PORT", "8000"))
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
