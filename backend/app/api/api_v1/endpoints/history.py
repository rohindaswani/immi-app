from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.db.models import User
from app.services.history import history_service
from app.schemas.history import (
    Address,
    AddressCreate,
    AddressUpdate,
    AddressHistory,
    AddressHistoryCreate,
    AddressHistoryUpdate,
    Employer,
    EmployerCreate,
    EmployerUpdate,
    EmploymentHistory,
    EmploymentHistoryCreate,
    EmploymentHistoryUpdate
)

router = APIRouter()

# Address endpoints
@router.get("/addresses", response_model=List[Address])
def get_addresses(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user_id: str = Depends(get_current_user)
):
    """
    Get all addresses
    """
    return history_service.get_addresses(db, skip=skip, limit=limit)

@router.post("/addresses", response_model=Address)
def create_address(
    address_in: AddressCreate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
):
    """
    Create a new address
    """
    return history_service.create_address(db, address_in, user_id=current_user_id)

@router.get("/addresses/{address_id}", response_model=Address)
def get_address(
    address_id: UUID = Path(...),
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
):
    """
    Get a specific address by ID
    """
    address = history_service.get_address(db, address_id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return address

@router.put("/addresses/{address_id}", response_model=Address)
def update_address(
    address_in: AddressUpdate,
    address_id: UUID = Path(...),
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
):
    """
    Update an address
    """
    address = history_service.update_address(
        db, address_id, address_in, user_id=current_user_id
    )
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return address

@router.delete("/addresses/{address_id}")
def delete_address(
    address_id: UUID = Path(...),
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
):
    """
    Delete an address if it's not referenced by any history records
    """
    success = history_service.delete_address(db, address_id)
    if not success:
        raise HTTPException(
            status_code=400, 
            detail="Address cannot be deleted as it is referenced by other records"
        )
    return {"message": "Address deleted successfully"}

# Address History endpoints
@router.get("/address-history", response_model=List[AddressHistory])
def get_address_history(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user_id: str = Depends(get_current_user)
):
    """
    Get address history for current user
    """
    return history_service.get_user_address_history(
        db, current_user_id, skip=skip, limit=limit
    )

@router.post("/address-history", response_model=AddressHistory)
def create_address_history(
    history_in: AddressHistoryCreate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
):
    """
    Create a new address history entry
    """
    try:
        return history_service.create_address_history(
            db, current_user_id, history_in
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/address-history/{history_id}", response_model=AddressHistory)
def get_address_history_entry(
    history_id: UUID = Path(...),
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
):
    """
    Get a specific address history entry
    """
    entry = history_service.get_address_history_entry(
        db, current_user_id, history_id
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Address history entry not found")
    return entry

@router.put("/address-history/{history_id}", response_model=AddressHistory)
def update_address_history_entry(
    history_in: AddressHistoryUpdate,
    history_id: UUID = Path(...),
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
):
    """
    Update an address history entry
    """
    entry = history_service.update_address_history(
        db, current_user_id, history_id, history_in
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Address history entry not found")
    return entry

@router.delete("/address-history/{history_id}")
def delete_address_history_entry(
    history_id: UUID = Path(...),
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
):
    """
    Delete an address history entry
    """
    success = history_service.delete_address_history(
        db, current_user_id, history_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Address history entry not found")
    return {"message": "Address history entry deleted successfully"}

# Employer endpoints
@router.get("/employers", response_model=List[Employer])
def get_employers(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user_id: str = Depends(get_current_user)
):
    """
    Get all employers
    """
    return history_service.get_employers(db, skip=skip, limit=limit)

@router.post("/employers", response_model=Employer)
def create_employer(
    employer_in: EmployerCreate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
):
    """
    Create a new employer
    """
    return history_service.create_employer(db, employer_in, user_id=current_user_id)

@router.get("/employers/{employer_id}", response_model=Employer)
def get_employer(
    employer_id: UUID = Path(...),
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
):
    """
    Get a specific employer by ID
    """
    employer = history_service.get_employer(db, employer_id)
    if not employer:
        raise HTTPException(status_code=404, detail="Employer not found")
    return employer

@router.put("/employers/{employer_id}", response_model=Employer)
def update_employer(
    employer_in: EmployerUpdate,
    employer_id: UUID = Path(...),
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
):
    """
    Update an employer
    """
    employer = history_service.update_employer(
        db, employer_id, employer_in, user_id=current_user_id
    )
    if not employer:
        raise HTTPException(status_code=404, detail="Employer not found")
    return employer

@router.delete("/employers/{employer_id}")
def delete_employer(
    employer_id: UUID = Path(...),
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
):
    """
    Delete an employer if it's not referenced by any employment history records
    """
    success = history_service.delete_employer(db, employer_id)
    if not success:
        raise HTTPException(
            status_code=400, 
            detail="Employer cannot be deleted as it is referenced by employment history records"
        )
    return {"message": "Employer deleted successfully"}

# Employment History endpoints
@router.get("/employment-history", response_model=List[EmploymentHistory])
def get_employment_history(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user_id: str = Depends(get_current_user)
):
    """
    Get employment history for current user
    """
    return history_service.get_user_employment_history(
        db, current_user_id, skip=skip, limit=limit
    )

@router.post("/employment-history", response_model=EmploymentHistory)
def create_employment_history(
    history_in: EmploymentHistoryCreate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
):
    """
    Create a new employment history entry
    """
    try:
        return history_service.create_employment_history(
            db, current_user_id, history_in
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/employment-history/{history_id}", response_model=EmploymentHistory)
def get_employment_history_entry(
    history_id: UUID = Path(...),
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
):
    """
    Get a specific employment history entry
    """
    entry = history_service.get_employment_history_entry(
        db, current_user_id, history_id
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Employment history entry not found")
    return entry

@router.put("/employment-history/{history_id}", response_model=EmploymentHistory)
def update_employment_history_entry(
    history_in: EmploymentHistoryUpdate,
    history_id: UUID = Path(...),
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
):
    """
    Update an employment history entry
    """
    entry = history_service.update_employment_history(
        db, current_user_id, history_id, history_in
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Employment history entry not found")
    return entry

@router.delete("/employment-history/{history_id}")
def delete_employment_history_entry(
    history_id: UUID = Path(...),
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
):
    """
    Delete an employment history entry
    """
    success = history_service.delete_employment_history(
        db, current_user_id, history_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Employment history entry not found")
    return {"message": "Employment history entry deleted successfully"}

# H1-B Validation endpoint
@router.get("/employment-history/{history_id}/validate-h1b")
def validate_h1b_employment(
    history_id: UUID = Path(...),  # Use ... to indicate required parameter
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
):
    """
    Validate employment history for H1-B compliance
    """
    results = history_service.validate_h1b_employment(
        db, current_user_id, history_id
    )
    return results

# Validation endpoint for all employment history
@router.get("/validate-h1b")
def validate_all_h1b_employment(
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
):
    """
    Validate all employment history for H1-B compliance
    """
    results = history_service.validate_h1b_employment(
        db, current_user_id
    )
    return results