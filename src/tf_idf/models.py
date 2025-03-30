from typing import List, Tuple
from sqlmodel import SQLModel
from pydantic import BaseModel

from src.models import Analysis

class WordResult(BaseModel):
    word: str
    tf: float
    idf: float

class ResultModel(SQLModel):
    analysis: Analysis
    results: List[Tuple[str, float, float]]
    