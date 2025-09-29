"""
Privacy and security configuration for handling sensitive immigration data
"""
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class PrivacyConfig:
    """Configuration for privacy and data protection"""
    
    # Fields that should never be sent to external LLMs
    ALWAYS_REDACT_FIELDS = [
        'passport_number',
        'alien_registration_number',
        'i94_number',
        'i797_number',
        'petition_number',
        'receipt_number',
        'case_number',
        'social_security_number',
        'ssn',
        'tax_id',
        'driver_license_number',
        'visa_foil_number',
        'sevis_id',
        'ds2019_number',
        'i20_number'
    ]
    
    # Fields that require explicit user consent
    REQUIRES_CONSENT_FIELDS = [
        'employer_name',
        'salary_information',
        'bank_account',
        'home_address',
        'phone_number'
    ]
    
    # Fields that are safe to share (dates, statuses, etc.)
    SAFE_FIELDS = [
        'visa_expiry_date',
        'authorized_stay_until',
        'ead_expiry_date',
        'passport_expiry_date',
        'entry_date',
        'current_status',
        'immigration_goals',
        'profile_type',
        'is_primary_beneficiary'
    ]
    
    @classmethod
    def should_redact(cls, field_name: str) -> bool:
        """Check if a field should be redacted"""
        field_lower = field_name.lower()
        return any(sensitive in field_lower for sensitive in cls.ALWAYS_REDACT_FIELDS)
    
    @classmethod
    def requires_consent(cls, field_name: str) -> bool:
        """Check if a field requires user consent"""
        field_lower = field_name.lower()
        return any(consent in field_lower for consent in cls.REQUIRES_CONSENT_FIELDS)
    
    @classmethod
    def is_safe(cls, field_name: str) -> bool:
        """Check if a field is safe to share"""
        field_lower = field_name.lower()
        return any(safe in field_lower for safe in cls.SAFE_FIELDS)
    
    @classmethod
    def redact_value(cls, value: Any, field_name: str) -> Any:
        """Redact a value based on field name"""
        if not value or not isinstance(value, str):
            return value
            
        if cls.should_redact(field_name):
            # For sensitive fields, show only last 4 characters
            if len(value) > 4:
                return f"***{value[-4:]}"
            else:
                return "****"
        
        return value
    
    @classmethod
    def sanitize_context(cls, context: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize an entire context dictionary"""
        sanitized = {}
        
        for key, value in context.items():
            # Skip internal fields
            if key.startswith('_'):
                continue
                
            if isinstance(value, dict):
                # Recursively sanitize nested dictionaries
                sanitized[key] = cls.sanitize_context(value)
            elif isinstance(value, list):
                # Handle lists
                sanitized[key] = [
                    cls.sanitize_context(item) if isinstance(item, dict) else cls.redact_value(item, key)
                    for item in value
                ]
            else:
                # Sanitize individual values
                sanitized[key] = cls.redact_value(value, key)
        
        return sanitized
    
    @classmethod
    def get_privacy_notice(cls) -> str:
        """Get privacy notice for users"""
        return """
        🔒 **Privacy Protection Active**
        
        Your sensitive information (passport numbers, I-94 numbers, etc.) is automatically 
        redacted before being sent to AI services. Only dates and status information are 
        shared to provide you with personalized immigration guidance.
        
        If you need assistance with specific document numbers, please let us know and we'll 
        ask for your explicit consent before processing that information.
        """