from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.db.models import (
    ImmigrationProfile,
    ImmigrationStatus,
    DocumentMetadata,
    TravelHistory,
    EmploymentHistory,
    AddressHistory,
    ImmigrationTimeline,
    ConversationContext
)


class ContextService:
    """Service for gathering user-specific context for AI chat"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def gather_user_context(
        self, 
        user_id: UUID, 
        conversation_id: UUID,
        message_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Gather comprehensive user context for AI assistance"""
        context = {
            "profile": self._get_profile_context(user_id),
            "current_status": self._get_current_status(user_id),
            "recent_documents": self._get_recent_documents(user_id),
            "upcoming_deadlines": self._get_upcoming_deadlines(user_id),
            "travel_history": self._get_recent_travel(user_id),
            "employment": self._get_current_employment(user_id),
        }
        
        # Track what context was accessed
        self._track_context_access(
            conversation_id, 
            message_id, 
            context
        )
        
        return context
    
    def _get_profile_context(self, user_id: UUID) -> Dict[str, Any]:
        """Get basic profile information"""
        profile = self.db.query(ImmigrationProfile).filter(
            ImmigrationProfile.user_id == user_id
        ).first()
        
        if not profile:
            return {}
        
        return {
            "profile_id": str(profile.profile_id),
            "priority_dates": profile.current_priority_dates,
            "authorized_stay_until": profile.authorized_stay_until.isoformat() if profile.authorized_stay_until else None,
            "ead_expiry_date": profile.ead_expiry_date.isoformat() if profile.ead_expiry_date else None,
            "visa_expiry_date": profile.visa_expiry_date.isoformat() if profile.visa_expiry_date else None,
        }
    
    def _get_current_status(self, user_id: UUID) -> Dict[str, Any]:
        """Get current immigration status details"""
        profile = self.db.query(ImmigrationProfile).filter(
            ImmigrationProfile.user_id == user_id
        ).first()
        
        if not profile or not profile.current_status_id:
            return {}
        
        status = self.db.query(ImmigrationStatus).filter(
            ImmigrationStatus.status_id == profile.current_status_id
        ).first()
        
        if not status:
            return {}
        
        return {
            "status_code": status.status_code,
            "status_name": status.status_name,
            "allows_employment": status.allows_employment,
            "employment_restrictions": status.employment_restrictions,
            "max_duration": status.max_duration,
            "grace_period": status.grace_period,
            "is_dual_intent": status.is_dual_intent,
        }
    
    def _get_recent_documents(self, user_id: UUID, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recently added or expiring documents"""
        profile = self.db.query(ImmigrationProfile).filter(
            ImmigrationProfile.user_id == user_id
        ).first()
        
        if not profile:
            return []
        
        # Get recent documents
        documents = self.db.query(DocumentMetadata).filter(
            DocumentMetadata.profile_id == profile.profile_id
        ).order_by(desc(DocumentMetadata.created_at)).limit(limit).all()
        
        return [{
            "document_type": doc.document_type,
            "document_subtype": doc.document_subtype,
            "issue_date": doc.issue_date.isoformat() if doc.issue_date else None,
            "expiry_date": doc.expiry_date.isoformat() if doc.expiry_date else None,
            "is_expiring_soon": self._is_expiring_soon(doc.expiry_date) if doc.expiry_date else False,
        } for doc in documents]
    
    def _get_upcoming_deadlines(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Get upcoming immigration deadlines"""
        profile = self.db.query(ImmigrationProfile).filter(
            ImmigrationProfile.user_id == user_id
        ).first()
        
        if not profile:
            return []
        
        # Check visa expiry
        deadlines = []
        
        if profile.visa_expiry_date:
            days_until = (profile.visa_expiry_date - datetime.now().date()).days
            if days_until <= 180:  # 6 months
                deadlines.append({
                    "type": "visa_expiry",
                    "date": profile.visa_expiry_date.isoformat(),
                    "days_until": days_until,
                    "priority": "high" if days_until <= 60 else "medium"
                })
        
        if profile.ead_expiry_date:
            days_until = (profile.ead_expiry_date - datetime.now().date()).days
            if days_until <= 180:
                deadlines.append({
                    "type": "ead_expiry",
                    "date": profile.ead_expiry_date.isoformat(),
                    "days_until": days_until,
                    "priority": "high" if days_until <= 90 else "medium"
                })
        
        if profile.authorized_stay_until:
            days_until = (profile.authorized_stay_until - datetime.now().date()).days
            if days_until <= 90:
                deadlines.append({
                    "type": "i94_expiry",
                    "date": profile.authorized_stay_until.isoformat(),
                    "days_until": days_until,
                    "priority": "critical" if days_until <= 30 else "high"
                })
        
        return sorted(deadlines, key=lambda x: x['days_until'])
    
    def _get_recent_travel(self, user_id: UUID, months: int = 6) -> List[Dict[str, Any]]:
        """Get recent travel history"""
        profile = self.db.query(ImmigrationProfile).filter(
            ImmigrationProfile.user_id == user_id
        ).first()
        
        if not profile:
            return []
        
        cutoff_date = datetime.now().date() - timedelta(days=months * 30)
        
        travels = self.db.query(TravelHistory).filter(
            and_(
                TravelHistory.profile_id == profile.profile_id,
                TravelHistory.departure_date >= cutoff_date
            )
        ).order_by(desc(TravelHistory.departure_date)).limit(5).all()
        
        return [{
            "departure_date": travel.departure_date.isoformat(),
            "arrival_date": travel.arrival_date.isoformat(),
            "departure_country": travel.departure_country.country_name if travel.departure_country else None,
            "arrival_country": travel.arrival_country.country_name if travel.arrival_country else None,
            "duration_days": (travel.arrival_date - travel.departure_date).days,
        } for travel in travels]
    
    def _get_current_employment(self, user_id: UUID) -> Dict[str, Any]:
        """Get current employment information"""
        profile = self.db.query(ImmigrationProfile).filter(
            ImmigrationProfile.user_id == user_id
        ).first()
        
        if not profile:
            return {}
        
        employment = self.db.query(EmploymentHistory).filter(
            and_(
                EmploymentHistory.profile_id == profile.profile_id,
                EmploymentHistory.is_current == True
            )
        ).first()
        
        if not employment:
            return {}
        
        return {
            "employer": employment.employer.company_name if employment.employer else None,
            "job_title": employment.job_title,
            "start_date": employment.start_date.isoformat(),
            "employment_type": employment.employment_type,
        }
    
    def _is_expiring_soon(self, expiry_date, days_threshold: int = 180) -> bool:
        """Check if a date is expiring within threshold"""
        if not expiry_date:
            return False
        days_until = (expiry_date - datetime.now().date()).days
        return 0 <= days_until <= days_threshold
    
    def _track_context_access(
        self, 
        conversation_id: UUID, 
        message_id: Optional[UUID],
        context: Dict[str, Any]
    ) -> None:
        """Track what context was accessed for transparency"""
        # Track profile access
        if context.get("profile"):
            self._record_context_access(
                conversation_id,
                message_id,
                "profile",
                context["profile"].get("profile_id"),
                "immigration_profiles",
                "Basic profile information for personalized assistance"
            )
        
        # Track status access
        if context.get("current_status"):
            self._record_context_access(
                conversation_id,
                message_id,
                "status",
                None,
                "immigration_statuses",
                "Current immigration status details"
            )
        
        # Track document access
        if context.get("recent_documents"):
            self._record_context_access(
                conversation_id,
                message_id,
                "document",
                None,
                "document_metadata",
                f"Recent {len(context['recent_documents'])} documents for deadline tracking"
            )
    
    def _record_context_access(
        self,
        conversation_id: UUID,
        message_id: Optional[UUID],
        context_type: str,
        entity_id: Optional[str],
        entity_table: str,
        access_reason: str
    ) -> None:
        """Record a single context access"""
        context_access = ConversationContext(
            conversation_id=conversation_id,
            message_id=message_id,
            context_type=context_type,
            entity_id=UUID(entity_id) if entity_id else None,
            entity_table=entity_table,
            access_reason=access_reason,
            data_summary={}  # Could add summary of what was accessed
        )
        self.db.add(context_access)
        self.db.commit()