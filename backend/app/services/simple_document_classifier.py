import logging
from typing import Optional
from app.services.document_extraction import DocumentExtractionService

logger = logging.getLogger(__name__)


class SimpleDocumentClassifier:
    """Simple service that only classifies document type, no data extraction"""
    
    def __init__(self):
        self.extractor = DocumentExtractionService()
    
    async def classify_document(
        self, 
        file_content: bytes, 
        file_type: str,
        document_type_hint: Optional[str] = None
    ) -> dict:
        """
        Classify document type only - no data extraction
        Returns: {
            "document_type": "passport" | "visa" | "i797" | etc,
            "confidence": 0.0-1.0,
            "detection_method": "ocr" | "hint" | "default"
        }
        """
        try:
            # Use the existing extraction service but only for classification
            result = await self.extractor.extract_from_file(
                file_content, file_type, document_type_hint
            )
            
            # If we detected a document type, use it
            if result.document_type:
                return {
                    "document_type": result.document_type,
                    "confidence": 0.9,  # High confidence if detected
                    "detection_method": "ocr"
                }
            
            # If hint provided and no detection, use hint
            if document_type_hint:
                return {
                    "document_type": document_type_hint,
                    "confidence": 0.5,  # Medium confidence from hint
                    "detection_method": "hint"
                }
            
            # Default to "other"
            return {
                "document_type": "other",
                "confidence": 0.1,  # Low confidence
                "detection_method": "default"
            }
            
        except Exception as e:
            logger.error(f"Document classification failed: {str(e)}")
            
            # On error, use hint or default
            if document_type_hint:
                return {
                    "document_type": document_type_hint,
                    "confidence": 0.3,
                    "detection_method": "hint_on_error"
                }
            
            return {
                "document_type": "other",
                "confidence": 0.0,
                "detection_method": "error_default"
            }