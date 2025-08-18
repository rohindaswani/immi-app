import os
import io
import base64
import json
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, date
from PIL import Image
import logging

from app.core.ai_config import AIConfig
from app.services.document_extraction import ExtractedData, DocumentExtractionService

logger = logging.getLogger(__name__)


class AIDocumentExtractionService:
    """Enhanced document extraction using AI (GPT-4 Vision or Claude)"""
    
    def __init__(self):
        self.config = AIConfig()
        self.base_extractor = DocumentExtractionService()
        self.ai_client = None
        
        # Initialize AI client based on configuration
        if self.config.is_ai_enabled():
            if self.config.AI_PROVIDER == "openai":
                try:
                    from openai import AsyncOpenAI
                    self.ai_client = AsyncOpenAI(api_key=self.config.OPENAI_API_KEY)
                    self.use_vision = True  # GPT-4 Vision
                    logger.info(f"OpenAI client initialized with model: {self.config.OPENAI_MODEL}")
                except ImportError:
                    logger.warning("OpenAI library not available")
                except Exception as e:
                    logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            elif self.config.AI_PROVIDER == "anthropic":
                try:
                    import anthropic
                    self.ai_client = anthropic.AsyncAnthropic(api_key=self.config.ANTHROPIC_API_KEY)
                    self.use_vision = True  # Claude Vision
                except ImportError:
                    logger.warning("Anthropic library not available")
    
    async def extract_with_ai(
        self, 
        file_content: bytes, 
        file_type: str,
        document_type_hint: Optional[str] = None
    ) -> ExtractedData:
        """Extract document data using AI vision capabilities"""
        
        # First, try traditional extraction as fallback
        base_result = await self.base_extractor.extract_from_file(
            file_content, file_type, document_type_hint
        )
        
        # If AI is not available, return base result
        if not self.ai_client or not self.use_vision:
            logger.info("AI extraction not available, using base extraction")
            return base_result
        
        try:
            # Use AI for enhanced extraction
            if file_type.lower() in ['image/jpeg', 'image/jpg', 'image/png']:
                ai_result = await self._extract_with_vision(
                    file_content, document_type_hint, base_result
                )
                return self._merge_results(base_result, ai_result)
            elif file_type.lower() == 'application/pdf':
                # Convert first page of PDF to image for vision API
                import pdf2image
                images = pdf2image.convert_from_bytes(file_content, first_page=1, last_page=1)
                if images:
                    # Convert PIL image to bytes
                    img_byte_arr = io.BytesIO()
                    images[0].save(img_byte_arr, format='PNG')
                    img_byte_arr = img_byte_arr.getvalue()
                    
                    ai_result = await self._extract_with_vision(
                        img_byte_arr, document_type_hint, base_result
                    )
                    return self._merge_results(base_result, ai_result)
            
            return base_result
            
        except Exception as e:
            logger.error(f"AI extraction failed: {str(e)}")
            base_result.warnings.append(f"AI extraction failed: {str(e)}")
            return base_result
    
    async def _extract_with_vision(
        self, 
        image_bytes: bytes,
        document_type_hint: Optional[str],
        base_result: ExtractedData
    ) -> ExtractedData:
        """Use AI vision API to extract document data"""
        
        # Encode image to base64
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        # Create prompt based on document type
        prompt = self._create_extraction_prompt(document_type_hint, base_result)
        
        if self.config.AI_PROVIDER == "openai":
            return await self._extract_with_openai(base64_image, prompt)
        elif self.config.AI_PROVIDER == "anthropic":
            return await self._extract_with_anthropic(base64_image, prompt)
        
        return ExtractedData()
    
    async def _extract_with_openai(self, base64_image: str, prompt: str) -> ExtractedData:
        """Extract using OpenAI GPT-4 Vision"""
        try:
            response = await self.ai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at extracting information from immigration documents. Extract all relevant information and return it in the specified JSON format."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            # Parse the response
            content = response.choices[0].message.content
            
            # Extract JSON from response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                data = json.loads(json_str)
                return self._parse_ai_response(data)
            
        except Exception as e:
            logger.error(f"OpenAI extraction error: {str(e)}")
        
        return ExtractedData()
    
    async def _extract_with_anthropic(self, base64_image: str, prompt: str) -> ExtractedData:
        """Extract using Claude Vision"""
        try:
            response = await self.ai_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                temperature=0.1,
                system="You are an expert at extracting information from immigration documents. Extract all relevant information and return it in the specified JSON format.",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": base64_image
                                }
                            }
                        ]
                    }
                ]
            )
            
            # Parse the response
            content = response.content[0].text
            
            # Extract JSON from response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                data = json.loads(json_str)
                return self._parse_ai_response(data)
            
        except Exception as e:
            logger.error(f"Anthropic extraction error: {str(e)}")
        
        return ExtractedData()
    
    def _create_extraction_prompt(
        self, 
        document_type_hint: Optional[str],
        base_result: ExtractedData
    ) -> str:
        """Create prompt for AI extraction"""
        
        base_prompt = """Analyze this immigration document image and extract all relevant information. 
Return the data in JSON format with the following fields (use null for missing data):

{
    "document_type": "passport|visa|i94|i797|ead|drivers_license|state_id|other",
    "document_number": "primary document/control number",
    "full_name": "complete name as shown",
    "first_name": "given/first name",
    "last_name": "surname/family name",
    "date_of_birth": "YYYY-MM-DD format",
    "nationality": "country of citizenship",
    "passport_number": "if applicable",
    "issue_date": "YYYY-MM-DD format",
    "expiry_date": "YYYY-MM-DD format",
    "issuing_authority": "issuing country/agency",
    "place_of_issue": "city/country of issue",
    "gender": "M/F",
"""
        
        if document_type_hint == "visa" or (base_result and base_result.document_type == "visa"):
            base_prompt += """
    "visa_type": "visa classification (e.g., B-1/B-2, F-1, H-1B)",
    "visa_class": "same as visa_type",
    "control_number": "visa control/foil number",
    "entries": "Single/Multiple",
    "annotation": "any annotations/notes",
"""
        
        elif document_type_hint == "i94" or (base_result and base_result.document_type == "i94"):
            base_prompt += """
    "i94_number": "11-digit I-94 number",
    "admission_date": "YYYY-MM-DD format",
    "admit_until_date": "YYYY-MM-DD format (or 'D/S' for Duration of Status)",
    "class_of_admission": "admission class (e.g., H-1B, F-1)",
"""
        
        elif document_type_hint == "i797" or (base_result and base_result.document_type == "i797"):
            base_prompt += """
    "receipt_number": "USCIS receipt number (3 letters + 10 digits)",
    "priority_date": "YYYY-MM-DD format if applicable",
    "notice_type": "Approval/Receipt/Rejection",
    "validity_from": "YYYY-MM-DD format",
    "validity_to": "YYYY-MM-DD format",
    "beneficiary_name": "beneficiary full name",
    "petitioner_name": "petitioner/employer name",
"""
        
        elif document_type_hint == "ead" or (base_result and base_result.document_type == "ead"):
            base_prompt += """
    "uscis_number": "USCIS# (XXX-XXX-XXX format)",
    "category": "eligibility category (e.g., C09, A05)",
    "card_number": "card number",
"""
        
        base_prompt += """
    "confidence_scores": {
        "overall": 0.0-1.0,
        "document_type": 0.0-1.0,
        "dates": 0.0-1.0,
        "names": 0.0-1.0
    }
}

Analyze the document carefully and extract all visible information. For dates, convert to YYYY-MM-DD format. 
For names, preserve the exact spelling and capitalization as shown in the document.
"""
        
        return base_prompt
    
    def _parse_ai_response(self, data: Dict[str, Any]) -> ExtractedData:
        """Parse AI response into ExtractedData object"""
        result = ExtractedData()
        
        # Map JSON fields to ExtractedData attributes
        field_mapping = {
            'document_type': 'document_type',
            'document_number': 'document_number',
            'full_name': 'full_name',
            'first_name': 'first_name',
            'last_name': 'last_name',
            'nationality': 'nationality',
            'passport_number': 'passport_number',
            'issuing_authority': 'issuing_authority',
            'place_of_issue': 'place_of_issue',
            'gender': 'gender',
            'visa_type': 'visa_type',
            'visa_class': 'visa_class',
            'control_number': 'control_number',
            'entries': 'entries',
            'annotation': 'annotation',
            'i94_number': 'i94_number',
            'class_of_admission': 'class_of_admission',
            'receipt_number': 'receipt_number',
            'notice_type': 'notice_type',
            'beneficiary_name': 'beneficiary_name',
            'petitioner_name': 'petitioner_name',
            'uscis_number': 'uscis_number',
            'category': 'category',
            'card_number': 'card_number',
        }
        
        # Copy simple fields
        for json_field, attr_name in field_mapping.items():
            if json_field in data and data[json_field]:
                setattr(result, attr_name, data[json_field])
        
        # Parse dates
        date_fields = {
            'date_of_birth': 'date_of_birth',
            'issue_date': 'issue_date',
            'expiry_date': 'expiry_date',
            'admission_date': 'admission_date',
            'admit_until_date': 'admit_until_date',
            'priority_date': 'priority_date',
            'validity_from': 'validity_from',
            'validity_to': 'validity_to',
        }
        
        for json_field, attr_name in date_fields.items():
            if json_field in data and data[json_field]:
                try:
                    if data[json_field] == 'D/S':  # Duration of Status
                        # Don't set date, but add a note
                        result.warnings.append(f"{json_field}: Duration of Status (D/S)")
                    else:
                        date_obj = datetime.strptime(data[json_field], '%Y-%m-%d').date()
                        setattr(result, attr_name, date_obj)
                except:
                    result.warnings.append(f"Could not parse date: {json_field}={data[json_field]}")
        
        # Set confidence scores
        if 'confidence_scores' in data and isinstance(data['confidence_scores'], dict):
            result.confidence_scores = data['confidence_scores']
        
        return result
    
    def _merge_results(self, base_result: ExtractedData, ai_result: ExtractedData) -> ExtractedData:
        """Merge results from base extraction and AI extraction"""
        # Start with AI result as it's likely more accurate
        merged = ai_result
        
        # Fill in any missing fields from base result
        for field in merged.__dataclass_fields__:
            ai_value = getattr(merged, field)
            base_value = getattr(base_result, field)
            
            # If AI didn't extract this field but base did, use base value
            if (ai_value is None or ai_value == "") and base_value:
                setattr(merged, field, base_value)
        
        # Merge warnings
        merged.warnings.extend(base_result.warnings)
        
        # Keep the extracted text from base result
        merged.extracted_text = base_result.extracted_text
        
        return merged