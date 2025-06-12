from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.core.config import settings


class StatusResponse(BaseModel):
    """Response model for service status endpoint.
    
    This model represents the current status of the service.
    """
    status: str = "ok"


class VersionResponse(BaseModel):
    """Response model for application version endpoint.
    
    This model contains information about the current version of the application.
    """
    version: str = settings.APP_VERSION


class MetricsResponse(BaseModel):
    """Response model for processing metrics endpoint.
    
    This model contains aggregated statistics about document processing operations.
    
    Attributes:
        files_processed (int): Total number of successfully processed files
        min_time_processed (float): Minimum processing time in seconds
        avg_time_processed (float): Average processing time in seconds
        max_time_processed (float): Maximum processing time in seconds
        latest_file_processed_timestamp (float | None): Processing time of the last file in seconds, or None if no files processed
        max_content_length (int): Maximum content length in characters across all processed files
        avg_content_length (float): Average content length in characters across all processed files
    """
    files_processed: int
    min_time_processed: float
    avg_time_processed: float
    max_time_processed: float
    latest_file_processed_timestamp: float | None
    max_content_length: int
    avg_content_length: float
        