from datetime import datetime, UTC
from typing import List, Optional

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import JSON

class Analysis(SQLModel, table=True):
    __tablename__ = "analyses"

    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(nullable=False)
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    total_words: int = Field(default=0)
    original_text: str = Field(default="")
    filtered_words: List[str] = Field(default_factory=list, sa_type=JSON)
    
    # Relationship with results
    results: List["AnalysisResult"] = Relationship(back_populates="analysis", cascade_delete="all, delete-orphan")

class AnalysisResult(SQLModel, table=True):
    __tablename__ = "analysis_results"

    id: Optional[int] = Field(default=None, primary_key=True)
    analysis_id: int = Field(foreign_key="analyses.id")
    word: str = Field(nullable=False)
    tf: float = Field(nullable=False)
    
    # Relationship with analysis
    analysis: Optional["Analysis"] = Relationship(back_populates="results")
