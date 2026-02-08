"""
Recurring Tasks Service Layer - Phase 5 Event-Driven Architecture
Manages recurring tasks with automatic recreation
Implements T046-T047 from tasks.md
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
import logging

from src.dapr.jobs import DaprJobsClient
from src.services.task_state_service import TaskStateService

logger = logging.getLogger(__name__)

# Initialize Dapr Jobs client
jobs_client = DaprJobsClient()


class RecurringService:
    """
    Recurring tasks service using Dapr Jobs API
    Implements T046-T047 from tasks.md
    """

    @staticmethod
    def _calculate_next_occurrence(
        due_date: str,
        recurrence_pattern: str
    ) -> Optional[str]:
        """
        Calculate next occurrence based on recurrence pattern

        Args:
            due_date: Current due date in ISO format
            recurrence_pattern: Recurrence pattern (daily, weekly, monthly, yearly)

        Returns:
            Next due date in ISO format, or None if invalid
        """
        try:
            current_due = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
            current_due = current_due.replace(tzinfo=None)

            if recurrence_pattern == "daily":
                next_due = current_due + timedelta(days=1)
            elif recurrence_pattern == "weekly":
                next_due = current_due + timedelta(weeks=1)
            elif recurrence_pattern == "monthly":
                # Approximate - add 30 days for monthly
                next_due = current_due + timedelta(days=30)
            elif recurrence_pattern == "yearly":
                # Approximate - add 365 days for yearly
                next_due = current_due + timedelta(days=365)
            elif recurrence_pattern.startswith("custom:"):
                # Custom interval in hours (e.g., "custom:48" for 48 hours)
                try:
                    hours = int(recurrence_pattern.split(":")[1])
                    if hours < 1:
                        raise ValueError("Custom interval must be at least 1 hour")
                    next_due = current_due + timedelta(hours=hours)
                except (IndexError, ValueError) as e:
                    logger.error(f"Invalid custom recurrence pattern: {recurrence_pattern}")
                    return None
            else:
                logger.error(f"Unknown recurrence pattern: {recurrence_pattern}")
                return None

            return next_due.isoformat() + "Z"

        except Exception as e:
            logger.error(f"❌ Failed to calculate next occurrence: {e}")
            return None

    @staticmethod
    async def create_recurring_task(
        user_id: str,
        title: str,
        description: Optional[str],
        priority: str,
        tags: Optional[list],
        due_date: str,
        recurrence_pattern: str,
        minutes_before: int = 1440
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Create a recurring task (T046)

        Args:
            user_id: User ID
            title: Task title
            description: Task description
            priority: Task priority
            tags: Task tags
            due_date: First due date
            recurrence_pattern: Recurrence pattern (daily, weekly, monthly, yearly, custom:N)
            minutes_before: Minutes before due date for reminder

        Returns:
            Tuple of (task_id, error_message)
        """
        try:
            # Validate custom interval is at least 1 hour
            if recurrence_pattern.startswith("custom:"):
                try:
                    hours = int(recurrence_pattern.split(":")[1])
                    if hours < 1:
                        return None, "Custom recurrence interval must be at least 1 hour"
                except (IndexError, ValueError):
                    return None, "Invalid custom recurrence pattern format. Use 'custom:N' where N is hours."

            # Add recurring metadata to tags
            recurring_tags = (tags or []) + [f"recurring:{recurrence_pattern}"]

            # Create the first instance
            task, error = await TaskStateService.create_task(
                user_id=user_id,
                title=title,
                description=description,
                priority=priority,
                tags=recurring_tags,
                due_date=due_date
            )

            if not task:
                return None, error

            # Schedule job for next occurrence recreation
            # When task is completed, the job will create the next instance
            next_due_date = RecurringService._calculate_next_occurrence(due_date, recurrence_pattern)

            if next_due_date:
                # Note: In production, you'd have a dedicated job handler for recurring tasks
                logger.info(
                    f"✅ Created recurring task {task.id} with pattern '{recurrence_pattern}'. "
                    f"Next occurrence: {next_due_date}"
                )

            return task.id, None

        except Exception as e:
            logger.error(f"❌ Failed to create recurring task: {e}")
            return None, str(e)

    @staticmethod
    async def handle_recurring_completion(
        task_id: str,
        user_id: str,
        title: str,
        description: Optional[str],
        priority: str,
        tags: list,
        recurrence_pattern: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Handle completion of a recurring task by creating next instance (T047)

        Args:
            task_id: Completed task ID
            user_id: User ID
            title: Task title
            description: Task description
            priority: Task priority
            tags: Task tags (should include recurring:pattern tag)
            recurrence_pattern: Recurrence pattern

        Returns:
            Tuple of (new_task_id, error_message)
        """
        try:
            # Calculate next due date
            current_due = datetime.utcnow().isoformat() + "Z"
            next_due_date = RecurringService._calculate_next_occurrence(current_due, recurrence_pattern)

            if not next_due_date:
                return None, "Failed to calculate next occurrence"

            # Create next instance
            new_task, error = await TaskStateService.create_task(
                user_id=user_id,
                title=title,
                description=description,
                priority=priority,
                tags=tags,
                due_date=next_due_date
            )

            if not new_task:
                return None, error

            logger.info(
                f"✅ Created next instance {new_task.id} of recurring task {task_id}. "
                f"Due: {next_due_date}"
            )

            return new_task.id, None

        except Exception as e:
            logger.error(f"❌ Failed to handle recurring completion: {e}")
            return None, str(e)

    @staticmethod
    def is_recurring_task(tags: list) -> Tuple[bool, Optional[str]]:
        """
        Check if a task is recurring based on tags

        Args:
            tags: Task tags

        Returns:
            Tuple of (is_recurring, recurrence_pattern)
        """
        for tag in tags:
            if tag.startswith("recurring:"):
                pattern = tag.split(":", 1)[1]
                return True, pattern
        return False, None


# Convenience export
__all__ = ['RecurringService']
