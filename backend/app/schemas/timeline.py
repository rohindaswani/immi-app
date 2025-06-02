from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum

class TimelineEventType(str, Enum):
    APPLICATION = "application"
    INTERVIEW = "interview"
    DECISION = "decision"
    DOCUMENT_REQUEST = "document_request"
    DEADLINE = "deadline"
    STATUS_CHANGE = "status_change"
    TRAVEL = "travel"
    OTHER = "other"

class EventCategory(str, Enum):
    VISA = "visa"
    GREEN_CARD = "green_card"
    CITIZENSHIP = "citizenship"
    WORK_PERMIT = "work_permit"
    TRAVEL_DOCUMENT = "travel_document"
    OTHER = "other"

class EventSubtype(str, Enum):
    H1B = "h1b"
    L1 = "l1"
    O1 = "o1"
    EB1 = "eb1"
    EB2 = "eb2"
    EB3 = "eb3"
    FAMILY_BASED = "family_based"
    ASYLUM = "asylum"
    OTHER = "other"

class PriorityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ImmigrationStatus(str, Enum):
    PREPARING = "preparing"
    SUBMITTED = "submitted"
    IN_REVIEW = "in_review"
    RFE_RECEIVED = "rfe_received"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    APPROVED = "approved"
    DENIED = "denied"
    PENDING = "pending"
    OTHER = "other"

class AlertFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

from uuid import UUID as UUIDType

class ImmigrationTimelineBase(BaseModel):
    event_title: str = Field(..., max_length=255)
    description: Optional[str] = None
    event_date: datetime
    event_type: str = Field(..., max_length=100)  # Changed to string to match DB
    # Uncommented fields that are in the DB model
    event_category: Optional[str] = None
    event_subtype: Optional[str] = None
    priority: Optional[str] = None
    is_milestone: Optional[bool] = None
    event_status: Optional[str] = None
    # These fields need to be valid UUIDs or None
    reference_id: Optional[UUIDType] = None
    reference_table: Optional[str] = None
    document_id: Optional[UUIDType] = None

class ImmigrationTimelineCreate(ImmigrationTimelineBase):
    pass

class ImmigrationTimelineUpdate(BaseModel):
    event_title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    event_date: Optional[datetime] = None
    event_type: Optional[str] = Field(None, max_length=100)
    # Uncommented fields that are in the DB model
    event_category: Optional[str] = None
    event_subtype: Optional[str] = None
    priority: Optional[str] = None
    is_milestone: Optional[bool] = None
    event_status: Optional[str] = None
    # These fields need to be valid UUIDs or None
    reference_id: Optional[UUIDType] = None
    reference_table: Optional[str] = None
    document_id: Optional[UUIDType] = None

class ImmigrationTimelineInDB(ImmigrationTimelineBase):
    event_id: str
    profile_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    document_id: Optional[str] = None
    travel_record_id: Optional[str] = None
    immigration_status_id: Optional[str] = None

    class Config:
        from_attributes = True

class ImmigrationTimeline(ImmigrationTimelineInDB):
    pass

# Timeline Milestone Schemas
class TimelineMilestoneBase(BaseModel):
    milestone_name: str = Field(..., max_length=200)
    description: Optional[str] = None
    immigration_path: str = Field(..., max_length=100)
    category: EventCategory
    estimated_days_from_start: Optional[int] = None
    is_required: bool = True
    order_sequence: Optional[int] = None
    completion_criteria: Optional[str] = None
    required_documents: Optional[List[str]] = None
    extra_data: Optional[Dict[str, Any]] = None

class TimelineMilestoneCreate(TimelineMilestoneBase):
    pass

class TimelineMilestoneUpdate(BaseModel):
    milestone_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    immigration_path: Optional[str] = Field(None, max_length=100)
    category: Optional[EventCategory] = None
    estimated_days_from_start: Optional[int] = None
    is_required: Optional[bool] = None
    order_sequence: Optional[int] = None
    completion_criteria: Optional[str] = None
    required_documents: Optional[List[str]] = None
    extra_data: Optional[Dict[str, Any]] = None

class TimelineMilestoneInDB(TimelineMilestoneBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TimelineMilestone(TimelineMilestoneInDB):
    pass

# Timeline Deadline Schemas
class TimelineDeadlineBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    deadline_date: datetime
    deadline_type: str = Field(..., max_length=100)
    priority_level: PriorityLevel = PriorityLevel.MEDIUM
    is_completed: bool = False
    alert_enabled: bool = True
    alert_days_before: int = Field(7, ge=0)
    alert_frequency: AlertFrequency = AlertFrequency.DAILY
    completion_notes: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None

class TimelineDeadlineCreate(TimelineDeadlineBase):
    pass

class TimelineDeadlineUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    deadline_date: Optional[datetime] = None
    deadline_type: Optional[str] = Field(None, max_length=100)
    priority_level: Optional[PriorityLevel] = None
    is_completed: Optional[bool] = None
    alert_enabled: Optional[bool] = None
    alert_days_before: Optional[int] = Field(None, ge=0)
    alert_frequency: Optional[AlertFrequency] = None
    completion_notes: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None

class TimelineDeadlineInDB(TimelineDeadlineBase):
    id: int
    user_id: int
    timeline_event_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TimelineDeadline(TimelineDeadlineInDB):
    pass

# Timeline Status History Schemas
class TimelineStatusHistoryBase(BaseModel):
    # Changed from enum to ID reference
    to_status_id: str  
    from_status_id: Optional[str] = None
    status_description: Optional[str] = None
    notes: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None

class TimelineStatusHistoryCreate(TimelineStatusHistoryBase):
    pass

class TimelineStatusHistoryUpdate(BaseModel):
    to_status_id: Optional[str] = None
    from_status_id: Optional[str] = None
    status_description: Optional[str] = None
    notes: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None

class TimelineStatusHistoryInDB(TimelineStatusHistoryBase):
    id: int
    user_id: int
    timeline_event_id: Optional[int] = None
    changed_at: datetime
    changed_by_user_id: Optional[int] = None

    class Config:
        from_attributes = True

class TimelineStatusHistory(TimelineStatusHistoryInDB):
    pass