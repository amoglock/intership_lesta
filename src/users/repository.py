import logging
from sqlmodel import Session, select
from src.database import engine
from src.models import User


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
        with Session(self.engine) as session:
            session.delete(user)
            session.commit()
        

