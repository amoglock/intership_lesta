from typing import List
from src.collections.repository import CollectionsRepository
from src.collections.schemas import CollectionResponse, DocumentInCollection
from src.documents.repository import DocumentsRepository
from src.documents.service import DocumentsService
from src.models import Collection
from src.tf_idf.processor import TFIDFProcessor
from src.users.schemas import UserResponse


class CollectionsService:
    """Service for managing collections and their documents.

    This service handles business logic for collections, including:
    - Creating and managing collections
    - Adding/removing documents to/from collections
    - Getting collection statistics using TF-IDF analysis
    - Managing document content within collections
    """

    def __init__(self):
        """Initialize the CollectionsService with required repositories and services."""
        self.repository = CollectionsRepository()
        self.documents_repository = DocumentsRepository()
        self.documents_sevice = DocumentsService()
        self.processor = TFIDFProcessor()

    async def add_document_to_collection(
        self, collection_id: int, document_id: int, user: UserResponse
    ):
        """Add a document to a collection.

        Args:
            collection_id (int): ID of the collection to add document to
            document_id (int): ID of the document to add
            user (UserResponse): Current user making the request

        Raises:
            NoResultFound: If collection or document doesn't exist or user doesn't have access
        """
        collection = await self.repository.get_collection_by_id(
            collection_id=collection_id, user_id=user.id
        )
        document = await self.documents_repository.get_one_or_all_documents(
            document_id=document_id, user_id=user.id
        )
        await self.repository.add_document_to_collection(collection, document)

    async def create_collection(
        self, collection_name: str, user: UserResponse
    ) -> CollectionResponse:
        """Create a new collection for the user.

        Args:
            collection_name (str): Name of the collection to create
            user (UserResponse): Current user creating the collection

        Returns:
            CollectionResponse: Created collection with its metadata
        """
        return await self.repository.create_collection(
            collection_name=collection_name, user_id=user.id
        )

    async def collection(
        self, collection_id: int, user: UserResponse
    ) -> list[DocumentInCollection]:
        """Get all documents in a collection.

        Args:
            collection_id (int): ID of the collection to get documents from
            user (UserResponse): Current user requesting the documents

        Returns:
            list[DocumentInCollection]: List of documents in the collection with their metadata

        Raises:
            NoResultFound: If collection doesn't exist or user doesn't have access
        """
        collection = await self.repository.get_collection_by_id(
            collection_id=collection_id, user_id=user.id
        )
        return collection.documents

    async def collections(self, user: UserResponse) -> list[CollectionResponse]:
        """Get all collections owned by the user.

        Args:
            user (UserResponse): Current user requesting their collections

        Returns:
            list[CollectionResponse]: List of all collections owned by the user with their documents
        """
        return await self.repository.get_all_collections(user_id=user.id)

    async def delete_document(
        self, collection_id: int, document_id: int, user: UserResponse
    ) -> None:
        """Remove a document from a collection.

        Args:
            collection_id (int): ID of the collection to remove document from
            document_id (int): ID of the document to remove
            user (UserResponse): Current user making the request

        Raises:
            NoResultFound: If collection or document doesn't exist or user doesn't have access
        """
        collection = await self.repository.get_collection_by_id(
            collection_id=collection_id, user_id=user.id
        )
        document = await self.documents_repository.get_one_or_all_documents(
            document_id=document_id, user_id=user.id
        )
        await self.repository.remove_document_from_collection(collection, document)

    async def get_collection_content(self, collection: Collection) -> List[str]:
        """Get the content of all documents in a collection.

        This method retrieves the content of each document in the collection.
        If the document's content is not cached, it reads the content from the file.

        Args:
            collection (Collection): The collection to get content from

        Returns:
            List[str]: List of document contents in the collection
        """
        collection_texts = []
        # Collect all collection content
        for doc in collection.documents:
            collection_texts.append(
                doc.content
                if doc.content
                else await self.documents_sevice.get_file_content(doc.file_path)
            )
        return collection_texts

    async def get_collection_statistics(
        self, collection_id: int, user: UserResponse
    ) -> dict:
        """Get TF-IDF statistics for all documents in a collection.

        This method calculates TF-IDF statistics for all documents in the collection,
        which helps identify the most important words and their significance.

        Args:
            collection_id (int): ID of the collection to get statistics for
            user (UserResponse): Current user requesting the statistics

        Returns:
            dict: TF-IDF statistics for the collection, including word frequencies and importance scores

        Raises:
            NoResultFound: If collection doesn't exist or user doesn't have access
        """
        collection = await self.repository.get_collection_by_id(
            collection_id=collection_id, user_id=user.id
        )
        collection_texts = await self.get_collection_content(collection=collection)

        return await self.processor.collection_statictics(collection_texts)
