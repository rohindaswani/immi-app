import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time

from app.core.config import settings
from app.core.middleware import setup_middleware
from app.api.api_v1.api import api_router
from app.db.postgres import Base, engine, SessionLocal
from app.db.init_db import init_db

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for managing immigration status and documents",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Startup event to create database tables
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        # Initialize with seed data
        db = SessionLocal()
        try:
            init_db(db)
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Set-Cookie"],
)

# Set up middlewares
setup_middleware(app)

# Include API router
app.include_router(api_router, prefix="")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": "0.1.0",
        "timestamp": time.time()
    }

# Root endpoint
@app.get("/")
def root():
    return {"message": f"Welcome to the {settings.PROJECT_NAME} API. Visit {settings.API_V1_STR}/docs for the API documentation."}

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )