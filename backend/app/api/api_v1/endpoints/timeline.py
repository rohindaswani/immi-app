from typing import List, Optional
from uuid import UUID
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.postgres import get_db
from app.db.models import User, ImmigrationProfile
from app.schemas.timeline import (
    ImmigrationTimeline,
    ImmigrationTimelineCreate,
    ImmigrationTimelineUpdate,
    TimelineMilestone,
    TimelineMilestoneCreate,
    TimelineMilestoneUpdate,
    TimelineDeadline,
    TimelineDeadlineCreate,
    TimelineDeadlineUpdate,
    TimelineStatusHistory,
    TimelineStatusHistoryCreate,
    TimelineStatusHistoryUpdate,
    TimelineEventType,
    EventCategory,
    PriorityLevel,
)
from app.services.timeline import timeline_service

router = APIRouter()

# Timeline Events Endpoints
@router.get("/events", response_model=List[ImmigrationTimeline])
def get_timeline_events(
    *,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    event_type: Optional[TimelineEventType] = Query(None),
    # Removed category parameter since column doesn't exist yet
    # category: Optional[EventCategory] = Query(None),
    priority: Optional[PriorityLevel] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    is_milestone: Optional[bool] = Query(None),
    is_deadline: Optional[bool] = Query(None),
) -> List[ImmigrationTimeline]:
    """
    Get timeline events for the current user with optional filtering
    """
    try:
        return timeline_service.get_user_timeline_events(
            db=db,
            user_id=current_user_id,
            skip=skip,
            limit=limit,
            event_type=event_type,
            # Removed category parameter
            # category=category,
            priority=priority,
            start_date=start_date,
            end_date=end_date,
            is_milestone=is_milestone,
            is_deadline=is_deadline,
        )
    except Exception as e:
        print(f"Error in get_timeline_events API: {e}")
        return []

@router.post("/events", response_model=ImmigrationTimeline)
def create_timeline_event(
    *,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user),
    event_in: ImmigrationTimelineCreate,
) -> ImmigrationTimeline:
    """
    Create a new timeline event
    """
    return timeline_service.create_timeline_event(
        db=db, user_id=current_user_id, event_in=event_in
    )

@router.get("/events/{event_id}", response_model=ImmigrationTimeline)
def get_timeline_event(
    *,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user),
    event_id: UUID,
) -> ImmigrationTimeline:
    """
    Get a specific timeline event
    """
    event = timeline_service.get_timeline_event(
        db=db, user_id=current_user_id, event_id=event_id
    )
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timeline event not found"
        )
    return event

@router.put("/events/{event_id}", response_model=ImmigrationTimeline)
def update_timeline_event(
    *,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user),
    event_id: UUID,
    event_in: ImmigrationTimelineUpdate,
) -> ImmigrationTimeline:
    """
    Update a timeline event
    """
    event = timeline_service.update_timeline_event(
        db=db, user_id=current_user_id, event_id=event_id, event_in=event_in
    )
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timeline event not found"
        )
    return event

@router.delete("/events/{event_id}")
def delete_timeline_event(
    *,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user),
    event_id: UUID,
) -> dict:
    """
    Delete a timeline event
    """
    success = timeline_service.delete_timeline_event(
        db=db, user_id=current_user_id, event_id=event_id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timeline event not found"
        )
    return {"message": "Timeline event deleted successfully"}

# Milestone Management Endpoints
@router.get("/milestones", response_model=List[TimelineMilestone])
def get_milestones(
    *,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user),
    immigration_path: Optional[str] = Query(None),
    category: Optional[EventCategory] = Query(None),
) -> List[TimelineMilestone]:
    """
    Get milestone templates
    """
    return timeline_service.get_milestones(
        db=db, immigration_path=immigration_path, category=category
    )

@router.post("/milestones", response_model=TimelineMilestone)
def create_milestone(
    *,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user),
    milestone_in: TimelineMilestoneCreate,
) -> TimelineMilestone:
    """
    Create a new milestone template (admin only)
    """
    # TODO: Add superuser check when user object is available
    # For now, allow all authenticated users to create milestones
    return timeline_service.create_milestone(db=db, milestone_in=milestone_in)

# Deadline Management Endpoints
@router.get("/deadlines", response_model=List[TimelineDeadline])
def get_deadlines(
    *,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user),
    upcoming_only: bool = Query(True),
    days_ahead: int = Query(30, ge=1, le=365),
) -> List[TimelineDeadline]:
    """
    Get user's deadlines
    """
    return timeline_service.get_user_deadlines(
        db=db,
        user_id=current_user_id,
        upcoming_only=upcoming_only,
        days_ahead=days_ahead,
    )

@router.post("/deadlines", response_model=TimelineDeadline)
def create_deadline(
    *,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user),
    deadline_in: TimelineDeadlineCreate,
) -> TimelineDeadline:
    """
    Create a new deadline
    """
    return timeline_service.create_deadline(
        db=db, user_id=current_user_id, deadline_in=deadline_in
    )

@router.put("/deadlines/{deadline_id}", response_model=TimelineDeadline)
def update_deadline(
    *,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user),
    deadline_id: UUID,
    deadline_in: TimelineDeadlineUpdate,
) -> TimelineDeadline:
    """
    Update a deadline
    """
    deadline = timeline_service.update_deadline(
        db=db, user_id=current_user_id, deadline_id=deadline_id, deadline_in=deadline_in
    )
    if not deadline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deadline not found"
        )
    return deadline

@router.delete("/deadlines/{deadline_id}")
def delete_deadline(
    *,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user),
    deadline_id: UUID,
) -> dict:
    """
    Delete a deadline
    """
    success = timeline_service.delete_deadline(
        db=db, user_id=current_user_id, deadline_id=deadline_id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deadline not found"
        )
    return {"message": "Deadline deleted successfully"}

# Status History Endpoints
@router.get("/status-history", response_model=List[TimelineStatusHistory])
def get_status_history(
    *,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> List[TimelineStatusHistory]:
    """
    Get user's immigration status change history
    """
    return timeline_service.get_user_status_history(
        db=db, user_id=current_user_id, skip=skip, limit=limit
    )

@router.post("/status-history", response_model=TimelineStatusHistory)
def create_status_change(
    *,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user),
    status_in: TimelineStatusHistoryCreate,
) -> TimelineStatusHistory:
    """
    Record a new status change
    """
    return timeline_service.create_status_change(
        db=db, user_id=current_user_id, status_in=status_in
    )

# Timeline Analytics Endpoints
@router.get("/analytics/summary")
def get_timeline_summary(
    *,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user),
) -> dict:
    """
    Get timeline analytics summary
    """
    try:
        return timeline_service.get_timeline_summary(db=db, user_id=current_user_id)
    except Exception as e:
        print(f"Error in get_timeline_summary API: {e}")
        return {
            "total_events": 0,
            "milestones_completed": 0,
            "total_milestones": 0,
            "milestone_completion_rate": 0,
            "upcoming_deadlines": 0,
            "overdue_deadlines": 0,
        }

@router.get("/analytics/progress")
def get_progress_analytics(
    *,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user),
    immigration_path: Optional[str] = Query(None),
) -> dict:
    """
    Get progress analytics for immigration journey
    """
    try:
        return timeline_service.get_progress_analytics(
            db=db, user_id=current_user_id, immigration_path=immigration_path
        )
    except Exception as e:
        print(f"Error in get_progress_analytics API: {e}")
        return {
            "immigration_path": immigration_path,
            "total_milestones": 0,
            "completed_milestones": 0,
            "remaining_milestones": 0,
            "progress_percentage": 0,
            "estimated_completion_months": 0,
        }