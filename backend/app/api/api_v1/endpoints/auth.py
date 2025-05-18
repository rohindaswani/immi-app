from urllib.parse import urlencode
import secrets
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from jose import jwt, JWTError
import json

from app.core.config import settings
from app.db.postgres import get_db
from app.schemas.token import Token
from app.schemas.user import UserResponse
from app.services.google_auth import GoogleAuthService

router = APIRouter()

# Generate a random state string for CSRF protection
def generate_state_param() -> str:
    return secrets.token_urlsafe(32)

@router.get("/google/url")
async def google_auth_url(db: Session = Depends(get_db)):
    """
    Get Google OAuth authorization URL with state parameter.
    """
    auth_service = GoogleAuthService(db)
    auth_url, state = await auth_service.get_google_auth_url()
    return {"url": auth_url, "state": state}

@router.get("/google/login")
async def google_login(request: Request, response: Response, db: Session = Depends(get_db)):
    """
    Initiate Google OAuth login flow.
    Redirects user to Google's authorization page.
    """
    # Get the Google auth URL and state
    auth_service = GoogleAuthService(db)
    auth_url, state = await auth_service.get_google_auth_url()
    
    # Store state in session
    request.session["oauth_state"] = state
    
    # Redirect to Google auth page
    return RedirectResponse(auth_url)

@router.get("/google/callback")
@router.post("/google/callback")
async def google_callback(
    request: Request,
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """
    Handle Google OAuth callback.
    Exchange code for tokens and authenticate user.
    """
    # Verify state parameter using StateStorage
    auth_service = GoogleAuthService(db)
    if not auth_service.state_storage.validate_state(state):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter"
        )
    
    try:
        # Authenticate with Google
        auth_service = GoogleAuthService(db)
        user_response, token = await auth_service.authenticate_with_google(code, state)
        
        # Create response with user data and tokens
        response = Response(
            content=json.dumps({
                "user": user_response.dict(),
                "token": token.dict()
            }),
            media_type="application/json"
        )
        
        # Set JWT tokens in cookies
        response.set_cookie(
            key="access_token",
            value=token.access_token,
            httponly=True,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            secure=settings.ENVIRONMENT != "development"
        )
        
        response.set_cookie(
            key="refresh_token",
            value=token.refresh_token,
            httponly=True,
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            secure=settings.ENVIRONMENT != "development"
        )
        
        # Add user info to query params for frontend
        query_params = {
            "user_id": user_response.user_id,
            "email": user_response.email,
            "first_name": user_response.first_name or "",
            "last_name": user_response.last_name or "",
            "authenticated": "true"
        }
        
        # Redirect to frontend with user data
        redirect_url = f"{settings.SERVER_URL}/auth/success?{urlencode(query_params)}"
        response = RedirectResponse(url=redirect_url)
        
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/token/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using the refresh token from cookies.
    """
    # Get refresh token from cookie
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Decode refresh token
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        
        # Check token type
        token_type = payload.get("type")
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user ID from token
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create new tokens
        from app.core.security import create_access_token, create_refresh_token
        
        new_access_token = create_access_token(subject=user_id)
        new_refresh_token = create_refresh_token(subject=user_id)
        
        # Create response with new tokens in cookies
        response = Response()
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            secure=settings.ENVIRONMENT != "development"
        )
        
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            secure=settings.ENVIRONMENT != "development"
        )
        
        # Return new tokens
        return Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    db: Session = Depends(get_db),
    auth_service: GoogleAuthService = Depends(GoogleAuthService)
):
    """
    Get the current authenticated user.
    """
    user = await auth_service.get_current_user()
    return user

@router.post("/logout")
async def logout():
    """
    Logout the current user by clearing auth cookies.
    """
    response = Response()
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    
    return {"message": "Successfully logged out"}