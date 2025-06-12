import logging
import os
from sqlmodel import Session, select
from src.database import engine
from src.models import User, Document, Collection
from src.core.config import settings


class UsersRepository:
    def __init__(self):
        self.engine = engine
        self.logger = logging.getLogger(__name__)

    def add_user(self, user: User) -> User:
        with Session(self.engine) as session:
            session.add(user)
            session.commit()
            session.refresh(user)
        return user


    def get_user_by_name(self, username: str) -> User:
        with Session(self.engine) as session:
            template = select(User).where(User.username == username)
            user = session.exec(template).first()
            return user
        
    def get_user_by_id(self, user_id: int) -> User:
        with Session(self.engine) as session:
            template = select(User).where(User.id == user_id)
            user = session.exec(template).first()
            return user
        
    def delete_user(self, user: User) -> None:
        """Physically delete user and all related data.
        
        This will:
        1. Delete all user's documents from storage
        2. Delete all user's collections
        3. Delete all user's documents from database
        4. Delete the user record
        
        Args:
            user (User): User to delete
        """
        with Session(self.engine) as session:
            # Get all user's documents
            documents = session.exec(
                select(Document).where(Document.owner_id == user.id)
            ).all()
            
            # Delete files from storage
            for doc in documents:
                try:
                    file_path = os.path.join(settings.UPLOAD_DIR, doc.unique_filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    self.logger.error(f"Error deleting file {doc.unique_filename}: {e}")
            
            # Delete all user's collections
            collections = session.exec(
                select(Collection).where(Collection.owner_id == user.id)
            ).all()
            for collection in collections:
                session.delete(collection)
            
            # Delete all user's documents
            for doc in documents:
                session.delete(doc)
            
            # Finally delete the user
            session.delete(user)
            session.commit()
        

