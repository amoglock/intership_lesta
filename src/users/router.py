from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from typing import List
from fastapi import Path

from src.users.auth import AuthService
from src.core.config import settings
from src.models import User
from src.users.dependencies import get_current_user
from .schemas import UserCreate, UserResponse, UserLogin, UserUpdate, Token

users_router = APIRouter(tags=["Users"])


@users_router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_data: UserCreate,
    auth_service: Annotated[AuthService, Depends()],
):
    """
    Register a new user.

    - **username**: Unique username for the user
    - **password**: User's password
    """
    return auth_service.create_user(user_data=user_data)


@users_router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends()],
    response: Response,
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests.

    - **username**: User's username
    - **password**: User's password
    """
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth_service.create_user_token(user)
    
    # Set token in cookie
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token['access_token']}",
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    return token


@users_router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    response: Response,
    current_user: Annotated[UserResponse, Depends(get_current_user)]
):
    """
    Logout user by clearing authentication cookies and invalidating token.
    
    This endpoint:
    1. Clears the access token cookie
    2. Returns a success message
    """
    # Clear the cookie
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,
        samesite="lax"
    )
    
    return {
        "message": "Successfully logged out",
        "user": current_user.username
    }


@users_router.patch("/user/{user_id}", response_model=UserResponse)
async def update_user(
    auth_service: Annotated[AuthService, Depends()],
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
):
    """
    Update user's password.

    - **user_id**: ID of the user to update
    - **password**: New password
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    user = auth_service.get_user(user_data=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user.hashed_password = auth_service.get_password_hash(user_update.password)
    user = auth_service.update_user(user_data=user)
    return user


@users_router.delete(
    "/user/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user account",
    description="""
    Delete user account and all associated data.
    
    This endpoint performs the following operations:
    1. Verifies user permissions
    2. Deletes all user's files from storage
    3. Deletes all user's collections
    4. Deletes all user's documents
    5. Deletes the user account
    
    After successful deletion:
    - All user's sessions are invalidated
    - All user's files are removed from storage
    - All user's collections and documents are deleted from database
    - User account is permanently deleted
    """,
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "User successfully deleted",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Not enough permissions to delete this user",
            "content": {
                "application/json": {
                    "example": {"detail": "Not enough permissions"}
                }
            }
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"}
                }
            }
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error during user deletion",
            "content": {
                "application/json": {
                    "example": {"detail": "Error deleting user: <error message>"}
                }
            }
        }
    }
)
async def delete_user(
    auth_service: Annotated[AuthService, Depends()],
    user_id: Annotated[int, Path(title="The ID of the user to delete", description="ID of the user account to be deleted")],
    current_user: User = Depends(get_current_user),
):
    """
    Delete user and all associated data.

    This endpoint:
    1. Verifies user permissions
    2. Deletes all user's files from storage
    3. Deletes all user's collections
    4. Deletes all user's documents
    5. Deletes the user account

    - **user_id**: ID of the user to delete
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not enough permissions"
        )

    user = auth_service.get_user(user_data=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )

    try:
        auth_service.delete_user(user)
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}"
        )
