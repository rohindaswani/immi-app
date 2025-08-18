from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.services.notification_service import NotificationService
from app.services.notification_rule_engine import NotificationRuleEngine
from app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    NotificationCreate,
    NotificationUpdate,
    NotificationStats,
    DeadlineNotificationCreate,
    CheckInReminderCreate
)

router = APIRouter()


@router.get("/", response_model=NotificationListResponse)
def get_notifications(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    unread_only: bool = Query(False, description="Show only unread notifications"),
    priority_filter: Optional[str] = Query(None, description="Filter by priority"),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get paginated notifications for the current user"""
    try:
        service = NotificationService(db)
        user_uuid = UUID(current_user)
        
        return service.get_notifications(
            user_id=user_uuid,
            page=page,
            page_size=page_size,
            unread_only=unread_only,
            priority_filter=priority_filter
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching notifications: {str(e)}")


@router.get("/stats", response_model=NotificationStats)
def get_notification_stats(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notification statistics for the current user"""
    try:
        service = NotificationService(db)
        user_uuid = UUID(current_user)
        
        return service.get_notification_stats(user_uuid)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching notification stats: {str(e)}")


@router.post("/", response_model=NotificationResponse, status_code=201)
def create_notification(
    notification_data: NotificationCreate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new notification"""
    try:
        service = NotificationService(db)
        user_uuid = UUID(current_user)
        
        return service.create_notification(user_uuid, notification_data)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating notification: {str(e)}")


@router.patch("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: UUID,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a specific notification as read"""
    try:
        service = NotificationService(db)
        user_uuid = UUID(current_user)
        
        success = service.mark_as_read(notification_id, user_uuid)
        if not success:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return {"message": "Notification marked as read"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating notification: {str(e)}")


@router.patch("/read-all")
def mark_all_notifications_as_read(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read for the current user"""
    try:
        service = NotificationService(db)
        user_uuid = UUID(current_user)
        
        updated_count = service.mark_all_as_read(user_uuid)
        return {"message": f"Marked {updated_count} notifications as read"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating notifications: {str(e)}")


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: UUID,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific notification"""
    try:
        service = NotificationService(db)
        user_uuid = UUID(current_user)
        
        success = service.delete_notification(notification_id, user_uuid)
        if not success:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return {"message": "Notification deleted"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting notification: {str(e)}")


@router.post("/deadline", response_model=NotificationResponse, status_code=201)
def create_deadline_notification(
    profile_id: UUID,
    deadline_data: DeadlineNotificationCreate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a deadline-based notification"""
    try:
        service = NotificationService(db)
        user_uuid = UUID(current_user)
        
        return service.create_deadline_notification(
            user_uuid, 
            profile_id, 
            deadline_data
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating deadline notification: {str(e)}")


@router.post("/checkin", response_model=NotificationResponse, status_code=201)
def create_checkin_reminder(
    reminder_data: CheckInReminderCreate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a monthly check-in reminder"""
    try:
        service = NotificationService(db)
        user_uuid = UUID(current_user)
        
        return service.create_checkin_reminder(user_uuid, reminder_data)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating check-in reminder: {str(e)}")


@router.post("/run-rules")
def run_notification_rules(
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually trigger notification rule engine (admin/testing)"""
    def run_rules():
        try:
            rule_engine = NotificationRuleEngine(db)
            results = rule_engine.run_all_rules()
            print(f"Rule engine results: {results}")
        except Exception as e:
            print(f"Error running notification rules: {str(e)}")
    
    background_tasks.add_task(run_rules)
    
    return {"message": "Notification rules triggered in background"}


@router.get("/preferences")
def get_notification_preferences(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's notification preferences"""
    try:
        service = NotificationService(db)
        user_uuid = UUID(current_user)
        
        preferences = service.get_user_notification_preferences(user_uuid)
        return {"preferences": preferences}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching preferences: {str(e)}")


@router.patch("/preferences")
def update_notification_preferences(
    preferences: dict,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's notification preferences"""
    try:
        service = NotificationService(db)
        user_uuid = UUID(current_user)
        
        success = service.update_notification_preferences(user_uuid, preferences)
        if not success:
            raise HTTPException(status_code=404, detail="User settings not found")
        
        return {"message": "Notification preferences updated"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating preferences: {str(e)}")


@router.delete("/cleanup")
def cleanup_expired_notifications(
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clean up expired notifications (admin/maintenance)"""
    def cleanup():
        try:
            service = NotificationService(db)
            cleaned_count = service.cleanup_expired_notifications()
            print(f"Cleaned up {cleaned_count} expired notifications")
        except Exception as e:
            print(f"Error cleaning up notifications: {str(e)}")
    
    background_tasks.add_task(cleanup)
    
    return {"message": "Notification cleanup triggered in background"}