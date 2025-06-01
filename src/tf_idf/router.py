import logging
from typing import Annotated

from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.tf_idf.processor import TFIDFProcessor
from src.core.config import settings


logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="src/templates")

@router.get("/", response_class=HTMLResponse)
async def upload_form(request: Request):
    """Display file upload form"""
    try:
        return templates.TemplateResponse(
            "upload.html",
            {"request": request}
        )
    except Exception as e:
        logger.error(f"Failed to render upload form: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to render upload form"
        )

@router.post("/upload", response_class=HTMLResponse)
async def process_file(
    request: Request,
    processor: Annotated[TFIDFProcessor, Depends()],
):
    """Process the uploaded file and return TF-IDF analysis results"""
    
    validation_data = request.state.file_validation
    file = validation_data["file"]

    try:
        content = await file.read()
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File cannot be decoded as text"
            )
        
        results = await processor.process_text(
            filename=file.filename,
            text=text,
        )
        
        # Sort results by IDF in descending order and limit to 50 words
        # Tuples in results have format (word, tf, idf)
        sorted_results = sorted(
            results.results, 
            key=lambda x: x[2],  # index 2 is IDF 
            reverse=True
        )[:settings.TOP_WORDS_COUNT]
        
        return templates.TemplateResponse(
            "upload.html",
            {
                "request": request,
                "results": sorted_results,
                "current_analysis": results.analysis,
                "error": None
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process file: {e}")
        return templates.TemplateResponse(
            "upload.html",
            {
                "request": request,
                "error": f"Failed to process file: {str(e)}",
                "results": None,
                "current_analysis": None
            }
        )
