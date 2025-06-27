import logging
import sys
import traceback
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.config import settings, setup_logging
from app.api.api_v1.api import api_router
import spacy

# Configure logging
logger = setup_logging()

def create_application() -> FastAPI:
    logger.info("Creating FastAPI application")
    
    # Initialize FastAPI application
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="API for analyzing legal documents",
        version="1.0.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        debug=settings.DEBUG
    )
    
    # Set up CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    # Add middleware for request logging
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        logger.info(f"Request: {request.method} {request.url}")
        logger.debug(f"Headers: {dict(request.headers)}")
        
        try:
            response = await call_next(request)
            logger.info(f"Response status: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    # Add exception handlers
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {str(exc)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error(f"Request validation error: {exc}")
        logger.error(f"Request body: {await request.body()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors(), "body": exc.body},
        )
    
    logger.info("FastAPI application created successfully")
    return app

# Create the FastAPI application
app = create_application()

# Load spaCy model at startup
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up application...")
    
    try:
        logger.info("Loading spaCy model...")
        nlp = spacy.load("en_core_web_sm")
        logger.info("spaCy model loaded successfully")
    except OSError as e:
        logger.warning("spaCy model not found, downloading...")
        try:
            import os
            logger.info("Downloading spaCy model...")
            os.system("python -m spacy download en_core_web_sm")
            nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy model downloaded and loaded successfully")
        except Exception as e:
            logger.error(f"Failed to download or load spaCy model: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    except Exception as e:
        logger.error(f"Unexpected error loading spaCy model: {str(e)}")
        logger.error(traceback.format_exc())
        raise
    
    logger.info("Application startup complete")

# Shutdown event handler
@app.on_event("shutdown")
def shutdown_event():
    logger.info("Application shutting down...")
    # Add any cleanup code here
