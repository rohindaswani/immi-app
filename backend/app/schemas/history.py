from datetime import date, datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, validator, EmailStr
from enum import Enum

# Address History Schemas
class AddressBase(BaseModel):
    street_address_1: str = Field(..., max_length=255)
    street_address_2: Optional[str] = Field(None, max_length=255)
    city_id: Optional[UUID] = None
    state_id: Optional[UUID] = None
    zip_code: Optional[str] = Field(None, max_length=20)
    country_id: UUID
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address_type: Optional[str] = Field(None, max_length=100)  # Home, work, mailing, etc.
    is_verified: Optional[bool] = False
    verification_date: Optional[date] = None

class AddressCreate(AddressBase):
    pass

class AddressUpdate(BaseModel):
    street_address_1: Optional[str] = Field(None, max_length=255)
    street_address_2: Optional[str] = Field(None, max_length=255)
    city_id: Optional[UUID] = None
    state_id: Optional[UUID] = None
    zip_code: Optional[str] = Field(None, max_length=20)
    country_id: Optional[UUID] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address_type: Optional[str] = Field(None, max_length=100)
    is_verified: Optional[bool] = None
    verification_date: Optional[date] = None

class AddressInDB(AddressBase):
    address_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None

    class Config:
        from_attributes = True

class Address(AddressInDB):
    city_name: Optional[str] = None
    state_name: Optional[str] = None
    country_name: Optional[str] = None

class AddressHistoryBase(BaseModel):
    address_id: UUID
    start_date: date
    end_date: Optional[date] = None
    is_current: bool = False
    address_type: Optional[str] = Field(None, max_length=100)  # residential, mailing, work
    verification_document_id: Optional[UUID] = None

class AddressHistoryCreate(AddressHistoryBase):
    profile_id: Optional[UUID] = None  # Will be set from the user_id in the service

class AddressHistoryUpdate(BaseModel):
    address_id: Optional[UUID] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None
    address_type: Optional[str] = Field(None, max_length=100)
    verification_document_id: Optional[UUID] = None

class AddressHistoryInDB(AddressHistoryBase):
    address_history_id: UUID
    profile_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None

    class Config:
        from_attributes = True

class AddressHistory(AddressHistoryInDB):
    address: Optional[Address] = None

# Employer Schemas
class EmployerBase(BaseModel):
    company_name: str = Field(..., max_length=255)
    company_ein: Optional[str] = Field(None, max_length=20)  # Employer Identification Number
    company_type: Optional[str] = Field(None, max_length=100)  # Corporation, LLC, etc.
    industry: Optional[str] = Field(None, max_length=100)
    address_id: Optional[UUID] = None
    contact_name: Optional[str] = Field(None, max_length=255)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=50)
    is_verified: Optional[bool] = False
    verification_date: Optional[date] = None

class EmployerCreate(EmployerBase):
    pass

class EmployerUpdate(BaseModel):
    company_name: Optional[str] = Field(None, max_length=255)
    company_ein: Optional[str] = Field(None, max_length=20)
    company_type: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    address_id: Optional[UUID] = None
    contact_name: Optional[str] = Field(None, max_length=255)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=50)
    is_verified: Optional[bool] = None
    verification_date: Optional[date] = None

class EmployerInDB(EmployerBase):
    employer_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None

    class Config:
        from_attributes = True

class Employer(EmployerInDB):
    address: Optional[Address] = None

# Employment History Schemas
class EmploymentHistoryBase(BaseModel):
    employer_id: UUID
    job_title: str = Field(..., max_length=255)
    job_description: Optional[str] = None
    department: Optional[str] = Field(None, max_length=255)
    employment_type: Optional[str] = Field(None, max_length=50)  # Full-time, Part-time, Contract, etc.
    start_date: date
    end_date: Optional[date] = None
    is_current: bool = False
    salary: Optional[float] = None
    salary_frequency: Optional[str] = Field(None, max_length=20)  # Annual, Monthly, Hourly, etc.
    working_hours_per_week: Optional[float] = None
    work_location_id: Optional[UUID] = None
    supervisor_name: Optional[str] = Field(None, max_length=255)
    supervisor_title: Optional[str] = Field(None, max_length=255)
    supervisor_phone: Optional[str] = Field(None, max_length=50)
    supervisor_email: Optional[EmailStr] = None
    termination_reason: Optional[str] = Field(None, max_length=255)
    is_verified: Optional[bool] = False
    verification_document_id: Optional[UUID] = None

class EmploymentHistoryCreate(EmploymentHistoryBase):
    profile_id: Optional[UUID] = None  # Will be set from the user_id in the service

class EmploymentHistoryUpdate(BaseModel):
    employer_id: Optional[UUID] = None
    job_title: Optional[str] = Field(None, max_length=255)
    job_description: Optional[str] = None
    department: Optional[str] = Field(None, max_length=255)
    employment_type: Optional[str] = Field(None, max_length=50)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None
    salary: Optional[float] = None
    salary_frequency: Optional[str] = Field(None, max_length=20)
    working_hours_per_week: Optional[float] = None
    work_location_id: Optional[UUID] = None
    supervisor_name: Optional[str] = Field(None, max_length=255)
    supervisor_title: Optional[str] = Field(None, max_length=255)
    supervisor_phone: Optional[str] = Field(None, max_length=50)
    supervisor_email: Optional[EmailStr] = None
    termination_reason: Optional[str] = Field(None, max_length=255)
    is_verified: Optional[bool] = None
    verification_document_id: Optional[UUID] = None

class EmploymentHistoryInDB(EmploymentHistoryBase):
    employment_id: UUID
    profile_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None

    class Config:
        from_attributes = True

class EmploymentHistory(EmploymentHistoryInDB):
    employer: Optional[Employer] = None
    work_location: Optional[Address] = None

# Extended schemas for nested relationships
class EmploymentHistoryWithDetails(EmploymentHistory):
    pass

class AddressHistoryWithDetails(AddressHistory):
    pass