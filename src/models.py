from datetime import datetime, UTC
from typing import List, Optional

from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    """User model representing application users.
    
    Attributes:
        id: Primary key
        username: Unique username
        hashed_password: Hashed password
        created_at: Timestamp when user was created
        is_active: Whether the user is active
    """
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    
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
        created_at: Timestamp when document was created
        reference_count: Number of collections referencing this document
        collections: List of collections containing this document
    """
    __tablename__ = "documents"

    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(nullable=False)
    unique_filename: str = Field(nullable=False, unique=True)
    file_path: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    reference_count: int = Field(default=1)
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
        documents: List of documents in this collection
    """
    __tablename__ = "collections"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    owner_id: int = Field(foreign_key="users.id")

    # Relationships
    documents: List[Document] = Relationship(
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
