import logging
from typing import Annotated

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

from src.documents.schemas import (
    DocumentContent,
    DocumentInDB,
    ErrorMessage,
    UploadFileResponse,
)
from src.documents.service import DocumentsService


documents_router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)
logger = logging.getLogger(__name__)



@documents_router.post(
    "/upload",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorMessage,
            "description": "The file was checked unsuccessfully",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorMessage},
    },
    response_model=UploadFileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_file(
    file_service: Annotated[DocumentsService, Depends()],
    file: UploadFile = File(...),
) -> UploadFileResponse:
    """Handle file upload"""
    try:
        if not await file_service.file_validation(file=file):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type or size",
            )

        uploaded_file_data = await file_service.upload_document_to_store(file=file)
        saved_document = await file_service.save_document_to_database(
            uploaded_file=uploaded_file_data
        )

        return UploadFileResponse(filename=saved_document.filename)

    except HTTPException as e:
        raise e
    except (FileNotFoundError, Exception) as e:
        error_message = (
            "Failed to save file to storage"
            if isinstance(e, FileNotFoundError)
            else "Error uploading file"
        )
        logger.error(f"{error_message}: {str(e)}")
        # TODO Check if the file exists and delete it

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_message
        )

@documents_router.get("/")
async def documents(
    file_service: Annotated[DocumentsService, Depends()],
) -> list[DocumentInDB]:
    """ """
    return await file_service.get_documents()


@documents_router.get(
    "/{document_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorMessage,
            "description": "The file was not found",
        },
    },
    response_model=DocumentContent,
)
async def document_by_id(
    document_id: Annotated[int, Path(title="The ID of the document to get")],
    file_service: Annotated[DocumentsService, Depends()],
) -> DocumentContent:
    """ """
    try:
        return await file_service.get_document_with_content(document_id=document_id)
    except (FileNotFoundError, NoResultFound) as e:
        logger.error(f"File not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )


@documents_router.delete(
    "/{document_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorMessage,
            "description": "The file was not found",
        },
    },
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_document(
    document_id: Annotated[int, Path(title="The ID of the document to delete")],
    file_service: Annotated[DocumentsService, Depends()],
) -> None:
    """ """
    try:
        await file_service.delete_document(document_id=document_id)
    except (FileNotFoundError, NoResultFound) as e:
        logger.error(f"File nor found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )
