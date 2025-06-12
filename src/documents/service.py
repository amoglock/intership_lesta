from datetime import UTC, datetime, timezone
import logging
import os
from pathlib import Path
from typing import List

from fastapi import HTTPException, UploadFile, status

from src.collections.repository import CollectionsRepository
from src.core.config import settings
from src.documents.repository import DocumentsRepository
from src.documents.schemas import DocumentContent, DocumentInDB
from src.metrics.repository import MetricsRepository
from src.models import Document, Metrics
from src.tf_idf.processor import TFIDFProcessor
from src.tf_idf.schemas import DocumentStatistics
from src.users.schemas import UserResponse


class DocumentsService:
    """Service for managing documents and their content.

    This service handles business logic for documents, including:
    - Uploading and storing documents
    - Managing document content in database and file system
    - Retrieving document content and metadata
    - Calculating document statistics
    - Managing document lifecycle (create, read, delete)
    """

    def __init__(self):
        """Initialize the DocumentsService with required repositories and processors."""
        self.logger = logging.getLogger(__name__)
        self.repository = DocumentsRepository()
        self.processor = TFIDFProcessor()
        self.collections = CollectionsRepository()
        self.metrics = MetricsRepository()
        self.max_content_size = settings.MAX_DB_CONTENT_SYMBOLS

    async def delete_document(self, document_id, user: UserResponse) -> None:
        """Delete a document and its associated file.

        Args:
            document_id (int): ID of the document to delete
            user (UserResponse): User who owns the document

        Raises:
            NoResultFound: If document doesn't exist or user doesn't have access
            FileNotFoundError: If document file cannot be found
        """
        document = await self.repository.get_one_or_all_documents(
            document_id=document_id,
            user_id=user.id,
        )
        await self.repository.delete_document(document=document)
        await self.delete_file_from_store(file_path=document.file_path)

    async def delete_file_from_store(self, file_path: str) -> None:
        """Delete a file from the storage system.

        Args:
            file_path (str): Path to the file to be deleted

        Note:
            This method silently succeeds if the file doesn't exist.
        """
        if os.path.exists(file_path):
            os.remove(file_path)
        self.logger.info(f"Document {file_path} removed success")

    async def get_document(self, document_id: int, user_id: int) -> Document:
        """Get a document by its ID.

        Args:
            document_id (int): ID of the document to retrieve
            user_id (int): ID of the user requesting the document

        Returns:
            Document: The requested document

        Raises:
            NoResultFound: If document doesn't exist or user doesn't have access
        """
        document = await self.repository.get_one_or_all_documents(
            document_id=document_id,
            user_id=user_id,
        )
        return document

    async def get_documents(self, user: UserResponse) -> Document | List[DocumentInDB]:
        """Get all documents owned by a user.

        Args:
            user (UserResponse): User whose documents to retrieve

        Returns:
            List[DocumentInDB]: List of documents owned by the user
        """
        documents = await self.repository.get_one_or_all_documents(user_id=user.id)
        return documents

    async def get_document_statistics(
        self, collection_id: int, document_id: int, user: UserResponse
    ) -> DocumentStatistics:
        """Get TF-IDF statistics for a document within its collection.

        Args:
            collection_id (int): ID of the collection containing the document
            document_id (int): ID of the document to analyze
            user (UserResponse): User requesting the statistics

        Returns:
            DocumentStatistics: TF-IDF statistics for the document

        Raises:
            HTTPException: If document is not in the specified collection
            NoResultFound: If document or collection doesn't exist
        """
        metrics = Metrics()

        # Get document and collection
        collection = await self.collections.get_collection_by_id(
            collection_id=collection_id,
            user_id=user.id,
        )
        document = await self.get_document(document_id=document_id, user_id=user.id)

        # Check if document is in collection
        if document not in collection.documents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document is not in collection",
            )

        collection_texts = []
        for doc in collection.documents:
            collection_texts.append(
                doc.content
                if doc.content
                else await self.get_file_content(doc.file_path)
            )

        statistics = await self.processor.document_statistics(
            document_content=document.content, collection_content=collection_texts
        )
        return DocumentStatistics(
            **{
                "document": document_id,
                "collection": collection_id,
                "tf_idf": statistics,
            }
        )

    async def get_document_with_content(
        self, document_id: int, user: UserResponse
    ) -> DocumentContent:
        """Get a document with its content.

        This method retrieves the document content either from the database
        if it's stored there, or from the file system if it's not.

        Args:
            document_id (int): ID of the document to retrieve
            user (UserResponse): User requesting the document

        Returns:
            DocumentContent: Document with its content

        Raises:
            NoResultFound: If document doesn't exist or user doesn't have access
            FileNotFoundError: If document file cannot be found
        """
        document = await self.get_document(document_id=document_id, user_id=user.id)

        # Use the content if it is in the database.
        if document.content:
            return DocumentContent.model_validate(document)
        else:
            # Read from file
            content = await self.get_file_content(document.file_path)

        return DocumentContent.model_validate(document, content=content)

    async def get_file_content(self, file_path: str) -> str:
        """Read content from a file.

        Args:
            file_path (str): Path to the file to read

        Returns:
            str: Content of the file

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file cannot be read
        """
        with open(file_path, "r") as file:
            content = file.read()
        return content

    async def save_document_to_database(
        self, uploaded_file: Document, owner: UserResponse
    ) -> Document:
        """Save document metadata to database.

        Args:
            uploaded_file (Document): Document metadata to save
            owner (UserResponse): User who owns the document

        Returns:
            Document: Saved document with its database ID

        Raises:
            Exception: If database operation fails
        """
        uploaded_file.owner_id = owner.id
        return await self.repository.add_document(uploaded_file=uploaded_file)

    async def upload_document_to_store(self, file: UploadFile) -> Document:
        """Upload file to storage and save content to database if it's a text file.

        This method:
        1. Generates a unique filename
        2. Saves the file to the storage system
        3. Attempts to store the content in the database if it's a text file
        4. Creates a document record with metadata

        Args:
            file (UploadFile): File to upload

        Returns:
            Document: Created document instance with metadata

        Raises:
            HTTPException: If file is empty
            Exception: If file upload or processing fails
        """
        try:
            # Generate file metadata
            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{timestamp}_{file.filename}"
            file_path = str(Path(settings.UPLOAD_DIR) / unique_filename)

            # Read and save file
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)

            # Store content in DB
            document_content = None
            try:
                document_content = content.decode("utf-8")
                content_lenght = len(document_content)
                if content_lenght == 0:
                    raise HTTPException(detail="File cannot be empty")
                if content_lenght > self.max_content_size:
                    document_content = None
                    self.logger.warning(
                        f"File {file.filename} content is too large "
                        f"({len(document_content)} characters) "
                        "to store in database"
                    )
            except UnicodeDecodeError:
                self.logger.warning(f"File {file.filename} is not a valid text file")

            # Create document record
            document = Document(
                filename=file.filename,
                unique_filename=unique_filename,
                file_path=file_path,
                content=document_content,
                content_length=content_lenght,
            )

            return document

        except Exception as e:
            self.logger.error(f"Error uploading file: {str(e)}")
            raise
