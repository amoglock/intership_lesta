import logging
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from src.core.config import settings

frontend_router = APIRouter(
    tags=["frontend"]
)
logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="src/frontend/templates")


@frontend_router.get("/", include_in_schema=False)
async def upload_form(request: Request):
    """Display file upload form"""
    try:
        return templates.TemplateResponse("upload.html", {"request": request})
    except Exception as e:
        logger.error(f"Error rendering template: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Error rendering template"},
        )
