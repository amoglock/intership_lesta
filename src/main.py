import logging
import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from src.core.config import settings
from src.database import create_db_and_tables
from src.documents.router import documents_router
from src.collections.router import collections_router
from src.frontend.router import frontend_router
from src.metrics.router import metrics_router
from src.tf_idf.router import router as tf_idf_router

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage FastAPI application lifecycle including database initialization."""
    # Initialization at startup
    try:
        create_db_and_tables()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    yield
    # Cleanup at shutdown
    logger.info("Application shutting down")

app = FastAPI(
    title=settings.APP_NAME,
    description="API for text analysis using TF-IDF algorithm",
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)


# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

# Connect routers
app.include_router(documents_router)
app.include_router(collections_router)
app.include_router(frontend_router)
app.include_router(metrics_router)
app.include_router(tf_idf_router, tags=["tf-idf"])

if __name__ == "__main__":
    uvicorn.run("src.main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=True)
    