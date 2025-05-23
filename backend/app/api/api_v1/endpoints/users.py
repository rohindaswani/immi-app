from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.schemas.user import UserResponse, UserUpdate
from app.schemas.user_settings import UserSettings
from app.services.user import UserService
from app.core.security import get_current_user
from app.db.postgres import get_db
from app.db.models import User

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user information.
    TEMPORARY: Returns test data for development.
    """
    # TEMPORARY: Return test user data for development/testing
    # TODO: Remove this and uncomment the real database query below
    return UserResponse(
        user_id=current_user_id,
        email="test@example.com",
        first_name="Test",
        last_name="User",
        is_active=True,
        email_verified=True
    )
    
    # Real database query (commented out for testing):
    """
    # Get user from database
    user = db.query(User).filter(User.user_id == current_user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        user_id=str(user.user_id),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        email_verified=user.email_verified
    )
    """


@router.put("/me", response_model=UserResponse)
async def update_current_user(user_data: UserUpdate):
    """
    Update current user information.
    """
    # This will be implemented once the user service is created
    # return await user_service.update_current_user(user_data)
    
    # Placeholder response
    return {
        "user_id": "example-user-id",
        "email": "user@example.com",
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "is_active": True,
        "email_verified": True
    }


@router.get("/me/settings", response_model=UserSettings)
async def get_user_settings():
    """
    Get current user settings.
    """
    # This will be implemented once the user service is created
    # return await user_service.get_settings()
    
    # Placeholder response
    return {
        "setting_id": "example-setting-id",
        "user_id": "example-user-id",
        "notification_preferences": {
            "email": True,
            "in_app": True
        },
        "ui_preferences": {
            "theme": "light",
            "language": "en"
        },
        "time_zone": "America/New_York",
        "language_preference": "en"
    }


@router.put("/me/settings", response_model=UserSettings)
async def update_user_settings(settings_data: UserSettings):
    """
    Update current user settings.
    """
    # This will be implemented once the user service is created
    # return await user_service.update_settings(settings_data)
    
    # Placeholder response
    return {
        "setting_id": "example-setting-id",
        "user_id": "example-user-id",
        "notification_preferences": settings_data.notification_preferences,
        "ui_preferences": settings_data.ui_preferences,
        "time_zone": settings_data.time_zone,
        "language_preference": settings_data.language_preference
    }