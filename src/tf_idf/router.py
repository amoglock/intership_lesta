from typing import Annotated, List
from fastapi import APIRouter, Request, File, UploadFile, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Form
from src.tf_idf.utils import check_valid_file_content
from src.tf_idf.processor import TFIDFProcessor
import logging

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
    file: UploadFile = File(...),
    max_file_size: int = Form(10_000_000, description="Maximum file size in bytes")
):
    """Process the uploaded file and return TF-IDF analysis results"""
    try:
        # Check file type
        if not check_valid_file_content(file.content_type):
            raise HTTPException(
                status_code=400,
                detail="Only text files are allowed"
            )
        
        # Read file content
        content = await file.read()
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="File cannot be decoded as text"
            )
        
        # Process text
        results = await processor.process_text(
            filename=file.filename,
            text=text,
            max_file_size=max_file_size
        )
        
        # Sort results by IDF in descending order and limit to 50 words
        # Tuples in results have format (word, tf, idf)
        sorted_results = sorted(
            results.results, 
            key=lambda x: x[2],  # index 2 is IDF 
            reverse=True
        )[:50]
        
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
