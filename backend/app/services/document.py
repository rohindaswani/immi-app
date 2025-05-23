import uuid
from datetime import date, datetime
from typing import List, Optional
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse
from app.db.models import DocumentMetadata, ImmigrationProfile
from app.services.storage import StorageService


class DocumentService:
    """
    Service for document operations.
    """
    
    # Document type validation
    ALLOWED_DOCUMENT_TYPES = {
        'passport', 'visa', 'i797', 'i94', 'ead', 'green_card', 
        'drivers_license', 'birth_certificate', 'marriage_certificate',
        'diploma', 'transcript', 'employment_letter', 'pay_stub',
        'tax_return', 'bank_statement', 'lease_agreement', 'utility_bill',
        'medical_record', 'vaccination_record', 'other'
    }
    
    # File type validation (MIME types)
    ALLOWED_FILE_TYPES = {
        'application/pdf': 'pdf',
        'image/jpeg': 'jpg',
        'image/jpg': 'jpg', 
        'image/png': 'png',
        'image/tiff': 'tiff',
        'image/webp': 'webp'
    }
    
    # Maximum file size (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    def __init__(self, db: Session):
        self.db = db
        self.storage_service = StorageService()
    
    async def get_documents(
        self, 
        user_id: str,
        document_type: Optional[str] = None,
        expiry_before: Optional[date] = None,
        expiry_after: Optional[date] = None
    ) -> List[DocumentResponse]:
        """
        Get all documents for a user with optional filtering.
        """
        # Get user's profile or create a test profile for development
        profile = self.db.query(ImmigrationProfile).filter(
            ImmigrationProfile.user_id == user_id
        ).first()
        
        # TEMPORARY: Create a test profile if none exists (for development/testing)
        if not profile and user_id == "12345678-1234-1234-1234-123456789abc":
            profile = ImmigrationProfile(
                user_id=user_id,
                profile_type="primary",
                notes="Test profile for development"
            )
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Build query
        query = self.db.query(DocumentMetadata).filter(
            DocumentMetadata.profile_id == profile.profile_id
        )
        
        # Apply filters
        if document_type:
            query = query.filter(DocumentMetadata.document_type == document_type)
            
        if expiry_before:
            query = query.filter(DocumentMetadata.expiry_date <= expiry_before)
            
        if expiry_after:
            query = query.filter(DocumentMetadata.expiry_date >= expiry_after)
            
        documents = query.order_by(DocumentMetadata.created_at.desc()).all()
        
        # Convert to response schema
        return [
            DocumentResponse(
                document_id=str(doc.document_id),
                user_id=str(doc.profile.user_id),
                document_type=doc.document_type,
                document_subtype=doc.document_subtype,
                document_number=doc.document_number,
                issuing_authority=doc.issuing_authority,
                related_immigration_type=doc.related_immigration_type,
                issue_date=doc.issue_date,
                expiry_date=doc.expiry_date,
                file_name=doc.file_name,
                file_size=doc.file_size,
                file_type=doc.file_type,
                is_verified=doc.is_verified,
                upload_date=doc.created_at,
                tags=doc.tags or []
            )
            for doc in documents
        ]
    
    async def get_document(self, document_id: str, user_id: str) -> Optional[DocumentResponse]:
        """
        Get a specific document by ID.
        """
        document = self.db.query(DocumentMetadata).filter(
            DocumentMetadata.document_id == document_id
        ).first()
        
        if not document:
            return None
            
        # Verify user owns this document
        if str(document.profile.user_id) != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
            
        return DocumentResponse(
            document_id=str(document.document_id),
            user_id=str(document.profile.user_id),
            document_type=document.document_type,
            document_subtype=document.document_subtype,
            document_number=document.document_number,
            issuing_authority=document.issuing_authority,
            related_immigration_type=document.related_immigration_type,
            issue_date=document.issue_date,
            expiry_date=document.expiry_date,
            file_name=document.file_name,
            file_size=document.file_size,
            file_type=document.file_type,
            is_verified=document.is_verified,
            upload_date=document.created_at,
            tags=document.tags or []
        )
    
    async def upload_document(
        self, 
        user_id: str,
        file: UploadFile,
        document_data: DocumentCreate
    ) -> DocumentResponse:
        """
        Upload a new document with metadata.
        """
        # Get user's profile or create a test profile for development
        profile = self.db.query(ImmigrationProfile).filter(
            ImmigrationProfile.user_id == user_id
        ).first()
        
        # TEMPORARY: Create a test profile if none exists (for development/testing)
        if not profile and user_id == "12345678-1234-1234-1234-123456789abc":
            profile = ImmigrationProfile(
                user_id=user_id,
                profile_type="primary",
                notes="Test profile for development"
            )
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Validate document type
        if document_data.document_type not in self.ALLOWED_DOCUMENT_TYPES:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid document type. Allowed types: {', '.join(self.ALLOWED_DOCUMENT_TYPES)}"
            )
            
        # Validate file size
        if file.size and file.size > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"File size exceeds maximum allowed size of {self.MAX_FILE_SIZE / (1024*1024):.1f}MB"
            )
            
        # Validate file type
        if file.content_type not in self.ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type. Allowed types: {', '.join(self.ALLOWED_FILE_TYPES.keys())}"
            )
            
        # Generate unique document ID
        document_id = uuid.uuid4()
        
        try:
            # Upload to storage using the correct API
            storage_key, storage_url = await self.storage_service.upload_file(
                file=file,
                folder="documents",
                user_id=user_id,
                metadata={
                    'user_id': user_id,
                    'document_type': document_data.document_type,
                    'document_id': str(document_id)
                }
            )
            
            # Create database record
            db_document = DocumentMetadata(
                document_id=document_id,
                profile_id=profile.profile_id,
                document_type=document_data.document_type,
                document_subtype=document_data.document_subtype,
                document_number=document_data.document_number,
                issuing_authority=document_data.issuing_authority,
                related_immigration_type=document_data.related_immigration_type,
                issue_date=document_data.issue_date,
                expiry_date=document_data.expiry_date,
                mongodb_id="",  # Will be set when we add MongoDB integration
                s3_key=storage_key,
                file_name=file.filename,
                file_size=file.size or 0,
                file_type=file.content_type,
                is_verified=False,
                tags=document_data.tags or [],
                created_by=uuid.UUID(user_id)
            )
            
            self.db.add(db_document)
            self.db.commit()
            self.db.refresh(db_document)
            
            return DocumentResponse(
                document_id=str(db_document.document_id),
                user_id=user_id,
                document_type=db_document.document_type,
                document_subtype=db_document.document_subtype,
                document_number=db_document.document_number,
                issuing_authority=db_document.issuing_authority,
                related_immigration_type=db_document.related_immigration_type,
                issue_date=db_document.issue_date,
                expiry_date=db_document.expiry_date,
                file_name=db_document.file_name,
                file_size=db_document.file_size,
                file_type=db_document.file_type,
                is_verified=db_document.is_verified,
                upload_date=db_document.created_at,
                tags=db_document.tags or []
            )
            
        except Exception as e:
            # Rollback database changes
            self.db.rollback()
            # Try to cleanup uploaded file
            try:
                await self.storage_service.delete_file(storage_key)
            except:
                pass
            raise HTTPException(status_code=500, detail=f"Failed to upload document: {str(e)}")
    
    async def update_document(self, document_id: str, user_id: str, document_data: DocumentUpdate) -> Optional[DocumentResponse]:
        """
        Update document metadata.
        """
        document = self.db.query(DocumentMetadata).filter(
            DocumentMetadata.document_id == document_id
        ).first()
        
        if not document:
            return None
            
        # Verify user owns this document
        if str(document.profile.user_id) != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
            
        # Update only provided fields
        update_data = document_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(document, field):
                setattr(document, field, value)
                
        document.updated_at = datetime.utcnow()
        document.updated_by = uuid.UUID(user_id)
        
        self.db.commit()
        self.db.refresh(document)
        
        return DocumentResponse(
            document_id=str(document.document_id),
            user_id=user_id,
            document_type=document.document_type,
            document_subtype=document.document_subtype,
            document_number=document.document_number,
            issuing_authority=document.issuing_authority,
            related_immigration_type=document.related_immigration_type,
            issue_date=document.issue_date,
            expiry_date=document.expiry_date,
            file_name=document.file_name,
            file_size=document.file_size,
            file_type=document.file_type,
            is_verified=document.is_verified,
            upload_date=document.created_at,
            tags=document.tags or []
        )
    
    async def delete_document(self, document_id: str, user_id: str) -> bool:
        """
        Delete a document.
        """
        document = self.db.query(DocumentMetadata).filter(
            DocumentMetadata.document_id == document_id
        ).first()
        
        if not document:
            return False
            
        # Verify user owns this document
        if str(document.profile.user_id) != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
            
        try:
            # Delete from storage
            if document.s3_key:
                await self.storage_service.delete_file(document.s3_key)
                
            # Delete from database
            self.db.delete(document)
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")
    
    async def get_document_url(self, document_id: str, user_id: str) -> str:
        """
        Get a presigned URL for document access.
        """
        document = self.db.query(DocumentMetadata).filter(
            DocumentMetadata.document_id == document_id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
            
        # Verify user owns this document
        if str(document.profile.user_id) != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
            
        if not document.s3_key:
            raise HTTPException(status_code=400, detail="Document file not found")
            
        return await self.storage_service.generate_presigned_url(document.s3_key)
        
    async def extract_data(self, document_id: str, user_id: str) -> dict:
        """
        Extract data from a document using OCR (placeholder for future AI integration).
        """
        document = self.db.query(DocumentMetadata).filter(
            DocumentMetadata.document_id == document_id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
            
        # Verify user owns this document
        if str(document.profile.user_id) != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
            
        # Placeholder implementation - will be enhanced with AI/OCR integration
        return {
            "extracted_fields": {},
            "confidence_score": 0.0,
            "message": "OCR extraction not yet implemented"
        }