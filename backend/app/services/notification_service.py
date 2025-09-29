from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from app.db.models import (
    Notification, 
    User, 
    ImmigrationProfile,
    DocumentMetadata,
    TimelineDeadline,
    UserSettings
)
from app.schemas.notification import (
    NotificationCreate, 
    NotificationUpdate,
    NotificationResponse,
    NotificationListResponse,
    DeadlineNotificationCreate,
    CheckInReminderCreate,
    NotificationStats
)


class NotificationService:
    """Service for managing notifications and alerts"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_notification(
        self, 
        user_id: UUID, 
        notification_data: NotificationCreate
    ) -> NotificationResponse:
        """Create a new notification"""
        notification = Notification(
            user_id=user_id,
            type=notification_data.type,
            title=notification_data.title,
            content=notification_data.content,
            priority=notification_data.priority,
            related_entity_type=notification_data.related_entity_type,
            related_entity_id=notification_data.related_entity_id,
            scheduled_for=notification_data.scheduled_for,
            expires_at=notification_data.expires_at
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        return NotificationResponse.from_orm(notification)
    
    def get_notifications(
        self, 
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
        unread_only: bool = False,
        priority_filter: Optional[str] = None
    ) -> NotificationListResponse:
        """Get paginated notifications for a user"""
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        
        # Apply filters
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        if priority_filter:
            query = query.filter(Notification.priority == priority_filter)
        
        # Filter out expired notifications
        query = query.filter(
            or_(
                Notification.expires_at.is_(None),
                Notification.expires_at > datetime.utcnow()
            )
        )
        
        # Get total count
        total_count = query.count()
        
        # Get unread count
        unread_count = self.db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False,
                or_(
                    Notification.expires_at.is_(None),
                    Notification.expires_at > datetime.utcnow()
                )
            )
        ).count()
        
        # Apply pagination and ordering
        notifications = query.order_by(
            desc(Notification.priority == 'high'),
            desc(Notification.created_at)
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        return NotificationListResponse(
            notifications=[NotificationResponse.from_orm(n) for n in notifications],
            total_count=total_count,
            unread_count=unread_count,
            page=page,
            page_size=page_size
        )
    
    def mark_as_read(self, notification_id: UUID, user_id: UUID) -> bool:
        """Mark a notification as read"""
        notification = self.db.query(Notification).filter(
            and_(
                Notification.notification_id == notification_id,
                Notification.user_id == user_id
            )
        ).first()
        
        if notification:
            notification.is_read = True
            self.db.commit()
            return True
        
        return False
    
    def mark_all_as_read(self, user_id: UUID) -> int:
        """Mark all notifications as read for a user"""
        updated_count = self.db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        ).update({Notification.is_read: True})
        
        self.db.commit()
        return updated_count
    
    def delete_notification(self, notification_id: UUID, user_id: UUID) -> bool:
        """Delete a notification"""
        notification = self.db.query(Notification).filter(
            and_(
                Notification.notification_id == notification_id,
                Notification.user_id == user_id
            )
        ).first()
        
        if notification:
            self.db.delete(notification)
            self.db.commit()
            return True
        
        return False
    
    def get_notification_stats(self, user_id: UUID) -> NotificationStats:
        """Get notification statistics for a user"""
        now = datetime.utcnow()
        
        # Basic counts
        total_notifications = self.db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                or_(
                    Notification.expires_at.is_(None),
                    Notification.expires_at > now
                )
            )
        ).count()
        
        unread_count = self.db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False,
                or_(
                    Notification.expires_at.is_(None),
                    Notification.expires_at > now
                )
            )
        ).count()
        
        critical_count = self.db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.priority == 'high',
                Notification.is_read == False,
                or_(
                    Notification.expires_at.is_(None),
                    Notification.expires_at > now
                )
            )
        ).count()
        
        # Get user's profile to check deadlines
        profile = self.db.query(ImmigrationProfile).filter(
            ImmigrationProfile.user_id == user_id
        ).first()
        
        upcoming_deadlines_count = 0
        overdue_count = 0
        
        if profile:
            # Check timeline deadlines
            deadlines = self.db.query(TimelineDeadline).filter(
                and_(
                    TimelineDeadline.profile_id == profile.profile_id,
                    TimelineDeadline.is_completed == False
                )
            ).all()
            
            for deadline in deadlines:
                days_until = (deadline.deadline_date - date.today()).days
                if days_until < 0:
                    overdue_count += 1
                elif days_until <= 30:  # Upcoming in 30 days
                    upcoming_deadlines_count += 1
        
        return NotificationStats(
            total_notifications=total_notifications,
            unread_count=unread_count,
            critical_count=critical_count,
            upcoming_deadlines_count=upcoming_deadlines_count,
            overdue_count=overdue_count
        )
    
    def create_deadline_notification(
        self, 
        user_id: UUID, 
        profile_id: UUID,
        deadline_data: DeadlineNotificationCreate
    ) -> NotificationResponse:
        """Create a deadline-based notification"""
        days_until = (deadline_data.deadline_date.date() - date.today()).days
        
        # Determine priority based on days until deadline
        if days_until <= 7:
            priority = "high"
        elif days_until <= 30:
            priority = "medium"  
        else:
            priority = "low"
        
        if deadline_data.is_critical:
            priority = "high"
        
        # Create the notification
        notification_data = NotificationCreate(
            type="deadline",
            title=deadline_data.deadline_title,
            content=deadline_data.deadline_description or f"Deadline in {days_until} days",
            priority=priority,
            related_entity_type="timeline_deadline",
            related_entity_id=profile_id,
            expires_at=deadline_data.deadline_date + timedelta(days=7)  # Expire 7 days after deadline
        )
        
        return self.create_notification(user_id, notification_data)
    
    def create_checkin_reminder(
        self, 
        user_id: UUID, 
        reminder_data: CheckInReminderCreate
    ) -> NotificationResponse:
        """Create a monthly check-in reminder"""
        notification_data = NotificationCreate(
            type="checkin",
            title="Monthly Status Check-In",
            content="Time for your monthly immigration status check-in. Please review your timeline and update any changes.",
            priority="medium",
            related_entity_type="profile",
            scheduled_for=reminder_data.next_reminder_date,
            expires_at=reminder_data.next_reminder_date + timedelta(days=7)
        )
        
        return self.create_notification(user_id, notification_data)
    
    def cleanup_expired_notifications(self) -> int:
        """Clean up expired notifications"""
        expired_count = self.db.query(Notification).filter(
            and_(
                Notification.expires_at.is_not(None),
                Notification.expires_at < datetime.utcnow()
            )
        ).delete()
        
        self.db.commit()
        return expired_count
    
    def get_user_notification_preferences(self, user_id: UUID) -> Dict[str, Any]:
        """Get user's notification preferences"""
        settings = self.db.query(UserSettings).filter(
            UserSettings.user_id == user_id
        ).first()
        
        if settings and settings.notification_preferences:
            return settings.notification_preferences
        
        # Default preferences
        return {
            "email_notifications": True,
            "deadline_alerts": True,
            "checkin_reminders": True,
            "document_expiry_alerts": True,
            "status_change_notifications": True
        }
    
    def update_notification_preferences(
        self, 
        user_id: UUID, 
        preferences: Dict[str, Any]
    ) -> bool:
        """Update user's notification preferences"""
        settings = self.db.query(UserSettings).filter(
            UserSettings.user_id == user_id
        ).first()
        
        if settings:
            settings.notification_preferences = preferences
            self.db.commit()
            return True
        
        return False