from typing import List
from pydantic import BaseModel


class WordStatistics(BaseModel):
    word: str
    tf: float
    idf: float
    tfidf: float


class DocumentStatistics(BaseModel):
    document: int
    collection: int
    tf_idf : List[WordStatistics]
