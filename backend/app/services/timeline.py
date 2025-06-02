from typing import List, Optional, Union
from uuid import UUID
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, inspect

from app.db.models import (
    ImmigrationTimeline as TimelineModel,
    TimelineMilestone as MilestoneModel,
    TimelineDeadline as DeadlineModel,
    TimelineStatusHistory as StatusHistoryModel,
    ImmigrationProfile,
)
from app.schemas.timeline import (
    ImmigrationTimelineCreate,
    ImmigrationTimelineUpdate,
    TimelineMilestoneCreate,
    TimelineDeadlineCreate,
    TimelineDeadlineUpdate,
    TimelineStatusHistoryCreate,
    TimelineEventType,
    EventCategory,
    PriorityLevel,
)


class TimelineService:
    """
    Service for managing immigration timeline operations
    """
    
    def _check_tables_exist(self, db: Session) -> bool:
        """Check if the timeline tables exist in the database"""
        try:
            inspector = inspect(db.bind)
            
            # Check if tables exist
            table_exists = (
                'immigration_timeline' in inspector.get_table_names() and
                'timeline_milestones' in inspector.get_table_names() and
                'timeline_deadlines' in inspector.get_table_names() and
                'timeline_status_history' in inspector.get_table_names()
            )
            
            # If the timeline table exists, print its columns for debugging
            if 'immigration_timeline' in inspector.get_table_names():
                print("Immigration timeline table columns:", inspector.get_columns('immigration_timeline'))
                
            return table_exists
        except Exception as e:
            print(f"Error checking if tables exist: {e}")
            return False

    def _ensure_uuid(self, value: Union[str, UUID]) -> UUID:
        """Convert string UUID to UUID object if needed"""
        if isinstance(value, str):
            return UUID(value)
        return value

    def _get_user_profile_id(self, db: Session, user_id: Union[str, UUID]) -> UUID:
        """Get the profile_id for a given user_id, create profile if it doesn't exist"""
        user_uuid = self._ensure_uuid(user_id)
        profile = db.query(ImmigrationProfile).filter(ImmigrationProfile.user_id == user_uuid).first()
        
        if not profile:
            # Create a default immigration profile for the user
            profile = ImmigrationProfile(
                user_id=user_uuid,
                profile_type="primary",
                notes="Auto-created profile for timeline tracking"
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
            
        return profile.profile_id

    def get_user_timeline_events(
        self,
        db: Session,
        user_id: Union[str, UUID],
        skip: int = 0,
        limit: int = 100,
        event_type: Optional[TimelineEventType] = None,
        category: Optional[EventCategory] = None,
        priority: Optional[PriorityLevel] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        is_milestone: Optional[bool] = None,
        is_deadline: Optional[bool] = None,
    ) -> List[TimelineModel]:
        """
        Get filtered timeline events for a user
        """
        if not self._check_tables_exist(db):
            print("Timeline tables don't exist in the database")
            return []
            
        try:
            profile_id = self._get_user_profile_id(db, user_id)
            query = db.query(TimelineModel).filter(TimelineModel.profile_id == profile_id)
        except Exception as e:
            print(f"Error in get_user_timeline_events: {e}")
            return []

        try:
            # Apply filters
            if event_type:
                query = query.filter(TimelineModel.event_type == event_type)
            # Skip category filter since column doesn't exist yet
            # if category:
            #     query = query.filter(TimelineModel.event_category == category)
            if priority:
                query = query.filter(TimelineModel.priority == priority)
            if start_date:
                query = query.filter(TimelineModel.event_date >= start_date)
            if end_date:
                query = query.filter(TimelineModel.event_date <= end_date)
            if is_milestone is not None:
                query = query.filter(TimelineModel.is_milestone.is_(is_milestone))
            if is_deadline is not None:
                query = query.filter(TimelineModel.is_deadline.is_(is_deadline))

            return query.order_by(desc(TimelineModel.event_date)).offset(skip).limit(limit).all()
        except Exception as e:
            print(f"Error applying filters in get_user_timeline_events: {e}")
            return []

    def create_timeline_event(
        self, db: Session, user_id: Union[str, UUID], event_in: ImmigrationTimelineCreate
    ) -> TimelineModel:
        """
        Create a new timeline event
        """
        profile_id = self._get_user_profile_id(db, user_id)
        # No need to pop fields anymore since schema matches DB model
        event_data = event_in.dict()
        
        # Create the event directly with all fields
        db_event = TimelineModel(
            profile_id=profile_id,
            **event_data
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return db_event

    def get_timeline_event(
        self, db: Session, user_id: Union[str, UUID], event_id: UUID
    ) -> Optional[TimelineModel]:
        """
        Get a specific timeline event
        """
        profile_id = self._get_user_profile_id(db, user_id)
        return db.query(TimelineModel).filter(
            and_(TimelineModel.event_id == event_id, TimelineModel.profile_id == profile_id)
        ).first()

    def update_timeline_event(
        self,
        db: Session,
        user_id: Union[str, UUID],
        event_id: UUID,
        event_in: ImmigrationTimelineUpdate,
    ) -> Optional[TimelineModel]:
        """
        Update a timeline event
        """
        db_event = self.get_timeline_event(db, user_id, event_id)
        if not db_event:
            return None

        # No need for special handling now that schema matches DB model
        update_data = event_in.dict(exclude_unset=True)
        
        # Apply updates directly
        for field, value in update_data.items():
            setattr(db_event, field, value)

        db.commit()
        db.refresh(db_event)
        return db_event

    def delete_timeline_event(
        self, db: Session, user_id: UUID, event_id: UUID
    ) -> bool:
        """
        Delete a timeline event
        """
        db_event = self.get_timeline_event(db, user_id, event_id)
        if not db_event:
            return False

        db.delete(db_event)
        db.commit()
        return True

    # Milestone Management
    def get_milestones(
        self,
        db: Session,
        immigration_path: Optional[str] = None,
        category: Optional[EventCategory] = None,
    ) -> List[MilestoneModel]:
        """
        Get milestone templates
        """
        query = db.query(MilestoneModel)

        if immigration_path:
            query = query.filter(MilestoneModel.immigration_path == immigration_path)
        if category:
            query = query.filter(MilestoneModel.category == category)

        return query.order_by(asc(MilestoneModel.order_sequence)).all()

    def create_milestone(
        self, db: Session, milestone_in: TimelineMilestoneCreate
    ) -> MilestoneModel:
        """
        Create a new milestone template
        """
        db_milestone = MilestoneModel(**milestone_in.dict())
        db.add(db_milestone)
        db.commit()
        db.refresh(db_milestone)
        return db_milestone

    # Deadline Management
    def get_user_deadlines(
        self,
        db: Session,
        user_id: Union[str, UUID],
        upcoming_only: bool = True,
        days_ahead: int = 30,
    ) -> List[DeadlineModel]:
        """
        Get user's deadlines
        """
        profile_id = self._get_user_profile_id(db, user_id)
        query = db.query(DeadlineModel).filter(DeadlineModel.profile_id == profile_id)

        if upcoming_only:
            today = date.today()
            future_date = today + timedelta(days=days_ahead)
            query = query.filter(
                and_(
                    DeadlineModel.deadline_date >= today,
                    DeadlineModel.deadline_date <= future_date,
                    DeadlineModel.is_completed.is_(False)
                )
            )

        return query.order_by(asc(DeadlineModel.deadline_date)).all()

    def create_deadline(
        self, db: Session, user_id: UUID, deadline_in: TimelineDeadlineCreate
    ) -> DeadlineModel:
        """
        Create a new deadline
        """
        profile_id = self._get_user_profile_id(db, user_id)
        db_deadline = DeadlineModel(
            profile_id=profile_id,
            **deadline_in.dict()
        )
        db.add(db_deadline)
        db.commit()
        db.refresh(db_deadline)
        return db_deadline

    def update_deadline(
        self,
        db: Session,
        user_id: Union[str, UUID],
        deadline_id: UUID,
        deadline_in: TimelineDeadlineUpdate,
    ) -> Optional[DeadlineModel]:
        """
        Update a deadline
        """
        profile_id = self._get_user_profile_id(db, user_id)
        db_deadline = db.query(DeadlineModel).filter(
            and_(DeadlineModel.deadline_id == deadline_id, DeadlineModel.profile_id == profile_id)
        ).first()

        if not db_deadline:
            return None

        update_data = deadline_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_deadline, field, value)

        db.commit()
        db.refresh(db_deadline)
        return db_deadline

    def delete_deadline(
        self, db: Session, user_id: UUID, deadline_id: UUID
    ) -> bool:
        """
        Delete a deadline
        """
        profile_id = self._get_user_profile_id(db, user_id)
        db_deadline = db.query(DeadlineModel).filter(
            and_(DeadlineModel.deadline_id == deadline_id, DeadlineModel.profile_id == profile_id)
        ).first()

        if not db_deadline:
            return False

        db.delete(db_deadline)
        db.commit()
        return True

    # Status History Management
    def get_user_status_history(
        self, db: Session, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[StatusHistoryModel]:
        """
        Get user's immigration status change history
        """
        profile_id = self._get_user_profile_id(db, user_id)
        return (
            db.query(StatusHistoryModel)
            .filter(StatusHistoryModel.profile_id == profile_id)
            .order_by(desc(StatusHistoryModel.changed_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_status_change(
        self, db: Session, user_id: UUID, status_in: TimelineStatusHistoryCreate
    ) -> StatusHistoryModel:
        """
        Record a new status change
        """
        profile_id = self._get_user_profile_id(db, user_id)
        # No special handling needed now that schema matches DB model
        db_status = StatusHistoryModel(
            profile_id=profile_id,
            changed_at=datetime.utcnow(),
            **status_in.dict()
        )
        db.add(db_status)
        db.commit()
        db.refresh(db_status)
        return db_status

    # Analytics
    def get_timeline_summary(self, db: Session, user_id: Union[str, UUID]) -> dict:
        """
        Get timeline analytics summary
        """
        if not self._check_tables_exist(db):
            print("Timeline tables don't exist in the database")
            return {
                "total_events": 0,
                "milestones_completed": 0,
                "total_milestones": 0,
                "milestone_completion_rate": 0,
                "upcoming_deadlines": 0,
                "overdue_deadlines": 0,
            }
            
        profile_id = self._get_user_profile_id(db, user_id)
        total_events = db.query(TimelineModel).filter(TimelineModel.profile_id == profile_id).count()
        
        try:
            milestones_completed = (
                db.query(TimelineModel)
                .filter(
                    and_(
                        TimelineModel.profile_id == profile_id,
                        TimelineModel.is_milestone.is_(True),
                        TimelineModel.event_status == "completed"
                    )
                )
                .count()
            )
        except Exception as e:
            # If there's an error, return 0 for milestones_completed
            milestones_completed = 0
        
        try:
            total_milestones = (
                db.query(TimelineModel)
                .filter(
                    and_(
                        TimelineModel.profile_id == profile_id,
                        TimelineModel.is_milestone.is_(True)
                    )
                )
                .count()
            )
        except Exception as e:
            total_milestones = 0
        
        try:
            upcoming_deadlines = (
                db.query(DeadlineModel)
                .filter(
                    and_(
                        DeadlineModel.profile_id == profile_id,
                        DeadlineModel.deadline_date >= date.today(),
                        DeadlineModel.is_completed.is_(False)
                    )
                )
                .count()
            )
        except Exception as e:
            upcoming_deadlines = 0
        
        try:
            overdue_deadlines = (
                db.query(DeadlineModel)
                .filter(
                    and_(
                        DeadlineModel.profile_id == profile_id,
                        DeadlineModel.deadline_date < date.today(),
                        DeadlineModel.is_completed.is_(False)
                    )
                )
                .count()
            )
        except Exception as e:
            overdue_deadlines = 0

        return {
            "total_events": total_events,
            "milestones_completed": milestones_completed,
            "total_milestones": total_milestones,
            "milestone_completion_rate": (
                milestones_completed / total_milestones * 100 
                if total_milestones > 0 else 0
            ),
            "upcoming_deadlines": upcoming_deadlines,
            "overdue_deadlines": overdue_deadlines,
        }

    def get_progress_analytics(
        self, db: Session, user_id: Union[str, UUID], immigration_path: Optional[str] = None
    ) -> dict:
        """
        Get progress analytics for immigration journey
        """
        if not self._check_tables_exist(db):
            print("Timeline tables don't exist in the database")
            return {
                "immigration_path": immigration_path,
                "total_milestones": 0,
                "completed_milestones": 0,
                "remaining_milestones": 0,
                "progress_percentage": 0,
                "estimated_completion_months": 0,
            }
            
        # Get milestone templates for the immigration path
        milestones_query = db.query(MilestoneModel)
        if immigration_path:
            milestones_query = milestones_query.filter(
                MilestoneModel.immigration_path == immigration_path
            )
        
        total_milestones = milestones_query.count()
        
        # Get user's completed milestones
        profile_id = self._get_user_profile_id(db, user_id)
        try:
            user_events_query = db.query(TimelineModel).filter(
                and_(
                    TimelineModel.profile_id == profile_id,
                    TimelineModel.is_milestone.is_(True),
                    TimelineModel.event_status == "completed"
                )
            )
            completed_milestones = user_events_query.count()
        except Exception as e:
            completed_milestones = 0
        
        # Calculate estimated completion time based on remaining milestones
        remaining_milestones = total_milestones - completed_milestones
        
        return {
            "immigration_path": immigration_path,
            "total_milestones": total_milestones,
            "completed_milestones": completed_milestones,
            "remaining_milestones": remaining_milestones,
            "progress_percentage": (
                completed_milestones / total_milestones * 100 
                if total_milestones > 0 else 0
            ),
            "estimated_completion_months": remaining_milestones * 2,  # Rough estimate
        }


# Create service instance
timeline_service = TimelineService()