"""
Dapr State Store Client Wrapper
Interacts with Redis via Dapr State Store API with ETag concurrency control
"""
from dapr.clients import DaprClient
from dapr.clients.grpc._state import StateOptions, Consistency, Concurrency
from typing import Dict, Any, Optional, List, Tuple
import logging
import json

logger = logging.getLogger(__name__)

STATE_STORE_NAME = "statestore-redis"


class DaprStateClient:
    """Wrapper for Dapr State Store operations"""

    def __init__(self):
        self.store_name = STATE_STORE_NAME

    async def get(self, key: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Get state from Redis via Dapr

        Args:
            key: State key (e.g., 'task:uuid')

        Returns:
            Tuple of (value, etag) or (None, None) if not found
        """
        try:
            with DaprClient() as client:
                state_item = client.get_state(
                    store_name=self.store_name,
                    key=key
                )

                if state_item.data:
                    value = json.loads(state_item.data)
                    etag = state_item.etag
                    logger.info(f"✅ Retrieved state for key '{key}' [etag={etag}]")
                    return value, etag
                else:
                    logger.info(f"⚠️  No state found for key '{key}'")
                    return None, None

        except Exception as e:
            logger.error(f"❌ Failed to get state for key '{key}': {e}")
            raise

    async def set(
        self,
        key: str,
        value: Dict[str, Any],
        etag: Optional[str] = None
    ) -> bool:
        """
        Set state in Redis via Dapr with optional ETag for concurrency control

        Args:
            key: State key
            value: State value (dict)
            etag: Optional ETag for optimistic locking

        Returns:
            True if set successfully

        Raises:
            Exception if ETag conflict (concurrent update)
        """
        try:
            with DaprClient() as client:
                # Configure state options for concurrency control
                state_options = None
                if etag:
                    state_options = StateOptions(
                        concurrency=Concurrency.first_write,
                        consistency=Consistency.strong
                    )

                # Save state
                client.save_state(
                    store_name=self.store_name,
                    key=key,
                    value=json.dumps(value),
                    etag=etag,
                    options=state_options
                )

                logger.info(f"✅ Saved state for key '{key}' [etag={etag}]")
                return True

        except Exception as e:
            if "etag" in str(e).lower() or "conflict" in str(e).lower():
                logger.warning(f"⚠️  ETag conflict for key '{key}': {e}")
                raise ValueError(f"Concurrent update detected for key '{key}'")
            else:
                logger.error(f"❌ Failed to save state for key '{key}': {e}")
                raise

    async def delete(self, key: str, etag: Optional[str] = None) -> bool:
        """
        Delete state from Redis via Dapr

        Args:
            key: State key
            etag: Optional ETag for concurrency control

        Returns:
            True if deleted successfully
        """
        try:
            with DaprClient() as client:
                # Configure state options if ETag provided
                state_options = None
                if etag:
                    state_options = StateOptions(
                        concurrency=Concurrency.first_write,
                        consistency=Consistency.strong
                    )

                client.delete_state(
                    store_name=self.store_name,
                    key=key,
                    etag=etag,
                    options=state_options
                )

                logger.info(f"✅ Deleted state for key '{key}'")
                return True

        except Exception as e:
            logger.error(f"❌ Failed to delete state for key '{key}': {e}")
            raise

    async def get_bulk(self, keys: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get multiple states in bulk

        Args:
            keys: List of state keys

        Returns:
            Dictionary of key -> value
        """
        try:
            with DaprClient() as client:
                bulk_result = client.get_bulk_state(
                    store_name=self.store_name,
                    keys=keys
                )

                results = {}
                for item in bulk_result.items:
                    if item.data:
                        results[item.key] = json.loads(item.data)

                logger.info(f"✅ Retrieved {len(results)}/{len(keys)} states in bulk")
                return results

        except Exception as e:
            logger.error(f"❌ Failed to get bulk state: {e}")
            raise

    async def query_by_prefix(self, prefix: str, limit: int = 100) -> Dict[str, Dict[str, Any]]:
        """
        Query states by key prefix (simulated via bulk get with known keys)

        Note: Redis doesn't support prefix queries natively via Dapr.
        This is a simplified implementation that would need enhancement for production.

        Args:
            prefix: Key prefix (e.g., 'task:user-123:')
            limit: Maximum number of results

        Returns:
            Dictionary of key -> value
        """
        # This is a placeholder - in production, maintain an index of keys
        # or use a database that supports prefix queries
        logger.warning(
            f"⚠️  Prefix query not fully supported by Redis State Store. "
            f"Prefix: {prefix}"
        )
        return {}


# Singleton instance
state_client = DaprStateClient()
