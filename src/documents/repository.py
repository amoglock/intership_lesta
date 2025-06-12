import logging
from typing import List
from sqlmodel import Session, select
from src.database import engine
from src.models import Collection, Document


class DocumentsRepository:
    def __init__(self):
        self.engine = engine
        self.logger = logging.getLogger(__name__)

    async def add_document(self, uploaded_file: Document) -> Document:
        """

        Args:
            uploaded_file (UploadedFile): _description_
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
        """ """
        with Session(self.engine) as session:
            session.delete(document)
            session.commit()
            self.logger.info(f"{document.filename} was deleted")

    async def get_one_or_all_documents(
        self, user_id: int, document_id: int | None = None
    ) -> Document | List[Document]:
        """Get documents for current user.

        Args:
            user_id (int): current active user id
            document_id (int | None, optional): the ID of a specific document. Defaults to None

        Returns:
            list[Document]: if document_id not set (None)
            Document: specific document with current document_id
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

