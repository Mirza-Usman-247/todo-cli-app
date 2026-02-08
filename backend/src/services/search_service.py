"""
Search Service Layer - Phase 5 Event-Driven Architecture
Provides search and filter functionality for tasks
Implements T042-T045 from tasks.md
"""
from typing import List, Optional
import logging

from src.models.task import Task

logger = logging.getLogger(__name__)


class SearchService:
    """
    Search and filter service for tasks
    NOTE: This is a simplified in-memory implementation.
    Production would use a search engine (Elasticsearch) or database with indices.
    """

    @staticmethod
    def filter_by_priority(tasks: List[Task], priority: str) -> List[Task]:
        """
        Filter tasks by priority (T042)

        Args:
            tasks: List of tasks to filter
            priority: Priority to filter by (low/medium/high/urgent)

        Returns:
            Filtered list of tasks
        """
        try:
            filtered = [task for task in tasks if task.priority == priority]
            logger.info(f"Filtered {len(filtered)} tasks with priority '{priority}'")
            return filtered

        except Exception as e:
            logger.error(f"❌ Failed to filter by priority: {e}")
            return []

    @staticmethod
    def filter_by_tags(tasks: List[Task], tags: List[str], match_all: bool = True) -> List[Task]:
        """
        Filter tasks by tags (T043)

        Args:
            tasks: List of tasks to filter
            tags: List of tags to filter by
            match_all: If True, task must have ALL tags (AND logic).
                      If False, task must have ANY tag (OR logic).

        Returns:
            Filtered list of tasks
        """
        try:
            if match_all:
                # Task must contain all specified tags
                filtered = [
                    task for task in tasks
                    if all(tag in task.tags for tag in tags)
                ]
            else:
                # Task must contain at least one tag
                filtered = [
                    task for task in tasks
                    if any(tag in task.tags for tag in tags)
                ]

            logger.info(f"Filtered {len(filtered)} tasks with tags {tags} (match_all={match_all})")
            return filtered

        except Exception as e:
            logger.error(f"❌ Failed to filter by tags: {e}")
            return []

    @staticmethod
    def search_by_keyword(tasks: List[Task], keyword: str) -> List[Task]:
        """
        Search tasks by keyword in title and description (T044)

        Args:
            tasks: List of tasks to search
            keyword: Search keyword (case-insensitive)

        Returns:
            List of matching tasks
        """
        try:
            keyword_lower = keyword.lower()

            filtered = [
                task for task in tasks
                if (keyword_lower in task.title.lower()) or
                   (task.description and keyword_lower in task.description.lower())
            ]

            logger.info(f"Found {len(filtered)} tasks matching keyword '{keyword}'")
            return filtered

        except Exception as e:
            logger.error(f"❌ Failed to search by keyword: {e}")
            return []

    @staticmethod
    def sort_tasks(
        tasks: List[Task],
        sort_by: str = "createdAt",
        ascending: bool = True
    ) -> List[Task]:
        """
        Sort tasks by field (T045)

        Args:
            tasks: List of tasks to sort
            sort_by: Field to sort by (createdAt, updatedAt, dueDate, priority)
            ascending: Sort order (True for ascending, False for descending)

        Returns:
            Sorted list of tasks
        """
        try:
            # Priority order mapping for sorting
            priority_order = {
                "low": 1,
                "medium": 2,
                "high": 3,
                "urgent": 4
            }

            if sort_by == "priority":
                # Sort by priority level
                sorted_tasks = sorted(
                    tasks,
                    key=lambda t: priority_order.get(t.priority, 0),
                    reverse=not ascending
                )
            elif sort_by == "dueDate":
                # Sort by due date (tasks without due date go to end)
                sorted_tasks = sorted(
                    tasks,
                    key=lambda t: t.dueDate if t.dueDate else "9999-12-31T23:59:59Z",
                    reverse=not ascending
                )
            elif sort_by == "createdAt":
                sorted_tasks = sorted(
                    tasks,
                    key=lambda t: t.createdAt,
                    reverse=not ascending
                )
            elif sort_by == "updatedAt":
                sorted_tasks = sorted(
                    tasks,
                    key=lambda t: t.updatedAt,
                    reverse=not ascending
                )
            else:
                logger.warning(f"⚠️  Unknown sort field '{sort_by}', returning unsorted")
                return tasks

            logger.info(f"Sorted {len(tasks)} tasks by '{sort_by}' (ascending={ascending})")
            return sorted_tasks

        except Exception as e:
            logger.error(f"❌ Failed to sort tasks: {e}")
            return tasks

    @staticmethod
    def apply_filters(
        tasks: List[Task],
        priority: Optional[str] = None,
        tags: Optional[List[str]] = None,
        keyword: Optional[str] = None,
        sort_by: str = "createdAt",
        ascending: bool = False
    ) -> List[Task]:
        """
        Apply multiple filters and sorting to tasks

        Args:
            tasks: List of tasks to filter
            priority: Optional priority filter
            tags: Optional tags filter
            keyword: Optional keyword search
            sort_by: Field to sort by
            ascending: Sort order

        Returns:
            Filtered and sorted list of tasks
        """
        try:
            filtered_tasks = tasks

            # Apply priority filter
            if priority:
                filtered_tasks = SearchService.filter_by_priority(filtered_tasks, priority)

            # Apply tags filter
            if tags:
                filtered_tasks = SearchService.filter_by_tags(filtered_tasks, tags, match_all=True)

            # Apply keyword search
            if keyword:
                filtered_tasks = SearchService.search_by_keyword(filtered_tasks, keyword)

            # Sort results
            filtered_tasks = SearchService.sort_tasks(filtered_tasks, sort_by, ascending)

            logger.info(f"Applied filters and returned {len(filtered_tasks)} tasks")
            return filtered_tasks

        except Exception as e:
            logger.error(f"❌ Failed to apply filters: {e}")
            return []


# Convenience export
__all__ = ['SearchService']
