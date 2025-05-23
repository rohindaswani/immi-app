"""
A simplified configuration file for troubleshooting.
Rename this to config.py if you continue to have issues.
"""

import secrets
from typing import Dict, List, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True)
    
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Immigration Advisor"


    GOOGLE_CLIENT_SECRET: str = "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"
    GOOGLE_REDIRECT_URI: str = "/api/v1/auth/google/callback"
    
    # SECURITY
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SESSION_MAX_AGE: int = 14 * 24 * 60 * 60  # 14 days in seconds
    
    # CORS and Allowed Hosts - static setup for simplicity
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    # DATABASE
    DATABASE_URL: Optional[str] = None
    MONGODB_URL: str = "mongodb://localhost:27017/immigration_advisor"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # ENVIRONMENT
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # LOGGING
    LOG_LEVEL: str = "INFO"
    
    # RATE LIMITING
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # DEBUG
    DEBUG: bool = False


settings = Settings()