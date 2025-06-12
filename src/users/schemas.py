from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    password: str


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True


class User(BaseModel):
    username: str


class UserInDB(User):
    hashed_password: str