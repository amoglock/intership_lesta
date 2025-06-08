from datetime import datetime, timezone
import logging
import os


from fastapi import HTTPException, UploadFile
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

from src.collections.repository import CollectionsRepository
from src.core.config import settings
from src.documents.repository import DocumentsRepository
from src.documents.schemas import DocumentContent, DocumentInDB
from src.models import Document
from src.tf_idf.processor import TFIDFProcessor


class DocumentsService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.repository = DocumentsRepository()
        self.processor = TFIDFProcessor()
        self.collections = CollectionsRepository()
        

    async def delete_document(self, document_id) -> None:
        """ """
        document = await self.repository.get_one_or_all_documents(document_id=document_id)
        await self.repository.delete_document(document=document)


    async def get_document(self, document_id: int) -> Document:
        """ """
        document = await self.repository.get_one_or_all_documents(
            document_id=document_id
        )
        return document
        

    async def get_documents(self) -> list[DocumentInDB]:
        """ """
        documents = await self.repository.get_one_or_all_documents()
        return documents
    
    async def get_document_statistics(self, collection_id:int, document_id: int):
        """ """
        collection_texts = []
        collection = await self.collections.get_collection_by_id(collection_id=collection_id)
        document = await self.get_document(document_id=document_id)
        if document in collection.documents:
            for doc in collection.documents:
                content = await self.get_file_content(doc.file_path)
                collection_texts.append(content)
        current_doc_content = await self.get_file_content(document.file_path)
 

        return await self.processor.document_statistics(current_doc_content, collection_texts)


    
    async def get_document_with_content(self, document_id: int) -> DocumentContent:
        """ """
        document = await self.get_document(document_id=document_id)
        content = await self.get_file_content(document.file_path)
        document_dict = document.model_dump()
        return DocumentContent(**document_dict, content=content)

    async def file_validation(self, file: UploadFile) -> bool:
        """Validates file size, content type and file extension.

        Args:
            file (UploadFile): Uploaded file by form

        Returns:
            bool: True if validation is successful, otherwise False

        Note:
            Validates against:
            - settings.MAX_FILE_SIZE: Maximum allowed file size
            - settings.ALLOWED_FILE_TYPES: List of allowed MIME types
            - settings.ALLOWED_EXTENSIONS: List of allowed file extensions
        """
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            return False

        return (
            file.size <= settings.MAX_FILE_SIZE
            and file.content_type in settings.ALLOWED_FILE_TYPES
        )

    async def get_file_content(self, file_path: str) -> str:
        """ """
        with open(file_path, "r") as file:
            content = file.read()
        return content

    async def save_document_to_database(self, uploaded_file: Document) -> Document:
        """

        Args:
            uploaded_file (Document): _description_
        """
        return await self.repository.add_document(uploaded_file=uploaded_file)

    async def upload_document_to_store(self, file: UploadFile) -> Document:
        """Uploads a file to the storage and returns the document metadata.

        Args:
            file (UploadFile): File to be uploaded

        Returns:
            UploadedDocument: Document metadata containing filename and filepath

        Raises:
            FileNotFoundError: If file could not be saved to storage
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        original_filename = file.filename
        unique_filename = f"{timestamp}_{original_filename}"

        file_path = os.path.join(settings.DATA_DIR, unique_filename)

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        if not os.path.exists(file_path):
            raise FileNotFoundError("Failed to save file to storage")

        self.logger.info(f"{file.filename} was uploaded successfully")
        uploaded_file_data = Document(
            filename=original_filename,
            unique_filename=unique_filename,
            file_path=file_path,
        )

        return uploaded_file_data
