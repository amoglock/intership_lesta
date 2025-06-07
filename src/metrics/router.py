import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from src.metrics.schemas import MetricsResponse, StatusResponse, VersionResponse
# from src.tf_idf.repository  import Repository


logger = logging.getLogger(__name__)

metrics_router = APIRouter(
    tags=["Metrics"],
)


@metrics_router.get(
        "/status", 
        summary="Status endpoint for monitoring",
        response_description="Returns 'OK' if service is available",
        response_model=StatusResponse,
        )
async def get_status():
    """Status endpoint for monitoring."""
    return StatusResponse


@metrics_router.get(
        "/version", 
        summary="App version endpoint",
        response_description="Returns current app version",
        response_model=VersionResponse,
        )
async def get_version():
    """Version endpoint for monitoring"""
    return VersionResponse


# @metrics_router.get(
#         "/metrics",
#         tags=["Monitoring"],
#         summary="Get processing metrics",
#         response_description="Returns processing metrics",
#         response_model=MetricsResponse
#         )
# async def get_metrics(repository: Annotated[Repository, Depends()]):
#     """Get processing metrics
    
#     Returns:
#         MetricsResponse: Processing metrics including:
#             - files_processed: total number of processed files
#             - min_time_processed: minimum processing time
#             - avg_time_processed: average processing time
#             - max_time_processed: maximum processing time
#             - latest_file_processed_timestamp: processing time of the last file
            
#     Raises:
#         HTTPException: If there is an error while fetching metrics
#     """
#     try:
#         metrics = await repository.get_metrics()
#         return MetricsResponse(**metrics)
#     except Exception as e:
#         logger.error(f"Failed to get metrics: {e}")
#         if isinstance(e, HTTPException):
#             raise
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Internal server error while fetching metrics"
#         )
