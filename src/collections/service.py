from src.collections.repository import CollectionsRepository
from src.collections.schemas import CollectionResponse
from src.documents.repository import DocumentsRepository
from src.documents.service import DocumentsService
from src.tf_idf.processor import TFIDFProcessor


class CollectionsService:

    def __init__(self):
        self.repository = CollectionsRepository()
        self.documents_repository = DocumentsRepository()
        self.documents_sevice = DocumentsService()
        self.processor = TFIDFProcessor()

    async def add_document_to_collection(
        self, collection_id: int, document_id: int
    ) -> None:
        """ """
        collection = await self.repository.get_collection_by_id(collection_id)
        document = await self.documents_repository.get_one_or_all_documents(document_id)
        await self.repository.add_document_to_collection(collection, document)

    async def create_collection(self):
        """ """
        return await self.repository.create_collection()

    async def collection(self, collection_id: int) -> list:
        """ """
        collection = await self.repository.get_collection_by_id(collection_id)
        return collection.documents

    async def collections(self) -> list[CollectionResponse]:
        """ """
        return await self.repository.get_all_collections()

    async def delete_document(self, collection_id: int, document_id: int) -> None:
        """ """
        collection = await self.repository.get_collection_by_id(collection_id)
        document = await self.documents_repository.get_one_or_all_documents(document_id)
        await self.repository.remove_document_from_collection(collection, document)

    async def get_collection_statistics(self, collection_id):
        """ """
        collection_texts = []
        collection = await self.repository.get_collection_by_id(
            collection_id=collection_id
        )
        for doc in collection.documents:
                content = await self.documents_sevice.get_file_content(doc.file_path)
                collection_texts.append(content)

        return await self.processor.collection_statictics(collection_texts)