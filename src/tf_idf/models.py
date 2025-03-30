from typing import List, Tuple
from sqlmodel import SQLModel


from src.models import Analysis

class ResultModel(SQLModel):
    analysis: Analysis
    results: List[Tuple[str, float, float]]
    