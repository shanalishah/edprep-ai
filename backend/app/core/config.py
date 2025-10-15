"""
Core configuration settings for IELTS Master Platform
"""

from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # App Info
    APP_NAME: str = "IELTS Master Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/ielts_master"
    REDIS_URL: str = "redis://localhost:6379"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "https://*.vercel.app",
        "https://edprep-ai.vercel.app",
        "https://ielts-master-platform.vercel.app"
    ]
    
    # ML Models
    MODELS_DIR: str = "/Users/shan/Desktop/Work/Projects/EdPrep AI/ielts-master-platform/backend/models"
    USE_ML_MODELS: bool = True
    FALLBACK_TO_RULE_BASED: bool = True
    
    # AI/LLM Settings
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    USE_AI_FEEDBACK: bool = True
    
    # Analytics
    ENABLE_ANALYTICS: bool = True
    ANALYTICS_RETENTION_DAYS: int = 365
    
    # Gamification
    ENABLE_GAMIFICATION: bool = True
    POINTS_PER_ESSAY: int = 10
    BONUS_POINTS_THRESHOLD: float = 7.0
    
    # Social Features
    ENABLE_SOCIAL_FEATURES: bool = True
    ENABLE_MENTORING: bool = True
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [".pdf", ".docx", ".txt"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
