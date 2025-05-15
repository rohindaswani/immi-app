from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse
from app.services.auth import AuthService

router = APIRouter()

auth_service = AuthService()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Register a new user.
    """
    # This will be implemented once the auth service is created
    # return await auth_service.register_user(user_data)
    
    # Placeholder response
    return {
        "user_id": "example-user-id",
        "email": user_data.email,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "is_active": True,
        "email_verified": False
    }


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    # This will be implemented once the auth service is created
    # return await auth_service.authenticate_user(form_data.username, form_data.password)
    
    # Placeholder response
    return {
        "access_token": "example-access-token",
        "refresh_token": "example-refresh-token",
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    """
    Refresh access token.
    """
    # This will be implemented once the auth service is created
    # return await auth_service.refresh_token(refresh_token)
    
    # Placeholder response
    return {
        "access_token": "new-example-access-token",
        "refresh_token": "new-example-refresh-token",
        "token_type": "bearer"
    }


@router.post("/logout")
async def logout():
    """
    Logout current user.
    """
    # This will be implemented once the auth service is created
    # return await auth_service.logout()
    
    # Placeholder response
    return {"message": "Successfully logged out"}