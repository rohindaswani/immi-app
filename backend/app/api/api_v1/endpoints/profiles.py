from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpdate
from app.services.profile import ProfileService
from app.services.google_auth import GoogleAuthService

router = APIRouter()

@router.get("/", response_model=List[ProfileResponse])
async def get_profiles(
    current_user = Depends(GoogleAuthService.get_current_user),
    profile_service: ProfileService = Depends()
):
    """
    Get all profiles for the current user.
    """
    return await profile_service.get_profiles(user_id=str(current_user.user_id))


@router.post("/", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: ProfileCreate,
    current_user = Depends(GoogleAuthService.get_current_user),
    profile_service: ProfileService = Depends()
):
    """
    Create a new immigration profile.
    """
    return await profile_service.create_profile(
        user_id=str(current_user.user_id),
        profile_data=profile_data
    )


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: str,
    current_user = Depends(GoogleAuthService.get_current_user),
    profile_service: ProfileService = Depends()
):
    """
    Get a specific immigration profile by ID.
    """
    return await profile_service.get_profile(
        profile_id=profile_id,
        user_id=str(current_user.user_id)
    )


@router.put("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: str,
    profile_data: ProfileUpdate,
    current_user = Depends(GoogleAuthService.get_current_user),
    profile_service: ProfileService = Depends()
):
    """
    Update a specific immigration profile.
    """
    return await profile_service.update_profile(
        profile_id=profile_id,
        user_id=str(current_user.user_id),
        profile_data=profile_data
    )


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile_id: str,
    current_user = Depends(GoogleAuthService.get_current_user),
    profile_service: ProfileService = Depends()
):
    """
    Delete a specific immigration profile.
    """
    await profile_service.delete_profile(
        profile_id=profile_id,
        user_id=str(current_user.user_id)
    )
    return None