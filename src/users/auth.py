from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from src.core.config import settings
from src.users.repository import UsersRepository
from src.users.schemas import UserCreate
from src.models import User
from .dependencies import create_access_token



class AuthService:

    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
        self.users_repository = UsersRepository()


    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)


    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)


    # def get_user(self, db, username: str):
    #     if username in db:
    #         user_dict = db[username]
    #         return UserInDB(**user_dict)
        
    def get_user(self, user_data: int | str) -> User | None:
        if isinstance(user_data, int):
            user = self.users_repository.get_user_by_id(user_id=user_data)
            return user
        if isinstance(user_data, str):
            user = self.users_repository.get_user_by_name(username=user_data)
            return user
        
    def delete_user(self, user: User) -> None:
        self.users_repository.delete_user(user)


    def authenticate_user(self, username: str, password: str) -> User:
        user = self.get_user(user_data=username)
        if not user:
            return False
        if not self._verify_password(password, user.hashed_password):
            return False
        return user

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt


    def create_user(self, user_data: UserCreate) -> User:
        # Check if user exists
        existing_user = self.get_user(user_data=user_data.username)

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

        # Create new user
        hashed_password = self.get_password_hash(user_data.password)
        db_user = User(username=user_data.username, hashed_password=hashed_password)
        db_user = self.users_repository.add_user(user=db_user)
        return db_user
    
    def update_user(self, user_data):
        db_user = self.users_repository.add_user(user_data)
        return db_user
        

    def create_user_token(self, user: User) -> dict:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "id": user.id}, 
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
