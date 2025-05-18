from typing import List, Optional
from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status

from app.db.postgres import get_db
from app.db.models import ImmigrationProfile, ImmigrationStatus
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse, ImmigrationStatus as ImmigrationStatusSchema


class ProfileService:
    """
    Service for immigration profile operations.
    """
    
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
    
    async def get_profiles(self, user_id: str) -> List[ProfileResponse]:
        """
        Get all profiles for a user.
        """
        profiles = self.db.query(ImmigrationProfile).filter(
            ImmigrationProfile.user_id == user_id
        ).all()
        
        return [self._map_to_response(profile) for profile in profiles]
    
    async def get_profile(self, profile_id: str, user_id: str) -> Optional[ProfileResponse]:
        """
        Get a specific profile by ID.
        """
        profile = self.db.query(ImmigrationProfile).filter(
            ImmigrationProfile.profile_id == profile_id,
            ImmigrationProfile.user_id == user_id
        ).first()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        return self._map_to_response(profile)
    
    async def create_profile(self, user_id: str, profile_data: ProfileCreate) -> ProfileResponse:
        """
        Create a new immigration profile.
        """
        # Verify the immigration status exists
        status = self.db.query(ImmigrationStatus).filter(
            ImmigrationStatus.status_code == profile_data.current_status_code
        ).first()
        
        if not status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Immigration status with code {profile_data.current_status_code} not found"
            )
        
        # Create new profile
        new_profile = ImmigrationProfile(
            profile_id=uuid4(),
            user_id=user_id,
            current_status_id=status.status_id,
            most_recent_i94_number=profile_data.most_recent_i94_number,
            most_recent_entry_date=profile_data.most_recent_entry_date,
            immigration_goals=profile_data.immigration_goals,
            alien_registration_number=profile_data.alien_registration_number,
            authorized_stay_until=profile_data.authorized_stay_until,
            ead_expiry_date=profile_data.ead_expiry_date,
            visa_expiry_date=profile_data.visa_expiry_date,
            passport_number=profile_data.passport_number,
            passport_country_id=profile_data.passport_country_id,
            passport_expiry_date=profile_data.passport_expiry_date,
            is_primary_beneficiary=profile_data.is_primary_beneficiary,
            primary_beneficiary_id=profile_data.primary_beneficiary_id,
            profile_type=profile_data.profile_type,
            notes=profile_data.notes,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(new_profile)
        self.db.commit()
        self.db.refresh(new_profile)
        
        return self._map_to_response(new_profile)
    
    async def update_profile(self, profile_id: str, user_id: str, profile_data: ProfileUpdate) -> Optional[ProfileResponse]:
        """
        Update an immigration profile.
        """
        # Get the profile
        profile = self.db.query(ImmigrationProfile).filter(
            ImmigrationProfile.profile_id == profile_id,
            ImmigrationProfile.user_id == user_id
        ).first()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        # Update status if provided
        if profile_data.current_status_code:
            status = self.db.query(ImmigrationStatus).filter(
                ImmigrationStatus.status_code == profile_data.current_status_code
            ).first()
            
            if not status:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Immigration status with code {profile_data.current_status_code} not found"
                )
            
            profile.current_status_id = status.status_id
        
        # Update fields if provided
        update_data = profile_data.dict(exclude_unset=True)
        
        for key, value in update_data.items():
            if key != 'current_status_code' and hasattr(profile, key) and value is not None:
                setattr(profile, key, value)
        
        # Update timestamps
        profile.updated_at = datetime.utcnow()
        profile.updated_by = user_id
        
        # Commit changes
        self.db.commit()
        self.db.refresh(profile)
        
        return self._map_to_response(profile)
    
    async def delete_profile(self, profile_id: str, user_id: str) -> bool:
        """
        Delete an immigration profile.
        """
        profile = self.db.query(ImmigrationProfile).filter(
            ImmigrationProfile.profile_id == profile_id,
            ImmigrationProfile.user_id == user_id
        ).first()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        self.db.delete(profile)
        self.db.commit()
        
        return True
    
    def _map_to_response(self, profile: ImmigrationProfile) -> ProfileResponse:
        """
        Map a database profile to a response schema.
        """
        status = profile.current_status
        
        return ProfileResponse(
            profile_id=str(profile.profile_id),
            user_id=str(profile.user_id),
            current_status=ImmigrationStatusSchema(
                status_code=status.status_code,
                status_name=status.status_name,
                status_category=status.status_category
            ),
            most_recent_i94_number=profile.most_recent_i94_number,
            most_recent_entry_date=profile.most_recent_entry_date,
            immigration_goals=profile.immigration_goals,
            alien_registration_number=profile.alien_registration_number,
            authorized_stay_until=profile.authorized_stay_until,
            ead_expiry_date=profile.ead_expiry_date,
            visa_expiry_date=profile.visa_expiry_date,
            passport_number=profile.passport_number,
            passport_country_id=str(profile.passport_country_id) if profile.passport_country_id else None,
            passport_expiry_date=profile.passport_expiry_date,
            is_primary_beneficiary=profile.is_primary_beneficiary,
            primary_beneficiary_id=str(profile.primary_beneficiary_id) if profile.primary_beneficiary_id else None,
            profile_type=profile.profile_type,
            notes=profile.notes
        )