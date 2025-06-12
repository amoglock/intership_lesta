import logging
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Path, status

from src.collections.service import CollectionsService
from src.collections.schemas import CollectionResponse, DocumentInCollection
from src.documents.schemas import ErrorMessage
from src.users.dependencies import get_current_user
from src.users.schemas import UserResponse


collections_router = APIRouter(
    prefix="/collections",
    tags=["Collections"],
    dependencies=[Depends(get_current_user)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Not authenticated",
            "model": ErrorMessage,
        },
    },
)

logger = logging.getLogger(__name__)


@collections_router.post(
    "/create",
    response_model=CollectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new collection",
    description="Create a new collection for the authenticated user",
    responses={
        status.HTTP_201_CREATED: {
            "description": "Collection successfully created",
            "model": CollectionResponse,
        },
    },
)
async def create_collection(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    collection_service: Annotated[CollectionsService, Depends()],
    collection_name: str,
):
    return await collection_service.create_collection(
        collection_name=collection_name,
        user=current_user,
    )


@collections_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=List[CollectionResponse],
    summary="Get collections list",
    description="Returns list of collections owned by the authenticated user with their documents",
    responses={
        status.HTTP_200_OK: {
            "description": "List of user's collections",
            "model": List[CollectionResponse],
        },
    },
)
async def collections(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    collection_service: Annotated[CollectionsService, Depends()],
):
    return await collection_service.collections(user=current_user)


@collections_router.get(
    "/{collection_id}",
    status_code=status.HTTP_200_OK,
    response_model=List[DocumentInCollection],
    summary="Get collection documents",
    description="Returns all documents associated with the specified collection",
    responses={
        status.HTTP_200_OK: {
            "description": "List of documents in the collection",
            "model": List[DocumentInCollection],
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Collection not found",
            "model": ErrorMessage,
        },
    },
)
async def collection_by_id(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    collection_id: Annotated[int, Path(title="The ID of the collection to get")],
    collection_service: Annotated[CollectionsService, Depends()],
):
    try:
        return await collection_service.collection(
            collection_id=collection_id, user=current_user
        )
    except Exception as e:
        logger.error(f"Error getting collection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found"
        )


@collections_router.get(
    "/{collection_id}/statistics",
    status_code=status.HTTP_200_OK,
    summary="Get collection statistics",
    description="Returns TF-IDF statistics for all documents in the collection",
    responses={
        status.HTTP_200_OK: {
            "description": "TF-IDF statistics for the collection",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Collection not found",
            "model": ErrorMessage,
        },
    },
)
async def collection_statistics(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    collection_id: Annotated[
        int, Path(title="The ID of the collection to get statistics for")
    ],
    service: Annotated[CollectionsService, Depends()],
):
    try:
        return await service.get_collection_statistics(collection_id=collection_id, user=current_user)
    except Exception as e:
        logger.error(f"Error getting collection statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found"
        )


@collections_router.post(
    "/{collection_id}/{document_id}",
    status_code=status.HTTP_200_OK,
    summary="Add document to collection",
    description="Add a document to the specified collection",
    responses={
        status.HTTP_200_OK: {
            "description": "Document successfully added to collection",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Collection or document not found",
            "model": ErrorMessage,
        },
    },
)
async def add_document(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    collection_id: Annotated[
        int, Path(title="The ID of the collection to add document to")
    ],
    document_id: Annotated[int, Path(title="The ID of the document to add")],
    service: Annotated[CollectionsService, Depends()],
):
    try:
        await service.add_document_to_collection(
            collection_id=collection_id,
            document_id=document_id,
            user=current_user,
        )
        return {"document": document_id, "collection": collection_id}
    except Exception as e:
        logger.error(f"Error adding document to collection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection or document not found",
        )


@collections_router.delete(
    "/{collection_id}/{document_id}",
    status_code=status.HTTP_200_OK,
    summary="Remove document from collection",
    description="Remove a document from the specified collection",
    responses={
        status.HTTP_200_OK: {
            "description": "Document successfully removed from collection",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Collection or document not found",
            "model": ErrorMessage,
        },
    },
)
async def delete_document(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    collection_id: Annotated[
        int, Path(title="The ID of the collection to remove document from")
    ],
    document_id: Annotated[int, Path(title="The ID of the document to remove")],
    service: Annotated[CollectionsService, Depends()],
):
    try:
        await service.delete_document(
            collection_id=collection_id, document_id=document_id, user=current_user
        )
        return {
            "document": document_id,
            "collection": collection_id,
            "status": "deleted",
        }
    except Exception as e:
        logger.error(f"Error removing document from collection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection or document not found",
        )
