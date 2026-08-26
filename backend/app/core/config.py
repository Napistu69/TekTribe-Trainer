"""Application configuration using Pydantic Settings."""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Environment-based configuration."""
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/tektribe")
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Security
    secret_key: str = "change-me-in-production"
    session_ttl_hours: int = 24
    
    # Game settings
    lockdown_min_imprint: int = 0
    lockdown_min_care_actions: int = 0
    lockdown_min_days: int = 0
    imprint_max: int = 100
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
