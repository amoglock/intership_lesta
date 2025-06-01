from typing import List, Tuple, Dict, Optional
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from src.models import Analysis, AnalysisResult, Metrics
from src.database import engine
import logging

logger = logging.getLogger(__name__)

class Repository:
    def __init__(self):
        self.engine = engine
    
    async def get_word_document_counts(self, words: set[str]) -> Dict[str, int]:
        """Get the number of documents for each word
        
        Args:
            words (set[str]): Set of words to count
            
        Returns:
            Dict[str, int]: Dictionary {word: document_count}
        """
        try:
            with Session(self.engine) as session:
                # Get all documents
                query = select(Analysis)
                analyses = session.exec(query).all()
                
                # Count the number of documents for each word
                counts = {}
                for word in words:
                    count = 0
                    for analysis in analyses:
                        if word in analysis.filtered_words:
                            count += 1
                    counts[word] = count
                return counts
        except Exception as e:
            logger.error(f"Error getting word document counts: {e}")
            raise
    
    async def get_total_documents(self) -> int:
        """Get the total number of documents in the database
        
        Returns:
            int: Total number of documents
        """
        try:
            with Session(self.engine) as session:
                query = select(func.count()).select_from(Analysis)
                return session.exec(query).first() or 0
        except Exception as e:
            logger.error(f"Error getting total documents: {e}")
            raise
    
    async def get_recent_analyses(self, limit: int = 5) -> List[Analysis]:
        """Get recent analyses
        
        Args:
            limit (int, optional): Number of analyses. Defaults to 5.
            
        Returns:
            List[Analysis]: List of recent analyses
        """
        try:
            with Session(self.engine) as session:
                query = select(Analysis).order_by(Analysis.created_at.desc()).limit(limit)
                return session.exec(query).all()
        except Exception as e:
            logger.error(f"Error getting recent analyses: {e}")
            raise
    
    async def save_result_to_db(self, analysis: Analysis, results: List[Tuple[str, float]]) -> Analysis:
        """Save analysis results to the database
        
        Args:
            analysis (Analysis): Analysis object
            results (List[Tuple[str, float]]): List of tuples (word, tf)
            
        Returns:
            Analysis: Saved analysis object
            
        Raises:
            ValueError: If the results list is empty
            IntegrityError: On database integrity error
        """
        if not results:
            raise ValueError("Results list cannot be empty")
            
        try:
            with Session(self.engine) as session:
                # Save words to filtered_words
                analysis.filtered_words = [word for word, _ in results]
                
                # Save analysis
                session.add(analysis)
                session.flush()
                
                # Create and save results
                analysis_results = [
                    AnalysisResult(
                        analysis_id=analysis.id,
                        word=word,
                        tf=tf
                    ) for word, tf in results
                ]
                
                session.add_all(analysis_results)
                session.commit()
                
                # Log saving information
                logger.info(f"Analysis saved with ID {analysis.id}")
                logger.info(f"Number of saved words: {len(analysis_results)}")
                
                # Get updated analysis object
                query = select(Analysis).where(Analysis.id == analysis.id)
                return session.exec(query).first()
                
        except IntegrityError as e:
            session.rollback()
            logger.error(f"Database integrity error: {e}")
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving results: {e}")
            raise
    
    async def get_analysis_by_id(self, analysis_id: int) -> Optional[Analysis]:
        """Get analysis by ID
        
        Args:
            analysis_id (int): Analysis ID
            
        Returns:
            Optional[Analysis]: Analysis object or None
        """
        try:
            with Session(self.engine) as session:
                query = select(Analysis).where(Analysis.id == analysis_id)
                return session.exec(query).first()
        except Exception as e:
            logger.error(f"Error getting analysis by ID: {e}")
            raise
    
    async def save_metrics(self, metrics: Metrics) -> Metrics:
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
            query = select(
                func.count(Metrics.id).label('files_processed'),
                func.min(Metrics.processing_time).label('min_time'),
                func.avg(Metrics.processing_time).label('avg_time'),
                func.max(Metrics.processing_time).label('max_time'),
                Metrics.processing_time.label('latest_time')
            ).where(
                Metrics.status == 'completed'
            ).order_by(
                Metrics.start_time.desc()
            ).limit(1)
            
            result = session.exec(query).first()
            
            if not result:
                return {
                    "files_processed": 0,
                    "min_time_processed": 0.0,
                    "avg_time_processed": 0.0,
                    "max_time_processed": 0.0,
                    "latest_file_processed_timestamp": None
                }
            
            return {
                "files_processed": result.files_processed,
                "min_time_processed": round(result.min_time, 3) if result.min_time else 0.0,
                "avg_time_processed": round(result.avg_time, 3) if result.avg_time else 0.0,
                "max_time_processed": round(result.max_time, 3) if result.max_time else 0.0,
                "latest_file_processed_timestamp": round(result.latest_time, 3) if result.latest_time else None
            }

