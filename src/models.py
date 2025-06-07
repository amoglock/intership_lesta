from datetime import datetime, UTC
from typing import List, Optional

from sqlmodel import SQLModel, Field, Relationship


class CollectionDocumentLink(SQLModel, table=True):
    __tablename__ = "collection_documents"

    collection_id: int = Field(foreign_key="collections.id", primary_key=True)
    document_id: int = Field(foreign_key="documents.id", primary_key=True)
    added_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Document(SQLModel, table=True):
    __tablename__ = "documents"

    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(nullable=False)
    unique_filename: str = Field(nullable=False, unique=True)
    file_path: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    reference_count: int = Field(default=1)

    # Relationships
    collections: List["Collection"] = Relationship(
        back_populates="documents", link_model=CollectionDocumentLink
    )


class Collection(SQLModel, table=True):
    __tablename__ = "collections"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    documents: List[Document] = Relationship(
        back_populates="collections", link_model=CollectionDocumentLink
    )


# class User(SQLModel, table=True):
#     __tablename__ = "users"

#     id: Optional[int] = Field(default=None, primary_key=True)
#     username: str = Field(nullable=False, unique=True)
#     password_hash: str = Field(nullable=False)
#     created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
#     updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

#     # Связи
#     documents: List["Document"] = Relationship(back_populates="user")
#     collections: List["Collection"] = Relationship(back_populates="user")


# class DocumentStatistics(SQLModel, table=True):
#     __tablename__ = "document_statistics"

#     id: Optional[int] = Field(default=None, primary_key=True)
#     document_id: int = Field(foreign_key="documents.id")
#     collection_id: int = Field(foreign_key="collections.id")
#     created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
#     updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

#     # Связи
#     document: "Document" = Relationship(back_populates="statistics")
#     collection: "Collection" = Relationship(back_populates="statistics")
#     word_statistics: List["WordStatistics"] = Relationship(back_populates="document_statistics")


# class WordStatistics(SQLModel, table=True):
#     __tablename__ = "word_statistics"

#     id: Optional[int] = Field(default=None, primary_key=True)
#     document_statistics_id: int = Field(foreign_key="document_statistics.id")
#     word: str = Field(nullable=False)
#     tf: float = Field(nullable=False)  # Term Frequency
#     idf: float = Field(nullable=False)  # Inverse Document Frequency

#     # Связи
#     document_statistics: "DocumentStatistics" = Relationship(back_populates="word_statistics")


# class GlobalMetrics(SQLModel, table=True):
#     """Глобальные метрики приложения"""
#     __tablename__ = "global_metrics"

#     id: Optional[int] = Field(default=None, primary_key=True)
#     total_requests: int = Field(default=0)
#     total_analyses: int = Field(default=0)
#     created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
#     updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

# class AnalysisMetrics(SQLModel, table=True):
#     """Метрики для каждого анализа"""
#     __tablename__ = "analysis_metrics"

#     id: Optional[int] = Field(default=None, primary_key=True)
#     analysis_id: Optional[int] = Field(default=None, foreign_key="analyses.id")
#     start_time: datetime = Field(default_factory=lambda: datetime.now(UTC))
#     end_time: Optional[datetime] = Field(default=None)
#     processing_time: Optional[float] = Field(default=None)
#     status: str = Field(default="pending")

#     # Relationship with analysis
#     analysis: Optional["Analysis"] = Relationship(back_populates="metrics")

# class Analysis(SQLModel, table=True):
#     """Анализ текста"""
#     __tablename__ = "analyses"

#     id: Optional[int] = Field(default=None, primary_key=True)
#     filename: str = Field(nullable=False)
#     content: str = Field(nullable=False)
#     created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
#     total_words: int = Field(default=0)
#     original_text: str = Field(default="")
#     filtered_words: List[str] = Field(default_factory=list, sa_type=JSON)

#     # Relationship with results
#     results: List["AnalysisResult"] = Relationship(back_populates="analysis", cascade_delete="all, delete-orphan")
#     # Relationship with metrics
#     metrics: Optional[AnalysisMetrics] = Relationship(back_populates="analysis")

# class AnalysisResult(SQLModel, table=True):
#     """Результат анализа для одного слова"""
#     __tablename__ = "analysis_results"

#     id: Optional[int] = Field(default=None, primary_key=True)
#     analysis_id: int = Field(foreign_key="analyses.id")
#     word: str = Field(nullable=False)
#     tf: float = Field(nullable=False)

#     # Relationship with analysis
#     analysis: Analysis = Relationship(back_populates="results")
