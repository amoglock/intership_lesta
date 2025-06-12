from datetime import UTC, datetime, timezone
import logging
from pathlib import Path
from typing import List
import json

from fastapi import HTTPException, UploadFile, status
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

from src.collections.repository import CollectionsRepository
from src.core.config import settings
from src.documents.repository import DocumentsRepository
from src.documents.schemas import DocumentContent, DocumentInDB
from src.metrics.repository import MetricsRepository
from src.models import Document, Metrics, User
from src.tf_idf.processor import TFIDFProcessor
from src.users.schemas import UserResponse


class DocumentsService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.repository = DocumentsRepository()
        self.processor = TFIDFProcessor()
        self.collections = CollectionsRepository()
        self.metrics = MetricsRepository()
        self.max_content_size = settings.MAX_DB_CONTENT_SYMBOLS

    async def delete_document(self, document_id, user: UserResponse) -> None:
        """ """
        document = await self.repository.get_one_or_all_documents(
            document_id=document_id,
            user_id=user.id,
        )
        await self.repository.delete_document(document=document)

    async def get_document(self, document_id: int, user_id: int) -> Document:
        """ """
        document = await self.repository.get_one_or_all_documents(
            document_id=document_id,
            user_id=user_id,
        )
        return document

    async def get_documents(self, user: UserResponse) -> Document | List[DocumentInDB]:
        """ """
        documents = await self.repository.get_one_or_all_documents(user_id=user.id)
        return documents

    async def get_document_statistics(
        self, collection_id: int, document_id: int, user: UserResponse
    ):
        """Get document statistics.

        Strategy:
        1. Try to get cached statistics from document
        2. If not found, calculate and update document
        3. Return statistics
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

        # Try to get cached statistics
        if document.tf_vector:
            self.logger.info(f"Using cached statistics for document {document_id}")
            return {
                "tf_vector": json.loads(document.tf_vector),
            }

        # If no cached statistics, calculate them
        self.logger.info(f"Calculating statistics for document {document_id}")

        # Get document content
        if document.content:
            current_doc_content = document.content
        else:
            current_doc_content = await self.get_file_content(document.file_path)

        # Calculate TF statistics
        tf_stats = await self.processor.document_statistics(current_doc_content)

        # Update document with statistics
        document.tf_vector = json.dumps(tf_stats["tf_vector"])
        document.word_count = tf_stats["word_count"]
        document.unique_words = tf_stats["unique_words"]
        document.stats_updated_at = datetime.now(UTC)

        await self.repository.update_document(document)

        # Update metrics
        metrics.end_time = datetime.now(UTC)
        metrics.processing_time = (
            metrics.end_time - metrics.start_time
        ).total_seconds()
        metrics.status = "completed"
        await self.metrics.save_metrics(metrics)

        return tf_stats

    # async def get_collection_statistics(self, collection_id: int):
    #     """Get collection statistics.

    #     Strategy:
    #     1. Try to get cached statistics from collection
    #     2. If not found, calculate and update collection
    #     3. Return statistics
    #     """
    #     # Get collection
    #     collection = await self.collections.get_collection_by_id(
    #         collection_id=collection_id
    #     )

    #     # Try to get cached statistics
    #     if collection.idf_vector is not None:
    #         self.logger.info(f"Using cached statistics for collection {collection_id}")
    #         return {
    #             "idf_vector": json.loads(collection.idf_vector),
    #             "total_documents": collection.total_documents,
    #             "total_words": collection.total_words,
    #             "vocabulary": json.loads(collection.vocabulary),
    #         }

    #     # If no cached statistics, calculate them
    #     self.logger.info(f"Calculating statistics for collection {collection_id}")

    #     # Get all documents content
    #     documents_content = []
    #     for doc in collection.documents:
    #         if doc.content:
    #             content = doc.content
    #         else:
    #             content = await self.get_file_content(doc.file_path)
    #         documents_content.append(content)

    #     # Calculate IDF statistics
    #     idf_stats = await self.processor.calculate_idf(documents_content)

    #     # Update collection with statistics
    #     collection.idf_vector = json.dumps(idf_stats["idf_vector"])
    #     collection.total_documents = idf_stats["total_documents"]
    #     collection.total_words = idf_stats["total_words"]
    #     collection.vocabulary = json.dumps(idf_stats["vocabulary"])
    #     collection.stats_updated_at = datetime.now(UTC)

    #     await self.collections.update_collection(collection)

    #     return idf_stats

    async def get_document_with_content(
        self, document_id: int, user: UserResponse
    ) -> DocumentContent:
        """Get document with its content.

        Returns:
            DocumentContent: Document with content from DB if available, otherwise from file
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
        """ """
        with open(file_path, "r") as file:
            content = file.read()
        return content

    async def save_document_to_database(
        self, uploaded_file: Document, owner: UserResponse
    ) -> Document:
        """
        Save document metadata to database.

        Args:
            uploaded_file (Document): Document metadata
            owner (User): Document owner

        Returns:
            Document: Saved document with metadata
        """
        uploaded_file.owner_id = owner.id
        return await self.repository.add_document(uploaded_file=uploaded_file)

    async def upload_document_to_store(self, file: UploadFile) -> Document:
        """Upload file to storage and save content to database if it's a text file.

        Args:
            file (UploadFile): File to upload

        Returns:
            Document: Created document instance
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
