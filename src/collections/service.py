from src.collections.repository import CollectionsRepository
from src.collections.schemas import CollectionResponse, DocumentInCollection
from src.documents.repository import DocumentsRepository
from src.documents.service import DocumentsService
from src.tf_idf.processor import TFIDFProcessor


class CollectionsService:
    """Service for managing collections and their documents.
    
    This service handles business logic for collections, including:
    - Creating and managing collections
    - Adding/removing documents to/from collections
    - Getting collection statistics
    """

    def __init__(self):
        self.repository = CollectionsRepository()
        self.documents_repository = DocumentsRepository()
        self.documents_sevice = DocumentsService()
        self.processor = TFIDFProcessor()

    async def add_document_to_collection(
        self, collection_id: int, document_id: int
    ) -> None:
        """Add a document to a collection.
        
        Args:
            collection_id: ID of the collection to add document to
            document_id: ID of the document to add
            
        Raises:
            NoResultFound: If collection or document doesn't exist
        """
        collection = await self.repository.get_collection_by_id(collection_id)
        document = await self.documents_repository.get_one_or_all_documents(document_id)
        await self.repository.add_document_to_collection(collection, document)

    async def create_collection(self) -> CollectionResponse:
        """Create a new collection.
        
        Returns:
            CollectionResponse: Created collection
        """
        return await self.repository.create_collection()

    async def collection(self, collection_id: int) -> list[DocumentInCollection]:
        """Get all documents in a collection.
        
        Args:
            collection_id: ID of the collection to get documents from
            
        Returns:
            list[DocumentInCollection]: List of documents in the collection
            
        Raises:
            NoResultFound: If collection doesn't exist
        """
        collection = await self.repository.get_collection_by_id(collection_id)
        return collection.documents

    async def collections(self) -> list[CollectionResponse]:
        """Get all collections with their documents.
        
        Returns:
            list[CollectionResponse]: List of all collections with their documents
        """
        return await self.repository.get_all_collections()

    async def delete_document(self, collection_id: int, document_id: int) -> None:
        """Remove a document from a collection.
        
        Args:
            collection_id: ID of the collection to remove document from
            document_id: ID of the document to remove
            
        Raises:
            NoResultFound: If collection or document doesn't exist
        """
        collection = await self.repository.get_collection_by_id(collection_id)
        document = await self.documents_repository.get_one_or_all_documents(document_id)
        await self.repository.remove_document_from_collection(collection, document)

    async def get_collection_statistics(self, collection_id: int) -> dict:
        """Get TF-IDF statistics for all documents in a collection.
        
        Args:
            collection_id: ID of the collection to get statistics for
            
        Returns:
            dict: TF-IDF statistics for the collection
            
        Raises:
            NoResultFound: If collection doesn't exist
        """
        collection_texts = []
        collection = await self.repository.get_collection_by_id(
            collection_id=collection_id
        )
        for doc in collection.documents:
            content = await self.documents_sevice.get_file_content(doc.file_path)
            collection_texts.append(content)

        return await self.processor.collection_statictics(collection_texts)