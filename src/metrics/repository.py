from fastapi import logger
from sqlalchemy import func
from sqlmodel import Session, select

from src.database import engine
from src.models import Metrics, Document


class MetricsRepository:
    """Repository for managing processing metrics in the database.

    This repository handles all database operations related to document processing metrics,
    including:
    - Retrieving aggregated metrics statistics
    - Saving new metrics records
    - Tracking processing times and statuses
    """

    def __init__(self):
        """Initialize the MetricsRepository with database engine."""
        self.engine = engine

    async def get_metrics(self) -> dict:
        """Get aggregated metrics from the database.

        This method retrieves various statistics about document processing:
        - Total number of processed files
        - Minimum, average, and maximum processing times
        - Timestamp of the last processed file
        - Maximum and average content lengths from processed documents

        Returns:
            dict: Dictionary containing the following metrics:
                - files_processed (int): Total number of successfully processed files
                - min_time_processed (float): Minimum processing time in seconds
                - avg_time_processed (float): Average processing time in seconds
                - max_time_processed (float): Maximum processing time in seconds
                - latest_file_processed_timestamp (float | None): Processing time of the last file
                - max_content_length (int): Maximum content length in characters from processed documents
                - avg_content_length (float): Average content length in characters from processed documents
        """
        with Session(self.engine) as session:
            # Query aggregated statistics for processing times
            stats_query = (
                select(
                    func.count(Metrics.id).label("files_processed"),
                    func.min(Metrics.processing_time).label("min_time"),
                    func.avg(Metrics.processing_time).label("avg_time"),
                    func.max(Metrics.processing_time).label("max_time"),
                )
                .where(Metrics.status == "completed")
            )

            # Query content length statistics from Document table
            content_stats_query = (
                select(
                    func.max(Document.content_length).label("max_content_length"),
                    func.avg(Document.content_length).label("avg_content_length"),
                )
            )

            # Query latest record
            latest_query = (
                select(Metrics.processing_time.label("latest_time"))
                .where(Metrics.status == "completed")
                .order_by(Metrics.start_time.desc())
                .limit(1)
            )

            try:
                stats = session.exec(stats_query).one()
                content_stats = session.exec(content_stats_query).one()
                latest_time = session.exec(latest_query).one()
            except Exception:
                # Return default values if no records found
                return {
                    "files_processed": 0,
                    "min_time_processed": 0.0,
                    "avg_time_processed": 0.0,
                    "max_time_processed": 0.0,
                    "latest_file_processed_timestamp": None,
                    "max_content_length": 0,
                    "avg_content_length": 0.0,
                }

            return {
                "files_processed": stats.files_processed or 0,
                "min_time_processed": round(stats.min_time, 3) if stats.min_time else 0.0,
                "avg_time_processed": round(stats.avg_time, 3) if stats.avg_time else 0.0,
                "max_time_processed": round(stats.max_time, 3) if stats.max_time else 0.0,
                "latest_file_processed_timestamp": (
                    round(latest_time, 3) if latest_time else None
                ),
                "max_content_length": content_stats.max_content_length or 0,
                "avg_content_length": round(content_stats.avg_content_length, 2) if content_stats.avg_content_length else 0.0,
            }

    async def save_metrics(self, metrics: Metrics) -> Metrics:
        """Save metrics to the database.

        This method saves a new metrics record to track document processing statistics.
        The metrics object should contain information about processing time, status,
        and other relevant statistics.

        Args:
            metrics (Metrics): Metrics object containing processing statistics

        Returns:
            Metrics: Saved metrics object with database ID

        Raises:
            Exception: If database operation fails
        """
        try:
            with Session(self.engine) as session:
                session.add(metrics)
                session.commit()
                session.refresh(metrics)
                return metrics
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving metrics: {e}")
            raise
