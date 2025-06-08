import logging
from typing import Annotated

from sqlalchemy.exc import NoResultFound
from fastapi import APIRouter, Depends, HTTPException, Path, status

from src.collections.service import CollectionsService
from src.collections.schemas import CollectionResponse, DocumentInCollection


collections_router = APIRouter(
    prefix="/collections",
    tags=["Collections"],
)
logger = logging.getLogger(__name__)


@collections_router.post("/create")
async def create_collection(
    service: Annotated[CollectionsService, Depends()],
):
    """ """
    return await service.create_collection()


@collections_router.get("/", response_model=list[CollectionResponse])
async def collections(
    service: Annotated[CollectionsService, Depends()],
) -> list[CollectionResponse]:
    """Get all collections with their documents.

    Returns:
        List[CollectionResponse]: List of collections with their documents
    """
    return await service.collections()


@collections_router.get("/{collection_id}")
async def collection_by_id(
    collection_id: Annotated[int, Path(title="The ID of the collection to get")],
    service: Annotated[CollectionsService, Depends()],
) -> list[DocumentInCollection]:
    """ """
    try:
        return await service.collection(collection_id=collection_id)
    except NoResultFound as e:
        logger.error(f"File not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
        )


@collections_router.get("/{collection_id}/statistics")
async def collection_satistics(
    collection_id: Annotated[int, Path(title="The ID of the collection to get statistics")],
    service: Annotated[CollectionsService, Depends()]
):
    """ """
    return await service.get_collection_statistics(collection_id=collection_id)



@collections_router.post("/{collection_id}/{document_id}")
async def add_document(
    collection_id: Annotated[
        int, Path(title="The ID of the collection to add document")
    ],
    document_id: Annotated[int, Path(title="The ID of the document to add collection")],
    service: Annotated[CollectionsService, Depends()],
):
    """ """
    await service.add_document_to_collection(
        collection_id=collection_id, document_id=document_id
    )


@collections_router.delete("/{collection_id}/{document_id}")
async def delete_document(
    collection_id: Annotated[
        int, Path(title="The ID of the collection to remove document")
    ],
    document_id: Annotated[int, Path(title="The ID of the document to remove")],
    service: Annotated[CollectionsService, Depends()],
):
    await service.delete_document(collection_id=collection_id, document_id=document_id)
