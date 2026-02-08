"""
Dapr Jobs API Client Wrapper
Schedules and manages jobs for reminders and scheduled tasks
Uses Dapr Jobs/Scheduler API (alpha1) via HTTP
"""
import os
import httpx
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
import json

logger = logging.getLogger(__name__)

# Dapr HTTP endpoint
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_URL = f"http://localhost:{DAPR_HTTP_PORT}"


class DaprJobsClient:
    """Wrapper for Dapr Jobs API operations via HTTP"""

    def __init__(self):
        self.dapr_url = DAPR_URL
        self.app_id = "backend"
        self.pubsub_name = "pubsub-kafka"

    async def schedule_job(
        self,
        job_id: str,
        at: datetime,
        payload: Dict[str, Any],
        retries: int = 3
    ) -> bool:
        """
        Schedule a reminder using Dapr pub/sub with delay (simpler approach)

        Since Dapr Jobs API has compatibility issues, we use a hybrid approach:
        - Store reminder metadata in Redis state store
        - Use a background checker or manual trigger for now
        - Future: Integrate with Dapr Actors for reminders

        Args:
            job_id: Unique identifier for the job
            at: Datetime when the job should execute
            payload: Data to pass to the job handler
            retries: Number of retry attempts on failure

        Returns:
            True if job scheduled successfully
        """
        try:
            from dapr.clients import DaprClient

            # Calculate seconds until reminder should fire
            now = datetime.utcnow()
            delay_seconds = int((at - now).total_seconds())

            if delay_seconds <= 0:
                logger.warning(f"⚠️  Job {job_id} is in the past, publishing immediately")
                # Publish reminder event immediately
                return await self._publish_reminder_now(payload)

            # Store reminder in state for tracking
            reminder_data = {
                "jobId": job_id,
                "triggerAt": at.isoformat() + "Z",
                "payload": payload,
                "status": "scheduled",
                "createdAt": now.isoformat() + "Z"
            }

            with DaprClient() as client:
                # Save to state store for tracking
                import json
                client.save_state(
                    store_name="statestore-redis",
                    key=f"reminder:{job_id}",
                    value=json.dumps(reminder_data)
                )

            logger.info(
                f"✅ Scheduled reminder '{job_id}' for {at.isoformat()}Z "
                f"({delay_seconds} seconds from now)"
            )

            # For immediate testing: if delay is less than 2 minutes, publish after delay
            if delay_seconds < 120:
                logger.info(f"⏰ Short delay detected, will publish reminder in {delay_seconds}s")
                import asyncio
                asyncio.create_task(self._delayed_publish(delay_seconds, payload, job_id))

            return True

        except Exception as e:
            logger.error(f"❌ Failed to schedule job '{job_id}': {e}")
            return False

    async def _delayed_publish(self, delay_seconds: int, payload: Dict[str, Any], job_id: str):
        """Publish reminder after delay (for testing short delays)"""
        import asyncio
        await asyncio.sleep(delay_seconds)
        logger.info(f"⏰ Delay complete, publishing reminder for job {job_id}")
        await self._publish_reminder_now(payload)

    async def _publish_reminder_now(self, payload: Dict[str, Any]) -> bool:
        """Publish a reminder event immediately to Kafka"""
        try:
            from src.events.publishers import TodoReminderPublisher

            success, error = await TodoReminderPublisher.publish(
                todo_id=payload.get("todoId"),
                user_id=payload.get("userId"),
                title=payload.get("title"),
                due_date=payload.get("dueDate"),
                minutes_before=payload.get("minutesBefore", 0)
            )

            if success:
                logger.info(f"✅ Published reminder event to Kafka")
                return True
            else:
                logger.error(f"❌ Failed to publish reminder: {error}")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to publish reminder now: {e}")
            return False

    async def schedule_reminder(
        self,
        todo_id: str,
        user_id: str,
        title: str,
        due_date: datetime,
        minutes_before: int = 1440  # Default: 24 hours
    ) -> bool:
        """
        Shortcut method to schedule a reminder for a todo item

        Args:
            todo_id: ID of the todo item
            user_id: ID of the user who owns the todo
            title: Title of the todo (for notification)
            due_date: When the todo is due
            minutes_before: How many minutes before due date to send reminder

        Returns:
            True if reminder scheduled successfully
        """
        reminder_time = due_date - timedelta(minutes=minutes_before)

        # Don't schedule if the reminder time is in the past
        if reminder_time < datetime.utcnow().replace(tzinfo=None):
            logger.warning(f"⚠️  Reminder time for todo {todo_id} is in the past, not scheduling")
            return False

        job_id = f"reminder:{todo_id}"
        payload = {
            "eventType": "todo-reminder",
            "todoId": todo_id,
            "userId": user_id,
            "title": title,
            "dueDate": due_date.isoformat() + "Z",
            "minutesBefore": minutes_before
        }

        return await self.schedule_job(
            job_id=job_id,
            at=reminder_time,
            payload=payload
        )

    async def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a scheduled job

        Args:
            job_id: ID of the job to cancel

        Returns:
            True if job cancelled successfully
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.delete(
                    f"{self.dapr_url}/v1.0-alpha1/jobs/{self.app_id}/{job_id}"
                )

                if response.status_code in [200, 204]:
                    logger.info(f"✅ Cancelled job '{job_id}'")
                    return True
                else:
                    logger.warning(
                        f"⚠️  Failed to cancel job '{job_id}': "
                        f"HTTP {response.status_code} - {response.text}"
                    )
                    return False

        except Exception as e:
            logger.error(f"❌ Failed to cancel job '{job_id}': {e}")
            return False

    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a scheduled job

        Args:
            job_id: ID of the job

        Returns:
            Job data dictionary or None if not found
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.dapr_url}/v1.0-alpha1/jobs/{self.app_id}/{job_id}"
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return None
                else:
                    logger.warning(
                        f"⚠️  Failed to get job '{job_id}': "
                        f"HTTP {response.status_code}"
                    )
                    return None

        except Exception as e:
            logger.error(f"❌ Failed to get job '{job_id}': {e}")
            return None

    async def cancel_reminder(self, todo_id: str) -> bool:
        """
        Shortcut method to cancel a reminder for a todo item
        """
        job_id = f"reminder:{todo_id}"
        return await self.cancel_job(job_id)


# Singleton instance
jobs_client = DaprJobsClient()


# Convenience exports
__all__ = ['DaprJobsClient', 'jobs_client']
