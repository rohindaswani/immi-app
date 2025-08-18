from typing import Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import logging
import asyncio

from app.db.postgres import get_db
from app.services.notification_rule_engine import NotificationRuleEngine
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class NotificationScheduler:
    """Background scheduler for automated notifications"""
    
    def __init__(self):
        self.is_running = False
        self.last_daily_run = None
        self.last_weekly_run = None
        self.last_monthly_run = None
    
    async def start_scheduler(self):
        """Start the notification scheduler"""
        self.is_running = True
        logger.info("Notification scheduler started")
        
        while self.is_running:
            try:
                await self._run_scheduled_tasks()
                # Wait 1 hour before next check
                await asyncio.sleep(3600)
            except Exception as e:
                logger.error(f"Error in scheduler: {str(e)}")
                # Wait 5 minutes before retrying on error
                await asyncio.sleep(300)
    
    def stop_scheduler(self):
        """Stop the notification scheduler"""
        self.is_running = False
        logger.info("Notification scheduler stopped")
    
    async def _run_scheduled_tasks(self):
        """Run scheduled notification tasks"""
        now = datetime.utcnow()
        
        # Run daily tasks (every 24 hours)
        if self._should_run_daily(now):
            await self._run_daily_tasks()
            self.last_daily_run = now
        
        # Run weekly tasks (every 7 days)
        if self._should_run_weekly(now):
            await self._run_weekly_tasks()
            self.last_weekly_run = now
        
        # Run monthly tasks (every 30 days)
        if self._should_run_monthly(now):
            await self._run_monthly_tasks()
            self.last_monthly_run = now
    
    def _should_run_daily(self, now: datetime) -> bool:
        """Check if daily tasks should run"""
        if self.last_daily_run is None:
            return True
        return now - self.last_daily_run >= timedelta(hours=24)
    
    def _should_run_weekly(self, now: datetime) -> bool:
        """Check if weekly tasks should run"""
        if self.last_weekly_run is None:
            return True
        return now - self.last_weekly_run >= timedelta(days=7)
    
    def _should_run_monthly(self, now: datetime) -> bool:
        """Check if monthly tasks should run"""
        if self.last_monthly_run is None:
            return True
        return now - self.last_monthly_run >= timedelta(days=30)
    
    async def _run_daily_tasks(self):
        """Run daily notification tasks"""
        logger.info("Running daily notification tasks")
        
        try:
            # Get database session
            db = next(get_db())
            
            # Run the notification rule engine
            rule_engine = NotificationRuleEngine(db)
            results = rule_engine.run_all_rules()
            
            logger.info(f"Daily tasks completed: {results}")
            
        except Exception as e:
            logger.error(f"Error in daily tasks: {str(e)}")
        finally:
            db.close()
    
    async def _run_weekly_tasks(self):
        """Run weekly notification tasks"""
        logger.info("Running weekly notification tasks")
        
        try:
            # Get database session
            db = next(get_db())
            
            # Clean up expired notifications
            service = NotificationService(db)
            cleaned_count = service.cleanup_expired_notifications()
            
            logger.info(f"Weekly cleanup: removed {cleaned_count} expired notifications")
            
        except Exception as e:
            logger.error(f"Error in weekly tasks: {str(e)}")
        finally:
            db.close()
    
    async def _run_monthly_tasks(self):
        """Run monthly notification tasks"""
        logger.info("Running monthly notification tasks")
        
        try:
            # Get database session
            db = next(get_db())
            
            # Run comprehensive rule engine check
            rule_engine = NotificationRuleEngine(db)
            results = rule_engine.run_all_rules()
            
            # Additional monthly maintenance tasks can be added here
            
            logger.info(f"Monthly tasks completed: {results}")
            
        except Exception as e:
            logger.error(f"Error in monthly tasks: {str(e)}")
        finally:
            db.close()
    
    async def run_immediate_check(self) -> Dict[str, Any]:
        """Run immediate notification check (for testing/manual trigger)"""
        logger.info("Running immediate notification check")
        
        try:
            # Get database session
            db = next(get_db())
            
            # Run the notification rule engine
            rule_engine = NotificationRuleEngine(db)
            results = rule_engine.run_all_rules()
            
            logger.info(f"Immediate check completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error in immediate check: {str(e)}")
            return {"error": str(e)}
        finally:
            db.close()


# Global scheduler instance
notification_scheduler = NotificationScheduler()


async def start_notification_scheduler():
    """Start the notification scheduler as a background task"""
    await notification_scheduler.start_scheduler()


def stop_notification_scheduler():
    """Stop the notification scheduler"""
    notification_scheduler.stop_scheduler()


async def run_notification_check():
    """Run an immediate notification check"""
    return await notification_scheduler.run_immediate_check()