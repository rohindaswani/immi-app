from pydantic import BaseModel
from typing import Optional, Dict
from datetime import date


class ImmigrationStatus(BaseModel):
    status_code: str
    status_name: str
    status_category: str


class ProfileBase(BaseModel):
    current_status_code: str
    most_recent_i94_number: Optional[str] = None
    most_recent_entry_date: Optional[date] = None
    immigration_goals: Optional[str] = None
    alien_registration_number: Optional[str] = None
    authorized_stay_until: Optional[date] = None
    ead_expiry_date: Optional[date] = None
    visa_expiry_date: Optional[date] = None
    passport_number: Optional[str] = None
    passport_country_id: Optional[str] = None
    passport_expiry_date: Optional[date] = None
    is_primary_beneficiary: bool = True
    primary_beneficiary_id: Optional[str] = None
    profile_type: str = "primary"  # primary or dependent
    notes: Optional[str] = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(BaseModel):
    current_status_code: Optional[str] = None
    most_recent_i94_number: Optional[str] = None
    most_recent_entry_date: Optional[date] = None
    immigration_goals: Optional[str] = None
    alien_registration_number: Optional[str] = None
    authorized_stay_until: Optional[date] = None
    ead_expiry_date: Optional[date] = None
    visa_expiry_date: Optional[date] = None
    passport_number: Optional[str] = None
    passport_country_id: Optional[str] = None
    passport_expiry_date: Optional[date] = None
    is_primary_beneficiary: Optional[bool] = None
    primary_beneficiary_id: Optional[str] = None
    profile_type: Optional[str] = None
    notes: Optional[str] = None


class ProfileResponse(BaseModel):
    profile_id: str
    user_id: str
    current_status: ImmigrationStatus
    most_recent_i94_number: Optional[str] = None
    most_recent_entry_date: Optional[date] = None
    immigration_goals: Optional[str] = None
    alien_registration_number: Optional[str] = None
    authorized_stay_until: Optional[date] = None
    ead_expiry_date: Optional[date] = None
    visa_expiry_date: Optional[date] = None
    passport_number: Optional[str] = None
    passport_country_id: Optional[str] = None
    passport_expiry_date: Optional[date] = None
    is_primary_beneficiary: bool
    primary_beneficiary_id: Optional[str] = None
    profile_type: str
    notes: Optional[str] = None