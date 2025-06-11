"""
Debug endpoint for troubleshooting requests.
"""
from typing import Any, Dict, Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Request, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator

router = APIRouter()

class AddressHistoryDebug(BaseModel):
    address_id: UUID
    start_date: date
    end_date: Optional[date] = None
    is_current: bool = False
    address_type: Optional[str] = None
    verification_document_id: Optional[UUID] = None

@router.post("/debug-request")
async def debug_request(request: Request) -> Dict[str, Any]:
    """
    Debug endpoint that logs request body and returns it for inspection.
    """
    body = await request.json()
    print("DEBUG REQUEST BODY:", body)
    
    # Check for UUIDs
    uuid_fields = ["address_id", "verification_document_id", "profile_id"]
    for field in uuid_fields:
        if field in body:
            print(f"DEBUG {field}:", body[field], "Type:", type(body[field]))
    
    # Check for date fields
    date_fields = ["start_date", "end_date"]
    for field in date_fields:
        if field in body:
            print(f"DEBUG {field}:", body[field], "Type:", type(body[field]))
    
    return {
        "received_data": body,
        "content_type": request.headers.get("content-type"),
        "message": "This is a debug endpoint to help troubleshoot request issues."
    }

@router.post("/validate-address-history")
async def validate_address_history(data: AddressHistoryDebug) -> Dict[str, Any]:
    """
    Validate address history data against the expected schema.
    """
    return {
        "valid": True,
        "data": {
            "address_id": str(data.address_id),
            "start_date": data.start_date.isoformat(),
            "end_date": data.end_date.isoformat() if data.end_date else None,
            "is_current": data.is_current,
            "address_type": data.address_type,
            "verification_document_id": str(data.verification_document_id) if data.verification_document_id else None
        },
        "message": "Data is valid and properly parsed."
    }