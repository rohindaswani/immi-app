import uuid
import logging
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse
from app.db.models import DocumentMetadata, ImmigrationProfile
from app.services.storage import StorageService
from app.services.document_extraction import DocumentExtractionService
from app.services.ai_document_extraction import AIDocumentExtractionService
from app.services.document_data_mapper import DocumentDataMapper
from app.services.simple_document_classifier import SimpleDocumentClassifier

logger = logging.getLogger(__name__)


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
        self.extraction_service = DocumentExtractionService()
        self.ai_extraction_service = AIDocumentExtractionService()
        self.data_mapper = DocumentDataMapper()
        self.classifier = SimpleDocumentClassifier()
    
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
            # Read file content for extraction
            file_content = await file.read()
            await file.seek(0)  # Reset file pointer for storage upload
            
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
            
            # Extract ALL data from document using AI-enhanced extraction
            extracted_data = await self.ai_extraction_service.extract_with_ai(
                file_content=file_content,
                file_type=file.content_type,
                document_type_hint=document_data.document_type
            )
            
            # Map extracted data to database fields
            mapped_data = self.data_mapper.map_extracted_data(
                extracted_data, 
                extracted_data.document_type or document_data.document_type
            )
            
            # Validate the mapped data
            validated_data = self.data_mapper.validate_mapping_data(mapped_data)
            
            # Use extracted data for ALL fields (no user input)
            doc_metadata = validated_data.get('document_metadata', {})
            
            final_document_number = doc_metadata.get('document_number')
            final_issuing_authority = doc_metadata.get('issuing_authority')
            final_document_subtype = doc_metadata.get('document_subtype')
            final_related_immigration_type = doc_metadata.get('related_immigration_type')
            
            # Handle date fields
            final_issue_date = self._parse_date_field(doc_metadata.get('issue_date'))
            final_expiry_date = self._parse_date_field(doc_metadata.get('expiry_date'))
            
            final_document_type = extracted_data.document_type or document_data.document_type
            
            # Create database record with extracted data
            db_document = DocumentMetadata(
                document_id=document_id,
                profile_id=profile.profile_id,
                document_type=final_document_type,
                document_subtype=final_document_subtype,
                document_number=final_document_number,
                issuing_authority=final_issuing_authority,
                related_immigration_type=final_related_immigration_type,
                issue_date=final_issue_date,
                expiry_date=final_expiry_date,
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
            
            # Update profile with extracted data
            profile_updates = validated_data.get('profile_updates', {})
            if profile_updates:
                self._update_profile_from_document(profile, profile_updates, validated_data)
            
            self.db.commit()
            self.db.refresh(db_document)
            
            # Create response with extraction metadata
            response = DocumentResponse(
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
                tags=db_document.tags or [],
                extraction_data={
                    'extracted_fields': self._serialize_extracted_data(extracted_data),
                    'mapped_data': validated_data,
                    'confidence_scores': extracted_data.confidence_scores,
                    'warnings': extracted_data.warnings + validated_data.get('warnings', []),
                    'was_extracted': True,
                    'document_type_detected': extracted_data.document_type,
                    'extraction_successful': True
                }
            )
                
            return response
            
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
        Extract data from a document using AI-enhanced OCR.
        """
        document = self.db.query(DocumentMetadata).filter(
            DocumentMetadata.document_id == document_id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
            
        # Verify user owns this document
        if str(document.profile.user_id) != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
            
        try:
            # Download document content from storage
            file_content = await self.storage_service.get_file_content(document.s3_key)
            
            # Extract data using AI-enhanced extraction
            extracted_data = await self.ai_extraction_service.extract_with_ai(
                file_content=file_content,
                file_type=document.file_type,
                document_type_hint=document.document_type
            )
            
            # Map extracted data to database fields
            mapped_data = self.data_mapper.map_extracted_data(
                extracted_data, 
                extracted_data.document_type or document.document_type
            )
            
            # Validate the mapped data
            validated_data = self.data_mapper.validate_mapping_data(mapped_data)
            
            return {
                "extracted_fields": self._serialize_extracted_data(extracted_data),
                "mapped_data": validated_data,
                "confidence_scores": extracted_data.confidence_scores,
                "warnings": extracted_data.warnings + validated_data.get('warnings', []),
                "extracted_text": extracted_data.extracted_text,
                "document_type_detected": extracted_data.document_type,
                "extraction_successful": True
            }
            
        except Exception as e:
            logger.error(f"Document extraction failed for document {document_id}: {str(e)}", exc_info=True)
            return {
                "extracted_fields": {},
                "confidence_scores": {},
                "warnings": [f"Extraction failed: {str(e)}"],
                "extraction_successful": False,
                "error": str(e)
            }
    
    def _serialize_extracted_data(self, extracted_data) -> dict:
        """Convert ExtractedData object to dictionary for JSON serialization"""
        result = {}
        
        # Basic fields
        for field in ['document_type', 'document_number', 'full_name', 'first_name', 'last_name',
                     'nationality', 'passport_number', 'issuing_authority', 'place_of_issue', 'gender']:
            value = getattr(extracted_data, field, None)
            if value:
                result[field] = value
        
        # Date fields (convert to string)
        for field in ['date_of_birth', 'issue_date', 'expiry_date', 'admission_date', 
                     'admit_until_date', 'priority_date', 'validity_from', 'validity_to']:
            value = getattr(extracted_data, field, None)
            if value:
                result[field] = value.isoformat() if hasattr(value, 'isoformat') else str(value)
        
        # Document-specific fields
        for field in ['visa_type', 'visa_class', 'control_number', 'entries', 'annotation',
                     'i94_number', 'class_of_admission', 'receipt_number', 'notice_type',
                     'beneficiary_name', 'petitioner_name', 'uscis_number', 'category', 'card_number']:
            value = getattr(extracted_data, field, None)
            if value:
                result[field] = value
                
        return result
    
    def _parse_date_field(self, date_str: str) -> Optional[date]:
        """Parse date string to date object"""
        if not date_str:
            return None
        
        try:
            if isinstance(date_str, str):
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            elif isinstance(date_str, date):
                return date_str
        except ValueError:
            logger.warning(f"Could not parse date: {date_str}")
        
        return None
    
    def _update_profile_from_document(
        self, 
        profile, 
        profile_updates: Dict[str, Any],
        validated_data: Dict[str, Any]
    ) -> None:
        """Update immigration profile with extracted document data"""
        
        for field, value in profile_updates.items():
            if value is not None:
                try:
                    # Handle date fields
                    if 'date' in field.lower() and isinstance(value, str):
                        value = self._parse_date_field(value)
                    
                    # Only update if the field exists and the value is meaningful
                    if hasattr(profile, field):
                        current_value = getattr(profile, field)
                        
                        # Only update if current value is None or empty, or if new value is more recent
                        should_update = False
                        
                        if current_value is None:
                            should_update = True
                        elif field in ['most_recent_entry_date', 'most_recent_i94_number'] and 'i94' in validated_data.get('document_metadata', {}).get('document_type', ''):
                            # Always update for more recent I-94 data
                            should_update = True
                        elif field.endswith('_expiry_date') and isinstance(value, date) and isinstance(current_value, date):
                            # Update if new expiry date is later (more recent document)
                            should_update = value > current_value
                        elif field in ['passport_number', 'alien_registration_number'] and not current_value:
                            # Update if we don't have this information yet
                            should_update = True
                        
                        if should_update:
                            setattr(profile, field, value)
                            logger.info(f"Updated profile field {field} with value from document")
                        
                except Exception as e:
                    logger.warning(f"Could not update profile field {field}: {str(e)}")
        
        # Handle special cases
        
        # Priority date updates for I-797
        if 'priority_date_update' in validated_data:
            priority_update = validated_data['priority_date_update']
            current_priority_dates = profile.current_priority_dates or {}
            
            # Add new priority date to the JSON field
            category = priority_update.get('category', 'general')
            current_priority_dates[category] = {
                'date': priority_update['date'],
                'source_document': 'i797',
                'updated_at': datetime.utcnow().isoformat()
            }
            
            profile.current_priority_dates = current_priority_dates
            logger.info(f"Updated priority date from I-797: {priority_update['date']}")
        
        # Country lookup for passport
        if 'country_lookup' in validated_data:
            nationality = validated_data['country_lookup']
            # Here you would typically do a country lookup
            # For now, we'll just log it
            logger.info(f"Need to lookup country for nationality: {nationality}")
        
        # Update timestamp
        profile.updated_at = datetime.utcnow()
        profile.updated_by = profile.created_by  # Use same user ID