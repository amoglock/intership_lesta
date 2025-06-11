from fastapi import HTTPException, status

from src.core.config import settings

class FileExtensionValidationError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension not allowed. Allowed extensions: {settings.ALLOWED_EXTENSIONS}"
        )

class FileSizeValidationError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size maximum allowed {settings.MAX_FILE_SIZE}"
        )

class FileTypeValidationError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Content type not allowed. Allowed types: {settings.ALLOWED_FILE_TYPES}"
        )
