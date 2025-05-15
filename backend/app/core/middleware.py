from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import time
from typing import Callable, Dict
from fastapi import Request, Response
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging request information and timing.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        log_dict = {
            "url": str(request.url),
            "method": request.method,
            "process_time": f"{process_time:.4f}s",
            "client": request.client.host if request.client else None,
            "status_code": response.status_code,
        }
        
        if response.status_code >= 500:
            logger.error(f"Request: {log_dict}")
        elif response.status_code >= 400:
            logger.warning(f"Request: {log_dict}")
        else:
            logger.info(f"Request: {log_dict}")
        
        # Add processing time header for debugging
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware for adding security headers to responses.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        
        # Set content security policy
        # response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline';"
        
        return response


def setup_middleware(app: FastAPI) -> None:
    """
    Set up all middleware for the application.
    """
    # CORS middleware for cross-origin requests
    # Use hardcoded values to avoid any parsing issues
    origins = ["http://localhost:3000", "http://localhost:8000", "*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Trusted host middleware - hardcoded for simplicity
    allowed_hosts = ["localhost", "127.0.0.1", "*"]
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=allowed_hosts
    )
    
    # Session middleware for managing session cookies
    app.add_middleware(
        SessionMiddleware, 
        secret_key=settings.SECRET_KEY,
        max_age=settings.SESSION_MAX_AGE,
    )
    
    # Gzip middleware for response compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Custom security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Request logging middleware
    app.add_middleware(RequestLoggerMiddleware)