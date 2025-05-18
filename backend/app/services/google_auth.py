import json
from typing import Dict, Optional, Tuple, Any
from uuid import uuid4
from datetime import datetime

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.core.state_storage import StateStorage
from app.db.postgres import get_db
from app.db.models import User
from app.schemas.token import Token
from app.schemas.user import UserResponse

# OAuth2 token endpoint
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/token"
)

class GoogleAuthService:
    """
    Service for handling Google OAuth authentication.
    """
    
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_CALLBACK_URL
        self.token_url = settings.GOOGLE_TOKEN_URL
        self.user_info_url = settings.GOOGLE_USER_INFO_URL
        self.state_storage = StateStorage()
    
    async def get_google_auth_url(self) -> Tuple[str, str]:
        """
        Generate the Google OAuth authorization URL and a new state token.
        """
        state = self.state_storage.generate_state()
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "scope": "openid email profile",
            "redirect_uri": self.redirect_uri,
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
        }
        
        # Construct query string
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{settings.GOOGLE_AUTHORIZE_URL}?{query_string}", state
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange the authorization code for access and refresh tokens.
        """
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, data=data)
            
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange code for token"
            )
        
        return response.json()
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get user information from Google using the access token.
        """
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.user_info_url, headers=headers)
            
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from Google"
            )
        
        return response.json()
    
    async def authenticate_with_google(self, code: str, state: str) -> Tuple[UserResponse, Token]:
        """
        Authenticate user with Google OAuth code.
        
        1. Validate state parameter
        2. Exchange code for tokens
        3. Get user info from Google
        4. Create or update user in database
        5. Generate JWT tokens
        6. Return user and tokens
        """
        # Validate state parameter
        if not self.state_storage.validate_state(state):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state parameter"
            )
        
        # Exchange code for tokens
        google_tokens = await self.exchange_code_for_token(code)
        google_access_token = google_tokens.get("access_token")
        
        if not google_access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Google token response"
            )
        
        # Get user info
        user_info = await self.get_user_info(google_access_token)
        
        # Extract relevant user details
        email = user_info.get("email")
        email_verified = user_info.get("email_verified", False)
        given_name = user_info.get("given_name")
        family_name = user_info.get("family_name")
        picture = user_info.get("picture")
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not found in Google user info"
            )
        
        # Check if user exists
        db_user = self.db.query(User).filter(User.email == email).first()
        
        if db_user:
            # Update existing user
            db_user.first_name = given_name or db_user.first_name
            db_user.last_name = family_name or db_user.last_name
            db_user.email_verified = email_verified
            db_user.last_login = datetime.utcnow()
            db_user.updated_at = datetime.utcnow()
        else:
            # Create new user
            db_user = User(
                user_id=uuid4(),
                email=email,
                first_name=given_name,
                last_name=family_name,
                is_active=True,
                email_verified=email_verified,
                password_hash="", # No password for Google auth users
                last_login=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.db.add(db_user)
        
        # Commit changes
        self.db.commit()
        self.db.refresh(db_user)
        
        # Create JWT tokens
        access_token = create_access_token(subject=str(db_user.user_id))
        refresh_token = create_refresh_token(subject=str(db_user.user_id))
        
        # Prepare response
        user_response = UserResponse(
            user_id=str(db_user.user_id),
            email=db_user.email,
            first_name=db_user.first_name,
            last_name=db_user.last_name,
            is_active=db_user.is_active,
            email_verified=db_user.email_verified
        )
        
        token = Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
        
        return user_response, token
    
    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> UserResponse:
        """
        Get current user from JWT token.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            # Decode JWT token
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            
            # Extract user ID
            user_id = payload.get("sub")
            if not user_id:
                raise credentials_exception
            
            # Get user from database
            db_user = self.db.query(User).filter(User.user_id == user_id).first()
            if not db_user or not db_user.is_active:
                raise credentials_exception
            
            # Return user data
            return UserResponse(
                user_id=str(db_user.user_id),
                email=db_user.email,
                first_name=db_user.first_name,
                last_name=db_user.last_name,
                is_active=db_user.is_active,
                email_verified=db_user.email_verified
            )
            
        except jwt.JWTError:
            raise credentials_exception