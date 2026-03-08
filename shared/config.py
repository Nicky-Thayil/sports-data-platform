"""
Shared configuration for the application.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    API_KEY_SECRET: str
    API_FOOTBALL_KEY: str
    ENVIRONMENT: str = "development"
    RATE_LIMIT_PER_MINUTE: int = 60
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()