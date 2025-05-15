from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from typing import List, Optional

from app.schemas.document import DocumentResponse, DocumentCreate
from app.services.document import DocumentService

router = APIRouter()

document_service = DocumentService()

@router.get("/", response_model=List[DocumentResponse])
async def get_documents(
    document_type: Optional[str] = None,
    expiry_before: Optional[str] = None,
    expiry_after: Optional[str] = None
):
    """
    Get all documents for the current user with optional filtering.
    """
    # This will be implemented once the document service is created
    # return await document_service.get_documents(document_type, expiry_before, expiry_after)
    
    # Placeholder response
    return [
        {
            "document_id": "example-document-id",
            "user_id": "example-user-id",
            "document_type": "passport",
            "document_number": "P1234567",
            "issuing_authority": "Department of State",
            "related_immigration_type": "H1-B",
            "issue_date": "2020-05-20",
            "expiry_date": "2030-05-20",
            "file_name": "passport.pdf",
            "file_size": 1024000,
            "file_type": "application/pdf",
            "is_verified": True,
            "upload_date": "2023-01-01T12:00:00Z",
            "tags": ["identity", "travel"]
        }
    ]


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    document_number: Optional[str] = Form(None),
    issuing_authority: Optional[str] = Form(None),
    related_immigration_type: Optional[str] = Form(None),
    issue_date: Optional[str] = Form(None),
    expiry_date: Optional[str] = Form(None),
    tags: Optional[str] = Form(None)
):
    """
    Upload a new document with metadata.
    """
    # This will be implemented once the document service is created
    # return await document_service.upload_document(file, document_type, document_number, issuing_authority, 
    #                                              related_immigration_type, issue_date, expiry_date, tags)
    
    # Parse tags if provided
    tag_list = tags.split(",") if tags else []
    
    # Placeholder response
    return {
        "document_id": "new-document-id",
        "user_id": "example-user-id",
        "document_type": document_type,
        "document_number": document_number,
        "issuing_authority": issuing_authority,
        "related_immigration_type": related_immigration_type,
        "issue_date": issue_date,
        "expiry_date": expiry_date,
        "file_name": file.filename,
        "file_size": 1024000,  # placeholder
        "file_type": file.content_type,
        "is_verified": False,
        "upload_date": "2023-06-15T14:30:00Z",  # placeholder
        "tags": tag_list
    }


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str):
    """
    Get a specific document by ID.
    """
    # This will be implemented once the document service is created
    # return await document_service.get_document(document_id)
    
    # Placeholder response
    return {
        "document_id": document_id,
        "user_id": "example-user-id",
        "document_type": "passport",
        "document_number": "P1234567",
        "issuing_authority": "Department of State",
        "related_immigration_type": "H1-B",
        "issue_date": "2020-05-20",
        "expiry_date": "2030-05-20",
        "file_name": "passport.pdf",
        "file_size": 1024000,
        "file_type": "application/pdf",
        "is_verified": True,
        "upload_date": "2023-01-01T12:00:00Z",
        "tags": ["identity", "travel"]
    }


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: str):
    """
    Delete a specific document.
    """
    # This will be implemented once the document service is created
    # await document_service.delete_document(document_id)
    return None


@router.post("/{document_id}/extract-data", response_model=dict)
async def extract_document_data(document_id: str):
    """
    Extract data from a document using OCR.
    """
    # This will be implemented once the document service and AI integration are created
    # return await document_service.extract_data(document_id)
    
    # Placeholder response
    return {
        "extracted_fields": {
            "name": "John Doe",
            "document_number": "P1234567",
            "issue_date": "2020-05-20",
            "expiry_date": "2030-05-20"
        },
        "confidence_score": 0.95
    }