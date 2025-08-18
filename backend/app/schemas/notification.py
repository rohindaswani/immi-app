from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class NotificationBase(BaseModel):
    """Base notification schema"""
    type: str = Field(..., description="Notification type (check-in, deadline, alert, etc.)")
    title: str = Field(..., max_length=255, description="Notification title")
    content: Optional[str] = Field(None, description="Notification content")
    priority: str = Field("medium", description="Priority level (high, medium, low)")
    related_entity_type: Optional[str] = Field(None, description="Related entity type")
    related_entity_id: Optional[UUID] = Field(None, description="Related entity ID")
    scheduled_for: Optional[datetime] = Field(None, description="When to send the notification")
    expires_at: Optional[datetime] = Field(None, description="When the notification expires")


class NotificationCreate(NotificationBase):
    """Schema for creating a notification"""
    pass


class NotificationUpdate(BaseModel):
    """Schema for updating a notification"""
    is_read: Optional[bool] = None
    expires_at: Optional[datetime] = None


class NotificationInDB(NotificationBase):
    """Schema for notification stored in database"""
    notification_id: UUID
    user_id: UUID
    is_read: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationResponse(NotificationInDB):
    """Schema for notification API response"""
    pass


class NotificationListResponse(BaseModel):
    """Schema for paginated notification list response"""
    notifications: List[NotificationResponse]
    total_count: int
    unread_count: int
    page: int = 1
    page_size: int = 20


class DeadlineNotificationCreate(BaseModel):
    """Schema for creating deadline-based notifications"""
    deadline_type: str = Field(..., description="Type of deadline (document_expiry, filing_deadline, etc.)")
    deadline_date: datetime = Field(..., description="Deadline date")
    deadline_title: str = Field(..., max_length=255, description="Deadline title")
    deadline_description: Optional[str] = Field(None, description="Deadline description")
    alert_days_before: List[int] = Field([30, 14, 7, 1], description="Days before deadline to send alerts")
    is_critical: bool = Field(False, description="Whether this is a critical deadline")


class CheckInReminderCreate(BaseModel):
    """Schema for creating monthly check-in reminders"""
    reminder_type: str = Field("monthly_checkin", description="Type of reminder")
    frequency_days: int = Field(30, description="Frequency in days")
    next_reminder_date: datetime = Field(..., description="Next reminder date")
    is_active: bool = Field(True, description="Whether reminder is active")


class NotificationStats(BaseModel):
    """Schema for notification statistics"""
    total_notifications: int
    unread_count: int
    critical_count: int
    upcoming_deadlines_count: int
    overdue_count: int