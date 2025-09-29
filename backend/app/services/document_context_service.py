import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session

from app.db.models import DocumentMetadata, ImmigrationProfile
from app.schemas.document import DocumentResponse
from app.core.privacy_config import PrivacyConfig

logger = logging.getLogger(__name__)


class DocumentContextService:
    """Service for aggregating user document data for AI chat context"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_user_document_context(self, user_id: str) -> Dict[str, Any]:
        """
        Aggregate all user document data into a structured context for AI chat
        Returns comprehensive user immigration profile and document summary
        """
        try:
            print(f"[DEBUG] Looking for profile with user_id: {user_id}")
            print(f"[DEBUG] user_id type: {type(user_id)}")
            
            # Check if user_id is a string UUID that needs conversion
            from uuid import UUID
            try:
                if isinstance(user_id, str):
                    user_uuid = UUID(user_id)
                else:
                    user_uuid = user_id
                print(f"[DEBUG] Converted to UUID: {user_uuid}")
            except ValueError:
                print(f"[DEBUG] Invalid UUID string: {user_id}")
                user_uuid = user_id
            
            # Get user's profile
            profile = self.db.query(ImmigrationProfile).filter(
                ImmigrationProfile.user_id == user_uuid
            ).first()
            
            print(f"[DEBUG] Profile found: {profile is not None}")
            if profile:
                print(f"[DEBUG] Profile ID: {profile.profile_id}")
            
            # Also check all profiles in database for debugging
            all_profiles = self.db.query(ImmigrationProfile).all()
            print(f"[DEBUG] Total profiles in DB: {len(all_profiles)}")
            for p in all_profiles:
                print(f"[DEBUG] Profile user_id: {p.user_id} (type: {type(p.user_id)})")
            
            if not profile:
                # Return empty context instead of error for new users
                logger.info(f"No profile found for user {user_id}, returning empty context")
                return {
                    "user_profile": {},
                    "documents": {},
                    "immigration_status": {},
                    "travel_history": {},
                    "compliance_alerts": {"alerts": [], "total_alerts": 0},
                    "context_summary": "New user with no profile data yet."
                }
            
            # Get all user documents
            documents = self.db.query(DocumentMetadata).filter(
                DocumentMetadata.profile_id == profile.profile_id
            ).order_by(DocumentMetadata.created_at.desc()).all()
            
            # Build comprehensive context
            context = {
                "user_profile": self._build_profile_context(profile),
                "documents": self._build_documents_context(documents),
                "immigration_status": self._build_status_context(profile),
                "travel_history": self._build_travel_context(profile),
                "compliance_alerts": self._build_compliance_context(documents),
                "context_summary": self._build_summary(profile, documents),
                "privacy_notice": PrivacyConfig.get_privacy_notice()
            }
            
            # Apply privacy sanitization to the entire context
            sanitized_context = PrivacyConfig.sanitize_context(context)
            
            return sanitized_context
            
        except Exception as e:
            logger.error(f"Error building document context for user {user_id}: {str(e)}")
            # Return empty context instead of error
            return {
                "user_profile": {},
                "documents": {},
                "immigration_status": {},
                "travel_history": {},
                "compliance_alerts": {"alerts": [], "total_alerts": 0},
                "context_summary": "Unable to load profile data."
            }
    
    def _redact_sensitive_info(self, value: str, field_name: str) -> str:
        """Redact sensitive information for security"""
        if not value:
            return None
            
        # List of fields that should be fully redacted
        sensitive_fields = [
            'passport_number', 'alien_registration_number', 
            'i94_number', 'petition_number', 'receipt_number',
            'case_number', 'document_number', 'i797_number'
        ]
        
        if field_name.lower() in sensitive_fields or any(s in field_name.lower() for s in sensitive_fields):
            # Show only last 4 characters
            if len(value) > 4:
                return f"***{value[-4:]}"
            else:
                return "****"
        
        return value
    
    def _build_profile_context(self, profile: ImmigrationProfile) -> Dict[str, Any]:
        """Build user profile context with sensitive data redacted"""
        # Get user info from the related user object if available
        user_name = "User"
        if hasattr(profile, 'user') and profile.user:
            first_name = getattr(profile.user, 'first_name', '')
            last_name = getattr(profile.user, 'last_name', '')
            user_name = f"{first_name or ''} {last_name or ''}".strip() or profile.user.email
        
        return {
            "full_name": user_name,
            "passport_has_been_provided": bool(profile.passport_number),  # Just indicate if we have it
            "passport_expiry": profile.passport_expiry_date.isoformat() if profile.passport_expiry_date else None,
            "current_status": "H1-B",  # We'll need to get this from the status relationship
            "most_recent_entry": profile.most_recent_entry_date.isoformat() if profile.most_recent_entry_date else None,
            "authorized_until": profile.authorized_stay_until.isoformat() if profile.authorized_stay_until else None,
            "priority_dates": profile.current_priority_dates,
            "i94_provided": bool(profile.most_recent_i94_number),  # Just indicate if we have it
            "visa_expiry": profile.visa_expiry_date.isoformat() if profile.visa_expiry_date else None,
            "ead_expiry": profile.ead_expiry_date.isoformat() if profile.ead_expiry_date else None,
            "immigration_goals": profile.immigration_goals,
            # Store original values separately (not sent to LLM)
            "_sensitive_data": {
                "passport_number": profile.passport_number,
                "i94_number": profile.most_recent_i94_number,
                "alien_registration_number": getattr(profile, 'alien_registration_number', None)
            }
        }
    
    def _build_documents_context(self, documents: List[DocumentMetadata]) -> Dict[str, Any]:
        """Build documents context organized by type with sensitive data redacted"""
        docs_by_type = {}
        
        for doc in documents:
            doc_type = doc.document_type
            if doc_type not in docs_by_type:
                docs_by_type[doc_type] = []
            
            # Redact sensitive document numbers
            doc_number_redacted = None
            if doc.document_number:
                # For document numbers, just indicate type and last 4 digits
                if len(doc.document_number) > 4:
                    doc_number_redacted = f"***{doc.document_number[-4:]}"
                else:
                    doc_number_redacted = "****"
            
            doc_info = {
                "document_type": doc.document_type,
                "has_document_number": bool(doc.document_number),  # Just indicate if we have it
                "document_number_partial": doc_number_redacted,  # Show only redacted version
                "issuing_authority": doc.issuing_authority,
                "issue_date": doc.issue_date.isoformat() if doc.issue_date else None,
                "expiry_date": doc.expiry_date.isoformat() if doc.expiry_date else None,
                "is_verified": doc.is_verified,
                "upload_date": doc.created_at.isoformat(),
                "subtype": doc.document_subtype,
                "related_immigration_type": doc.related_immigration_type,
                "tags": doc.tags or []
            }
            
            docs_by_type[doc_type].append(doc_info)
        
        return docs_by_type
    
    def _build_status_context(self, profile: ImmigrationProfile) -> Dict[str, Any]:
        """Build immigration status context"""
        return {
            "current_status": "H1-B",  # Default for now, should come from status relationship
            "status_expiry": profile.visa_expiry_date.isoformat() if profile.visa_expiry_date else None,
            "visa_expiry": profile.visa_expiry_date.isoformat() if profile.visa_expiry_date else None,
            "ead_expiry": profile.ead_expiry_date.isoformat() if profile.ead_expiry_date else None,
            "authorized_until": profile.authorized_stay_until.isoformat() if profile.authorized_stay_until else None,
            "priority_dates": profile.current_priority_dates
        }
    
    def _build_travel_context(self, profile: ImmigrationProfile) -> Dict[str, Any]:
        """Build travel history context with sensitive data redacted"""
        return {
            "most_recent_entry": {
                "date": profile.most_recent_entry_date.isoformat() if profile.most_recent_entry_date else None,
                "has_i94_record": bool(profile.most_recent_i94_number),  # Just indicate if we have it
                "port_of_entry": None  # This field doesn't exist in the model
            },
            "travel_document_info": {
                "has_passport_on_file": bool(profile.passport_number),  # Just indicate if we have it
                "passport_expiry": profile.passport_expiry_date.isoformat() if profile.passport_expiry_date else None,
                "passport_country": "India"  # Default, should get from passport_country_id relationship
            }
        }
    
    def _build_compliance_context(self, documents: List[DocumentMetadata]) -> Dict[str, Any]:
        """Build compliance and deadline alerts context"""
        alerts = []
        today = date.today()
        
        for doc in documents:
            if doc.expiry_date:
                days_until_expiry = (doc.expiry_date - today).days
                
                if days_until_expiry < 0:
                    alerts.append({
                        "type": "expired",
                        "document": doc.document_type,
                        "document_number": doc.document_number,
                        "expired_date": doc.expiry_date.isoformat(),
                        "days_expired": abs(days_until_expiry),
                        "urgency": "critical"
                    })
                elif days_until_expiry <= 30:
                    alerts.append({
                        "type": "expiring_soon",
                        "document": doc.document_type,
                        "document_number": doc.document_number,
                        "expiry_date": doc.expiry_date.isoformat(),
                        "days_remaining": days_until_expiry,
                        "urgency": "high" if days_until_expiry <= 7 else "medium"
                    })
                elif days_until_expiry <= 180:
                    alerts.append({
                        "type": "upcoming_expiry",
                        "document": doc.document_type,
                        "document_number": doc.document_number,
                        "expiry_date": doc.expiry_date.isoformat(),
                        "days_remaining": days_until_expiry,
                        "urgency": "low"
                    })
        
        return {
            "alerts": alerts,
            "total_alerts": len(alerts),
            "critical_count": len([a for a in alerts if a["urgency"] == "critical"]),
            "high_priority_count": len([a for a in alerts if a["urgency"] == "high"])
        }
    
    def _build_summary(self, profile: ImmigrationProfile, documents: List[DocumentMetadata]) -> str:
        """Build a natural language summary of the user's immigration situation"""
        from datetime import timezone
        
        # Get user name from related user object
        name = "The user"
        if hasattr(profile, 'user') and profile.user:
            first_name = getattr(profile.user, 'first_name', '')
            last_name = getattr(profile.user, 'last_name', '')
            user_name = f"{first_name or ''} {last_name or ''}".strip()
            name = user_name if user_name else profile.user.email
        
        status = "H1-B"  # Default status for now
        
        # Document counts
        doc_counts = {}
        for doc in documents:
            doc_type = doc.document_type
            doc_counts[doc_type] = doc_counts.get(doc_type, 0) + 1
        
        # Recent activity - fix timezone issue
        now = datetime.now(timezone.utc)
        recent_uploads = 0
        for doc in documents:
            # Make created_at timezone aware if it isn't
            created_at = doc.created_at
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            if (now - created_at).days <= 30:
                recent_uploads += 1
        
        # Build summary
        summary_parts = [
            f"{name} is currently in {status} status.",
        ]
        
        if profile.immigration_goals:
            summary_parts.append(f"Immigration goal: {profile.immigration_goals}")
        
        if profile.authorized_stay_until:
            auth_date = profile.authorized_stay_until
            days_remaining = (auth_date - date.today()).days
            if days_remaining > 0:
                summary_parts.append(f"Authorized to stay until {auth_date.strftime('%B %d, %Y')} ({days_remaining} days remaining).")
            else:
                summary_parts.append(f"Authorization expired on {auth_date.strftime('%B %d, %Y')} ({abs(days_remaining)} days ago).")
        
        if profile.visa_expiry_date:
            visa_date = profile.visa_expiry_date
            days_remaining = (visa_date - date.today()).days
            if days_remaining > 0:
                summary_parts.append(f"Visa expires on {visa_date.strftime('%B %d, %Y')} ({days_remaining} days remaining).")
        
        if doc_counts:
            doc_summary = ", ".join([f"{count} {doc_type.replace('_', ' ')}" for doc_type, count in doc_counts.items()])
            summary_parts.append(f"Has uploaded {doc_summary} documents.")
        
        if recent_uploads > 0:
            summary_parts.append(f"Recently uploaded {recent_uploads} documents in the last 30 days.")
        
        return " ".join(summary_parts)