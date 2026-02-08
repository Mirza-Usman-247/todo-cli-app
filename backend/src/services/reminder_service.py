"""
Reminder Service Layer - Phase 5 Event-Driven Architecture
Manages task reminders via Dapr Jobs API
Implements T039-T041 from tasks.md
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
import logging

from src.dapr.jobs import DaprJobsClient

logger = logging.getLogger(__name__)

# Initialize Dapr Jobs client
jobs_client = DaprJobsClient()


class ReminderService:
    """
    Reminder scheduling service using Dapr Jobs API
    Implements T039-T041 from tasks.md
    """

    @staticmethod
    async def schedule_reminder(
        todo_id: str,
        user_id: str,
        title: str,
        due_date: str,
        minutes_before: int = 1440  # Default: 24 hours
    ) -> Tuple[bool, Optional[str]]:
        """
        Schedule a reminder for a task (T039)

        Args:
            todo_id: Task ID
            user_id: User ID
            title: Task title (for notification)
            due_date: Due date in ISO format
            minutes_before: Minutes before due date to send reminder (default 24h)

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Parse due date
            try:
                due_dt = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                due_dt = due_dt.replace(tzinfo=None)
            except ValueError:
                return False, "Invalid due date format"

            # Calculate reminder time
            reminder_time = due_dt - timedelta(minutes=minutes_before)

            # Don't schedule if reminder time is in the past
            now = datetime.utcnow()
            if reminder_time < now:
                logger.warning(
                    f"⚠️  Reminder time {reminder_time} is in the past for task {todo_id}. "
                    "Not scheduling."
                )
                return False, "Reminder time is in the past"

            # Schedule via Dapr Jobs API
            success = await jobs_client.schedule_reminder(
                todo_id=todo_id,
                user_id=user_id,
                title=title,
                due_date=due_dt,
                minutes_before=minutes_before
            )

            if success:
                logger.info(
                    f"✅ Scheduled reminder for task {todo_id} at {reminder_time} "
                    f"({minutes_before} minutes before due date)"
                )
                return True, None
            else:
                return False, "Failed to schedule reminder via Dapr Jobs API"

        except Exception as e:
            logger.error(f"❌ Failed to schedule reminder for task {todo_id}: {e}")
            return False, str(e)

    @staticmethod
    async def cancel_reminder(todo_id: str) -> Tuple[bool, Optional[str]]:
        """
        Cancel a reminder for a task (T040)

        Args:
            todo_id: Task ID

        Returns:
            Tuple of (success, error_message)
        """
        try:
            success = await jobs_client.cancel_reminder(todo_id=todo_id)

            if success:
                logger.info(f"✅ Cancelled reminder for task {todo_id}")
                return True, None
            else:
                return False, "Failed to cancel reminder via Dapr Jobs API"

        except Exception as e:
            logger.error(f"❌ Failed to cancel reminder for task {todo_id}: {e}")
            return False, str(e)

    @staticmethod
    async def reschedule_reminder(
        todo_id: str,
        user_id: str,
        title: str,
        new_due_date: str,
        minutes_before: int = 1440
    ) -> Tuple[bool, Optional[str]]:
        """
        Reschedule a reminder when due date changes (T041)

        Args:
            todo_id: Task ID
            user_id: User ID
            title: Task title
            new_due_date: New due date in ISO format
            minutes_before: Minutes before due date to send reminder

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Cancel existing reminder
            cancel_success, cancel_error = await ReminderService.cancel_reminder(todo_id)

            if not cancel_success:
                logger.warning(
                    f"⚠️  Failed to cancel existing reminder for task {todo_id}: {cancel_error}"
                )

            # Schedule new reminder
            schedule_success, schedule_error = await ReminderService.schedule_reminder(
                todo_id=todo_id,
                user_id=user_id,
                title=title,
                due_date=new_due_date,
                minutes_before=minutes_before
            )

            if schedule_success:
                logger.info(f"✅ Rescheduled reminder for task {todo_id}")
                return True, None
            else:
                return False, f"Failed to reschedule: {schedule_error}"

        except Exception as e:
            logger.error(f"❌ Failed to reschedule reminder for task {todo_id}: {e}")
            return False, str(e)


# Convenience export
__all__ = ['ReminderService']
