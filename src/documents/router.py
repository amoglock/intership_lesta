import logging
from typing import Annotated, List

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Path,
    UploadFile,
    status,
)
from sqlalchemy.exc import NoResultFound

from src.documents.dependencies import file_validation
from src.documents.schemas import (
    DocumentContent,
    DocumentInDB,
    ErrorMessage,
    UploadFileResponse,
)
from src.documents.service import DocumentsService
from src.tf_idf.schemas import DocumentStatistics
from src.users.dependencies import get_current_user
from src.users.schemas import UserResponse


documents_router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
    dependencies=[Depends(get_current_user)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorMessage,
            "description": "Not authenticated",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorMessage,
            "description": "Internal server error occurred",
        },
    },
)

logger = logging.getLogger(__name__)


@documents_router.get(
    "/",
    response_model=List[DocumentInDB],
    status_code=status.HTTP_200_OK,
    summary="Get all user documents",
    description="Returns a list of all documents owned by the authenticated user",
    responses={
        status.HTTP_200_OK: {
            "description": "List of user's documents",
            "model": List[DocumentInDB],
        },
    },
)
async def documents(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    file_service: Annotated[DocumentsService, Depends()],
):
    logger.info(
        f"Fetching documents for user {current_user.username} (ID: {current_user.id})"
    )
    return await file_service.get_documents(user=current_user)


@documents_router.post(
    "/upload",
    response_model=UploadFileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a new file",
    description="Uploads a file, validates it, and saves it to the database",
    responses={
        status.HTTP_201_CREATED: {
            "description": "File successfully uploaded and saved",
            "model": UploadFileResponse,
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Failed to save file to storage or database",
            "model": ErrorMessage,
        },
    },
)
async def upload_file(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    file: Annotated[UploadFile, File(), Depends(file_validation)],
    file_service: Annotated[DocumentsService, Depends()],
):
    logger.info(
        f"Starting file upload for user {current_user.username} (ID: {current_user.id}). "
        f"File: {file.filename}, type: {file.content_type}"
    )

    try:
        uploaded_file_data = await file_service.upload_document_to_store(file=file)
        saved_document = await file_service.save_document_to_database(
            uploaded_file=uploaded_file_data, owner=current_user
        )

        logger.info(
            f"File uploaded successfully. User: {current_user.username}, "
            f"Document ID: {saved_document.id}, filename: {saved_document.filename}"
        )
        return UploadFileResponse.model_validate(saved_document)

    except (FileNotFoundError, Exception) as e:
        error_message = (
            "Failed to save file to storage"
            if isinstance(e, FileNotFoundError)
            else "Error uploading file"
        )
        if uploaded_file_data:
            await file_service.delete_file_from_store(
                file_path=uploaded_file_data.file_path
            )

        logger.error(
            f"{error_message}: {str(e)}. User: {current_user.username}, "
            f"File: {file.filename}, Error type: {type(e).__name__}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_message
        )


@documents_router.get(
    "/{document_id}",
    response_model=DocumentContent,
    status_code=status.HTTP_200_OK,
    summary="Get document content",
    description="Returns the content of a specific document",
    responses={
        status.HTTP_200_OK: {
            "description": "Document content retrieved successfully",
            "model": DocumentContent,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "The document was not found",
            "model": ErrorMessage,
        },
    },
)
async def document_by_id(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    document_id: Annotated[int, Path(title="The ID of the document to get")],
    file_service: Annotated[DocumentsService, Depends()],
):
    logger.info(f"Fetching document with ID: {document_id}")

    try:
        document = await file_service.get_document_with_content(
            document_id=document_id,
            user=current_user,
        )
        logger.info(
            f"Document retrieved successfully. ID: {document_id}, filename: {document.filename}"
        )
        return document
    except (FileNotFoundError, NoResultFound) as e:
        logger.error(f"Document not found. ID: {document_id}, Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )


@documents_router.get(
    "/{document_id}/statistics",
    status_code=status.HTTP_200_OK,
    response_model=DocumentStatistics,
    summary="Get document statistics",
    description="Returns TF-IDF statistics for the document within its collection",
    responses={
        status.HTTP_200_OK: {
            "description": "Document statistics retrieved successfully",
            "model": DocumentStatistics,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "The document was not found",
            "model": ErrorMessage,
        },
    },
)
async def document_statistics(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    document_id: Annotated[int, Path(title="The ID of the document to get statistics")],
    collection_id: int,
    file_service: Annotated[DocumentsService, Depends()],
):
    logger.info(
        f"Fetching statistics for document {document_id} in collection {collection_id}"
    )
    try:
        return await file_service.get_document_statistics(
            collection_id=collection_id,
            document_id=document_id,
            user=current_user,
        )
    except (NoResultFound) as e:
        logger.error(f"Document not found. ID: {document_id}, Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )


@documents_router.delete(
    "/{document_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete document",
    description="Deletes a document owned by the authenticated user",
    responses={
        status.HTTP_200_OK: {
            "description": "Document successfully deleted",
            "content": {
                "application/json": {
                    "example": {"document_id": 123, "status": "deleted"}
                }
            },
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "The document was not found",
            "model": ErrorMessage,
        },
    },
)
async def delete_document(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    document_id: Annotated[int, Path(title="The ID of the document to delete")],
    file_service: Annotated[DocumentsService, Depends()],
):
    logger.info(f"Attempting to delete document with ID: {document_id}")

    try:
        await file_service.delete_document(document_id=document_id, user=current_user)
        logger.info(f"Document deleted successfully. ID: {document_id}")
        return {"document_id": document_id, "status": "deleted"}
    except (FileNotFoundError, NoResultFound) as e:
        logger.error(f"Failed to delete document. ID: {document_id}, Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )
