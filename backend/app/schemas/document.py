from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime


class DocumentBase(BaseModel):
    document_type: str  # passport, visa, I-797, I-94, etc.
    document_subtype: Optional[str] = None  # optional subcategory
    document_number: Optional[str] = None
    issuing_authority: Optional[str] = None
    related_immigration_type: Optional[str] = None  # H1-B, L-1, OPT, etc.
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    tags: Optional[List[str]] = None


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    document_type: Optional[str] = None
    document_subtype: Optional[str] = None
    document_number: Optional[str] = None
    issuing_authority: Optional[str] = None
    related_immigration_type: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    tags: Optional[List[str]] = None
    is_verified: Optional[bool] = None


class DocumentResponse(DocumentBase):
    document_id: str
    user_id: str
    file_name: str
    file_size: int
    file_type: str  # MIME type
    is_verified: bool = False
    upload_date: datetime
    tags: List[str] = []
    extraction_data: Optional[dict] = None  # Contains extraction results if available


class DocumentExtractResponse(BaseModel):
    extracted_fields: dict
    confidence_score: float