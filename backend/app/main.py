import logging
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import time
from pathlib import Path

from app.core.config import settings
from app.core.middleware import setup_middleware
from app.api.api_v1.api import api_router
from app.db.postgres import Base, engine, SessionLocal
from app.db.init_db import init_db
from app.core.security import get_current_user

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
app.include_router(api_router, prefix=settings.API_V1_STR)

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

# File serving endpoint for locally stored files
@app.get("/files/{file_path:path}")
async def serve_file(
    file_path: str,
    download: bool = False,
    current_user: str = Depends(get_current_user)
):
    """
    Serve uploaded files with authentication.
    Only allows users to access files in their own directory.
    
    Args:
        file_path: Path to the file relative to uploads directory
        download: If True, force download. If False, display inline for preview.
    """
    try:
        # Security check: ensure the file path contains the current user's ID
        if current_user not in file_path:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Construct the full file path
        uploads_dir = Path("uploads")
        full_file_path = uploads_dir / file_path
        
        # Security check: ensure the path doesn't contain directory traversal attempts
        try:
            full_file_path.resolve().relative_to(uploads_dir.resolve())
        except ValueError:
            raise HTTPException(status_code=403, detail="Invalid file path")
        
        # Check if file exists
        if not full_file_path.exists() or not full_file_path.is_file():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Determine content type based on file extension
        file_extension = full_file_path.suffix.lower()
        content_type_map = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.tiff': 'image/tiff',
            '.tif': 'image/tiff',
            '.webp': 'image/webp'
        }
        
        media_type = content_type_map.get(file_extension, 'application/octet-stream')
        
        # Create custom headers for preview vs download
        headers = {}
        
        # Set Content-Disposition header based on download parameter
        if download:
            headers["Content-Disposition"] = f'attachment; filename="{full_file_path.name}"'
        else:
            headers["Content-Disposition"] = f'inline; filename="{full_file_path.name}"'
            # Allow iframe embedding for preview
            headers["Content-Security-Policy"] = "frame-ancestors 'self' http://localhost:3000"
        
        # Return the file with appropriate headers
        response = FileResponse(
            path=str(full_file_path),
            media_type=media_type,
            filename=full_file_path.name if download else None,
            headers=headers
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving file {file_path}: {e}")
        raise HTTPException(status_code=500, detail="Error serving file")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )