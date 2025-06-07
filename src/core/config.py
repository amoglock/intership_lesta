from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path
import json
from .version import __version__

class Settings(BaseSettings):
    """Application settings"""
    # Basic settings
    APP_NAME: str = "TF-IDF Analyzer"
    APP_VERSION: str = __version__
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Paths
    STATIC_DIR: str = "src/frontend/static"
    DATA_DIR: str = "data"

    # App settings
    MAX_FILE_SIZE: int = 1_048_576
    ALLOWED_FILE_TYPES: List[str] = ["text/plain"]
    ALLOWED_EXTENSIONS: List[str]  = [".txt"]
    TOP_WORDS_COUNT: int = 50
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = str(Path(__file__).parent.parent.parent / ".env")
        env_file_encoding = "utf-8"
        case_sensitive = True

    def __init__(self, **values):
        super().__init__(**values)
        # ALLOWED_FILE_TYPES и CORS_ORIGINS можно задавать строкой через запятую или json
        if isinstance(self.ALLOWED_FILE_TYPES, str):
            try:
                self.ALLOWED_FILE_TYPES = json.loads(self.ALLOWED_FILE_TYPES)
            except Exception:
                self.ALLOWED_FILE_TYPES = [x.strip() for x in self.ALLOWED_FILE_TYPES.split(",") if x.strip()]
        if isinstance(self.CORS_ORIGINS, str):
            try:
                self.CORS_ORIGINS = json.loads(self.CORS_ORIGINS)
            except Exception:
                self.CORS_ORIGINS = [x.strip() for x in self.CORS_ORIGINS.split(",") if x.strip()]

    def validate_database_url(self) -> None:
        """
        Validate database URL. If not provided, raise an error.
        This is to ensure that the database URL is set.
        """
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL is required")


# Create settings instance
settings = Settings()
settings.validate_database_url()

# Create necessary directories
os.makedirs(settings.DATA_DIR, exist_ok=True) 