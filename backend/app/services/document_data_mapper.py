from typing import Dict, Any, Optional, List
from datetime import date, datetime
from dataclasses import dataclass
import logging

from app.services.document_extraction import ExtractedData

logger = logging.getLogger(__name__)


@dataclass
class DocumentMapping:
    """Maps extracted data to database fields"""
    document_metadata_fields: Dict[str, str]  # field_name -> extracted_field
    profile_update_fields: Dict[str, str]     # profile_field -> extracted_field
    confidence_threshold: float = 0.7         # Minimum confidence to auto-populate


class DocumentDataMapper:
    """Maps extracted document data to database models based on document type"""
    
    def __init__(self):
        self.mappings = self._initialize_mappings()
    
    def _initialize_mappings(self) -> Dict[str, DocumentMapping]:
        """Initialize document type mappings"""
        return {
            'passport': DocumentMapping(
                document_metadata_fields={
                    'document_number': 'passport_number',
                    'issuing_authority': 'issuing_authority',
                    'issue_date': 'issue_date',
                    'expiry_date': 'expiry_date',
                },
                profile_update_fields={
                    'passport_number': 'passport_number',
                    'passport_expiry_date': 'expiry_date',
                    # Will need country lookup for passport_country_id
                }
            ),
            'visa': DocumentMapping(
                document_metadata_fields={
                    'document_number': 'control_number',
                    'document_subtype': 'visa_type',
                    'issuing_authority': 'issuing_authority',
                    'issue_date': 'issue_date',
                    'expiry_date': 'expiry_date',
                    'related_immigration_type': 'visa_class',
                },
                profile_update_fields={
                    'visa_expiry_date': 'expiry_date',
                }
            ),
            'i94': DocumentMapping(
                document_metadata_fields={
                    'document_number': 'i94_number',
                    'issue_date': 'admission_date',
                    'expiry_date': 'admit_until_date',
                    'related_immigration_type': 'class_of_admission',
                },
                profile_update_fields={
                    'most_recent_i94_number': 'i94_number',
                    'most_recent_entry_date': 'admission_date',
                    'authorized_stay_until': 'admit_until_date',
                }
            ),
            'i797': DocumentMapping(
                document_metadata_fields={
                    'document_number': 'receipt_number',
                    'document_subtype': 'notice_type',
                    'issue_date': 'validity_from',
                    'expiry_date': 'validity_to',
                    'issuing_authority': 'issuing_authority',
                },
                profile_update_fields={
                    # I-797 may update priority dates - will need special handling
                }
            ),
            'ead': DocumentMapping(
                document_metadata_fields={
                    'document_number': 'card_number',
                    'document_subtype': 'category',
                    'issue_date': 'issue_date',
                    'expiry_date': 'expiry_date',
                },
                profile_update_fields={
                    'ead_expiry_date': 'expiry_date',
                }
            ),
            'green_card': DocumentMapping(
                document_metadata_fields={
                    'document_number': 'card_number',
                    'issue_date': 'issue_date',
                    'expiry_date': 'expiry_date',
                },
                profile_update_fields={
                    # Green card holders have permanent status
                }
            ),
            'drivers_license': DocumentMapping(
                document_metadata_fields={
                    'document_number': 'document_number',
                    'issuing_authority': 'issuing_authority',
                    'issue_date': 'issue_date',
                    'expiry_date': 'expiry_date',
                },
                profile_update_fields={}  # No profile updates for driver's license
            ),
        }
    
    def map_extracted_data(
        self, 
        extracted_data: ExtractedData, 
        document_type: str
    ) -> Dict[str, Any]:
        """Map extracted data to database fields"""
        
        if document_type not in self.mappings:
            logger.warning(f"No mapping found for document type: {document_type}")
            return self._create_generic_mapping(extracted_data)
        
        mapping = self.mappings[document_type]
        result = {
            'document_metadata': {},
            'profile_updates': {},
            'confidence_info': {},
            'warnings': []
        }
        
        # Map document metadata fields
        for db_field, extracted_field in mapping.document_metadata_fields.items():
            value = getattr(extracted_data, extracted_field, None)
            if value is not None:
                # Convert dates to proper format
                if isinstance(value, date):
                    value = value.isoformat()
                elif db_field in ['issue_date', 'expiry_date'] and isinstance(value, str):
                    # Try to parse date string
                    try:
                        parsed_date = datetime.strptime(value, '%Y-%m-%d').date()
                        value = parsed_date.isoformat()
                    except:
                        result['warnings'].append(f"Could not parse date for {db_field}: {value}")
                        continue
                
                result['document_metadata'][db_field] = value
        
        # Map profile update fields
        for profile_field, extracted_field in mapping.profile_update_fields.items():
            value = getattr(extracted_data, extracted_field, None)
            if value is not None:
                # Convert dates to proper format
                if isinstance(value, date):
                    value = value.isoformat()
                
                result['profile_updates'][profile_field] = value
        
        # Add confidence information
        if hasattr(extracted_data, 'confidence_scores') and extracted_data.confidence_scores:
            result['confidence_info'] = extracted_data.confidence_scores
        
        # Add document type-specific logic
        result = self._apply_document_specific_logic(result, extracted_data, document_type)
        
        return result
    
    def _apply_document_specific_logic(
        self, 
        result: Dict[str, Any], 
        extracted_data: ExtractedData, 
        document_type: str
    ) -> Dict[str, Any]:
        """Apply document-specific business logic"""
        
        if document_type == 'passport':
            # For passports, we should also extract nationality for country lookup
            if hasattr(extracted_data, 'nationality') and extracted_data.nationality:
                result['country_lookup'] = extracted_data.nationality
        
        elif document_type == 'visa':
            # For visas, map visa type to immigration type
            if hasattr(extracted_data, 'visa_type') and extracted_data.visa_type:
                # Common visa type mappings
                visa_mapping = {
                    'H-1B': 'H1-B',
                    'H1B': 'H1-B',
                    'L-1': 'L-1',
                    'L1': 'L-1',
                    'F-1': 'F-1',
                    'F1': 'F-1',
                    'J-1': 'J-1',
                    'J1': 'J-1',
                    'O-1': 'O-1',
                    'O1': 'O-1',
                    'B-1/B-2': 'B1/B2',
                    'B1/B2': 'B1/B2'
                }
                
                visa_type = extracted_data.visa_type.upper()
                if visa_type in visa_mapping:
                    result['document_metadata']['related_immigration_type'] = visa_mapping[visa_type]
        
        elif document_type == 'i94':
            # For I-94, check if admit until date is "D/S" (Duration of Status)
            if hasattr(extracted_data, 'admit_until_date'):
                if isinstance(extracted_data.admit_until_date, str) and 'D/S' in extracted_data.admit_until_date.upper():
                    result['profile_updates']['authorized_stay_until'] = None  # No specific end date
                    result['warnings'].append("I-94 shows Duration of Status (D/S) - no specific end date")
        
        elif document_type == 'i797':
            # For I-797, extract priority date if it's an approval notice
            if hasattr(extracted_data, 'priority_date') and extracted_data.priority_date:
                # This would need special handling to update the priority_dates JSON field
                result['priority_date_update'] = {
                    'date': extracted_data.priority_date.isoformat() if isinstance(extracted_data.priority_date, date) else extracted_data.priority_date,
                    'document_type': 'i797'
                }
        
        elif document_type == 'ead':
            # For EAD, extract USCIS number and category
            if hasattr(extracted_data, 'uscis_number') and extracted_data.uscis_number:
                result['profile_updates']['alien_registration_number'] = extracted_data.uscis_number
            
            # EAD category can help determine immigration status
            if hasattr(extracted_data, 'category') and extracted_data.category:
                category_mapping = {
                    'C09': 'H1-B spouse (H4)',
                    'C10': 'L-1 spouse (L2)',
                    'A05': 'Asylee',
                    'C03': 'F-1 student',
                    'C08': 'Asylum applicant'
                }
                
                category = extracted_data.category.upper()
                if category in category_mapping:
                    result['status_hint'] = category_mapping[category]
        
        return result
    
    def _create_generic_mapping(self, extracted_data: ExtractedData) -> Dict[str, Any]:
        """Create generic mapping for unknown document types"""
        result = {
            'document_metadata': {},
            'profile_updates': {},
            'confidence_info': {},
            'warnings': ['Unknown document type - using generic mapping']
        }
        
        # Map basic fields that exist in most documents
        basic_mappings = {
            'document_number': 'document_number',
            'issue_date': 'issue_date', 
            'expiry_date': 'expiry_date',
            'issuing_authority': 'issuing_authority'
        }
        
        for db_field, extracted_field in basic_mappings.items():
            value = getattr(extracted_data, extracted_field, None)
            if value is not None:
                if isinstance(value, date):
                    value = value.isoformat()
                result['document_metadata'][db_field] = value
        
        return result
    
    def validate_mapping_data(self, mapped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate mapped data before database insertion"""
        validated_data = mapped_data.copy()
        
        # Validate dates
        for field_group in ['document_metadata', 'profile_updates']:
            if field_group in validated_data:
                for field, value in list(validated_data[field_group].items()):
                    if 'date' in field.lower() and isinstance(value, str):
                        try:
                            # Validate date format
                            datetime.strptime(value, '%Y-%m-%d')
                        except ValueError:
                            validated_data['warnings'].append(f"Invalid date format for {field}: {value}")
                            del validated_data[field_group][field]
        
        # Validate document numbers (basic format checking)
        doc_metadata = validated_data.get('document_metadata', {})
        if 'document_number' in doc_metadata:
            doc_num = doc_metadata['document_number']
            if not isinstance(doc_num, str) or len(doc_num.strip()) == 0:
                validated_data['warnings'].append("Empty or invalid document number")
                del doc_metadata['document_number']
        
        return validated_data
    
    def get_supported_document_types(self) -> List[str]:
        """Get list of supported document types"""
        return list(self.mappings.keys())
    
    def get_mapping_info(self, document_type: str) -> Optional[Dict[str, Any]]:
        """Get mapping information for a document type"""
        if document_type not in self.mappings:
            return None
        
        mapping = self.mappings[document_type]
        return {
            'document_metadata_fields': list(mapping.document_metadata_fields.keys()),
            'profile_update_fields': list(mapping.profile_update_fields.keys()),
            'confidence_threshold': mapping.confidence_threshold
        }