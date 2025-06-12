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
)

logger = logging.getLogger(__name__)


@collections_router.post(
    "/create",
    response_model=CollectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new collection",
    description="Create a new collection",
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
    description="Returns only own collections with documents list",
)
async def collections(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    collection_service: Annotated[CollectionsService, Depends()],
):

    return await collection_service.collections(user=current_user)


@collections_router.get(
    "/{collection_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorMessage,
            "description": "The collection was not found",
        },
    },
    response_model=List[DocumentInCollection],
    summary="Get all documents in the collection",
    description="Returns only documents linked with the collection",
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


@collections_router.get("/{collection_id}/statistics")
async def collection_statistics(
    collection_id: Annotated[
        int, Path(title="The ID of the collection to get statistics for")
    ],
    service: Annotated[CollectionsService, Depends()],
):
    """Get TF-IDF statistics for all documents in a collection.

    Args:
        collection_id: ID of the collection to get statistics for

    Returns:
        dict: TF-IDF statistics for the collection

    Raises:
        HTTPException: If collection doesn't exist
    """
    try:
        return await service.get_collection_statistics(collection_id)
    except Exception as e:
        logger.error(f"Error getting collection statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found"
        )


@collections_router.post(
    "/{collection_id}/{document_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorMessage,
            "description": "The collection was not found",
        },
    },
    summary="Add document to collection",
    description="Add document only to own collection",
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
        # TODO Fix response if document already in collection
        logger.error(f"Error adding document to collection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection or document not found",
        )


@collections_router.delete(
    "/{collection_id}/{document_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete document from collection",
    description="Delete only own collection",
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
