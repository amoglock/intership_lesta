import logging
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Path, status

from sqlalchemy.exc import NoResultFound
from src.collections.service import CollectionsService
from src.collections.schemas import CollectionResponse, DocumentInCollection


collections_router = APIRouter(
    prefix="/collections",
    tags=["Collections"],
)
logger = logging.getLogger(__name__)


@collections_router.post("/create", response_model=CollectionResponse)
async def create_collection(
    service: Annotated[CollectionsService, Depends()],
) -> CollectionResponse:
    """Create a new collection.
    
    Returns:
        CollectionResponse: Created collection
    """
    return await service.create_collection()


@collections_router.get("/", response_model=List[CollectionResponse])
async def collections(
    service: Annotated[CollectionsService, Depends()]
) -> List[CollectionResponse]:
    """Get all collections with their documents.
    
    Returns:
        List[CollectionResponse]: List of all collections with their documents
    """
    return await service.collections()


@collections_router.get("/{collection_id}", response_model=List[DocumentInCollection])
async def collection_by_id(
    collection_id: Annotated[int, Path(title="The ID of the collection to get")],
    service: Annotated[CollectionsService, Depends()]
) -> List[DocumentInCollection]:
    """Get all documents in a collection.
    
    Args:
        collection_id: ID of the collection to get documents from
        
    Returns:
        List[DocumentInCollection]: List of documents in the collection
        
    Raises:
        HTTPException: If collection doesn't exist
    """
    try:
        return await service.collection(collection_id)
    except Exception as e:
        logger.error(f"Error getting collection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )


@collections_router.get("/{collection_id}/statistics")
async def collection_statistics(
    collection_id: Annotated[int, Path(title="The ID of the collection to get statistics for")],
    service: Annotated[CollectionsService, Depends()]
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )


@collections_router.post("/{collection_id}/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_document(
    collection_id: Annotated[int, Path(title="The ID of the collection to add document to")],
    document_id: Annotated[int, Path(title="The ID of the document to add")],
    service: Annotated[CollectionsService, Depends()]
) -> None:
    """Add a document to a collection.
    
    Args:
        collection_id: ID of the collection to add document to
        document_id: ID of the document to add
        
    Raises:
        HTTPException: If collection or document doesn't exist
    """
    try:
        await service.add_document_to_collection(collection_id, document_id)
    except Exception as e:
        logger.error(f"Error adding document to collection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection or document not found"
        )


@collections_router.delete("/{collection_id}/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    collection_id: Annotated[int, Path(title="The ID of the collection to remove document from")],
    document_id: Annotated[int, Path(title="The ID of the document to remove")],
    service: Annotated[CollectionsService, Depends()]
) -> None:
    """Remove a document from a collection.
    
    Args:
        collection_id: ID of the collection to remove document from
        document_id: ID of the document to remove
        
    Raises:
        HTTPException: If collection or document doesn't exist
    """
    try:
        await service.delete_document(collection_id, document_id)
    except Exception as e:
        logger.error(f"Error removing document from collection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection or document not found"
        )
