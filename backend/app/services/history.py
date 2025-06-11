from typing import List, Optional, Union, Dict, Any
from uuid import UUID
from datetime import date, datetime

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, inspect
from fastapi import HTTPException

from app.db.models import (
    ImmigrationProfile,
    Address,
    AddressHistory,
    Employer, 
    EmploymentHistory,
    Country,
    State,
    City
)
from app.schemas.history import (
    AddressCreate,
    AddressUpdate,
    AddressHistoryCreate,
    AddressHistoryUpdate,
    EmployerCreate,
    EmployerUpdate,
    EmploymentHistoryCreate,
    EmploymentHistoryUpdate,
)


class HistoryService:
    """
    Service for managing address and employment history
    """
    
    def _ensure_uuid(self, value: Union[str, UUID]) -> UUID:
        """Convert string UUID to UUID object if needed"""
        if isinstance(value, str):
            return UUID(value)
        return value

    def _get_user_profile_id(self, db: Session, user_id: Union[str, UUID]) -> UUID:
        """Get the profile_id for a given user_id, create profile if it doesn't exist"""
        user_uuid = self._ensure_uuid(user_id)
        profile = db.query(ImmigrationProfile).filter(ImmigrationProfile.user_id == user_uuid).first()
        
        if not profile:
            # Create a default immigration profile for the user
            profile = ImmigrationProfile(
                user_id=user_uuid,
                profile_type="primary",
                notes="Auto-created profile for history tracking"
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
            
        return profile.profile_id

    # Address Methods
    def get_addresses(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[Address]:
        """
        Get all addresses
        """
        return db.query(Address).offset(skip).limit(limit).all()

    def get_address(self, db: Session, address_id: UUID) -> Optional[Address]:
        """
        Get a specific address by ID
        """
        return db.query(Address).filter(Address.address_id == address_id).first()

    def create_address(self, db: Session, address_in: AddressCreate, user_id: Optional[UUID] = None) -> Address:
        """
        Create a new address
        """
        address_data = address_in.dict()
        
        # Set created_by if user_id is provided
        if user_id:
            address_data["created_by"] = self._ensure_uuid(user_id)
        
        db_address = Address(**address_data)
        db.add(db_address)
        db.commit()
        db.refresh(db_address)
        return db_address

    def update_address(
        self, db: Session, address_id: UUID, address_in: AddressUpdate, user_id: Optional[UUID] = None
    ) -> Optional[Address]:
        """
        Update an address
        """
        db_address = self.get_address(db, address_id)
        if not db_address:
            return None

        update_data = address_in.dict(exclude_unset=True)
        
        # Set updated_by if user_id is provided
        if user_id:
            update_data["updated_by"] = self._ensure_uuid(user_id)
            update_data["updated_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(db_address, field, value)

        db.add(db_address)
        db.commit()
        db.refresh(db_address)
        return db_address

    def delete_address(self, db: Session, address_id: UUID) -> bool:
        """
        Delete an address if it's not referenced by any history records
        """
        db_address = self.get_address(db, address_id)
        if not db_address:
            return False

        # Check if address is referenced by address history
        address_history = db.query(AddressHistory).filter(
            AddressHistory.address_id == address_id
        ).first()
        
        # Check if address is referenced by employer
        employer = db.query(Employer).filter(
            Employer.address_id == address_id
        ).first()
        
        # Check if address is referenced by employment history
        employment_history = db.query(EmploymentHistory).filter(
            EmploymentHistory.work_location_id == address_id
        ).first()
        
        if address_history or employer or employment_history:
            # Address is being referenced, don't delete
            return False

        db.delete(db_address)
        db.commit()
        return True

    # Address History Methods
    def get_user_address_history(
        self, db: Session, user_id: Union[str, UUID], skip: int = 0, limit: int = 100
    ) -> List[AddressHistory]:
        """
        Get address history for a user
        """
        profile_id = self._get_user_profile_id(db, user_id)
        return (
            db.query(AddressHistory)
            .filter(AddressHistory.profile_id == profile_id)
            .order_by(desc(AddressHistory.start_date))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_address_history_entry(
        self, db: Session, user_id: Union[str, UUID], history_id: UUID
    ) -> Optional[AddressHistory]:
        """
        Get a specific address history entry
        """
        profile_id = self._get_user_profile_id(db, user_id)
        return db.query(AddressHistory).filter(
            and_(
                AddressHistory.address_history_id == history_id,
                AddressHistory.profile_id == profile_id
            )
        ).first()

    def create_address_history(
        self, db: Session, user_id: Union[str, UUID], history_in: AddressHistoryCreate
    ) -> AddressHistory:
        """
        Create a new address history entry
        """
        profile_id = self._get_user_profile_id(db, user_id)
        
        # Check if the address exists
        address_id = history_in.address_id
        db_address = self.get_address(db, address_id)
        if not db_address:
            raise HTTPException(status_code=404, detail="Address not found")
        
        # If this is marked as current, set all other address history entries to not current
        if history_in.is_current:
            current_addresses = db.query(AddressHistory).filter(
                and_(
                    AddressHistory.profile_id == profile_id,
                    AddressHistory.is_current.is_(True),
                    AddressHistory.address_type == history_in.address_type
                )
            ).all()
            
            for curr_addr in current_addresses:
                curr_addr.is_current = False
                db.add(curr_addr)
        
        # Create the history entry
        history_data = history_in.dict()
        history_data["profile_id"] = profile_id
        history_data["created_by"] = self._ensure_uuid(user_id)
        
        db_history = AddressHistory(**history_data)
        db.add(db_history)
        db.commit()
        db.refresh(db_history)
        return db_history

    def update_address_history(
        self, db: Session, user_id: Union[str, UUID], history_id: UUID, history_in: AddressHistoryUpdate
    ) -> Optional[AddressHistory]:
        """
        Update an address history entry
        """
        db_history = self.get_address_history_entry(db, user_id, history_id)
        if not db_history:
            return None

        update_data = history_in.dict(exclude_unset=True)
        
        # If is_current is being set to True, update other entries
        if update_data.get("is_current") is True:
            profile_id = self._get_user_profile_id(db, user_id)
            current_addresses = db.query(AddressHistory).filter(
                and_(
                    AddressHistory.profile_id == profile_id,
                    AddressHistory.is_current.is_(True),
                    AddressHistory.address_history_id != history_id,
                    AddressHistory.address_type == (
                        update_data.get("address_type") or db_history.address_type
                    )
                )
            ).all()
            
            for curr_addr in current_addresses:
                curr_addr.is_current = False
                db.add(curr_addr)
        
        # Update the history entry
        update_data["updated_by"] = self._ensure_uuid(user_id)
        update_data["updated_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(db_history, field, value)

        db.add(db_history)
        db.commit()
        db.refresh(db_history)
        return db_history

    def delete_address_history(
        self, db: Session, user_id: Union[str, UUID], history_id: UUID
    ) -> bool:
        """
        Delete an address history entry
        """
        db_history = self.get_address_history_entry(db, user_id, history_id)
        if not db_history:
            return False

        db.delete(db_history)
        db.commit()
        return True

    # Employer Methods
    def get_employers(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[Employer]:
        """
        Get all employers
        """
        return db.query(Employer).offset(skip).limit(limit).all()

    def get_employer(self, db: Session, employer_id: UUID) -> Optional[Employer]:
        """
        Get a specific employer by ID
        """
        return db.query(Employer).filter(Employer.employer_id == employer_id).first()

    def create_employer(
        self, db: Session, employer_in: EmployerCreate, user_id: Optional[UUID] = None
    ) -> Employer:
        """
        Create a new employer
        """
        employer_data = employer_in.dict()
        
        # Set created_by if user_id is provided
        if user_id:
            employer_data["created_by"] = self._ensure_uuid(user_id)
        
        db_employer = Employer(**employer_data)
        db.add(db_employer)
        db.commit()
        db.refresh(db_employer)
        return db_employer

    def update_employer(
        self, db: Session, employer_id: UUID, employer_in: EmployerUpdate, user_id: Optional[UUID] = None
    ) -> Optional[Employer]:
        """
        Update an employer
        """
        db_employer = self.get_employer(db, employer_id)
        if not db_employer:
            return None

        update_data = employer_in.dict(exclude_unset=True)
        
        # Set updated_by if user_id is provided
        if user_id:
            update_data["updated_by"] = self._ensure_uuid(user_id)
            update_data["updated_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(db_employer, field, value)

        db.add(db_employer)
        db.commit()
        db.refresh(db_employer)
        return db_employer

    def delete_employer(self, db: Session, employer_id: UUID) -> bool:
        """
        Delete an employer if it's not referenced by any employment history records
        """
        db_employer = self.get_employer(db, employer_id)
        if not db_employer:
            return False

        # Check if employer is referenced by employment history
        employment_history = db.query(EmploymentHistory).filter(
            EmploymentHistory.employer_id == employer_id
        ).first()
        
        if employment_history:
            # Employer is being referenced, don't delete
            return False

        db.delete(db_employer)
        db.commit()
        return True

    # Employment History Methods
    def get_user_employment_history(
        self, db: Session, user_id: Union[str, UUID], skip: int = 0, limit: int = 100
    ) -> List[EmploymentHistory]:
        """
        Get employment history for a user
        """
        profile_id = self._get_user_profile_id(db, user_id)
        return (
            db.query(EmploymentHistory)
            .filter(EmploymentHistory.profile_id == profile_id)
            .order_by(desc(EmploymentHistory.start_date))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_employment_history_entry(
        self, db: Session, user_id: Union[str, UUID], history_id: UUID
    ) -> Optional[EmploymentHistory]:
        """
        Get a specific employment history entry
        """
        profile_id = self._get_user_profile_id(db, user_id)
        return db.query(EmploymentHistory).filter(
            and_(
                EmploymentHistory.employment_id == history_id,
                EmploymentHistory.profile_id == profile_id
            )
        ).first()

    def create_employment_history(
        self, db: Session, user_id: Union[str, UUID], history_in: EmploymentHistoryCreate
    ) -> EmploymentHistory:
        """
        Create a new employment history entry
        """
        profile_id = self._get_user_profile_id(db, user_id)
        
        # Check if the employer exists
        employer_id = history_in.employer_id
        db_employer = self.get_employer(db, employer_id)
        if not db_employer:
            raise HTTPException(status_code=404, detail="Employer not found")
        
        # If work_location_id is provided, check if it exists
        if history_in.work_location_id:
            db_location = self.get_address(db, history_in.work_location_id)
            if not db_location:
                raise HTTPException(status_code=404, detail="Work location address not found")
        
        # If this is marked as current, set all other employment history entries to not current
        if history_in.is_current:
            current_employments = db.query(EmploymentHistory).filter(
                and_(
                    EmploymentHistory.profile_id == profile_id,
                    EmploymentHistory.is_current.is_(True)
                )
            ).all()
            
            for curr_emp in current_employments:
                curr_emp.is_current = False
                db.add(curr_emp)
        
        # Create the history entry
        history_data = history_in.dict()
        history_data["profile_id"] = profile_id
        history_data["created_by"] = self._ensure_uuid(user_id)
        
        db_history = EmploymentHistory(**history_data)
        db.add(db_history)
        db.commit()
        db.refresh(db_history)
        return db_history

    def update_employment_history(
        self, db: Session, user_id: Union[str, UUID], history_id: UUID, history_in: EmploymentHistoryUpdate
    ) -> Optional[EmploymentHistory]:
        """
        Update an employment history entry
        """
        db_history = self.get_employment_history_entry(db, user_id, history_id)
        if not db_history:
            return None

        update_data = history_in.dict(exclude_unset=True)
        
        # If employer_id is provided, check if it exists
        if update_data.get("employer_id"):
            db_employer = self.get_employer(db, update_data["employer_id"])
            if not db_employer:
                raise HTTPException(status_code=404, detail="Employer not found")
        
        # If work_location_id is provided, check if it exists
        if update_data.get("work_location_id"):
            db_location = self.get_address(db, update_data["work_location_id"])
            if not db_location:
                raise HTTPException(status_code=404, detail="Work location address not found")
        
        # If is_current is being set to True, update other entries
        if update_data.get("is_current") is True:
            profile_id = self._get_user_profile_id(db, user_id)
            current_employments = db.query(EmploymentHistory).filter(
                and_(
                    EmploymentHistory.profile_id == profile_id,
                    EmploymentHistory.is_current.is_(True),
                    EmploymentHistory.employment_id != history_id
                )
            ).all()
            
            for curr_emp in current_employments:
                curr_emp.is_current = False
                db.add(curr_emp)
        
        # Update the history entry
        update_data["updated_by"] = self._ensure_uuid(user_id)
        update_data["updated_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(db_history, field, value)

        db.add(db_history)
        db.commit()
        db.refresh(db_history)
        return db_history

    def delete_employment_history(
        self, db: Session, user_id: Union[str, UUID], history_id: UUID
    ) -> bool:
        """
        Delete an employment history entry
        """
        db_history = self.get_employment_history_entry(db, user_id, history_id)
        if not db_history:
            return False

        db.delete(db_history)
        db.commit()
        return True

    # Validation for H1-B employment requirements
    def validate_h1b_employment(
        self, db: Session, user_id: Union[str, UUID], employment_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Validate employment history for H1-B compliance
        
        Returns a dictionary with validation results:
        {
            "is_valid": True/False,
            "issues": ["List of compliance issues"],
            "warnings": ["List of warnings"]
        }
        """
        profile_id = self._get_user_profile_id(db, user_id)
        
        # Initialize results
        results = {
            "is_valid": True,
            "issues": [],
            "warnings": []
        }
        
        # Get the employment history entry if provided
        employment = None
        if employment_id:
            employment = self.get_employment_history_entry(db, user_id, employment_id)
            if not employment:
                results["is_valid"] = False
                results["issues"].append("Employment history entry not found")
                return results
        
        # Get all employment history for validation
        employment_history = self.get_user_employment_history(db, user_id)
        
        # Validation logic for H1-B:
        # 1. Check for gaps in employment
        # 2. Verify employment types (must be full-time for H1-B)
        # 3. Check for working hours compliance (must be at least 35 hours/week)
        # 4. Verify employer information is complete
        
        # Sort employment by start date
        sorted_history = sorted(employment_history, key=lambda x: x.start_date)
        
        # Check for gaps
        for i in range(1, len(sorted_history)):
            prev_end = sorted_history[i-1].end_date
            curr_start = sorted_history[i].start_date
            
            if prev_end and curr_start:
                # Calculate days between jobs
                gap_days = (curr_start - prev_end).days - 1
                
                if gap_days > 60:
                    results["is_valid"] = False
                    results["issues"].append(
                        f"Gap of {gap_days} days between jobs exceeds 60-day H1-B grace period"
                    )
                elif gap_days > 0:
                    results["warnings"].append(
                        f"Gap of {gap_days} days detected between jobs (within grace period)"
                    )
        
        # Check current or provided employment
        target_employment = employment if employment else next(
            (e for e in employment_history if e.is_current), None
        )
        
        if target_employment:
            # Check employment type
            if target_employment.employment_type and target_employment.employment_type.lower() != "full-time":
                results["is_valid"] = False
                results["issues"].append(
                    f"H1-B requires full-time employment, but current type is {target_employment.employment_type}"
                )
            
            # Check working hours
            if target_employment.working_hours_per_week:
                if target_employment.working_hours_per_week < 35:
                    results["is_valid"] = False
                    results["issues"].append(
                        f"H1-B requires at least 35 hours/week, but current is {target_employment.working_hours_per_week}"
                    )
            else:
                results["warnings"].append("Working hours not specified - H1-B requires at least 35 hours/week")
            
            # Check employer information
            employer = db.query(Employer).filter(Employer.employer_id == target_employment.employer_id).first()
            if employer:
                if not employer.company_ein:
                    results["warnings"].append("Employer EIN not specified - this is required for H1-B petitions")
            
        else:
            results["is_valid"] = False
            results["issues"].append("No current employment found - H1-B requires continuous employment")
        
        return results


# Create service instance
history_service = HistoryService()