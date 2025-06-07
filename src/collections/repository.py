from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from src.collections.schemas import CollectionResponse, DocumentInCollection
from src.database import engine
from src.models import Collection, Document, CollectionDocumentLink


class CollectionsRepository:

    def __init__(self):
        self.engine = engine

    async def add_document_to_collection(
        self, collection: Collection, document: Document
    ) -> None:
        """ """
        with Session(self.engine) as session:
            collection.documents.append(document)
            session.add(collection)
            session.commit()

    async def create_collection(self) -> Collection:
        """ """
        with Session(self.engine) as session:
            collection = Collection(name="My collection")
            session.add(collection)
            session.commit()
            session.refresh(collection)
            return collection
        
    async def remove_document_from_collection(self, collection: Collection, document: Document):
        """ """
        with Session(self.engine) as session:
            collection.documents.remove(document)
            session.add(collection)
            session.commit()

    async def get_collection_by_id(self, collection_id: int) -> Collection:
        """ """
        with Session(self.engine) as session:
            template = (
                select(Collection)
                .where(Collection.id == collection_id)
                .options(selectinload(Collection.documents))
            )
            collection = session.exec(template).one()
            return collection

    async def get_all_collections(self) -> list[CollectionResponse]:
        """Get all collections with their documents.

        Returns:
            list[Collection]: List of all collections with their documents
        """
        with Session(self.engine) as session:
            template = select(Collection).options(selectinload(Collection.documents))
            collections = session.exec(template).all()

            return collections
