from fastapi import HTTPException, UploadFile, status
from src.core.config import settings

async def check_valid_file_content(file_content: str) -> None:
    """Validates that the uploaded file is a plain text file ('text/plain' content type).

    Args:
        file_content (str): The content type header from the uploaded file
            (e.g., from UploadFile.content_type).

    Raises:
        HTTPException: If content type is not 'text/plain', raises 400 Bad Request
            with detail "Only text files are allowed".

    Note:
        - This is an async function to maintain consistency with FastAPI's file handling
        - The check is case-sensitive (must be exactly 'text/plain')
        - No return value - either passes silently or raises an exception
    """
    if not file_content == "text/plain":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only text files are allowed"
        )


async def check_file_size(file: UploadFile) -> None:
    """Checks if the uploaded file exceeds the maximum allowed file size.

    Reads a chunk of the file up to `MAX_FILE_SIZE + 1` bytes to determine if the file
    is larger than the limit. If the file exceeds the limit, raises an HTTP 413 error.

    Args:
        file (UploadFile): The uploaded file to check, typically from FastAPI's `File()`.

    Raises:
        HTTPException: 
            - Status code 413 (Payload Too Large) if the file size exceeds `MAX_FILE_SIZE`.
            - The error detail includes the maximum allowed size in megabytes.

    Notes:
        - The file pointer is partially read but not reset (use `await file.seek(0)` if needed later).
        - `MAX_FILE_SIZE` should be defined in `settings` (e.g., in bytes).
        - No return value - either passes silently or raises an exception
    """
    content = await file.read(settings.MAX_FILE_SIZE + 1)
    if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE/(1024 * 1024)}MB"
            )
