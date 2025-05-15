from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpdate
from app.services.profile import ProfileService

router = APIRouter()

profile_service = ProfileService()

@router.get("/", response_model=List[ProfileResponse])
async def get_profiles():
    """
    Get all profiles for the current user.
    """
    # This will be implemented once the profile service is created
    # return await profile_service.get_profiles()
    
    # Placeholder response
    return [
        {
            "profile_id": "example-profile-id",
            "user_id": "example-user-id",
            "current_status": {
                "status_code": "H1-B",
                "status_name": "H-1B Specialty Occupation",
                "status_category": "Employment"
            },
            "most_recent_i94_number": "1234567890",
            "most_recent_entry_date": "2023-01-15",
            "immigration_goals": "Maintain H1-B status and eventually apply for a green card",
            "authorized_stay_until": "2026-01-14",
            "visa_expiry_date": "2026-01-14",
            "passport_expiry_date": "2030-05-20",
            "is_primary_beneficiary": True
        }
    ]


@router.post("/", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(profile_data: ProfileCreate):
    """
    Create a new immigration profile.
    """
    # This will be implemented once the profile service is created
    # return await profile_service.create_profile(profile_data)
    
    # Placeholder response
    return {
        "profile_id": "new-profile-id",
        "user_id": "example-user-id",
        "current_status": {
            "status_code": profile_data.current_status_code,
            "status_name": "H-1B Specialty Occupation",
            "status_category": "Employment"
        },
        "most_recent_i94_number": profile_data.most_recent_i94_number,
        "most_recent_entry_date": profile_data.most_recent_entry_date,
        "immigration_goals": profile_data.immigration_goals,
        "authorized_stay_until": profile_data.authorized_stay_until,
        "visa_expiry_date": profile_data.visa_expiry_date,
        "passport_expiry_date": profile_data.passport_expiry_date,
        "is_primary_beneficiary": profile_data.is_primary_beneficiary
    }


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(profile_id: str):
    """
    Get a specific immigration profile by ID.
    """
    # This will be implemented once the profile service is created
    # return await profile_service.get_profile(profile_id)
    
    # Placeholder response
    return {
        "profile_id": profile_id,
        "user_id": "example-user-id",
        "current_status": {
            "status_code": "H1-B",
            "status_name": "H-1B Specialty Occupation",
            "status_category": "Employment"
        },
        "most_recent_i94_number": "1234567890",
        "most_recent_entry_date": "2023-01-15",
        "immigration_goals": "Maintain H1-B status and eventually apply for a green card",
        "authorized_stay_until": "2026-01-14",
        "visa_expiry_date": "2026-01-14",
        "passport_expiry_date": "2030-05-20",
        "is_primary_beneficiary": True
    }


@router.put("/{profile_id}", response_model=ProfileResponse)
async def update_profile(profile_id: str, profile_data: ProfileUpdate):
    """
    Update a specific immigration profile.
    """
    # This will be implemented once the profile service is created
    # return await profile_service.update_profile(profile_id, profile_data)
    
    # Placeholder response
    return {
        "profile_id": profile_id,
        "user_id": "example-user-id",
        "current_status": {
            "status_code": profile_data.current_status_code or "H1-B",
            "status_name": "H-1B Specialty Occupation",
            "status_category": "Employment"
        },
        "most_recent_i94_number": profile_data.most_recent_i94_number or "1234567890",
        "most_recent_entry_date": profile_data.most_recent_entry_date or "2023-01-15",
        "immigration_goals": profile_data.immigration_goals or "Maintain H1-B status and eventually apply for a green card",
        "authorized_stay_until": profile_data.authorized_stay_until or "2026-01-14",
        "visa_expiry_date": profile_data.visa_expiry_date or "2026-01-14",
        "passport_expiry_date": profile_data.passport_expiry_date or "2030-05-20",
        "is_primary_beneficiary": profile_data.is_primary_beneficiary if profile_data.is_primary_beneficiary is not None else True
    }