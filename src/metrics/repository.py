from fastapi import logger
from sqlalchemy import func
from sqlmodel import Session, select

from src.database import engine
from src.models import Metrics


class MetricsRepository:

    def __init__(self):
        self.engine = engine

    async def get_metrics(self) -> dict:
        """Get aggregated metrics from the database

        Returns:
            dict: Dictionary with metrics:
                - files_processed (int): total number of processed files
                - min_time_processed (float): minimum processing time
                - avg_time_processed (float): average processing time
                - max_time_processed (float): maximum processing time
                - latest_file_processed_timestamp (float | None): processing time of the last file
        """
        with Session(self.engine) as session:
            # 1. Запрос агрегированной статистики
            stats_query = (
                select(
                    func.count(Metrics.id).label("files_processed"),
                    func.min(Metrics.processing_time).label("min_time"),
                    func.avg(Metrics.processing_time).label("avg_time"),
                    func.max(Metrics.processing_time).label("max_time"),
                )
                .where(Metrics.status == "completed")
            )

            # 2. Запрос последней записи
            latest_query = (
                select(Metrics.processing_time.label("latest_time"))
                .where(Metrics.status == "completed")
                .order_by(Metrics.start_time.desc())
                .limit(1)
            )

            stats = session.exec(stats_query).one()
            latest_time = session.exec(latest_query).one()

            if not stats:
                return {
                    "files_processed": 0,
                    "min_time_processed": 0.0,
                    "avg_time_processed": 0.0,
                    "max_time_processed": 0.0,
                    "latest_file_processed_timestamp": None,
                }

            return {
                "files_processed": stats.files_processed,
                "min_time_processed": round(stats.min_time, 3) if stats.min_time else 0.0,
                "avg_time_processed": round(stats.avg_time, 3) if stats.avg_time else 0.0,
                "max_time_processed": round(stats.max_time, 3) if stats.max_time else 0.0,
                "latest_file_processed_timestamp": (
                    round(latest_time, 3) if latest_time else None
                ),
            }

    async def save_metrics(self, metrics):
        """Save metrics to the database

        Args:
            metrics (Metrics): Metrics object

        Returns:
            Metrics: Saved metrics object
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
