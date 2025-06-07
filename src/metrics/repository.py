from sqlalchemy import func
from sqlmodel import Session, select

from src.database import engine


class MetricsRepository:

        def __init__(self):
            self.engine = engine

        # async def get_metrics(self) -> dict:
        #     """Get aggregated metrics from the database
                
        #         Returns:
        #             dict: Dictionary with metrics:
        #                 - files_processed (int): total number of processed files
        #                 - min_time_processed (float): minimum processing time
        #                 - avg_time_processed (float): average processing time
        #                 - max_time_processed (float): maximum processing time
        #                 - latest_file_processed_timestamp (float | None): processing time of the last file
        #     """
        #     with Session(self.engine) as session:
        #         query = select(
        #             func.count(AnalysisMetrics.id).label('files_processed'),
        #             func.min(AnalysisMetrics.processing_time).label('min_time'),
        #         func.avg(AnalysisMetrics.processing_time).label('avg_time'),
        #         func.max(AnalysisMetrics.processing_time).label('max_time'),
        #         AnalysisMetrics.processing_time.label('latest_time')
        #     ).where(
        #         AnalysisMetrics.status == 'completed'
        #     ).order_by(
        #         AnalysisMetrics.start_time.desc()
        #     ).limit(1)
            
        #     result = session.exec(query).first()
            
        #     if not result:
        #         return {
        #             "files_processed": 0,
        #             "min_time_processed": 0.0,
        #             "avg_time_processed": 0.0,
        #             "max_time_processed": 0.0,
        #             "latest_file_processed_timestamp": None
        #         }
            
        #     return {
        #         "files_processed": result.files_processed,
        #         "min_time_processed": round(result.min_time, 3) if result.min_time else 0.0,
        #         "avg_time_processed": round(result.avg_time, 3) if result.avg_time else 0.0,
        #         "max_time_processed": round(result.max_time, 3) if result.max_time else 0.0,
        #         "latest_file_processed_timestamp": round(result.latest_time, 3) if result.latest_time else None
        #     }
        
        # async def save_metrics(self, metrics):
        #     """Save metrics to the database
            
        #     Args:
        #         metrics (Metrics): Metrics object
                
        #     Returns:
        #         Metrics: Saved metrics object
        #     """
        # try:
        #     with Session(self.engine) as session:
        #         session.add(metrics)
        #         session.commit()
        #         session.refresh(metrics)
        #         return metrics
        # except Exception as e:
        #     session.rollback()
        #     logger.error(f"Error saving metrics: {e}")
        #     raise