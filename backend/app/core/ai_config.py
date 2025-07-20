import os
from typing import Optional


class AIConfig:
    """Configuration for AI services"""
    
    # OpenAI Configuration (if using OpenAI)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "500"))
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    
    # Anthropic Configuration (if using Claude)
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
    
    # General AI Configuration
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "openai")  # "openai", "anthropic", "local"
    AI_TIMEOUT: int = int(os.getenv("AI_TIMEOUT", "30"))  # seconds
    
    # Context Configuration
    MAX_CONTEXT_DOCUMENTS: int = int(os.getenv("MAX_CONTEXT_DOCUMENTS", "5"))
    MAX_CONTEXT_TRAVEL_MONTHS: int = int(os.getenv("MAX_CONTEXT_TRAVEL_MONTHS", "6"))
    DEADLINE_WARNING_DAYS: int = int(os.getenv("DEADLINE_WARNING_DAYS", "180"))
    
    # Safety and Compliance
    ENABLE_CONTENT_FILTERING: bool = os.getenv("ENABLE_CONTENT_FILTERING", "true").lower() == "true"
    LOG_AI_INTERACTIONS: bool = os.getenv("LOG_AI_INTERACTIONS", "true").lower() == "true"
    
    @classmethod
    def is_ai_enabled(cls) -> bool:
        """Check if AI services are properly configured"""
        if cls.AI_PROVIDER == "openai":
            return cls.OPENAI_API_KEY is not None
        elif cls.AI_PROVIDER == "anthropic":
            return cls.ANTHROPIC_API_KEY is not None
        elif cls.AI_PROVIDER == "local":
            return True  # Assume local model is available
        return False
    
    @classmethod
    def get_model_config(cls) -> dict:
        """Get model configuration based on provider"""
        if cls.AI_PROVIDER == "openai":
            return {
                "model": cls.OPENAI_MODEL,
                "max_tokens": cls.OPENAI_MAX_TOKENS,
                "temperature": cls.OPENAI_TEMPERATURE,
                "api_key": cls.OPENAI_API_KEY
            }
        elif cls.AI_PROVIDER == "anthropic":
            return {
                "model": cls.ANTHROPIC_MODEL,
                "max_tokens": 1000,  # Anthropic default
                "api_key": cls.ANTHROPIC_API_KEY
            }
        return {}