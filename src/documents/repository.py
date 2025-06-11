import logging
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
                collection = session.exec(select(Collection)).first()
                uploaded_file.collections = [collection]
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

    async def get_one_or_all_documents(self, document_id: int | None = None) -> list[Document]:
        """_summary_"""

        try:
            with Session(self.engine) as session:
                if document_id:
                    statement = select(Document).where(Document.id == 0)
                    document = session.exec(statement).one()
                    return document

                statement = select(Document)
                documents = session.exec(statement).all()
                return documents

        except Exception as e:
            self.logger.error(f"Error get list or one of document: {e}")
            raise
