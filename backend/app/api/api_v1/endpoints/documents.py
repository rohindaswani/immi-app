from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session

from app.schemas.document import DocumentResponse, DocumentCreate, DocumentUpdate
from app.services.document import DocumentService
from app.core.security import get_current_user
from app.db.postgres import get_db

router = APIRouter()

@router.get("/", response_model=List[DocumentResponse])
async def get_documents(
    document_type: Optional[str] = None,
    expiry_before: Optional[str] = None,
    expiry_after: Optional[str] = None,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all documents for the current user with optional filtering.
    """
    document_service = DocumentService(db)
    
    # Parse date strings if provided
    expiry_before_date = None
    expiry_after_date = None
    
    if expiry_before:
        try:
            expiry_before_date = date.fromisoformat(expiry_before)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid expiry_before date format. Use YYYY-MM-DD.")
            
    if expiry_after:
        try:
            expiry_after_date = date.fromisoformat(expiry_after)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid expiry_after date format. Use YYYY-MM-DD.")
    
    return await document_service.get_documents(
        user_id=current_user,
        document_type=document_type,
        expiry_before=expiry_before_date,
        expiry_after=expiry_after_date
    )


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    document_subtype: Optional[str] = Form(None),
    document_number: Optional[str] = Form(None),
    issuing_authority: Optional[str] = Form(None),
    related_immigration_type: Optional[str] = Form(None),
    issue_date: Optional[str] = Form(None),
    expiry_date: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a new document with metadata.
    """
    document_service = DocumentService(db)
    
    # Parse dates if provided
    issue_date_parsed = None
    expiry_date_parsed = None
    
    if issue_date:
        try:
            issue_date_parsed = date.fromisoformat(issue_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid issue_date format. Use YYYY-MM-DD.")
            
    if expiry_date:
        try:
            expiry_date_parsed = date.fromisoformat(expiry_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid expiry_date format. Use YYYY-MM-DD.")
    
    # Parse tags if provided
    tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
    
    # Create document data
    document_data = DocumentCreate(
        document_type=document_type,
        document_subtype=document_subtype,
        document_number=document_number,
        issuing_authority=issuing_authority,
        related_immigration_type=related_immigration_type,
        issue_date=issue_date_parsed,
        expiry_date=expiry_date_parsed,
        tags=tag_list
    )
    
    return await document_service.upload_document(
        user_id=current_user,
        file=file,
        document_data=document_data
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific document by ID.
    """
    document_service = DocumentService(db)
    document = await document_service.get_document(document_id, current_user)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
        
    return document


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    document_update: DocumentUpdate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update document metadata.
    """
    document_service = DocumentService(db)
    document = await document_service.update_document(document_id, current_user, document_update)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
        
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a specific document.
    """
    document_service = DocumentService(db)
    success = await document_service.delete_document(document_id, current_user)
    
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
        
    return None


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a presigned URL to download the document.
    """
    document_service = DocumentService(db)
    download_url = await document_service.get_document_url(document_id, current_user)
    
    return {"download_url": download_url}


@router.post("/{document_id}/extract-data", response_model=dict)
async def extract_document_data(
    document_id: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Extract data from a document using AI-enhanced OCR.
    """
    document_service = DocumentService(db)
    return await document_service.extract_data(document_id, current_user)


@router.put("/{document_id}/apply-extraction", response_model=DocumentResponse)
async def apply_extracted_data(
    document_id: str,
    extraction_data: dict,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Apply extracted data to update document metadata.
    """
    document_service = DocumentService(db)
    
    # Convert extraction data to DocumentUpdate format
    update_data = {}
    extracted_fields = extraction_data.get('extracted_fields', {})
    
    # Map extracted fields to document fields
    field_mapping = {
        'document_number': 'document_number',
        'issuing_authority': 'issuing_authority',
        'issue_date': 'issue_date',
        'expiry_date': 'expiry_date'
    }
    
    for extracted_field, document_field in field_mapping.items():
        if extracted_field in extracted_fields and extracted_fields[extracted_field]:
            update_data[document_field] = extracted_fields[extracted_field]
    
    # Create DocumentUpdate object
    from app.schemas.document import DocumentUpdate
    document_update = DocumentUpdate(**update_data)
    
    return await document_service.update_document(document_id, current_user, document_update)