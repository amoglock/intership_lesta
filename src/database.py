import os
from sqlmodel import SQLModel, create_engine
from sqlalchemy.exc import SQLAlchemyError
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Create database directory if it doesn't exist
os.makedirs("data", exist_ok=True)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DEBUG else {}
)

# Create database tables
def create_db_and_tables() -> None:
    """Create tables in the database"""
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except SQLAlchemyError as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise
    