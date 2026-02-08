"""
Timezone Service - Phase 5 Event-Driven Architecture
Handles timezone conversions for due dates and reminders
Implements T041A from tasks.md
"""
from datetime import datetime, timezone
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TimezoneService:
    """
    Timezone conversion service for task due dates and reminders
    Stores all dates in UTC, converts to user timezone for display
    """

    @staticmethod
    def to_utc(dt_str: str, user_timezone: str = "UTC") -> Optional[str]:
        """
        Convert datetime string from user timezone to UTC

        Args:
            dt_str: Datetime string in ISO format
            user_timezone: User's timezone (e.g., "America/New_York")

        Returns:
            UTC datetime string in ISO format with 'Z' suffix
        """
        try:
            # Parse datetime string
            if dt_str.endswith('Z'):
                # Already in UTC
                dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            else:
                dt = datetime.fromisoformat(dt_str)

            # If no timezone info, assume it's in user's timezone
            if dt.tzinfo is None:
                # For now, treat as UTC if no timezone specified
                # In production, parse user_timezone and localize
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                # Convert to UTC
                dt = dt.astimezone(timezone.utc)

            # Return as ISO string with Z suffix
            return dt.isoformat().replace('+00:00', 'Z')

        except Exception as e:
            logger.error(f"❌ Failed to convert datetime to UTC: {e}")
            return None

    @staticmethod
    def from_utc(dt_str: str, user_timezone: str = "UTC") -> Optional[str]:
        """
        Convert UTC datetime string to user timezone

        Args:
            dt_str: UTC datetime string in ISO format
            user_timezone: Target timezone (e.g., "America/New_York")

        Returns:
            Datetime string in user's timezone
        """
        try:
            # Parse UTC datetime
            if dt_str.endswith('Z'):
                dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            else:
                dt = datetime.fromisoformat(dt_str)

            # Ensure datetime is in UTC
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                dt = dt.astimezone(timezone.utc)

            # For now, return as UTC
            # In production, use pytz or zoneinfo to convert to user_timezone
            # Example with zoneinfo (Python 3.9+):
            # from zoneinfo import ZoneInfo
            # user_tz = ZoneInfo(user_timezone)
            # dt = dt.astimezone(user_tz)

            return dt.isoformat()

        except Exception as e:
            logger.error(f"❌ Failed to convert datetime from UTC: {e}")
            return None

    @staticmethod
    def get_current_utc() -> str:
        """
        Get current UTC timestamp in ISO format

        Returns:
            Current UTC datetime string with 'Z' suffix
        """
        return datetime.utcnow().isoformat() + 'Z'

    @staticmethod
    def parse_and_validate(dt_str: str) -> tuple[bool, Optional[datetime]]:
        """
        Parse and validate datetime string

        Args:
            dt_str: Datetime string to parse

        Returns:
            Tuple of (is_valid, datetime_object)
        """
        try:
            if dt_str.endswith('Z'):
                dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            else:
                dt = datetime.fromisoformat(dt_str)

            return True, dt

        except Exception as e:
            logger.error(f"❌ Failed to parse datetime '{dt_str}': {e}")
            return False, None

    @staticmethod
    def is_in_future(dt_str: str, user_timezone: str = "UTC") -> bool:
        """
        Check if datetime is in the future

        Args:
            dt_str: Datetime string to check
            user_timezone: User's timezone for comparison

        Returns:
            True if datetime is in the future
        """
        try:
            is_valid, dt = TimezoneService.parse_and_validate(dt_str)

            if not is_valid or dt is None:
                return False

            # Ensure datetime has timezone info
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)

            # Get current UTC time
            now = datetime.now(timezone.utc)

            return dt > now

        except Exception as e:
            logger.error(f"❌ Failed to check if datetime is in future: {e}")
            return False

    @staticmethod
    def add_hours(dt_str: str, hours: int) -> Optional[str]:
        """
        Add hours to a datetime

        Args:
            dt_str: Base datetime string
            hours: Number of hours to add

        Returns:
            New datetime string
        """
        try:
            is_valid, dt = TimezoneService.parse_and_validate(dt_str)

            if not is_valid or dt is None:
                return None

            # Ensure datetime has timezone info
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)

            # Add hours
            from datetime import timedelta
            new_dt = dt + timedelta(hours=hours)

            # Return as ISO string with Z suffix
            return new_dt.isoformat().replace('+00:00', 'Z')

        except Exception as e:
            logger.error(f"❌ Failed to add {hours} hours to datetime: {e}")
            return None

    @staticmethod
    def format_for_display(dt_str: str, user_timezone: str = "UTC", format_str: str = "%Y-%m-%d %H:%M") -> Optional[str]:
        """
        Format datetime for user-friendly display

        Args:
            dt_str: UTC datetime string
            user_timezone: User's timezone
            format_str: strftime format string

        Returns:
            Formatted datetime string
        """
        try:
            # Convert to user timezone
            user_dt_str = TimezoneService.from_utc(dt_str, user_timezone)

            if not user_dt_str:
                return None

            is_valid, dt = TimezoneService.parse_and_validate(user_dt_str)

            if not is_valid or dt is None:
                return None

            # Format for display
            return dt.strftime(format_str)

        except Exception as e:
            logger.error(f"❌ Failed to format datetime for display: {e}")
            return None


# Convenience export
__all__ = ['TimezoneService']
