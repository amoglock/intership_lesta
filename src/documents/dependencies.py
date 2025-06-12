import logging
import os
from fastapi import UploadFile

from src.core.config import settings
from src.documents.exceptions import (
    FileExtensionValidationError,
    FileSizeValidationError,
    FileTypeValidationError,
)

logger = logging.getLogger(__name__)


async def file_validation(file: UploadFile) -> UploadFile:
    """Validates file size, content type and file extension.

    Args:
        file (UploadFile): Uploaded file by form

    Returns:
        bool: True if validation is successful, otherwise False

    Note:
        Validates against:
        - settings.MAX_FILE_SIZE: Maximum allowed file size
        - settings.ALLOWED_FILE_TYPES: List of allowed MIME types
        - settings.ALLOWED_EXTENSIONS: List of allowed file extensions
    """
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in settings.ALLOWED_EXTENSIONS:
        logger.info("Fail validate. File not in ALLOWED_EXTENSIONS")
        raise FileExtensionValidationError()

    if file.size > settings.MAX_FILE_SIZE:
        logger.info("Fail validate. File is too large size")
        raise FileSizeValidationError()

    if file.content_type not in settings.ALLOWED_FILE_TYPES:
        logger.info("Fail validate. File not in ALLOWED_FILE_TYPES")
        raise FileTypeValidationError()

    return file
