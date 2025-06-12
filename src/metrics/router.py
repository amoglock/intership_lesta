import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from src.metrics.repository import MetricsRepository
from src.metrics.schemas import MetricsResponse, StatusResponse, VersionResponse
# from src.tf_idf.repository  import Repository


logger = logging.getLogger(__name__)

metrics_router = APIRouter(
    tags=["Metrics"],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error occurred",
        },
    },
)


@metrics_router.get(
    "/status",
    summary="Get service status",
    description="Check if the service is available and responding",
    response_model=StatusResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "Service is available and responding",
            "model": StatusResponse,
        },
    },
)
async def get_status():
    return StatusResponse


@metrics_router.get(
    "/version",
    summary="Get application version",
    description="Returns the current version of the application",
    response_model=VersionResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "Current application version",
            "model": VersionResponse,
        },
    },
)
async def get_version():
    return VersionResponse


@metrics_router.get(
    "/metrics",
    summary="Get processing metrics",
    description="Returns aggregated statistics about document processing, including processing times and file content lenght",
    response_model=MetricsResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "Processing metrics retrieved successfully",
            "model": MetricsResponse,
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Failed to retrieve processing metrics",
        },
    },
)
async def get_metrics(repository: Annotated[MetricsRepository, Depends()]):
    try:
        metrics = await repository.get_metrics()
        return MetricsResponse(**metrics)
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching metrics"
        )
