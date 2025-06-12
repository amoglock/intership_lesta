from datetime import datetime, UTC
from typing import List, Optional

from sqlalchemy.dialects.postgresql import JSON
from sqlmodel import SQLModel, Field, Relationship

from src.tf_idf.schemas import WordStatistics


class User(SQLModel, table=True):
    """User model representing application users.
    
    Attributes:
        id: Primary key
        username: Unique username
        hashed_password: Hashed password
        created_at: Timestamp when user was created
    """
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    
    # Relationships
    collections: list["Collection"] = Relationship(back_populates="owner")
    documents: list["Document"] = Relationship(back_populates="owner")


class CollectionDocumentLink(SQLModel, table=True):
    """Link table for many-to-many relationship between Collection and Document.
    
    Attributes:
        collection_id: Foreign key to collections table
        document_id: Foreign key to documents table
        added_at: Timestamp when document was added to collection
    """
    __tablename__ = "collection_documents"

    collection_id: int = Field(foreign_key="collections.id", primary_key=True)
    document_id: int = Field(foreign_key="documents.id", primary_key=True)
    added_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Document(SQLModel, table=True):
    """Document model representing uploaded text files.
    
    Attributes:
        id: Primary key
        filename: Original filename
        unique_filename: Unique filename with timestamp
        file_path: Path to stored file
        content: Document text content
        created_at: Timestamp when document was created
        reference_count: Number of collections referencing this document
        
        # Statistics
        tf_vector: JSON string with Term Frequency vector
    """
    __tablename__ = "documents"

    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(nullable=False)
    unique_filename: str = Field(nullable=False, unique=True)
    file_path: str = Field(nullable=False)
    content: List[WordStatistics] = Field(nullable=True, sa_type=JSON)
    content_length: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    owner_id: int = Field(foreign_key="users.id")

    # Relationships
    collections: List["Collection"] = Relationship(
        back_populates="documents", link_model=CollectionDocumentLink
    )
    owner: "User" = Relationship(back_populates="documents")


class Collection(SQLModel, table=True):
    """Collection model representing groups of documents.
    
    Attributes:
        id: Primary key
        name: Collection name
        description: Optional collection description
        created_at: Timestamp when collection was created
        updated_at: Timestamp when collection was last updated
        
        # Statistics
        idf_vector: JSON string with Inverse Document Frequency vector
        total_documents: Number of documents in collection
        total_words: Total number of words in collection
        vocabulary: JSON string with all unique words in collection
        stats_updated_at: When statistics were last updated
    """
    __tablename__ = "collections"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    owner_id: int = Field(foreign_key="users.id")

    # Relationships
    documents: List["Document"] = Relationship(
        back_populates="collections", link_model=CollectionDocumentLink
    )
    owner: "User" = Relationship(back_populates="collections")


class Metrics(SQLModel, table=True):
    """Metrics model for tracking processing times and status.
    
    Attributes:
        id: Primary key
        start_time: When the process started
        end_time: When the process ended
        processing_time: Total processing time in seconds
        status: Current status of the process
    """
    __tablename__ = "metrics"

    id: Optional[int] = Field(default=None, primary_key=True)
    start_time: datetime = Field(default_factory=lambda: datetime.now(UTC))
    end_time: Optional[datetime] = Field(default=None)
    processing_time: Optional[float] = Field(default=None)
    status: str = Field(default="pending")     
