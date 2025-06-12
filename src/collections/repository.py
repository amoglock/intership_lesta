from typing import List

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from src.collections.schemas import CollectionResponse
from src.database import engine
from src.models import Collection, Document


class CollectionsRepository:
    """Repository for managing collections and their documents.

    This repository handles all database operations related to collections,
    including CRUD operations and managing document-collection relationships.
    """

    def __init__(self):
        self.engine = engine

    async def add_document_to_collection(
        self, collection: Collection, document: Document
    ) -> None:
        """Add a document to a collection.

        Args:
            collection: Collection to add document to
            document: Document to add to collection
        """
        with Session(self.engine) as session:
            collection.documents.append(document)
            session.add(collection)
            session.commit()

    async def create_collection(self, collection_name: str, user_id: int) -> Collection:
        """Create a new collection.

        Returns:
            Collection: Created collection
        """
        with Session(self.engine) as session:
            collection = Collection(name=collection_name, owner_id=user_id)
            session.add(collection)
            session.commit()
            session.refresh(collection)
            collection.documents = []
        return collection

    async def remove_document_from_collection(
        self, collection: Collection, document: Document
    ) -> None:
        """Remove a document from a collection.

        Args:
            collection: Collection to remove document from
            document: Document to remove from collection
        """
        with Session(self.engine) as session:
            collection.documents.remove(document)
            session.add(collection)
            session.commit()

    async def get_collection_by_id(
        self, collection_id: int, user_id: int
    ) -> Collection:
        """Get a collection by its ID.

        Args:
            collection_id: ID of the collection to get

        Returns:
            Collection: Collection with its documents

        Raises:
            NoResultFound: If collection with given ID doesn't exist
        """
        with Session(self.engine) as session:
            template = (
                select(Collection)
                .where(Collection.id == collection_id)
                .where(Collection.owner_id == user_id)
                .options(selectinload(Collection.documents))
            )
            collection = session.exec(template).one()
        return collection

    async def get_all_collections(self, user_id: int) -> List[CollectionResponse]:
        """Get all collections with their documents.

        Returns:
            list[CollectionResponse]: List of all collections with their documents
        """
        with Session(self.engine) as session:
            template = (
                select(Collection)
                .where(Collection.owner_id == user_id)
                .options(selectinload(Collection.documents))
            )
            collections = session.exec(template).all()
            return collections
