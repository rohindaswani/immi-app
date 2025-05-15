"""
Hardcoded configuration file with no .env dependency
"""

import secrets
from typing import List, Optional


class Settings:
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Immigration Advisor"
    
    # SECURITY
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SESSION_MAX_AGE: int = 14 * 24 * 60 * 60  # 14 days in seconds
    
    # CORS and Allowed Hosts - hardcoded
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    # DATABASE
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/immigration_advisor"
    MONGODB_URL: str = "mongodb://localhost:27017/immigration_advisor"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # ENVIRONMENT
    ENVIRONMENT: str = "development"
    
    # LOGGING
    LOG_LEVEL: str = "INFO"
    
    # FILE STORAGE
    STORAGE_BUCKET_NAME: Optional[str] = None
    STORAGE_ACCESS_KEY: Optional[str] = None
    STORAGE_SECRET_KEY: Optional[str] = None
    STORAGE_REGION: Optional[str] = None
    STORAGE_ENDPOINT: Optional[str] = None
    
    # RATE LIMITING
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # DEBUG
    DEBUG: bool = True
    
    # SERVICES
    PINECONE_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None


settings = Settings()