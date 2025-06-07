from src.metrics.repository import MetricsRepository

class MetricsService():

    def __init__(self):
        self.repository = MetricsRepository()

    async def get_metrics(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.repository.get_metrics()
    
    async def save_metrics(self):
        """
        
        """
        return self.repository.save_metrics()