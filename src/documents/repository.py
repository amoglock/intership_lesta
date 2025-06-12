import logging
from typing import List
from sqlmodel import Session, select
from src.database import engine
from src.models import Document


class DocumentsRepository:
    """Repository for managing document data in the database.

    This repository handles all database operations related to documents, including:
    - Adding new documents
    - Retrieving documents
    - Updating document information
    - Deleting documents
    """

    def __init__(self):
        """Initialize the DocumentsRepository with database engine and logger."""
        self.engine = engine
        self.logger = logging.getLogger(__name__)

    async def add_document(self, uploaded_file: Document) -> Document:
        """Add a new document to the database.

        Args:
            uploaded_file (Document): Document object containing file information and metadata

        Returns:
            Document: The saved document with its database ID

        Raises:
            Exception: If there is an error during database operations
        """
        try:
            with Session(self.engine) as session:
                session.add(uploaded_file)
                session.commit()

                self.logger.info(f"{uploaded_file.filename} was saved successfully")
                return uploaded_file
        except Exception as e:
            self.logger.error(f"Error saving document: {e}")
            raise

    async def delete_document(self, document: Document) -> None:
        """Delete a document from the database.

        Args:
            document (Document): The document to be deleted

        Note:
            This operation permanently removes the document from the database.
            Make sure to handle any associated files separately.
        """
        with Session(self.engine) as session:
            session.delete(document)
            session.commit()
            self.logger.info(f"{document.filename} was deleted")

    async def get_one_or_all_documents(
        self, user_id: int, document_id: int | None = None
    ) -> Document | List[Document]:
        """Get documents for the specified user.

        Args:
            user_id (int): ID of the user whose documents to retrieve
            document_id (int | None, optional): ID of a specific document to retrieve. Defaults to None.

        Returns:
            Document | List[Document]: If document_id is provided, returns the specific document.
                                     If document_id is None, returns a list of all user's documents.

        Raises:
            NoResultFound: If document_id is provided but the document doesn't exist
        """
        with Session(self.engine) as session:
            if document_id:
                statement = (
                    select(Document)
                    .where(Document.id == document_id)
                    .where(Document.owner_id == user_id)
                )
                document = session.exec(statement).one()
                return document

            statement = select(Document).where(Document.owner_id == user_id)
            documents = session.exec(statement).all()
            return documents

    async def update_document(self, document: Document) -> None:
        """Update an existing document in the database.

        Args:
            document (Document): The document object with updated information

        Note:
            The document must already exist in the database with a valid ID.
            Only the fields that have been modified will be updated.
        """
        with Session(self.engine) as session:
            session.add(document)
            session.commit()
