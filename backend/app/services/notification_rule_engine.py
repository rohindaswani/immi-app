from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, date
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging

from app.db.models import (
    User,
    ImmigrationProfile,
    DocumentMetadata,
    TimelineDeadline,
    Notification
)
from app.services.notification_service import NotificationService
from app.services.email_service import EmailService
from app.schemas.notification import NotificationCreate, DeadlineNotificationCreate

logger = logging.getLogger(__name__)


class NotificationRuleEngine:
    """Rule engine for automated notification generation"""
    
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)
        self.email_service = EmailService()
    
    def run_all_rules(self) -> Dict[str, Any]:
        """Run all notification rules and return summary"""
        results = {
            "document_expiry_alerts": 0,
            "deadline_reminders": 0,
            "checkin_reminders": 0,
            "status_warnings": 0,
            "total_notifications_created": 0,
            "errors": []
        }
        
        try:
            # Run document expiry checks
            results["document_expiry_alerts"] = self._check_document_expiry()
            
            # Run deadline reminders
            results["deadline_reminders"] = self._check_upcoming_deadlines()
            
            # Run monthly check-in reminders
            results["checkin_reminders"] = self._check_monthly_checkins()
            
            # Run status warnings (e.g., approaching I-94 expiry)
            results["status_warnings"] = self._check_status_warnings()
            
            # Calculate total
            results["total_notifications_created"] = (
                results["document_expiry_alerts"] + 
                results["deadline_reminders"] + 
                results["checkin_reminders"] + 
                results["status_warnings"]
            )
            
            logger.info(f"Rule engine completed: {results['total_notifications_created']} notifications created")
            
        except Exception as e:
            logger.error(f"Error in rule engine: {str(e)}")
            results["errors"].append(str(e))
        
        return results
    
    def _check_document_expiry(self) -> int:
        """Check for documents that are expiring soon"""
        notifications_created = 0
        
        # Get all documents that expire within 180 days (6 months)
        expiry_threshold = date.today() + timedelta(days=180)
        
        documents = self.db.query(DocumentMetadata).join(ImmigrationProfile).filter(
            and_(
                DocumentMetadata.expiry_date.is_not(None),
                DocumentMetadata.expiry_date <= expiry_threshold,
                DocumentMetadata.expiry_date >= date.today()  # Not already expired
            )
        ).all()
        
        for doc in documents:
            days_until_expiry = (doc.expiry_date - date.today()).days
            
            # Check if we should send alert based on days until expiry
            alert_days = self._get_document_alert_days(doc.document_type)
            
            if days_until_expiry in alert_days:
                # Check if we've already sent this alert
                existing_notification = self._check_existing_notification(
                    doc.profile.user_id,
                    "document_expiry",
                    doc.document_id
                )
                
                if not existing_notification:
                    notification_data = NotificationCreate(
                        type="document_expiry",
                        title=f"{doc.document_type} Expiring Soon",
                        content=f"Your {doc.document_type} (#{doc.document_number}) expires in {days_until_expiry} days on {doc.expiry_date}. Please renew it soon.",
                        priority=self._get_expiry_priority(days_until_expiry),
                        related_entity_type="document",
                        related_entity_id=doc.document_id,
                        expires_at=datetime.combine(doc.expiry_date + timedelta(days=30), datetime.min.time())
                    )
                    
                    # Create in-app notification
                    self.notification_service.create_notification(
                        doc.profile.user_id,
                        notification_data
                    )
                    
                    # Send email notification if user has email notifications enabled
                    preferences = self.notification_service.get_user_notification_preferences(doc.profile.user_id)
                    if preferences.get("email_notifications", True) and preferences.get("document_expiry_alerts", True):
                        user = self.db.query(User).filter(User.user_id == doc.profile.user_id).first()
                        if user and user.email:
                            self.email_service.send_document_expiry_email(
                                to_email=user.email,
                                user_name=f"{user.first_name} {user.last_name}" if user.first_name else "User",
                                document_type=doc.document_type,
                                document_number=doc.document_number or "N/A",
                                expiry_date=datetime.combine(doc.expiry_date, datetime.min.time()),
                                days_until=days_until_expiry
                            )
                    
                    notifications_created += 1
        
        return notifications_created
    
    def _check_upcoming_deadlines(self) -> int:
        """Check for upcoming timeline deadlines"""
        notifications_created = 0
        
        # Get deadlines in the next 30 days
        deadline_threshold = date.today() + timedelta(days=30)
        
        deadlines = self.db.query(TimelineDeadline).join(ImmigrationProfile).filter(
            and_(
                TimelineDeadline.deadline_date <= deadline_threshold,
                TimelineDeadline.deadline_date >= date.today(),
                TimelineDeadline.is_completed == False
            )
        ).all()
        
        for deadline in deadlines:
            days_until_deadline = (deadline.deadline_date - date.today()).days
            
            # Check if we should send alert
            if days_until_deadline in deadline.alert_days_before:
                existing_notification = self._check_existing_notification(
                    deadline.profile.user_id,
                    "deadline",
                    deadline.deadline_id
                )
                
                if not existing_notification:
                    priority = "high" if deadline.is_critical or days_until_deadline <= 7 else "medium"
                    
                    notification_data = NotificationCreate(
                        type="deadline",
                        title=f"Deadline Approaching: {deadline.deadline_title}",
                        content=deadline.deadline_description or f"You have a deadline in {days_until_deadline} days",
                        priority=priority,
                        related_entity_type="timeline_deadline",
                        related_entity_id=deadline.deadline_id,
                        expires_at=datetime.combine(deadline.deadline_date + timedelta(days=7), datetime.min.time())
                    )
                    
                    # Create in-app notification
                    self.notification_service.create_notification(
                        deadline.profile.user_id,
                        notification_data
                    )
                    
                    # Send email notification if user has email notifications enabled
                    preferences = self.notification_service.get_user_notification_preferences(deadline.profile.user_id)
                    if preferences.get("email_notifications", True) and preferences.get("deadline_alerts", True):
                        user = self.db.query(User).filter(User.user_id == deadline.profile.user_id).first()
                        if user and user.email:
                            self.email_service.send_deadline_alert_email(
                                to_email=user.email,
                                user_name=f"{user.first_name} {user.last_name}" if user.first_name else "User",
                                deadline_title=deadline.deadline_title,
                                deadline_date=datetime.combine(deadline.deadline_date, datetime.min.time()),
                                days_until=days_until_deadline,
                                deadline_type=deadline.deadline_type,
                                is_critical=deadline.is_critical
                            )
                    
                    notifications_created += 1
        
        return notifications_created
    
    def _check_monthly_checkins(self) -> int:
        """Check for users who need monthly check-in reminders"""
        notifications_created = 0
        
        # Get users who haven't had a check-in notification in the last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        users_needing_checkin = self.db.query(User).join(ImmigrationProfile).filter(
            ~User.user_id.in_(
                self.db.query(Notification.user_id).filter(
                    and_(
                        Notification.type == "checkin",
                        Notification.created_at >= thirty_days_ago
                    )
                )
            )
        ).all()
        
        for user in users_needing_checkin:
            # Check user preferences
            preferences = self.notification_service.get_user_notification_preferences(user.user_id)
            
            if preferences.get("checkin_reminders", True):
                notification_data = NotificationCreate(
                    type="checkin",
                    title="Monthly Status Check-In",
                    content="It's time for your monthly immigration status check-in. Please review your timeline and update any changes in your profile.",
                    priority="medium",
                    related_entity_type="profile",
                    expires_at=datetime.utcnow() + timedelta(days=7)
                )
                
                # Create in-app notification  
                self.notification_service.create_notification(
                    user.user_id,
                    notification_data
                )
                
                # Send email notification if user has email notifications enabled
                if preferences.get("email_notifications", True):
                    self.email_service.send_monthly_checkin_email(
                        to_email=user.email,
                        user_name=f"{user.first_name} {user.last_name}" if user.first_name else "User"
                    )
                
                notifications_created += 1
        
        return notifications_created
    
    def _check_status_warnings(self) -> int:
        """Check for status-related warnings (I-94 expiry, etc.)"""
        notifications_created = 0
        
        # Check I-94 expiry warnings
        ninety_days_from_now = date.today() + timedelta(days=90)
        
        profiles = self.db.query(ImmigrationProfile).filter(
            and_(
                ImmigrationProfile.authorized_stay_until.is_not(None),
                ImmigrationProfile.authorized_stay_until <= ninety_days_from_now,
                ImmigrationProfile.authorized_stay_until >= date.today()
            )
        ).all()
        
        for profile in profiles:
            days_until_expiry = (profile.authorized_stay_until - date.today()).days
            
            # Send alerts at 90, 60, 30, 14, 7, and 1 day(s) before
            alert_days = [90, 60, 30, 14, 7, 1]
            
            if days_until_expiry in alert_days:
                existing_notification = self._check_existing_notification(
                    profile.user_id,
                    "i94_expiry",
                    profile.profile_id
                )
                
                if not existing_notification:
                    priority = "high" if days_until_expiry <= 30 else "medium"
                    
                    notification_data = NotificationCreate(
                        type="i94_expiry",
                        title="I-94 Authorized Stay Expiring Soon",
                        content=f"Your authorized stay in the US expires in {days_until_expiry} days on {profile.authorized_stay_until}. Please ensure you maintain legal status.",
                        priority=priority,
                        related_entity_type="profile",
                        related_entity_id=profile.profile_id,
                        expires_at=datetime.combine(profile.authorized_stay_until + timedelta(days=30), datetime.min.time())
                    )
                    
                    self.notification_service.create_notification(
                        profile.user_id,
                        notification_data
                    )
                    notifications_created += 1
        
        return notifications_created
    
    def _get_document_alert_days(self, document_type: str) -> List[int]:
        """Get alert days based on document type"""
        alert_schedules = {
            "passport": [180, 90, 60, 30, 14],  # 6 months to 2 weeks
            "visa": [180, 90, 60, 30, 14, 7, 1],  # More frequent for visas
            "ead": [120, 90, 60, 30, 14, 7, 1],  # 4 months to 1 day
            "i797": [180, 90, 60, 30, 14],
            "drivers_license": [60, 30, 14, 7],  # 2 months to 1 week
            "default": [90, 60, 30, 14, 7]  # Default schedule
        }
        
        return alert_schedules.get(document_type.lower(), alert_schedules["default"])
    
    def _get_expiry_priority(self, days_until_expiry: int) -> str:
        """Get priority based on days until expiry"""
        if days_until_expiry <= 7:
            return "high"
        elif days_until_expiry <= 30:
            return "medium"
        else:
            return "low"
    
    def _check_existing_notification(
        self, 
        user_id: UUID, 
        notification_type: str, 
        related_entity_id: UUID
    ) -> bool:
        """Check if a similar notification already exists"""
        # Look for notifications created in the last 7 days for the same entity
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        existing = self.db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.type == notification_type,
                Notification.related_entity_id == related_entity_id,
                Notification.created_at >= seven_days_ago
            )
        ).first()
        
        return existing is not None
    
    def create_custom_deadline(
        self, 
        user_id: UUID,
        profile_id: UUID,
        deadline_data: Dict[str, Any]
    ) -> Optional[UUID]:
        """Create a custom deadline with notifications"""
        try:
            # Create the timeline deadline
            deadline = TimelineDeadline(
                profile_id=profile_id,
                deadline_type=deadline_data.get("deadline_type", "custom"),
                deadline_date=deadline_data["deadline_date"],
                deadline_title=deadline_data["deadline_title"],
                deadline_description=deadline_data.get("deadline_description"),
                alert_days_before=deadline_data.get("alert_days_before", [30, 14, 7, 1]),
                is_critical=deadline_data.get("is_critical", False)
            )
            
            self.db.add(deadline)
            self.db.commit()
            self.db.refresh(deadline)
            
            # Create initial notification if deadline is soon
            days_until = (deadline_data["deadline_date"] - date.today()).days
            if days_until <= 30:
                deadline_notification = DeadlineNotificationCreate(
                    deadline_type=deadline.deadline_type,
                    deadline_date=deadline.deadline_date,
                    deadline_title=deadline.deadline_title,
                    deadline_description=deadline.deadline_description,
                    alert_days_before=deadline.alert_days_before,
                    is_critical=deadline.is_critical
                )
                
                self.notification_service.create_deadline_notification(
                    user_id,
                    profile_id,
                    deadline_notification
                )
            
            return deadline.deadline_id
            
        except Exception as e:
            logger.error(f"Error creating custom deadline: {str(e)}")
            return None