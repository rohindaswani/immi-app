"""
API dependencies for FastAPI routes.
This module re-exports common dependencies used across API endpoints.
"""
from app.core.security import get_current_user
from app.db.postgres import get_db

# Re-export dependencies to simplify imports in endpoint files
__all__ = ["get_current_user", "get_db"]