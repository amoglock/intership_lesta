from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Application settings"""
    # Basic settings
    APP_NAME: str = "TF-IDF Analyzer"
    DEBUG: bool = False
    API_VERSION: str = "v1"
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/tfidf.db"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Paths
    STATIC_DIR: str = "src/static"
    DATA_DIR: str = "data"
    
    class Config:
        env_file = ".env"

settings = Settings()

# Create necessary directories
os.makedirs(settings.DATA_DIR, exist_ok=True) 