from pydantic import BaseModel

from src.core.config import settings


class StatusResponse(BaseModel):
    """Response model for the `/status` endpoint.

    Indicates the current operational state of the service.

    Attributes:
        status: A string representing the service status. Defaults to "OK".
               Possible values:
               - "OK": Service is operational
    """
    status: str = "OK"

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "OK",
                },
            ]    
        }
    }


class VersionResponse(BaseModel):
    """Response model for the `/version` endpoint.

    Contains the current application version, fetched from settings.

    Attributes:
        version (str): The current version of the application (e.g., "v1.2.3").
                      Automatically populated from `settings.APP_VERSION`.
    """
    version: str = settings.APP_VERSION

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "version": "v0.1.0",
                }
            ]
        }
    }


class MetricsResponse(BaseModel):
    """"""
    files_processed: int
    min_time_processed: float
    avg_time_processed: float
    max_time_processed: float
    latest_file_processed_timestamp: float | None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "files_processed": 1,
                    "min_time_processed": 0.123,
                    "avg_time_processed": 0.123,
                    "max_time_processed": 0.123,
                    "latest_file_processed_timestamp": 0.123,
                }    
            ]
        }
    }
        