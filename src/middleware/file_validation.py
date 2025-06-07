from typing import Callable
from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp
from src.core.config import settings
import os
# import logging
# from sqlmodel import Session, select
# from src.models import GlobalMetrics
# from src.database import engine
# from datetime import datetime, UTC

# logger = logging.getLogger(__name__)

# class RequestCounterMiddleware(BaseHTTPMiddleware):
#     """
#     Middleware for counting effective requests
#     """
#     def __init__(self, app: ASGIApp):
#         super().__init__(app)
#         self.excluded_paths = {
#             "/static/",
#             "/favicon.ico",
#             "/docs",
#             "/redoc",
#             "/openapi.json"
#         }

#     async def dispatch(self, request: Request, call_next: Callable) -> Response:
#         if any(request.url.path.startswith(path) for path in self.excluded_paths):
#             return await call_next(request)

#         try:
#             with Session(engine) as session:
#                 statement = select(GlobalMetrics)
#                 results = session.exec(statement)
#                 metrics = results.first()
#                 if not metrics:
#                     metrics = GlobalMetrics()
#                     session.add(metrics)
                
#                 metrics.total_requests = (metrics.total_requests or 0) + 1
                
#                 if request.url.path == "/upload" and request.method == "POST":
#                     metrics.total_analyses = (metrics.total_analyses or 0) + 1
                
#                 metrics.updated_at = datetime.now(UTC)
#                 session.commit()
#         except Exception as e:
#             logger.error(f"Error updating request metrics: {e}")
        
#         return await call_next(request)

class FileValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for validating uploaded files:
    - Checks Content-Type
    - Checks file size
    - Checks file extension (.txt)
    - Checks allowed MIME types
    - Saves result to request.state.file_validation
    Applied only to POST /upload
    """
    def __init__(self, app:  ASGIApp):
        super().__init__(app)
        self.max_size = settings.MAX_FILE_SIZE
        self.allowed_types = settings.ALLOWED_FILE_TYPES 
        self.allowed_extensions = settings.ALLOWED_EXTENSIONS

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        File validation for POST /upload:
        - Content-Type check
        - Size check
        - Extension check
        - MIME type check
        """
        if request.url.path == "/documents/upload" and request.method == "POST":
            # Check request Content-Type
            content_type = request.headers.get("content-type", "")
            if not content_type.startswith("multipart/form-data"):
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail="Only multipart/form-data uploads are supported"
                )

            try:
                form_data = await request.form()
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid form data: {str(e)}"
                )

            if "file" not in form_data:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file uploaded")
            
            file = form_data["file"]
            
            # Check file size
            file_size = 0
            chunk_size = 64 * 1024  # 64kb at once
            temp = await file.read(chunk_size)
            file_size += len(temp)
            
            while len(temp) == chunk_size and file_size <= self.max_size:
                temp = await file.read(chunk_size)
                file_size += len(temp)
            
            if file_size > self.max_size:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File too large. Max size is {self.max_size/(1024*1024):.2f}MB"
                )
            
            # Check file type
            if file.content_type not in self.allowed_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Only {self.allowed_types} files are allowed. Got {file.content_type}"
                )
            
            # Check file extension
            filename = file.filename
            ext = os.path.splitext(filename)[1].lower()
            if ext not in self.allowed_extensions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Only {self.allowed_extensions} files are allowed"
                )
            
            # Return pointer to start
            await file.seek(0)
            
            # Save validated data
            request.state.file_validation = {
                "file": file
            }
        
        return await call_next(request)
