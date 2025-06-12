from src.metrics.repository import MetricsRepository

class MetricsService:
    """Service for managing document processing metrics.

    This service provides a high-level interface for working with metrics,
    including retrieving aggregated statistics and saving new metrics records.
    It acts as a facade for the MetricsRepository, providing additional
    business logic if needed.
    """

    def __init__(self):
        """Initialize the MetricsService with required repository."""
        self.repository = MetricsRepository()

    async def get_metrics(self):
        """Get aggregated processing metrics.

        This method retrieves various statistics about document processing
        from the repository, including processing times and file counts.

        Returns:
            dict: Dictionary containing the following metrics:
                - files_processed (int): Total number of processed files
                - min_time_processed (float): Minimum processing time in seconds
                - avg_time_processed (float): Average processing time in seconds
                - max_time_processed (float): Maximum processing time in seconds
                - latest_file_processed_timestamp (float | None): Processing time of the last file
        """
        return await self.repository.get_metrics()
    
    async def save_metrics(self, metrics):
        """Save new metrics record.

        This method saves a new metrics record to track document processing statistics.
        The metrics object should contain information about processing time, status,
        and other relevant statistics.

        Args:
            metrics: Metrics object containing processing statistics

        Returns:
            Metrics: Saved metrics object with database ID

        Raises:
            Exception: If database operation fails
        """
        return await self.repository.save_metrics(metrics)